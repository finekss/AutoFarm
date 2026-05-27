import time
import sys
import cv2
import numpy as np
import mss
import ctypes
import win32gui
from pathlib import Path

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

def get_window_bounds(title: str) -> tuple[int, int, int, int]:
    hwnd = win32gui.FindWindow(None, title)
    if not hwnd:
        matches = []
        def enum_callback(h, _):
            if win32gui.IsWindowVisible(h) and title.lower() in win32gui.GetWindowText(h).lower():
                matches.append(h)
            return True
        win32gui.EnumWindows(enum_callback, None)
        if not matches:
            raise ValueError(f"Window containing '{title}' not found.")
        hwnd = matches[0]
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    return left, top, right - left, bottom - top

def run_debug(window_title: str, fps: int = 15, duration: int = 10) -> None:
    print(f"Searching for window: '{window_title}'...")
    try:
        left, top, width, height = get_window_bounds(window_title)
    except ValueError as e:
        print(e)
        print("Tip: Open Task Manager to see the exact window title.")
        return

    print(f"Window found. Region: ({left}, {top}, {width}, {height})")
    print(f"Capturing {duration}s @ {fps}FPS. Press 'q' to exit.")

    monitor = {"left": left, "top": top, "width": width, "height": height}
    frames = []
    start = time.time()

    with mss.mss() as sct:
        while time.time() - start < duration:
            t0 = time.perf_counter()
            frame = np.array(sct.grab(monitor))[..., :3]
            frames.append(frame)

            cv2.imshow("Game Window Capture", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            elapsed = time.perf_counter() - t0
            time.sleep(max(0.0, 1.0 / fps - elapsed))

    cv2.destroyAllWindows()

    if not frames:
        print("ERROR: No frames captured.")
        return

    is_black = np.mean(frames[-1]) < 15
    variance = 0.0
    if len(frames) > 2:
        diff = np.abs(frames[-1].astype(float) - frames[-2].astype(float))
        variance = np.mean(diff)

    if is_black:
        print("SCREEN IS BLACK. Game may be in Exclusive Fullscreen or minimized.")
    elif variance < 2.0:
        print("SCREEN IS STATIC. Game might be paused or region offset.")
    else:
        print("CAPTURE WORKING: Window captured correctly.")

    out_path = Path("debug_last_frame.jpg")
    cv2.imwrite(str(out_path), frames[-1])
    print(f"Last frame saved to: {out_path}")

if __name__ == "__main__":
    try:
        GAME_WINDOW_TITLE = "HoYoPlay"
        run_debug(GAME_WINDOW_TITLE)
    except KeyboardInterrupt:
        sys.exit(0)