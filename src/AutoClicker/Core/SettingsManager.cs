using System;
using System.IO;
using System.Text.Json;
using AutoClicker.Models;

namespace AutoClicker.Core
{
    public static class SettingsManager
    {
        private static readonly string SettingsFile = Path.Combine(
            AppDomain.CurrentDomain.BaseDirectory,
            "settings.json"
        );

        public static ClickSettings Load()
        {
            try
            {
                if (File.Exists(SettingsFile))
                {
                    string json = File.ReadAllText(SettingsFile);
                    var settings = JsonSerializer.Deserialize<ClickSettings>(json);
                    if (settings != null) return settings;
                }
            }
            catch { }

            return new ClickSettings();
        }

        public static void Save(ClickSettings settings)
        {
            try
            {
                var options = new JsonSerializerOptions { WriteIndented = true };
                string json = JsonSerializer.Serialize(settings, options);
                File.WriteAllText(SettingsFile, json);
            }
            catch { }
        }
    }
}
