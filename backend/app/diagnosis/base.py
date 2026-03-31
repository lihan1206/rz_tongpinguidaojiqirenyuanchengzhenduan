from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class DiagnosisType(str, Enum):
    TEMPERATURE = "temperature"
    VIBRATION = "vibration"
    POSITION = "position"
    PRESSURE = "pressure"
    HUMIDITY = "humidity"
    VOLTAGE = "voltage"
    CURRENT = "current"
    SPEED = "speed"
    CUSTOM = "custom"


class OperatorType(str, Enum):
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    EQ = "=="
    NEQ = "!="
    BETWEEN = "between"
    OUTSIDE = "outside"


@dataclass
class DiagnosisContext:
    robot_id: int
    sensor_type: str
    value: float
    raw_data: dict[str, Any] | None = None


@dataclass
class DiagnosisResult:
    triggered: bool
    rule_id: int | None = None
    rule_name: str | None = None
    fault_type: str | None = None
    description: str | None = None
    level: str = "一般"
    extra: dict[str, Any] | None = None


class DiagnosisStrategy(ABC):
    @property
    @abstractmethod
    def diagnosis_type(self) -> DiagnosisType:
        pass

    @abstractmethod
    def evaluate(self, context: DiagnosisContext, rule: Any) -> DiagnosisResult:
        pass

    @abstractmethod
    def generate_description(self, context: DiagnosisContext, rule: Any) -> str:
        pass

    def supports(self, sensor_type: str) -> bool:
        return sensor_type.lower() == self.diagnosis_type.value


class BaseDiagnosisStrategy(DiagnosisStrategy):
    def _compare(self, value: float, operator: str, threshold: float) -> bool:
        match operator:
            case OperatorType.GT.value:
                return value > threshold
            case OperatorType.GTE.value:
                return value >= threshold
            case OperatorType.LT.value:
                return value < threshold
            case OperatorType.LTE.value:
                return value <= threshold
            case OperatorType.EQ.value:
                return abs(value - threshold) < 1e-9
            case OperatorType.NEQ.value:
                return abs(value - threshold) >= 1e-9
            case _:
                return False

    def evaluate(self, context: DiagnosisContext, rule: Any) -> DiagnosisResult:
        triggered = self._compare(context.value, rule.operator, float(rule.threshold))
        return DiagnosisResult(
            triggered=triggered,
            rule_id=rule.id,
            rule_name=rule.name,
            fault_type=rule.name,
            description=self.generate_description(context, rule) if triggered else None,
            level=rule.level,
        )

    def generate_description(self, context: DiagnosisContext, rule: Any) -> str:
        return f"传感器[{context.sensor_type}]数值为{context.value}，触发规则：{rule.operator}{rule.threshold}"
