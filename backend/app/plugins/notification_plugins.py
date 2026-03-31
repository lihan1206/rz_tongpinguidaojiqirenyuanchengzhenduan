from typing import Any

from app.notification.base import BaseNotificationStrategy, NotificationChannel
from app.plugins.base import NotificationPluginInterface


class SlackNotificationPlugin(NotificationPluginInterface):
    @property
    def name(self) -> str:
        return "slack_notification"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def channel(self) -> str:
        return "slack"

    def initialize(self, config: dict[str, Any] | None = None) -> None:
        self.webhook_url = config.get("webhook_url") if config else None

    def shutdown(self) -> None:
        pass

    def get_strategy_class(self) -> type:
        plugin = self

        class SlackNotificationStrategy(BaseNotificationStrategy):
            @property
            def channel(self) -> NotificationChannel:
                return NotificationChannel.WEBHOOK

            async def send(self, context):
                return type("NotificationResult", (), {
                    "success": bool(plugin.webhook_url),
                    "channel": self.channel,
                    "message_id": f"slack_{id(context)}",
                    "error": None if plugin.webhook_url else "未配置Slack Webhook"
                })()

        return SlackNotificationStrategy
