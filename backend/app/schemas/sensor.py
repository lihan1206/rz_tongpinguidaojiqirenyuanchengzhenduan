from datetime import datetime

from pydantic import BaseModel


class SensorIn(BaseModel):
    robot_id: int
    sensor_type: str
    value: float


class SensorOut(BaseModel):
    id: int
    robot_id: int
    sensor_type: str
    value: float
    ts: datetime

    class Config:
        from_attributes = True
