MAX_SCORE = 10
RECOVERY_RATE = 0.10

EYE_WEIGHT = 0.40
HEAD_WEIGHT = 0.30
YAWN_WEIGHT = 2.0


def calculate_fatigue_score(
    fatigue_score,
    eye_closed,
    head_down,
    new_yawn
):

    if eye_closed:
        fatigue_score += EYE_WEIGHT

    if head_down:
        fatigue_score += HEAD_WEIGHT

    if new_yawn:
        fatigue_score += YAWN_WEIGHT

    if not eye_closed and not head_down:
        fatigue_score -= RECOVERY_RATE

    fatigue_score = max(0, fatigue_score)
    fatigue_score = min(MAX_SCORE, fatigue_score)

    return fatigue_score


def get_status(score):

    if score >= 8:
        return "DROWSY"

    elif score >= 4:
        return "TIRED"

    else:
        return "NORMAL"