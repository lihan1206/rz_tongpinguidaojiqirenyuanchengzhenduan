from typing import List

from app.models.fault import FaultRule
from app.models.sensor import SensorData
from app.services.diagnose.strategies.base import DiagnoseResult, DiagnoseStrategy


class TemperatureDiagnoseStrategy(DiagnoseStrategy):
    """温度诊断策略"""

    @property
    def sensor_type(self) -> str:
        return "temperature"

    def diagnose(
        self,
        sensor_data: SensorData,
        rules: List[FaultRule],
    ) -> List[DiagnoseResult]:
        results: List[DiagnoseResult] = []

        # 获取温度值
        temperature = sensor_data.value

        # 按优先级检查规则（按严重程度从高到低）
        for rule in rules:
            if rule.sensor_type != self.sensor_type:
                continue

            result = self._evaluate_rule(temperature, rule, sensor_data)
            if result:
                results.append(result)

        # 如果没有故障，返回正常结果
        if not results:
            results.append(
                DiagnoseResult(
                    is_fault=False,
                    fault_type=self.sensor_type,
                    level="正常",
                    description=f"温度正常: 当前值{temperature}",
                    sensor_data={
                        "sensor_id": sensor_data.sensor_id,
                        "value": temperature,
                        "timestamp": sensor_data.timestamp.isoformat() if sensor_data.timestamp else None,
                    },
                )
            )

        return results


# 导出策略实例
temperature_strategy = TemperatureDiagnoseStrategy()