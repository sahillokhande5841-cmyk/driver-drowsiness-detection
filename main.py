import cv2
import mediapipe as mp
import pygame
import time
from eye import (
    LEFT_EYE,
    RIGHT_EYE,
    calculate_ear
)
from fatigue import calculate_fatigue_score, get_status
from mouth import calculate_mar, MOUTH
from utils import (
    draw_landmarks,
    draw_points
)
from head_pose import (
    get_head_points,
    get_head_pose
)

pygame.mixer.init()
pygame.mixer.music.load("alarm.wav")

calibrating = True
calibration_start = time.time()
CALIBRATION_FACTOR = 0.75
CALIBRATION_TIME = 5
ear_values = []


mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()

cap = cv2.VideoCapture(0)

EAR_THRESHOLD = 0.25
EYE_CLOSED_MIN_FRAMES = 15
blink_count = 0
eye_closed = False
closed_eye_frames = 0

MAR_THRESHOLD = 0.30
mouth_open = False
mouth_open_frames = 0
yawn_count = 0
YAWN_MIN_FRAMES = 30

HEAD_DOWN_THRESHOLD = 20 
HEAD_DOWN_MIN_FRAMES = 20

head_down = False
head_down_frames = 0
fatigue_score = 0

while True:
    ret, frame = cap.read()

    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        face = results.multi_face_landmarks[0]

        height, width = frame.shape[:2]

        ear = calculate_ear(face)
        mar = calculate_mar(face)

        head_points = get_head_points(face, width, height)

        pitch, yaw, roll = get_head_pose(
            face,
            width,
            height
        )

        if calibrating:
            time_left = max(0, CALIBRATION_TIME - (time.time() - calibration_start))
            status = f"CALIBRATING ({time_left:.1f}s)"
            ear_values.append(ear)

            if time.time() - calibration_start >= CALIBRATION_TIME:
                average_ear = sum(ear_values) / len(ear_values)
                EAR_THRESHOLD = average_ear * CALIBRATION_FACTOR
                calibrating = False
                print(f"Calibration complete. Threshold set to: {EAR_THRESHOLD}")
        
        else:
            
            if ear < EAR_THRESHOLD:
                closed_eye_frames += 1
                if not eye_closed:
                    eye_closed = True  
            else:
                closed_eye_frames = 0
                if eye_closed:
                    blink_count += 1
                    eye_closed = False 

            
            new_yawn = False
            if mar > MAR_THRESHOLD:
                mouth_open_frames += 1

                if not mouth_open:
                    mouth_open = True

            else:
                if mouth_open:
                    if mouth_open_frames >= YAWN_MIN_FRAMES:
                        yawn_count += 1
                        new_yawn = True
                    mouth_open = False
                    mouth_open_frames = 0

    

            if pitch < -HEAD_DOWN_THRESHOLD:
                head_down_frames += 1
            else:
                head_down_frames = 0

            if head_down_frames >= HEAD_DOWN_MIN_FRAMES:
                head_down = True
            else:
                head_down = False


            fatigue_score = calculate_fatigue_score(
                fatigue_score=fatigue_score,
                eye_closed=closed_eye_frames >= EYE_CLOSED_MIN_FRAMES,
                head_down=head_down,
                new_yawn=new_yawn
            )
            status = get_status(fatigue_score)
            
            if status == "DROWSY":
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1)
            else:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
        

        for point in head_points:
            cv2.circle(frame, point, 4, (255, 0, 255), -1)
            
        draw_points(frame, LEFT_EYE, face, width, height)
        draw_points(frame, RIGHT_EYE, face, width, height)

        draw_landmarks(frame, LEFT_EYE, face, width, height)
        draw_landmarks(frame, RIGHT_EYE, face, width, height)

        draw_points(frame, MOUTH, face, width, height)
        draw_landmarks(frame, MOUTH, face, width, height)

        if status.startswith("CALIBRATING"):
            color = (0,255,255)

        elif status == "NORMAL":
            color = (0,255,0)

        elif status == "TIRED":
            color = (0,165,255)

        else:
            color = (0,0,255)

        status_text = f"Status: {status}"
        cv2.putText(
            frame,
            status_text,
            (50,100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2
        )  

        blink_text = f"Blinks: {blink_count}"
        cv2.putText(
            frame,
            blink_text,
            (50, 200),
            cv2.FONT_HERSHEY_SIMPLEX,   
            1,
            (255, 255, 0),
            2
        )
        text = f"EAR: {ear:.2f}"
        cv2.putText(
            frame,
            text,
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        if calibrating:
            threshold_text = "Threshold: Calculating..."
        else:
            threshold_text = f"Threshold: {EAR_THRESHOLD:.2f}"
        cv2.putText(
            frame,
            threshold_text,
            (50, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 0),
            2
        )

        mar_text = f"MAR: {mar:.2f}"
        cv2.putText(
            frame,
            mar_text,
            (50, 250),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 0),
            2
        )

        score_text = f"Fatigue Score: {fatigue_score:.1f}"
        cv2.putText(
            frame,
            score_text,
            (50, 450),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 165, 255),
            2
        )
        
        yawn_text = f"Yawns: {yawn_count}"
        cv2.putText(
            frame,
            yawn_text,
            (50, 300),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 0),
            2
        ) 

        pitch_text = f"Pitch: {pitch:.1f}"
        cv2.putText(
            frame,
            pitch_text,
            (50, 350),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 0, 255),
            2
        )

        head_text = f"Head: {'DOWN' if head_down else 'NORMAL'}"
        cv2.putText(
            frame,
            head_text,
            (50, 400),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 0, 255),
            2
        )
            
    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()