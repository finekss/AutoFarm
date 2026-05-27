import ctypes
import win32gui
from typing import Tuple

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

def get_window_bounds(title: str) -> Tuple[int, int, int, int]:
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