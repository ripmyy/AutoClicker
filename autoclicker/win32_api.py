"""
Win32 API bindings for AutoClicker Reimagined.
Handles mouse input simulation (SendInput), background window message dispatch (PostMessage/SendMessage),
window hierarchy enumeration, DPI awareness, high-resolution multimedia timers, and coordinate translation.
"""

import ctypes
from ctypes import wintypes
import time
from typing import Tuple, Optional, Dict, Any

# Win32 DLLs
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
winmm = ctypes.windll.winmm

# --- Windows Messages & Flags ---
WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_LBUTTONDBLCLK = 0x0203
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_RBUTTONDBLCLK = 0x0206
WM_MBUTTONDOWN = 0x0207
WM_MBUTTONUP = 0x0208
WM_MBUTTONDBLCLK = 0x0209

MK_LBUTTON = 0x0001
MK_RBUTTON = 0x0002
MK_MBUTTON = 0x0010

GA_PARENT = 1
GA_ROOT = 2
GA_ROOTOWNER = 3

INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_ABSOLUTE = 0x8000

# High-DPI Awareness Constants
DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = ctypes.c_void_p(-4)

# --- Win32 Ctypes Structs ---
class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_ulonglong),
    ]

class INPUT(ctypes.Structure):
    class _I(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]
    _anonymous_ = ("_input",)
    _fields_ = [
        ("type", wintypes.DWORD),
        ("_input", _I),
    ]

# Setup function signatures
user32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]
user32.GetCursorPos.restype = wintypes.BOOL

user32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
user32.SetCursorPos.restype = wintypes.BOOL

user32.WindowFromPoint.argtypes = [POINT]
user32.WindowFromPoint.restype = wintypes.HWND

user32.ScreenToClient.argtypes = [wintypes.HWND, ctypes.POINTER(POINT)]
user32.ScreenToClient.restype = wintypes.BOOL

user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(POINT)]
user32.ClientToScreen.restype = wintypes.BOOL

user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
user32.GetWindowRect.restype = wintypes.BOOL

user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
user32.GetClientRect.restype = wintypes.BOOL

user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.PostMessageW.restype = wintypes.BOOL

user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.SendMessageW.restype = ctypes.c_longlong

user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
user32.SendInput.restype = wintypes.UINT

user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
user32.GetAncestor.restype = wintypes.HWND

user32.IsWindow.argtypes = [wintypes.HWND]
user32.IsWindow.restype = wintypes.BOOL

user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL

user32.GetForegroundWindow.restype = wintypes.HWND
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL


def enable_high_dpi_awareness():
    """Enable high-DPI scaling awareness for crisp rendering and pixel-perfect coordinate mapping."""
    try:
        user32.SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2)
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                user32.SetProcessDPIAware()
            except Exception:
                pass


def ensure_desktop_station():
    """Ensure process and current thread are attached to interactive winsta0 / default desktop."""
    try:
        hw = user32.OpenWindowStationW("winsta0", False, 0x10000000)
        if hw:
            user32.SetProcessWindowStation(hw)
            hd = user32.OpenDesktopW("default", 0, False, 0x10000000)
            if hd:
                user32.SetThreadDesktop(hd)
    except Exception:
        pass


def set_multimedia_timer(enable: bool = True):
    """Enable 1ms timer precision via Windows multimedia timer."""
    try:
        if enable:
            winmm.timeBeginPeriod(1)
        else:
            winmm.timeEndPeriod(1)
    except Exception:
        pass


def make_lparam(x: int, y: int) -> int:
    """Pack client coordinates (x, y) into a Win32 32-bit LPARAM."""
    return ((int(y) & 0xFFFF) << 16) | (int(x) & 0xFFFF)


def get_cursor_pos() -> Tuple[int, int]:
    """Get physical mouse cursor position on screen."""
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return int(pt.x), int(pt.y)


def set_cursor_pos(x: int, y: int) -> bool:
    """Set mouse cursor position on screen."""
    return bool(user32.SetCursorPos(int(x), int(y)))


def screen_to_client(hwnd: int, screen_x: int, screen_y: int) -> Tuple[int, int]:
    """Convert screen coordinates to window client coordinates."""
    pt = POINT(int(screen_x), int(screen_y))
    user32.ScreenToClient(hwnd, ctypes.byref(pt))
    return int(pt.x), int(pt.y)


def client_to_screen(hwnd: int, client_x: int, client_y: int) -> Tuple[int, int]:
    """Convert window client coordinates to screen coordinates."""
    pt = POINT(int(client_x), int(client_y))
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    return int(pt.x), int(pt.y)


def get_window_under_cursor() -> int:
    """Return the HWND directly beneath current mouse cursor."""
    x, y = get_cursor_pos()
    pt = POINT(x, y)
    return int(user32.WindowFromPoint(pt))


def get_root_window(hwnd: int) -> int:
    """Get the top-level root window handle for any child or sub-window."""
    if not hwnd:
        return 0
    root = user32.GetAncestor(hwnd, GA_ROOT)
    return int(root) if root else hwnd


def get_window_rect(hwnd: int) -> Tuple[int, int, int, int]:
    """Return window rect (left, top, right, bottom)."""
    rect = RECT()
    if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return rect.left, rect.top, rect.right, rect.bottom
    return 0, 0, 0, 0


def get_client_size(hwnd: int) -> Tuple[int, int]:
    """Return client area (width, height)."""
    rect = RECT()
    if user32.GetClientRect(hwnd, ctypes.byref(rect)):
        return rect.right - rect.left, rect.bottom - rect.top
    return 0, 0


def is_window_valid(hwnd: int) -> bool:
    """Check if window handle is valid and active."""
    return bool(user32.IsWindow(hwnd))


