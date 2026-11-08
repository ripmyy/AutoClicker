using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Input;
using System.Windows.Threading;
using AutoClicker.Core;
using AutoClicker.Interop;

namespace AutoClicker.UI
{
    public partial class TargetPickerWindow : Window
    {
        public bool PickedSuccessfully { get; private set; }
        public IntPtr CapturedHwnd { get; private set; }
        public int CapturedClientX { get; private set; }
        public int CapturedClientY { get; private set; }
        public string CapturedTitle { get; private set; } = string.Empty;
        public string CapturedProcess { get; private set; } = string.Empty;

        private readonly DispatcherTimer _timer;
        private IntPtr _mouseHookHandle = IntPtr.Zero;
        private LowLevelMouseProc? _mouseProc;

        private delegate IntPtr LowLevelMouseProc(int nCode, IntPtr wParam, IntPtr lParam);
        private const int WH_MOUSE_LL = 14;
        private const int WM_LBUTTONDOWN = 0x0201;

        [DllImport("user32.dll", SetLastError = true)]
        private static extern IntPtr SetWindowsHookEx(int idHook, LowLevelMouseProc lpfn, IntPtr hMod, uint dwThreadId);

        [DllImport("user32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool UnhookWindowsHookEx(IntPtr hhk);

        [DllImport("user32.dll")]
        private static extern IntPtr CallNextHookEx(IntPtr hhk, int nCode, IntPtr wParam, IntPtr lParam);

        [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern IntPtr GetModuleHandle(string? lpModuleName);

        public TargetPickerWindow()
        {
            InitializeComponent();

            Left = (SystemParameters.PrimaryScreenWidth - Width) / 2;
            Top = 25;

            _timer = new DispatcherTimer
            {
                Interval = TimeSpan.FromMilliseconds(35)
            };
            _timer.Tick += OnTimerTick;

            Loaded += OnLoaded;
            Unloaded += OnUnloaded;
            KeyDown += OnKeyDown;
        }

        private void OnLoaded(object sender, RoutedEventArgs e)
        {
            _timer.Start();
            InstallHook();
        }

        private void OnUnloaded(object sender, RoutedEventArgs e)
        {
            _timer.Stop();
            RemoveHook();
        }

        private void OnKeyDown(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Escape)
            {
                PickedSuccessfully = false;
                Close();
            }
        }

        private void OnTimerTick(object? sender, EventArgs e)
        {
            try
            {
                var target = WindowManager.ResolveWindowUnderCursor();
                string title = target.Title.Length > 25 ? target.Title[..23] + ".." : target.Title;
                TxtLiveInfo.Text = $"[{target.ProcessName}] {title} | Client: ({target.ClientX}, {target.ClientY})";
            }
            catch { }
        }

        private void InstallHook()
        {
            _mouseProc = MouseHookCallback;
            using var curProcess = Process.GetCurrentProcess();
            using var curModule = curProcess.MainModule;
            if (curModule != null)
            {
                _mouseHookHandle = SetWindowsHookEx(WH_MOUSE_LL, _mouseProc, GetModuleHandle(curModule.ModuleName), 0);
            }
        }

        private void RemoveHook()
        {
            if (_mouseHookHandle != IntPtr.Zero)
            {
                UnhookWindowsHookEx(_mouseHookHandle);
                _mouseHookHandle = IntPtr.Zero;
            }
        }

        private IntPtr MouseHookCallback(int nCode, IntPtr wParam, IntPtr lParam)
        {
            if (nCode >= 0 && wParam == (IntPtr)WM_LBUTTONDOWN)
            {
                // Capture current window & client coords
                var target = WindowManager.ResolveWindowUnderCursor();
                CapturedHwnd = target.TargetHwnd;
                CapturedClientX = target.ClientX;
                CapturedClientY = target.ClientY;
                CapturedTitle = target.Title;
                CapturedProcess = target.ProcessName;
                PickedSuccessfully = true;

                Dispatcher.BeginInvoke(new Action(() =>
                {
                    try { System.Media.SystemSounds.Asterisk.Play(); } catch { }
                    Close();
                }));
            }

            return CallNextHookEx(_mouseHookHandle, nCode, wParam, lParam);
        }
    }
}
