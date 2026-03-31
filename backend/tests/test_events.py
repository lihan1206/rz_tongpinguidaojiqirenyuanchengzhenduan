import pytest
from datetime import datetime

from app.events import (
    Event,
    EventBus,
    EventType,
    EventHandler,
    MetricsHandler,
)


class TestEvent:
    def test_event_creation(self):
        event = Event(
            type=EventType.FAULT_DETECTED,
            payload={"robot_id": 1, "description": "Test fault"},
        )
        assert event.type == EventType.FAULT_DETECTED
        assert event.payload["robot_id"] == 1
        assert isinstance(event.timestamp, datetime)


class TestEventBus:
    @pytest.fixture
    def event_bus(self):
        return EventBus()

    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self, event_bus):
        received_events = []

        class TestHandler(EventHandler):
            @property
            def event_types(self):
                return [EventType.FAULT_DETECTED]

            async def handle(self, event):
                received_events.append(event)

        handler = TestHandler()
        event_bus.subscribe(handler)

        event = Event(type=EventType.FAULT_DETECTED, payload={"test": "data"})
        await event_bus.publish(event)

        assert len(received_events) == 1
        assert received_events[0].payload["test"] == "data"

    @pytest.mark.asyncio
    async def test_callable_handler(self, event_bus):
        received = []

        def handler(event):
            received.append(event)

        event_bus.subscribe_callable(EventType.ROBOT_CREATED, handler)

        event = Event(type=EventType.ROBOT_CREATED, payload={"robot_id": 1})
        await event_bus.publish(event)

        assert len(received) == 1


class TestMetricsHandler:
    @pytest.fixture
    def handler(self):
        return MetricsHandler()

    @pytest.mark.asyncio
    async def test_metrics_collection(self, handler):
        event1 = Event(
            type=EventType.FAULT_DETECTED,
            payload={"robot_id": 1},
        )
        event2 = Event(
            type=EventType.FAULT_DETECTED,
            payload={"robot_id": 1},
        )

        await handler.handle(event1)
        await handler.handle(event2)

        metrics = handler.get_metrics()
        assert metrics["fault.detected.1"] == 2
