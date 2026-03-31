"""诊断服务单元测试"""
from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import BusinessException, ErrorCode
from app.schemas.fault import FaultRuleCreate, FaultRuleUpdate
from app.services.diagnose.diagnose_service import DiagnoseService
from app.services.diagnose.strategy_factory import DiagnoseStrategyFactory


class TestDiagnoseStrategyFactory:
    """诊断策略工厂测试"""

    def test_factory_initialization(self):
        """测试工厂初始化"""
        factory = DiagnoseStrategyFactory()
        supported_types = factory.get_supported_types()
        assert "temperature" in supported_types
        assert "vibration" in supported_types
        assert "position" in supported_types

    def test_get_existing_strategy(self):
        """测试获取已存在的策略"""
        factory = DiagnoseStrategyFactory()
        strategy = factory.get_strategy("temperature")
        assert strategy is not None
        assert strategy.sensor_type == "temperature"

    def test_get_non_existing_strategy(self):
        """测试获取不存在的策略"""
        factory = DiagnoseStrategyFactory()
        with pytest.raises(BusinessException) as exc_info:
            factory.get_strategy("non_existent")
        assert exc_info.value.error_code == ErrorCode.DIAGNOSE_TYPE_NOT_SUPPORTED

    def test_has_strategy(self):
        """测试检查策略是否存在"""
        factory = DiagnoseStrategyFactory()
        assert factory.has_strategy("temperature") is True
        assert factory.has_strategy("non_existent") is False

    def test_register_new_strategy(self):
        """测试注册新策略"""
        from app.services.diagnose.strategies.base import DiagnoseStrategy, DiagnoseResult

        class NewStrategy(DiagnoseStrategy):
            @property
            def sensor_type(self) -> str:
                return "new_type"

            def diagnose(self, sensor_data, rules):
                return [DiagnoseResult(is_fault=False, fault_type="new_type", level="正常", description="测试")]

        factory = DiagnoseStrategyFactory()
        new_strategy = NewStrategy()
        factory.register(new_strategy)

        assert factory.has_strategy("new_type") is True
        assert "new_type" in factory.get_supported_types()


class TestDiagnoseService:
    """诊断服务测试"""

    def setup_method(self):
        """每个测试前的设置"""
        self.service = DiagnoseService()

    def test_create_rule_success(self, mock_db, mock_fault_rule):
        """测试成功创建规则"""
        rule_data = FaultRuleCreate(
            name="温度过高",
            sensor_type="temperature",
            operator=">",
            threshold=80,
            level="严重",
            enabled=True,
        )

        # Mock repository方法
        with patch.object(self.service.fault_rule_repo, "get_by_sensor_type_and_name") as mock_get:
            mock_get.return_value = None  # 规则不存在
            with patch.object(self.service.fault_rule_repo, "create") as mock_create:
                mock_create.return_value = mock_fault_rule

                result = self.service.create_rule(mock_db, rule_data)

                assert result is not None
                assert result.name == "温度过高"
                mock_create.assert_called_once()

    def test_create_rule_already_exists(self, mock_db):
        """测试创建已存在的规则"""
        rule_data = FaultRuleCreate(
            name="温度过高",
            sensor_type="temperature",
            operator=">",
            threshold=80,
            level="严重",
            enabled=True,
        )

        with patch.object(self.service.fault_rule_repo, "get_by_sensor_type_and_name") as mock_get:
            mock_get.return_value = True  # 规则已存在

            with pytest.raises(BusinessException) as exc_info:
                self.service.create_rule(mock_db, rule_data)

            assert exc_info.value.error_code == ErrorCode.DIAGNOSE_RULE_ALREADY_EXISTS

    def test_create_rule_unsupported_type(self, mock_db):
        """测试创建不支持的传感器类型规则"""
        rule_data = FaultRuleCreate(
            name="测试规则",
            sensor_type="unsupported",
            operator=">",
            threshold=80,
            level="严重",
            enabled=True,
        )

        with patch.object(self.service.fault_rule_repo, "get_by_sensor_type_and_name") as mock_get:
            mock_get.return_value = None

            with pytest.raises(BusinessException) as exc_info:
                self.service.create_rule(mock_db, rule_data)

            assert exc_info.value.error_code == ErrorCode.DIAGNOSE_TYPE_NOT_SUPPORTED

    def test_get_rule_success(self, mock_db, mock_fault_rule):
        """测试成功获取规则"""
        with patch.object(self.service.fault_rule_repo, "get") as mock_get:
            mock_get.return_value = mock_fault_rule

            result = self.service.get_rule(mock_db, 1)

            assert result is not None
            assert result.id == 1

    def test_get_rule_not_found(self, mock_db):
        """测试获取不存在的规则"""
        with patch.object(self.service.fault_rule_repo, "get") as mock_get:
            mock_get.return_value = None

            with pytest.raises(BusinessException) as exc_info:
                self.service.get_rule(mock_db, 999)

            assert exc_info.value.error_code == ErrorCode.DIAGNOSE_RULE_NOT_FOUND

    def test_list_rules(self, mock_db, mock_fault_rule):
        """测试获取规则列表"""
        with patch.object(self.service.fault_rule_repo, "list") as mock_list:
            mock_list.return_value = [mock_fault_rule]

            results = self.service.list_rules(mock_db)

            assert len(results) == 1
            mock_list.assert_called_once()

    def test_update_rule_success(self, mock_db, mock_fault_rule):
        """测试成功更新规则"""
        update_data = FaultRuleUpdate(
            name="新名称",
            threshold=90,
        )

        with patch.object(self.service.fault_rule_repo, "get") as mock_get:
            mock_get.return_value = mock_fault_rule
            with patch.object(self.service.fault_rule_repo, "update") as mock_update:
                mock_fault_rule.name = "新名称"
                mock_fault_rule.threshold = 90
                mock_update.return_value = mock_fault_rule

                result = self.service.update_rule(mock_db, 1, update_data)

                assert result.name == "新名称"
                assert result.threshold == 90

    def test_delete_rule_success(self, mock_db, mock_fault_rule):
        """测试成功删除规则"""
        with patch.object(self.service.fault_rule_repo, "get") as mock_get:
            mock_get.return_value = mock_fault_rule
            with patch.object(self.service.fault_rule_repo, "delete") as mock_delete:
                self.service.delete_rule(mock_db, 1)
                mock_delete.assert_called_once_with(mock_db, id=1)

    def test_update_fault_status_invalid_status(self, mock_db):
        """测试更新故障状态-无效状态"""
        with pytest.raises(BusinessException) as exc_info:
            self.service.update_fault_status(mock_db, 1, "无效状态")

        assert exc_info.value.error_code == ErrorCode.FAULT_STATUS_INVALID

    @patch.object(DiagnoseService, '_record_fault_logs')
    def test_execute_diagnose(self, mock_record, mock_db, mock_sensor_data, mock_fault_rule):
        """测试执行诊断"""
        with patch.object(self.service.sensor_data_repo, "get_latest_by_robot_and_type") as mock_get_data:
            mock_get_data.return_value = mock_sensor_data
            with patch.object(self.service.fault_rule_repo, "list_enabled") as mock_get_rules:
                mock_get_rules.return_value = [mock_fault_rule]

                results = self.service.execute_diagnose(mock_db, 1, "temperature")

                assert results is not None
                mock_record.assert_called_once()