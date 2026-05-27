import asyncio
import sys
from pathlib import Path
from src.core.config import Config
from src.core.logger import setup_logger, logger
from src.core.event_bus import EventBus
from src.core.state_machine import StateMachine, State, Transition

async def main():
    cfg = Config.load(Path("../configs/base.yaml"))
    setup_logger(cfg)
    logger.info("AutoFarm Core starting...")

    bus = EventBus()
    sm = StateMachine(bus)

    daily_found = False
    def mark_daily_found():
        nonlocal daily_found
        daily_found = True

    sm.add_transition(Transition(State.IDLE, State.LOGIN, condition=lambda: True))
    sm.add_transition(Transition(State.LOGIN, State.NAVIGATE_TO_DAILY, condition=lambda: True))
    sm.add_transition(Transition(State.NAVIGATE_TO_DAILY, State.IDLE,
                                condition=lambda: daily_found, action=mark_daily_found))

    try:
        await sm.run(tick_interval=0.5)
    except KeyboardInterrupt:
        logger.info("Interrupt received.")
    finally:
        sm.stop()
        logger.info("Core shutdown complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)