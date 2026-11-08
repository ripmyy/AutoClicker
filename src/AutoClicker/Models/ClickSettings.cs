using System;

namespace AutoClicker.Models
{
    public enum TargetingMode
    {
        CurrentCursor,
        FixedScreen,
        BackgroundWindow
    }

    public enum MouseButtonType
    {
        Left,
        Right,
        Middle
    }

    public enum ClickType
    {
        Single,
        Double,
        Triple
    }

    public enum RepeatMode
    {
        UntilStopped,
        CountLimit,
        TimeLimit
    }

    public class ClickSettings
    {
        public TargetingMode Mode { get; set; } = TargetingMode.BackgroundWindow;
        public MouseButtonType Button { get; set; } = MouseButtonType.Left;
        public ClickType Type { get; set; } = ClickType.Single;
        public RepeatMode Repeat { get; set; } = RepeatMode.UntilStopped;

        // Interval
        public int Hours { get; set; } = 0;
        public int Minutes { get; set; } = 0;
        public int Seconds { get; set; } = 0;
        public int Milliseconds { get; set; } = 100;

        public bool UseCpsMode { get; set; } = true;
        public double Cps { get; set; } = 10.0;

        public double GetIntervalMilliseconds()
        {
            if (UseCpsMode)
            {
                return 1000.0 / Math.Max(0.1, Cps);
            }
            double total = (Hours * 3600.0 + Minutes * 60.0 + Seconds) * 1000.0 + Milliseconds;
            return Math.Max(1.0, total);
        }

        // Target (Background or Fixed)
        [System.Text.Json.Serialization.JsonIgnore]
        public IntPtr TargetHwnd { get; set; } = IntPtr.Zero;
        public string TargetProcessName { get; set; } = string.Empty;
        public string TargetWindowTitle { get; set; } = string.Empty;
        public int TargetX { get; set; } = 100;
        public int TargetY { get; set; } = 100;

        // Anti-Detection & Jitter
        public bool JitterEnabled { get; set; } = false;
        public double JitterMilliseconds { get; set; } = 15.0;
        public int JitterPixels { get; set; } = 3;
        public double HoldDurationMs { get; set; } = 15.0;

        // Stop limits
        public int MaxClicks { get; set; } = 1000;
        public double MaxTimeSeconds { get; set; } = 60.0;

        // Hotkeys
        public uint ToggleKeyVk { get; set; } = 0x75; // VK_F6
        public string ToggleKeyName { get; set; } = "F6";
        public uint PickKeyVk { get; set; } = 0x76;   // VK_F7
        public string PickKeyName { get; set; } = "F7";

        // Options
        public bool PlayAudio { get; set; } = true;
        public bool TopMost { get; set; } = true;
    }
}
