from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json
from app.api.v1.endpoints.detector import get_detector

router = APIRouter()

@router.websocket("/ws")
async def websocket_telemetry(websocket: WebSocket):
    """
    Streams high-frequency real-time biometric telemetry at 10Hz to connected clients.
    Carries EAR, MAR, Pitch, Yaw, Roll, status, fatigue score, blinks, yawns, and active alerts.
    """
    await websocket.accept()
    detector = get_detector()

    try:
        while True:
            # Gather detector telemetry
            metrics = detector.get_metrics()

            # Ensure valid JSON types
            safe_payload = {
                "status": metrics.get("status", "NORMAL"),
                "cameraStatus": metrics.get("cameraStatus", "ready"),
                "faceDetected": bool(metrics.get("faceDetected", False)),
                "fatigueScore": float(metrics.get("fatigueScore", 0.0)),
                "ear": float(metrics.get("ear", 0.0)),
                "earThreshold": float(metrics.get("earThreshold", 0.20)),
                "mar": float(metrics.get("mar", 0.0)),
                "marThreshold": float(metrics.get("marThreshold", 0.52)),
                "pitch": float(metrics.get("pitch", 0.0)),
                "yaw": float(metrics.get("yaw", 0.0)),
                "roll": float(metrics.get("roll", 0.0)),
                "blinkCount": int(metrics.get("blinkCount", 0)),
                "yawnCount": int(metrics.get("yawnCount", 0)),
                "isEyeClosed": bool(metrics.get("isEyeClosed", False)),
                "isYawning": bool(metrics.get("isYawning", False)),
                "isHeadDown": bool(metrics.get("isHeadDown", False)),
                "isPhoneDistracted": bool(metrics.get("isPhoneDistracted", False)),
                "fps": float(metrics.get("fps", 0.0)),
                "running": bool(metrics.get("running", False)),
                "activeAlert": metrics.get("activeAlert"),
                "recentEvents": metrics.get("recentEvents", []),
                "calibrating": bool(metrics.get("calibrating", False))
            }

            await websocket.send_text(json.dumps(safe_payload))
            await asyncio.sleep(0.1)  # 10 Hz refresh rate

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[WebSocket] Disconnected with error: {e}")
