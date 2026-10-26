from app.utils import calculate_aspect_ratio_px, draw_polygon

# Canonical MediaPipe 478 landmark indices for accurate Eye Aspect Ratio (EAR)
LEFT_EYE_HORIZONTAL = (33, 133)
LEFT_EYE_VERTICAL_PAIRS = [
    (160, 144),  # Lateral vertical pair
    (159, 145),  # Center vertical pair (maximum aperture)
    (158, 153)   # Medial vertical pair
]

RIGHT_EYE_HORIZONTAL = (362, 263)
RIGHT_EYE_VERTICAL_PAIRS = [
    (385, 380),  # Lateral vertical pair
    (386, 374),  # Center vertical pair (maximum aperture)
    (387, 373)   # Medial vertical pair
]

# Full eye contour contours for visualization
LEFT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
RIGHT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]

def calculate_ear(landmarks, width: int = 640, height: int = 480):
    """
    Computes Eye Aspect Ratio (EAR) using true Euclidean distances in pixel space.
    Eliminates aspect-ratio distortion and returns (avg_ear, left_ear, right_ear).
    """
    if len(landmarks) < 400:
        return 0.0, 0.0, 0.0

    left_ear = calculate_aspect_ratio_px(
        landmarks,
        horizontal_pair=LEFT_EYE_HORIZONTAL,
        vertical_pairs=LEFT_EYE_VERTICAL_PAIRS,
        width=width,
        height=height
    )

    right_ear = calculate_aspect_ratio_px(
        landmarks,
        horizontal_pair=RIGHT_EYE_HORIZONTAL,
        vertical_pairs=RIGHT_EYE_VERTICAL_PAIRS,
        width=width,
        height=height
    )

    avg_ear = (left_ear + right_ear) / 2.0
    return float(avg_ear), float(left_ear), float(right_ear)

def draw_eyes(frame, landmarks, width: int, height: int, is_closed: bool = False):
    """Draws left and right eye contours with dynamic color coding."""
    color = (0, 0, 255) if is_closed else (0, 255, 0)
    draw_polygon(frame, landmarks, LEFT_EYE, width, height, color=color, thickness=1, fill=is_closed)
    draw_polygon(frame, landmarks, RIGHT_EYE, width, height, color=color, thickness=1, fill=is_closed)
