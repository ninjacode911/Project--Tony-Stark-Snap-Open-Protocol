"""Cross-platform startup registration.

Handles auto-start on login for:
- Windows:  VBScript in shell:startup folder (silent, no console flash)
- macOS:    LaunchAgent plist in ~/Library/LaunchAgents/
- Linux:    .desktop file in ~/.config/autostart/
"""

import os
import sys
import stat
import argparse
import platform
from pathlib import Path


SYSTEM = platform.system()
APP_ID = "com.starksnap.autopilot"
APP_NAME = "Snap Autopilot"
MAIN_SCRIPT = Path(__file__).parent / "main.py"
PYTHON_EXE = sys.executable


# ---------------------------------------------------------------------------
#  Windows
# ---------------------------------------------------------------------------

def _win_startup_path() -> Path:
    return (
        Path(os.environ["APPDATA"])
        / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        / "SnapAutopilot.vbs"
    )


def _win_install() -> None:
    vbs_path = _win_startup_path()
    vbs_content = (
        'Set WshShell = CreateObject("WScript.Shell")\n'
        f'WshShell.Run """{PYTHON_EXE}"" ""{MAIN_SCRIPT}"" --tray", 0, False\n'
    )
    vbs_path.write_text(vbs_content, encoding="utf-8")
    print(f"  [INSTALLED] Added to Windows startup.")
    print(f"  Script: {vbs_path}")


def _win_uninstall() -> None:
    vbs_path = _win_startup_path()
    if vbs_path.exists():
        vbs_path.unlink()
        print("  [REMOVED] Removed from Windows startup.")
    else:
        print("  [INFO] Not currently in Windows startup.")


def _win_status() -> None:
    vbs_path = _win_startup_path()
    if vbs_path.exists():
        print(f"  [STATUS] Active in Windows startup.")
        print(f"  Script: {vbs_path}")
    else:
        print("  [STATUS] Not in Windows startup.")


# ---------------------------------------------------------------------------
#  macOS
# ---------------------------------------------------------------------------

def _mac_plist_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{APP_ID}.plist"


def _mac_install() -> None:
    plist_path = _mac_plist_path()
    plist_path.parent.mkdir(parents=True, exist_ok=True)

    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{APP_ID}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{PYTHON_EXE}</string>
        <string>{MAIN_SCRIPT}</string>
        <string>--tray</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/snap-autopilot.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/snap-autopilot.err</string>
</dict>
</plist>
"""
    plist_path.write_text(plist_content, encoding="utf-8")
    print(f"  [INSTALLED] Added to macOS Login Items (LaunchAgent).")
    print(f"  Plist: {plist_path}")
    print(f"  Logs:  /tmp/snap-autopilot.log")
    print()
    print("  NOTE: Grant microphone access to your Terminal or Python")
    print("        in System Settings > Privacy & Security > Microphone.")


def _mac_uninstall() -> None:
    plist_path = _mac_plist_path()
    if plist_path.exists():
        plist_path.unlink()
        print("  [REMOVED] Removed from macOS Login Items.")
    else:
        print("  [INFO] Not currently in macOS Login Items.")


def _mac_status() -> None:
    plist_path = _mac_plist_path()
    if plist_path.exists():
        print(f"  [STATUS] Active in macOS Login Items.")
        print(f"  Plist: {plist_path}")
    else:
        print("  [STATUS] Not in macOS Login Items.")


# ---------------------------------------------------------------------------
#  Linux
# ---------------------------------------------------------------------------

def _linux_desktop_path() -> Path:
    return Path.home() / ".config" / "autostart" / "snap-autopilot.desktop"


def _linux_install() -> None:
    desktop_path = _linux_desktop_path()
    desktop_path.parent.mkdir(parents=True, exist_ok=True)

    desktop_content = f"""[Desktop Entry]
Type=Application
Name={APP_NAME}
Comment=Double-snap to launch your workspace
Exec={PYTHON_EXE} {MAIN_SCRIPT} --tray
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
X-MATE-Autostart-enabled=true
X-KDE-autostart-after=panel
"""
    desktop_path.write_text(desktop_content, encoding="utf-8")
    # Make executable
    desktop_path.chmod(desktop_path.stat().st_mode | stat.S_IEXEC)
    print(f"  [INSTALLED] Added to Linux autostart.")
    print(f"  File: {desktop_path}")
    print()
    print("  NOTE: Works with GNOME, KDE, MATE, XFCE, and most")
    print("        XDG-compliant desktop environments.")


def _linux_uninstall() -> None:
    desktop_path = _linux_desktop_path()
    if desktop_path.exists():
        desktop_path.unlink()
        print("  [REMOVED] Removed from Linux autostart.")
    else:
        print("  [INFO] Not currently in Linux autostart.")


def _linux_status() -> None:
    desktop_path = _linux_desktop_path()
    if desktop_path.exists():
        print(f"  [STATUS] Active in Linux autostart.")
        print(f"  File: {desktop_path}")
    else:
        print("  [STATUS] Not in Linux autostart.")


# ---------------------------------------------------------------------------
#  Dispatch
# ---------------------------------------------------------------------------

HANDLERS = {
    "Windows": {"install": _win_install, "uninstall": _win_uninstall, "status": _win_status},
    "Darwin":  {"install": _mac_install, "uninstall": _mac_uninstall, "status": _mac_status},
    "Linux":   {"install": _linux_install, "uninstall": _linux_uninstall, "status": _linux_status},
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Manage Snap Autopilot auto-start on login"
    )
    parser.add_argument(
        "action",
        choices=["install", "uninstall", "status"],
        help="install: add to startup | uninstall: remove | status: check",
    )
    args = parser.parse_args()

    handlers = HANDLERS.get(SYSTEM)
    if handlers is None:
        print(f"  [ERROR] Unsupported platform: {SYSTEM}")
        print("  Supported: Windows, macOS, Linux")
        sys.exit(1)

    handlers[args.action]()


if __name__ == "__main__":
    main()
