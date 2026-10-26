import cv2
import numpy as np
import time
import os
import threading
from typing import Optional, Dict, Any

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

from app.config import (
    FACE_LANDMARKER_MODEL,
    CAMERA_INDICES,
    FRAME_WIDTH,
    FRAME_HEIGHT,
    CALIBRATION_TIME,
    CALIBRATION_FACTOR,
    DEFAULT_EAR_THRESHOLD,
    MIN_EAR_THRESHOLD,
    MAX_EAR_THRESHOLD,
    MIN_CALIBRATION_SAMPLES,
    BLINK_MIN_DURATION,
    BLINK_MAX_DURATION,
    DROWSINESS_WARNING_TIME,
    CRITICAL_DROWSINESS_TIME,
    RECOVERY_OPEN_TIME,
    MAR_THRESHOLD,
    YAWN_MIN_DURATION,
    YAWN_COOLDOWN,
    HEAD_DOWN_PITCH_THRESHOLD,
    HEAD_DOWN_MIN_DURATION,
    HEAD_TURN_YAW_THRESHOLD,
    HEAD_TURN_MIN_DURATION,
    PHONE_CHECK_INTERVAL
)

from app.eye import calculate_ear, draw_eyes
from app.mouth import calculate_mar, draw_mouth
from app.head_pose import get_head_pose, draw_head_pose
from app.phone import PhoneDetector
from app.fatigue import update_fatigue_score, get_driver_status
from app.alerts import AlertManager
from app.utils import draw_pill_badge, create_standby_frame

