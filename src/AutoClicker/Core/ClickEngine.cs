using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Threading;
using AutoClicker.Interop;
using AutoClicker.Models;

namespace AutoClicker.Core
{
    public class ClickEngine
    {
        private Thread? _workerThread;
        private readonly CancellationTokenSource _cts = new();
        private volatile bool _isRunning;

        public bool IsRunning => _isRunning;
        public long TotalClicks { get; private set; }
        public double CurrentCps { get; private set; }
        public TimeSpan ElapsedTime { get; private set; }

        public event Action<long, double, TimeSpan>? OnStatsUpdated;
        public event Action<bool, string>? OnStateChanged;

        private readonly Random _random = new();

        public void Start(ClickSettings settings)
        {
            if (_isRunning) return;

            _isRunning = true;
            TotalClicks = 0;
            CurrentCps = 0.0;
            ElapsedTime = TimeSpan.Zero;

            Win32.TimeBeginPeriod(1);
            OnStateChanged?.Invoke(true, "Running");

            _workerThread = new Thread(() => RunLoop(settings))
            {
                IsBackground = true,
                Priority = ThreadPriority.Highest,
                Name = "ClickEngineThread"
            };
            _workerThread.Start();
        }

        public void Stop(string reason = "Stopped")
        {
            if (!_isRunning) return;

            _isRunning = false;
            Win32.TimeEndPeriod(1);

            OnStateChanged?.Invoke(false, reason);
            OnStatsUpdated?.Invoke(TotalClicks, 0.0, ElapsedTime);
        }

        public void Toggle(ClickSettings settings)
        {
            if (_isRunning) Stop("Toggle Hotkey");
            else Start(settings);
        }

        private void RunLoop(ClickSettings settings)
        {
            var swTotal = Stopwatch.StartNew();
            var swIter = Stopwatch.StartNew();
            var clickTimes = new Queue<double>();
            long lastStatsTick = 0;

            try
            {
                while (_isRunning)
                {
                    double nowTotal = swTotal.Elapsed.TotalSeconds;
                    ElapsedTime = swTotal.Elapsed;

                    // Stop condition checks
                    if (settings.Repeat == RepeatMode.CountLimit && TotalClicks >= settings.MaxClicks)
                    {
                        Stop($"Reached limit of {settings.MaxClicks} clicks");
                        break;
                    }
                    if (settings.Repeat == RepeatMode.TimeLimit && nowTotal >= settings.MaxTimeSeconds)
                    {
                        Stop($"Elapsed {settings.MaxTimeSeconds}s time limit");
                        break;
                    }

                    // Background window validity check
                    if (settings.Mode == TargetingMode.BackgroundWindow)
                    {
                        if (settings.TargetHwnd == IntPtr.Zero || !Win32.IsWindow(settings.TargetHwnd))
                        {
                            Stop("Target window was closed or became invalid");
                            break;
                        }
                    }

                    // Calculate Coordinates with optional scatter jitter
                    int curX = settings.TargetX;
                    int curY = settings.TargetY;
                    if (settings.JitterEnabled && settings.JitterPixels > 0)
                    {
                        curX += _random.Next(-settings.JitterPixels, settings.JitterPixels + 1);
                        curY += _random.Next(-settings.JitterPixels, settings.JitterPixels + 1);
                    }

                    // Execute Click
                    if (settings.Mode == TargetingMode.BackgroundWindow)
                    {
                        ExecuteBackgroundClick(settings.TargetHwnd, curX, curY, settings.Button, settings.Type, settings.HoldDurationMs);
                    }
                    else if (settings.Mode == TargetingMode.FixedScreen)
                    {
                        Win32.SetCursorPos(curX, curY);
                        ExecuteForegroundClick(settings.Button, settings.Type, settings.HoldDurationMs);
                    }
                    else // CurrentCursor
                    {
                        ExecuteForegroundClick(settings.Button, settings.Type, settings.HoldDurationMs);
                    }

                    TotalClicks++;
                    double curTimestamp = swTotal.Elapsed.TotalSeconds;
                    clickTimes.Enqueue(curTimestamp);

                    // Maintain 1-second sliding window for accurate real-time CPS
                    while (clickTimes.Count > 0 && clickTimes.Peek() < curTimestamp - 1.0)
                    {
                        clickTimes.Dequeue();
                    }
                    CurrentCps = clickTimes.Count;

                    // Throttle UI update events (approx 20 FPS)
                    if (swTotal.ElapsedMilliseconds - lastStatsTick >= 50)
                    {
                        lastStatsTick = swTotal.ElapsedMilliseconds;
                        OnStatsUpdated?.Invoke(TotalClicks, CurrentCps, ElapsedTime);
                    }

                    // Calculate sleep delay with jitter
                    double baseIntervalMs = settings.GetIntervalMilliseconds();
                    double curIntervalMs = baseIntervalMs;
                    if (settings.JitterEnabled && settings.JitterMilliseconds > 0)
                    {
                        double jitter = (_random.NextDouble() * 2.0 - 1.0) * settings.JitterMilliseconds;
                        curIntervalMs = Math.Max(1.0, baseIntervalMs + jitter);
                    }

                    // High precision timing wait
                    long targetTick = Stopwatch.GetTimestamp() + (long)(curIntervalMs * Stopwatch.Frequency / 1000.0);
                    while (_isRunning && Stopwatch.GetTimestamp() < targetTick)
                    {
                        long remainingTicks = targetTick - Stopwatch.GetTimestamp();
                        double remainingMs = remainingTicks * 1000.0 / Stopwatch.Frequency;
                        if (remainingMs > 2.0)
                        {
                            Thread.Sleep((int)(remainingMs - 1.0));
                        }
                    }
                }
            }
            finally
            {
                _isRunning = false;
                Win32.TimeEndPeriod(1);
            }
        }

