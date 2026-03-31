from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class SensorIn(BaseModel):
    robot_id: Annotated[int, Field(ge=1, description="机器人ID")]
    sensor_type: Annotated[str, Field(min_length=1, max_length=50, description="传感器类型")]
    value: Annotated[float, Field(description="传感器数值")]


class SensorOut(BaseModel):
    id: int
    robot_id: int
    sensor_type: str
    value: float
    ts: datetime

    class Config:
        from_attributes = True
