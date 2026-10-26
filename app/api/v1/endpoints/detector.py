from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict, Any
from app.detection import Detector
from app.schemas import MessageResponse, SettingsUpdate, StatusResponse
from app.core.exceptions import DetectorNotRunningError
from app.core.logging import get_logger

logger = get_logger("app.api.detector")

router = APIRouter()

_detector: Optional[Detector] = None


def get_detector() -> Detector:
    global _detector
    if _detector is None:
        _detector = Detector()
    return _detector


def set_detector(detector: Detector) -> None:
    global _detector
    _detector = detector


@router.post("/start", response_model=MessageResponse, tags=["Detector"])
def start_detector() -> MessageResponse:
    det = get_detector()
    det.start()
    logger.info("Detector start requested and initiated.")
    return MessageResponse(message="Detector started successfully.")


@router.post("/stop", response_model=MessageResponse, tags=["Detector"])
def stop_detector() -> MessageResponse:
    det = get_detector()
    det.stop()
    logger.info("Detector stop requested and executed.")
    return MessageResponse(message="Detector stopped successfully.")


@router.post("/recalibrate", response_model=MessageResponse, tags=["Detector"])
def recalibrate_detector() -> MessageResponse:
    det = get_detector()
    if not det.running:
        raise DetectorNotRunningError("Detector is not running. Please start first.")
    det.recalibrate()
    logger.info("Detector recalibration requested.")
    return MessageResponse(message="Recalibration initiated.")


@router.get("/status", tags=["Detector"])
def get_detector_status() -> Dict[str, Any]:
    det = get_detector()
    return {
        "running": det.running,
        "cameraStatus": det.camera_status,
        "faceDetected": det.face_detected,
        "status": det.status,
        "earThreshold": det.ear_threshold,
        "marThreshold": det.mar_threshold,
        "language": det.alert_manager.language,
        "audioEnabled": det.alert_manager.audio_enabled,
    }


@router.post("/settings", tags=["Detector"])
def update_detector_settings(settings: SettingsUpdate) -> Dict[str, Any]:
    det = get_detector()
    if settings.earThreshold is not None:
        det.ear_threshold = settings.earThreshold
    if settings.marThreshold is not None:
        det.mar_threshold = settings.marThreshold
    if settings.language is not None:
        det.alert_manager.set_language(settings.language)
    if settings.audioEnabled is not None:
        det.alert_manager.set_audio_enabled(settings.audioEnabled)

    logger.info("Detector settings updated.")
    return {
        "message": "Settings updated successfully.",
        "earThreshold": det.ear_threshold,
        "marThreshold": det.mar_threshold,
        "language": det.alert_manager.language,
        "audioEnabled": det.alert_manager.audio_enabled,
    }


@router.get("/events", tags=["Detector"])
def get_detector_events() -> List[Dict[str, Any]]:
    det = get_detector()
    return det.alert_manager.get_events(50)


@router.get("/video_feed", tags=["Detector"])
def video_feed():
    det = get_detector()
    if not det.running:
        raise DetectorNotRunningError("Detector is not running. Please start the detector first.")

    return StreamingResponse(
        det.generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
