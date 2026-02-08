"""
RNG Data Collector TUI

A Textual-based TUI for collecting random number generator data.
Supports Intel RDSEED, TrueRNG, BitBabbler, and pseudo RNG.

Usage:
    uv run python rng_tui.py

Features:
- Device selection with availability check
- Configurable sample size (bits), frequency, and duration
- Real-time statistics display
- Live data table with hex preview
- CSV export with datetime and statistics
"""

import asyncio
import csv
from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ProgressBar,
    Select,
    Static,
)

# Import RNG modules
from rng_devices import intel_seed, truerng, bitbabbler_rng, pseudo_rng


# Device registry
DEVICES = {
    "intel_seed": {"name": "Intel RDSEED", "module": intel_seed, "type": "Hardware"},
    "truerng": {"name": "TrueRNG", "module": truerng, "type": "Hardware"},
    "bitbabbler_rng": {
        "name": "BitBabbler",
        "module": bitbabbler_rng,
        "type": "Hardware",
    },
    "pseudo_rng": {"name": "Pseudo RNG", "module": pseudo_rng, "type": "Software"},
}


class StatsPanel(Static):
    """Panel displaying real-time statistics."""

    current_ratio = reactive(50.0)
    running_avg = reactive(50.0)
    total_samples = reactive(0)
    elapsed_time = reactive("00:00:00")
    is_collecting = reactive(False)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("📊 Real-time Statistics", classes="title")
            yield Label("Current Ratio: 50.00%", id="current_ratio")
            yield Label("Running Avg: 50.00%", id="running_avg")
            yield Label("Total Samples: 0", id="total_samples")
            yield Label("Elapsed: 00:00:00", id="elapsed_time")
            yield ProgressBar(total=100, show_percentage=True, id="progress")

            # Buttons row within StatsPanel
            with Horizontal(classes="stats-buttons"):
                yield Button("▶ Start", id="start_btn", variant="success")
                yield Button(
                    "⏸ Pause", id="pause_btn", variant="warning", disabled=True
                )
                yield Button("■ Stop", id="stop_btn", variant="error", disabled=True)

    def watch_current_ratio(self, ratio: float):
        self.query_one("#current_ratio", Label).update(f"Current Ratio: {ratio:.2f}%")
        # Color code based on ratio quality
        if 45 <= ratio <= 55:
            self.query_one("#current_ratio").styles.color = "#00ff00"  # Green
        elif 40 <= ratio <= 60:
            self.query_one("#current_ratio").styles.color = "#ffff00"  # Yellow
        else:
            self.query_one("#current_ratio").styles.color = "#ff0000"  # Red

    def watch_running_avg(self, avg: float):
        self.query_one("#running_avg", Label).update(f"Running Avg: {avg:.2f}%")

    def watch_total_samples(self, count: int):
        self.query_one("#total_samples", Label).update(f"Total Samples: {count}")

    def watch_elapsed_time(self, time_str: str):
        self.query_one("#elapsed_time", Label).update(f"Elapsed: {time_str}")

    def update_progress(self, current: int, total: int):
        """Update progress bar for fixed duration."""
        progress = self.query_one("#progress", ProgressBar)
        if total > 0:
            progress.update(total=total, progress=current)
            progress.styles.visibility = "visible"
        else:
            progress.styles.visibility = "hidden"


