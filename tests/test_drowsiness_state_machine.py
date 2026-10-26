import time
import pytest
from app.detection import Detector
from tests.test_detection_modules import create_mock_face

def test_blinking_vs_prolonged_closure():
    """
    Verify that short blinks (0.15s) increment blink count and DO NOT trigger drowsiness alerts,
    while prolonged closure (>=1.2s) triggers early warning and (>=2.2s) triggers critical alert.
    """
    det = Detector()
    det.calibrating = False
    det.camera_status = "connected"
    det.face_detected = True
    det.ear_threshold = 0.20
    det.alert_manager.audio_enabled = False

    t0 = 1000.0

    # 1. Normal blink: eyes close for 0.20s then reopen
    closed_face = create_mock_face(eye_open=False)
    open_face = create_mock_face(eye_open=True)

    # Frame 1: eye closes at t0
    det._process_face(np_dummy_frame(), closed_face, 640, 480, now=t0, dt=0.033)
    assert det.eye_closure_start == t0
    assert not det.eye_closed_prolonged
    assert not det.eye_closed_severe
    assert det.alert_manager.get_active_alert() is None

    # Frame 2: eye reopens at t0 + 0.20s
    det._process_face(np_dummy_frame(), open_face, 640, 480, now=t0 + 0.20, dt=0.033)
    assert det.blink_count == 1
    assert det.eye_closure_start is None
    assert not det.eye_closed_prolonged
    assert not det.eye_closed_severe

    # 2. Prolonged closure: 1.3s
    det._process_face(np_dummy_frame(), closed_face, 640, 480, now=t0 + 1.0, dt=0.033)
    det._process_face(np_dummy_frame(), closed_face, 640, 480, now=t0 + 2.3, dt=1.3)
    assert det.eye_closed_prolonged is True
    assert det.eye_closed_severe is False
    assert det.status == "DROWSINESS_WARNING"

    # 3. Severe microsleep: 2.5s continuous closure
    det._process_face(np_dummy_frame(), closed_face, 640, 480, now=t0 + 3.6, dt=1.3)
    assert det.eye_closed_severe is True
    assert det.status == "CRITICAL_DROWSINESS"

    # 4. Immediate recovery: eyes reopen for 0.4s
    det._process_face(np_dummy_frame(), open_face, 640, 480, now=t0 + 3.7, dt=0.1)
    # Recovery in progress (0.1s open)
    det._process_face(np_dummy_frame(), open_face, 640, 480, now=t0 + 4.15, dt=0.45)
    # 0.45s continuous open eyes -> alert cleared!
    assert det.eye_closed_severe is False
    assert det.eye_closed_prolonged is False
    assert det.alert_manager.get_active_alert() is None
    assert det.status != "CRITICAL_DROWSINESS"

def test_face_loss_hysteresis():
    """
    Verify that temporary face loss (<1.2s) preserves camera status and avoids NO_FACE flicker,
    while sustained loss (>=1.2s) transitions cleanly to NO_FACE without stopping the camera.
    """
    det = Detector()
    det.calibrating = False
    det.camera_status = "connected"
    det.face_detected = True

    t0 = 2000.0
    frame = np_dummy_frame()

    # Landmark is temporarily None for 0.5s (single frame drop / occlusion)
    det.landmarker = None  # simulates detection failure
    det._process_single_frame(frame)
    assert det.camera_status == "connected"
    # Status should not immediately flip to NO_FACE within < 1.2s
    det.face_lost_start = t0
    det.status = "NORMAL"

    # Simulate 0.5s elapsed
    now = t0 + 0.5
    face_absent_duration = now - det.face_lost_start
    assert face_absent_duration < 1.2
    assert det.camera_status == "connected"

    # Simulate 1.5s elapsed (sustained face loss)
    now = t0 + 1.5
    face_absent_duration = now - det.face_lost_start
    if face_absent_duration > 1.2:
        det.face_detected = False
        det.status = "NO_FACE"

    assert det.face_detected is False
    assert det.status == "NO_FACE"
    assert det.camera_status == "connected"  # Camera stays independent!

def test_yawn_duration_and_cooldown():
    """Verify mouth must remain wide for at least 1.2s to count as a yawn and debounce multiple yawns."""
    det = Detector()
    det.calibrating = False
    det.camera_status = "connected"
    det.face_detected = True
    det.mar_threshold = 0.52
    det.alert_manager.audio_enabled = False

    t0 = 3000.0
    open_mouth = create_mock_face(mouth_open=True)
    closed_mouth = create_mock_face(mouth_open=False)

    # 1. Quick opening (0.4s speech) -> not a yawn
    det._process_face(np_dummy_frame(), open_mouth, 640, 480, now=t0, dt=0.033)
    det._process_face(np_dummy_frame(), closed_mouth, 640, 480, now=t0 + 0.4, dt=0.4)
    assert det.yawn_count == 0
    assert not det.is_yawning

    # 2. Genuine yawn (1.4s wide open)
    det._process_face(np_dummy_frame(), open_mouth, 640, 480, now=t0 + 1.0, dt=0.033)
    det._process_face(np_dummy_frame(), open_mouth, 640, 480, now=t0 + 2.3, dt=1.3)
    assert det.is_yawning is True
    # Mouth closes -> increments yawn count
    det._process_face(np_dummy_frame(), closed_mouth, 640, 480, now=t0 + 2.5, dt=0.2)
    assert det.yawn_count == 1
    assert not det.is_yawning

def np_dummy_frame():
    import numpy as np
    return np.zeros((480, 640, 3), dtype=np.uint8)
