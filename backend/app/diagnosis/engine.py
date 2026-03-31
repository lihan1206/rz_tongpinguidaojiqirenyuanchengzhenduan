from typing import Any

from app.core.exceptions import BusinessException
from app.diagnosis.base import (
    DiagnosisContext,
    DiagnosisResult,
    DiagnosisStrategy,
    DiagnosisType,
)
from app.diagnosis.strategies import (
    CurrentDiagnosisStrategy,
    HumidityDiagnosisStrategy,
    MotorOverloadDiagnosisStrategy,
    PositionDiagnosisStrategy,
    PressureDiagnosisStrategy,
    SpeedDiagnosisStrategy,
    TemperatureDiagnosisStrategy,
    VibrationDiagnosisStrategy,
    VoltageDiagnosisStrategy,
)


class DiagnosisStrategyFactory:
    _strategies: dict[DiagnosisType, DiagnosisStrategy] = {}

    @classmethod
    def register(cls, strategy: DiagnosisStrategy) -> None:
        cls._strategies[strategy.diagnosis_type] = strategy

    @classmethod
    def get_strategy(cls, diagnosis_type: DiagnosisType) -> DiagnosisStrategy:
        strategy = cls._strategies.get(diagnosis_type)
        if not strategy:
            raise BusinessException(f"不支持的诊断类型: {diagnosis_type}")
        return strategy

    @classmethod
    def get_strategy_by_sensor_type(cls, sensor_type: str) -> DiagnosisStrategy | None:
        try:
            diagnosis_type = DiagnosisType(sensor_type.lower())
            return cls._strategies.get(diagnosis_type)
        except ValueError:
            return None

    @classmethod
    def list_supported_types(cls) -> list[str]:
        return [t.value for t in cls._strategies.keys()]


class DiagnosisEngine:
    def __init__(self):
        self._factory = DiagnosisStrategyFactory

    def diagnose(self, context: DiagnosisContext, rules: list[Any]) -> list[DiagnosisResult]:
        results = []
        for rule in rules:
            strategy = self._factory.get_strategy_by_sensor_type(rule.sensor_type)
            if strategy:
                result = strategy.evaluate(context, rule)
                if result.triggered:
                    results.append(result)
        return results

    def diagnose_single(self, context: DiagnosisContext, rule: Any) -> DiagnosisResult:
        strategy = self._factory.get_strategy_by_sensor_type(rule.sensor_type)
        if not strategy:
            return DiagnosisResult(triggered=False)
        return strategy.evaluate(context, rule)


DiagnosisStrategyFactory.register(TemperatureDiagnosisStrategy())
DiagnosisStrategyFactory.register(VibrationDiagnosisStrategy())
DiagnosisStrategyFactory.register(PositionDiagnosisStrategy())
DiagnosisStrategyFactory.register(PressureDiagnosisStrategy())
DiagnosisStrategyFactory.register(HumidityDiagnosisStrategy())
DiagnosisStrategyFactory.register(VoltageDiagnosisStrategy())
DiagnosisStrategyFactory.register(CurrentDiagnosisStrategy())
DiagnosisStrategyFactory.register(SpeedDiagnosisStrategy())
DiagnosisStrategyFactory.register(MotorOverloadDiagnosisStrategy())
