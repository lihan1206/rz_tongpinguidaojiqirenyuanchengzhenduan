import pytest
from unittest.mock import MagicMock, patch

from app.core.exceptions import AlreadyExistsException, NotFoundException
from app.diagnosis import DiagnosisContext, DiagnosisEngine, DiagnosisStrategyFactory, TemperatureDiagnosisStrategy
from app.models.robot import Robot
from app.repositories.robot_repository import RobotRepository
from app.schemas.robot import RobotCreate, RobotUpdate
from app.services.robot_service import RobotService


class TestRobotService:
    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def mock_repository(self, mock_db):
        return RobotRepository(mock_db)

    @pytest.fixture
    def robot_service(self, mock_repository):
        return RobotService(mock_repository)

    def test_create_robot_success(self, robot_service, mock_repository):
        mock_repository.get_by_device_id.return_value = None
        mock_robot = Robot(id=1, device_id="R001", status="离线")
        mock_repository.create.return_value = mock_robot
        mock_repository.refresh.return_value = mock_robot

        data = RobotCreate(device_id="R001")
        result = robot_service.create(data)

        assert result.device_id == "R001"
        mock_repository.get_by_device_id.assert_called_once_with("R001")

    def test_create_robot_already_exists(self, robot_service, mock_repository):
        mock_repository.get_by_device_id.return_value = Robot(id=1, device_id="R001")

        data = RobotCreate(device_id="R001")

        with pytest.raises(AlreadyExistsException):
            robot_service.create(data)

    def test_get_robot_not_found(self, robot_service, mock_repository):
        mock_repository.get.return_value = None

        with pytest.raises(NotFoundException):
            robot_service.get(999)

    def test_update_robot_success(self, robot_service, mock_repository):
        mock_robot = Robot(id=1, device_id="R001", status="离线")
        mock_repository.get.return_value = mock_robot
        mock_repository.refresh.return_value = mock_robot

        data = RobotUpdate(status="在线")
        result = robot_service.update(1, data)

        mock_repository.update.assert_called_once()
        mock_repository.create_status_log.assert_called_once()


class TestDiagnosisEngine:
    @pytest.fixture
    def engine(self):
        return DiagnosisEngine()

    def test_diagnose_with_temperature_rule(self, engine):
        mock_rule = MagicMock()
        mock_rule.id = 1
        mock_rule.name = "温度过高"
        mock_rule.sensor_type = "temperature"
        mock_rule.operator = ">"
        mock_rule.threshold = 80
        mock_rule.level = "严重"

        context = DiagnosisContext(
            robot_id=1,
            sensor_type="temperature",
            value=90.0,
        )

        results = engine.diagnose(context, [mock_rule])

        assert len(results) == 1
        assert results[0].triggered is True
        assert results[0].rule_id == 1

    def test_diagnose_no_trigger(self, engine):
        mock_rule = MagicMock()
        mock_rule.id = 1
        mock_rule.name = "温度过高"
        mock_rule.sensor_type = "temperature"
        mock_rule.operator = ">"
        mock_rule.threshold = 80
        mock_rule.level = "严重"

        context = DiagnosisContext(
            robot_id=1,
            sensor_type="temperature",
            value=70.0,
        )

        results = engine.diagnose(context, [mock_rule])

        assert len(results) == 0


class TestDiagnosisStrategy:
    def test_temperature_strategy_evaluate(self):
        strategy = TemperatureDiagnosisStrategy()

        mock_rule = MagicMock()
        mock_rule.id = 1
        mock_rule.name = "温度过高"
        mock_rule.operator = ">"
        mock_rule.threshold = 80
        mock_rule.level = "严重"

        context = DiagnosisContext(
            robot_id=1,
            sensor_type="temperature",
            value=90.0,
        )

        result = strategy.evaluate(context, mock_rule)

        assert result.triggered is True
        assert "温度异常" in result.description

    def test_strategy_factory_registration(self):
        factory = DiagnosisStrategyFactory
        strategy = factory.get_strategy_by_sensor_type("temperature")

        assert strategy is not None
        assert isinstance(strategy, TemperatureDiagnosisStrategy)


class TestExceptions:
    def test_not_found_exception(self):
        exc = NotFoundException("机器人", 1)
        assert exc.status_code == 404
        assert "机器人" in exc.message
        assert "1" in exc.message

    def test_already_exists_exception(self):
        exc = AlreadyExistsException("机器人", "device_id", "R001")
        assert exc.status_code == 400
        assert "已存在" in exc.message

    def test_business_exception(self):
        from app.core.exceptions import BusinessException
        exc = BusinessException("操作失败")
        assert exc.status_code == 400
        assert exc.message == "操作失败"
