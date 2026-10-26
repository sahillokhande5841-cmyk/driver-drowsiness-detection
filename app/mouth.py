from app.utils import calculate_aspect_ratio_px, draw_polygon

# Mouth landmark indices
MOUTH_HORIZONTAL = (78, 308)
MOUTH_VERTICAL_PAIRS = [
    (13, 14),   # Inner center
    (82, 87),   # Inner mid-left
    (312, 317)  # Inner mid-right
]

# Outer lip contour
MOUTH_OUTER = [
    61, 146, 91, 181, 84, 17,
    314, 405, 321, 375, 291,
    409, 270, 269, 267, 0,
    37, 39, 40, 185
]

# Inner lip contour
MOUTH_INNER = [
    78, 95, 88, 178, 87, 14,
    317, 402, 318, 324, 308,
    415, 310, 311, 312, 13,
    82, 81, 80, 191
]

def calculate_mar(landmarks, width: int = 640, height: int = 480) -> float:
    """
    Computes Mouth Aspect Ratio (MAR) in true pixel space.
    Average of 3 vertical lip distances divided by the horizontal lip width.
    """
    if len(landmarks) < 400:
        return 0.0

    mar = calculate_aspect_ratio_px(
        landmarks,
        horizontal_pair=MOUTH_HORIZONTAL,
        vertical_pairs=MOUTH_VERTICAL_PAIRS,
        width=width,
        height=height
    )

    return float(mar)

def draw_mouth(frame, landmarks, width: int, height: int, is_yawning: bool = False):
    """Draws outer and inner mouth polygons on the frame."""
    color = (0, 0, 255) if is_yawning else (0, 200, 255)
    draw_polygon(frame, landmarks, MOUTH_OUTER, width, height, color=color, thickness=1, fill=is_yawning)
    draw_polygon(frame, landmarks, MOUTH_INNER, width, height, color=color, thickness=1, fill=False)
