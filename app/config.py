import os

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
FACE_LANDMARKER_MODEL = os.path.join(MODELS_DIR, "face_landmarker.task")
YOLO_MODEL = os.path.join(MODELS_DIR, "yolov8n.pt")

# Camera Configuration
CAMERA_INDICES = [0, 1, 2]
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
TARGET_FPS = 30

# Calibration Settings
CALIBRATION_TIME = 5.0          # seconds
CALIBRATION_FACTOR = 0.72        # 72% of open-eye resting baseline
DEFAULT_EAR_THRESHOLD = 0.20     # Safe default if calibration skipped
MIN_EAR_THRESHOLD = 0.14         # Floor limit for smaller/distant eyes
MAX_EAR_THRESHOLD = 0.28         # Ceiling limit
MIN_CALIBRATION_SAMPLES = 20

# Eye Closure & Blink Timing (Time-based in seconds)
BLINK_MIN_DURATION = 0.08        # minimum blink duration
BLINK_MAX_DURATION = 0.40        # maximum blink duration (normal blink is 0.15 - 0.35s)
DROWSINESS_WARNING_TIME = 1.2    # Continuous closure duration for early drowsiness warning
CRITICAL_DROWSINESS_TIME = 2.2   # Continuous closure duration for severe microsleep / alarm
RECOVERY_OPEN_TIME = 0.4         # Continuous open-eye duration to confirm recovery and silence alert

# Yawn Detection (MAR)
MAR_THRESHOLD = 0.52             # Ratio threshold distinguishing yawning from speech
YAWN_MIN_DURATION = 1.2          # Must stay open for at least 1.2s to be a genuine yawn
YAWN_COOLDOWN = 3.5              # Seconds between counting consecutive yawns

# Head Pose Settings (Degrees)
HEAD_DOWN_PITCH_THRESHOLD = 18.0 # Degrees down from resting pitch baseline
HEAD_DOWN_MIN_DURATION = 1.5     # Sustained downward pitch duration
HEAD_TURN_YAW_THRESHOLD = 28.0   # Horizontal gaze turning threshold
HEAD_TURN_MIN_DURATION = 2.0     # Sustained distracted gaze duration

# Mobile Phone Distraction
PHONE_CONF_THRESHOLD = 0.40      # YOLO confidence threshold
PHONE_MIN_DURATION = 0.9         # Sustained phone detection duration in seconds
PHONE_CHECK_INTERVAL = 3         # Run YOLO every N frames to maintain 30 FPS

# Fatigue Scoring & Decay Rates
MAX_FATIGUE_SCORE = 10.0
NORMAL_DECAY_RATE = 0.15         # Passive score decay per second when alert
ACTIVE_RECOVERY_RATE = 2.0       # Accelerated decay per second when recovering from a warning
EYE_CLOSED_WEIGHT = 1.0          # Added per second of closed eyes
HEAD_DOWN_WEIGHT = 0.6           # Added per second of head down
YAWN_WEIGHT = 2.0                # Added per completed yawn
PHONE_WEIGHT = 1.5               # Added per second of phone distraction

# State Machine Thresholds
FATIGUE_WARNING_SCORE = 3.5
DROWSINESS_WARNING_SCORE = 6.0
CRITICAL_DROWSINESS_SCORE = 8.5

# Audio & Voice Alert Paths
ALARM_SOUND = os.path.join(BASE_DIR, "alarm.wav")
ALERT_MP3 = os.path.join(BASE_DIR, "alert.mp3")
WAKE_UP_MP3 = os.path.join(BASE_DIR, "wake_up.mp3")

# Alert Cooldowns (seconds)
ALERT_COOLDOWN_DROWSY = 4.0
ALERT_COOLDOWN_YAWN = 6.0
ALERT_COOLDOWN_PHONE = 5.0
ALERT_COOLDOWN_HEAD = 5.0
