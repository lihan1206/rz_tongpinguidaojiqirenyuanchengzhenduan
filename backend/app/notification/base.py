from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class NotificationChannel(str, Enum):
    SYSTEM = "system"
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    WECHAT = "wechat"
    DINGTALK = "dingtalk"
    FEISHU = "feishu"


@dataclass
class NotificationContext:
    recipient: str
    subject: str
    content: str
    level: str = "一般"
    extra: dict[str, Any] | None = None


@dataclass
class NotificationResult:
    success: bool
    channel: NotificationChannel
    message_id: str | None = None
    error: str | None = None


class NotificationStrategy(ABC):
    @property
    @abstractmethod
    def channel(self) -> NotificationChannel:
        pass

    @abstractmethod
    async def send(self, context: NotificationContext) -> NotificationResult:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    def validate_recipient(self, recipient: str) -> bool:
        return bool(recipient)


class BaseNotificationStrategy(NotificationStrategy):
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    def is_available(self) -> bool:
        return True
