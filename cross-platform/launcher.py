"""Cross-platform program launcher.

Handles platform-specific launch mechanics:
- Windows: subprocess with DETACHED_PROCESS flag
- macOS:   'open -a' for .app bundles, direct exec for binaries
- Linux:   direct subprocess execution
"""

import json
import platform
import shutil
import subprocess
from pathlib import Path
from dataclasses import dataclass


CONFIG_PATH = Path(__file__).parent / "config.json"
SYSTEM = platform.system()


@dataclass
class Program:
    name: str
    path: str


def load_programs(config_path: Path = CONFIG_PATH) -> list[Program]:
    """Load program list from config.json."""
    with open(config_path, encoding="utf-8") as f:
        data = json.load(f)
    return [Program(name=p["name"], path=p["path"]) for p in data["programs"]]


def _resolve_path(path_str: str) -> str | None:
    """Resolve a program path, checking existence or PATH lookup.

    Supports:
    - Absolute paths:   /Applications/Spotify.app, C:\\Program Files\\...
    - Command names:    brave-browser, spotify (looked up via PATH)
    - macOS app names:  Spotify (resolved to /Applications/Spotify.app)
    """
    path = Path(path_str)

    # Absolute or relative path that exists on disk
    if path.exists():
        return str(path)

    # Try looking up as a command on PATH (Linux/macOS)
    found = shutil.which(path_str)
    if found:
        return found

    # macOS: try resolving bare app name to /Applications/<name>.app
    if SYSTEM == "Darwin" and not path_str.endswith(".app"):
        app_path = Path(f"/Applications/{path_str}.app")
        if app_path.exists():
            return str(app_path)

    return None


def _launch_one(program: Program) -> str:
    """Launch a single program. Returns a status message."""
    resolved = _resolve_path(program.path)

    if resolved is None:
        return f"  [SKIP] {program.name} -- not found: {program.path}"

    try:
        if SYSTEM == "Windows":
            subprocess.Popen(
                [resolved],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.DETACHED_PROCESS,
            )

        elif SYSTEM == "Darwin":
            # macOS: use 'open -a' for .app bundles
            if resolved.endswith(".app"):
                subprocess.Popen(
                    ["open", "-a", resolved],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                subprocess.Popen(
                    [resolved],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )

        else:
            # Linux and other Unix-like systems
            subprocess.Popen(
                [resolved],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

        return f"  [OK]   {program.name}"

    except OSError as e:
        return f"  [FAIL] {program.name} -- {e}"


def launch_all(programs: list[Program] | None = None) -> list[str]:
    """Launch all configured programs. Returns list of status messages."""
    if programs is None:
        programs = load_programs()
    return [_launch_one(prog) for prog in programs]
