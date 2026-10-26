from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.detection import Detector

from app.websockets.routes import (
    router as websocket_router,
    set_detector,
)

app = FastAPI(
    title="Driver Drowsiness Detection API",
    version="1.0.0"
)

app.include_router(websocket_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = Detector()
set_detector(detector)


@app.get("/")
def root():
    return {
        "message": "Welcome to the Driver Drowsiness Detection API!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/start")
def start_detector():
    detector.start()
    return {
        "message": "Detector started successfully."
    }


@app.post("/stop")
def stop_detector():
    detector.stop()
    return {
        "message": "Detector stopped successfully."
    }


@app.get("/video_feed")
def video_feed():

    if detector.cap is None:
        raise HTTPException(
            status_code=400,
            detail="Detector is not running."
        )

    return StreamingResponse(
        detector.generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )