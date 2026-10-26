import cv2
import mediapipe as mp
import time
import pygame
import threading

from app.config import (
    CALIBRATION_TIME,
    CALIBRATION_FACTOR,
    EYE_CLOSED_MIN_FRAMES,
    MAR_THRESHOLD,
    YAWN_MIN_FRAMES,
    HEAD_DOWN_THRESHOLD,
    HEAD_DOWN_MIN_FRAMES,
    ALARM_SOUND
)

from app.fatigue import (
    calculate_fatigue_score,
    get_status
)

from app.eye import (
    calculate_ear,
    LEFT_EYE,
    RIGHT_EYE
)

from app.mouth import (
    calculate_mar,
    MOUTH
)

from app.utils import (
    draw_landmarks,
    draw_points
)

from app.head_pose import (
    get_head_pose,
    get_head_points
)


class Detector:

    def __init__(self):

        self.cap = None
        self.face_mesh = None

        self._reset_state()
    
    def _reset_state(self):
        self.calibrating = True
        self.calibration_start = time.time()
        self.ear_values = []
        self.ear_threshold = None

 
        self.blink_count = 0
        self.yawn_count = 0

        self.closed_eye_frames = 0
        self.mouth_open_frames = 0
        self.head_down_frames = 0

        self.eye_closed = False
        self.mouth_open = False
        self.head_down = False

        self.ear = 0.0
        self.mar = 0.0

        self.pitch = 0.0
        self.yaw = 0.0
        self.roll = 0.0

        self.status = "INITIALIZING"
        self.fatigue_score = 0.0

        self.latest_frame = None

        self.latest_metrics = {}

        self.running = False
        self.processing_thread = None

        self.lock = threading.Lock()

    def start(self):

        if self.cap is not None:
            print("Detector is already running.")
            return
        
        self._reset_state()

        pygame.mixer.init()
        pygame.mixer.music.load(ALARM_SOUND)

        self.cap = cv2.VideoCapture(0)

        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.running = True

        self.processing_thread = threading.Thread(
        target=self._processing_loop,
        daemon=True
        )

        self.processing_thread.start()

        print("Detector started.")


    def _extract_features(self, face, frame):

        height, width = frame.shape[:2]

        self.ear = calculate_ear(face)

        self.mar = calculate_mar(face)

        self.pitch, self.yaw, self.roll = get_head_pose(
            face,
            width,
            height
        )
    
    def _handle_calibration(self):

        time_left = max(
            0,
            CALIBRATION_TIME - (time.time() - self.calibration_start)
        )

        self.status = f"CALIBRATING ({time_left:.1f}s)"

        self.ear_values.append(self.ear)

        if time.time() - self.calibration_start >= CALIBRATION_TIME:

            average_ear = sum(self.ear_values) / len(self.ear_values)

            self.ear_threshold = average_ear * CALIBRATION_FACTOR

            self.calibrating = False

            print(
                f"Calibration complete. Threshold set to: {self.ear_threshold:.2f}"
            )
        
    def _handle_blinks(self):

        if self.ear < self.ear_threshold:

            self.closed_eye_frames += 1

            if not self.eye_closed:
                self.eye_closed = True

        else:

            self.closed_eye_frames = 0

            if self.eye_closed:

                self.blink_count += 1

                self.eye_closed = False
    
    def _handle_yawns(self):

        new_yawn = False

        if self.mar > MAR_THRESHOLD:

            self.mouth_open_frames += 1

            if not self.mouth_open:
                self.mouth_open = True

        else:

            if self.mouth_open:

                if self.mouth_open_frames >= YAWN_MIN_FRAMES:

                    self.yawn_count += 1

                    new_yawn = True

                self.mouth_open = False
                self.mouth_open_frames = 0

        return new_yawn
    
    def _handle_head_pose(self):

        if self.pitch < -HEAD_DOWN_THRESHOLD:

            self.head_down_frames += 1

        else:

            self.head_down_frames = 0

        self.head_down = (
            self.head_down_frames >= HEAD_DOWN_MIN_FRAMES
        )

    def _update_fatigue(self, new_yawn):

        self.fatigue_score = calculate_fatigue_score(
            fatigue_score=self.fatigue_score,
            eye_closed=self.closed_eye_frames >= EYE_CLOSED_MIN_FRAMES,
            head_down=self.head_down,
            new_yawn=new_yawn
        )

        self.status = get_status(self.fatigue_score)

    def _handle_alarm(self):

        if self.status == "DROWSY":

            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)

        else:

            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()

    def _build_metrics(self):
        return {
            "status": self.status,
            "fatigueScore": float(self.fatigue_score),
            "ear": float(self.ear),
            "mar": float(self.mar),
            "pitch": float(self.pitch),
            "yaw": float(self.yaw),
            "roll": float(self.roll),
            "blinkCount": self.blink_count,
            "yawnCount": self.yawn_count,
            "headDown": self.head_down,
            "earThreshold": (
                float(self.ear_threshold)
                if self.ear_threshold is not None
                else None
            ),
        }

    def get_metrics(self):
        with self.lock:
            return self.latest_metrics.copy()
    
    def _draw_overlay(self, frame, face):
        height, width = frame.shape[:2]
        draw_points(frame, LEFT_EYE, face, width, height)
        draw_points(frame, RIGHT_EYE, face, width, height)

        draw_landmarks(frame, LEFT_EYE, face, width, height)
        draw_landmarks(frame, RIGHT_EYE, face, width, height)

        draw_points(frame, MOUTH, face, width, height)
        draw_landmarks(frame, MOUTH, face, width, height)

        head_points = get_head_points(face, width, height)

        for point in head_points:
            cv2.circle(frame, point, 4, (255, 0, 255), -1)

    def generate_frames(self):

       while self.running:

            with self.lock:
                if self.latest_frame is None:
                    frame = None
                else:
                    frame = self.latest_frame.copy()

            if frame is None:
                with self.lock:
                    if self.latest_frame is None:
                        time.sleep(0.01)
                    continue

                frame = self.latest_frame.copy()

            ret, buffer = cv2.imencode(".jpg", frame)

            if not ret:
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + buffer.tobytes()
                + b"\r\n"
            )
    
    def stop(self):

        self.running = False

        if self.processing_thread is not None:
            self.processing_thread.join(timeout=1)
            self.processing_thread = None

        if self.cap is not None:

            self.cap.release()

            self.cap = None

        if self.face_mesh is not None:
            self.face_mesh.close()
            self.face_mesh = None

        pygame.mixer.music.stop()

        print("Detector stopped.")


    def process_frame(self):
        if self.cap is None or self.face_mesh is None:
            return

        ret, frame = self.cap.read()

        if not ret:
            return
        

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results = self.face_mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            return 

        face = results.multi_face_landmarks[0]

        self._extract_features(face, frame)

        if self.calibrating:

            self._handle_calibration()

        else:

            self._handle_blinks()

            new_yawn = self._handle_yawns()

            self._handle_head_pose()

            self._update_fatigue(new_yawn)

            self._handle_alarm()

        self._draw_overlay(frame, face)
        with self.lock:
            self.latest_frame = frame.copy()
            self.latest_metrics = self._build_metrics()

    def _processing_loop(self):
        while self.running:
            self.process_frame()
            time.sleep(0.01)