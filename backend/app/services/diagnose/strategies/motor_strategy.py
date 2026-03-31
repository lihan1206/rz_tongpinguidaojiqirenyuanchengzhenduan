from typing import List

from app.models.fault import FaultRule
from app.models.sensor import SensorData
from app.services.diagnose.strategies.base import DiagnoseResult, DiagnoseStrategy


class MotorOverloadDiagnoseStrategy(DiagnoseStrategy):
    """电机过载诊断策略"""

    @property
    def sensor_type(self) -> str:
        return "motor"

    def diagnose(
        self,
        sensor_data: SensorData,
        rules: List[FaultRule],
    ) -> List[DiagnoseResult]:
        results: List[DiagnoseResult] = []

        # 获取电机负载值
        motor_load = sensor_data.value

        for rule in rules:
            if rule.sensor_type != self.sensor_type:
                continue

            result = self._evaluate_rule(motor_load, rule, sensor_data)
            if result:
                results.append(result)

        if not results:
            results.append(
                DiagnoseResult(
                    is_fault=False,
                    fault_type=self.sensor_type,
                    level="正常",
                    description=f"电机负载正常: 当前值{motor_load}",
                    sensor_data={
                        "sensor_id": sensor_data.sensor_id,
                        "value": motor_load,
                        "timestamp": sensor_data.ts.isoformat() if sensor_data.ts else None,
                    },
                )
            )

        return results


# 导出策略实例
motor_strategy = MotorOverloadDiagnoseStrategy()
