"""
Window management and discovery helper for AutoClicker Reimagined.
Allows discovering active game and app windows, finding child controls,
and mapping coordinates between screen and client space.
"""

import ctypes
from ctypes import wintypes
from typing import List, Dict, Any, Optional, Tuple
import psutil

from .win32_api import (
    user32,
    POINT,
    RECT,
    ensure_desktop_station,
    screen_to_client,
    client_to_screen,
    get_root_window,
    get_window_info,
    get_cursor_pos,
    is_window_valid,
)

# Callback type for EnumWindows and EnumChildWindows
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


class WindowManager:
    """Manages active window listing, process association, and coordinate conversion."""

    @staticmethod
    def get_active_windows() -> List[Dict[str, Any]]:
        """
        Return a filtered list of all interactive application windows on the desktop.
        Filters out invisible utility, taskbar, background system windows.
        """
        ensure_desktop_station()
        windows = []

        def enum_handler(hwnd: int, lparam: int) -> bool:
            if not user32.IsWindowVisible(hwnd):
                return True

            length = user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return True

            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value.strip()

            if not title:
                return True

            # Filter out known Windows system shell overlays that shouldn't be clicked
            ignored_titles = {
                "Program Manager",
                "Windows Input Experience",
                "Settings",
                "Default IME",
                "MSCTFIME UI",
            }
            if title in ignored_titles:
                return True

            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

            process_name = "unknown"
            try:
                proc = psutil.Process(pid.value)
                process_name = proc.name()
            except Exception:
                pass

            # Ignore typical background helper processes
            ignored_processes = {"explorer.exe" if title == "" else ""}
            if process_name in ignored_processes:
                return True

            rect = RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            width = rect.right - rect.left
            height = rect.bottom - rect.top

            # Only windows with actual size
            if width > 50 and height > 50:
                display_label = f"[{process_name}] {title}"
                if len(display_label) > 65:
                    display_label = display_label[:62] + "..."

                windows.append({
                    "hwnd": int(hwnd),
                    "title": title,
                    "process": process_name,
                    "pid": pid.value,
                    "rect": (rect.left, rect.top, rect.right, rect.bottom),
                    "size": (width, height),
                    "label": display_label,
                })
            return True

        cb = WNDENUMPROC(enum_handler)
        user32.EnumWindows(cb, 0)

        # Sort with popular game processes / active windows near top
        def sort_key(item):
            proc = item["process"].lower()
            is_game = any(k in proc for k in ["roblox", "minecraft", "game", "steam", "discord", "chrome", "edge"])
            return (0 if is_game else 1, item["title"].lower())

        windows.sort(key=sort_key)
        return windows

    @staticmethod
    def get_child_windows(parent_hwnd: int) -> List[int]:
        """Enumerate child windows belonging to parent_hwnd."""
        children = []

        def child_proc(hwnd: int, lparam: int) -> bool:
            children.append(int(hwnd))
            return True

        cb = WNDENUMPROC(child_proc)
        user32.EnumChildWindows(parent_hwnd, cb, 0)
        return children

    @staticmethod
    def resolve_target_under_cursor() -> Dict[str, Any]:
        """
        Inspect whatever is currently under the cursor:
        Gets screen coordinate, root window, child window, and client coordinates.
        """
        ensure_desktop_station()
        sx, sy = get_cursor_pos()
        pt = POINT(sx, sy)

        child_hwnd = int(user32.WindowFromPoint(pt))
        root_hwnd = get_root_window(child_hwnd) if child_hwnd else 0

        # Compute client coords
        target_hwnd = child_hwnd if child_hwnd else root_hwnd
        cx, cy = screen_to_client(target_hwnd, sx, sy) if target_hwnd else (0, 0)
        rcx, rcy = screen_to_client(root_hwnd, sx, sy) if root_hwnd else (0, 0)

        info = get_window_info(root_hwnd if root_hwnd else child_hwnd)

        return {
            "screen_x": sx,
            "screen_y": sy,
            "target_hwnd": target_hwnd,
            "root_hwnd": root_hwnd,
            "child_hwnd": child_hwnd,
            "client_x": cx,
            "client_y": cy,
            "root_client_x": rcx,
            "root_client_y": rcy,
            "title": info.get("title", ""),
            "process": info.get("process", ""),
            "pid": info.get("pid", 0),
        }
