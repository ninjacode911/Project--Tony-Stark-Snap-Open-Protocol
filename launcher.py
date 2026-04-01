"""Program launcher — opens all configured applications."""

import json
import subprocess
from pathlib import Path
from dataclasses import dataclass


CONFIG_PATH = Path(__file__).parent / "config.json"


@dataclass
class Program:
    name: str
    path: str


def load_programs(config_path: Path = CONFIG_PATH) -> list[Program]:
    """Load program list from config.json."""
    with open(config_path, encoding="utf-8") as f:
        data = json.load(f)
    return [Program(name=p["name"], path=p["path"]) for p in data["programs"]]


def launch_all(programs: list[Program] | None = None) -> list[str]:
    """Launch all configured programs. Returns list of status messages."""
    if programs is None:
        programs = load_programs()

    results: list[str] = []
    for prog in programs:
        exe = Path(prog.path)
        if not exe.exists():
            results.append(f"  [SKIP] {prog.name} — not found at {prog.path}")
            continue
        try:
            subprocess.Popen(
                [str(exe)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.DETACHED_PROCESS,
            )
            results.append(f"  [OK]   {prog.name}")
        except OSError as e:
            results.append(f"  [FAIL] {prog.name} — {e}")
    return results
