"""
诊断相关的 Pydantic Schemas (DTO)
用于API数据传输，与数据库Entity分离
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.diagnosis.interfaces import DiagnosisSeverity, DiagnosisType


class DiagnosisResultDTO(BaseModel):
    """诊断结果DTO"""
    diagnosis_type: DiagnosisType
    severity: DiagnosisSeverity
    is_anomaly: bool
    message: str
    details: Dict[str, Any] = {}
    timestamp: datetime
    robot_id: Optional[int] = None
    suggestion: Optional[str] = None

    class Config:
        from_attributes = True


class DiagnosticSummaryDTO(BaseModel):
    """诊断摘要DTO"""
    robot_id: int
    device_id: str
    overall_status: DiagnosisSeverity
    total_checks: int
    anomaly_count: int
    warning_count: int
    critical_count: int
    results: List[DiagnosisResultDTO]
    timestamp: datetime

    class Config:
        from_attributes = True


class DiagnosisStrategyInfoDTO(BaseModel):
    """诊断策略信息DTO"""
    type: str
    name: str
    description: str


class DiagnosisConfigDTO(BaseModel):
    """诊断配置DTO"""
    id: Optional[int] = None
    diagnosis_type: str
    enabled: bool = True
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class DiagnosisConfigUpdate(BaseModel):
    """诊断配置更新DTO"""
    enabled: Optional[bool] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    description: Optional[str] = None


class DiagnosisRequest(BaseModel):
    """诊断请求DTO"""
    robot_id: int
    diagnosis_types: Optional[List[str]] = None


class DiagnosisRecordDTO(BaseModel):
    """诊断记录DTO"""
    id: int
    robot_id: int
    diagnosis_type: str
    severity: str
    is_anomaly: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    suggestion: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DiagnosisRecordCreate(BaseModel):
    """创建诊断记录DTO"""
    robot_id: int
    diagnosis_type: str
    severity: str
    is_anomaly: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    suggestion: Optional[str] = None


class RobotDiagnosticDataRequest(BaseModel):
    """机器人诊断数据请求DTO - 用于手动传入诊断数据"""
    robot_id: int
    device_id: str
    temperature: Optional[float] = None
    temperature_threshold: float = 80.0
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    expected_lat: Optional[float] = None
    expected_lng: Optional[float] = None
    position_tolerance: float = 5.0
    motor_current: Optional[float] = None
    motor_rated_current: Optional[float] = None
    motor_load_percentage: Optional[float] = None
    motor_overload_threshold: float = 90.0
    status: Optional[str] = None
    raw_sensor_data: Dict[str, Any] = {}


class DiagnosisResponse(BaseModel):
    """通用诊断响应"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
