from app.diagnosis.base import BaseDiagnosisStrategy, DiagnosisType
from app.plugins.base import DiagnosisPluginInterface


class CustomDiagnosisPlugin(DiagnosisPluginInterface):
    @property
    def name(self) -> str:
        return "custom_diagnosis"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def sensor_types(self) -> list[str]:
        return ["custom"]

    def initialize(self, config: dict | None = None) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def get_strategy_class(self) -> type:
        class CustomDiagnosisStrategy(BaseDiagnosisStrategy):
            @property
            def diagnosis_type(self) -> DiagnosisType:
                return DiagnosisType.CUSTOM

            def generate_description(self, context, rule) -> str:
                return f"自定义诊断: {context.value}"

        return CustomDiagnosisStrategy


class ExampleTemperaturePlugin(DiagnosisPluginInterface):
    @property
    def name(self) -> str:
        return "temperature_advanced"

    @property
    def version(self) -> str:
        return "2.0.0"

    @property
    def sensor_types(self) -> list[str]:
        return ["temperature", "temp", "温度"]

    def initialize(self, config: dict | None = None) -> None:
        self.config = config or {}

    def shutdown(self) -> None:
        pass

    def get_strategy_class(self) -> type:
        from app.diagnosis.strategies import TemperatureDiagnosisStrategy
        return TemperatureDiagnosisStrategy