class Detector:
    def __init__(self):
        self.cap: Optional[cv2.VideoCapture] = None
        self.landmarker = None
        self.phone_detector = PhoneDetector()
        self.alert_manager = AlertManager()

        self.running = False
        self.camera_status = "stopped"  # "connected", "reconnecting", "error", "stopped"
        self.face_detected = False
        self.camera_index = 0

        self.lock = threading.Lock()
        self.processing_thread: Optional[threading.Thread] = None

        self.latest_frame: Optional[np.ndarray] = None
        self.latest_metrics: Dict[str, Any] = {}

        # Initialize dynamic state
        self._reset_state()

    def _init_landmarker(self):
        """Initializes MediaPipe Tasks FaceLandmarker."""
        if not os.path.exists(FACE_LANDMARKER_MODEL):
            print(f"[Detector] ERROR: Model not found at {FACE_LANDMARKER_MODEL}")
            return

        try:
            base_options = mp_python.BaseOptions(model_asset_path=FACE_LANDMARKER_MODEL)
            options = mp_vision.FaceLandmarkerOptions(
                base_options=base_options,
                running_mode=mp_vision.RunningMode.IMAGE,
                num_faces=1,
                min_face_detection_confidence=0.5,
                min_face_presence_confidence=0.5,
                min_tracking_confidence=0.5,
                output_face_blendshapes=False
            )
            self.landmarker = mp_vision.FaceLandmarker.create_from_options(options)
            print("[Detector] MediaPipe FaceLandmarker successfully initialized.")
        except Exception as e:
            print(f"[Detector] Failed to initialize FaceLandmarker: {e}")
            self.landmarker = None

    def _reset_state(self):
        """Resets dynamic detection state for calibration and tracking."""
        self.calibrating = True
        self.calibration_start = time.time()
        self.ear_values = []
        self.pitch_values = []
        self.ear_threshold = DEFAULT_EAR_THRESHOLD
        self.mar_threshold = MAR_THRESHOLD
        self.baseline_pitch = 0.0

        # Metrics
        self.ear = 0.0
        self.mar = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.roll = 0.0

        self.blink_count = 0
        self.yawn_count = 0

        # Time-based tracking
        self.eye_closure_start: Optional[float] = None
        self.open_eye_start: Optional[float] = None
        self.eye_closed_prolonged = False
        self.eye_closed_severe = False

        self.yawn_start: Optional[float] = None
        self.is_yawning = False
        self.last_yawn_counted_time = 0.0

        self.head_down_start: Optional[float] = None
        self.head_down = False

        self.head_turn_start: Optional[float] = None
        self.head_turned = False

        self.phone_start: Optional[float] = None
        self.phone_distracted = False
        self.detected_phones = []

        self.fatigue_score = 0.0
        self.status = "INITIALIZING"
        self.face_lost_start: Optional[float] = None

        self.last_frame_time = time.time()
        self.fps = 0.0
        self.frame_count = 0

    def start(self):
        """Starts webcam capture and background processing thread."""
        if self.running:
            print("[Detector] Already running.")
            return

        self._reset_state()
        self.running = True
        self.camera_status = "connecting"

        # Start capture and processing in background
        self.processing_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.processing_thread.start()
        print("[Detector] Processing thread launched.")

    def stop(self):
        """Stops background loop and releases camera."""
        self.running = False
        if self.processing_thread is not None:
            self.processing_thread.join(timeout=1.5)
            self.processing_thread = None

        self._release_camera()
        self.camera_status = "stopped"
        with self.lock:
            self.latest_frame = None
            self.latest_metrics = {}
        print("[Detector] Stopped.")

    def recalibrate(self):
        """Triggers a fresh calibration routine."""
        with self.lock:
            self.calibrating = True
            self.calibration_start = time.time()
            self.ear_values = []
            self.pitch_values = []
            self.status = "CALIBRATING"
        print("[Detector] Recalibration initiated.")

    def _open_camera(self) -> bool:
        """Attempts to open camera trying CAP_DSHOW on Windows then default."""
        self._release_camera()

        for idx in CAMERA_INDICES:
            try:
                # Try DirectShow on Windows for instant, reliable hardware open
                cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW) if os.name == 'nt' else cv2.VideoCapture(idx)
                if cap.isOpened():
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
                    cap.set(cv2.CAP_PROP_FPS, 30)
                    ret, test_frame = cap.read()
                    if ret and test_frame is not None:
                        self.cap = cap
                        self.camera_index = idx
                        self.camera_status = "connected"
                        print(f"[Detector] Camera index {idx} opened successfully.")
                        return True
                    cap.release()
            except Exception as e:
                print(f"[Detector] Error opening camera index {idx}: {e}")

        # Fallback to default backend
        try:
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, test_frame = cap.read()
                if ret and test_frame is not None:
                    self.cap = cap
                    self.camera_index = 0
                    self.camera_status = "connected"
                    print("[Detector] Default camera 0 opened successfully.")
                    return True
                cap.release()
        except Exception:
            pass

        self.camera_status = "error"
        print("[Detector] Failed to open any camera.")
        return False

    def _release_camera(self):
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

    def _run_loop(self):
        """Main processing thread loop."""
        self._init_landmarker()
        consecutive_read_failures = 0

        while self.running:
            # Connect or reconnect camera if needed
            if self.cap is None or not self.cap.isOpened():
                success = self._open_camera()
                if not success:
                    with self.lock:
                        self.status = "CAMERA_ERROR"
                        self.camera_status = "error"
                        self.latest_frame = create_standby_frame(
                            FRAME_WIDTH, FRAME_HEIGHT,
                            message="WEBCAM UNAVAILABLE",
                            subtext="Check camera connection or privacy settings"
                        )
                        self.latest_metrics = self._build_metrics()
                    time.sleep(1.0)
                    continue

            ret, frame = self.cap.read()
            if not ret or frame is None:
                consecutive_read_failures += 1
                if consecutive_read_failures > 10:
                    self.camera_status = "reconnecting"
                    self.status = "CAMERA_ERROR"
                    self._release_camera()
                    consecutive_read_failures = 0
                time.sleep(0.03)
                continue

            consecutive_read_failures = 0
            self.camera_status = "connected"
            self.frame_count += 1

            # Process the frame through detection pipeline
            self._process_single_frame(frame)

            # Cap loop rate to ~30 FPS
            time.sleep(0.01)

    def _process_single_frame(self, frame: np.ndarray):
        """Runs Face Landmarker, Phone Detection, and Fatigue Computation."""
        now = time.time()
        dt = max(0.001, now - self.last_frame_time)
        self.last_frame_time = now
        self.fps = 0.9 * self.fps + 0.1 * (1.0 / dt)

        height, width = frame.shape[:2]
        display_frame = frame.copy()

        # 1. Mobile Phone Distraction Detection (run every N frames for speed)
        if self.frame_count % PHONE_CHECK_INTERVAL == 0:
            self.detected_phones = self.phone_detector.detect(frame)
            if len(self.detected_phones) > 0:
                if self.phone_start is None:
                    self.phone_start = now
                if (now - self.phone_start) >= 0.8:
                    self.phone_distracted = True
                    self.alert_manager.trigger("PHONE_DISTRACTION", "Mobile phone in driver hand/view")
            else:
                self.phone_start = None
                self.phone_distracted = False

        # Draw detected phones if present
        if len(self.detected_phones) > 0:
            self.phone_detector.draw_detections(display_frame, self.detected_phones)

        # 2. Face Landmark Detection
        landmarks = None
        if self.landmarker is not None:
            try:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                res = self.landmarker.detect(mp_image)
                if res and res.face_landmarks and len(res.face_landmarks) > 0:
                    landmarks = res.face_landmarks[0]
            except Exception as e:
                print(f"[Detector] Landmarker error: {e}")
                landmarks = None

        # 3. Handle Face Presence / Absence with 1.2s Hysteresis
        if landmarks is not None:
            self.face_detected = True
            self.face_lost_start = None
            self._process_face(display_frame, landmarks, width, height, now, dt)
        else:
            if self.face_lost_start is None:
                self.face_lost_start = now
            face_absent_duration = now - self.face_lost_start

            # Only switch to NO_FACE and display searching HUD after 1.2s sustained loss
            if face_absent_duration > 1.2:
                self.face_detected = False
                self.status = "NO_FACE"
                self.eye_closure_start = None
                self.open_eye_start = None
                self.yawn_start = None
                self.head_down_start = None
                self.head_turn_start = None

                draw_pill_badge(
                    display_frame,
                    "SEARCHING FOR DRIVER FACE",
                    (width // 2 - 150, height // 2 - 20),
                    bg_color=(20, 20, 30),
                    text_color=(0, 165, 255),
                    font_scale=0.6,
                    thickness=2,
                    padding=(14, 10)
                )

        # 4. Top Status Header Overlay
        self._draw_status_bar(display_frame, width)

        # 5. Thread-safe publish
        with self.lock:
            self.latest_frame = display_frame
            self.latest_metrics = self._build_metrics()

    def _process_face(self, frame: np.ndarray, landmarks, width: int, height: int, now: float, dt: float):
        """Processes facial landmarks: EAR, MAR, Head Pose, and Fatigue."""
        # Calculate aspect ratios with accurate pixel scaling
        self.ear, left_ear, right_ear = calculate_ear(landmarks, width, height)
        self.mar = calculate_mar(landmarks, width, height)
        self.pitch, self.yaw, self.roll, nose_pt = get_head_pose(landmarks, width, height)

        # A. Calibration Phase (First 5 seconds of good face detection)
        if self.calibrating:
            time_spent = now - self.calibration_start
            time_left = max(0.0, CALIBRATION_TIME - time_spent)
            self.status = f"CALIBRATING ({time_left:.1f}s)"

            # Record all valid open-eye samples (filter extreme noise below 0.08)
            if self.ear > 0.08:
                self.ear_values.append(self.ear)
                self.pitch_values.append(self.pitch)

            if time_spent >= CALIBRATION_TIME:
                if len(self.ear_values) >= MIN_CALIBRATION_SAMPLES:
                    avg_ear = sum(self.ear_values) / len(self.ear_values)
                    self.ear_threshold = float(np.clip(avg_ear * CALIBRATION_FACTOR, MIN_EAR_THRESHOLD, MAX_EAR_THRESHOLD))
                    self.baseline_pitch = float(np.median(self.pitch_values))
                    print(f"[Detector] Calibration complete! Resting EAR: {avg_ear:.3f}, Threshold: {self.ear_threshold:.3f}, Baseline Pitch: {self.baseline_pitch:.1f}°")
                else:
                    self.ear_threshold = DEFAULT_EAR_THRESHOLD
                    self.baseline_pitch = 0.0
                    print("[Detector] Insufficient calibration samples. Using safe defaults.")
                self.calibrating = False
        else:
            # B. Eye Closure & Blink Timing with Immediate Recovery
            is_eye_below_thresh = self.ear < self.ear_threshold
            is_recovering = False

            if is_eye_below_thresh:
                self.open_eye_start = None
                if self.eye_closure_start is None:
                    self.eye_closure_start = now
                closure_duration = now - self.eye_closure_start

                if closure_duration >= DROWSINESS_WARNING_TIME:
                    self.eye_closed_prolonged = True
                    self.alert_manager.trigger("DROWSINESS_WARNING", f"Prolonged eye closure ({closure_duration:.1f}s)")

                if closure_duration >= CRITICAL_DROWSINESS_TIME:
                    self.eye_closed_severe = True
                    self.alert_manager.trigger("CRITICAL_DROWSINESS", f"Severe microsleep / sleeping ({closure_duration:.1f}s)")
            else:
                # Eyes are open!
                if self.eye_closure_start is not None:
                    closure_duration = now - self.eye_closure_start
                    if BLINK_MIN_DURATION <= closure_duration <= BLINK_MAX_DURATION:
                        self.blink_count += 1
                    self.eye_closure_start = None

                # Immediate open-eye recovery confirmation
                if self.open_eye_start is None:
                    self.open_eye_start = now
                open_duration = now - self.open_eye_start

                if open_duration >= RECOVERY_OPEN_TIME:
                    self.eye_closed_prolonged = False
                    self.eye_closed_severe = False
                    self.alert_manager.clear_active_alert()
                    is_recovering = True

            # C. Yawning Detection (Time-based MAR)
            is_mouth_wide = self.mar > self.mar_threshold
            new_yawn_completed = False

            if is_mouth_wide:
                if self.yawn_start is None:
                    self.yawn_start = now
                yawn_duration = now - self.yawn_start

                if yawn_duration >= YAWN_MIN_DURATION:
                    self.is_yawning = True
                    self.alert_manager.trigger("YAWNING", f"Yawning detected ({yawn_duration:.1f}s)")
            else:
                if self.yawn_start is not None:
                    yawn_duration = now - self.yawn_start
                    if yawn_duration >= YAWN_MIN_DURATION:
                        if (now - self.last_yawn_counted_time) >= YAWN_COOLDOWN:
                            self.yawn_count += 1
                            new_yawn_completed = True
                            self.last_yawn_counted_time = now
                self.yawn_start = None
                self.is_yawning = False

            # D. Head Pose & Downward Posture (Pitch relative to resting baseline)
            # In our corrected camera frame, positive pitch means nodding head DOWN
            relative_pitch = self.pitch - self.baseline_pitch
            is_head_pitch_down = relative_pitch > HEAD_DOWN_PITCH_THRESHOLD

            if is_head_pitch_down:
                if self.head_down_start is None:
                    self.head_down_start = now
                if (now - self.head_down_start) >= HEAD_DOWN_MIN_DURATION:
                    self.head_down = True
                    self.alert_manager.trigger("HEAD_DOWN", f"Head pitched down ({relative_pitch:.1f}°)")
            else:
                self.head_down_start = None
                self.head_down = False

            # E. Distracted Gaze (Yaw turning left/right)
            is_head_turned = abs(self.yaw) > HEAD_TURN_YAW_THRESHOLD
            if is_head_turned:
                if self.head_turn_start is None:
                    self.head_turn_start = now
                if (now - self.head_turn_start) >= HEAD_TURN_MIN_DURATION:
                    self.head_turned = True
            else:
                self.head_turn_start = None
                self.head_turned = False

            # F. Update Fatigue Score with Dynamic Recovery
            self.fatigue_score = update_fatigue_score(
                current_score=self.fatigue_score,
                dt=dt,
                eye_closed_prolonged=self.eye_closed_prolonged,
                head_down=self.head_down,
                yawn_completed=new_yawn_completed,
                phone_distracted=self.phone_distracted,
                is_recovering=is_recovering
            )

            # G. Determine Centralized Driver Status
            self.status = get_driver_status(
                fatigue_score=self.fatigue_score,
                eye_closed_severe=self.eye_closed_severe,
                eye_closed_prolonged=self.eye_closed_prolonged,
                phone_distracted=self.phone_distracted,
                head_down_prolonged=self.head_down or self.head_turned,
                is_calibrating=False,
                face_detected=True,
                camera_connected=(self.camera_status == "connected")
            )

        # Visual Overlays on Frame
        is_closed_visual = (self.eye_closure_start is not None) and ((now - self.eye_closure_start) > 0.3)
        draw_eyes(frame, landmarks, width, height, is_closed=is_closed_visual)
        draw_mouth(frame, landmarks, width, height, is_yawning=self.is_yawning)
        draw_head_pose(frame, self.pitch, self.yaw, self.roll, nose_pt)

    def _draw_status_bar(self, frame: np.ndarray, width: int):
        """Draws clean HUD status pill and telemetry bars on frame."""
        status_colors = {
            "NORMAL": (0, 200, 100),              # Emerald Green
            "FATIGUE_WARNING": (0, 165, 255),     # Amber
            "TIRED": (0, 165, 255),               # Amber
            "DROWSINESS_WARNING": (0, 120, 255),  # Deep Amber/Orange
            "CRITICAL_DROWSINESS": (0, 0, 240),   # Critical Red
            "DROWSY": (0, 0, 240),                # Red
            "DISTRACTED_PHONE": (0, 69, 255),     # Red-Orange
            "DISTRACTED_HEAD_DOWN": (0, 140, 255),
            "CALIBRATING": (255, 200, 0),         # Cyan
            "NO_FACE": (120, 120, 140),           # Muted gray
            "CAMERA_ERROR": (0, 0, 220),          # Red error
            "INITIALIZING": (100, 100, 100)
        }
        status_key = self.status.split(" ")[0] if self.status.startswith("CALIBRATING") else self.status
        color = status_colors.get(status_key, (150, 150, 150))
        label = self.status.replace("_", " ")

        # Top-left Status Pill
        draw_pill_badge(frame, f"STATUS: {label}", (16, 16), color, (255, 255, 255), 0.55, 1)

        # Top-right FPS / Camera badge
        cam_color = (0, 200, 100) if self.camera_status == "connected" else (0, 0, 220)
        draw_pill_badge(
            frame,
            f"CAM {self.camera_index} | {int(self.fps)} FPS",
            (width - 150, 16),
            (25, 25, 35),
            cam_color,
            0.45,
            1
        )

        # Bottom telemetry overlay strip
        bottom_y = frame.shape[0] - 30
        telemetry = f"EAR: {self.ear:.2f}/{self.ear_threshold:.2f} | MAR: {self.mar:.2f} | PITCH: {self.pitch:+.0f}° | BLINKS: {self.blink_count} | YAWNS: {self.yawn_count}"
        draw_pill_badge(
            frame,
            telemetry,
            (16, bottom_y),
            (20, 20, 28),
            (220, 220, 220),
            0.45,
            1,
            padding=(8, 4)
        )

    def _build_metrics(self) -> Dict[str, Any]:
        """Constructs full telemetry payload for WebSockets and API."""
        active_alert = self.alert_manager.get_active_alert()
        events = self.alert_manager.get_events(15)

        return {
            "status": self.status,
            "cameraStatus": self.camera_status,
            "faceDetected": self.face_detected,
            "fatigueScore": round(float(self.fatigue_score), 2),
            "ear": round(float(self.ear), 3),
            "earThreshold": round(float(self.ear_threshold), 3),
            "mar": round(float(self.mar), 3),
            "marThreshold": round(float(self.mar_threshold), 3),
            "pitch": round(float(self.pitch), 1),
            "yaw": round(float(self.yaw), 1),
            "roll": round(float(self.roll), 1),
            "blinkCount": int(self.blink_count),
            "yawnCount": int(self.yawn_count),
            "isEyeClosed": bool(self.eye_closed_prolonged or self.eye_closed_severe),
            "isYawning": bool(self.is_yawning),
            "isHeadDown": bool(self.head_down),
            "isPhoneDistracted": bool(self.phone_distracted),
            "fps": round(float(self.fps), 1),
            "running": bool(self.running),
            "activeAlert": active_alert,
            "recentEvents": events,
            "calibrating": bool(self.calibrating)
        }

    def get_metrics(self) -> Dict[str, Any]:
        with self.lock:
            return self.latest_metrics.copy()

    def generate_frames(self):
        """Generator yielding MJPEG frame stream continuously without stalling."""
        while self.running:
            with self.lock:
                frame = self.latest_frame.copy() if self.latest_frame is not None else None

            if frame is None:
                frame = create_standby_frame(FRAME_WIDTH, FRAME_HEIGHT, "INITIALIZING VIDEO", "Connecting to camera stream...")

            ret, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not ret:
                time.sleep(0.02)
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + buffer.tobytes()
                + b"\r\n"
            )
            time.sleep(0.025)  # ~35-40 FPS max streaming rate
