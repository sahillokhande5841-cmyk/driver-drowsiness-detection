import pytest
from app.fatigue import update_fatigue_score, get_driver_status
from app.config import (
    MAX_FATIGUE_SCORE,
    NORMAL_DECAY_RATE,
    ACTIVE_RECOVERY_RATE,
    FATIGUE_WARNING_SCORE,
    DROWSINESS_WARNING_SCORE,
    CRITICAL_DROWSINESS_SCORE
)

def test_fatigue_score_increases_on_events():
    """Verify fatigue score increments on prolonged eye closure, head down, and yawn."""
    score = 0.0
    dt = 1.0

    # Eye closed prolonged
    score_after_eye = update_fatigue_score(
        current_score=score,
        dt=dt,
        eye_closed_prolonged=True,
        head_down=False,
        yawn_completed=False,
        phone_distracted=False
    )
    assert score_after_eye > score

    # Completed Yawn
    score_after_yawn = update_fatigue_score(
        current_score=score,
        dt=dt,
        eye_closed_prolonged=False,
        head_down=False,
        yawn_completed=True,
        phone_distracted=False
    )
    assert score_after_yawn >= 2.0

def test_fatigue_score_active_recovery_vs_normal():
    """Verify active recovery decays significantly faster than normal passive decay."""
    initial_score = 5.0
    dt = 1.0

    normal_decayed = update_fatigue_score(
        current_score=initial_score,
        dt=dt,
        eye_closed_prolonged=False,
        head_down=False,
        yawn_completed=False,
        phone_distracted=False,
        is_recovering=False
    )
    assert normal_decayed == pytest.approx(initial_score - NORMAL_DECAY_RATE * dt)

    active_decayed = update_fatigue_score(
        current_score=initial_score,
        dt=dt,
        eye_closed_prolonged=False,
        head_down=False,
        yawn_completed=False,
        phone_distracted=False,
        is_recovering=True
    )
    assert active_decayed == pytest.approx(initial_score - ACTIVE_RECOVERY_RATE * dt)
    assert active_decayed < normal_decayed

def test_fatigue_score_bounds():
    """Verify score stays strictly within [0.0, MAX_FATIGUE_SCORE]."""
    zero_score = update_fatigue_score(
        current_score=0.0,
        dt=1.0,
        eye_closed_prolonged=False,
        head_down=False,
        yawn_completed=False,
        phone_distracted=False
    )
    assert zero_score == 0.0

    max_score = update_fatigue_score(
        current_score=float(MAX_FATIGUE_SCORE) + 5.0,
        dt=1.0,
        eye_closed_prolonged=True,
        head_down=True,
        yawn_completed=True,
        phone_distracted=True
    )
    assert max_score == float(MAX_FATIGUE_SCORE)

def test_get_driver_status_mappings():
    """Verify centralized driver status classifications and immediate recovery."""
    # Camera error
    assert get_driver_status(
        0.0, False, False, False, False, camera_connected=False
    ) == "CAMERA_ERROR"

    # No face
    assert get_driver_status(
        0.0, False, False, False, False, face_detected=False
    ) == "NO_FACE"

    # Calibrating
    assert get_driver_status(
        0.0, False, False, False, False, is_calibrating=True
    ) == "CALIBRATING"

    # Severe eye closure -> CRITICAL_DROWSINESS
    assert get_driver_status(
        0.0, eye_closed_severe=True, eye_closed_prolonged=True,
        phone_distracted=False, head_down_prolonged=False
    ) == "CRITICAL_DROWSINESS"

    # Early warning eye closure -> DROWSINESS_WARNING
    assert get_driver_status(
        0.0, eye_closed_severe=False, eye_closed_prolonged=True,
        phone_distracted=False, head_down_prolonged=False
    ) == "DROWSINESS_WARNING"

    # Distractions
    assert get_driver_status(
        1.0, False, False, phone_distracted=True, head_down_prolonged=False
    ) == "DISTRACTED_PHONE"

    assert get_driver_status(
        1.0, False, False, phone_distracted=False, head_down_prolonged=True
    ) == "DISTRACTED_HEAD_DOWN"

    # Open-eye recovery: even if historical fatigue score is high, open eyes must NOT say CRITICAL_DROWSINESS!
    assert get_driver_status(
        fatigue_score=9.0, eye_closed_severe=False, eye_closed_prolonged=False,
        phone_distracted=False, head_down_prolonged=False
    ) == "DROWSINESS_WARNING"

    # Fatigue warning
    assert get_driver_status(
        fatigue_score=FATIGUE_WARNING_SCORE + 0.1, eye_closed_severe=False, eye_closed_prolonged=False,
        phone_distracted=False, head_down_prolonged=False
    ) == "FATIGUE_WARNING"

    # Alert & Normal
    assert get_driver_status(
        0.0, False, False, False, False
    ) == "NORMAL"
