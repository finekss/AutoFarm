from enum import Enum, auto
from typing import Callable, Optional
from collections import defaultdict
from dataclasses import dataclass
import asyncio
from .event_bus import EventBus, Event
from .logger import logger


class State(Enum):
    IDLE = auto()
    LOGIN = auto()
    NAVIGATE_TO_DAILY = auto()
    EXECUTE_DAILY = auto()
    NAVIGATE_TO_DUNGEON = auto()
    EXECUTE_DUNGEON = auto()
    NAVIGATE_TO_GUILD = auto()
    EXECUTE_GUILD = auto()
    ERROR = auto()


@dataclass
class Transition:
    from_state: State
    to_state: State
    condition: Optional[Callable[[], bool]] = None
    action: Optional[Callable[[], None]] = None


class StateMachine:
    def __init__(self, event_bus: EventBus):
        self._state = State.IDLE
        self._transitions: dict[State, list[Transition]] = defaultdict(list)
        self._event_bus = event_bus
        self._running = False
        self._event_bus.subscribe("state_change", self._on_state_change_event)

    def add_transition(self, transition: Transition) -> None:
        self._transitions[transition.from_state].append(transition)

    @property
    def current_state(self) -> State:
        return self._state

    def set_state(self, new_state: State) -> bool:
        if new_state == self._state:
            return False
        old_state = self._state
        self._state = new_state
        self._event_bus.publish(Event("state_change", {"from": old_state.name, "to": new_state.name}))
        logger.info(f"State: {old_state.name} → {new_state.name}")
        return True

    def _on_state_change_event(self, event: Event) -> None:
        pass

    async def tick(self) -> bool:
        for transition in self._transitions.get(self._state, []):
            if transition.condition is None or transition.condition():
                if transition.action:
                    transition.action()
                self.set_state(transition.to_state)
                return True
        return True

    async def run(self, tick_interval: float = 0.1) -> None:
        self._running = True
        while self._running:
            await self.tick()
            await asyncio.sleep(tick_interval)

    def stop(self) -> None:
        self._running = False
        self.set_state(State.IDLE)