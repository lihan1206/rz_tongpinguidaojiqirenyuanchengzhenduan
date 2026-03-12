from datetime import datetime

from pydantic import BaseModel


class MaintenanceCommandOut(BaseModel):
    id: int
    name: str
    command_type: str
    default_params: dict


class RemoteCommandCreate(BaseModel):
    robot_id: int
    command_type: str
    params: dict = {}


class RemoteCommandUpdate(BaseModel):
    status: str
    result: str | None = None


class RemoteCommandOut(BaseModel):
    id: int
    robot_id: int
    command_type: str
    params: dict
    status: str
    result: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommandLogOut(BaseModel):
    id: int
    remote_command_id: int
    status: str
    result: str | None
    created_at: datetime

    class Config:
        from_attributes = True
