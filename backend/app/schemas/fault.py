from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class FaultRuleCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100, description="规则名称")]
    sensor_type: Annotated[str, Field(min_length=1, max_length=50, description="传感器类型")]
    operator: Annotated[str, Field(description="比较运算符")] = ">"
    threshold: Annotated[int, Field(description="阈值")]
    level: Annotated[str, Field(max_length=20, description="告警级别")] = "严重"
    enabled: bool = True

    @Field.validator("operator")
    @classmethod
    def validate_operator(cls, v: str) -> str:
        valid_operators = [">", ">=", "<", "<=", "==", "!="]
        if v not in valid_operators:
            raise ValueError(f"运算符必须是以下之一: {valid_operators}")
        return v


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


class FaultLogStatusUpdate(BaseModel):
    status: Annotated[str, Field(description="状态")]


class ApiResponse(BaseModel):
    code: str = "SUCCESS"
    message: str = "操作成功"
    data: dict | None = None


class PagedResponse(BaseModel):
    code: str = "SUCCESS"
    message: str = "操作成功"
    data: list
    total: int | None = None
    page: int | None = None
    page_size: int | None = None
