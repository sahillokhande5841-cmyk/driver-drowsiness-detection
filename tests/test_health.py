import pytest
from datetime import datetime
from app.api.v1.endpoints.health import health_check
from app.api.v1.endpoints.detector import get_detector_status, start_detector, stop_detector, get_detector

def test_api_health_endpoint():
    """Verify health_check endpoint function returns expected schema."""
    h = health_check()
    assert h.status == "healthy"
    assert h.service is not None
    assert h.version is not None
    assert h.timestamp is not None

def test_detector_status_endpoint():
    """Verify detector status returns all expected fields."""
    s = get_detector_status()
    assert "running" in s
    assert "cameraStatus" in s
    assert "faceDetected" in s
    assert "earThreshold" in s
    assert "marThreshold" in s
    assert "language" in s

def test_start_and_stop_lifecycle():
    """Verify detector start and stop lifecycle endpoints."""
    start_res = start_detector()
    assert start_res.message == "Detector started successfully."
    det = get_detector()
    assert det.running is True

    stop_res = stop_detector()
    assert stop_res.message == "Detector stopped successfully."
    assert det.running is False
