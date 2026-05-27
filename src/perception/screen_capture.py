import asyncio
import time
import numpy as np
import mss
from typing import Optional
from ..core.event_bus import EventBus, Event
from ..core.logger import logger
from ..core.config import Config
from .window_utils import get_window_bounds

class ScreenCapture:
    def __init__(self, cfg: Config, event_bus: EventBus):
        self.target_fps = cfg.perception.target_fps
        self.frame_interval = 1.0 / self.target_fps
        self.event_bus = event_bus
        self._running = False
        self._last_frame: Optional[np.ndarray] = None
        self._sct = mss.mss()

        title = cfg.game.window_title
        if title:
            try:
                self.region = get_window_bounds(title)
                logger.info(f"Auto-detected window '{title}': {self.region}")
            except ValueError as e:
                logger.warning(f"Window detection failed: {e}. Using fallback region.")
                self.region = cfg.perception.capture_region
        else:
            self.region = cfg.perception.capture_region
            logger.info(f"Using manual capture region: {self.region}")

    async def run(self) -> None:
        self._running = True
        logger.info(f"Capture started. Region: {self.region}, FPS: {self.target_fps}")
        while self._running:
            start = time.perf_counter()
            frame = self._capture()
            if frame is not None:
                self._last_frame = frame
                self.event_bus.publish(Event("frame_captured", {"frame": frame, "timestamp": time.time()}))
            await asyncio.sleep(max(0.0, self.frame_interval - (time.perf_counter() - start)))

    def _capture(self) -> Optional[np.ndarray]:
        try:
            monitor = {"left": self.region[0], "top": self.region[1],
                       "width": self.region[2], "height": self.region[3]}
            return np.array(self._sct.grab(monitor))[..., :3]
        except Exception as e:
            logger.error(f"Capture failed: {e}")
            return None

    @property
    def latest_frame(self) -> Optional[np.ndarray]:
        return self._last_frame

    def stop(self) -> None:
        self._running = False