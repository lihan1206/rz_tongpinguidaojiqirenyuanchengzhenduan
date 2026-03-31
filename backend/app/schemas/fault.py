from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class FaultRuleCreate(BaseModel):
    """创建故障规则DTO"""
    name: str = Field(..., min_length=1, max_length=100, description="规则名称")
    sensor_type: str = Field(..., min_length=1, max_length=50, description="传感器类型")
    operator: str = Field(">", min_length=1, max_length=10, description="比较运算符")
    threshold: int = Field(..., description="阈值")
    level: str = Field("严重", min_length=1, max_length=20, description="故障级别")
    enabled: bool = Field(True, description="是否启用")

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, v: str) -> str:
        valid_operators = [">", ">=", "<", "<=", "==", "!="]
        if v not in valid_operators:
            raise ValueError(f"无效的运算符，支持: {valid_operators}")
        return v


class FaultRuleUpdate(BaseModel):
    """更新故障规则DTO"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="规则名称")
    sensor_type: Optional[str] = Field(None, min_length=1, max_length=50, description="传感器类型")
    operator: Optional[str] = Field(None, min_length=1, max_length=10, description="比较运算符")
    threshold: Optional[int] = Field(None, description="阈值")
    level: Optional[str] = Field(None, min_length=1, max_length=20, description="故障级别")
    enabled: Optional[bool] = Field(None, description="是否启用")

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid_operators = [">", ">=", "<", "<=", "==", "!="]
        if v not in valid_operators:
            raise ValueError(f"无效的运算符，支持: {valid_operators}")
        return v


class FaultRuleOut(BaseModel):
    """故障规则输出DTO"""
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


class FaultLogCreate(BaseModel):
    """创建故障日志DTO（内部使用）"""
    robot_id: int
    rule_id: Optional[int] = None
    fault_type: str
    description: str
    level: str
    status: str = "未处理"


class FaultLogOut(BaseModel):
    """故障日志输出DTO"""
    id: int
    robot_id: int
    rule_id: Optional[int]
    fault_type: str
    description: str
    level: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DiagnoseRequest(BaseModel):
    """诊断请求DTO"""
    robot_id: int = Field(..., description="机器人ID")
    sensor_type: Optional[str] = Field(None, description="传感器类型，不指定则诊断所有类型")


class DiagnoseResultItem(BaseModel):
    """诊断结果项DTO"""
    is_fault: bool
    fault_type: str
    level: str
    description: str
    rule_id: Optional[int] = None
    sensor_data: Optional[Dict[str, Any]] = None


class DiagnoseResponse(BaseModel):
    """诊断响应DTO"""
    robot_id: int
    results: list[DiagnoseResultItem]
    fault_count: int
    executed_at: datetime


class FaultStatusUpdate(BaseModel):
    """故障状态更新DTO"""
    status: str = Field(..., min_length=1, max_length=20, description="故障状态")
