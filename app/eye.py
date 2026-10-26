from app.utils import calculate_distance, draw_landmarks, draw_points, calculate_aspect_ratio

LEFT_EYE = [33, 160, 158, 133, 153, 144]

RIGHT_EYE = [362, 385, 387, 263, 373, 380]


def calculate_ear(face):
    left_ear = calculate_aspect_ratio(
        face,
        (33, 133),
        (160, 144),
        (158, 153)
    )

    right_ear = calculate_aspect_ratio(
        face,
        (362, 263),
        (385, 380),
        (387, 373)
    )

    return (left_ear + right_ear) / 2