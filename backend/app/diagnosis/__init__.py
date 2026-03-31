"""
诊断模块
提供可扩展的诊断策略模式实现
"""

from app.diagnosis.interfaces import (
    DiagnosisResult,
    DiagnosisSeverity,
    DiagnosisStrategy,
    DiagnosisType,
    RobotDiagnosticData,
)
from app.diagnosis.service import DiagnosisService, DiagnosticSummary
from app.diagnosis.strategies import (
    TemperatureDiagnosisStrategy,
    PositionDiagnosisStrategy,
    MotorDiagnosisStrategy,
)

__all__ = [
    # 接口
    "DiagnosisResult",
    "DiagnosisSeverity",
    "DiagnosisStrategy",
    "DiagnosisType",
    "RobotDiagnosticData",
    # 服务
    "DiagnosisService",
    "DiagnosticSummary",
    # 策略
    "TemperatureDiagnosisStrategy",
    "PositionDiagnosisStrategy",
    "MotorDiagnosisStrategy",
]