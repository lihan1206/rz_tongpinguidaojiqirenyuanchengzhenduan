"""
温度异常诊断策略
检测机器人温度是否超过安全阈值
"""

import math
from typing import Dict, Any

from app.diagnosis.interfaces import (
    DiagnosisResult,
    DiagnosisSeverity,
    DiagnosisStrategy,
    DiagnosisType,
    RobotDiagnosticData,
)


class TemperatureDiagnosisStrategy(DiagnosisStrategy):
    """
    温度异常诊断策略
    检测机器人温度是否超过安全阈值
    """

    # 温度阈值配置（摄氏度）
    WARNING_THRESHOLD = 70.0   # 警告阈值
    CRITICAL_THRESHOLD = 85.0  # 严重阈值
    NORMAL_MAX = 60.0          # 正常上限

    @property
    def diagnosis_type(self) -> DiagnosisType:
        return DiagnosisType.TEMPERATURE

    def diagnose(self, data: RobotDiagnosticData) -> DiagnosisResult:
        """
        执行温度诊断

        诊断逻辑：
        - 温度 < 60°C: 正常
        - 60°C <= 温度 < 70°C: 轻微偏高
        - 70°C <= 温度 < 85°C: 警告
        - 温度 >= 85°C: 严重
        """
        temperature = data.temperature
        robot_id = data.robot_id

        # 如果没有温度数据，返回正常状态
        if temperature is None:
            return DiagnosisResult(
                diagnosis_type=self.diagnosis_type,
                severity=DiagnosisSeverity.NORMAL,
                is_anomaly=False,
                message="无温度数据，无法诊断",
                robot_id=robot_id,
                details={"available": False},
                suggestion="请检查温度传感器是否正常工作"
            )

        # 计算与阈值的差距
        temp_diff_warning = temperature - self.WARNING_THRESHOLD
        temp_diff_critical = temperature - self.CRITICAL_THRESHOLD

        details: Dict[str, Any] = {
            "current_temperature": temperature,
            "warning_threshold": self.WARNING_THRESHOLD,
            "critical_threshold": self.CRITICAL_THRESHOLD,
            "normal_max": self.NORMAL_MAX,
            "temperature_trend": self._calculate_trend(data),
        }

        # 诊断逻辑
        if temperature >= self.CRITICAL_THRESHOLD:
            # 严重：温度超过临界值
            return DiagnosisResult(
                diagnosis_type=self.diagnosis_type,
                severity=DiagnosisSeverity.CRITICAL,
                is_anomaly=True,
                message=f"温度严重超标！当前温度: {temperature}°C，超过临界值 {self.CRITICAL_THRESHOLD}°C",
                robot_id=robot_id,
                details=details,
                suggestion="立即停机检查！可能原因：1)散热系统故障 2)环境温度过高 3)电机过载 4)冷却液不足"
            )
        elif temperature >= self.WARNING_THRESHOLD:
            # 警告：温度超过警告值
            return DiagnosisResult(
                diagnosis_type=self.diagnosis_type,
                severity=DiagnosisSeverity.WARNING,
                is_anomaly=True,
                message=f"温度偏高警告！当前温度: {temperature}°C，超过警告阈值 {self.WARNING_THRESHOLD}°C",
                robot_id=robot_id,
                details=details,
                suggestion="建议降低负载或检查散热系统。可能原因：1)散热风扇故障 2)通风不良 3)长时间高负载运行"
            )
        elif temperature >= self.NORMAL_MAX:
            # 轻微偏高
            return DiagnosisResult(
                diagnosis_type=self.diagnosis_type,
                severity=DiagnosisSeverity.NORMAL,
                is_anomaly=False,
                message=f"温度轻微偏高，当前温度: {temperature}°C，建议关注",
                robot_id=robot_id,
                details=details,
                suggestion="温度在正常范围内但偏高，建议监控温度变化趋势"
            )
        else:
            # 正常
            return DiagnosisResult(
                diagnosis_type=self.diagnosis_type,
                severity=DiagnosisSeverity.NORMAL,
                is_anomaly=False,
                message=f"温度正常，当前温度: {temperature}°C",
                robot_id=robot_id,
                details=details,
                suggestion="温度正常，继续保持监控"
            )

    def _calculate_trend(self, data: RobotDiagnosticData) -> str:
        """
        计算温度趋势（简化版，实际可能需要历史数据）
        """
        temperature = data.temperature
        threshold = data.temperature_threshold

        if temperature is None:
            return "unknown"

        ratio = temperature / threshold if threshold > 0 else 0

        if ratio >= 1.0:
            return "rising_critical"
        elif ratio >= 0.9:
            return "rising_warning"
        elif ratio >= 0.8:
            return "rising"
        else:
            return "stable"

    def get_description(self) -> str:
        return "检测机器人温度是否超过安全阈值，支持多级预警"
