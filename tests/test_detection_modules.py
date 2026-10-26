import pytest
import numpy as np
from app.eye import calculate_ear, LEFT_EYE, RIGHT_EYE
from app.mouth import calculate_mar, MOUTH_HORIZONTAL, MOUTH_VERTICAL_CENTER
from app.head_pose import get_head_pose, MODEL_POINTS
from app.phone import PhoneDetector
from app.alerts import AlertManager

class MockLandmark:
    def __init__(self, x, y, z=0.0):
        self.x = x
        self.y = y
        self.z = z

def create_mock_face(eye_open=True, mouth_open=False):
    """Creates a mock face with 478 landmarks for unit testing."""
    landmarks = [MockLandmark(0.5, 0.5) for _ in range(478)]

    # Left eye outer corner (33) and inner corner (133)
    landmarks[33] = MockLandmark(0.30, 0.40)
    landmarks[133] = MockLandmark(0.40, 0.40)

    # Vertical landmarks for left eye
    if eye_open:
        landmarks[160] = MockLandmark(0.33, 0.36)
        landmarks[144] = MockLandmark(0.33, 0.44)
        landmarks[158] = MockLandmark(0.37, 0.36)
        landmarks[153] = MockLandmark(0.37, 0.44)
    else:
        # Eyelids touching (closed)
        landmarks[160] = MockLandmark(0.33, 0.40)
        landmarks[144] = MockLandmark(0.33, 0.40)
        landmarks[158] = MockLandmark(0.37, 0.40)
        landmarks[153] = MockLandmark(0.37, 0.40)

    # Right eye inner corner (362) and outer corner (263)
    landmarks[362] = MockLandmark(0.60, 0.40)
    landmarks[263] = MockLandmark(0.70, 0.40)

    if eye_open:
        landmarks[385] = MockLandmark(0.63, 0.36)
        landmarks[380] = MockLandmark(0.63, 0.44)
        landmarks[387] = MockLandmark(0.67, 0.36)
        landmarks[373] = MockLandmark(0.67, 0.44)
    else:
        landmarks[385] = MockLandmark(0.63, 0.40)
        landmarks[380] = MockLandmark(0.63, 0.40)
        landmarks[387] = MockLandmark(0.67, 0.40)
        landmarks[373] = MockLandmark(0.67, 0.40)

    # Mouth landmarks (78, 308) horizontal
    landmarks[78] = MockLandmark(0.40, 0.70)
    landmarks[308] = MockLandmark(0.60, 0.70)

    if mouth_open:
        landmarks[13] = MockLandmark(0.50, 0.62)
        landmarks[14] = MockLandmark(0.50, 0.78)
        landmarks[82] = MockLandmark(0.45, 0.63)
        landmarks[87] = MockLandmark(0.45, 0.77)
        landmarks[312] = MockLandmark(0.55, 0.63)
        landmarks[317] = MockLandmark(0.55, 0.77)
    else:
        landmarks[13] = MockLandmark(0.50, 0.70)
        landmarks[14] = MockLandmark(0.50, 0.70)
        landmarks[82] = MockLandmark(0.45, 0.70)
        landmarks[87] = MockLandmark(0.45, 0.70)
        landmarks[312] = MockLandmark(0.55, 0.70)
        landmarks[317] = MockLandmark(0.55, 0.70)

    return landmarks

def test_ear_calculation_open_vs_closed():
    """Verify EAR calculation properly discriminates open vs closed eyes."""
    open_face = create_mock_face(eye_open=True)
    ear_open, left_open, right_open = calculate_ear(open_face)
    assert ear_open > 0.30

    closed_face = create_mock_face(eye_open=False)
    ear_closed, left_closed, right_closed = calculate_ear(closed_face)
    assert ear_closed < 0.05
    assert ear_open > ear_closed * 4.0

def test_mar_calculation_normal_vs_yawning():
    """Verify MAR calculation properly discriminates closed vs wide open mouth."""
    normal_face = create_mock_face(mouth_open=False)
    mar_normal = calculate_mar(normal_face)
    assert mar_normal < 0.10

    yawn_face = create_mock_face(mouth_open=True)
    mar_yawn = calculate_mar(yawn_face)
    assert mar_yawn > 0.50
    assert mar_yawn > mar_normal * 4.0

def test_head_pose_calculation():
    """Verify head pose returns pitch, yaw, roll numeric values."""
    mock_face = create_mock_face()
    pitch, yaw, roll, nose_pt = get_head_pose(mock_face, width=640, height=480)
    assert isinstance(pitch, float)
    assert isinstance(yaw, float)
    assert isinstance(roll, float)
    assert isinstance(nose_pt, tuple)
    assert len(nose_pt) == 2

def test_alert_manager_cooldowns_and_language():
    """Verify alert manager triggers events with cooldown deduplication and bilingual texts."""
    am = AlertManager()
    am.audio_enabled = False  # Avoid playing audio in tests

    # Trigger first drowsiness alert
    alert1 = am.trigger("DROWSINESS", "First test alert")
    assert alert1 is not None
    assert alert1["type"] == "DROWSINESS"
    assert "सो रहे हैं" in alert1["messageHindi"]
    assert "Drowsiness" in alert1["messageEnglish"]

    # Immediate second alert must be blocked by cooldown
    alert2 = am.trigger("DROWSINESS", "Immediate second alert")
    assert alert2 is None  # Cooldown active!

    # Switch language to English
    am.set_language("en")
    assert am.language == "en"
