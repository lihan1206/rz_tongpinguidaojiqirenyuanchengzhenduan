import pytest
from unittest.mock import MagicMock, AsyncMock

from app.notification import (
    NotificationChannel,
    NotificationContext,
    NotificationService,
    NotificationStrategyFactory,
    EmailNotificationStrategy,
    SmsNotificationStrategy,
)


class TestNotificationStrategies:
    def test_email_validation(self):
        strategy = EmailNotificationStrategy()
        assert strategy.validate_recipient("test@example.com") is True
        assert strategy.validate_recipient("invalid-email") is False

    def test_sms_validation(self):
        strategy = SmsNotificationStrategy()
        assert strategy.validate_recipient("13800138000") is True
        assert strategy.validate_recipient("12345") is False

    @pytest.mark.asyncio
    async def test_email_send(self):
        strategy = EmailNotificationStrategy()
        context = NotificationContext(
            recipient="test@example.com",
            subject="Test",
            content="Test content",
        )
        result = await strategy.send(context)
        assert result.success is True
        assert result.channel == NotificationChannel.EMAIL

    @pytest.mark.asyncio
    async def test_email_send_invalid(self):
        strategy = EmailNotificationStrategy()
        context = NotificationContext(
            recipient="invalid",
            subject="Test",
            content="Test content",
        )
        result = await strategy.send(context)
        assert result.success is False


class TestNotificationFactory:
    def test_create_strategy(self):
        strategy = NotificationStrategyFactory.create(NotificationChannel.EMAIL)
        assert isinstance(strategy, EmailNotificationStrategy)

    def test_list_channels(self):
        channels = NotificationStrategyFactory.list_channels()
        assert "email" in channels
        assert "sms" in channels


class TestNotificationService:
    @pytest.fixture
    def service(self):
        return NotificationService()

    @pytest.mark.asyncio
    async def test_send(self, service):
        context = NotificationContext(
            recipient="test@example.com",
            subject="Test",
            content="Test content",
        )
        result = await service.send(NotificationChannel.SYSTEM, context)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_broadcast(self, service):
        context = NotificationContext(
            recipient="test@example.com",
            subject="Test",
            content="Test content",
        )
        results = await service.broadcast(
            [NotificationChannel.SYSTEM, NotificationChannel.EMAIL],
            context,
        )
        assert len(results) == 2
