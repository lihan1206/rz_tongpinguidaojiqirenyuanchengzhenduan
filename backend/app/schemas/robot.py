from datetime import datetime

from pydantic import BaseModel


class RobotCreate(BaseModel):
    device_id: str
    model: str | None = None
    location: str | None = None
    status: str = "离线"
    ip: str | None = None
    port: int | None = None


class RobotUpdate(BaseModel):
    model: str | None = None
    location: str | None = None
    status: str | None = None
    ip: str | None = None
    port: int | None = None


class RobotOut(BaseModel):
    id: int
    device_id: str
    model: str | None = None
    location: str | None = None
    status: str
    ip: str | None = None
    port: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class PositionIn(BaseModel):
    lat: float
    lng: float


class PositionOut(BaseModel):
    id: int
    robot_id: int
    lat: float
    lng: float
    ts: datetime

    class Config:
        from_attributes = True


class StatusLogOut(BaseModel):
    id: int
    robot_id: int
    from_status: str | None
    to_status: str
    ts: datetime
    note: str | None

    class Config:
        from_attributes = True
