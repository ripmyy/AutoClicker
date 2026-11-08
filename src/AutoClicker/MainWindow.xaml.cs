using System;
using System.Collections.Generic;
using System.Media;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Interop;
using System.Windows.Media;
using AutoClicker.Core;
using AutoClicker.Interop;
using AutoClicker.Models;
using AutoClicker.UI;

namespace AutoClicker
{
    public partial class MainWindow : Window
    {
        private readonly ClickEngine _engine = new();
        private IntPtr _windowHandle = IntPtr.Zero;
        private List<WindowInfo> _windows = new();
        private IntPtr _currentTargetHwnd = IntPtr.Zero;

        private const int HOTKEY_ID_TOGGLE = 9001;
        private const int HOTKEY_ID_PICK = 9002;

        public MainWindow()
        {
            InitializeComponent();

            Loaded += OnMainWindowLoaded;
            Closed += OnMainWindowClosed;

            _engine.OnStatsUpdated += OnEngineStatsUpdated;
            _engine.OnStateChanged += OnEngineStateChanged;
        }

        private void OnMainWindowLoaded(object sender, RoutedEventArgs e)
        {
            _windowHandle = new WindowInteropHelper(this).Handle;
            var source = HwndSource.FromHwnd(_windowHandle);
            source?.AddHook(HwndHook);

            // Register default global hotkeys F6 (toggle) and F7 (picker)
            RegisterHotkeys();

            RefreshActiveWindows();
        }

        private void OnMainWindowClosed(object? sender, EventArgs e)
        {
            _engine.Stop("Window Closed");
            UnregisterHotkeys();
        }

        private void RegisterHotkeys()
        {
            // VK_F6 = 0x75, VK_F7 = 0x76
            Win32.RegisterHotKey(_windowHandle, HOTKEY_ID_TOGGLE, Win32.MOD_NOREPEAT, 0x75);
            Win32.RegisterHotKey(_windowHandle, HOTKEY_ID_PICK, Win32.MOD_NOREPEAT, 0x76);
        }

        private void UnregisterHotkeys()
        {
            Win32.UnregisterHotKey(_windowHandle, HOTKEY_ID_TOGGLE);
            Win32.UnregisterHotKey(_windowHandle, HOTKEY_ID_PICK);
        }

        private IntPtr HwndHook(IntPtr hwnd, int msg, IntPtr wParam, IntPtr lParam, ref bool handled)
        {
            if (msg == Win32.WM_HOTKEY)
            {
                int id = wParam.ToInt32();
                if (id == HOTKEY_ID_TOGGLE)
                {
                    OnBtnStartStopClicked(this, new RoutedEventArgs());
                    handled = true;
                }
                else if (id == HOTKEY_ID_PICK)
                {
                    OnBtnPickTargetClicked(this, new RoutedEventArgs());
                    handled = true;
                }
            }
            return IntPtr.Zero;
        }

        private void RefreshActiveWindows()
        {
            _windows = WindowManager.GetActiveWindows();
            CmbActiveWindows.Items.Clear();

            foreach (var win in _windows)
            {
                CmbActiveWindows.Items.Add(win);
            }

            if (_windows.Count > 0 && _currentTargetHwnd == IntPtr.Zero)
            {
                CmbActiveWindows.SelectedIndex = 0;
            }
        }

        private void OnWindowSelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (CmbActiveWindows.SelectedItem is WindowInfo win)
            {
                _currentTargetHwnd = win.Handle;
                UpdateTargetSummary(win.DisplayText, int.TryParse(TxtCoordX.Text, out int x) ? x : 0, int.TryParse(TxtCoordY.Text, out int y) ? y : 0);
            }
        }

        private void UpdateTargetSummary(string windowTitle, int x, int y)
        {
            TxtTargetSummary.Text = $"Target: {windowTitle} | Pos: ({x}, {y})";
        }

