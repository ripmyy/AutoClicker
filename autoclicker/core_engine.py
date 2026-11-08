"""
High-performance clicking engine for AutoClicker Reimagined.
Supports:
- True background inactive window messaging (Alt-Tab friendly)
- Ultra-precision timing with Windows multimedia timer (timeBeginPeriod)
- Sliding-window CPS measurement
- Anti-detection randomization (delay jitter + coordinate scatter)
- Dynamic stop conditions (infinite, count limit, time limit)
"""

import threading
import time
import random
from typing import Callable, Optional, Dict, Any

from .win32_api import (
    set_multimedia_timer,
    post_background_click,
    send_input_click,
    smart_focus_tap_click,
    get_cursor_pos,
    client_to_screen,
    is_window_valid,
)


class ClickEngine:
    """Thread-safe, high-precision autoclicker engine."""

    def __init__(self):
        self._is_running = False
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        # Statistics
        self.total_clicks = 0
        self.current_cps = 0.0
        self.start_time = 0.0
        self.elapsed_time = 0.0
        self._click_timestamps = []

        # Callbacks
        self.on_stats_update: Optional[Callable[[int, float, float], None]] = None
        self.on_state_change: Optional[Callable[[bool, str], None]] = None

    @property
    def is_running(self) -> bool:
        return self._is_running

    def start(self, config: Dict[str, Any]):
        """Start the clicking engine with the provided configuration dictionary."""
        if self._is_running:
            return

        self._is_running = True
        self._stop_event.clear()
        self.total_clicks = 0
        self.current_cps = 0.0
        self.start_time = time.perf_counter()
        self.elapsed_time = 0.0
        self._click_timestamps = []

        set_multimedia_timer(True)

        if self.on_state_change:
            self.on_state_change(True, "Running")

        self._thread = threading.Thread(
            target=self._run_loop, args=(config,), daemon=True, name="ClickEngineThread"
        )
        self._thread.start()

    def stop(self, reason: str = "User Stopped"):
        """Stop the clicking engine."""
        if not self._is_running:
            return

        self._is_running = False
        self._stop_event.set()

        if self._thread and self._thread.is_alive() and threading.current_thread() != self._thread:
            self._thread.join(timeout=0.4)

        set_multimedia_timer(False)

        if self.on_state_change:
            self.on_state_change(False, reason)

    def toggle(self, config: Dict[str, Any]):
        """Toggle running state."""
        if self._is_running:
            self.stop("Hot-key Toggle")
        else:
            self.start(config)

    def _run_loop(self, config: Dict[str, Any]):
        """Worker loop executing clicks with hybrid sleep/spin timing."""
        mode = config.get("mode", "background")  # "background", "cursor", "fixed_screen"
        delivery_mode = config.get("delivery_mode", "post_message")  # "post_message", "send_message", "focus_tap"
        target_hwnd = config.get("target_hwnd", 0)
        target_x = config.get("target_x", 0)
        target_y = config.get("target_y", 0)

        button = config.get("button", "left")
        click_type = config.get("click_type", "single")
        hold_ms = float(config.get("hold_duration_ms", 12.0))

        # Base Interval calculation
        if config.get("use_cps_mode", False):
            cps = max(0.1, float(config.get("cps", 10.0)))
            base_interval = 1.0 / cps
        else:
            hours = float(config.get("interval_hours", 0))
            mins = float(config.get("interval_mins", 0))
            secs = float(config.get("interval_secs", 0))
            ms = float(config.get("interval_ms", 100))
            base_interval = (hours * 3600.0) + (mins * 60.0) + secs + (ms / 1000.0)
            base_interval = max(0.001, base_interval)

        # Anti-detection jitter settings
        jitter_enabled = config.get("jitter_enabled", False)
        jitter_ms = float(config.get("jitter_ms", 0.0))
        coord_jitter_px = int(config.get("coord_jitter_px", 0))

        # Stop condition
        stop_mode = config.get("stop_mode", "infinite")  # "infinite", "count", "time"
        max_clicks = int(config.get("max_clicks", 100))
        max_time_sec = float(config.get("max_time_sec", 60.0))

        last_stats_tick = time.perf_counter()

        try:
            while not self._stop_event.is_set():
                iter_start = time.perf_counter()

                # 1. Stop condition checks
                if stop_mode == "count" and self.total_clicks >= max_clicks:
                    self.stop(f"Reached target of {max_clicks} clicks")
                    break
                elif stop_mode == "time" and (iter_start - self.start_time) >= max_time_sec:
                    self.stop(f"Elapsed target time of {max_time_sec:.1f}s")
                    break

                # 2. Check window validity in background mode
                if mode == "background":
                    if not target_hwnd or not is_window_valid(target_hwnd):
                        self.stop("Target window was closed or is invalid")
                        break

                # 3. Apply coordinate jitter if configured
                cur_x, cur_y = target_x, target_y
                if coord_jitter_px > 0 and jitter_enabled:
                    cur_x += random.randint(-coord_jitter_px, coord_jitter_px)
                    cur_y += random.randint(-coord_jitter_px, coord_jitter_px)

                # 4. Fire click based on mode
                if mode == "background":
                    if delivery_mode == "focus_tap":
                        # Convert client coords to screen coords for focus tap
                        sx, sy = client_to_screen(target_hwnd, cur_x, cur_y)
                        smart_focus_tap_click(target_hwnd, sx, sy, button, click_type, hold_ms)
                    else:
                        use_send = (delivery_mode == "send_message")
                        post_background_click(
                            target_hwnd,
                            cur_x,
                            cur_y,
                            button=button,
                            click_type=click_type,
                            hold_ms=hold_ms,
                            move_first=True,
                            use_send=use_send,
                        )
                elif mode == "fixed_screen":
                    send_input_click(button, click_type, hold_ms, cur_x, cur_y)
                else:  # "cursor"
                    send_input_click(button, click_type, hold_ms, None, None)

                # 5. Record click & update CPS sliding window
                now = time.perf_counter()
                self.total_clicks += 1
                self._click_timestamps.append(now)

                # Prune timestamps older than 1 second
                cutoff = now - 1.0
                while self._click_timestamps and self._click_timestamps[0] < cutoff:
                    self._click_timestamps.pop(0)

                self.current_cps = float(len(self._click_timestamps))
                self.elapsed_time = now - self.start_time

                # 6. Throttle UI stats update (~15-20 FPS)
                if now - last_stats_tick >= 0.05:
                    last_stats_tick = now
                    if self.on_stats_update:
                        self.on_stats_update(self.total_clicks, self.current_cps, self.elapsed_time)

                # 7. Calculate sleep duration with jitter
                cur_interval = base_interval
                if jitter_enabled and jitter_ms > 0:
                    # Random uniform jitter between -jitter_ms and +jitter_ms
                    delta = (random.uniform(-jitter_ms, jitter_ms)) / 1000.0
                    cur_interval = max(0.001, cur_interval + delta)

                # Hybrid sleep loop: coarse sleep for >2ms, fine spin-wait for precision
                target_wake_time = iter_start + cur_interval
                while not self._stop_event.is_set():
                    remaining = target_wake_time - time.perf_counter()
                    if remaining <= 0:
                        break
                    if remaining > 0.003:
                        time.sleep(remaining - 0.002)
                    # Remaining <= 3ms spins for microsecond accuracy

        finally:
            self._is_running = False
            set_multimedia_timer(False)
            if self.on_stats_update:
                self.on_stats_update(self.total_clicks, 0.0, self.elapsed_time)
