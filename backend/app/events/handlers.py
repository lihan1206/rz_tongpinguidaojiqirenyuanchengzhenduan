import logging
from typing import Any

from app.events.base import Event, EventHandler, EventType
from app.notification import NotificationChannel, NotificationContext, NotificationService

logger = logging.getLogger(__name__)


class FaultNotificationHandler(EventHandler):
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service
        self._channels: list[NotificationChannel] = [NotificationChannel.SYSTEM]

    @property
    def event_types(self) -> list[EventType]:
        return [EventType.FAULT_DETECTED, EventType.ALARM_TRIGGERED]

    @property
    def priority(self) -> int:
        return 100

    def configure_channels(self, channels: list[NotificationChannel]) -> None:
        self._channels = channels

    async def handle(self, event: Event) -> None:
        payload = event.payload
        robot_id = payload.get("robot_id")
        description = payload.get("description", "未知故障")
        level = payload.get("level", "一般")

        context = NotificationContext(
            recipient=str(robot_id),
            subject=f"机器人#{robot_id}故障告警",
            content=description,
            level=level,
            extra=payload,
        )

        results = await self.notification_service.broadcast(self._channels, context)
        for result in results:
            if result.success:
                logger.info(f"Notification sent via {result.channel.value}")
            else:
                logger.warning(f"Notification failed: {result.error}")


class AuditLogHandler(EventHandler):
    @property
    def event_types(self) -> list[EventType]:
        return [
            EventType.ROBOT_CREATED,
            EventType.ROBOT_UPDATED,
            EventType.ROBOT_DELETED,
            EventType.FAULT_DETECTED,
            EventType.COMMAND_SENT,
            EventType.USER_LOGIN,
        ]

    @property
    def priority(self) -> int:
        return 50

    async def handle(self, event: Event) -> None:
        logger.info(
            f"Audit: {event.type.value} - {event.payload} at {event.timestamp}"
        )


class MetricsHandler(EventHandler):
    def __init__(self):
        self._counters: dict[str, int] = {}

    @property
    def event_types(self) -> list[EventType]:
        return [EventType.FAULT_DETECTED, EventType.SENSOR_DATA_RECEIVED]

    async def handle(self, event: Event) -> None:
        key = f"{event.type.value}.{event.payload.get('robot_id', 'unknown')}"
        self._counters[key] = self._counters.get(key, 0) + 1

    def get_metrics(self) -> dict[str, int]:
        return self._counters.copy()
