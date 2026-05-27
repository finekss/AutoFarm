import pytest
from src.core.config import Config
from src.core.logger import setup_logger
from src.core.event_bus import EventBus, Event
from src.core.state_machine import StateMachine, State, Transition


def test_state_machine_basic_flow(tmp_path):

    cfg = Config(project_root=tmp_path)
    setup_logger(cfg)
    bus = EventBus()
    sm = StateMachine(bus)

    sm.add_transition(Transition(State.IDLE, State.LOGIN, condition=lambda: True))
    sm.add_transition(Transition(State.LOGIN, State.IDLE, condition=lambda: True))

    assert sm.current_state == State.IDLE
    import asyncio
    asyncio.run(sm.tick())
    assert sm.current_state == State.LOGIN
    asyncio.run(sm.tick())
    assert sm.current_state == State.IDLE


def test_conditional_transitions(tmp_path):
    cfg = Config(project_root=tmp_path)
    setup_logger(cfg)
    bus = EventBus()
    sm = StateMachine(bus)

    trigger = False
    sm.add_transition(Transition(State.IDLE, State.LOGIN, condition=lambda: True))
    sm.add_transition(Transition(State.LOGIN, State.NAVIGATE_TO_DAILY, condition=lambda: trigger))

    import asyncio
    asyncio.run(sm.tick())
    assert sm.current_state == State.LOGIN

    asyncio.run(sm.tick())
    assert sm.current_state == State.LOGIN

    trigger = True
    asyncio.run(sm.tick())
    assert sm.current_state == State.NAVIGATE_TO_DAILY