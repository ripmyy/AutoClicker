# ⚡ AutoClicker Reimagined

<div align="center">

[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-10B981?style=for-the-badge)](LICENSE)
[![Release](https://img.shields.io/badge/Release-v2.0.0%20Standalone%20EXE-00E5FF?style=for-the-badge)](dist/AutoClickerReimagined.exe)
[![Speed](https://img.shields.io/badge/Speed-1%20to%201000%2B%20CPS-EF4444?style=for-the-badge)](https://github.com)

**The next-generation Windows autoclicker featuring true inactive background clicking.**  
*Autoclick Roblox, Minecraft, or idle games in the background while you chat on Discord, watch YouTube, or work.*

[Download Ready-to-Use EXE](#-quick-start--installation) • [Key Features](#-why-autoclicker-reimagined) • [Comparison](#-feature-comparison) • [How It Works](#-how-background-clicking-works) • [Roblox & Discord Guide](#-roblox--discord-background-guide)

</div>

---

## 🌟 Why AutoClicker Reimagined?

Traditional autoclickers (like OP Auto Clicker 3.0 or Speed AutoClicker) hijack your physical mouse cursor and require the target game window to remain actively focused in the foreground. If you Alt-Tab away to Discord or a browser, either the clicks stop, or worse, they click all over your active desktop.

**AutoClicker Reimagined changes the game:**
- 👻 **True Alt-Tab Background Clicking**: Posts native Win32 messages (`WM_LBUTTONDOWN` / `WM_LBUTTONUP`) directly into the target application's message queue. **Your mouse cursor stays completely free**, and focus is never stolen!
- ⚡ **Sub-Millisecond High-Precision Engine**: Powered by the Windows multimedia high-resolution timer (`timeBeginPeriod(1)`) and hybrid spin-wait sleep, eliminating the notorious 15.6ms Windows timer jitter.
- 🛡️ **Anti-Detection & Anti-AFK Humanizer Shield**: Randomizes click intervals (±ms) and coordinates (±px) so anti-bot and anti-AFK systems can never detect a robotic pattern.
- 🎯 **Interactive Crosshair Target Picker**: Point-and-click target finder that automatically detects window handles, process names, and client coordinates with a single click or `F7` hotkey.
- 🎨 **Modern Cyber-Glassmorphic GUI**: Dark mode interface designed with CustomTkinter, real-time sliding CPS graph, live stopwatch, and audio feedback.
- 📦 **Single Standalone Executable (.exe)**: Zero runtime setup required for end users. Download and double-click to run!

---

## 📊 Feature Comparison

| Feature | OP Auto Clicker 3.0 | Speed AutoClicker | **AutoClicker Reimagined** |
| :--- | :---: | :---: | :---: |
| **Alt-Tab / Background Inactive Clicking** | ❌ No | ❌ No | **✅ Yes (Stealth Win32 Messages)** |
| **Mouse Free While Autoclicking** | ❌ No (Stolen) | ❌ No (Stolen) | **✅ Yes (Completely Free)** |
| **Interactive Target Window Picker** | ❌ No | ❌ No | **✅ Yes (One-Click HUD + F7)** |
| **Anti-Detection Jitter (Delay & Radius)** | ❌ No | ⚠️ Partial | **✅ Yes (Dual Gaussian Jitter)** |
| **Real-Time Sliding CPS Meter** | ❌ No | ❌ No | **✅ Yes (Sub-second Accuracy)** |
| **Built-in Game Presets** | ❌ No | ❌ No | **✅ Yes (Roblox, Minecraft, etc.)** |
| **Modern High-DPI Cyber UI** | ❌ Ancient Win32 | ❌ Basic WinForms | **✅ High-DPI CustomTkinter Dark** |
| **Custom Audio Cues** | ❌ No | ❌ No | **✅ Yes (Start, Stop, Pick Cues)** |
| **Always-on-Top & Pinned Mode** | ⚠️ Basic | ⚠️ Basic | **✅ Yes** |

---

## 🕹️ Roblox + Discord Background Guide

Here is how you can farm an idle game or simulator on **Roblox** while actively typing on **Discord**:

```
 ┌────────────────────────────────────────┐       ┌────────────────────────────────────────┐
 │            Roblox Player               │       │           Discord / Browser            │
 │             (BACKGROUND)               │       │              (FOREGROUND)              │
 │                                        │       │                                        │
 │   🎯 Target Point: (X: 520, Y: 380)    │       │  You are freely typing, chatting,     │
 │   ⚡ AutoClicker sends Win32 Messages  │       │  or browsing videos here!             │
 │   🔄 Zero focus loss & no mouse jump   │       │  Physical mouse remains 100% yours.    │
 └────────────────────────────────────────┘       └────────────────────────────────────────┘
```

### 3-Step Setup:
1. Open **Roblox** and position your character/camera.
2. In AutoClicker Reimagined, click **`🎯 Interactive Target Window & Point Picker`** (or press **`F7`**).
   - Hover your cursor over the exact spot inside Roblox you want to click.
   - **Left-Click** once. The target window (`[RobloxPlayerBeta.exe] Roblox`) and exact coordinates are locked automatically!
3. Press **`F6`** (or click `▶ START`).
   - Switch to **Discord**, watch YouTube, or play another game.
   - Roblox continues clicking in the background without interruptions!

---

## ⚙️ How Background Clicking Works

```
           [ User Hits F6 (Global Hotkey) ]
                          │
                          ▼
             [ Click Engine Background Thread ]
                          │
       ┌──────────────────┴──────────────────┐
       ▼                                     ▼
[ Foreground Mode ]                 [ Background Mode ]
       │                                     │
   SendInput()                     Win32 Message Pipeline
   (Moves/clicks physical               PostMessageW(
    cursor on screen)                     hwnd,
                                          WM_MOUSEMOVE,
                                          WM_LBUTTONDOWN,
                                          WM_LBUTTONUP,
                                          lParam=(Y<<16)|X
                                        )
                                             │
                                             ▼
                                  Target Window Queue
                                  (No focus switch,
                                   no cursor movement)
```

1. **Direct Win32 Message Queuing**: Messages are sent directly to the HWND handle of the window client area via `PostMessageW`.
2. **Hover State Simulation**: Sends `WM_MOUSEMOVE` coordinates preceding the button down state so in-game UI buttons register hover and press events accurately.
3. **Fallback Smart Focus-Tap**: For strict direct-input / exclusive games, an optional tap-and-restore mode briefly focuses and clicks in ~8ms before restoring your active window.

---

## 🚀 Quick Start & Installation

### Option 1: Run the Standalone `.exe` (No Python Needed)
1. Head to the [`dist/`](dist/) folder or your GitHub Releases page.
2. Run **`AutoClickerReimagined.exe`**.
3. That's it! Everything is bundled into a single file.

### Option 2: Run from Python Source
Requirements: Python 3.10 or newer on Windows 10/11.

```bash
# 1. Clone this repository
git clone https://github.com/your-username/autoclicker-reimagined.git
cd autoclicker-reimagined

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the application
python main.py
```

---

## 🔨 Building the Standalone `.exe`

Want to compile the binary yourself? A pre-configured build pipeline using PyInstaller is included:

```bash
# Run the automated build script
python build_exe.py
```
*Or simply double-click `build.bat` in Windows Explorer.*

The single standalone executable will be generated at:
```
dist/AutoClickerReimagined.exe
```

---

## ⌨️ Default Hotkeys

| Hotkey | Action | Description |
| :---: | :---: | :--- |
| **`F6`** | **Start / Stop Toggle** | Starts or stops autoclicking globally from any application. |
| **`F7`** | **Target Picker** | Opens the live crosshair target picker overlay. |
| **`ESC`** | **Cancel Picker** | Exits the target picker without modifying current coordinates. |

*(All hotkeys are 100% customizable in the **Hotkeys & Settings** tab).*

---

## 🛡️ Anti-Detection & Humanizer Mode

If you are playing games with heuristic bot detection or AFK kick timers, enable the **Anti-Detection Shield**:
- **Interval Jitter (± ms)**: Breaks constant cadence by adding micro-variations to click intervals.
- **Coordinate Dispersion (± px)**: Clicks within a small natural radius instead of the exact same pixel every time.
- **Natural Hold Duration**: Simulates realistic mechanical mouse switch depression (~15-30ms) rather than instantaneous 0ms synthetic clicks.

---

## 📁 Project Architecture

```
AutoClicker Reimagined/
├── autoclicker/
│   ├── win32_api.py         # Low-level Win32 ctypes (PostMessage, SendInput, High-res timer)
│   ├── window_manager.py    # Desktop window enumeration, child detection, coord translation
│   ├── core_engine.py       # High-precision clicking loop with sliding CPS meter
│   ├── config_manager.py    # Presets system & JSON configuration persistence
│   ├── hotkey_manager.py    # Global system-wide keyboard hooks
│   ├── sound_effects.py     # Asynchronous audio cues for start/stop/pick
│   └── gui/
│       ├── app.py           # CustomTkinter dark cyber interface & live HUD
│       └── picker_overlay.py# Interactive screen HUD for window & coordinate capture
├── assets/
│   ├── icon.ico             # High-res multi-layer icon (16x16 to 256x256)
│   └── icon.png             # Application logo
├── tests/
│   └── test_core.py         # Unit & integration tests
├── build_exe.py             # PyInstaller automated packaging script
├── build.bat                # 1-click Windows compile batch script
├── main.py                  # Application entry point
├── requirements.txt         # Python package dependencies
├── LICENSE                  # MIT Open Source License
└── README.md                # Comprehensive documentation
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
