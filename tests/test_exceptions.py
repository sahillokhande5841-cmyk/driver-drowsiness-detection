import pytest
from app.core.exceptions import AppException, DetectorNotRunningError, DetectorAlreadyRunningError

def test_app_exception_attributes():
    """Test AppException initialization and attributes."""
    exc = AppException(message="Custom failure occurred", status_code=400, details={"field": "test"})
    assert exc.message == "Custom failure occurred"
    assert exc.status_code == 400
    assert exc.details == {"field": "test"}

def test_detector_domain_exceptions():
    """Test specific detector domain exception subclasses."""
    not_running = DetectorNotRunningError()
    assert not_running.status_code == 400
    assert "not running" in not_running.message.lower()

    already_running = DetectorAlreadyRunningError()
    assert already_running.status_code == 409
    assert "already running" in already_running.message.lower()
