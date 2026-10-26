from app.utils import calculate_aspect_ratio

MOUTH_HORIZONTAL = (78, 308)

MOUTH_VERTICAL1 = (13, 14)

MOUTH_VERTICAL2 = (82, 87)

MOUTH = [
    61, 146, 91, 181, 84, 17,
    314, 405, 321, 375, 291,
    409, 270, 269, 267, 0,
    37, 39, 40, 185, 61
]

def calculate_mar(face):
    mar = calculate_aspect_ratio(
        face,
        MOUTH_HORIZONTAL,
        MOUTH_VERTICAL1,
        MOUTH_VERTICAL2
    )

    return mar