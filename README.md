# ⚡ AutoClicker Reimagined

<div align="center">

[![C#](https://img.shields.io/badge/C%23-10.0-239120?style=for-the-badge&logo=c-sharp&logoColor=white)](https://docs.microsoft.com/en-us/dotnet/csharp/)
[![WPF .NET 6](https://img.shields.io/badge/.NET%206.0-WPF-512BD4?style=for-the-badge&logo=dotnet&logoColor=white)](https://dotnet.microsoft.com)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-10B981?style=for-the-badge)](LICENSE)
[![Release](https://img.shields.io/badge/Release-v2.0.0%20Standalone%20EXE-00E5FF?style=for-the-badge)](dist/AutoClicker.exe)
[![Speed](https://img.shields.io/badge/Speed-1%20to%201000%2B%20CPS-EF4444?style=for-the-badge)](https://github.com)

**A high-performance C# / WPF Windows auto clicker featuring true Alt-Tab background inactive window clicking.**  
*Inspired by the clean architecture of [oriash93/AutoClicker](https://github.com/oriash93/AutoClicker), but built with the #1 most requested feature: autoclicking inactive background games (Roblox, Minecraft, etc.) without stealing your mouse cursor or focus.*

[Download Standalone EXE](#-quick-start--installation) • [Key Improvements](#-key-improvements-over-oriash93autoclicker) • [Feature Comparison](#-feature-comparison) • [Roblox & Discord Guide](#-how-to-autoclick-roblox-while-chatting-in-discord) • [Architecture](#-project-architecture)

</div>

---

## 🌟 Why AutoClicker Reimagined?

The classic [oriash93/AutoClicker](https://github.com/oriash93/AutoClicker) is one of GitHub's most respected C# WPF autoclickers due to its clean native UI and lightweight design. However, like OP Auto Clicker, it suffers from a fundamental limitation: **it hijacks your physical mouse cursor and requires the game window to stay active in the foreground**.

If you Alt-Tab away to Discord, chat with friends, or watch YouTube, you can't keep autoclicking.

**AutoClicker Reimagined solves this natively in C# & WPF:**
- 👻 **True Alt-Tab Background Inactive Clicking**: Posts low-level Win32 messages (`WM_LBUTTONDOWN` / `WM_LBUTTONUP`) directly into the target application's message queue. **Your mouse cursor stays 100% free**, and focus is never stolen.
- 🎯 **Interactive Crosshair Target Picker**: Point-and-click target finder that inspects windows under your cursor in real time via a non-intrusive HUD and global mouse hook.
- ⚡ **Native Multimedia Timer Engine (`winmm`)**: High-precision timer (`timeBeginPeriod(1)`) eliminating Windows' notorious 15.6ms thread sleep quantization, enabling stable 1 to 1000+ CPS.
- 🛡️ **Anti-Detection & Humanizer Shield**: Gaussian interval jitter (± ms) and coordinate scatter radius (± px) to bypass in-game anti-AFK kicks and bot detection heuristics.
- 📊 **Real-time Sliding CPS Meter**: Live sub-second click rate monitor, total click counter, and running stopwatch.
- 🎨 **Modern Windows 11 Fluent Dark UI**: Built with custom WPF styles, rounded corners, clean contrast, and zero external runtime dependencies.

---

## 📊 Feature Comparison

| Feature | OP Auto Clicker 3.0 | [oriash93/AutoClicker](https://github.com/oriash93/AutoClicker) | **AutoClicker Reimagined** |
| :--- | :---: | :---: | :---: |
| **Technology** | C++ / Win32 (Ancient) | C# / WPF (.NET Framework) | **C# / WPF (.NET 6 Modern)** |
| **Alt-Tab Inactive Background Clicking** | ❌ No | ❌ No | **✅ Yes (Native Win32 PostMessage)** |
| **Mouse Free While Autoclicking** | ❌ No (Cursor Hijacked) | ❌ No (Cursor Hijacked) | **✅ Yes (Cursor 100% Free)** |
| **Target Window & Point Picker** | ❌ No | ❌ No | **✅ Yes (Interactive HUD + `F7`)** |
| **Anti-AFK & Anti-Bot Jitter** | ❌ No | ❌ No | **✅ Yes (Delay + Radius Gaussian)** |
| **Live Sliding CPS Meter** | ❌ No | ❌ No | **✅ Yes (Sub-second precision)** |
| **Multimedia Timer (`timeBeginPeriod`)** | ❌ No | ⚠️ Basic Sleep | **✅ 1ms Windows Kernel Timer** |
| **Sound Cues on Start/Stop/Pick** | ❌ No | ❌ No | **✅ Yes (Non-blocking audio)** |
| **Single-File Self-Contained Binary** | ⚠️ Standalone C++ | ⚠️ Needs .NET Framework | **✅ Single-File Native `.exe`** |

---

## 🕹️ How to Autoclick Roblox While Chatting in Discord

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

1. **Open Roblox** (or any game/window) and position your character.
2. In AutoClicker Reimagined, click **`🎯 Interactive Target Window & Point Picker`** (or press **`F7`**):
   - A floating cyber HUD appears at the top of your screen showing the window and coordinates under your cursor in real time.
   - Simply hover over the exact spot inside Roblox you want to click and **Left-Click** once.
   - The window (`[RobloxPlayerBeta] Roblox`) and client coordinates `(X, Y)` are locked automatically!
3. Press **`F6`** (or click `▶ START`):
   - Switch to **Discord**, write code, watch YouTube, or browse the web.
   - Roblox continues clicking in the background without interruptions!

---

## 🚀 Quick Start & Installation

### Option 1: Standalone Single-File Executable (Recommended)
1. Download **`AutoClicker.exe`** from [`dist/AutoClicker.exe`](dist/AutoClicker.exe) or the GitHub Releases tab.
2. Double-click to run. No installation or separate .NET runtime required!

### Option 2: Build from Source (.NET 6 SDK)
```bash
# 1. Clone this repository
git clone https://github.com/your-username/AutoClicker-Reimagined.git
cd AutoClicker-Reimagined

# 2. Build Release solution
dotnet build AutoClicker.sln -c Release

# 3. Publish single-file standalone executable
dotnet publish src/AutoClicker/AutoClicker.csproj -c Release -r win-x64 -p:PublishSingleFile=true --self-contained true -o dist/
```
*Or simply run `build.bat` in Windows Explorer.*

---

## ⌨️ Global Hotkeys

| Hotkey | Action | Description |
| :---: | :---: | :--- |
| **`F6`** | **Start / Stop Toggle** | Starts or stops the autoclicker globally from any game or application. |
| **`F7`** | **Target Picker** | Opens the live crosshair target picker HUD to lock onto any window. |
| **`ESC`** | **Cancel Picker** | Exits the target picker overlay without changing coordinates. |

---

## 📁 Project Architecture

```
AutoClicker/
├── AutoClicker.sln                  # Visual Studio / .NET 6 Solution File
├── src/
│   └── AutoClicker/
│       ├── AutoClicker.csproj       # WPF Project configuration
│       ├── App.xaml                 # Application lifecycle & styles resource dictionary
│       ├── App.xaml.cs
│       ├── MainWindow.xaml          # Modern Fluent Dark WPF user interface
│       ├── MainWindow.xaml.cs       # UI logic, global hotkey hooks, and event handlers
│       ├── Interop/
│       │   └── Win32.cs             # P/Invoke signatures (PostMessage, RegisterHotKey, timeBeginPeriod)
│       ├── Core/
│       │   ├── ClickEngine.cs       # High-precision multithreaded click execution loop
│       │   └── WindowManager.cs     # Window enumeration, child HWND detection, coord mapping
│       ├── Models/
│       │   ├── ClickSettings.cs     # Settings model, interval math, and presets
│       │   └── WindowInfo.cs        # Process & window metadata
│       ├── UI/
│       │   ├── TargetPickerWindow.xaml    # Floating cyber crosshair overlay HUD
│       │   └── TargetPickerWindow.xaml.cs # Low-level mouse hook for screen capture
│       └── Resources/
│           ├── Styles.xaml          # Modern Dark WPF controls (Buttons, GroupBoxes, Sliders)
│           └── app.ico              # High-res application icon
├── dist/
│   └── AutoClicker.exe              # Ready-to-use compiled standalone binary
├── build.bat                        # One-click Windows compile & publish script
├── LICENSE                          # MIT Open Source License
└── README.md                        # Documentation & guides
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
