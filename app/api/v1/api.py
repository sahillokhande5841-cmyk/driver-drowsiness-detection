from fastapi import APIRouter
from app.api.v1.endpoints import health, detector

api_router = APIRouter()

# Health endpoints -> /api/health
api_router.include_router(health.router)

# Detector endpoints -> /api/start, /api/stop, /api/video_feed
api_router.include_router(detector.router)
