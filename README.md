# Driver Drowsiness Detection System

This started as a single-file OpenCV script that watched a webcam feed and sounded an alarm when your eyes stayed closed too long. It's since grown into a FastAPI backend with a React dashboard on top, but the core idea hasn't changed — track facial landmarks, score fatigue frame by frame, and warn the driver before it becomes a problem.

Screenshots will be added in a future update.

## Why this exists

Drowsy driving causes thousands of accidents every year, and most existing solutions either require dedicated hardware or are locked inside proprietary car systems. This project started as an experiment to see how far a standard webcam and open-source computer vision libraries could go in replicating that kind of monitoring — no special sensors, just a camera and some math on facial geometry.

It turns eye closure, yawning, and head pose into a single fatigue score that updates every frame.

## Key features

- **Real-time webcam monitoring** — processes the video stream frame by frame with minimal latency
- **Automatic calibration** — records the driver's baseline eye-closure ratio for the first few seconds and derives a personal EAR threshold from it, instead of using one fixed value for everyone
- **Eye Aspect Ratio (EAR)** — detects prolonged or repeated eye closure
- **Mouth Aspect Ratio (MAR)** — detects yawning
- **Head pose estimation** — tracks pitch, yaw, and roll from the landmarks; sustained downward pitch counts toward the fatigue score
- **Fatigue score** — a weighted score that rises on closed eyes, head-down frames, and completed yawns, and decays when none of those are happening
- **Driver status classification** — maps the fatigue score to Normal, Tired, or Drowsy
- **Live dashboard** — React frontend showing the video feed and metrics as they update
- **Alarm system** — audio alert triggered locally via Pygame when drowsiness crosses a threshold
- **Live metrics over WebSockets** — the dashboard doesn't poll; metrics are pushed to the client as they're computed

## Tech stack

**Backend**
- Python
- FastAPI
- OpenCV
- MediaPipe Face Mesh
- NumPy
- Pygame (audio alerts)

**Frontend**
- React
- Vite
- Tailwind CSS

**Communication**
- REST API for configuration and session control
- WebSockets for streaming live metrics to the dashboard
- MJPEG streaming for the live video feed

## Project structure

```
driver-drowsiness-detection/
├── app/
│   ├── main.py             # FastAPI app + REST endpoints (/start, /stop, /video_feed, /health)
│   ├── detection.py        # Detector class — capture loop, feature extraction, fatigue scoring
│   ├── eye.py               # Eye Aspect Ratio (EAR)
│   ├── mouth.py              # Mouth Aspect Ratio (MAR)
│   ├── head_pose.py          # Head pose estimation (pitch/yaw/roll)
│   ├── fatigue.py             # Fatigue score aggregation + status thresholds
│   ├── config.py               # Calibration and threshold constants
│   ├── schemas.py               # Pydantic response models
│   ├── utils.py                  # Landmark drawing helpers
│   └── websockets/
│       └── routes.py              # WebSocket endpoint (/ws) streaming live metrics
├── frontend/
│   └── src/
│       ├── components/    # CameraFeed, ControlPanel, MetricsCard, StatusCard
│       ├── pages/
│       │   └── Dashboard.jsx
│       ├── services/
│       │   └── api.js      # Axios client for the REST API
│       ├── App.jsx
│       └── main.jsx
├── main.py                 # Standalone OpenCV script (the original, non-API version)
├── alarm.wav
├── requirements.txt
└── README.md
```

## Detection pipeline

1. **Capture** — `Detector` reads frames from the webcam in a background thread
2. **Landmark extraction** — each frame goes through MediaPipe Face Mesh
3. **Calibration** — for the first 5 seconds, EAR values are averaged and multiplied by a calibration factor (0.75) to set a per-driver EAR threshold, instead of using a fixed value for everyone
4. **Metric computation** — EAR, MAR, and head pitch/yaw/roll are computed per frame from the landmarks
5. **Fatigue scoring** — the score goes up when eyes stay closed past a frame threshold, the head stays down, or a yawn completes, and decays slowly otherwise; `get_status()` maps the score to Normal, Tired, or Drowsy
6. **Alerting** — Pygame loops the alarm sound while status is Drowsy and stops as soon as it isn't
7. **Streaming** — frames are JPEG-encoded and served over MJPEG at `/video_feed`; metrics are pushed over the `/ws` WebSocket roughly every 100ms, both consumed by the React dashboard

## Quick start

### Backend

```bash
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The backend serves the REST/WebSocket API and MJPEG stream; the frontend connects to it and renders the dashboard. Make sure your webcam is accessible to the backend process.

## Future improvements

- Dockerize backend and frontend for one-command setup
- Add authentication so sessions are tied to a specific driver profile
- Persist session history (fatigue trends over time, not just live state)
- Benchmark and document detection latency and accuracy under different lighting conditions
- Support multiple camera sources / in-vehicle camera hardware

## Author

- **Sahil Lokhande** - [@sahillokhande5841-cmyk](https://github.com/sahillokhande5841-cmyk)
