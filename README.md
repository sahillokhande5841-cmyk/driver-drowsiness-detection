# AI Driver Drowsiness & Safety Detection System

A professional, real-time AI-powered driver safety monitoring system that detects **driver fatigue**, **sleeping/microsleeps**, **prolonged yawning**, **head-down posture**, and **mobile-phone distraction** using standard webcams and computer vision deep-learning models.

---

## 🌟 Key Features

1. **Robust Real-Time Computer Vision Pipeline**
   - **478 Facial Landmarks**: Powered by Google MediaPipe Tasks Face Landmarker.
   - **Hardware Camera Auto-Probe**: DirectShow (`CAP_DSHOW`) and Windows Media Foundation auto-probing with zero-freeze standby canvas fallbacks.
   - **Decoupled Architecture**: Camera status and face tracking are strictly decoupled — losing face detection never crashes or stops the webcam feed.

2. **Accurate Biometric Algorithms**
   - **Eye Aspect Ratio (EAR)**: Uses 6 Euclidean landmark points per eye; time-based duration classification accurately discriminates normal blinks (150–350ms) from microsleeps and prolonged eye closures (≥1.3s).
   - **Automatic Baseline Calibration**: Records driver-specific resting EAR and head angle during the first 5 seconds to personalize thresholds; recalibrate anytime with one click.
   - **Mouth Aspect Ratio (MAR)**: 3 vertical lip measurements against horizontal mouth width; recognizes sustained yawning (≥1.2s) while rejecting casual talking.
   - **3D Head Pose Estimation**: Computes Pitch, Yaw, and Roll via `cv2.solvePnP` to identify sustained downward head slumping and distracted gaze angles.
   - **Mobile Phone Distraction AI**: YOLOv8 neural network (`yolov8n.pt`) detects cell phones in the driver's hand or line of sight in real time.

3. **Bilingual Alert System & Cooldowns**
   - **Hindi & English Voice Alerts**: Built-in voice alerts (e.g. *"सावधान! आप सो रहे हैं! कृपया जागें!"* / *"Warning! Drowsiness detected! Wake up!"*).
   - **Web Speech API & Local Audio**: Native browser speech synthesis with automatic Hindi/English voice selection, supported by local audio fallbacks (`wake_up.mp3`, `alert.mp3`, `alarm.wav`).
   - **Intelligent Cooldowns**: 4–6 second alert cooldowns and state-transition deduplication prevent audio stuttering and notification spam.

4. **Professional Dark UI Dashboard**
   - Sleek slate-950 dark theme built with React 19, Tailwind CSS, and Lucide icons.
   - Live MJPEG video stream with dynamic HUD overlays, 3D head-orientation axes, and bounding boxes.
   - 10Hz live WebSocket telemetry pushing EAR, MAR, pitch, blinks, yawns, and fatigue scores.
   - Real-time SVG sparkline charts with threshold reference lines.
   - Settings drawer for sensitivity adjustments, volume sliders, and language selection.
   - Chronological safety event audit log.

---

## 🏗️ Architecture

```
driver-drowsiness-detection/
├── app/
│   ├── main.py                 # FastAPI application, CORS, routers & root aliases
│   ├── detection.py            # Core Detector: frame capture, landmarker, feature extraction, HUD
│   ├── eye.py                  # Eye Aspect Ratio (EAR) & blink calculation
│   ├── mouth.py                # Mouth Aspect Ratio (MAR) & yawn detection
│   ├── head_pose.py            # 3D head pose estimation (Pitch, Yaw, Roll) via solvePnP
│   ├── phone.py                # Mobile phone distraction detection via YOLOv8
│   ├── fatigue.py              # Time-based fatigue score aggregation & status mappings
│   ├── alerts.py               # AlertManager with per-type cooldowns & bilingual messages
│   ├── utils.py                # Mathematical distances, HUD overlays, standby frames
│   ├── config.py               # Thresholds, timings, model paths, and constants
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── websockets/
│   │   └── routes.py           # Real-time WebSocket streaming at 10Hz
│   └── api/v1/                 # Modular API v1 routers (/health, /detector)
├── models/
│   ├── face_landmarker.task    # MediaPipe Face Landmarker model
│   └── yolov8n.pt              # YOLOv8 object detection model (phone detection)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CameraFeed.jsx          # Live video stream with HUD & alert banners
│   │   │   ├── StatusCard.jsx          # Safety status badge & subsystem matrix
│   │   │   ├── MetricsCard.jsx         # Biometric telemetry cards
│   │   │   ├── TelemetryCharts.jsx     # Live rolling sparkline charts
│   │   │   ├── ControlPanel.jsx        # Start, Stop, Calibrate & Quick Actions
│   │   │   ├── EventLogCard.jsx        # Chronological safety audit event log
│   │   │   ├── SettingsModal.jsx       # Sensitivity, volume & language settings
│   │   │   └── VoiceAlertHandler.jsx   # Bilingual Web Speech API voice synthesis
│   │   ├── pages/
│   │   │   └── Dashboard.jsx           # Main cockpit dashboard
│   │   ├── services/
│   │   │   └── api.js                  # Axios client for backend REST endpoints
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── tests/                      # Pytest unit tests (15 test suites)
├── main.py                     # Standalone OpenCV desktop window runner
├── alert.mp3                   # Voice audio asset
├── wake_up.mp3                 # Voice audio asset
├── alarm.wav                   # Loud alarm audio asset
├── requirements.txt            # Python dependencies
└── README.md
```

---

## 🚀 Getting Started

### 1. Backend Setup

```powershell
# Navigate to project directory
cd c:\Users\SAHIL\.gemini\antigravity-ide\scratch\reference_repo

# Run FastAPI backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend starts at `http://127.0.0.1:8000`. You can verify:
- Health check: `http://127.0.0.1:8000/health`
- Interactive Swagger docs: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup

In a second terminal window:

```powershell
cd frontend
npm.cmd run dev
```

Open your browser at **`http://localhost:5173`**.

Click **"START MONITORING"** to begin driver monitoring!

### 3. Running the Standalone Desktop Application (Optional)

If you prefer to run the direct OpenCV window without the browser dashboard:

```powershell
python main.py
```
- Press **`q`** to quit.
- Press **`r`** to recalibrate baseline.

---

## 🧪 Running Unit Tests

Run the test suite using pytest:

```powershell
python -m pytest tests/ -v
```

All 15 unit tests will execute and pass:
- Config defaults & CORS parsing
- EAR computation (open vs closed eyes)
- MAR computation (normal vs yawning)
- 3D Head pose estimation
- AlertManager cooldown deduplication & bilingual translations
- Exception handling & domain errors
- Fatigue score integration, decay & status mappings
- Endpoint health & lifecycle verification