def get_window_info(hwnd: int) -> Dict[str, Any]:
    """Inspect window details (title, process name, PID, client size, valid state)."""
    if not hwnd or not user32.IsWindow(hwnd):
        return {"hwnd": hwnd, "valid": False, "title": "", "process": "", "pid": 0, "client_size": (0, 0)}

    length = user32.GetWindowTextLengthW(hwnd)
    title = ""
    if length > 0:
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        title = buff.value

    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    
    proc_name = "unknown"
    try:
        import psutil
        proc = psutil.Process(pid.value)
        proc_name = proc.name()
    except Exception:
        pass

    w, h = get_client_size(hwnd)
    return {
        "hwnd": hwnd,
        "valid": True,
        "title": title,
        "process": proc_name,
        "pid": pid.value,
        "client_size": (w, h),
    }


def send_input_click(button: str = "left", click_type: str = "single", hold_ms: float = 12.0, x: Optional[int] = None, y: Optional[int] = None):
    """
    Simulate standard foreground mouse click via Win32 SendInput.
    """
    if x is not None and y is not None:
        set_cursor_pos(x, y)

    btn = button.lower()
    if btn == "left":
        down_flag = MOUSEEVENTF_LEFTDOWN
        up_flag = MOUSEEVENTF_LEFTUP
    elif btn == "right":
        down_flag = MOUSEEVENTF_RIGHTDOWN
        up_flag = MOUSEEVENTF_RIGHTUP
    elif btn == "middle":
        down_flag = MOUSEEVENTF_MIDDLEDOWN
        up_flag = MOUSEEVENTF_MIDDLEUP
    else:
        down_flag = MOUSEEVENTF_LEFTDOWN
        up_flag = MOUSEEVENTF_LEFTUP

    clicks_count = 1
    if click_type == "double":
        clicks_count = 2
    elif click_type == "triple":
        clicks_count = 3

    for i in range(clicks_count):
        # Mouse Down
        inp_down = INPUT()
        inp_down.type = INPUT_MOUSE
        inp_down.mi.dwFlags = down_flag
        user32.SendInput(1, ctypes.byref(inp_down), ctypes.sizeof(INPUT))

        # Hold duration
        if hold_ms > 0:
            time.sleep(hold_ms / 1000.0)

        # Mouse Up
        inp_up = INPUT()
        inp_up.type = INPUT_MOUSE
        inp_up.mi.dwFlags = up_flag
        user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(INPUT))

        if i < clicks_count - 1:
            time.sleep(0.04)  # 40ms interval between double clicks


def post_background_click(
    hwnd: int,
    client_x: int,
    client_y: int,
    button: str = "left",
    click_type: str = "single",
    hold_ms: float = 15.0,
    move_first: bool = True,
    use_send: bool = False
) -> bool:
    """
    Post Win32 mouse messages (WM_LBUTTONDOWN / WM_LBUTTONUP) directly to an inactive or background window.
    Will NOT steal focus or move the physical cursor.
    Works seamlessly while alt-tabbed (e.g. playing Roblox while on Discord).
    """
    if not hwnd or not user32.IsWindow(hwnd):
        return False

    lParam = make_lparam(client_x, client_y)
    btn = button.lower()

    if btn == "left":
        down_msg = WM_LBUTTONDOWN
        up_msg = WM_LBUTTONUP
        dbl_msg = WM_LBUTTONDBLCLK
        wParam_down = MK_LBUTTON
    elif btn == "right":
        down_msg = WM_RBUTTONDOWN
        up_msg = WM_RBUTTONUP
        dbl_msg = WM_RBUTTONDBLCLK
        wParam_down = MK_RBUTTON
    elif btn == "middle":
        down_msg = WM_MBUTTONDOWN
        up_msg = WM_MBUTTONUP
        dbl_msg = WM_MBUTTONDBLCLK
        wParam_down = MK_MBUTTON
    else:
        down_msg = WM_LBUTTONDOWN
        up_msg = WM_LBUTTONUP
        dbl_msg = WM_LBUTTONDBLCLK
        wParam_down = MK_LBUTTON

    dispatch = user32.SendMessageW if use_send else user32.PostMessageW

    # Send WM_MOUSEMOVE first so the window's UI tracks hover/focus coordinates
    if move_first:
        dispatch(hwnd, WM_MOUSEMOVE, 0, lParam)

    clicks_count = 1
    if click_type == "double":
        clicks_count = 2
    elif click_type == "triple":
        clicks_count = 3

    for i in range(clicks_count):
        # DOWN
        msg = dbl_msg if (i == 1 and click_type == "double") else down_msg
        dispatch(hwnd, msg, wParam_down, lParam)

        # Realistic press-down hold duration
        if hold_ms > 0:
            time.sleep(hold_ms / 1000.0)

        # UP
        dispatch(hwnd, up_msg, 0, lParam)

        if i < clicks_count - 1:
            time.sleep(0.035)

    return True


def smart_focus_tap_click(
    hwnd: int,
    screen_x: int,
    screen_y: int,
    button: str = "left",
    click_type: str = "single",
    hold_ms: float = 12.0
) -> bool:
    """
    Fallback for high-privilege direct input games:
    Briefly activates target window, fires SendInput, and immediately restores previous foreground window.
    """
    if not hwnd or not user32.IsWindow(hwnd):
        return False

    prev_fg = user32.GetForegroundWindow()
    try:
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.005)
        send_input_click(button, click_type, hold_ms, screen_x, screen_y)
        time.sleep(0.005)
    finally:
        if prev_fg and prev_fg != hwnd and user32.IsWindow(prev_fg):
            user32.SetForegroundWindow(prev_fg)
    return True
