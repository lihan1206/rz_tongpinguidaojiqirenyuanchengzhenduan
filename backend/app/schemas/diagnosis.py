from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, Field

from app.diagnosis.base import DiagnosisType


class DiagnosisRequestDTO(BaseModel):
    robot_id: Annotated[int, Field(gt=0, description="机器人ID")]
    diagnosis_types: list[DiagnosisType] | None = Field(default=None, description="诊断类型列表，为空则执行所有诊断")


class SensorDataDTO(BaseModel):
    sensor_type: str
    value: float
    ts: datetime | None = None


class DiagnosisResultDTO(BaseModel):
    triggered: bool
    diagnosis_type: DiagnosisType
    rule_id: int | None = None
    rule_name: str | None = None
    fault_type: str | None = None
    description: str | None = None
    level: str = "一般"
    extra: dict[str, Any] | None = None


class RobotDiagnosisSummaryDTO(BaseModel):
    robot_id: int
    robot_device_id: str | None = None
    robot_status: str | None = None
    diagnosis_time: datetime
    total_checks: int
    triggered_count: int
    results: list[DiagnosisResultDTO]


class DiagnosisReportDTO(BaseModel):
    robot_id: int
    robot_device_id: str
    diagnosis_type: DiagnosisType
    sensor_value: float | None = None
    threshold: float | None = None
    operator: str | None = None
    is_abnormal: bool
    severity: str
    description: str
    recommendation: str | None = None
    timestamp: datetime


class DiagnosisRuleDTO(BaseModel):
    id: int
    name: str
    sensor_type: str
    operator: str
    threshold: float
    level: str
    enabled: bool

    class Config:
        from_attributes = True


class DiagnosisTypeOutDTO(BaseModel):
    type_code: str
    type_name: str
    description: str
    supported_operators: list[str]


class DiagnosisTypeInfoDTO:
    TYPE_INFO: dict[DiagnosisType, dict[str, Any]] = {
        DiagnosisType.TEMPERATURE: {
            "type_name": "温度诊断",
            "description": "检测机器人运行温度是否超过安全阈值",
            "supported_operators": [">", ">=", "<", "<=", "==", "!="],
        },
        DiagnosisType.POSITION: {
            "type_name": "位置诊断",
            "description": "检测机器人位置是否偏离预定轨道",
            "supported_operators": [">", ">=", "<", "<=", "outside"],
        },
        DiagnosisType.MOTOR_OVERLOAD: {
            "type_name": "电机过载诊断",
            "description": "检测电机负载是否超过额定功率",
            "supported_operators": [">", ">=", "=="],
        },
        DiagnosisType.VIBRATION: {
            "type_name": "振动诊断",
            "description": "检测机器人振动是否异常",
            "supported_operators": [">", ">=", "<", "<="],
        },
        DiagnosisType.PRESSURE: {
            "type_name": "压力诊断",
            "description": "检测系统压力是否正常",
            "supported_operators": [">", ">=", "<", "<=", "==", "!="],
        },
        DiagnosisType.HUMIDITY: {
            "type_name": "湿度诊断",
            "description": "检测环境湿度是否在正常范围",
            "supported_operators": [">", ">=", "<", "<="],
        },
        DiagnosisType.VOLTAGE: {
            "type_name": "电压诊断",
            "description": "检测供电电压是否稳定",
            "supported_operators": [">", ">=", "<", "<=", "==", "!="],
        },
        DiagnosisType.CURRENT: {
            "type_name": "电流诊断",
            "description": "检测工作电流是否正常",
            "supported_operators": [">", ">=", "<", "<="],
        },
        DiagnosisType.SPEED: {
            "type_name": "速度诊断",
            "description": "检测运行速度是否符合预期",
            "supported_operators": [">", ">=", "<", "<="],
        },
    }

    @classmethod
    def get_info(cls, diagnosis_type: DiagnosisType) -> dict[str, Any] | None:
        return cls.TYPE_INFO.get(diagnosis_type)

    @classmethod
    def list_all(cls) -> list[DiagnosisTypeOutDTO]:
        result = []
        for dt, info in cls.TYPE_INFO.items():
            result.append(
                DiagnosisTypeOutDTO(
                    type_code=dt.value,
                    type_name=info["type_name"],
                    description=info["description"],
                    supported_operators=info["supported_operators"],
                )
            )
        return result
