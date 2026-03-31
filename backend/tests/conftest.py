from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db():
    """创建模拟的数据库会话"""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_fault_rule():
    """创建模拟的故障规则对象"""
    from app.models.fault import FaultRule
    from datetime import datetime

    rule = FaultRule()
    rule.id = 1
    rule.name = "温度过高"
    rule.sensor_type = "temperature"
    rule.operator = ">"
    rule.threshold = 80
    rule.level = "严重"
    rule.enabled = True
    rule.created_at = datetime.now()
    return rule


@pytest.fixture
def mock_sensor_data():
    """创建模拟的传感器数据对象"""
    from app.models.sensor import SensorData
    from datetime import datetime

    sensor_data = SensorData()
    sensor_data.id = 1
    sensor_data.sensor_id = 1
    sensor_data.value = 85
    sensor_data.timestamp = datetime.now()
    return sensor_data


@pytest.fixture
def mock_fault_log():
    """创建模拟的故障日志对象"""
    from app.models.fault import FaultLog
    from datetime import datetime

    log = FaultLog()
    log.id = 1
    log.robot_id = 1
    log.rule_id = 1
    log.fault_type = "temperature"
    log.description = "温度过高: 当前值85 > 阈值80"
    log.level = "严重"
    log.status = "未处理"
    log.created_at = datetime.now()
    return log