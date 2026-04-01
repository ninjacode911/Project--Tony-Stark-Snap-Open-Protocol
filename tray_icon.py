"""System tray integration for Snap Autopilot."""

import threading

from PIL import Image, ImageDraw
import pystray

from snap_detector import SnapDetector
from launcher import load_programs, launch_all


def _create_icon_image(color: str = "#e63946") -> Image.Image:
    """Create a simple colored circle icon for the tray."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Outer ring
    draw.ellipse([4, 4, size - 4, size - 4], fill=color, outline="#1d3557", width=3)
    # Inner arc reactor glow
    draw.ellipse([20, 20, size - 20, size - 20], fill="#a8dadc")
    draw.ellipse([26, 26, size - 26, size - 26], fill="#f1faee")
    return img


def run_with_tray(config: dict) -> None:
    """Run the snap listener with a system tray icon."""
    detection = config["detection"]

    detector = SnapDetector(
        threshold=detection["threshold"],
        sample_rate=detection["sample_rate"],
        chunk_size=detection["chunk_size"],
        double_snap_window=detection["double_snap_window"],
        min_snap_interval=detection["min_snap_interval"],
        cooldown=detection["cooldown"],
    )

    icon: pystray.Icon | None = None

    def on_trigger() -> None:
        print("\n  >>> DOUBLE SNAP DETECTED! Launching workspace...")
        results = launch_all()
        for line in results:
            print(line)
        detector.stop()
        if icon:
            icon.icon = _create_icon_image(color="#2d6a4f")
            icon.title = "Stark Snap Autopilot - Launched"
            icon.notify("Workspace launched! Autopilot complete.", "Snap Autopilot")

    def on_quit(tray_icon: pystray.Icon, item: pystray.MenuItem) -> None:
        detector.stop()
        tray_icon.stop()

    detector.on_double_snap(on_trigger)

    programs = load_programs()
    program_names = ", ".join(p.name for p in programs)

    menu = pystray.Menu(
        pystray.MenuItem(f"Programs: {program_names}", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", on_quit),
    )

    icon = pystray.Icon(
        name="snap_autopilot",
        icon=_create_icon_image(),
        title="Stark Snap Autopilot - Listening",
        menu=menu,
    )

    # Start snap detector in background
    detector.start_async()

    print("  [TRAY] Running in system tray. Right-click the icon for options.")
    print("  [LISTENING] Snap twice to launch your workspace.\n")

    # pystray.Icon.run() blocks until the icon is stopped
    icon.run()
