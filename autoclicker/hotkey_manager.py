"""
Global hotkey listener and dispatcher for AutoClicker Reimagined.
Allows starting, stopping, and picking coordinates from anywhere in Windows.
"""

from typing import Callable, Optional
import keyboard


class HotkeyManager:
    """Manages global hotkeys for toggling autoclicker and picking targets."""

    def __init__(self):
        self._toggle_handler = None
        self._pick_handler = None
        self._current_toggle_key = ""
        self._current_pick_key = ""

    def register_toggle(self, key_combo: str, callback: Callable[[], None]) -> bool:
        """Register global hotkey to start/stop the autoclicker."""
        if not key_combo:
            return False

        try:
            if self._toggle_handler:
                try:
                    keyboard.remove_hotkey(self._toggle_handler)
                except Exception:
                    pass
                self._toggle_handler = None

            self._toggle_handler = keyboard.add_hotkey(key_combo, callback, suppress=False)
            self._current_toggle_key = key_combo.strip()
            return True
        except Exception:
            return False

    def register_pick(self, key_combo: str, callback: Callable[[], None]) -> bool:
        """Register global hotkey to capture current target window and coordinates."""
        if not key_combo:
            return False

        try:
            if self._pick_handler:
                try:
                    keyboard.remove_hotkey(self._pick_handler)
                except Exception:
                    pass
                self._pick_handler = None

            self._pick_handler = keyboard.add_hotkey(key_combo, callback, suppress=False)
            self._current_pick_key = key_combo.strip()
            return True
        except Exception:
            return False

    def unregister_all(self):
        """Unregister all hotkeys."""
        try:
            if self._toggle_handler:
                keyboard.remove_hotkey(self._toggle_handler)
            if self._pick_handler:
                keyboard.remove_hotkey(self._pick_handler)
        except Exception:
            pass
        self._toggle_handler = None
        self._pick_handler = None