class ConfigPanel(Static):
    """Panel for configuration inputs."""

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("⚙️ Configuration", classes="title")

            yield Label("Device:")
            yield Select(
                [
                    (f"{info['name']} ({info['type']})", key)
                    for key, info in DEVICES.items()
                ],
                id="device_select",
                value="pseudo_rng",
            )

            yield Label("Sample Size (bits):")
            yield Input(value="2048", id="bits_input", type="integer")

            yield Label("Frequency (seconds):")
            yield Input(value="1.0", id="freq_input", type="number")

            yield Label("Duration (seconds, 0 = infinite):")
            yield Input(value="0", id="duration_input", type="integer")

            yield Label("Folds (BitBabbler only, 0=raw):")
            yield Select(
                [(str(i), i) for i in range(5)],
                id="folds_select",
                value=0,
                disabled=True,
            )

            yield Label("Output File (auto-generated if empty):")
            yield Input(
                value="",
                id="output_input",
                placeholder="./rng_data_YYYYMMDD_HHMMSS.csv",
            )

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle device selection changes."""
        if event.select.id == "device_select":
            folds_select = self.query_one("#folds_select", Select)
            folds_select.disabled = event.value != "bitbabbler_rng"


class DataTablePanel(Static):
    """Panel displaying collected data in a table."""

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("📋 Collected Data", classes="title")
            table = DataTable(id="data_table")
            table.add_column("#", width=6)
            table.add_column("Time", width=12)
            table.add_column("Bytes", width=6)
            table.add_column("Ones", width=5)
            table.add_column("Zeros", width=5)
            table.add_column("Ratio%", width=8)
            table.add_column("Hex", width=16)
            yield table

    def add_sample(
        self,
        sample_num: int,
        timestamp: str,
        bytes_count: int,
        ones: int,
        zeros: int,
        ratio: float,
        hex_preview: str,
    ):
        """Add a sample row to the table."""
        table = self.query_one("#data_table", DataTable)
        table.add_row(
            str(sample_num),
            timestamp,
            str(bytes_count),
            str(ones),
            str(zeros),
            f"{ratio:.2f}",
            hex_preview,
        )
        # Auto-scroll to bottom
        table.scroll_end()


class RNGCollectorApp(App):
    """Main TUI application for RNG data collection."""

    CSS_PATH = "style.css"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "start", "Start"),
        ("p", "pause", "Pause"),
        ("x", "stop", "Stop"),
    ]

    def __init__(self):
        super().__init__()
        self.device_module = None
        self.device_key = None
        self.sample_bytes = 256  # 2048 bits / 8
        self.frequency = 1.0
        self.duration = 60
        self.folds = 0  # BitBabbler folding level (0-4)
        self.output_file = None
        self.is_collecting = False
        self.is_paused = False
        self.collection_task = None
        self.sample_count = 0
        self.total_ones = 0
        self.start_time = None
        self.csv_writer = None
        self.csv_file = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        # Side-by-side layout: ConfigPanel (left) + StatsPanel (right with buttons)
        with Horizontal(classes="top-container"):
            yield ConfigPanel()
            yield StatsPanel()

        # Bottom container for DataTablePanel (takes remaining space)
        with Vertical(classes="bottom-container"):
            yield DataTablePanel()

        yield Footer()

    def on_mount(self):
        """Called when app is mounted."""
        self.title = "RNG Data Collector TUI"
        self.sub_title = "Hardware & Software RNG Data Collection"

    async def on_button_pressed(self, event: Button.Pressed):
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "start_btn":
            await self.action_start()
        elif button_id == "pause_btn":
            await self.action_pause()
        elif button_id == "stop_btn":
            await self.action_stop()

    async def action_start(self):
        """Start data collection."""
        if self.is_collecting:
            return

        # Get configuration
        config = self.query_one(ConfigPanel)
        device_key = config.query_one("#device_select", Select).value
        bits_str = config.query_one("#bits_input", Input).value
        freq_str = config.query_one("#freq_input", Input).value
        duration_str = config.query_one("#duration_input", Input).value
        output_path = config.query_one("#output_input", Input).value

        # Validate and set parameters
        try:
            bits = int(bits_str)
            if bits % 8 != 0:
                self.notify("Bits must be divisible by 8", severity="error")
                return
            self.sample_bytes = bits // 8

            self.frequency = float(freq_str)
            if self.frequency <= 0:
                self.notify("Frequency must be positive", severity="error")
                return

            self.duration = int(duration_str)
            if self.duration < 0:
                self.notify("Duration must be non-negative", severity="error")
                return

            # Set device
            self.device_key = device_key
            self.device_module = DEVICES[device_key]["module"]

            # Get folds for BitBabbler
            if device_key == "bitbabbler_rng":
                self.folds = config.query_one("#folds_select", Select).value
            else:
                self.folds = 0

            # Clear any stale device references before checking
            if device_key in ("bitbabbler_rng", "intel_seed", "truerng"):
                try:
                    if device_key == "bitbabbler_rng":
                        bitbabbler_rng.close()
                        await asyncio.sleep(0.1)  # Reduced from 300ms
                    elif device_key == "intel_seed":
                        intel_seed.close()
                        await asyncio.sleep(0.05)  # Reduced from 100ms
                    elif device_key == "truerng":
                        # TrueRNG doesn't need explicit close, executor stays alive
                        pass
                except Exception:
                    pass  # Ignore errors - device might not have been opened

            # Check device availability with retry logic
            device_available = False
            error_msg = ""
            for attempt in range(3):
                try:
                    if self.device_module.is_device_available():
                        device_available = True
                        break
                except Exception as e:
                    error_msg = str(e)

                if attempt < 2:  # Don't sleep on last attempt
                    await asyncio.sleep(
                        0.2
                    )  # Reduced from 500ms for better responsiveness

            if not device_available:
                if device_key == "bitbabbler_rng":
                    self.notify(
                        f"Device {DEVICES[device_key]['name']} not available. "
                        "The USB device may be busy. Try waiting a few seconds or reconnecting.",
                        severity="error",
                    )
                elif error_msg:
                    self.notify(
                        f"Device {DEVICES[device_key]['name']} not available: {error_msg}",
                        severity="error",
                    )
                else:
                    self.notify(
                        f"Device {DEVICES[device_key]['name']} not available",
                        severity="error",
                    )
                return

            # Set output file
            if output_path:
                self.output_file = output_path
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.output_file = f"./rng_data_{timestamp}.csv"

            # Open CSV file
            self.csv_file = open(self.output_file, "w", newline="")
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(
                ["datetime", "ones", "zeros", "ratio_percent", "sample_bytes", "device"]
            )

            # Reset state
            self.is_collecting = True
            self.is_paused = False
            self.sample_count = 0
            self.total_ones = 0
            self.start_time = asyncio.get_event_loop().time()

            # Update UI
            self._update_buttons()
            stats = self.query_one(StatsPanel)
            stats.is_collecting = True

            # Clear table
            table = self.query_one("#data_table", DataTable)
            table.clear()

            # Start collection
            self.collection_task = asyncio.create_task(self._collection_loop())

            self.notify(
                f"Started collection to {self.output_file}", severity="information"
            )

        except ValueError as e:
            self.notify(f"Invalid input: {e}", severity="error")

    async def action_pause(self):
        """Pause/resume data collection."""
        if not self.is_collecting:
            return

        self.is_paused = not self.is_paused

        if self.is_paused:
            self.notify("Collection paused", severity="warning")
        else:
            self.notify("Collection resumed", severity="information")

        self._update_buttons()

    async def action_stop(self):
        """Stop data collection and properly release device resources."""
        if not self.is_collecting:
            return

        self.is_collecting = False
        self.is_paused = False

        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass

        # Close device resources for hardware RNGs
        if self.device_key and self.device_module:
            try:
                if self.device_key == "bitbabbler_rng":
                    # Show feedback to user before closing
                    self.notify("Closing BitBabbler device...", severity="information")
                    # Close BitBabbler cached device
                    bitbabbler_rng.close()
                    # Shorter delay for better responsiveness (200ms instead of 500ms)
                    await asyncio.sleep(0.2)
                elif self.device_key == "intel_seed":
                    # Clear Intel RDSEED global instance
                    intel_seed.close()
                    await asyncio.sleep(0.05)  # Reduced from 100ms
                elif self.device_key == "truerng":
                    # TrueRNG closes serial port per operation, no persistent resources
                    pass
                # PseudoRNG has no resources to release
            except Exception as e:
                # Log but don't fail - device might already be closed
                print(f"Warning: Error closing device: {e}")

        # Close CSV file
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None
            self.csv_writer = None

        # Reset device references
        self.device_module = None
        self.device_key = None

        # Update UI
        self._update_buttons()
        stats = self.query_one(StatsPanel)
        stats.is_collecting = False

        self.notify(
            f"Collection stopped. Data saved to {self.output_file}",
            severity="information",
        )

    def _update_buttons(self):
        """Update button states."""
        start_btn = self.query_one("#start_btn", Button)
        pause_btn = self.query_one("#pause_btn", Button)
        stop_btn = self.query_one("#stop_btn", Button)

        if not self.is_collecting:
            start_btn.disabled = False
            pause_btn.disabled = True
            stop_btn.disabled = True
        elif self.is_paused:
            start_btn.disabled = True
            pause_btn.disabled = False
            pause_btn.label = "▶ Resume"
            stop_btn.disabled = False
        else:
            start_btn.disabled = True
            pause_btn.disabled = False
            pause_btn.label = "⏸ Pause"
            stop_btn.disabled = False

    async def _collection_loop(self):
        """Main data collection loop."""
        stats_panel = self.query_one(StatsPanel)
        data_table = self.query_one(DataTablePanel)

        try:
            while self.is_collecting:
                if self.is_paused:
                    await asyncio.sleep(0.1)
                    continue

                # Collect sample
                timestamp = datetime.now()
                if self.device_key == "bitbabbler_rng":
                    data = await self.device_module.get_bytes_async(
                        self.sample_bytes, self.folds
                    )
                else:
                    data = await self.device_module.get_bytes_async(self.sample_bytes)

                # Calculate statistics
                ones = sum(bin(b).count("1") for b in data)
                zeros = len(data) * 8 - ones
                ratio = (ones / (ones + zeros)) * 100

                # Update counters
                self.sample_count += 1
                self.total_ones += ones

                # Calculate running average
                running_avg = (
                    self.total_ones / (self.sample_count * len(data) * 8)
                ) * 100

                # Calculate elapsed time
                elapsed = asyncio.get_event_loop().time() - self.start_time
                hours = int(elapsed // 3600)
                minutes = int((elapsed % 3600) // 60)
                seconds = int(elapsed % 60)
                elapsed_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

                # Update UI (reactive updates)
                stats_panel.current_ratio = ratio
                stats_panel.running_avg = running_avg
                stats_panel.total_samples = self.sample_count
                stats_panel.elapsed_time = elapsed_str

                # Update progress bar (if duration > 0)
                if self.duration > 0:
                    progress = int((elapsed / self.duration) * 100)
                    stats_panel.update_progress(progress, 100)

                # Add to table
                hex_preview = data.hex()[:12] + "..."
                data_table.add_sample(
                    self.sample_count,
                    timestamp.strftime("%H:%M:%S.%f")[:-3],
                    len(data),
                    ones,
                    zeros,
                    ratio,
                    hex_preview,
                )

                # Write to CSV
                if self.csv_writer:
                    self.csv_writer.writerow(
                        [
                            timestamp.isoformat(),
                            ones,
                            zeros,
                            f"{ratio:.2f}",
                            len(data),
                            self.device_module.__name__,
                        ]
                    )
                    self.csv_file.flush()  # Ensure data is written

                # Check if duration exceeded
                if self.duration > 0 and elapsed >= self.duration:
                    await self.action_stop()
                    break

                # Wait for next sample
                await asyncio.sleep(self.frequency)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.notify(f"Error during collection: {e}", severity="error")
            await self.action_stop()


if __name__ == "__main__":
    app = RNGCollectorApp()
    app.run()
