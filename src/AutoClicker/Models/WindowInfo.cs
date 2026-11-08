using System;

namespace AutoClicker.Models
{
    public class WindowInfo
    {
        public IntPtr Handle { get; set; }
        public string Title { get; set; } = string.Empty;
        public string ProcessName { get; set; } = string.Empty;
        public uint ProcessId { get; set; }
        public int Width { get; set; }
        public int Height { get; set; }

        public string DisplayText => string.IsNullOrWhiteSpace(Title)
            ? $"[{ProcessName}] (HWND: 0x{Handle.ToInt64():X})"
            : $"[{ProcessName}] {Title}";

        public override string ToString() => DisplayText;
    }
}
