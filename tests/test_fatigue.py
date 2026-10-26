from app.fatigue import update_fatigue_score, get_driver_status
from app.config import MAX_FATIGUE_SCORE, STATUS_DROWSY_SCORE, STATUS_TIRED_SCORE


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


def test_fatigue_score_decays():
    """Verify fatigue score decays when driver is alert."""
    initial_score = 5.0
    dt = 1.0
    decayed = update_fatigue_score(
        current_score=initial_score,
        dt=dt,
        eye_closed_prolonged=False,
        head_down=False,
        yawn_completed=False,
        phone_distracted=False
    )
    assert decayed < initial_score


def test_fatigue_score_bounds():
    """Verify score stays within [0, MAX_FATIGUE_SCORE]."""
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
    """Verify driver status classifications."""
    # Calibrating
    assert get_driver_status(0.0, False, False, False, is_calibrating=True) == "CALIBRATING"

    # No face
    assert get_driver_status(0.0, False, False, False, face_detected=False) == "NO_FACE"

    # Severe eye closure or high fatigue
    assert get_driver_status(0.0, eye_closed_severe=True, phone_distracted=False, head_down_prolonged=False) == "DROWSY"
    assert get_driver_status(STATUS_DROWSY_SCORE + 0.5, False, False, False) == "DROWSY"

    # Distractions
    assert get_driver_status(1.0, False, phone_distracted=True, head_down_prolonged=False) == "DISTRACTED_PHONE"
    assert get_driver_status(1.0, False, phone_distracted=False, head_down_prolonged=True) == "DISTRACTED_HEAD_DOWN"

    # Tired vs Normal
    assert get_driver_status(STATUS_TIRED_SCORE + 0.1, False, False, False) == "TIRED"
    assert get_driver_status(0.0, False, False, False) == "NORMAL"
