# Architecture

This document describes how the system is put together: process boundaries, threading model, and how data moves from the webcam to the browser. It does not cover the detection algorithms themselves (EAR, MAR, fatigue scoring) — see the README for that.

## Overview

The system is two processes: a FastAPI backend that owns the camera and does all the CV work, and a React frontend that's a thin client for it. They talk over REST (control), MJPEG (video), and WebSocket (metrics).

```
┌─────────────────────┐
│   React Dashboard    │
│   (Vite, port 5173)  │
└──────────┬───────────┘
           │ REST (start/stop) · MJPEG (frame) · WebSocket (metrics)
           ▼
┌─────────────────────┐
│   FastAPI Backend    │
│   (Uvicorn, :8000)   │
└──────────┬───────────┘
           │ owns
           ▼
┌─────────────────────┐
│   Detector class     │
└──────────┬───────────┘
           │ runs on
           ▼
┌─────────────────────┐
│ Background thread    │
│ (processing loop)    │
└──────────┬───────────┘
           │ calls
           ▼
┌─────────────────────┐
│ MediaPipe + OpenCV   │
└──────────┬───────────┘
           │ writes
           ▼
┌─────────────────────┐
│ latest_frame /       │
│ latest_metrics       │
│ (lock-protected)     │
└──────────┬───────────┘
           │ read by
           ▼
┌─────────────────────┐
│ MJPEG stream +       │
│ WebSocket handler    │
└───────────────────────┘
```

The key design decision is the layer at the bottom: the background thread never talks to the network directly. It just writes into two shared attributes, and the HTTP/WebSocket layer reads from them whenever a client asks. Producer and consumers are fully decoupled.

## Component responsibilities

| Component | Responsibility |
|---|---|
| `frontend/` (React) | Renders the dashboard, issues start/stop commands, displays the video stream and live metrics. Holds no detection logic. |
| `app/main.py` | FastAPI app definition, CORS config, REST endpoints, owns the single `Detector` instance. |
| `app/websockets/routes.py` | WebSocket endpoint that reads from the shared `Detector` and pushes metrics to connected clients. |
| `app/detection.py` (`Detector`) | Owns the video capture, the MediaPipe face mesh instance, and the background thread. Exposes `start()`, `stop()`, `get_metrics()`, `generate_frames()`. |
| Background thread | Runs the capture → landmark extraction → scoring loop continuously, outside the request/response cycle. |
| `latest_frame` / `latest_metrics` | The only handoff point between the processing thread and the API layer. Guarded by a `threading.Lock`. |

## Backend design

`app/main.py` builds one `FastAPI()` instance and one `Detector()` instance at import time. The detector is injected into the WebSocket router via `set_detector()` — there's no dependency injection framework here, just a module-level reference, which is fine given there's exactly one detector for the process's lifetime.

REST surface:

- `GET /` — liveness check
- `GET /health` — health check
- `POST /start` — starts capture + the background thread
- `POST /stop` — stops the thread and releases the camera
- `GET /video_feed` — MJPEG stream, backed by `Detector.generate_frames()`

The WebSocket route (`/ws`) is a separate `APIRouter` mounted into the main app. It doesn't do any detection work itself — it's a thin loop that polls `detector.get_metrics()` every 100ms and forwards whatever it gets as JSON. If the detector isn't running yet, it just sends stale/default metrics rather than erroring, which keeps the frontend logic simple.

`Detector` is the only class that touches OpenCV or MediaPipe. Everything else — routes, WebSocket handler — only ever calls its public methods (`start`, `stop`, `get_metrics`, `generate_frames`). That boundary is what makes the background-thread design tractable: nothing outside `Detector` needs to know threading is involved.

## Frontend design

The frontend is intentionally shallow. `Dashboard.jsx` is the only component that holds state — `metrics` and `running` — and everything else is presentational:

```
App
 └── Dashboard            (owns state: metrics, running)
      ├── StatusCard      (renders status + fatigue score)
      ├── CameraFeed      (renders <img src=".../video_feed">)
      ├── MetricsCard     (renders EAR / MAR / pitch / counts)
      └── ControlPanel    (Start / Stop buttons)
```

Two things are worth calling out because they're easy to miss reading the components in isolation:

- **The video feed isn't fetched with JS at all.** `CameraFeed` just points an `<img>` tag at `/video_feed`. The browser's native support for `multipart/x-mixed-replace` handles the streaming — no polling, no manual frame decoding on the client.
- **The WebSocket connection is scoped to `running`.** `Dashboard` opens a `WebSocket` in a `useEffect` keyed on `running`, and tears it down in the cleanup function. Hitting Start doesn't just call the REST endpoint — it also flips `running`, which is what actually opens the socket.

REST calls go through a shared `axios` instance (`services/api.js`) pointed at the backend's origin. There's no client-side routing or global state library — a single page is all the app needs right now.

## Thread model

There are exactly two threads that matter here:

