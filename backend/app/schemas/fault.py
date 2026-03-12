from datetime import datetime

from pydantic import BaseModel


class FaultRuleCreate(BaseModel):
    name: str
    sensor_type: str
    operator: str = ">"
    threshold: int
    level: str = "严重"
    enabled: bool = True


class FaultRuleOut(BaseModel):
    id: int
    name: str
    sensor_type: str
    operator: str
    threshold: int
    level: str
    enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FaultLogOut(BaseModel):
    id: int
    robot_id: int
    rule_id: int | None
    fault_type: str
    description: str
    level: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
