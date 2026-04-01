"""Tony Stark Snap Autopilot — double-snap to launch your workspace.

Cross-platform: Windows, macOS, and Linux.
"""

import sys
import json
import argparse
from pathlib import Path

from snap_detector import SnapDetector
from launcher import load_programs, launch_all


CONFIG_PATH = Path(__file__).parent / "config.json"

BANNER = """
  +-----------------------------------------------------------+
  |          STARK INDUSTRIES - SNAP AUTOPILOT v1.0           |
  |          Cross-Platform Edition                           |
  |                                                           |
  |       "Sometimes you gotta run before you can walk."      |
  |                                        - Tony Stark       |
  +-----------------------------------------------------------+
"""


def load_config() -> dict:
    """Load full config from config.json."""
    if not CONFIG_PATH.exists():
        example = CONFIG_PATH.parent / "config.example.json"
        print(f"  [ERROR] config.json not found.")
        print(f"  Copy the example and edit your program paths:")
        print(f"    cp {example.name} config.json")
        sys.exit(1)

    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def print_status(config: dict) -> None:
    """Print current configuration status."""
    programs = load_programs(CONFIG_PATH)
    detection = config["detection"]

    print("\n  [PROGRAMS LOADED]")
    for prog in programs:
        exists = Path(prog.path).exists()
        status = "READY" if exists else "PATH (will resolve at launch)"
        print(f"    - {prog.name}: {status}")

    print(f"\n  [DETECTION SETTINGS]")
    print(f"    Threshold:       {detection['threshold']}")
    print(f"    Snap window:     {detection['double_snap_window']}s")
    print(f"    Cooldown:        {detection['cooldown']}s")
    print()


def run_listener(config: dict) -> None:
    """Run the main snap listener. Launches programs once, then exits."""
    detection = config["detection"]

    detector = SnapDetector(
        threshold=detection["threshold"],
        sample_rate=detection["sample_rate"],
        chunk_size=detection["chunk_size"],
        double_snap_window=detection["double_snap_window"],
        min_snap_interval=detection["min_snap_interval"],
        cooldown=detection["cooldown"],
    )

    def on_trigger() -> None:
        print("\n  >>> DOUBLE SNAP DETECTED! Launching workspace...")
        print("  >>> J.A.R.V.I.S: \"Right away, sir.\"\n")
        results = launch_all()
        for line in results:
            print(line)
        print("\n  >>> All systems online. Mission complete.")
        print("  >>> Snap Autopilot shutting down. See you next boot.\n")
        detector.stop()

    detector.on_double_snap(on_trigger)

    print("  [LISTENING] Snap twice to launch your workspace.")
    print("  [HINT]      Press Ctrl+C to stop.\n")

    detector.start()


def run_calibration(config: dict) -> None:
    """Run calibration mode to help tune snap threshold."""
    detection = config["detection"]

    print("\n  [CALIBRATION MODE]")
    print("  Snap your fingers a few times. Watch the amplitude values.")
    print("  Your threshold should be BELOW your snap amplitude")
    print("  but ABOVE your normal background noise.\n")
    print(f"  Current threshold: {detection['threshold']}")
    print("  Press Ctrl+C to stop.\n")

    peak_values: list[float] = []

    def on_snap(amplitude: float) -> None:
        peak_values.append(amplitude)
        bar_len = int(amplitude * 50)
        bar = "#" * bar_len
        print(f"  SNAP detected | amplitude: {amplitude:.4f} | {bar}")

    detector = SnapDetector(
        threshold=0.05,
        sample_rate=detection["sample_rate"],
        chunk_size=detection["chunk_size"],
        double_snap_window=detection["double_snap_window"],
        min_snap_interval=0.15,
        cooldown=999,
    )
    detector.on_snap(on_snap)

    try:
        detector.start()
    except KeyboardInterrupt:
        pass

    if peak_values:
        avg = sum(peak_values) / len(peak_values)
        print(f"\n  [RESULTS]")
        print(f"    Snaps detected:    {len(peak_values)}")
        print(f"    Average amplitude: {avg:.4f}")
        print(f"    Min amplitude:     {min(peak_values):.4f}")
        print(f"    Max amplitude:     {max(peak_values):.4f}")
        suggested = round(min(peak_values) * 0.7, 2)
        print(f"    Suggested threshold: {suggested}")
        print(f"\n  Update 'threshold' in config.json to {suggested} if needed.\n")
    else:
        print("\n  No snaps detected. Try snapping closer to the microphone.\n")


def run_test_launch() -> None:
    """Test launch all programs without snap detection."""
    print("\n  [TEST MODE] Launching all configured programs...\n")
    results = launch_all()
    for line in results:
        print(line)
    print()


def list_devices() -> None:
    """List available audio input devices."""
    print("\n  [AUDIO DEVICES]")
    print(SnapDetector.list_devices())
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tony Stark Snap Autopilot -- double-snap to launch your workspace"
    )
    parser.add_argument(
        "--calibrate", action="store_true",
        help="Run calibration mode to tune snap sensitivity",
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Test launch all programs without snap detection",
    )
    parser.add_argument(
        "--devices", action="store_true",
        help="List available audio input devices",
    )
    parser.add_argument(
        "--tray", action="store_true",
        help="Run with system tray icon (minimized)",
    )
    args = parser.parse_args()

    print(BANNER)

    if args.devices:
        list_devices()
        return

    config = load_config()

    if args.calibrate:
        run_calibration(config)
        return

    if args.test:
        run_test_launch()
        return

    if args.tray:
        try:
            from tray_icon import run_with_tray
            print_status(config)
            run_with_tray(config)
        except ImportError:
            print("  [ERROR] pystray not installed. Run: pip install pystray Pillow")
            sys.exit(1)
        return

    print_status(config)
    run_listener(config)


if __name__ == "__main__":
    main()
