from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings
from app.schemas import HealthResponse
from app.api.v1.endpoints.detector import get_detector

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check() -> HealthResponse:
    """Returns application health status, service metadata, and timestamp."""
    det = get_detector()
    is_running = bool(getattr(det, "running", False))
    cam_status = "active" if getattr(det, "cap", None) is not None else "ready"

    return HealthResponse(
        status="healthy",
        cameraStatus=cam_status,
        running=is_running,
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
