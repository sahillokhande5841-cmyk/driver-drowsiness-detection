from typing import Optional, Any, List, Dict
from pydantic import BaseModel, Field, ConfigDict

class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    status: str = Field(..., description="Service health status", json_schema_extra={"example": "healthy"})
    cameraStatus: str = Field(default="ready", description="Camera connectivity status")
    running: bool = Field(default=False, description="Whether detector is running")
    faceDetected: bool = Field(default=False, description="Whether driver face is currently detected")
    service: Optional[str] = Field(default="Driver Drowsiness Detection API", description="Service name")
    version: Optional[str] = Field(default="2.0.0", description="API version")
    timestamp: Optional[str] = Field(default=None, description="ISO timestamp")

class MessageResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    message: str = Field(..., description="Status or result message")
    success: bool = True

class SettingsUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")
    earThreshold: Optional[float] = None
    marThreshold: Optional[float] = None
    language: Optional[str] = None  # "hi" or "en"
    audioEnabled: Optional[bool] = None

class StatusResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    running: bool
    cameraStatus: str
    faceDetected: bool
    status: str
    earThreshold: float
    marThreshold: float
    language: str
    audioEnabled: bool
