from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import register_exception_handlers
from app.api.v1.api import api_router
from app.api.v1.endpoints.detector import (
    get_detector,
    set_detector,
    start_detector,
    stop_detector,
    recalibrate_detector,
    update_detector_settings,
    get_detector_status,
    get_detector_events,
    video_feed,
)
from app.api.v1.endpoints.health import health_check
from app.websockets.routes import (
    router as websocket_router,
    set_detector as set_websocket_detector,
)

# Initialize structured logging
setup_logging()
logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    # Ensure detector instance is shared across HTTP and WebSockets
    shared_detector = get_detector()
    set_websocket_detector(shared_detector)
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}")
    if shared_detector.running:
        shared_detector.stop()


# Initialize FastAPI Application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI Driver Drowsiness & Safety Detection Backend with Real-Time Video, Facial Landmarks and Distraction Analysis",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register structured exception handlers
register_exception_handlers(app)

# Configure CORS Middleware (Allow all local origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Router under /api
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include WebSocket Router under /ws
app.include_router(websocket_router)

# --------------------------------------------------------------------------
# Root and Backwards-Compatible Endpoints for Frontend
# --------------------------------------------------------------------------
@app.get("/", tags=["General"])
def root():
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME}!",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
        "status": "/status"
    }


# Backwards compatibility root aliases
app.add_api_route("/health", health_check, methods=["GET"], include_in_schema=False)
app.add_api_route("/status", get_detector_status, methods=["GET"], include_in_schema=False)
app.add_api_route("/start", start_detector, methods=["POST"], include_in_schema=False)
app.add_api_route("/stop", stop_detector, methods=["POST"], include_in_schema=False)
app.add_api_route("/recalibrate", recalibrate_detector, methods=["POST"], include_in_schema=False)
app.add_api_route("/settings", update_detector_settings, methods=["POST"], include_in_schema=False)
app.add_api_route("/events", get_detector_events, methods=["GET"], include_in_schema=False)
app.add_api_route("/video_feed", video_feed, methods=["GET"], include_in_schema=False)
