from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable


class EventType(str, Enum):
    ROBOT_CREATED = "robot.created"
    ROBOT_UPDATED = "robot.updated"
    ROBOT_DELETED = "robot.deleted"
    ROBOT_STATUS_CHANGED = "robot.status_changed"

    SENSOR_DATA_RECEIVED = "sensor.data_received"

    FAULT_DETECTED = "fault.detected"
    FAULT_RESOLVED = "fault.resolved"
    FAULT_ESCALATED = "fault.escalated"

    ALARM_TRIGGERED = "alarm.triggered"
    ALARM_ACKNOWLEDGED = "alarm.acknowledged"

    COMMAND_SENT = "command.sent"
    COMMAND_EXECUTED = "command.executed"

    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"


@dataclass
class Event:
    type: EventType
    payload: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    source: str | None = None
    correlation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class EventHandler(ABC):
    @property
    @abstractmethod
    def event_types(self) -> list[EventType]:
        pass

    @abstractmethod
    async def handle(self, event: Event) -> None:
        pass

    @property
    def priority(self) -> int:
        return 0


EventHandlerCallable = Callable[[Event], None]
