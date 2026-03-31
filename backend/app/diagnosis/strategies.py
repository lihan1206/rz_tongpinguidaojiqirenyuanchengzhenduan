from dataclasses import dataclass
from typing import Any

from app.diagnosis.base import (
    BaseDiagnosisStrategy,
    DiagnosisContext,
    DiagnosisResult,
    DiagnosisType,
)


@dataclass
class MotorOverloadContext:
    robot_id: int
    current_load: float
    rated_power: float
    running_time_minutes: float
    temperature: float | None = None


class TemperatureDiagnosisStrategy(BaseDiagnosisStrategy):
    @property
    def diagnosis_type(self) -> DiagnosisType:
        return DiagnosisType.TEMPERATURE

    def generate_description(self, context: DiagnosisContext, rule) -> str:
        if context.value > float(rule.threshold):
            return f"温度异常：机器人#{context.robot_id}温度{context.value}°C超过阈值{rule.threshold}°C"
        return f"温度异常：机器人#{context.robot_id}温度{context.value}°C低于阈值{rule.threshold}°C"


class VibrationDiagnosisStrategy(BaseDiagnosisStrategy):
    @property
    def diagnosis_type(self) -> DiagnosisType:
        return DiagnosisType.VIBRATION

    def generate_description(self, context: DiagnosisContext, rule) -> str:
        return f"振动异常：机器人#{context.robot_id}振动值{context.value}mm/s触发规则{rule.operator}{rule.threshold}"


class PositionDiagnosisStrategy(BaseDiagnosisStrategy):
    @property
    def diagnosis_type(self) -> DiagnosisType:
        return DiagnosisType.POSITION

    def evaluate(self, context: DiagnosisContext, rule) -> DiagnosisResult:
        if rule.operator == "outside":
            triggered = context.value < float(rule.threshold) or context.value > float(rule.threshold) * 2
        else:
            triggered = self._compare(context.value, rule.operator, float(rule.threshold))
        return DiagnosisResult(
            triggered=triggered,
            rule_id=rule.id,
            rule_name=rule.name,
            fault_type=rule.name,
            description=self.generate_description(context, rule) if triggered else None,
            level=rule.level,
        )

    def generate_description(self, context: DiagnosisContext, rule) -> str:
        return f"位置异常：机器人#{context.robot_id}位置偏离正常范围，当前值{context.value}"


class PressureDiagnosisStrategy(BaseDiagnosisStrategy):
    @property
    def diagnosis_type(self) -> DiagnosisType:
        return DiagnosisType.PRESSURE

    def generate_description(self, context: DiagnosisContext, rule) -> str:
        return f"压力异常：机器人#{context.robot_id}压力值{context.value}MPa触发规则{rule.operator}{rule.threshold}"


class HumidityDiagnosisStrategy(BaseDiagnosisStrategy):
    @property
    def diagnosis_type(self) -> DiagnosisType:
        return DiagnosisType.HUMIDITY

    def generate_description(self, context: DiagnosisContext, rule) -> str:
        return f"湿度异常：机器人#{context.robot_id}湿度{context.value}%触发规则{rule.operator}{rule.threshold}%"


class VoltageDiagnosisStrategy(BaseDiagnosisStrategy):
    @property
    def diagnosis_type(self) -> DiagnosisType:
        return DiagnosisType.VOLTAGE

    def generate_description(self, context: DiagnosisContext, rule) -> str:
        return f"电压异常：机器人#{context.robot_id}电压{context.value}V触发规则{rule.operator}{rule.threshold}V"


class CurrentDiagnosisStrategy(BaseDiagnosisStrategy):
    @property
    def diagnosis_type(self) -> DiagnosisType:
        return DiagnosisType.CURRENT

    def generate_description(self, context: DiagnosisContext, rule) -> str:
        return f"电流异常：机器人#{context.robot_id}电流{context.value}A触发规则{rule.operator}{rule.threshold}A"


class SpeedDiagnosisStrategy(BaseDiagnosisStrategy):
    @property
    def diagnosis_type(self) -> DiagnosisType:
        return DiagnosisType.SPEED

    def generate_description(self, context: DiagnosisContext, rule) -> str:
        return f"速度异常：机器人#{context.robot_id}速度{context.value}m/s触发规则{rule.operator}{rule.threshold}m/s"


