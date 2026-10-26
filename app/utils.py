import cv2
import numpy as np
import math

def get_pixel_coords(landmark, width: int, height: int):
    """Converts a normalized landmark (0..1) into absolute integer pixel coordinates."""
    return int(landmark.x * width), int(landmark.y * height)

def calculate_distance_px(pt1, pt2, width: int, height: int) -> float:
    """Computes true Euclidean distance between two landmarks in pixel coordinates."""
    x1, y1 = pt1.x * width, pt1.y * height
    x2, y2 = pt2.x * width, pt2.y * height
    return float(math.hypot(x1 - x2, y1 - y2))

def calculate_aspect_ratio_px(landmarks, horizontal_pair, vertical_pairs, width: int, height: int) -> float:
    """
    Computes aspect ratio using Euclidean distances in pixel space.
    Eliminates non-uniform scaling distortions between 4:3 and 16:9 aspect frames.
    """
    p_h1, p_h2 = landmarks[horizontal_pair[0]], landmarks[horizontal_pair[1]]
    horizontal_dist = calculate_distance_px(p_h1, p_h2, width, height)
    if horizontal_dist < 1e-6:
        return 0.0

    vertical_dists = [
        calculate_distance_px(landmarks[top], landmarks[bottom], width, height)
        for (top, bottom) in vertical_pairs
    ]
    avg_vertical = sum(vertical_dists) / len(vertical_dists)
    return float(avg_vertical / horizontal_dist)

def draw_polygon(frame, landmarks, indices, width: int, height: int, color=(0, 255, 0), thickness=1, fill=False):
    """Draws a connected polygon connecting landmark indices."""
    pts = []
    for idx in indices:
        if idx < len(landmarks):
            pts.append(get_pixel_coords(landmarks[idx], width, height))
    if len(pts) > 2:
        pts_arr = np.array(pts, np.int32).reshape((-1, 1, 2))
        if fill:
            overlay = frame.copy()
            cv2.fillPoly(overlay, [pts_arr], color)
            cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
        cv2.polylines(frame, [pts_arr], isClosed=True, color=color, thickness=thickness, lineType=cv2.LINE_AA)

def draw_head_axes(frame, pitch, yaw, roll, nose_pt, axis_length=50):
    """
    Draws 3D Cartesian orientation axes from the driver's nose tip:
      - X Axis (Pitch / Nod): RED
      - Y Axis (Yaw / Gaze): GREEN
      - Z Axis (Roll / Tilt): BLUE
    """
    pitch_r = math.radians(pitch)
    yaw_r = math.radians(yaw)
    roll_r = math.radians(roll)

    # 3D Unit vectors transformed by Euler angles
    # X Axis (Red)
    x1 = int(nose_pt[0] + axis_length * (math.cos(yaw_r) * math.cos(roll_r)))
    y1 = int(nose_pt[1] + axis_length * (math.cos(pitch_r) * math.sin(roll_r) + math.cos(roll_r) * math.sin(pitch_r) * math.sin(yaw_r)))

    # Y Axis (Green)
    x2 = int(nose_pt[0] - axis_length * (math.cos(yaw_r) * math.sin(roll_r)))
    y2 = int(nose_pt[1] + axis_length * (math.cos(pitch_r) * math.cos(roll_r) - math.sin(pitch_r) * math.sin(yaw_r) * math.sin(roll_r)))

    # Z Axis (Blue - Forward into camera)
    x3 = int(nose_pt[0] + axis_length * (math.sin(yaw_r)))
    y3 = int(nose_pt[1] - axis_length * (math.sin(pitch_r) * math.cos(yaw_r)))

    cv2.line(frame, nose_pt, (x1, y1), (0, 0, 255), 2, cv2.LINE_AA)   # X - Pitch (Red)
    cv2.line(frame, nose_pt, (x2, y2), (0, 255, 0), 2, cv2.LINE_AA)   # Y - Yaw (Green)
    cv2.line(frame, nose_pt, (x3, y3), (255, 0, 0), 2, cv2.LINE_AA)   # Z - Roll (Blue)

def draw_pill_badge(frame, text, top_left, bg_color, text_color, font_scale=0.5, thickness=1, padding=(10, 6)):
    """Draws a modern HUD rounded-look badge with clean background and border."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)

    px, py = padding
    x, y = top_left
    w = text_w + 2 * px
    h = text_h + 2 * py

    # Semi-transparent pill background
    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + w, y + h), bg_color, -1)
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)

    # Outline
    cv2.rectangle(frame, (x, y), (x + w, y + h), (60, 60, 75), 1)

    # Text
    text_origin = (x + px, y + h - py)
    cv2.putText(frame, text, text_origin, font, font_scale, text_color, thickness, cv2.LINE_AA)

def create_standby_frame(width: int, height: int, message: str, subtext: str) -> np.ndarray:
    """Generates a professional dark standby frame when webcam is initializing or disconnected."""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:] = (18, 18, 24)  # Deep Slate-950

    # Draw centered standby box
    box_w, box_h = 380, 110
    bx = (width - box_w) // 2
    by = (height - box_h) // 2
    cv2.rectangle(frame, (bx, by), (bx + box_w, by + box_h), (28, 28, 38), -1)
    cv2.rectangle(frame, (bx, by), (bx + box_w, by + box_h), (50, 50, 70), 1)

    # Status message
    cv2.putText(
        frame,
        message,
        (bx + 25, by + 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 165, 255),
        2,
        cv2.LINE_AA
    )

    # Subtext
    cv2.putText(
        frame,
        subtext,
        (bx + 25, by + 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.42,
        (160, 160, 180),
        1,
        cv2.LINE_AA
    )

    return frame
