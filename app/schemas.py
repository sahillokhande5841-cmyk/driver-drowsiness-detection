from typing import Optional
from pydantic import BaseModel


class Metrics(BaseModel):
    status: str
    fatigueScore: float

    ear: float
    earThreshold: Optional[float]

    mar: float

    pitch: float
    yaw: float
    roll: float

    blinkCount: int
    yawnCount: int

    headDown: bool