from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json


class Settings(BaseSettings):
    # Application Info
    PROJECT_NAME: str = "Driver Drowsiness Detection API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"

    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    # Detection & Calibration Parameters
    CALIBRATION_TIME: int = 5
    CALIBRATION_FACTOR: float = 0.75

    EYE_CLOSED_MIN_FRAMES: int = 15

    MAR_THRESHOLD: float = 0.30
    YAWN_MIN_FRAMES: int = 30

    HEAD_DOWN_THRESHOLD: int = 20
    HEAD_DOWN_MIN_FRAMES: int = 20

    ALARM_SOUND: str = "alarm.wav"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
