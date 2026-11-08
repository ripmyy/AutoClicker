"""
Interactive target window and coordinate picker overlay.
Displays a sleek borderless HUD at the top of the screen showing live window info
and captures mouse clicks globally to automatically lock target window and (X, Y) coordinates.
"""

import time
import threading
from typing import Callable, Optional, Dict, Any
import customtkinter as ctk
import pynput

from ..window_manager import WindowManager
from ..sound_effects import play_cue


class TargetPickerOverlay:
    """Floating transparent cyber HUD that captures target window & coordinates."""

    def __init__(self, master: ctk.CTk, on_picked: Callable[[Dict[str, Any]], None], sound_enabled: bool = True):
        self.master = master
        self.on_picked = on_picked
        self.sound_enabled = sound_enabled

        self.overlay: Optional[ctk.CTkToplevel] = None
        self._mouse_listener: Optional[pynput.mouse.Listener] = None
        self._key_listener: Optional[pynput.keyboard.Listener] = None
        self._is_active = False

        self._lbl_title = None
        self._lbl_info = None
        self._lbl_tip = None

    def start(self):
        """Display the picker HUD and begin listening for user click."""
        if self._is_active:
            return

        self._is_active = True

        # Build floating HUD
        self.overlay = ctk.CTkToplevel(self.master)
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-alpha", 0.94)

        # Center at top of primary screen
        sw = self.overlay.winfo_screenwidth()
        hud_w, hud_h = 520, 85
        pos_x = max(10, (sw - hud_w) // 2)
        pos_y = 25
        self.overlay.geometry(f"{hud_w}x{hud_h}+{pos_x}+{pos_y}")

        # Cyber styling container
        container = ctk.CTkFrame(
            self.overlay,
            corner_radius=12,
            fg_color="#0F172A",
            border_width=2,
            border_color="#00E5FF",
        )
        container.pack(fill="both", expand=True, padx=2, pady=2)

        self._lbl_title = ctk.CTkLabel(
            container,
            text="🎯 TARGET PICKER ACTIVE — HOVER OVER GAME & CLICK",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#00E5FF",
        )
        self._lbl_title.pack(pady=(6, 0))

        self._lbl_info = ctk.CTkLabel(
            container,
            text="Inspecting: [Hover over any window...]",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#F8FAFC",
        )
        self._lbl_info.pack(pady=(2, 0))

        self._lbl_tip = ctk.CTkLabel(
            container,
            text="Left-Click on target to lock | Press ESC to cancel",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#94A3B8",
        )
        self._lbl_tip.pack(pady=(2, 6))

        # Start listeners
        self._mouse_listener = pynput.mouse.Listener(on_click=self._on_mouse_click)
        self._mouse_listener.daemon = True
        self._mouse_listener.start()

        self._key_listener = pynput.keyboard.Listener(on_press=self._on_key_press)
        self._key_listener.daemon = True
        self._key_listener.start()

        # Start live cursor inspection update loop
        self._update_inspection()

    def _update_inspection(self):
        """Update live target HUD text at 30 FPS."""
        if not self._is_active or not self.overlay:
            return

        try:
            target = WindowManager.resolve_target_under_cursor()
            proc = target.get("process", "unknown")
            title = target.get("title", "")
            if len(title) > 28:
                title = title[:26] + ".."
            cx = target.get("client_x", 0)
            cy = target.get("client_y", 0)
            
            txt = f"[{proc}] {title} | Client Pos: ({cx}, {cy})"
            if self._lbl_info:
                self._lbl_info.configure(text=txt)
        except Exception:
            pass

        if self._is_active:
            self.overlay.after(35, self._update_inspection)

    def _on_mouse_click(self, x, y, button, pressed):
        """Global click captured."""
        if not pressed or button != pynput.mouse.Button.left:
            return

        if not self._is_active:
            return

        # Give 30ms for mouse event settling, then capture target info
        time.sleep(0.02)
        target = WindowManager.resolve_target_under_cursor()

        play_cue("pick", self.sound_enabled)

        # Schedule closing and callback on Tkinter main thread
        self.master.after(0, lambda: self._finish_picking(target))

    def _on_key_press(self, key):
        """Check for ESC key to cancel."""
        if key == pynput.keyboard.Key.esc:
            self.master.after(0, self._cancel_picking)

    def _finish_picking(self, target_data: Dict[str, Any]):
        """Clean up and notify caller with captured target."""
        self._cleanup()
        if self.on_picked:
            self.on_picked(target_data)

    def _cancel_picking(self):
        """Cancel picking without applying changes."""
        self._cleanup()

    def _cleanup(self):
        self._is_active = False

        if self._mouse_listener:
            try:
                self._mouse_listener.stop()
            except Exception:
                pass
            self._mouse_listener = None

        if self._key_listener:
            try:
                self._key_listener.stop()
            except Exception:
                pass
            self._key_listener = None

        if self.overlay:
            try:
                self.overlay.destroy()
            except Exception:
                pass
            self.overlay = None
