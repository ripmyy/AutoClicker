using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using AutoClicker.Interop;
using AutoClicker.Models;

namespace AutoClicker.Core
{
    public static class WindowManager
    {
        public static List<WindowInfo> GetActiveWindows()
        {
            var windows = new List<WindowInfo>();

            Win32.EnumWindows((hWnd, lParam) =>
            {
                if (!Win32.IsWindowVisible(hWnd)) return true;

                int length = Win32.GetWindowTextLength(hWnd);
                if (length == 0) return true;

                var sb = new StringBuilder(length + 1);
                Win32.GetWindowText(hWnd, sb, sb.Capacity);
                string title = sb.ToString().Trim();
                if (string.IsNullOrEmpty(title)) return true;

                if (title is "Program Manager" or "Default IME" or "MSCTFIME UI" or "Settings")
                    return true;

                Win32.GetWindowThreadProcessId(hWnd, out uint pid);
                string processName = "unknown";
                try
                {
                    using var proc = Process.GetProcessById((int)pid);
                    processName = proc.ProcessName;
                }
                catch { }

                Win32.GetWindowRect(hWnd, out Win32.RECT rect);
                if (rect.Width > 60 && rect.Height > 60)
                {
                    windows.Add(new WindowInfo
                    {
                        Handle = hWnd,
                        Title = title,
                        ProcessName = processName,
                        ProcessId = pid,
                        Width = rect.Width,
                        Height = rect.Height
                    });
                }
                return true;
            }, IntPtr.Zero);

            return windows.OrderBy(w =>
            {
                string p = w.ProcessName.ToLower();
                return p.Contains("roblox") || p.Contains("minecraft") || p.Contains("discord") || p.Contains("chrome") ? 0 : 1;
            }).ThenBy(w => w.Title).ToList();
        }

        public static (IntPtr TargetHwnd, IntPtr RootHwnd, int ClientX, int ClientY, string Title, string ProcessName) ResolveWindowUnderCursor()
        {
            Win32.GetCursorPos(out Win32.POINT screenPt);
            IntPtr childHwnd = Win32.WindowFromPoint(screenPt);
            IntPtr rootHwnd = childHwnd != IntPtr.Zero ? Win32.GetAncestor(childHwnd, Win32.GA_ROOT) : IntPtr.Zero;

            IntPtr targetHwnd = childHwnd != IntPtr.Zero ? childHwnd : rootHwnd;

            Win32.POINT clientPt = screenPt;
            if (targetHwnd != IntPtr.Zero)
            {
                Win32.ScreenToClient(targetHwnd, ref clientPt);
            }

            string title = "";
            string process = "unknown";

            IntPtr queryHwnd = rootHwnd != IntPtr.Zero ? rootHwnd : targetHwnd;
            if (queryHwnd != IntPtr.Zero)
            {
                int len = Win32.GetWindowTextLength(queryHwnd);
                if (len > 0)
                {
                    var sb = new StringBuilder(len + 1);
                    Win32.GetWindowText(queryHwnd, sb, sb.Capacity);
                    title = sb.ToString();
                }

                Win32.GetWindowThreadProcessId(queryHwnd, out uint pid);
                try
                {
                    using var proc = Process.GetProcessById((int)pid);
                    process = proc.ProcessName;
                }
                catch { }
            }

            return (targetHwnd, rootHwnd, clientPt.X, clientPt.Y, title, process);
        }
    }
}
