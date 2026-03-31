"""策略模式单元测试"""
from typing import List

import pytest

from app.models.fault import FaultRule
from app.services.diagnose.strategies import (
    DiagnoseResult,
    position_strategy,
    temperature_strategy,
    vibration_strategy,
)
from app.services.diagnose.strategies.base import DiagnoseStrategy


class TestTemperatureStrategy:
    """温度诊断策略测试"""

    def test_sensor_type(self):
        """测试传感器类型属性"""
        assert temperature_strategy.sensor_type == "temperature"

    def test_diagnose_normal(self, mock_sensor_data, mock_fault_rule):
        """测试正常情况诊断"""
        mock_sensor_data.value = 70  # 低于阈值80
        rules = [mock_fault_rule]

        results = temperature_strategy.diagnose(mock_sensor_data, rules)

        assert len(results) == 1
        assert results[0].is_fault is False
        assert results[0].level == "正常"

    def test_diagnose_fault(self, mock_sensor_data, mock_fault_rule):
        """测试故障情况诊断"""
        mock_sensor_data.value = 85  # 高于阈值80
        rules = [mock_fault_rule]

        results = temperature_strategy.diagnose(mock_sensor_data, rules)

        assert len(results) == 1
        assert results[0].is_fault is True
        assert results[0].fault_type == "temperature"
        assert "85" in results[0].description
        assert "80" in results[0].description

    def test_diagnose_no_rules(self, mock_sensor_data):
        """测试无规则时的诊断"""
        mock_sensor_data.value = 75
        results = temperature_strategy.diagnose(mock_sensor_data, [])

        assert len(results) == 1
        assert results[0].is_fault is False

    @pytest.mark.parametrize(
        "value,operator,threshold,expected",
        [
            (85, ">", 80, True),
            (80, ">", 80, False),
            (80, ">=", 80, True),
            (75, "<", 80, True),
            (80, "<=", 80, True),
            (80, "==", 80, True),
            (85, "!=", 80, True),
        ],
    )
    def test_evaluate_rule_different_operators(
        self,
        mock_sensor_data,
        mock_fault_rule,
        value,
        operator,
        threshold,
        expected,
    ):
        """测试不同运算符的规则评估"""
        mock_sensor_data.value = value
        mock_fault_rule.operator = operator
        mock_fault_rule.threshold = threshold

        result = temperature_strategy._evaluate_rule(
            value,
            mock_fault_rule,
            mock_sensor_data,
        )

        assert (result is not None) == expected


class TestVibrationStrategy:
    """振动诊断策略测试"""

    def test_sensor_type(self):
        """测试传感器类型属性"""
        assert vibration_strategy.sensor_type == "vibration"

    def test_diagnose_fault(self, mock_sensor_data, mock_fault_rule):
        """测试故障情况诊断"""
        mock_fault_rule.sensor_type = "vibration"
        mock_fault_rule.name = "振动异常"
        mock_fault_rule.threshold = 100

        mock_sensor_data.value = 150
        rules = [mock_fault_rule]

        results = vibration_strategy.diagnose(mock_sensor_data, rules)

        assert len(results) == 1
        assert results[0].is_fault is True
        assert results[0].fault_type == "vibration"


class TestPositionStrategy:
    """位置诊断策略测试"""

    def test_sensor_type(self):
        """测试传感器类型属性"""
        assert position_strategy.sensor_type == "position"

    def test_diagnose_normal(self, mock_sensor_data, mock_fault_rule):
        """测试正常情况诊断"""
        mock_fault_rule.sensor_type = "position"
        mock_fault_rule.name = "位置偏移"
        mock_fault_rule.operator = "!="
        mock_fault_rule.threshold = 0

        mock_sensor_data.value = 0
        rules = [mock_fault_rule]

        results = position_strategy.diagnose(mock_sensor_data, rules)

        assert len(results) == 1
        assert results[0].is_fault is False