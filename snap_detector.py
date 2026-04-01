"""Snap detection engine using real-time microphone audio analysis."""

import time
import threading
from typing import Callable

import numpy as np
import sounddevice as sd


class SnapDetector:
    """Detects double finger-snap patterns from microphone input."""

    def __init__(
        self,
        threshold: float = 0.4,
        sample_rate: int = 44100,
        chunk_size: int = 1024,
        double_snap_window: float = 1.0,
        min_snap_interval: float = 0.25,
        cooldown: float = 10.0,
    ) -> None:
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.double_snap_window = double_snap_window
        self.min_snap_interval = min_snap_interval
        self.cooldown = cooldown

        self._first_snap_time: float | None = None
        self._last_snap_time: float = 0.0
        self._last_trigger_time: float = 0.0
        self._on_double_snap: Callable[[], None] | None = None
        self._on_snap: Callable[[float], None] | None = None
        self._running = False
        self._stream: sd.InputStream | None = None

    def on_double_snap(self, callback: Callable[[], None]) -> None:
        """Register a callback for when a double-snap is detected."""
        self._on_double_snap = callback

    def on_snap(self, callback: Callable[[float], None]) -> None:
        """Register a callback for individual snap events (used in calibration)."""
        self._on_snap = callback

    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info: dict,
        status: sd.CallbackFlags,
    ) -> None:
        """Process each audio chunk from the microphone."""
        if status:
            return

        peak_amplitude = np.max(np.abs(indata))
        current_time = time.time()

        if peak_amplitude < self.threshold:
            # No snap — check if first snap timed out
            if (
                self._first_snap_time is not None
                and current_time - self._first_snap_time > self.double_snap_window
            ):
                self._first_snap_time = None
            return

        # Debounce: ignore if too close to the last registered snap
        if current_time - self._last_snap_time < self.min_snap_interval:
            return

        self._last_snap_time = current_time

        # Notify calibration listener
        if self._on_snap:
            self._on_snap(float(peak_amplitude))

        # Cooldown: ignore snaps if we just triggered a launch
        if current_time - self._last_trigger_time < self.cooldown:
            return

        if self._first_snap_time is None:
            # First snap registered
            self._first_snap_time = current_time
        else:
            elapsed = current_time - self._first_snap_time
            if elapsed <= self.double_snap_window:
                # Double snap detected!
                self._first_snap_time = None
                self._last_trigger_time = current_time
                if self._on_double_snap:
                    # Run callback in a separate thread to avoid blocking audio
                    threading.Thread(
                        target=self._on_double_snap, daemon=True
                    ).start()
            else:
                # Too slow — treat this as a new first snap
                self._first_snap_time = current_time

    def start(self) -> None:
        """Start listening for snaps. Blocks until stop() is called."""
        self._running = True
        self._stream = sd.InputStream(
            callback=self._audio_callback,
            samplerate=self.sample_rate,
            channels=1,
            blocksize=self.chunk_size,
            dtype="float32",
        )
        self._stream.start()
        try:
            while self._running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self._stream.stop()
            self._stream.close()

    def start_async(self) -> threading.Thread:
        """Start listening in a background thread. Returns the thread."""
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()
        return thread

    def stop(self) -> None:
        """Stop listening for snaps."""
        self._running = False

    @staticmethod
    def list_devices() -> str:
        """List available audio input devices."""
        devices = sd.query_devices()
        lines: list[str] = []
        for i, dev in enumerate(devices):
            if dev["max_input_channels"] > 0:
                marker = " [DEFAULT]" if i == sd.default.device[0] else ""
                lines.append(f"  [{i}] {dev['name']}{marker}")
        return "\n".join(lines)
