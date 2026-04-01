<div align="center">

# Tony Stark Snap Open Protocol

**Snap Your Fingers Twice — Your Entire Workspace Launches Instantly**

*Inspired by Tony Stark's iconic snap gesture. A real-time audio-powered automation tool that listens for double finger-snaps and launches your configured programs on command.*

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%2011-0078D4?style=flat&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Audio](https://img.shields.io/badge/Audio-Real--Time%20DSP-FF6F00?style=flat&logo=soundcharts&logoColor=white)](https://python-sounddevice.readthedocs.io/)
[![License](https://img.shields.io/badge/License-Source%20Available-blue.svg)](LICENSE)

</div>

---

## Overview

Tony Stark Snap Open Protocol is a hands-free workspace launcher for Windows. It uses real-time microphone audio analysis to detect the distinctive sound pattern of a double finger-snap, then automatically launches all your configured programs in one shot. Once launched, the listener shuts itself down — one snap cycle per boot, just like suiting up.

The tool runs silently in the system tray on Windows startup. No terminal, no manual clicks. You turn on your PC, snap twice, and your entire workspace is ready.

**What makes this different from typical automation launchers:**

- **Gesture-activated, not keyboard-triggered** — uses real-time audio DSP to detect physical finger snaps, not hotkeys or macros.
- **Adaptive calibration system** — built-in calibration mode lets you tune snap sensitivity to your specific microphone and environment.
- **One-shot execution** — programs launch once per boot cycle. No accidental re-triggers hours later.
- **Silent startup integration** — runs invisibly from Windows startup with a system tray icon. Zero manual steps after installation.
- **Fully configurable** — swap programs, adjust detection thresholds, and tune timing windows through a single JSON config file.

---

## Architecture

```
                     Microphone Input
                           |
                           v
              +------------------------+
              |    Audio Stream        |  44100 Hz, mono, float32
              |    (sounddevice)       |  1024-sample chunks
              +-----------+------------+
                          |
                          v
              +------------------------+
              |   Amplitude Analysis   |  Peak amplitude per chunk
              |   (numpy)             |  Threshold comparison
              +-----------+------------+
                          |
                    Above threshold?
                     /          \
                   No            Yes
                   |              |
                (ignore)          v
                      +------------------------+
                      |   Debounce Filter      |  Min 250ms between snaps
                      |   (time-based)         |  Prevents double-count
                      +-----------+------------+
                                  |
                                  v
                      +------------------------+
                      |   Pattern Matcher      |  Tracks snap pairs
                      |   (double-snap)        |  1.0s detection window
                      +-----------+------------+
                                  |
                           Double snap?
                            /        \
                          No          Yes
                          |            |
                       (reset)         v
                              +------------------------+
                              |   Program Launcher     |  subprocess.Popen
                              |   (launcher.py)        |  DETACHED_PROCESS
                              +-----------+------------+
                                          |
                                          v
                              +------------------------+
                              |   Shutdown Listener    |  One-shot execution
                              |   Tray icon -> green   |  Mission complete
                              +------------------------+
```

---

## Features

| Feature | Detail |
|---------|--------|
| **Real-Time Snap Detection** | Continuous microphone monitoring with peak amplitude analysis at 44100 Hz sample rate |
| **Double-Snap Pattern Recognition** | Detects two snaps within a configurable time window (default 1.0s) with debounce filtering |
| **One-Shot Execution** | Programs launch once per boot — listener auto-shuts down after trigger to prevent re-opens |
| **Calibration Mode** | Interactive mode that displays live amplitude values and suggests optimal threshold settings |
| **System Tray Integration** | Runs silently with an arc-reactor styled tray icon that turns green after launch |
| **Windows Startup Integration** | VBS-based silent startup script — no console window flash on boot |
| **Configurable Programs** | Add, remove, or reorder programs through a simple JSON config file |
| **Adjustable Sensitivity** | Tune threshold, snap window, debounce interval, and cooldown via config |
| **Audio Device Listing** | Built-in command to list all available microphone inputs for troubleshooting |
| **Test Launch Mode** | Launch all programs instantly without snap detection for verification |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Audio Capture** | sounddevice 0.5.5 | Real-time microphone input streaming via PortAudio backend |
| **Signal Processing** | NumPy 1.24+ | Peak amplitude calculation and threshold comparison on audio chunks |
| **System Tray** | pystray 0.19.5 | System tray icon with menu, notifications, and status indicator |
| **Icon Rendering** | Pillow 10.0+ | Generates the arc-reactor tray icon dynamically |
| **Process Management** | subprocess (stdlib) | Launches programs as detached processes independent of the listener |
| **Startup Integration** | VBScript | Silent Windows startup without console window visibility |
| **Runtime** | Python 3.12+ | Core runtime with type hints and modern syntax |

---

## Project Structure

```
Project--Tony-Stark-Snap-Open-Protocol/
├── main.py                # Entry point — CLI with calibrate, test, tray, and listen modes
├── snap_detector.py       # Audio capture engine and double-snap pattern recognition
├── launcher.py            # Program launcher with path validation and error handling
├── tray_icon.py           # System tray integration with arc-reactor icon
├── setup_startup.py       # Install/uninstall from Windows startup folder
├── config.json            # User configuration — programs list and detection tuning
├── requirements.txt       # Python dependencies
├── LICENSE                # Source Available license
├── .gitignore             # Git ignore rules
└── .gitattributes         # Line ending and binary file handling
```

---

## Quick Start

### Prerequisites

- Python 3.12 or higher — [Download](https://www.python.org/downloads/)
- Windows 10/11 with a working microphone
- A working pair of fingers

### 1. Clone and install

```bash
git clone https://github.com/ninjacode911/Project--Tony-Stark-Snap-Open-Protocol.git
cd Project--Tony-Stark-Snap-Open-Protocol
pip install -r requirements.txt
```

### 2. Configure your programs

Open `config.json` and update the program paths to match your system:

```json
{
    "programs": [
        {
            "name": "Your App",
            "path": "C:\\Path\\To\\YourApp.exe"
        }
    ]
}
```

Find your program paths using `where <program>` in Command Prompt or check the shortcut properties.

### 3. Calibrate snap detection

```bash
python main.py --calibrate
```

Snap your fingers 5-6 times. The tool displays the amplitude of each detected sound. Note the values for your snaps vs background noise, then update the `threshold` in `config.json` to sit between them.

### 4. Test it

```bash
python main.py
```

Snap twice within 1 second. All configured programs should launch. Press `Ctrl+C` to stop.

### 5. Enable auto-start on boot

```bash
python setup_startup.py install
```

From now on, the listener starts silently when Windows boots. Snap twice — workspace is ready.

To remove from startup:

```bash
python setup_startup.py uninstall
```

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `programs` | *4 apps* | Array of program objects with `name` and `path` fields |
| `threshold` | `0.3` | Minimum amplitude to register as a snap (0.0 - 1.0). Lower = more sensitive |
| `sample_rate` | `44100` | Audio sample rate in Hz. Standard CD quality |
| `chunk_size` | `1024` | Audio frames per processing chunk. Lower = faster detection, higher CPU |
| `double_snap_window` | `1.0` | Maximum seconds between two snaps to count as a double-snap |
| `min_snap_interval` | `0.25` | Minimum seconds between registered snaps (debounce filter) |
| `cooldown` | `10` | Seconds to ignore snaps after a successful launch trigger |

---

## CLI Reference

| Command | Description |
|---------|-------------|
| `python main.py` | Start the snap listener in console mode |
| `python main.py --tray` | Start with system tray icon (recommended for daily use) |
| `python main.py --calibrate` | Run calibration to tune snap threshold |
| `python main.py --test` | Launch all programs immediately without snap detection |
| `python main.py --devices` | List all available audio input devices |
| `python setup_startup.py install` | Add to Windows startup (runs silently on boot) |
| `python setup_startup.py uninstall` | Remove from Windows startup |
| `python setup_startup.py status` | Check if auto-start is currently enabled |

---

## License

**Source Available — All Rights Reserved.** See [LICENSE](LICENSE) for full terms.

The source code is publicly visible for viewing and educational purposes. Any
use in personal, commercial, or academic projects requires explicit written
permission from the author.

To request permission: navnitamrutharaj1234@gmail.com

**Author:** Navnit Amrutharaj
