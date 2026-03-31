"""
电机过载诊断策略
检测电机电流和负载是否超过额定值
"""

from typing import Dict, Any

from app.diagnosis.interfaces import (
    DiagnosisResult,
    DiagnosisSeverity,
    DiagnosisStrategy,
    DiagnosisType,
    RobotDiagnosticData,
)


class MotorDiagnosisStrategy(DiagnosisStrategy):
    """
    电机过载诊断策略
    检测电机电流和负载是否超过额定值
    """

    # 负载阈值（百分比）
    WARNING_THRESHOLD = 80.0   # 警告阈值（%）
    CRITICAL_THRESHOLD = 95.0  # 严重阈值（%）
    NORMAL_MAX = 70.0          # 正常上限（%）

    @property
    def diagnosis_type(self) -> DiagnosisType:
        return DiagnosisType.MOTOR

    def diagnose(self, data: RobotDiagnosticData) -> DiagnosisResult:
        """
        执行电机诊断

        诊断逻辑：
        - 负载 < 70%: 正常
        - 70% <= 负载 < 80%: 轻微偏高
        - 80% <= 负载 < 95%: 警告
        - 负载 >= 95%: 严重
        """
        robot_id = data.robot_id

        # 计算电机负载百分比
        load_percentage = self._calculate_load_percentage(data)

        if load_percentage is None:
            return DiagnosisResult(
                diagnosis_type=self.diagnosis_type,
                severity=DiagnosisSeverity.NORMAL,
                is_anomaly=False,
                message="无电机数据，无法诊断",
                robot_id=robot_id,
                details={"available": False},
                suggestion="请检查电机电流传感器是否正常工作"
            )

        # 获取电流值
        motor_current = data.motor_current
        rated_current = data.motor_rated_current

        details: Dict[str, Any] = {
            "available": True,
            "motor_current": motor_current,
            "rated_current": rated_current,
            "load_percentage": round(load_percentage, 2),
            "warning_threshold": self.WARNING_THRESHOLD,
            "critical_threshold": self.CRITICAL_THRESHOLD,
            "normal_max": self.NORMAL_MAX,
            "current_margin": round(self.CRITICAL_THRESHOLD - load_percentage, 2) if load_percentage < self.CRITICAL_THRESHOLD else 0,
        }

        # 添加额外诊断信息
        if motor_current is not None and rated_current is not None and rated_current > 0:
            details["current_ratio"] = round(motor_current / rated_current, 2)

        # 诊断逻辑
        if load_percentage >= self.CRITICAL_THRESHOLD:
            return DiagnosisResult(
                diagnosis_type=self.diagnosis_type,
                severity=DiagnosisSeverity.CRITICAL,
                is_anomaly=True,
                message=f"电机严重过载！当前负载: {load_percentage:.1f}%，超过临界值 {self.CRITICAL_THRESHOLD}%",
                robot_id=robot_id,
                details=details,
                suggestion="立即降低负载或停机检查！可能原因：1)机械卡阻 2)负载过重 3)电机故障 4)传动系统异常"
            )
        elif load_percentage >= self.WARNING_THRESHOLD:
            return DiagnosisResult(
                diagnosis_type=self.diagnosis_type,
                severity=DiagnosisSeverity.WARNING,
                is_anomaly=True,
                message=f"电机过载警告！当前负载: {load_percentage:.1f}%，超过警告阈值 {self.WARNING_THRESHOLD}%",
                robot_id=robot_id,
                details=details,
                suggestion="建议降低运行速度或检查负载情况。可能原因：1)负载增加 2)传动效率下降 3)电机老化"
            )
        elif load_percentage >= self.NORMAL_MAX:
            return DiagnosisResult(
                diagnosis_type=self.diagnosis_type,
                severity=DiagnosisSeverity.NORMAL,
                is_anomaly=False,
                message=f"电机负载偏高，当前负载: {load_percentage:.1f}%",
                robot_id=robot_id,
                details=details,
                suggestion="电机负载在正常范围内但偏高，建议监控运行状态"
            )
        else:
            return DiagnosisResult(
                diagnosis_type=self.diagnosis_type,
                severity=DiagnosisSeverity.NORMAL,
                is_anomaly=False,
                message=f"电机运行正常，当前负载: {load_percentage:.1f}%",
                robot_id=robot_id,
                details=details,
                suggestion="电机运行状态良好"
            )

    def _calculate_load_percentage(self, data: RobotDiagnosticData) -> float:
        """
        计算电机负载百分比

        优先使用直接提供的负载百分比，否则根据电流计算
        """
        # 如果直接提供了负载百分比
        if data.motor_load_percentage is not None:
            return data.motor_load_percentage

        # 根据电流计算负载百分比
        if data.motor_current is not None and data.motor_rated_current is not None:
            if data.motor_rated_current > 0:
                return (data.motor_current / data.motor_rated_current) * 100

        # 从原始传感器数据中尝试获取
        raw_data = data.raw_sensor_data
        if "motor_load" in raw_data:
            return float(raw_data["motor_load"])
        if "motor_current" in raw_data and "rated_current" in raw_data:
            current = float(raw_data["motor_current"])
            rated = float(raw_data["rated_current"])
            if rated > 0:
                return (current / rated) * 100

        return None

    def _analyze_motor_health(self, data: RobotDiagnosticData) -> Dict[str, Any]:
        """
        分析电机健康状况（扩展功能）
        """
        raw_data = data.raw_sensor_data
        health_info = {
            "vibration_level": raw_data.get("vibration"),
            "temperature": raw_data.get("motor_temperature"),
            "operating_hours": raw_data.get("operating_hours"),
            "efficiency": None
        }

        # 简单效率估算
        if data.motor_load_percentage is not None:
            # 电机在低负载时效率较低
            load = data.motor_load_percentage
            if load < 30:
                health_info["efficiency"] = "low"
            elif load < 70:
                health_info["efficiency"] = "optimal"
            elif load < 90:
                health_info["efficiency"] = "good"
            else:
                health_info["efficiency"] = "stressed"

        return health_info

    def get_description(self) -> str:
        return "检测电机电流和负载是否超过额定值，支持基于电流计算和直接负载百分比两种方式"
