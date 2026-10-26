import cv2


def calculate_distance(point1, point2):
    return ((point1.x - point2.x) ** 2 +
            (point1.y - point2.y) ** 2) ** 0.5

def draw_landmarks(frame, points, face, width, height):
    points_size = len(points)

    for i in range(points_size - 1):
        landmark1 = face.landmark[points[i]]
        landmark2 = face.landmark[points[i + 1]]
        x1 = int(landmark1.x * width)
        y1 = int(landmark1.y * height)
        x2 = int(landmark2.x * width)
        y2 = int(landmark2.y * height)
        cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2) 

    n = len(points)-1
    x1 = int(face.landmark[points[n]].x * width)
    y1 = int(face.landmark[points[n]].y * height)
    x2 = int(face.landmark[points[0]].x * width) 
    y2 = int(face.landmark[points[0]].y * height)
    cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

def draw_points(frame, points, face, width, height):
    for i in points:
        landmark = face.landmark[i]
        x = int(landmark.x * width)
        y = int(landmark.y * height)
        cv2.circle(frame, (x, y), 3, (0, 255,0), -1)

def calculate_aspect_ratio(face, horizontal, vertical1, vertical2):
    v1 = calculate_distance(
        face.landmark[vertical1[0]],
        face.landmark[vertical1[1]]
    )

    v2 = calculate_distance(
        face.landmark[vertical2[0]],
        face.landmark[vertical2[1]]
    )

    h = calculate_distance(
        face.landmark[horizontal[0]],
        face.landmark[horizontal[1]]
    )

    ear = (v1 + v2) / (2 * h)

    return ear