class MotorOverloadDiagnosisStrategy(BaseDiagnosisStrategy):
    OVERLOAD_THRESHOLD_RATIO = 1.2
    CRITICAL_OVERLOAD_RATIO = 1.5
    OVERHEAT_TEMPERATURE = 80.0
    LONG_RUNNING_MINUTES = 60

    @property
    def diagnosis_type(self) -> DiagnosisType:
        return DiagnosisType.MOTOR_OVERLOAD

    def evaluate(self, context: DiagnosisContext, rule: Any) -> DiagnosisResult:
        triggered = self._compare(context.value, rule.operator, float(rule.threshold))
        load_ratio = context.value / float(rule.threshold) if float(rule.threshold) > 0 else 0

        extra_info = {
            "load_ratio": load_ratio,
            "is_critical": load_ratio >= self.CRITICAL_OVERLOAD_RATIO,
            "overload_percentage": (load_ratio - 1) * 100 if load_ratio > 1 else 0,
        }

        return DiagnosisResult(
            triggered=triggered,
            rule_id=rule.id,
            rule_name=rule.name,
            fault_type=rule.name,
            description=self.generate_description(context, rule) if triggered else None,
            level=self._determine_severity(load_ratio, rule.level),
            extra=extra_info,
        )

    def _determine_severity(self, load_ratio: float, base_level: str) -> str:
        if load_ratio >= self.CRITICAL_OVERLOAD_RATIO:
            return "紧急"
        if load_ratio >= self.OVERLOAD_THRESHOLD_RATIO:
            return "严重"
        return base_level

    def generate_description(self, context: DiagnosisContext, rule: Any) -> str:
        threshold = float(rule.threshold)
        load_ratio = context.value / threshold if threshold > 0 else 0
        overload_percent = (load_ratio - 1) * 100 if load_ratio > 1 else 0

        if load_ratio >= self.CRITICAL_OVERLOAD_RATIO:
            return (
                f"电机严重过载：机器人#{context.robot_id}负载{context.value}W，"
                f"超过额定功率{threshold}W的{overload_percent:.1f}%，存在烧毁风险，请立即停机检查！"
            )
        elif load_ratio >= self.OVERLOAD_THRESHOLD_RATIO:
            return (
                f"电机过载警告：机器人#{context.robot_id}负载{context.value}W，"
                f"超过额定功率{threshold}W的{overload_percent:.1f}%，建议降低负载或停机冷却"
            )
        return (
            f"电机负载偏高：机器人#{context.robot_id}负载{context.value}W，"
            f"接近额定功率{threshold}W，请关注运行状态"
        )

    def diagnose_motor_status(
        self, motor_context: MotorOverloadContext, rule: Any
    ) -> DiagnosisResult:
        load_ratio = motor_context.current_load / motor_context.rated_power
        is_overload = load_ratio > self.OVERLOAD_THRESHOLD_RATIO
        is_critical = load_ratio >= self.CRITICAL_OVERLOAD_RATIO
        is_overheating = (
            motor_context.temperature is not None
            and motor_context.temperature > self.OVERHEAT_TEMPERATURE
        )
        is_long_running = motor_context.running_time_minutes > self.LONG_RUNNING_MINUTES

        triggered = is_overload or is_overheating

        extra_info = {
            "load_ratio": load_ratio,
            "is_critical": is_critical,
            "is_overheating": is_overheating,
            "is_long_running": is_long_running,
            "running_time_minutes": motor_context.running_time_minutes,
            "temperature": motor_context.temperature,
            "recommendations": self._generate_recommendations(
                is_overload, is_critical, is_overheating, is_long_running
            ),
        }

        description = None
        if triggered:
            description = self._generate_motor_description(
                motor_context, is_critical, is_overheating
            )

        return DiagnosisResult(
            triggered=triggered,
            rule_id=rule.id if rule else None,
            rule_name="电机过载综合诊断" if rule is None else rule.name,
            fault_type="电机过载",
            description=description,
            level=self._determine_motor_severity(
                is_critical, is_overheating, is_long_running
            ),
            extra=extra_info,
        )

    def _generate_recommendations(
        self,
        is_overload: bool,
        is_critical: bool,
        is_overheating: bool,
        is_long_running: bool,
    ) -> list[str]:
        recommendations = []
        if is_critical:
            recommendations.append("立即停机，检查电机和负载")
        if is_overheating:
            recommendations.append("检查散热系统，清理散热片")
        if is_long_running:
            recommendations.append("考虑安排停机休息，避免持续过热")
        if is_overload and not is_critical:
            recommendations.append("降低负载或检查机械部件是否有卡阻")
        return recommendations

    def _generate_motor_description(
        self,
        context: MotorOverloadContext,
        is_critical: bool,
        is_overheating: bool,
    ) -> str:
        load_percent = (context.current_load / context.rated_power) * 100
        parts = [f"机器人#{context.robot_id}电机异常："]

        if is_critical:
            parts.append(f"负载率{load_percent:.1f}%（严重过载）")
        else:
            parts.append(f"负载率{load_percent:.1f}%")

        if is_overheating:
            parts.append(f"温度{context.temperature}°C（过热）")

        parts.append(f"已运行{context.running_time_minutes:.0f}分钟")

        return "，".join(parts) + "。"

    def _determine_motor_severity(
        self, is_critical: bool, is_overheating: bool, is_long_running: bool
    ) -> str:
        if is_critical and is_overheating:
            return "紧急"
        if is_critical or is_overheating:
            return "严重"
        if is_long_running:
            return "警告"
        return "一般"
