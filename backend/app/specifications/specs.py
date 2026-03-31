from typing import Any

from app.models.fault import FaultLog, FaultRule
from app.models.robot import Robot
from app.models.sensor import SensorData
from app.specifications.base import FieldSpecification, Specification


class RobotSpecifications:
    @staticmethod
    def has_device_id(device_id: str) -> Specification[Robot]:
        return FieldSpecification(Robot.device_id, "==", device_id)

    @staticmethod
    def has_status(status: str) -> Specification[Robot]:
        return FieldSpecification(Robot.status, "==", status)

    @staticmethod
    def status_in(statuses: list[str]) -> Specification[Robot]:
        return FieldSpecification(Robot.status, "in", statuses)

    @staticmethod
    def is_online() -> Specification[Robot]:
        return FieldSpecification(Robot.status, "==", "在线")

    @staticmethod
    def is_offline() -> Specification[Robot]:
        return FieldSpecification(Robot.status, "==", "离线")

    @staticmethod
    def has_location_like(location: str) -> Specification[Robot]:
        return FieldSpecification(Robot.location, "like", location)


class FaultLogSpecifications:
    @staticmethod
    def has_robot_id(robot_id: int) -> Specification[FaultLog]:
        return FieldSpecification(FaultLog.robot_id, "==", robot_id)

    @staticmethod
    def has_level(level: str) -> Specification[FaultLog]:
        return FieldSpecification(FaultLog.level, "==", level)

    @staticmethod
    def level_in(levels: list[str]) -> Specification[FaultLog]:
        return FieldSpecification(FaultLog.level, "in", levels)

    @staticmethod
    def has_status(status: str) -> Specification[FaultLog]:
        return FieldSpecification(FaultLog.status, "==", status)

    @staticmethod
    def is_unresolved() -> Specification[FaultLog]:
        return FieldSpecification(FaultLog.status, "==", "未处理")

    @staticmethod
    def is_critical() -> Specification[FaultLog]:
        return FieldSpecification(FaultLog.level, "==", "严重")


class SensorDataSpecifications:
    @staticmethod
    def has_robot_id(robot_id: int) -> Specification[SensorData]:
        return FieldSpecification(SensorData.robot_id, "==", robot_id)

    @staticmethod
    def has_sensor_type(sensor_type: str) -> Specification[SensorData]:
        return FieldSpecification(SensorData.sensor_type, "==", sensor_type)

    @staticmethod
    def sensor_type_in(types: list[str]) -> Specification[SensorData]:
        return FieldSpecification(SensorData.sensor_type, "in", types)


class FaultRuleSpecifications:
    @staticmethod
    def is_enabled() -> Specification[FaultRule]:
        return FieldSpecification(FaultRule.enabled, "==", True)

    @staticmethod
    def has_sensor_type(sensor_type: str) -> Specification[FaultRule]:
        return FieldSpecification(FaultRule.sensor_type, "==", sensor_type)

    @staticmethod
    def has_level(level: str) -> Specification[FaultRule]:
        return FieldSpecification(FaultRule.level, "==", level)

    @staticmethod
    def active_for_sensor(sensor_type: str) -> Specification[FaultRule]:
        return FaultRuleSpecifications.is_enabled().and_(
            FaultRuleSpecifications.has_sensor_type(sensor_type)
        )
