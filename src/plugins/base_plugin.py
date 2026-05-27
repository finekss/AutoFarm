from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional
from src.core.state_machine import State, StateMachine
from src.core.event_bus import EventBus


@dataclass
class PluginContext:
    state_machine: StateMachine
    event_bus: EventBus
    config: Dict[str, Any]


class TaskPlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    async def can_run(self, ctx: PluginContext) -> bool: ...

    @abstractmethod
    async def execute(self, ctx: PluginContext) -> Dict[str, Any]: ...

    def register_transitions(self, sm: StateMachine) -> None:
        """probably will need to register transitions"""
        pass