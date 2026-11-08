"""
Main GUI application for AutoClicker Reimagined.
Modern dark cyber-themed interface built with CustomTkinter.
"""

import time
import os
import sys
import tkinter as tk
from typing import Dict, Any, Optional
import customtkinter as ctk

def get_asset_path(relative_path: str) -> str:
    """Resolve asset path correctly for both development and PyInstaller bundled environments."""
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_path, relative_path)

from ..win32_api import (
    enable_high_dpi_awareness,
    ensure_desktop_station,
    get_window_info,
    get_client_size,
    post_background_click,
)
from ..window_manager import WindowManager
from ..core_engine import ClickEngine
from ..config_manager import ConfigManager, PRESETS
from ..hotkey_manager import HotkeyManager
from ..sound_effects import play_cue
from .picker_overlay import TargetPickerOverlay


class AutoClickerApp(ctk.CTk):
    """Main application window for AutoClicker Reimagined."""

    def __init__(self):
        # High DPI awareness must be initialized before window creation
        enable_high_dpi_awareness()
        ensure_desktop_station()

        super().__init__()

        # Setup CustomTkinter Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("AutoClicker Reimagined — Background & High-Speed Engine")
        self.geometry("740x760")
        self.minsize(680, 700)

        # App icon
        try:
            icon_file = get_asset_path(os.path.join("assets", "icon.ico"))
            if os.path.exists(icon_file):
                self.iconbitmap(icon_file)
        except Exception:
            pass

        # Backend components
        self.config_mgr = ConfigManager()
        self.engine = ClickEngine()
        self.hotkey_mgr = HotkeyManager()

        # Engine callbacks
        self.engine.on_stats_update = self._on_stats_update
        self.engine.on_state_change = self._on_engine_state_change

        # UI state variables
        self.mode_var = tk.StringVar(value=self.config_mgr.config.get("mode", "background"))
        self.delivery_mode_var = tk.StringVar(value=self.config_mgr.config.get("delivery_mode", "post_message"))
        self.button_var = tk.StringVar(value=self.config_mgr.config.get("button", "left"))
        self.click_type_var = tk.StringVar(value=self.config_mgr.config.get("click_type", "single"))
        self.use_cps_var = tk.BooleanVar(value=self.config_mgr.config.get("use_cps_mode", True))
        self.cps_var = tk.DoubleVar(value=self.config_mgr.config.get("cps", 10.0))
        self.jitter_enabled_var = tk.BooleanVar(value=self.config_mgr.config.get("jitter_enabled", False))
        self.jitter_ms_var = tk.DoubleVar(value=self.config_mgr.config.get("jitter_ms", 12.0))
        self.coord_jitter_var = tk.IntVar(value=self.config_mgr.config.get("coord_jitter_px", 3))
        self.hold_ms_var = tk.DoubleVar(value=self.config_mgr.config.get("hold_duration_ms", 12.0))
        self.stop_mode_var = tk.StringVar(value=self.config_mgr.config.get("stop_mode", "infinite"))
        self.max_clicks_var = tk.IntVar(value=self.config_mgr.config.get("max_clicks", 1000))
        self.max_time_var = tk.DoubleVar(value=self.config_mgr.config.get("max_time_sec", 60.0))
        self.always_on_top_var = tk.BooleanVar(value=self.config_mgr.config.get("always_on_top", True))
        self.sound_enabled_var = tk.BooleanVar(value=self.config_mgr.config.get("sound_effects", True))

        self.target_hwnd = self.config_mgr.config.get("target_hwnd", 0)
        self.target_x_var = tk.IntVar(value=self.config_mgr.config.get("target_x", 100))
        self.target_y_var = tk.IntVar(value=self.config_mgr.config.get("target_y", 100))

        # Interval details
        self.int_h_var = tk.IntVar(value=self.config_mgr.config.get("interval_hours", 0))
        self.int_m_var = tk.IntVar(value=self.config_mgr.config.get("interval_mins", 0))
        self.int_s_var = tk.IntVar(value=self.config_mgr.config.get("interval_secs", 0))
        self.int_ms_var = tk.IntVar(value=self.config_mgr.config.get("interval_ms", 100))

        # Hotkeys
        self.hotkey_toggle_var = tk.StringVar(value=self.config_mgr.config.get("hotkey_toggle", "F6"))
        self.hotkey_pick_var = tk.StringVar(value=self.config_mgr.config.get("hotkey_pick", "F7"))

        # Windows cache
        self.active_windows_cache = []

        # Build Interface
        self._build_ui()

        # Apply initial settings
        self.attributes("-topmost", self.always_on_top_var.get())
        self._register_hotkeys()

        # Handle window exit cleanly
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        """Construct the complete user interface."""
        # Top Header Bar
        header = ctk.CTkFrame(self, corner_radius=0, fg_color="#0F172A", height=70)
        header.pack(fill="x", side="top")

        # Title & Subtitle
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", padx=16, pady=10)

        lbl_title = ctk.CTkLabel(
            title_box,
            text="⚡ AUTOCLICKER REIMAGINED",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color="#00E5FF",
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            title_box,
            text="Alt-Tab Inactive Window Clicking • High-Precision Timing Engine",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#94A3B8",
        )
        lbl_sub.pack(anchor="w")

        # Header Right Controls (Presets, Topmost, Sound)
        header_right = ctk.CTkFrame(header, fg_color="transparent")
        header_right.pack(side="right", padx=16, pady=10)

        ctk.CTkLabel(
            header_right,
            text="Preset:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#E2E8F0"
        ).pack(side="left", padx=(0, 6))

        preset_names = list(PRESETS.keys())
        self.preset_dropdown = ctk.CTkOptionMenu(
            header_right,
            values=preset_names,
            width=175,
            command=self._on_preset_selected,
            fg_color="#1E293B",
            button_color="#0284C7",
            button_hover_color="#0369A1",
        )
        self.preset_dropdown.pack(side="left", padx=(0, 10))

        sw_top = ctk.CTkSwitch(
            header_right,
            text="Pinned",
            variable=self.always_on_top_var,
            command=self._on_topmost_toggled,
            width=50,
            progress_color="#00E5FF",
        )
        sw_top.pack(side="left", padx=4)

        sw_snd = ctk.CTkSwitch(
            header_right,
            text="Audio",
            variable=self.sound_enabled_var,
            width=50,
            progress_color="#10B981",
        )
        sw_snd.pack(side="left", padx=4)

        # Tabview for categorized navigation
        self.tabs = ctk.CTkTabview(
            self,
            fg_color="#111827",
            segmented_button_fg_color="#1F2937",
            segmented_button_selected_color="#0284C7",
            segmented_button_selected_hover_color="#0369A1",
        )
        self.tabs.pack(fill="both", expand=True, padx=12, pady=(8, 4))

        tab_main = self.tabs.add("⚡ Click Settings")
        tab_target = self.tabs.add("🎯 Background Target")
        tab_antidetect = self.tabs.add("🛡️ Anti-Detection & Jitter")
        tab_hotkeys = self.tabs.add("⚙️ Hotkeys & Settings")

        self._build_tab_main(tab_main)
        self._build_tab_target(tab_target)
        self._build_tab_antidetect(tab_antidetect)
        self._build_tab_hotkeys(tab_hotkeys)

        # Bottom HUD / Status Bar
        self._build_bottom_hud()

    def _build_tab_main(self, parent):
        """Build the primary Click Settings tab."""
        # 1. Mode Card
        card_mode = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1E293B")
        card_mode.pack(fill="x", padx=10, pady=(6, 8))

        ctk.CTkLabel(
            card_mode,
            text="TARGETING MODE",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38BDF8"
        ).pack(anchor="w", padx=14, pady=(8, 4))

        mode_btn_box = ctk.CTkFrame(card_mode, fg_color="transparent")
        mode_btn_box.pack(fill="x", padx=14, pady=(0, 10))

        modes = [
            ("👻 Background Window (Alt-Tab Friendly)", "background"),
            ("🖱️ Follow Mouse Cursor", "cursor"),
            ("📍 Fixed Screen Coords", "fixed_screen"),
        ]
        for label, val in modes:
            r = ctk.CTkRadioButton(
                mode_btn_box,
                text=label,
                value=val,
                variable=self.mode_var,
                command=self._on_mode_changed,
                fg_color="#00E5FF",
                font=ctk.CTkFont(size=12),
            )
            r.pack(side="left", padx=(0, 16))

        # 2. Click Speed / Interval Card
        card_speed = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1E293B")
        card_speed.pack(fill="x", padx=10, pady=6)

        header_speed = ctk.CTkFrame(card_speed, fg_color="transparent")
        header_speed.pack(fill="x", padx=14, pady=(8, 4))

        ctk.CTkLabel(
            header_speed,
            text="CLICK SPEED / RATE",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38BDF8"
        ).pack(side="left")

        # Switch between CPS slider and exact interval
        sw_cps = ctk.CTkSwitch(
            header_speed,
            text="Direct CPS Mode",
            variable=self.use_cps_var,
            command=self._update_speed_mode_visibility,
            progress_color="#00E5FF",
            font=ctk.CTkFont(size=11),
        )
        sw_cps.pack(side="right")

        # CPS Controls Container
        self.box_cps = ctk.CTkFrame(card_speed, fg_color="transparent")
        self.box_cps.pack(fill="x", padx=14, pady=(4, 10))

        lbl_cps_val_box = ctk.CTkFrame(self.box_cps, fg_color="transparent")
        lbl_cps_val_box.pack(fill="x", pady=(0, 4))

        self.lbl_cps_display = ctk.CTkLabel(
            lbl_cps_val_box,
            text=f"Speed: {self.cps_var.get():.1f} CPS  (1 Click every {1000.0/max(0.1, self.cps_var.get()):.1f} ms)",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color="#F8FAFC",
        )
        self.lbl_cps_display.pack(side="left")

        # CPS Slider
        self.slider_cps = ctk.CTkSlider(
            self.box_cps,
            from_=1.0,
            to=250.0,
            number_of_steps=249,
            variable=self.cps_var,
            command=self._on_cps_slider,
            progress_color="#00E5FF",
            button_color="#38BDF8",
            button_hover_color="#0284C7",
        )
        self.slider_cps.pack(fill="x", pady=(2, 6))

        # Quick CPS Pills
        quick_cps_box = ctk.CTkFrame(self.box_cps, fg_color="transparent")
        quick_cps_box.pack(fill="x")
        ctk.CTkLabel(quick_cps_box, text="Quick Presets:", font=ctk.CTkFont(size=11), text_color="#94A3B8").pack(side="left", padx=(0, 6))

        for q_cps in [5, 10, 16, 25, 50, 100, 200, 500]:
            btn = ctk.CTkButton(
                quick_cps_box,
                text=f"{q_cps}",
                width=38,
                height=24,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#334155",
                hover_color="#0284C7",
                command=lambda val=q_cps: self._set_cps_quick(val),
            )
            btn.pack(side="left", padx=2)

        # Interval Controls Container (Hours, Mins, Secs, Ms)
        self.box_interval = ctk.CTkFrame(card_speed, fg_color="transparent")
        # will be packed or hidden based on use_cps_var
        int_fields = [
            ("Hours", self.int_h_var),
            ("Mins", self.int_m_var),
            ("Secs", self.int_s_var),
            ("Milliseconds", self.int_ms_var),
        ]
        for lbl_name, var in int_fields:
            col = ctk.CTkFrame(self.box_interval, fg_color="transparent")
            col.pack(side="left", expand=True, padx=4, pady=6)
            ctk.CTkLabel(col, text=lbl_name, font=ctk.CTkFont(size=11), text_color="#94A3B8").pack()
            e = ctk.CTkEntry(col, textvariable=var, width=80, justify="center", font=ctk.CTkFont(size=13, weight="bold"))
            e.pack(pady=2)

        self._update_speed_mode_visibility()

        # 3. Mouse Options & Click Type Card
        card_mouse = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1E293B")
        card_mouse.pack(fill="x", padx=10, pady=6)

        ctk.CTkLabel(
            card_mouse,
            text="MOUSE BUTTON & CLICK TYPE",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38BDF8"
        ).pack(anchor="w", padx=14, pady=(8, 4))

        mouse_row = ctk.CTkFrame(card_mouse, fg_color="transparent")
        mouse_row.pack(fill="x", padx=14, pady=(2, 10))

        # Button Segment
        ctk.CTkLabel(mouse_row, text="Button:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 6))
        seg_btn = ctk.CTkSegmentedButton(
            mouse_row,
            values=["Left", "Right", "Middle"],
            variable=self.button_var,
            selected_color="#0284C7",
            selected_hover_color="#0369A1",
        )
        seg_btn.pack(side="left", padx=(0, 20))

        # Click Type Segment
        ctk.CTkLabel(mouse_row, text="Type:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 6))
        seg_type = ctk.CTkSegmentedButton(
            mouse_row,
            values=["Single", "Double", "Triple"],
            variable=self.click_type_var,
            selected_color="#0284C7",
            selected_hover_color="#0369A1",
        )
        seg_type.pack(side="left", padx=(0, 20))

        # Hold Duration
        ctk.CTkLabel(mouse_row, text="Hold (ms):", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 4))
        e_hold = ctk.CTkEntry(mouse_row, textvariable=self.hold_ms_var, width=55, justify="center")
        e_hold.pack(side="left")

        # 4. Stop Condition Card
        card_stop = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1E293B")
        card_stop.pack(fill="x", padx=10, pady=6)

        ctk.CTkLabel(
            card_stop,
            text="STOP CONDITION",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38BDF8"
        ).pack(anchor="w", padx=14, pady=(8, 4))

        stop_row = ctk.CTkFrame(card_stop, fg_color="transparent")
        stop_row.pack(fill="x", padx=14, pady=(2, 10))

        ctk.CTkRadioButton(
            stop_row,
            text="Repeat Until Stopped (Hotkey)",
            value="infinite",
            variable=self.stop_mode_var,
            fg_color="#00E5FF",
        ).pack(side="left", padx=(0, 16))

        r_count = ctk.CTkRadioButton(
            stop_row,
            text="Stop After",
            value="count",
            variable=self.stop_mode_var,
            fg_color="#00E5FF",
        )
        r_count.pack(side="left", padx=(0, 4))

        e_count = ctk.CTkEntry(stop_row, textvariable=self.max_clicks_var, width=65, justify="center")
        e_count.pack(side="left", padx=(0, 4))
        ctk.CTkLabel(stop_row, text="clicks", text_color="#94A3B8").pack(side="left", padx=(0, 16))

        r_time = ctk.CTkRadioButton(
            stop_row,
            text="Stop After",
            value="time",
            variable=self.stop_mode_var,
            fg_color="#00E5FF",
        )
        r_time.pack(side="left", padx=(0, 4))

        e_time = ctk.CTkEntry(stop_row, textvariable=self.max_time_var, width=65, justify="center")
        e_time.pack(side="left", padx=(0, 4))
        ctk.CTkLabel(stop_row, text="seconds", text_color="#94A3B8").pack(side="left")

    def _build_tab_target(self, parent):
        """Build the Background Window Target tab."""
        # Top banner explanation
        banner = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1E293B", border_width=1, border_color="#00E5FF")
        banner.pack(fill="x", padx=10, pady=(8, 6))

        ctk.CTkLabel(
            banner,
            text="👻 ALT-TAB & BACKGROUND INACTIVE WINDOW CLICKING",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#00E5FF",
        ).pack(anchor="w", padx=14, pady=(8, 2))

        ctk.CTkLabel(
            banner,
            text="Clicking messages are sent straight to the target window's queue via Win32 API.\n"
                 "You can chat in Discord, browse YouTube, or code while your game is clicked in the background without moving your cursor!",
            font=ctk.CTkFont(size=11),
            text_color="#CBD5E1",
            justify="left",
        ).pack(anchor="w", padx=14, pady=(0, 8))

        # Big Interactive Picker Button Card
        card_picker = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1E293B")
        card_picker.pack(fill="x", padx=10, pady=6)

        btn_pick = ctk.CTkButton(
            card_picker,
            text="🎯 Interactive Target Window & Point Picker (or press F7)",
            height=46,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#0284C7",
            hover_color="#0369A1",
            command=self._start_target_picker,
        )
        btn_pick.pack(fill="x", padx=14, pady=12)

        # Dropdown selection of active windows
        card_win_list = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1E293B")
        card_win_list.pack(fill="x", padx=10, pady=6)

        header_win = ctk.CTkFrame(card_win_list, fg_color="transparent")
        header_win.pack(fill="x", padx=14, pady=(8, 4))

        ctk.CTkLabel(
            header_win,
            text="SELECT TARGET WINDOW FROM ACTIVE PROCESSES",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38BDF8"
        ).pack(side="left")

        btn_refresh = ctk.CTkButton(
            header_win,
            text="🔄 Refresh Windows",
            width=130,
            height=26,
            fg_color="#334155",
            hover_color="#475569",
            command=self._refresh_window_list,
        )
        btn_refresh.pack(side="right")

        self.win_dropdown = ctk.CTkOptionMenu(
            card_win_list,
            values=["[No windows loaded — click Refresh]"],
            command=self._on_window_dropdown_selected,
            height=34,
            fg_color="#0F172A",
            button_color="#0284C7",
            button_hover_color="#0369A1",
        )
        self.win_dropdown.pack(fill="x", padx=14, pady=(4, 10))

        # Target Coordinates Card
        card_coords = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1E293B")
        card_coords.pack(fill="x", padx=10, pady=6)

        ctk.CTkLabel(
            card_coords,
            text="TARGET CLICK COORDINATES (CLIENT RELATIVE)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38BDF8"
        ).pack(anchor="w", padx=14, pady=(8, 4))

        coords_row = ctk.CTkFrame(card_coords, fg_color="transparent")
        coords_row.pack(fill="x", padx=14, pady=(2, 10))

        ctk.CTkLabel(coords_row, text="Client X:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 4))
        ctk.CTkEntry(coords_row, textvariable=self.target_x_var, width=70, justify="center").pack(side="left", padx=(0, 16))

        ctk.CTkLabel(coords_row, text="Client Y:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 4))
        ctk.CTkEntry(coords_row, textvariable=self.target_y_var, width=70, justify="center").pack(side="left", padx=(0, 16))

        btn_center = ctk.CTkButton(
            coords_row,
            text="📐 Center on Window",
            width=140,
            fg_color="#334155",
            hover_color="#475569",
            command=self._center_coords_on_target,
        )
        btn_center.pack(side="left", padx=(0, 10))

        # Target Details & Test Button Card
        card_target_status = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1E293B")
        card_target_status.pack(fill="x", padx=10, pady=6)

        header_test = ctk.CTkFrame(card_target_status, fg_color="transparent")
        header_test.pack(fill="x", padx=14, pady=(8, 4))

        self.lbl_target_summary = ctk.CTkLabel(
            header_test,
            text=self._format_target_summary(),
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#F8FAFC",
            justify="left",
        )
        self.lbl_target_summary.pack(side="left")

        btn_test = ctk.CTkButton(
            header_test,
            text="⚡ Test 1 Click",
            width=120,
            height=32,
            fg_color="#10B981",
            hover_color="#059669",
            font=ctk.CTkFont(weight="bold"),
            command=self._test_background_click,
        )
        btn_test.pack(side="right")

        # Delivery Mode selector (Stealth PostMessage vs SendMessage vs Focus Tap)
        card_delivery = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1E293B")
        card_delivery.pack(fill="x", padx=10, pady=6)

        ctk.CTkLabel(
            card_delivery,
            text="BACKGROUND DELIVERY ENGINE",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38BDF8"
        ).pack(anchor="w", padx=14, pady=(8, 4))

        del_box = ctk.CTkFrame(card_delivery, fg_color="transparent")
        del_box.pack(fill="x", padx=14, pady=(2, 10))

        deliveries = [
            ("PostMessage (Stealth / Zero Focus Loss)", "post_message"),
            ("SendMessage (Synchronous)", "send_message"),
            ("Smart Focus-Tap (Fallback)", "focus_tap"),
        ]
        for lbl_del, val_del in deliveries:
            ctk.CTkRadioButton(
                del_box,
                text=lbl_del,
                value=val_del,
                variable=self.delivery_mode_var,
                fg_color="#00E5FF",
                font=ctk.CTkFont(size=11),
            ).pack(side="left", padx=(0, 14))

        # Initial populate of windows
        self.after(300, self._refresh_window_list)

    def _build_tab_antidetect(self, parent):
        """Build the Anti-Detection & Jitter tab."""
        card_anti = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1E293B")
        card_anti.pack(fill="x", padx=10, pady=(8, 6))

        header_anti = ctk.CTkFrame(card_anti, fg_color="transparent")
        header_anti.pack(fill="x", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            header_anti,
            text="ANTI-DETECTION & HUMANIZER SHIELD",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#10B981",
        ).pack(side="left")

        sw_anti = ctk.CTkSwitch(
            header_anti,
            text="Enable Shield",
            variable=self.jitter_enabled_var,
            progress_color="#10B981",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        sw_anti.pack(side="right")

        ctk.CTkLabel(
            card_anti,
            text="Breaks robotic timing signatures by introducing natural human micro-variations\n"
                 "to click intervals and coordinate dispersal. Highly recommended for Roblox, Minecraft, and MMOs.",
            font=ctk.CTkFont(size=11),
            text_color="#CBD5E1",
            justify="left",
        ).pack(anchor="w", padx=14, pady=(0, 10))

        # 1. Interval Jitter Slider
        card_interval_jit = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1E293B")
        card_interval_jit.pack(fill="x", padx=10, pady=6)

        lbl_jit_header = ctk.CTkFrame(card_interval_jit, fg_color="transparent")
        lbl_jit_header.pack(fill="x", padx=14, pady=(8, 2))

        ctk.CTkLabel(
            lbl_jit_header,
            text="Click Interval Jitter (± ms):",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38BDF8"
        ).pack(side="left")

        self.lbl_jitter_val = ctk.CTkLabel(
            lbl_jit_header,
            text=f"±{self.jitter_ms_var.get():.1f} ms",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color="#F8FAFC",
        )
        self.lbl_jitter_val.pack(side="right")

        slider_jit = ctk.CTkSlider(
            card_interval_jit,
            from_=0.0,
            to=100.0,
            variable=self.jitter_ms_var,
            command=lambda val: self.lbl_jitter_val.configure(text=f"±{float(val):.1f} ms"),
            progress_color="#10B981",
            button_color="#34D399",
            button_hover_color="#059669",
        )
        slider_jit.pack(fill="x", padx=14, pady=(2, 10))

        # 2. Coordinate Jitter Slider
        card_coord_jit = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1E293B")
        card_coord_jit.pack(fill="x", padx=10, pady=6)

        lbl_coord_header = ctk.CTkFrame(card_coord_jit, fg_color="transparent")
        lbl_coord_header.pack(fill="x", padx=14, pady=(8, 2))

        ctk.CTkLabel(
            lbl_coord_header,
            text="Coordinate Scatter Radius (± pixels):",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38BDF8"
        ).pack(side="left")

        self.lbl_coord_val = ctk.CTkLabel(
            lbl_coord_header,
            text=f"±{self.coord_jitter_var.get()} px",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color="#F8FAFC",
        )
        self.lbl_coord_val.pack(side="right")

        slider_coord = ctk.CTkSlider(
            card_coord_jit,
            from_=0,
            to=25,
            number_of_steps=25,
            variable=self.coord_jitter_var,
            command=lambda val: self.lbl_coord_val.configure(text=f"±{int(float(val))} px"),
            progress_color="#10B981",
            button_color="#34D399",
            button_hover_color="#059669",
        )
        slider_coord.pack(fill="x", padx=14, pady=(2, 10))

    def _build_tab_hotkeys(self, parent):
        """Build Hotkeys & Settings tab."""
        card_hk = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1E293B")
        card_hk.pack(fill="x", padx=10, pady=(8, 6))

        ctk.CTkLabel(
            card_hk,
            text="GLOBAL HOTKEYS CONFIGURATION",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38BDF8"
        ).pack(anchor="w", padx=14, pady=(8, 4))

        hk_box = ctk.CTkFrame(card_hk, fg_color="transparent")
        hk_box.pack(fill="x", padx=14, pady=(2, 10))

        # Start / Stop Hotkey
        row_toggle = ctk.CTkFrame(hk_box, fg_color="transparent")
        row_toggle.pack(fill="x", pady=4)
        ctk.CTkLabel(row_toggle, text="Start / Stop Toggle Hotkey:", width=220, anchor="w").pack(side="left")
        e_tog = ctk.CTkEntry(row_toggle, textvariable=self.hotkey_toggle_var, width=90, justify="center")
        e_tog.pack(side="left", padx=8)

        # Target Picker Hotkey
        row_pick = ctk.CTkFrame(hk_box, fg_color="transparent")
        row_pick.pack(fill="x", pady=4)
        ctk.CTkLabel(row_pick, text="Target Coordinate Picker Hotkey:", width=220, anchor="w").pack(side="left")
        e_pk = ctk.CTkEntry(row_pick, textvariable=self.hotkey_pick_var, width=90, justify="center")
        e_pk.pack(side="left", padx=8)

        btn_apply_hk = ctk.CTkButton(
            hk_box,
            text="Apply Hotkeys",
            width=120,
            fg_color="#0284C7",
            hover_color="#0369A1",
            command=self._register_hotkeys,
        )
        btn_apply_hk.pack(anchor="w", pady=(8, 2))

        # Settings Save/Reset
        card_save = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1E293B")
        card_save.pack(fill="x", padx=10, pady=6)

        ctk.CTkLabel(
            card_save,
            text="SAVE SETTINGS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38BDF8"
        ).pack(anchor="w", padx=14, pady=(8, 4))

        save_row = ctk.CTkFrame(card_save, fg_color="transparent")
        save_row.pack(fill="x", padx=14, pady=(2, 10))

        btn_save = ctk.CTkButton(
            save_row,
            text="💾 Save as Default Settings",
            fg_color="#334155",
            hover_color="#475569",
            command=self._save_current_settings,
        )
        btn_save.pack(side="left", padx=(0, 10))

        self.lbl_save_status = ctk.CTkLabel(save_row, text="", text_color="#10B981")
        self.lbl_save_status.pack(side="left")

    def _build_bottom_hud(self):
        """Construct the persistent live stats and action trigger bar."""
        hud_bar = ctk.CTkFrame(self, corner_radius=0, fg_color="#0B0F19", height=85)
        hud_bar.pack(fill="x", side="bottom")

        # Left: Status Badge
        badge_box = ctk.CTkFrame(hud_bar, fg_color="transparent")
        badge_box.pack(side="left", padx=16, pady=12)

        self.status_badge = ctk.CTkButton(
            badge_box,
            text="● STOPPED",
            width=115,
            height=34,
            fg_color="#334155",
            hover_color="#334155",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#94A3B8",
            corner_radius=8,
        )
        self.status_badge.pack()

        # Center: Live Statistics
        stats_box = ctk.CTkFrame(hud_bar, fg_color="transparent")
        stats_box.pack(side="left", expand=True, padx=10, pady=8)

        stats_top = ctk.CTkFrame(stats_box, fg_color="transparent")
        stats_top.pack()

        self.lbl_stat_clicks = ctk.CTkLabel(
            stats_top,
            text="Clicks: 0",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color="#F8FAFC",
        )
        self.lbl_stat_clicks.pack(side="left", padx=10)

        self.lbl_stat_cps = ctk.CTkLabel(
            stats_top,
            text="Speed: 0.0 CPS",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color="#00E5FF",
        )
        self.lbl_stat_cps.pack(side="left", padx=10)

        self.lbl_stat_time = ctk.CTkLabel(
            stats_top,
            text="Time: 00:00:00",
            font=ctk.CTkFont(family="Consolas", size=13),
            text_color="#94A3B8",
        )
        self.lbl_stat_time.pack(side="left", padx=10)

        self.lbl_hud_target = ctk.CTkLabel(
            stats_box,
            text="Target: " + self._get_short_target_desc(),
            font=ctk.CTkFont(size=11),
            text_color="#64748B",
        )
        self.lbl_hud_target.pack(pady=(2, 0))

        # Right: Prominent Toggle Button
        btn_box = ctk.CTkFrame(hud_bar, fg_color="transparent")
        btn_box.pack(side="right", padx=16, pady=12)

        self.btn_action = ctk.CTkButton(
            btn_box,
            text=f"▶ START ({self.hotkey_toggle_var.get()})",
            width=160,
            height=44,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            command=self._on_action_button_click,
            corner_radius=8,
        )
        self.btn_action.pack()

    # --- UI Event Handlers & Helpers ---

    def _on_cps_slider(self, val):
        cps = float(val)
        interval_ms = 1000.0 / max(0.1, cps)
        self.lbl_cps_display.configure(
            text=f"Speed: {cps:.1f} CPS  (1 Click every {interval_ms:.1f} ms)"
        )

    def _set_cps_quick(self, cps_val):
        self.cps_var.set(float(cps_val))
        self._on_cps_slider(cps_val)

    def _update_speed_mode_visibility(self):
        if self.use_cps_var.get():
            self.box_interval.pack_forget()
            self.box_cps.pack(fill="x", padx=14, pady=(4, 10))
        else:
            self.box_cps.pack_forget()
            self.box_interval.pack(fill="x", padx=14, pady=(4, 10))

    def _on_mode_changed(self):
        self._update_target_labels()

    def _on_topmost_toggled(self):
        self.attributes("-topmost", self.always_on_top_var.get())

    def _on_preset_selected(self, preset_name: str):
        cfg = self.config_mgr.apply_preset(preset_name)
        if "cps" in cfg:
            self.cps_var.set(cfg["cps"])
            self._on_cps_slider(cfg["cps"])
        if "use_cps_mode" in cfg:
            self.use_cps_var.set(cfg["use_cps_mode"])
            self._update_speed_mode_visibility()
        if "jitter_enabled" in cfg:
            self.jitter_enabled_var.set(cfg["jitter_enabled"])
        if "jitter_ms" in cfg:
            self.jitter_ms_var.set(cfg["jitter_ms"])
            if hasattr(self, "lbl_jitter_val"):
                self.lbl_jitter_val.configure(text=f"±{cfg['jitter_ms']:.1f} ms")
        if "coord_jitter_px" in cfg:
            self.coord_jitter_var.set(cfg["coord_jitter_px"])
            if hasattr(self, "lbl_coord_val"):
                self.lbl_coord_val.configure(text=f"±{cfg['coord_jitter_px']} px")
        if "button" in cfg:
            self.button_var.set(cfg["button"].capitalize())
        if "click_type" in cfg:
            self.click_type_var.set(cfg["click_type"].capitalize())
        if "mode" in cfg:
            self.mode_var.set(cfg["mode"])
        play_cue("pick", self.sound_enabled_var.get())

    def _format_target_summary(self) -> str:
        proc = self.config_mgr.config.get("target_process", "None")
        title = self.config_mgr.config.get("target_title", "None")
        if len(title) > 28:
            title = title[:26] + ".."
        x = self.target_x_var.get()
        y = self.target_y_var.get()
        return f"Target: [{proc}] {title}\nCoords: Client (X: {x}, Y: {y}) | HWND: {self.target_hwnd}"

    def _get_short_target_desc(self) -> str:
        mode = self.mode_var.get()
        if mode == "cursor":
            return "Mouse Cursor (Foreground)"
        elif mode == "fixed_screen":
            return f"Fixed Screen ({self.target_x_var.get()}, {self.target_y_var.get()})"
        proc = self.config_mgr.config.get("target_process", "None")
        if proc == "unknown" or not proc:
            proc = "Target Window"
        return f"[{proc}] at ({self.target_x_var.get()}, {self.target_y_var.get()})"

    def _update_target_labels(self):
        txt = self._format_target_summary()
        if hasattr(self, "lbl_target_summary"):
            self.lbl_target_summary.configure(text=txt)
        if hasattr(self, "lbl_hud_target"):
            self.lbl_hud_target.configure(text="Target: " + self._get_short_target_desc())

    def _refresh_window_list(self):
        windows = WindowManager.get_active_windows()
        self.active_windows_cache = windows

        labels = [w["label"] for w in windows]
        if not labels:
            labels = ["[No interactive windows found]"]

        self.win_dropdown.configure(values=labels)
        # Select first if none selected
        if windows and not self.target_hwnd:
            self._select_window_by_index(0)

    def _on_window_dropdown_selected(self, label: str):
        for w in self.active_windows_cache:
            if w["label"] == label:
                self.target_hwnd = w["hwnd"]
                self.config_mgr.config["target_hwnd"] = w["hwnd"]
                self.config_mgr.config["target_process"] = w["process"]
                self.config_mgr.config["target_title"] = w["title"]
                self._update_target_labels()
                break

    def _select_window_by_index(self, idx: int):
        if 0 <= idx < len(self.active_windows_cache):
            w = self.active_windows_cache[idx]
            self.target_hwnd = w["hwnd"]
            self.config_mgr.config["target_hwnd"] = w["hwnd"]
            self.config_mgr.config["target_process"] = w["process"]
            self.config_mgr.config["target_title"] = w["title"]
            self.win_dropdown.set(w["label"])
            self._update_target_labels()

    def _center_coords_on_target(self):
        if not self.target_hwnd:
            return
        w, h = get_client_size(self.target_hwnd)
        if w > 0 and h > 0:
            self.target_x_var.set(w // 2)
            self.target_y_var.set(h // 2)
            self._update_target_labels()
            play_cue("pick", self.sound_enabled_var.get())

    def _start_target_picker(self):
        """Launch interactive crosshair picker HUD."""
        picker = TargetPickerOverlay(
            master=self,
            on_picked=self._on_target_picked_callback,
            sound_enabled=self.sound_enabled_var.get()
        )
        picker.start()

    def _on_target_picked_callback(self, target_data: Dict[str, Any]):
        """Called when user clicks a window with target picker."""
        hwnd = target_data.get("target_hwnd", 0)
        cx = target_data.get("client_x", 0)
        cy = target_data.get("client_y", 0)
        proc = target_data.get("process", "unknown")
        title = target_data.get("title", "")

        self.target_hwnd = hwnd
        self.target_x_var.set(cx)
        self.target_y_var.set(cy)

        self.config_mgr.config["target_hwnd"] = hwnd
        self.config_mgr.config["target_process"] = proc
        self.config_mgr.config["target_title"] = title
        self.config_mgr.config["target_x"] = cx
        self.config_mgr.config["target_y"] = cy

        self._update_target_labels()
        self.mode_var.set("background")

    def _test_background_click(self):
        """Fire a single test click to verify target window response."""
        if not self.target_hwnd:
            self.lbl_target_summary.configure(text="⚠️ Select a valid window first!")
            return

        cx = self.target_x_var.get()
        cy = self.target_y_var.get()
        btn = self.button_var.get().lower()

        success = post_background_click(
            self.target_hwnd,
            cx,
            cy,
            button=btn,
            click_type="single",
            hold_ms=15.0,
            move_first=True,
            use_send=(self.delivery_mode_var.get() == "send_message"),
        )
        play_cue("test", self.sound_enabled_var.get())
        if success:
            proc = self.config_mgr.config.get("target_process", "Window")
            self.lbl_target_summary.configure(
                text=f"✅ Sent test click to [{proc}] at ({cx}, {cy})!"
            )
            self.after(2500, self._update_target_labels)
        else:
            self.lbl_target_summary.configure(text="❌ Failed to send click: Window handle invalid.")

    def _register_hotkeys(self):
        """Bind global hotkeys."""
        self.hotkey_mgr.unregister_all()

        key_toggle = self.hotkey_toggle_var.get().strip()
        key_pick = self.hotkey_pick_var.get().strip()

        if key_toggle:
            self.hotkey_mgr.register_toggle(key_toggle, self._hotkey_toggle_invoked)
            if hasattr(self, "btn_action"):
                state_lbl = "START" if not self.engine.is_running else "STOP"
                self.btn_action.configure(text=f"{'▶' if state_lbl=='START' else '⏹'} {state_lbl} ({key_toggle})")

        if key_pick:
            self.hotkey_mgr.register_pick(key_pick, lambda: self.after(0, self._start_target_picker))

    def _hotkey_toggle_invoked(self):
        # Hotkey listener runs on a background thread; schedule toggle on Tkinter loop
        self.after(0, self._on_action_button_click)

    def _get_active_config(self) -> Dict[str, Any]:
        """Compile all UI state into engine configuration."""
        return {
            "mode": self.mode_var.get(),
            "delivery_mode": self.delivery_mode_var.get(),
            "target_hwnd": self.target_hwnd,
            "target_x": self.target_x_var.get(),
            "target_y": self.target_y_var.get(),
            "button": self.button_var.get().lower(),
            "click_type": self.click_type_var.get().lower(),
            "hold_duration_ms": self.hold_ms_var.get(),
            "use_cps_mode": self.use_cps_var.get(),
            "cps": self.cps_var.get(),
            "interval_hours": self.int_h_var.get(),
            "interval_mins": self.int_m_var.get(),
            "interval_secs": self.int_s_var.get(),
            "interval_ms": self.int_ms_var.get(),
            "jitter_enabled": self.jitter_enabled_var.get(),
            "jitter_ms": self.jitter_ms_var.get(),
            "coord_jitter_px": self.coord_jitter_var.get(),
            "stop_mode": self.stop_mode_var.get(),
            "max_clicks": self.max_clicks_var.get(),
            "max_time_sec": self.max_time_var.get(),
        }

    def _on_action_button_click(self):
        """User clicked Start/Stop button or triggered toggle hotkey."""
        if self.engine.is_running:
            self.engine.stop("User Stopped")
            play_cue("stop", self.sound_enabled_var.get())
        else:
            cfg = self._get_active_config()
            if cfg["mode"] == "background" and not cfg["target_hwnd"]:
                self.tabs.set("🎯 Background Target")
                self.lbl_target_summary.configure(text="⚠️ Please select or pick a target window first!")
                return
            play_cue("start", self.sound_enabled_var.get())
            self.engine.start(cfg)

    def _on_engine_state_change(self, is_running: bool, reason: str):
        """Called by engine when state changes."""
        self.after(0, lambda: self._apply_engine_state(is_running, reason))

    def _apply_engine_state(self, is_running: bool, reason: str):
        hk = self.hotkey_toggle_var.get().strip()
        if is_running:
            self.status_badge.configure(
                text="● CLICKING...",
                fg_color="#065F46",
                hover_color="#065F46",
                text_color="#34D399",
            )
            self.btn_action.configure(
                text=f"⏹ STOP ({hk})",
                fg_color="#EF4444",
                hover_color="#DC2626",
            )
        else:
            self.status_badge.configure(
                text="● STOPPED",
                fg_color="#334155",
                hover_color="#334155",
                text_color="#94A3B8",
            )
            self.btn_action.configure(
                text=f"▶ START ({hk})",
                fg_color="#10B981",
                hover_color="#059669",
            )

    def _on_stats_update(self, total_clicks: int, current_cps: float, elapsed_time: float):
        """Called periodically by engine with click metrics."""
        self.after(0, lambda: self._apply_stats(total_clicks, current_cps, elapsed_time))

    def _apply_stats(self, total_clicks: int, current_cps: float, elapsed_time: float):
        self.lbl_stat_clicks.configure(text=f"Clicks: {total_clicks:,}")
        self.lbl_stat_cps.configure(text=f"Speed: {current_cps:.1f} CPS")

        mins, secs = divmod(int(elapsed_time), 60)
        hours, mins = divmod(mins, 60)
        self.lbl_stat_time.configure(text=f"Time: {hours:02d}:{mins:02d}:{secs:02d}")

    def _save_current_settings(self):
        cfg = self._get_active_config()
        cfg["hotkey_toggle"] = self.hotkey_toggle_var.get().strip()
        cfg["hotkey_pick"] = self.hotkey_pick_var.get().strip()
        cfg["always_on_top"] = self.always_on_top_var.get()
        cfg["sound_effects"] = self.sound_enabled_var.get()
        cfg["target_process"] = self.config_mgr.config.get("target_process", "")
        cfg["target_title"] = self.config_mgr.config.get("target_title", "")

        self.config_mgr.config.update(cfg)
        self.config_mgr.save()

        self.lbl_save_status.configure(text="Settings saved successfully!")
        self.after(2500, lambda: self.lbl_save_status.configure(text=""))

    def _on_close(self):
        """Clean shutdown handler."""
        if self.engine.is_running:
            self.engine.stop("Application Exit")
        self.hotkey_mgr.unregister_all()
        self.destroy()
