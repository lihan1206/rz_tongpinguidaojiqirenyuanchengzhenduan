from typing import Dict, List

from app.core.exceptions import ErrorCode, BusinessException
from app.services.diagnose.strategies import (
    DiagnoseStrategy,
    position_strategy,
    temperature_strategy,
    vibration_strategy,
)


class DiagnoseStrategyFactory:
    """诊断策略工厂类"""

    def __init__(self):
        self._strategies: Dict[str, DiagnoseStrategy] = {}
        # 注册默认策略
        self.register(temperature_strategy)
        self.register(vibration_strategy)
        self.register(position_strategy)

    def register(self, strategy: DiagnoseStrategy) -> None:
        """
        注册诊断策略

        :param strategy: 诊断策略实例
        """
        self._strategies[strategy.sensor_type] = strategy

    def unregister(self, sensor_type: str) -> None:
        """
        注销诊断策略

        :param sensor_type: 传感器类型
        """
        self._strategies.pop(sensor_type, None)

    def get_strategy(self, sensor_type: str) -> DiagnoseStrategy:
        """
        获取指定传感器类型的诊断策略

        :param sensor_type: 传感器类型
        :return: 诊断策略实例
        :raises BusinessException: 如果不支持该传感器类型
        """
        strategy = self._strategies.get(sensor_type.lower())
        if not strategy:
            raise BusinessException(
                error_code=ErrorCode.DIAGNOSE_TYPE_NOT_SUPPORTED,
                message=f"不支持的诊断类型: {sensor_type}",
                detail={"supported_types": self.get_supported_types()},
            )
        return strategy

    def get_supported_types(self) -> List[str]:
        """
        获取所有支持的传感器类型

        :return: 支持的传感器类型列表
        """
        return list(self._strategies.keys())

    def has_strategy(self, sensor_type: str) -> bool:
        """
        检查是否支持指定的传感器类型

        :param sensor_type: 传感器类型
        :return: 是否支持
        """
        return sensor_type.lower() in self._strategies


# 创建全局策略工厂实例
strategy_factory = DiagnoseStrategyFactory()