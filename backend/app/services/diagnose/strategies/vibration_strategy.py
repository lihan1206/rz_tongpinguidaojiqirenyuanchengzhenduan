from typing import List

from app.models.fault import FaultRule
from app.models.sensor import SensorData
from app.services.diagnose.strategies.base import DiagnoseResult, DiagnoseStrategy


class VibrationDiagnoseStrategy(DiagnoseStrategy):
    """振动诊断策略"""

    @property
    def sensor_type(self) -> str:
        return "vibration"

    def diagnose(
        self,
        sensor_data: SensorData,
        rules: List[FaultRule],
    ) -> List[DiagnoseResult]:
        results: List[DiagnoseResult] = []

        # 获取振动值
        vibration = sensor_data.value

        for rule in rules:
            if rule.sensor_type != self.sensor_type:
                continue

            result = self._evaluate_rule(vibration, rule, sensor_data)
            if result:
                results.append(result)

        if not results:
            results.append(
                DiagnoseResult(
                    is_fault=False,
                    fault_type=self.sensor_type,
                    level="正常",
                    description=f"振动正常: 当前值{vibration}",
                    sensor_data={
                        "sensor_id": sensor_data.sensor_id,
                        "value": vibration,
                        "timestamp": sensor_data.ts.isoformat() if sensor_data.ts else None,
                    },
                )
            )

        return results


# 导出策略实例
vibration_strategy = VibrationDiagnoseStrategy()