1. **The asyncio event loop** (Uvicorn) — handles all HTTP requests and the WebSocket connection.
2. **The background processing thread** — spawned by `Detector.start()`, runs `_processing_loop()` in an infinite `while self.running` loop with a small sleep between iterations.

```
 asyncio event loop                 background thread
 ┌──────────────────┐               ┌──────────────────────┐
 │ handle /start     │──spawns────▶ │ _processing_loop()    │
 │ handle /stop       │──joins────  │  cap.read()            │
 │ handle /video_feed │              │  face_mesh.process()   │
 │ handle /ws          │              │  compute EAR/MAR/pose  │
 │                      │              │  update fatigue score  │
 │  reads ───────────┐  │              │  write under lock:      │
 │                    ▼  │◀────────────│    latest_frame          │
 │            latest_frame/metrics    │    latest_metrics         │
 └──────────────────────┘               └──────────────────────┘
```

`cv2.VideoCapture.read()` and `FaceMesh.process()` are both blocking, CPU-bound calls. Running them directly inside an `async def` route handler would stall the event loop — every other request, including the WebSocket heartbeat, would queue up behind a single frame's processing time. Putting that work on its own thread means the event loop is never blocked by it; it just reads whatever the thread last wrote.

The two threads only meet at `latest_frame` and `latest_metrics`, both written and read under the same `threading.Lock`. The critical sections are short — a copy in, a copy out — so lock contention isn't a real concern at this frame rate. This is a deliberate trade-off: instead of a queue or an async-safe channel between the thread and the event loop, the API layer always reads whatever the *most recent* frame/metrics happen to be. Dropping intermediate frames is fine for a live dashboard; buffering them would just add latency.

`generate_frames()` is a plain (synchronous) generator, not an async one. FastAPI runs sync generators used in a `StreamingResponse` in a worker thread pool, so it doesn't need to be made async — it just reads the lock-protected frame and yields JPEG-encoded bytes in a loop.

## Data flow

```
Webcam
  │  cv2.VideoCapture.read()
  ▼
Raw frame (BGR)
  │  MediaPipe Face Mesh
  ▼
Landmarks
  │  EAR / MAR / head pose (see README)
  ▼
Per-frame metrics + annotated frame
  │  write (lock)
  ▼
latest_frame ──────────────┐   latest_metrics
  │                         │        │
  │ read (lock)             │        │ read (lock)
  ▼                         │        ▼
JPEG encode                 │   JSON serialize
  │                         │        │
  ▼                         │        ▼
MJPEG chunk ────────────────┘   WebSocket message
  │                                  │
  ▼                                  ▼
<img src="/video_feed">        Dashboard state (metrics)
```

Both output paths (MJPEG and WebSocket) originate from the same shared state and update independently of each other — a slow WebSocket client doesn't stall the video stream, and vice versa.

## Communication flow

| Channel | Direction | Purpose | Cadence |
|---|---|---|---|
| REST (`/start`, `/stop`, `/health`) | Frontend → Backend | Session control | On user action |
| MJPEG (`/video_feed`) | Backend → Frontend | Live annotated video | Continuous, as fast as frames are produced |
| WebSocket (`/ws`) | Backend → Frontend | Live metrics (status, score, EAR, MAR, pose, counts) | ~10/sec |

REST is only used for control actions, which are infrequent and naturally request/response. Everything that needs to update continuously — video and metrics — uses a persistent connection instead.

## Why WebSockets

The dashboard needs metrics roughly every 100ms for the status and numbers to feel live. Polling a REST endpoint at that rate means a new HTTP connection (or at least a new request/response cycle) ten times a second, for data that's usually unchanged between ticks. A WebSocket keeps one connection open and lets the backend push updates only when there's something to send, cutting out the repeated connection/serialization overhead and the latency of a request-driven model. It also matches the shape of the data: metrics are a continuous stream generated by the backend, not something the frontend is querying on demand.

MJPEG was kept as-is for video rather than also moving it onto the WebSocket — browsers already handle `multipart/x-mixed-replace` natively via a plain `<img>` tag, so there's no reason to reimplement frame delivery over a second channel.

## Why a background thread

`Detector.process_frame()` does blocking I/O (camera read) and CPU-bound inference (MediaPipe) on every call. FastAPI's request handlers run on an asyncio event loop, and a single event loop is single-threaded — anything that blocks it blocks every other request being served, including the WebSocket that's supposed to be pushing metrics in near real time.

Two alternatives were available: run the detection loop as an `async` task cooperatively yielding control, or run it on a separate OS thread. MediaPipe and OpenCV don't offer async APIs, so making them cooperative would mean manually chunking blocking calls — not practical. A background thread sidesteps that: the capture/inference loop runs continuously and independently, and the event loop only ever does cheap, non-blocking reads of whatever state the thread last produced. This keeps `/health`, `/ws`, and `/video_feed` all responsive regardless of how long a given frame takes to process.