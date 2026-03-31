import pytest
from unittest.mock import MagicMock

from app.specifications import (
    FieldSpecification,
    RobotSpecifications,
    FaultLogSpecifications,
    SpecificationRepository,
)
from app.models.robot import Robot
from app.models.fault import FaultLog


class TestSpecifications:
    def test_field_specification_equals(self):
        spec = FieldSpecification(Robot.status, "==", "在线")
        robot = Robot(id=1, device_id="R001", status="在线")
        assert spec.is_satisfied_by(robot) is True

        robot_offline = Robot(id=2, device_id="R002", status="离线")
        assert spec.is_satisfied_by(robot_offline) is False

    def test_field_specification_in(self):
        spec = FieldSpecification(Robot.status, "in", ["在线", "运行中"])
        robot = Robot(id=1, device_id="R001", status="在线")
        assert spec.is_satisfied_by(robot) is True

    def test_and_specification(self):
        spec1 = FieldSpecification(Robot.status, "==", "在线")
        spec2 = FieldSpecification(Robot.device_id, "==", "R001")
        combined = spec1.and_(spec2)

        robot = Robot(id=1, device_id="R001", status="在线")
        assert combined.is_satisfied_by(robot) is True

        robot2 = Robot(id=2, device_id="R002", status="在线")
        assert combined.is_satisfied_by(robot2) is False

    def test_or_specification(self):
        spec1 = FieldSpecification(Robot.status, "==", "在线")
        spec2 = FieldSpecification(Robot.status, "==", "运行中")
        combined = spec1.or_(spec2)

        robot1 = Robot(id=1, device_id="R001", status="在线")
        robot2 = Robot(id=2, device_id="R002", status="运行中")
        robot3 = Robot(id=3, device_id="R003", status="离线")

        assert combined.is_satisfied_by(robot1) is True
        assert combined.is_satisfied_by(robot2) is True
        assert combined.is_satisfied_by(robot3) is False

    def test_not_specification(self):
        spec = FieldSpecification(Robot.status, "==", "在线")
        not_spec = spec.not_()

        robot = Robot(id=1, device_id="R001", status="离线")
        assert not_spec.is_satisfied_by(robot) is True


class TestRobotSpecifications:
    def test_is_online(self):
        spec = RobotSpecifications.is_online()
        robot = Robot(id=1, device_id="R001", status="在线")
        assert spec.is_satisfied_by(robot) is True

    def test_status_in(self):
        spec = RobotSpecifications.status_in(["在线", "运行中"])
        robot = Robot(id=1, device_id="R001", status="运行中")
        assert spec.is_satisfied_by(robot) is True


class TestFaultLogSpecifications:
    def test_is_unresolved(self):
        spec = FaultLogSpecifications.is_unresolved()
        log = MagicMock(spec=spec)
        log.status = "未处理"
        assert spec.is_satisfied_by(log) is True

    def test_is_critical(self):
        spec = FaultLogSpecifications.is_critical()
        log = MagicMock()
        log.level = "严重"
        assert spec.is_satisfied_by(log) is True
