from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.models.fault import FaultRule
from app.models.sensor import SensorData


class DiagnoseResult(BaseModel):
    """诊断结果模型"""

    is_fault: bool
    fault_type: str
    level: str
    description: str
    rule_id: Optional[int] = None
    sensor_data: Optional[Dict[str, Any]] = None


class DiagnoseStrategy(ABC):
    """诊断策略接口"""

    @property
    @abstractmethod
    def sensor_type(self) -> str:
        """支持的传感器类型"""
        pass

    @abstractmethod
    def diagnose(
        self,
        sensor_data: SensorData,
        rules: List[FaultRule],
    ) -> List[DiagnoseResult]:
        """
        执行诊断

        :param sensor_data: 传感器数据
        :param rules: 诊断规则列表
        :return: 诊断结果列表
        """
        pass

    def _evaluate_rule(
        self,
        value: int,
        rule: FaultRule,
        sensor_data: SensorData,
    ) -> Optional[DiagnoseResult]:
        """
        评估单个规则是否触发

        :param value: 要检查的值
        :param rule: 诊断规则
        :param sensor_data: 传感器数据
        :return: 诊断结果（如果触发）
        """
        is_triggered = False

        match rule.operator:
            case ">":
                is_triggered = value > rule.threshold
            case ">=":
                is_triggered = value >= rule.threshold
            case "<":
                is_triggered = value < rule.threshold
            case "<=":
                is_triggered = value <= rule.threshold
            case "==":
                is_triggered = value == rule.threshold
            case "!=":
                is_triggered = value != rule.threshold

        if is_triggered:
            return DiagnoseResult(
                is_fault=True,
                fault_type=rule.sensor_type,
                level=rule.level,
                description=f"{rule.name}: 当前值{value} {rule.operator} 阈值{rule.threshold}",
                rule_id=rule.id,
                sensor_data={
                    "sensor_id": sensor_data.sensor_id,
                    "value": value,
                    "timestamp": sensor_data.ts.isoformat() if sensor_data.ts else None,
                },
            )

        return None