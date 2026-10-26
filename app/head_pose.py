import cv2
import numpy as np
import math
from app.utils import draw_head_axes

# 6 Canonical landmark indices for Head Pose Estimation
HEAD_POINTS = [
    1,    # Nose tip
    152,  # Chin
    33,   # Left eye corner in image
    263,  # Right eye corner in image
    61,   # Left mouth corner in image
    291   # Right mouth corner in image
]

# Canonical 3D facial model points (in mm, centered at nose tip)
# System aligned with OpenCV Camera Frame:
#   +X points RIGHT
#   +Y points DOWN (chin has +Y, eyes have -Y)
#   +Z points FORWARD into scene (nose is at Z=0, eyes/chin/mouth are recessed at +Z)
MODEL_POINTS = np.array([
    (0.0, 0.0, 0.0),          # Nose tip (index 1)
    (0.0, 110.0, 40.0),       # Chin (index 152) - down (+Y)
    (-65.0, -60.0, 40.0),     # Left eye corner (index 33) - up (-Y), left (-X)
    (65.0, -60.0, 40.0),      # Right eye corner (index 263) - up (-Y), right (+X)
    (-40.0, 50.0, 35.0),      # Left mouth corner (index 61) - down (+Y), left (-X)
    (40.0, 50.0, 35.0)        # Right mouth corner (index 291) - down (+Y), right (+X)
], dtype=np.float64)

def get_head_points(landmarks, width: int, height: int):
    """Extract 2D pixel coordinates for the 6 head pose reference landmarks."""
    image_points = []
    for idx in HEAD_POINTS:
        if idx < len(landmarks):
            pt = landmarks[idx]
            image_points.append((float(pt.x * width), float(pt.y * height)))
        else:
            image_points.append((float(width) / 2.0, float(height) / 2.0))
    return np.array(image_points, dtype=np.float64)

def get_head_pose(landmarks, width: int, height: int):
    """
    Estimates 3D head pose (pitch, yaw, roll) using solvePnP and direct rotation matrix decomposition.
    
    Conventions:
      Pitch: Rotation around X-axis. Positive = nodding DOWN, Negative = looking UP.
      Yaw:   Rotation around Y-axis. Positive = looking RIGHT, Negative = looking LEFT.
      Roll:  Rotation around Z-axis. Head sideways tilt.
      
    Returns: (pitch, yaw, roll, nose_2d_pixel_coords)
    """
    if len(landmarks) < 400:
        return 0.0, 0.0, 0.0, (width // 2, height // 2)

    image_points = get_head_points(landmarks, width, height)
    nose_pt = (int(image_points[0][0]), int(image_points[0][1]))

    focal_length = float(width)
    center = (float(width) / 2.0, float(height) / 2.0)
    camera_matrix = np.array([
        [focal_length, 0.0, center[0]],
        [0.0, focal_length, center[1]],
        [0.0, 0.0, 1.0]
    ], dtype=np.float64)

    dist_coeffs = np.zeros((4, 1), dtype=np.float64)

    success, rotation_vector, translation_vector = cv2.solvePnP(
        MODEL_POINTS,
        image_points,
        camera_matrix,
        dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE
    )

    if not success:
        return 0.0, 0.0, 0.0, nose_pt

    rotation_matrix, _ = cv2.Rodrigues(rotation_vector)

    # Robust Tait-Bryan Euler angle decomposition
    sy = math.sqrt(rotation_matrix[0, 0] * rotation_matrix[0, 0] + rotation_matrix[1, 0] * rotation_matrix[1, 0])
    singular = sy < 1e-6

    if not singular:
        x = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
        y = math.atan2(-rotation_matrix[2, 0], sy)
        z = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
    else:
        x = math.atan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
        y = math.atan2(-rotation_matrix[2, 0], sy)
        z = 0.0

    pitch = math.degrees(x)
    yaw = math.degrees(y)
    roll = math.degrees(z)

    # Sanity clamping for natural human neck range of motion
    pitch = float(np.clip(pitch, -85.0, 85.0))
    yaw = float(np.clip(yaw, -85.0, 85.0))
    roll = float(np.clip(roll, -85.0, 85.0))

    return pitch, yaw, roll, nose_pt

def draw_head_pose(frame, pitch, yaw, roll, nose_pt):
    """Draws 3D Cartesian orientation axes from the driver's nose tip."""
    draw_head_axes(frame, pitch, yaw, roll, nose_pt, axis_length=55)
