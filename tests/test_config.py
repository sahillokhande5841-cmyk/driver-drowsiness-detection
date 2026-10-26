from app.core.config import Settings, settings


def test_settings_defaults():
    """Verify that settings have appropriate default values."""
    assert settings.PROJECT_NAME == "Driver Drowsiness Detection API"
    assert settings.API_V1_STR == "/api"
    assert isinstance(settings.PORT, int)
    assert settings.CALIBRATION_TIME == 5
    assert settings.CALIBRATION_FACTOR == 0.75
    assert settings.EYE_CLOSED_MIN_FRAMES == 15
    assert settings.MAR_THRESHOLD == 0.30
    assert settings.HEAD_DOWN_THRESHOLD == 20


def test_cors_origins_parsing():
    """Verify that CORS origins parse list and string formats properly."""
    custom_settings = Settings(
        CORS_ORIGINS=["http://test.local"],
        _env_file=None
    )
    assert "http://test.local" in custom_settings.CORS_ORIGINS

    parsed_settings = Settings(
        CORS_ORIGINS="http://foo.com, http://bar.com",
        _env_file=None
    )
    assert "http://foo.com" in parsed_settings.CORS_ORIGINS
    assert "http://bar.com" in parsed_settings.CORS_ORIGINS
