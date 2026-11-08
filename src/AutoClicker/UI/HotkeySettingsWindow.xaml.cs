using System.Windows;
using System.Windows.Input;

namespace AutoClicker.UI
{
    public partial class HotkeySettingsWindow : Window
    {
        public uint ToggleKeyVk { get; private set; }
        public string ToggleKeyName { get; private set; }
        public uint PickKeyVk { get; private set; }
        public string PickKeyName { get; private set; }

        private bool _listeningForToggle;
        private bool _listeningForPick;

        public HotkeySettingsWindow(uint currentToggleVk, string currentToggleName, uint currentPickVk, string currentPickName)
        {
            InitializeComponent();

            ToggleKeyVk = currentToggleVk;
            ToggleKeyName = currentToggleName;
            PickKeyVk = currentPickVk;
            PickKeyName = currentPickName;

            TxtToggleKey.Text = ToggleKeyName;
            TxtPickKey.Text = PickKeyName;

            PreviewKeyDown += OnWindowPreviewKeyDown;
        }

        private void OnBtnChangeToggleClicked(object sender, RoutedEventArgs e)
        {
            _listeningForToggle = true;
            _listeningForPick = false;
            TxtToggleKey.Text = "[Press any key...]";
            TxtHint.Text = "Press the key you want to use for Start / Stop.";
        }

        private void OnBtnChangePickClicked(object sender, RoutedEventArgs e)
        {
            _listeningForPick = true;
            _listeningForToggle = false;
            TxtPickKey.Text = "[Press any key...]";
            TxtHint.Text = "Press the key you want to use for Target Picker.";
        }

        private void OnWindowPreviewKeyDown(object sender, KeyEventArgs e)
        {
            if (!_listeningForToggle && !_listeningForPick) return;

            Key key = e.Key == Key.System ? e.SystemKey : e.Key;

            // Ignore standalone modifier keys
            if (key is Key.LeftCtrl or Key.RightCtrl or Key.LeftAlt or Key.RightAlt or Key.LeftShift or Key.RightShift or Key.LWin or Key.RWin)
                return;

            int vk = KeyInterop.VirtualKeyFromKey(key);
            string keyName = key.ToString();

            if (_listeningForToggle)
            {
                ToggleKeyVk = (uint)vk;
                ToggleKeyName = keyName;
                TxtToggleKey.Text = keyName;
                _listeningForToggle = false;
            }
            else if (_listeningForPick)
            {
                PickKeyVk = (uint)vk;
                PickKeyName = keyName;
                TxtPickKey.Text = keyName;
                _listeningForPick = false;
            }

            TxtHint.Text = "Key recorded successfully. Click Save to apply.";
            e.Handled = true;
        }

        private void OnBtnSaveClicked(object sender, RoutedEventArgs e)
        {
            DialogResult = true;
            Close();
        }

        private void OnBtnCancelClicked(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
            Close();
        }
    }
}
