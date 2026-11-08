"""
Configuration and preset profile management for AutoClicker Reimagined.
Handles saving/loading user settings and provides ready-to-use game presets.
"""

import json
import os
from typing import Dict, Any

DEFAULT_CONFIG: Dict[str, Any] = {
    "mode": "background",               # "background", "cursor", "fixed_screen"
    "delivery_mode": "post_message",    # "post_message", "send_message", "focus_tap"
    "target_hwnd": 0,
    "target_title": "",
    "target_process": "",
    "target_x": 100,
    "target_y": 100,
    "button": "left",                   # "left", "right", "middle"
    "click_type": "single",             # "single", "double", "triple"
    "hold_duration_ms": 12.0,
    "use_cps_mode": True,
    "cps": 10.0,
    "interval_hours": 0,
    "interval_mins": 0,
    "interval_secs": 0,
    "interval_ms": 100,
    "jitter_enabled": False,
    "jitter_ms": 12.0,
    "coord_jitter_px": 3,
    "stop_mode": "infinite",            # "infinite", "count", "time"
    "max_clicks": 1000,
    "max_time_sec": 300.0,
    "hotkey_toggle": "F6",
    "hotkey_pick": "F7",
    "sound_effects": True,
    "always_on_top": True,
    "theme": "dark",
}

PRESETS: Dict[str, Dict[str, Any]] = {
    "Default (10 CPS)": {
        "use_cps_mode": True,
        "cps": 10.0,
        "jitter_enabled": False,
        "jitter_ms": 0.0,
        "coord_jitter_px": 0,
        "button": "left",
        "click_type": "single",
    },
    "Roblox AFK Farm (Background + Anti-AFK)": {
        "mode": "background",
        "delivery_mode": "post_message",
        "use_cps_mode": True,
        "cps": 5.0,
        "jitter_enabled": True,
        "jitter_ms": 35.0,
        "coord_jitter_px": 5,
        "button": "left",
        "click_type": "single",
        "hold_duration_ms": 25.0,
    },
    "Ultra Speed (100 CPS)": {
        "use_cps_mode": True,
        "cps": 100.0,
        "jitter_enabled": False,
        "button": "left",
        "click_type": "single",
        "hold_duration_ms": 2.0,
    },
    "Minecraft PvP (16 CPS Jitter)": {
        "use_cps_mode": True,
        "cps": 16.0,
        "jitter_enabled": True,
        "jitter_ms": 10.0,
        "coord_jitter_px": 2,
        "button": "left",
        "click_type": "single",
        "hold_duration_ms": 15.0,
    },
    "Cookie Clicker Hyper (200 CPS)": {
        "use_cps_mode": True,
        "cps": 200.0,
        "jitter_enabled": False,
        "button": "left",
        "click_type": "single",
        "hold_duration_ms": 1.0,
    },
    "Slow Auto-Farmer (1 Click / 30s)": {
        "use_cps_mode": False,
        "interval_hours": 0,
        "interval_mins": 0,
        "interval_secs": 30,
        "interval_ms": 0,
        "jitter_enabled": True,
        "jitter_ms": 2000.0,
        "coord_jitter_px": 8,
        "button": "left",
    },
}


class ConfigManager:
    """Manages saving, loading, and merging settings."""

    def __init__(self, config_path: str = "autoclicker_config.json"):
        self.config_path = config_path
        self.config: Dict[str, Any] = dict(DEFAULT_CONFIG)
        self.load()

    def load(self) -> Dict[str, Any]:
        """Load configuration from disk, falling back to defaults."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.config.update(data)
            except Exception:
                pass
        return self.config

    def save(self):
        """Persist current configuration to disk."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    def apply_preset(self, preset_name: str) -> Dict[str, Any]:
        """Apply a predefined preset to current configuration."""
        if preset_name in PRESETS:
            self.config.update(PRESETS[preset_name])
            self.save()
        return self.config
