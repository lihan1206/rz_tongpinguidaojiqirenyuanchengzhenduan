import asyncio
import logging
from collections import defaultdict
from typing import Any

from app.events.base import Event, EventHandler, EventHandlerCallable, EventType

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self):
        self._handlers: dict[EventType, list[EventHandler | EventHandlerCallable]] = defaultdict(list)
        self._middleware: list[Callable] = []

    def subscribe(self, handler: EventHandler | EventHandlerCallable) -> None:
        if isinstance(handler, EventHandler):
            for event_type in handler.event_types:
                self._handlers[event_type].append(handler)
        else:
            raise ValueError("Handler must be an EventHandler instance")

    def subscribe_callable(
        self,
        event_type: EventType,
        handler: EventHandlerCallable,
    ) -> None:
        self._handlers[event_type].append(handler)

    def unsubscribe(self, handler: EventHandler) -> None:
        for event_type in handler.event_types:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)

    def add_middleware(self, middleware: Callable) -> None:
        self._middleware.append(middleware)

    async def publish(self, event: Event) -> None:
        logger.info(f"Publishing event: {event.type.value}")

        for middleware in self._middleware:
            try:
                await middleware(event)
            except Exception as e:
                logger.exception(f"Middleware error: {e}")

        handlers = self._handlers.get(event.type, [])
        sorted_handlers = sorted(
            [h for h in handlers if isinstance(h, EventHandler)],
            key=lambda h: h.priority,
            reverse=True,
        )

        tasks = []
        for handler in sorted_handlers:
            tasks.append(self._execute_handler(handler, event))

        for handler in [h for h in handlers if not isinstance(h, EventHandler)]:
            tasks.append(self._execute_callable(handler, event))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute_handler(self, handler: EventHandler, event: Event) -> None:
        try:
            await handler.handle(event)
        except Exception as e:
            logger.exception(f"Handler {handler.__class__.__name__} error: {e}")

    async def _execute_callable(self, handler: EventHandlerCallable, event: Event) -> None:
        try:
            result = handler(event)
            if asyncio.iscoroutine(result):
                await result
        except Exception as e:
            logger.exception(f"Callable handler error: {e}")

    def publish_sync(self, event: Event) -> None:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(self.publish(event))
        else:
            loop.run_until_complete(self.publish(event))


event_bus = EventBus()


from typing import Callable
