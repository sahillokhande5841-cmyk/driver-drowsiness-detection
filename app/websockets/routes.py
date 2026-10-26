from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio

router = APIRouter()

detector = None


def set_detector(det):
    global detector
    detector = det


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    try:
        while True:

            if detector is not None:
                await websocket.send_json(detector.get_metrics())

            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        print("WebSocket disconnected")