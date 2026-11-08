"""
Audio feedback generator for AutoClicker Reimagined.
Produces non-blocking audio cues for Start, Stop, and Target Pick events.
"""

import threading
import winsound


def _sound_worker(sound_type: str):
    try:
        if sound_type == "start":
            winsound.Beep(900, 70)
            winsound.Beep(1300, 90)
        elif sound_type == "stop":
            winsound.Beep(1100, 70)
            winsound.Beep(650, 90)
        elif sound_type == "pick":
            winsound.Beep(1500, 60)
        elif sound_type == "test":
            winsound.Beep(1000, 50)
    except Exception:
        pass


def play_cue(sound_type: str, enabled: bool = True):
    """Play audio cue asynchronously without blocking the calling thread."""
    if not enabled:
        return
    threading.Thread(target=_sound_worker, args=(sound_type,), daemon=True).start()
