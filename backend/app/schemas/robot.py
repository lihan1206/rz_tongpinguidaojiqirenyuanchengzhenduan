from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class RobotCreate(BaseModel):
    device_id: Annotated[str, Field(min_length=1, max_length=80, description="设备ID")]
    model: Annotated[str | None, Field(max_length=80, description="型号")] = None
    location: Annotated[str | None, Field(max_length=200, description="位置")] = None
    status: Annotated[str, Field(max_length=30, description="状态")] = "离线"
    ip: Annotated[str | None, Field(max_length=60, description="IP地址")] = None
    port: Annotated[int | None, Field(ge=1, le=65535, description="端口")] = None

    @field_validator("ip")
    @classmethod
    def validate_ip(cls, v: str | None) -> str | None:
        if v is not None:
            import re
            pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
            if not re.match(pattern, v):
                raise ValueError("IP地址格式不正确")
        return v


class RobotUpdate(BaseModel):
    model: Annotated[str | None, Field(max_length=80)] = None
    location: Annotated[str | None, Field(max_length=200)] = None
    status: Annotated[str | None, Field(max_length=30)] = None
    ip: Annotated[str | None, Field(max_length=60)] = None
    port: Annotated[int | None, Field(ge=1, le=65535)] = None


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
    lat: Annotated[float, Field(ge=-90, le=90, description="纬度")]
    lng: Annotated[float, Field(ge=-180, le=180, description="经度")]


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
