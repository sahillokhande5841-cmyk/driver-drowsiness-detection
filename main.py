import cv2
import time
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.detection import Detector

def main():
    print("=" * 60)
    print(" AI Driver Drowsiness Detection System - Desktop OpenCV Runner ")
    print("=" * 60)
    print("Press 'q' or 'ESC' to exit.")
    print("Press 'r' to recalibrate baseline resting thresholds.")
    print("=" * 60)

    detector = Detector()
    detector.start()

    cv2.namedWindow("Driver Drowsiness Safety Monitor", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Driver Drowsiness Safety Monitor", 960, 720)

    try:
        while True:
            metrics = detector.get_metrics()
            with detector.lock:
                frame = detector.latest_frame.copy() if detector.latest_frame is not None else None

            if frame is not None:
                cv2.imshow("Driver Drowsiness Safety Monitor", frame)

            key = cv2.waitKey(20) & 0xFF
            if key == ord('q') or key == 27:
                print("\n[Runner] Exit requested by user.")
                break
            elif key == ord('r'):
                print("\n[Runner] Triggering recalibration...")
                detector.recalibrate()

    except KeyboardInterrupt:
        print("\n[Runner] Interrupted by keyboard.")
    finally:
        detector.stop()
        cv2.destroyAllWindows()
        print("[Runner] Cleanup completed successfully.")

if __name__ == "__main__":
    main()
