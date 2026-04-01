"""Add or remove Snap Autopilot from Windows startup."""

import sys
import argparse
from pathlib import Path


def get_startup_folder() -> Path:
    """Get the Windows startup folder path."""
    import os
    return Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def get_vbs_path() -> Path:
    """Get the path for the startup VBS script."""
    return get_startup_folder() / "SnapAutopilot.vbs"


def get_python_path() -> str:
    """Get the current Python interpreter path."""
    return sys.executable


def install() -> None:
    """Add Snap Autopilot to Windows startup (runs hidden with tray icon)."""
    main_script = Path(__file__).parent / "main.py"
    python_exe = get_python_path()
    vbs_path = get_vbs_path()

    # VBS script to run Python silently (no console window flash)
    vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """{python_exe}"" ""{main_script}"" --tray", 0, False
'''

    vbs_path.write_text(vbs_content, encoding="utf-8")
    print(f"  [INSTALLED] Snap Autopilot added to Windows startup.")
    print(f"  Script: {vbs_path}")
    print(f"  It will run silently in the system tray on next boot.\n")


def uninstall() -> None:
    """Remove Snap Autopilot from Windows startup."""
    vbs_path = get_vbs_path()
    if vbs_path.exists():
        vbs_path.unlink()
        print(f"  [REMOVED] Snap Autopilot removed from Windows startup.\n")
    else:
        print(f"  [INFO] Snap Autopilot is not in Windows startup.\n")


def status() -> None:
    """Check if Snap Autopilot is in Windows startup."""
    vbs_path = get_vbs_path()
    if vbs_path.exists():
        print(f"  [STATUS] Snap Autopilot IS in Windows startup.")
        print(f"  Script: {vbs_path}\n")
    else:
        print(f"  [STATUS] Snap Autopilot is NOT in Windows startup.\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Manage Snap Autopilot Windows startup"
    )
    parser.add_argument(
        "action",
        choices=["install", "uninstall", "status"],
        help="install: add to startup | uninstall: remove | status: check",
    )
    args = parser.parse_args()

    if args.action == "install":
        install()
    elif args.action == "uninstall":
        uninstall()
    else:
        status()


if __name__ == "__main__":
    main()