        private void OnBtnPickTargetClicked(object sender, RoutedEventArgs e)
        {
            var picker = new TargetPickerWindow { Owner = this };
            picker.ShowDialog();

            if (picker.PickedSuccessfully)
            {
                _currentTargetHwnd = picker.CapturedHwnd;
                TxtCoordX.Text = picker.CapturedClientX.ToString();
                TxtCoordY.Text = picker.CapturedClientY.ToString();

                string desc = $"[{picker.CapturedProcess}] {picker.CapturedTitle}";
                UpdateTargetSummary(desc, picker.CapturedClientX, picker.CapturedClientY);

                RadioModeBackground.IsChecked = true;

                // Select matching window in combo if present
                for (int i = 0; i < CmbActiveWindows.Items.Count; i++)
                {
                    if (CmbActiveWindows.Items[i] is WindowInfo w && w.Handle == _currentTargetHwnd)
                    {
                        CmbActiveWindows.SelectedIndex = i;
                        break;
                    }
                }
            }
        }

        private void OnBtnRefreshWindowsClicked(object sender, RoutedEventArgs e)
        {
            RefreshActiveWindows();
        }

        private void OnBtnCenterWindowClicked(object sender, RoutedEventArgs e)
        {
            if (_currentTargetHwnd != IntPtr.Zero && Win32.GetClientRect(_currentTargetHwnd, out Win32.RECT rect))
            {
                int cx = rect.Width / 2;
                int cy = rect.Height / 2;
                TxtCoordX.Text = cx.ToString();
                TxtCoordY.Text = cy.ToString();
                UpdateTargetSummary(TxtTargetSummary.Text.Split('|')[0].Trim(), cx, cy);
            }
        }

