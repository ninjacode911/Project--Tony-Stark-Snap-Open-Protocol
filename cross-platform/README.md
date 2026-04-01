# Snap Autopilot — Cross-Platform Edition

This is the cross-platform version of Tony Stark Snap Autopilot. It works on **Windows**, **macOS**, and **Linux**.

See the [main README](../README.md) for full project documentation.

---

## Platform Differences

### Launcher

| Platform | How Programs Launch | Path Format |
|----------|-------------------|-------------|
| **Windows** | `subprocess.Popen` with `DETACHED_PROCESS` | `C:\Program Files\App\app.exe` |
| **macOS** | `open -a` for `.app` bundles, direct exec for binaries | `/Applications/App.app` or command name |
| **Linux** | `subprocess.Popen` with `start_new_session` | `/usr/bin/app` or command name |

### Startup Registration

| Platform | Method | Location |
|----------|--------|----------|
| **Windows** | VBScript in startup folder | `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\` |
| **macOS** | LaunchAgent plist | `~/Library/LaunchAgents/com.starksnap.autopilot.plist` |
| **Linux** | XDG autostart .desktop file | `~/.config/autostart/snap-autopilot.desktop` |

### Path Resolution

The launcher resolves program paths in this order:
1. Check if the path exists as an absolute/relative file path
2. Look up the name on system PATH (e.g., `spotify`, `brave-browser`)
3. macOS only: resolve bare name to `/Applications/<name>.app`

This means on Linux/macOS you can use just the command name (e.g., `spotify`) instead of the full path.

---

## Config Examples by Platform

### Windows

```json
{
    "programs": [
        {"name": "Brave", "path": "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"},
        {"name": "Spotify", "path": "C:\\Users\\<YourUsername>\\AppData\\Local\\Microsoft\\WindowsApps\\Spotify.exe"},
        {"name": "VS Code", "path": "C:\\Users\\<YourUsername>\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"}
    ]
}
```

### macOS

```json
{
    "programs": [
        {"name": "Brave", "path": "/Applications/Brave Browser.app"},
        {"name": "Spotify", "path": "/Applications/Spotify.app"},
        {"name": "VS Code", "path": "/Applications/Visual Studio Code.app"}
    ]
}
```

### Linux

```json
{
    "programs": [
        {"name": "Brave", "path": "brave-browser"},
        {"name": "Spotify", "path": "spotify"},
        {"name": "VS Code", "path": "code"}
    ]
}
```

---

## Platform-Specific Notes

### macOS

- **Microphone permission required.** On first run, macOS will prompt you to grant microphone access. If running via startup, grant access to Terminal or Python in: `System Settings > Privacy & Security > Microphone`
- **PortAudio required.** Install via Homebrew: `brew install portaudio`
- Startup logs are written to `/tmp/snap-autopilot.log`

### Linux

- **PulseAudio or PipeWire required.** Most desktop distros include one of these.
- **PortAudio required.** Install via your package manager:
  - Ubuntu/Debian: `sudo apt install libportaudio2 python3-dev`
  - Fedora: `sudo dnf install portaudio`
  - Arch: `sudo pacman -S portaudio`
- **System tray** requires AppIndicator support. Install if missing:
  - Ubuntu/Debian: `sudo apt install gir1.2-ayatanaappindicator3-0.1`
  - Fedora: `sudo dnf install libayatana-appindicator-gtk3`
- Autostart works with GNOME, KDE, MATE, XFCE, and any XDG-compliant desktop.

### Windows

- Works out of the box. No additional system dependencies needed.
- PortAudio is bundled with the `sounddevice` pip package on Windows.
