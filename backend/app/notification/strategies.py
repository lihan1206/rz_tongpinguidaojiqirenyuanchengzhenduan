import re
from typing import Any

from app.notification.base import (
    BaseNotificationStrategy,
    NotificationChannel,
    NotificationContext,
    NotificationResult,
)


class SystemNotificationStrategy(BaseNotificationStrategy):
    @property
    def channel(self) -> NotificationChannel:
        return NotificationChannel.SYSTEM

    async def send(self, context: NotificationContext) -> NotificationResult:
        return NotificationResult(
            success=True,
            channel=self.channel,
            message_id=f"sys_{id(context)}",
        )


class EmailNotificationStrategy(BaseNotificationStrategy):
    @property
    def channel(self) -> NotificationChannel:
        return NotificationChannel.EMAIL

    def validate_recipient(self, recipient: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, recipient))

    async def send(self, context: NotificationContext) -> NotificationResult:
        if not self.validate_recipient(context.recipient):
            return NotificationResult(
                success=False,
                channel=self.channel,
                error="无效的邮箱地址",
            )
        return NotificationResult(
            success=True,
            channel=self.channel,
            message_id=f"email_{id(context)}",
        )


class SmsNotificationStrategy(BaseNotificationStrategy):
    @property
    def channel(self) -> NotificationChannel:
        return NotificationChannel.SMS

    def validate_recipient(self, recipient: str) -> bool:
        pattern = r"^1[3-9]\d{9}$"
        return bool(re.match(pattern, recipient))

    async def send(self, context: NotificationContext) -> NotificationResult:
        if not self.validate_recipient(context.recipient):
            return NotificationResult(
                success=False,
                channel=self.channel,
                error="无效的手机号码",
            )
        return NotificationResult(
            success=True,
            channel=self.channel,
            message_id=f"sms_{id(context)}",
        )


class WebhookNotificationStrategy(BaseNotificationStrategy):
    @property
    def channel(self) -> NotificationChannel:
        return NotificationChannel.WEBHOOK

    async def send(self, context: NotificationContext) -> NotificationResult:
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            return NotificationResult(
                success=False,
                channel=self.channel,
                error="未配置Webhook URL",
            )
        return NotificationResult(
            success=True,
            channel=self.channel,
            message_id=f"webhook_{id(context)}",
        )


class WeChatNotificationStrategy(BaseNotificationStrategy):
    @property
    def channel(self) -> NotificationChannel:
        return NotificationChannel.WECHAT

    async def send(self, context: NotificationContext) -> NotificationResult:
        corp_id = self.config.get("corp_id")
        agent_id = self.config.get("agent_id")
        if not corp_id or not agent_id:
            return NotificationResult(
                success=False,
                channel=self.channel,
                error="未配置企业微信参数",
            )
        return NotificationResult(
            success=True,
            channel=self.channel,
            message_id=f"wechat_{id(context)}",
        )


class DingTalkNotificationStrategy(BaseNotificationStrategy):
    @property
    def channel(self) -> NotificationChannel:
        return NotificationChannel.DINGTALK

    async def send(self, context: NotificationContext) -> NotificationResult:
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            return NotificationResult(
                success=False,
                channel=self.channel,
                error="未配置钉钉Webhook",
            )
        return NotificationResult(
            success=True,
            channel=self.channel,
            message_id=f"dingtalk_{id(context)}",
        )


class FeishuNotificationStrategy(BaseNotificationStrategy):
    @property
    def channel(self) -> NotificationChannel:
        return NotificationChannel.FEISHU

    async def send(self, context: NotificationContext) -> NotificationResult:
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            return NotificationResult(
                success=False,
                channel=self.channel,
                error="未配置飞书Webhook",
            )
        return NotificationResult(
            success=True,
            channel=self.channel,
            message_id=f"feishu_{id(context)}",
        )