        private void OnBtnTestClickClicked(object sender, RoutedEventArgs e)
        {
            if (_currentTargetHwnd == IntPtr.Zero || !Win32.IsWindow(_currentTargetHwnd))
            {
                MessageBox.Show("Please pick or select a valid target window first!", "Target Required", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            int.TryParse(TxtCoordX.Text, out int x);
            int.TryParse(TxtCoordY.Text, out int y);

            IntPtr lParam = Win32.MakeLParam(x, y);
            Win32.PostMessage(_currentTargetHwnd, Win32.WM_MOUSEMOVE, IntPtr.Zero, lParam);
            Win32.PostMessage(_currentTargetHwnd, Win32.WM_LBUTTONDOWN, (IntPtr)Win32.MK_LBUTTON, lParam);
            Win32.PostMessage(_currentTargetHwnd, Win32.WM_LBUTTONUP, IntPtr.Zero, lParam);

            if (ChkAudio.IsChecked == true)
            {
                try { SystemSounds.Asterisk.Play(); } catch { }
            }

            TxtTargetSummary.Text = $"✅ Sent test click to target at ({x}, {y})!";
        }

        private ClickSettings BuildSettings()
        {
            var s = new ClickSettings
            {
                Mode = RadioModeBackground.IsChecked == true ? TargetingMode.BackgroundWindow :
                       (RadioModeCursor.IsChecked == true ? TargetingMode.CurrentCursor : TargetingMode.FixedScreen),
                TargetHwnd = _currentTargetHwnd,
                TargetX = int.TryParse(TxtCoordX.Text, out int tx) ? tx : 100,
                TargetY = int.TryParse(TxtCoordY.Text, out int ty) ? ty : 100,

                Button = (MouseButtonType)CmbMouseButton.SelectedIndex,
                Type = (ClickType)CmbClickType.SelectedIndex,
                HoldDurationMs = double.TryParse(TxtHoldMs.Text, out double hold) ? hold : 15.0,

                UseCpsMode = ChkCpsMode.IsChecked == true,
                Cps = SliderCps.Value,

                Hours = int.TryParse(TxtHours.Text, out int h) ? h : 0,
                Minutes = int.TryParse(TxtMins.Text, out int m) ? m : 0,
                Seconds = int.TryParse(TxtSecs.Text, out int sec) ? sec : 0,
                Milliseconds = int.TryParse(TxtMs.Text, out int ms) ? ms : 100,

                JitterEnabled = ChkJitter.IsChecked == true,
                JitterMilliseconds = double.TryParse(TxtJitterMs.Text, out double jms) ? jms : 15.0,
                JitterPixels = int.TryParse(TxtJitterPx.Text, out int jpx) ? jpx : 3,

                Repeat = RadioRepeatCount.IsChecked == true ? RepeatMode.CountLimit : RepeatMode.UntilStopped,
                MaxClicks = int.TryParse(TxtRepeatCount.Text, out int mc) ? mc : 1000,

                PlayAudio = ChkAudio.IsChecked == true,
                TopMost = ChkTopMost.IsChecked == true
            };
            return s;
        }

        private void OnBtnStartStopClicked(object sender, RoutedEventArgs e)
        {
            if (_engine.IsRunning)
            {
                _engine.Stop("User Clicked Stop");
                if (ChkAudio.IsChecked == true)
                {
                    try { SystemSounds.Beep.Play(); } catch { }
                }
            }
            else
            {
                var settings = BuildSettings();
                if (settings.Mode == TargetingMode.BackgroundWindow && (settings.TargetHwnd == IntPtr.Zero || !Win32.IsWindow(settings.TargetHwnd)))
                {
                    MessageBox.Show("Please pick or select a valid target window for background clicking!", "Target Required", MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }

                _engine.Start(settings);
                if (ChkAudio.IsChecked == true)
                {
                    try { SystemSounds.Asterisk.Play(); } catch { }
                }
            }
        }

        private void OnEngineStateChanged(bool isRunning, string reason)
        {
            Dispatcher.Invoke(() =>
            {
                if (isRunning)
                {
                    BadgeStatus.Background = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#065F46"));
                    TxtStatus.Text = "● CLICKING...";
                    TxtStatus.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#34D399"));

                    BtnStartStop.Content = "⏹ STOP (F6)";
                    BtnStartStop.Background = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#EF4444"));
                }
                else
                {
                    BadgeStatus.Background = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#334155"));
                    TxtStatus.Text = "● STOPPED";
                    TxtStatus.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#94A3B8"));

                    BtnStartStop.Content = "▶ START (F6)";
                    BtnStartStop.Background = new SolidColorBrush((Color)ColorConverter.ConvertFromString("#10B981"));
                }
            });
        }

        private void OnEngineStatsUpdated(long totalClicks, double currentCps, TimeSpan elapsed)
        {
            Dispatcher.Invoke(() =>
            {
                TxtMetricClicks.Text = $"Clicks: {totalClicks:N0}";
                TxtMetricCps.Text = $"Speed: {currentCps:F1} CPS";
                TxtMetricTime.Text = $"Time: {elapsed:hh\\:mm\\:ss}";
            });
        }

        private void OnCpsSliderChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            if (TxtSpeedLabel != null)
            {
                double cps = SliderCps.Value;
                double interval = 1000.0 / Math.Max(0.1, cps);
                TxtSpeedLabel.Text = $"Speed: {cps:F1} CPS ({interval:F1} ms interval)";
            }
        }

        private void OnQuickCpsClicked(object sender, RoutedEventArgs e)
        {
            if (sender is Button btn && double.TryParse(btn.Content.ToString(), out double val))
            {
                SliderCps.Value = val;
            }
        }

        private void OnCpsModeChanged(object sender, RoutedEventArgs e)
        {
            if (PanelCps != null && PanelInterval != null)
            {
                bool isCps = ChkCpsMode.IsChecked == true;
                PanelCps.Visibility = isCps ? Visibility.Visible : Visibility.Collapsed;
                PanelInterval.Visibility = isCps ? Visibility.Collapsed : Visibility.Visible;
            }
        }

        private void OnTargetModeChanged(object sender, RoutedEventArgs e)
        {
            // UI visibility tweaks if needed
        }

        private void OnTopMostChanged(object sender, RoutedEventArgs e)
        {
            Topmost = ChkTopMost.IsChecked == true;
        }
    }
}
