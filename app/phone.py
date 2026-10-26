import cv2
import numpy as np
import os
from ultralytics import YOLO
from app.config import YOLO_MODEL, PHONE_CONF_THRESHOLD

class PhoneDetector:
    """
    Detects mobile cell phones in the webcam view using YOLOv8.
    COCO dataset class 67 corresponds to 'cell phone'.
    """
    PHONE_CLASS_ID = 67

    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        if not os.path.exists(YOLO_MODEL):
            print(f"[PhoneDetector] YOLO model weight not found at {YOLO_MODEL}. Downloading default yolov8n...")
        try:
            self.model = YOLO(YOLO_MODEL if os.path.exists(YOLO_MODEL) else "yolov8n.pt")
            print("[PhoneDetector] YOLOv8 model loaded successfully.")
        except Exception as e:
            print(f"[PhoneDetector] Failed to load YOLO model: {e}")
            self.model = None

    def detect(self, frame: np.ndarray):
        """
        Runs object detection and filters for cell phones with confidence >= threshold.
        Returns list of (x1, y1, x2, y2, confidence) bounding boxes.
        """
        if self.model is None:
            return []

        try:
            # Run inference; verbose=False to keep logs clean
            results = self.model(frame, conf=PHONE_CONF_THRESHOLD, classes=[self.PHONE_CLASS_ID], verbose=False)
            detections = []
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0].cpu().numpy())
                    detections.append((int(x1), int(y1), int(x2), int(y2), conf))
            return detections
        except Exception as e:
            print(f"[PhoneDetector] Inference error: {e}")
            return []

    def draw_detections(self, frame: np.ndarray, detections):
        """Draws highlighted orange/red bounding boxes around detected mobile phones."""
        for (x1, y1, x2, y2, conf) in detections:
            # Outer box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 140, 255), 2)
            # Label
            label = f"MOBILE PHONE {int(conf * 100)}%"
            cv2.putText(
                frame,
                label,
                (x1, max(20, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 140, 255),
                2,
                cv2.LINE_AA
            )
