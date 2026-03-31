from app.diagnosis.base import (
    BaseDiagnosisStrategy,
    DiagnosisContext,
    DiagnosisResult,
    DiagnosisType,
)


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
