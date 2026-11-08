"""
Unit and integration tests for AutoClicker Reimagined core functionality.
"""

import time
import os
import unittest

from autoclicker.win32_api import (
    make_lparam,
    get_cursor_pos,
    set_multimedia_timer,
)
from autoclicker.config_manager import ConfigManager, PRESETS
from autoclicker.core_engine import ClickEngine


class TestAutoClicker(unittest.TestCase):

    def test_make_lparam(self):
        # 100, 200 -> 0x00c80064
        lp = make_lparam(100, 200)
        self.assertEqual(lp, (200 << 16) | 100)

    def test_cursor_pos(self):
        x, y = get_cursor_pos()
        self.assertIsInstance(x, int)
        self.assertIsInstance(y, int)

    def test_config_manager(self):
        tmp_config_path = "test_config_temp.json"
        if os.path.exists(tmp_config_path):
            os.remove(tmp_config_path)

        cfg_mgr = ConfigManager(tmp_config_path)
        self.assertEqual(cfg_mgr.config.get("hotkey_toggle"), "F6")

        cfg_mgr.apply_preset("Roblox AFK Farm (Background + Anti-AFK)")
        self.assertEqual(cfg_mgr.config.get("mode"), "background")
        self.assertTrue(cfg_mgr.config.get("jitter_enabled"))

        cfg_mgr.save()
        self.assertTrue(os.path.exists(tmp_config_path))

        cfg_mgr_loaded = ConfigManager(tmp_config_path)
        self.assertEqual(cfg_mgr_loaded.config.get("cps"), 5.0)

        # Cleanup
        if os.path.exists(tmp_config_path):
            os.remove(tmp_config_path)

    def test_engine_count_limit(self):
        engine = ClickEngine()
        # Test 10 clicks in cursor mode (or background with fake hwnd)
        # Using a dummy config with stop_mode="count" and max_clicks=5
        cfg = {
            "mode": "cursor",
            "use_cps_mode": True,
            "cps": 50.0,
            "button": "left",
            "click_type": "single",
            "hold_duration_ms": 1.0,
            "stop_mode": "count",
            "max_clicks": 5,
            "jitter_enabled": False,
        }
        engine.start(cfg)
        time.sleep(0.4)
        self.assertFalse(engine.is_running)
        self.assertEqual(engine.total_clicks, 5)


if __name__ == "__main__":
    unittest.main()
