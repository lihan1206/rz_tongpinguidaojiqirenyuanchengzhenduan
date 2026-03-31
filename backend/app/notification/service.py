from typing import Any

from app.core.exceptions import BusinessException
from app.notification.base import (
    NotificationChannel,
    NotificationContext,
    NotificationResult,
    NotificationStrategy,
)
from app.notification.strategies import (
    DingTalkNotificationStrategy,
    EmailNotificationStrategy,
    FeishuNotificationStrategy,
    SmsNotificationStrategy,
    SystemNotificationStrategy,
    WebhookNotificationStrategy,
    WeChatNotificationStrategy,
)


class NotificationStrategyFactory:
    _strategies: dict[NotificationChannel, type[NotificationStrategy]] = {}

    @classmethod
    def register(cls, channel: NotificationChannel, strategy_class: type[NotificationStrategy]) -> None:
        cls._strategies[channel] = strategy_class

    @classmethod
    def create(cls, channel: NotificationChannel, config: dict[str, Any] | None = None) -> NotificationStrategy:
        strategy_class = cls._strategies.get(channel)
        if not strategy_class:
            raise BusinessException(f"不支持的通知渠道: {channel}")
        return strategy_class(config)

    @classmethod
    def list_channels(cls) -> list[str]:
        return [c.value for c in cls._strategies.keys()]


NotificationStrategyFactory.register(NotificationChannel.SYSTEM, SystemNotificationStrategy)
NotificationStrategyFactory.register(NotificationChannel.EMAIL, EmailNotificationStrategy)
NotificationStrategyFactory.register(NotificationChannel.SMS, SmsNotificationStrategy)
NotificationStrategyFactory.register(NotificationChannel.WEBHOOK, WebhookNotificationStrategy)
NotificationStrategyFactory.register(NotificationChannel.WECHAT, WeChatNotificationStrategy)
NotificationStrategyFactory.register(NotificationChannel.DINGTALK, DingTalkNotificationStrategy)
NotificationStrategyFactory.register(NotificationChannel.FEISHU, FeishuNotificationStrategy)


class NotificationService:
    def __init__(self):
        self._factory = NotificationStrategyFactory
        self._configs: dict[NotificationChannel, dict[str, Any]] = {}

    def configure(self, channel: NotificationChannel, config: dict[str, Any]) -> None:
        self._configs[channel] = config

    async def send(
        self,
        channel: NotificationChannel,
        context: NotificationContext,
    ) -> NotificationResult:
        config = self._configs.get(channel)
        strategy = self._factory.create(channel, config)
        return await strategy.send(context)

    async def broadcast(
        self,
        channels: list[NotificationChannel],
        context: NotificationContext,
    ) -> list[NotificationResult]:
        results = []
        for channel in channels:
            try:
                result = await self.send(channel, context)
                results.append(result)
            except Exception as e:
                results.append(
                    NotificationResult(
                        success=False,
                        channel=channel,
                        error=str(e),
                    )
                )
        return results
