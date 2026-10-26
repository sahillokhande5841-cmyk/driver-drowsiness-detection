# Setup Guide

## Prerequisites

- Python 3.10+ (MediaPipe doesn't yet support the latest Python releases — if `pip install` fails on `mediapipe`, try 3.10–3.12)
- Node.js 18+
- A working webcam

## 1. Clone the repository

```bash
git clone https://github.com/sahillokhande5841-cmyk/driver-drowsiness-detection.git
cd driver-drowsiness-detection
```

## 2. Create a Python virtual environment

```bash
python -m venv venv
```

Activate it:

```bash
# macOS / Linux
source venv/bin/activate

# Windows (Command Prompt)
venv\Scripts\activate.bat

# Windows (PowerShell)
# If script execution is disabled, first run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1
```

## 3. Configure Environment Variables

Copy the example environment configuration:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# macOS / Linux
cp .env.example .env
```

## 4. Install backend dependencies

```bash
pip install -r requirements.txt
```

## 5. Run initial tests

```bash
pytest
```

## 6. Run the FastAPI backend

From the repo root (not inside `app/`):

```bash
uvicorn app.main:app --reload
```

Backend runs at `http://127.0.0.1:8000`. Confirm it's up:

```bash
# Health check endpoint
curl http://127.0.0.1:8000/api/health
```

## 7. Install frontend dependencies

In a new terminal:

```bash
cd frontend
npm install
```

## 8. Run the React frontend

```bash
npm run dev
```

Frontend runs at `http://localhost:5173`.

## 9. Open the dashboard

Visit `http://localhost:5173` in your browser and click **Start**. Grant webcam access if prompted.

---

## Troubleshooting

### Webcam unavailable

- Close any other app using the camera (Zoom, Teams, another browser tab) — most OSes only let one process access it at a time.
- If you have multiple cameras, `cv2.VideoCapture(0)` in `app/detection.py` may be pointing at the wrong one. Try changing the index to `1`, `2`, etc.
- On Linux, confirm the camera is visible with `ls /dev/video*` and that your user has permission to access it.
- On macOS, check System Settings → Privacy & Security → Camera and make sure your terminal or IDE is allowed.

### Python dependency errors

- Make sure the virtual environment is activated before installing or running anything — `which python` (macOS/Linux) or `where python` (Windows) should point inside `venv/`.
- Upgrade pip first if installs fail oddly: `pip install --upgrade pip`.
- `mediapipe` and `opencv-python` are the most version-sensitive packages here. If install fails, check that your Python version is supported by the pinned `mediapipe` version in `requirements.txt`.

### Node modules issues

- Delete and reinstall if `npm install` behaves inconsistently:
  ```bash
  rm -rf node_modules package-lock.json
  npm install
  ```
- Make sure you're running `npm install` inside `frontend/`, not the repo root — there's no `package.json` at the top level.

### CORS errors in the browser console

- The backend only allows `http://localhost:5173` by default (set in `app/main.py`, `CORSMiddleware`). If you're running the frontend on a different port or host, update `allow_origins` there and restart the backend.
- CORS errors also show up if the backend isn't running at all — check the "Backend not running" section below before assuming it's a CORS config issue.

### Backend not running / dashboard stuck on "INITIALIZING"

- Confirm the backend process is actually up: `curl http://127.0.0.1:8000/health` should return `{"status": "healthy"}`.
- The dashboard won't show live metrics until you click **Start**, which calls `POST /start` — the WebSocket connection only opens after that.
- If `/start` returns an error, check the backend terminal output — it usually means the camera couldn't be opened (see Webcam section above).