        private static void ExecuteBackgroundClick(IntPtr hWnd, int x, int y, MouseButtonType btn, ClickType type, double holdMs)
        {
            IntPtr lParam = Win32.MakeLParam(x, y);

            uint downMsg = Win32.WM_LBUTTONDOWN;
            uint upMsg = Win32.WM_LBUTTONUP;
            uint dblMsg = Win32.WM_LBUTTONDBLCLK;
            IntPtr wParamDown = (IntPtr)Win32.MK_LBUTTON;

            if (btn == MouseButtonType.Right)
            {
                downMsg = Win32.WM_RBUTTONDOWN;
                upMsg = Win32.WM_RBUTTONUP;
                dblMsg = Win32.WM_RBUTTONDBLCLK;
                wParamDown = (IntPtr)Win32.MK_RBUTTON;
            }
            else if (btn == MouseButtonType.Middle)
            {
                downMsg = Win32.WM_MBUTTONDOWN;
                upMsg = Win32.WM_MBUTTONUP;
                dblMsg = Win32.WM_MBUTTONDBLCLK;
                wParamDown = (IntPtr)Win32.MK_MBUTTON;
            }

            // Simulate mouse hover so the control detects cursor before click
            Win32.PostMessage(hWnd, Win32.WM_MOUSEMOVE, IntPtr.Zero, lParam);

            int clickCount = type == ClickType.Double ? 2 : (type == ClickType.Triple ? 3 : 1);
            for (int i = 0; i < clickCount; i++)
            {
                uint msg = (i == 1 && type == ClickType.Double) ? dblMsg : downMsg;
                Win32.PostMessage(hWnd, msg, wParamDown, lParam);

                if (holdMs > 0)
                {
                    Thread.Sleep((int)holdMs);
                }

                Win32.PostMessage(hWnd, upMsg, IntPtr.Zero, lParam);

                if (i < clickCount - 1)
                {
                    Thread.Sleep(30);
                }
            }
        }

        private static void ExecuteForegroundClick(MouseButtonType btn, ClickType type, double holdMs)
        {
            uint downFlag = Win32.MOUSEEVENTF_LEFTDOWN;
            uint upFlag = Win32.MOUSEEVENTF_LEFTUP;

            if (btn == MouseButtonType.Right)
            {
                downFlag = Win32.MOUSEEVENTF_RIGHTDOWN;
                upFlag = Win32.MOUSEEVENTF_RIGHTUP;
            }
            else if (btn == MouseButtonType.Middle)
            {
                downFlag = Win32.MOUSEEVENTF_MIDDLEDOWN;
                upFlag = Win32.MOUSEEVENTF_MIDDLEUP;
            }

            int count = type == ClickType.Double ? 2 : (type == ClickType.Triple ? 3 : 1);
            for (int i = 0; i < count; i++)
            {
                var inputDown = new Win32.INPUT
                {
                    type = Win32.INPUT_MOUSE,
                    mi = new Win32.MOUSEINPUT { dwFlags = downFlag }
                };
                Win32.SendInput(1, new[] { inputDown }, Marshal.SizeOf(typeof(Win32.INPUT)));

                if (holdMs > 0)
                {
                    Thread.Sleep((int)holdMs);
                }

                var inputUp = new Win32.INPUT
                {
                    type = Win32.INPUT_MOUSE,
                    mi = new Win32.MOUSEINPUT { dwFlags = upFlag }
                };
                Win32.SendInput(1, new[] { inputUp }, Marshal.SizeOf(typeof(Win32.INPUT)));

                if (i < count - 1)
                {
                    Thread.Sleep(30);
                }
            }
        }
    }
}
