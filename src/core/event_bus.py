from collections import defaultdict
from typing import Callable, Any, Dict, List
from dataclasses import dataclass, field
import asyncio

@dataclass
class Event:
    type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: asyncio.get_event_loop().time())


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        self._subscribers[event_type].append(handler)

    def publish(self, event: Event) -> None:
        for handler in self._subscribers.get(event.type, []):
            try:
                handler(event)
            except Exception as e:
                from core.logger import logger
                logger.error(f"Event handler failed: {e}")

    def publish_async(self, event: Event) -> None:
        asyncio.create_task(self._publish_async(event))

    async def _publish_async(self, event: Event) -> None:
        for handler in self._subscribers.get(event.type, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                from core.logger import logger
                logger.error(f"Async event handler failed: {e}")