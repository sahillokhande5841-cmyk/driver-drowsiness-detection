import cv2
import numpy as np

HEAD_POINTS = [1, 33, 263, 61, 291, 199]

import numpy as np

MODEL_POINTS = np.array([
    (0.0, 0.0, 0.0),          # Nose tip    
    (-30.0, -30.0, -30.0),    # Left eye corner
    (30.0, -30.0, -30.0),     # Right eye corner
    (-25.0, 30.0, -30.0),     # Left mouth corner
    (25.0, 30.0, -30.0),      # Right mouth corner
    (0.0, 65.0, -5.0)         # Chin
], dtype=np.float64)

def get_head_points(face, width, height):
    image_points = []

    for point in HEAD_POINTS:
        x = int(face.landmark[point].x * width)
        y = int(face.landmark[point].y * height)

        image_points.append((x, y))

    return image_points

def get_head_pose(face, width, height):
    image_points = np.array(
        get_head_points(face, width, height),
        dtype=np.float64
    )

    focal_length = width

    camera_matrix = np.array([
        [focal_length, 0, width / 2],
        [0, focal_length, height / 2],
        [0, 0, 1]
    ], dtype=np.float64)

    dist_coeffs = np.zeros((4, 1))

    success, rotation_vector, translation_vector = cv2.solvePnP(
        MODEL_POINTS,
        image_points,
        camera_matrix,
        dist_coeffs
    )

    rotation_matrix, _ = cv2.Rodrigues(rotation_vector)

    projection_matrix = np.hstack((rotation_matrix, translation_vector))

    _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(projection_matrix)

    pitch = euler_angles[0][0]
    yaw = euler_angles[1][0]
    roll = euler_angles[2][0]

    return pitch, yaw, roll