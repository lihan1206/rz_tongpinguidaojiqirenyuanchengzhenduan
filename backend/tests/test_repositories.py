import pytest
from unittest.mock import MagicMock

from app.repositories.base import BaseRepository
from app.repositories.robot_repository import RobotRepository
from app.repositories.fault_repository import FaultRuleRepository, FaultLogRepository
from app.models.robot import Robot
from app.models.fault import FaultRule, FaultLog


class TestBaseRepository:
    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def repository(self, mock_db):
        return BaseRepository(mock_db, Robot)

    def test_get(self, repository, mock_db):
        mock_robot = Robot(id=1, device_id="R001")
        mock_db.get.return_value = mock_robot

        result = repository.get(1)

        mock_db.get.assert_called_once_with(Robot, 1)
        assert result == mock_robot

    def test_get_not_found(self, repository, mock_db):
        mock_db.get.return_value = None

        result = repository.get(999)

        assert result is None

    def test_create(self, repository, mock_db):
        mock_db.flush = MagicMock()

        result = repository.create({"device_id": "R001", "status": "离线"})

        mock_db.add.assert_called_once()
        mock_db.flush.assert_called_once()


class TestRobotRepository:
    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def repository(self, mock_db):
        return RobotRepository(mock_db)

    def test_get_by_device_id(self, repository, mock_db):
        mock_robot = Robot(id=1, device_id="R001")
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = mock_robot
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        result = repository.get_by_device_id("R001")

        mock_db.query.assert_called_once()
        assert result == mock_robot


class TestFaultRuleRepository:
    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def repository(self, mock_db):
        return FaultRuleRepository(mock_db)

    def test_list_enabled_by_sensor_type(self, repository, mock_db):
        mock_rules = [MagicMock(id=1), MagicMock(id=2)]
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.all.return_value = mock_rules
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query

        result = repository.list_enabled_by_sensor_type("temperature")

        mock_db.query.assert_called_once()
        assert len(result) == 2
