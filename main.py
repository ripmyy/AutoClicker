"""
AutoClicker Reimagined
----------------------
A modern, ultra-high-speed auto clicker for Windows featuring true Alt-Tab background
window clicking, anti-detection humanizer jitter, sliding CPS monitoring, and custom hotkeys.

Author: GitHub Open Source Community
License: MIT
"""

import sys
import os

# Ensure root directory is on Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autoclicker.gui.app import AutoClickerApp


def main():
    try:
        app = AutoClickerApp()
        app.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                f"An unexpected error occurred:\n\n{str(e)}\n\nCheck terminal or logs.",
                "AutoClicker Reimagined - Error",
                0x10  # MB_ICONERROR
            )
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
