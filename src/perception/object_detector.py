import asyncio
import time
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
from ultralytics import YOLO
from ..core.event_bus import EventBus, Event
from ..core.logger import logger
from ..core.config import Config


class ObjectDetector:
    def __init__(self, cfg: Config, event_bus: EventBus):
        self.cfg = cfg.perception
        self.event_bus = event_bus
        model_path = Path(self.cfg.yolo_model_path)

        if not model_path.exists():
            logger.warning("YOLO model not found. Loading fallback yolo11n.pt")
            self.model = YOLO("yolo11n.pt")
        else:
            self.model = YOLO(str(model_path))

        logger.info(f"Detector ready. Device: {self.cfg.device}, Model: {self.model.model_name}")

    async def process_frame(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        results = await asyncio.to_thread(
            self.model.predict, source=frame, conf=self.cfg.confidence_threshold,
            iou=self.cfg.iou_threshold, device=self.cfg.device, verbose=False, imgsz=640
        )
        detections = []
        for res in results:
            if res.boxes is None: continue
            for box in res.boxes:
                detections.append({
                    "class_name": self.model.names[int(box.cls.item())],
                    "confidence": float(box.conf.item()),
                    "bbox": box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                })
        return detections

    async def run_loop(self) -> None:
        def on_frame(event: Event):
            frame = event.payload.get("frame")
            if frame is not None:
                asyncio.create_task(self._process_and_publish(frame))

        self.event_bus.subscribe("frame_captured", on_frame)

    async def _process_and_publish(self, frame: np.ndarray) -> None:
        try:
            t0 = time.perf_counter()
            detections = await self.process_frame(frame)
            latency = (time.perf_counter() - t0) * 1000
            self.event_bus.publish(Event("objects_detected", {
                "detections": detections, "latency_ms": latency, "timestamp": time.time()
            }))
        except Exception as e:
            logger.error(f"Detection failed: {e}")