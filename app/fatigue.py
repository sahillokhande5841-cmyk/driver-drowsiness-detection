from app.config import (
    MAX_FATIGUE_SCORE,
    NORMAL_DECAY_RATE,
    ACTIVE_RECOVERY_RATE,
    EYE_CLOSED_WEIGHT,
    HEAD_DOWN_WEIGHT,
    YAWN_WEIGHT,
    PHONE_WEIGHT,
    FATIGUE_WARNING_SCORE,
    DROWSINESS_WARNING_SCORE,
    CRITICAL_DROWSINESS_SCORE,
)

def update_fatigue_score(
    current_score: float,
    dt: float,
    eye_closed_prolonged: bool,
    head_down: bool,
    yawn_completed: bool,
    phone_distracted: bool = False,
    is_recovering: bool = False
) -> float:
    """
    Updates the fatigue score using time-based delta (dt seconds).
    - Increases during prolonged eye closure, head down, yawn completion, or phone distraction.
    - Decays at NORMAL_DECAY_RATE during normal attentiveness.
    - Decays at ACTIVE_RECOVERY_RATE (accelerated) when driver actively opens eyes to recover.
    - Strictly clamped to [0.0, MAX_FATIGUE_SCORE].
    """
    new_score = float(current_score)

    # Accumulate score for fatigue & distraction events
    if eye_closed_prolonged:
        new_score += EYE_CLOSED_WEIGHT * dt * 2.5

    if head_down:
        new_score += HEAD_DOWN_WEIGHT * dt

    if yawn_completed:
        new_score += YAWN_WEIGHT

    if phone_distracted:
        new_score += PHONE_WEIGHT * dt

    # Recovery / decay when driver is attentive and no fatigue event occurred
    if not eye_closed_prolonged and not head_down and not phone_distracted and not yawn_completed:
        if is_recovering:
            new_score -= ACTIVE_RECOVERY_RATE * dt
        else:
            new_score -= NORMAL_DECAY_RATE * dt

    return float(max(0.0, min(float(MAX_FATIGUE_SCORE), new_score)))


def get_driver_status(
    fatigue_score: float,
    eye_closed_severe: bool,
    eye_closed_prolonged: bool,
    phone_distracted: bool,
    head_down_prolonged: bool,
    is_calibrating: bool = False,
    face_detected: bool = True,
    camera_connected: bool = True
) -> str:
    """
    Centralized 7+ state machine for driver drowsiness status:
    1. CAMERA_ERROR: Camera feed unavailable or disconnected
    2. INITIALIZING: Initial startup
    3. CALIBRATING: Baseline measurement active
    4. NO_FACE: Driver face absent (>1.2s hysteresis)
    5. CRITICAL_DROWSINESS: Eyes closed >= 2.2s (microsleep/sleeping)
    6. DROWSINESS_WARNING: Eyes closed >= 1.2s, or high fatigue score with closed eyes
    7. DISTRACTED: Mobile phone or sustained head down posture
    8. FATIGUE_WARNING: Elevated fatigue score (frequent blinks/yawns)
    9. NORMAL: Eyes open, posture upright, attentive
    """
    if not camera_connected:
        return "CAMERA_ERROR"

    if not face_detected:
        return "NO_FACE"

    if is_calibrating:
        return "CALIBRATING"

    # Critical drowsiness: only when severe closure is actively ongoing
    if eye_closed_severe:
        return "CRITICAL_DROWSINESS"

    # Drowsiness warning: early eye closure warning
    if eye_closed_prolonged:
        return "DROWSINESS_WARNING"

    # Distraction states
    if phone_distracted:
        return "DISTRACTED_PHONE"

    if head_down_prolonged:
        return "DISTRACTED_HEAD_DOWN"

    # Score-based fatigue states (only when eyes are open)
    if fatigue_score >= DROWSINESS_WARNING_SCORE:
        return "DROWSINESS_WARNING"

    if fatigue_score >= FATIGUE_WARNING_SCORE:
        return "FATIGUE_WARNING"

    return "NORMAL"
