import pytest
import numpy as np
import math
import cv2
from app.eye import calculate_ear, LEFT_EYE, RIGHT_EYE
from app.mouth import calculate_mar, MOUTH_HORIZONTAL, MOUTH_VERTICAL_PAIRS
from app.head_pose import get_head_pose, MODEL_POINTS
from app.alerts import AlertManager

class MockLandmark:
    def __init__(self, x, y, z=0.0):
        self.x = x
        self.y = y
        self.z = z

def create_mock_face(eye_open=True, mouth_open=False, pitch_deg=0.0, yaw_deg=0.0):
    """
    Creates a mock face with 478 landmarks for unit testing.
    Uses projective geometry to generate accurate 2D coordinates for head pose points.
    """
    landmarks = [MockLandmark(0.5, 0.5, 0.0) for _ in range(478)]

    # Left eye outer corner (33) and inner corner (133)
    landmarks[33] = MockLandmark(0.30, 0.40)
    landmarks[133] = MockLandmark(0.40, 0.40)

    # Vertical landmarks for left eye
    if eye_open:
        landmarks[160] = MockLandmark(0.33, 0.36)
        landmarks[144] = MockLandmark(0.33, 0.44)
        landmarks[159] = MockLandmark(0.35, 0.35)
        landmarks[145] = MockLandmark(0.35, 0.45)
        landmarks[158] = MockLandmark(0.37, 0.36)
        landmarks[153] = MockLandmark(0.37, 0.44)
    else:
        # Eyelids touching (closed)
        landmarks[160] = MockLandmark(0.33, 0.40)
        landmarks[144] = MockLandmark(0.33, 0.40)
        landmarks[159] = MockLandmark(0.35, 0.40)
        landmarks[145] = MockLandmark(0.35, 0.40)
        landmarks[158] = MockLandmark(0.37, 0.40)
        landmarks[153] = MockLandmark(0.37, 0.40)

    # Right eye inner corner (362) and outer corner (263)
    landmarks[362] = MockLandmark(0.60, 0.40)
    landmarks[263] = MockLandmark(0.70, 0.40)

    if eye_open:
        landmarks[385] = MockLandmark(0.63, 0.36)
        landmarks[380] = MockLandmark(0.63, 0.44)
        landmarks[386] = MockLandmark(0.65, 0.35)
        landmarks[374] = MockLandmark(0.65, 0.45)
        landmarks[387] = MockLandmark(0.67, 0.36)
        landmarks[373] = MockLandmark(0.67, 0.44)
    else:
        landmarks[385] = MockLandmark(0.63, 0.40)
        landmarks[380] = MockLandmark(0.63, 0.40)
        landmarks[386] = MockLandmark(0.65, 0.40)
        landmarks[374] = MockLandmark(0.65, 0.40)
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

    # Project the 6 head pose points: Nose (1), Chin (152), Left Eye Left (33), Right Eye Right (263), Mouth Left (61), Mouth Right (291)
    focal_length = 640.0
    center = (320.0, 240.0)
    cam = np.array([[focal_length, 0, center[0]], [0, focal_length, center[1]], [0, 0, 1]], dtype=np.float64)
    dist = np.zeros((4, 1), dtype=np.float64)

    rvec = np.array([math.radians(pitch_deg), math.radians(yaw_deg), 0.0], dtype=np.float64)
    tvec = np.array([0.0, 0.0, 500.0], dtype=np.float64)
    pts, _ = cv2.projectPoints(MODEL_POINTS, rvec, tvec, cam, dist)
    pts_norm = pts.reshape(-1, 2) / np.array([640.0, 480.0])

    head_point_indices = [1, 152, 33, 263, 61, 291]
    for i, idx in enumerate(head_point_indices):
        landmarks[idx] = MockLandmark(float(pts_norm[i, 0]), float(pts_norm[i, 1]))

    return landmarks

def test_ear_calculation_open_vs_closed():
    """Verify EAR calculation properly discriminates open vs closed eyes."""
    open_face = create_mock_face(eye_open=True)
    ear_open, left_open, right_open = calculate_ear(open_face, width=640, height=480)
    assert ear_open > 0.25, f"Expected open EAR > 0.25, got {ear_open}"

    closed_face = create_mock_face(eye_open=False)
    ear_closed, left_closed, right_closed = calculate_ear(closed_face, width=640, height=480)
    assert ear_closed < 0.05, f"Expected closed EAR < 0.05, got {ear_closed}"
    assert ear_open > ear_closed * 4.0

def test_mar_calculation_normal_vs_yawning():
    """Verify MAR calculation properly discriminates closed vs wide open mouth."""
    normal_face = create_mock_face(mouth_open=False)
    mar_normal = calculate_mar(normal_face, width=640, height=480)
    assert mar_normal < 0.10, f"Expected normal MAR < 0.10, got {mar_normal}"

    yawn_face = create_mock_face(mouth_open=True)
    mar_yawn = calculate_mar(yawn_face, width=640, height=480)
    assert mar_yawn > 0.50, f"Expected yawn MAR > 0.50, got {mar_yawn}"
    assert mar_yawn > mar_normal * 4.0

def test_head_pose_calculation_angles():
    """Verify head pose returns sensible pitch, yaw, roll numeric values and validates angles."""
    # 1. Frontal neutral face
    mock_neutral = create_mock_face(pitch_deg=0.0, yaw_deg=0.0)
    pitch, yaw, roll, nose_pt = get_head_pose(mock_neutral, width=640, height=480)
    assert isinstance(pitch, float)
    assert isinstance(yaw, float)
    assert isinstance(roll, float)
    assert abs(pitch) < 2.0, f"Neutral face pitch should be ~0°, got {pitch}"
    assert abs(yaw) < 2.0, f"Neutral face yaw should be ~0°, got {yaw}"
    assert abs(roll) < 2.0, f"Neutral face roll should be ~0°, got {roll}"

    # 2. Downward nod (+20 deg pitch)
    mock_down = create_mock_face(pitch_deg=20.0, yaw_deg=0.0)
    pitch_down, _, _, _ = get_head_pose(mock_down, width=640, height=480)
    assert pitch_down == pytest.approx(20.0, abs=1.0)

    # 3. Looking right (+25 deg yaw)
    mock_right = create_mock_face(pitch_deg=0.0, yaw_deg=25.0)
    _, yaw_right, _, _ = get_head_pose(mock_right, width=640, height=480)
    assert yaw_right == pytest.approx(25.0, abs=1.0)

def test_alert_manager_cooldowns_and_recovery():
    """Verify alert manager triggers events with cooldown deduplication, recovery clear, and bilingual texts."""
    am = AlertManager()
    am.audio_enabled = False  # Avoid playing audio in tests

    # Trigger critical drowsiness alert
    alert1 = am.trigger("CRITICAL_DROWSINESS", "First test alert")
    assert alert1 is not None
    assert alert1["type"] == "CRITICAL_DROWSINESS"
    assert "सो रहे हैं" in alert1["messageHindi"]
    assert "Wake up" in alert1["messageEnglish"]

    # Immediate second alert must be blocked by cooldown
    alert2 = am.trigger("CRITICAL_DROWSINESS", "Immediate second alert")
    assert alert2 is None  # Cooldown active!

    # Active alert is present
    assert am.get_active_alert() is not None

    # Immediate clear on driver recovery
    am.clear_active_alert()
    assert am.get_active_alert() is None

    # Switch language to English
    am.set_language("en")
    assert am.language == "en"
