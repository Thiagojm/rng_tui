import asyncio
import os
import traceback
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.stats import norm
from textual.app import App, ComposeResult
from textual.containers import (
    HorizontalScroll,
    VerticalScroll,
)
from textual.widgets import (
    Button,
    DataTable,
    DirectoryTree,
    Footer,
    Header,
    Input,
    Select,
    Static,
    TabbedContent,
    TabPane,
)

# Import RNG device modules for close() operations
from lib.rng_devices import bitbabbler_rng, intel_seed

# Import services
from lib.services import filenames
from lib.services.storage import (
    read_csv_counts,
    write_csv_count,
    write_enhanced_excel,
)

from .config import DEVICES
from .panels import (
    AnalysisPanel,
    ConfigPanel,
    DataTablePanel,
    StatsPanel,
)


class RNGCollectorApp(App):
    """Main TUI application for RNG data collection."""

    CSS_PATH = "static/style.css"

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

        # Analysis state
        self.analysis_df = None
        self.selected_file_path = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with TabbedContent(initial="collect"):
            # Tab 1: Data Collection (existing functionality)
            with TabPane("Collect", id="collect"):
                with HorizontalScroll():
                    with VerticalScroll():
                        yield ConfigPanel()
                    yield StatsPanel()
                yield DataTablePanel()

            # Tab 2: Statistical Analysis (new functionality)
            with TabPane("Analysis", id="analysis"):
                with VerticalScroll():
                    yield AnalysisPanel()

        yield Footer()

    def on_mount(self):
        """Called when app is mounted."""
        self.title = "RNG Data Collector TUI"
        self.sub_title = "Hardware & Software RNG Data Collection"

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Handle file selection from DirectoryTree."""
        self.selected_file_path = str(event.path)

        # Update input field
        panel = self.query_one(AnalysisPanel)
        panel.query_one("#analysis_file_input", Input).value = self.selected_file_path

        # Validate file
        self.validate_selected_file()

        # Try auto-detect parameters from filename
        try:
            bits = filenames.parse_bits(self.selected_file_path)
            interval = filenames.parse_interval(self.selected_file_path)
            panel.query_one("#analysis_bits_input", Input).value = str(bits)
            panel.query_one("#analysis_interval_input", Input).value = str(interval)
            self.notify(
                f"Auto-detected: {bits} bits, {interval}s interval",
                severity="information",
            )
        except ValueError:
            pass

    async def on_button_pressed(self, event: Button.Pressed):
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "start_btn":
            await self.action_start()
        elif button_id == "pause_btn":
            await self.action_pause()
        elif button_id == "stop_btn":
            await self.action_stop()
        elif button_id == "refresh_tree_btn":
            tree = self.query_one("#file_tree", DirectoryTree)
            tree.reload()
            self.notify("File tree refreshed", severity="information")
        elif button_id == "analyze_btn":
            await self.action_analyze()
        elif button_id == "export_btn":
            await self.action_export_excel()

    async def action_start(self):
        """Start data collection."""
        if self.is_collecting:
            return

        # Get configuration
        config = self.query_one(ConfigPanel)
        device_key_raw = config.query_one("#device_select", Select).value
        bits_str = config.query_one("#bits_input", Input).value
        freq_str = config.query_one("#freq_input", Input).value
        duration_str = config.query_one("#duration_input", Input).value

        # Validate device selection
        if device_key_raw is None or device_key_raw == "":
            self.notify("Please select a device", severity="error")
            return
        device_key: str = str(device_key_raw)

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
            device_info = DEVICES.get(device_key)
            if device_info is None:
                self.notify(f"Unknown device: {device_key}", severity="error")
                return
            self.device_module = device_info["module"]

            # Get folds for BitBabbler
            if device_key == "bitbabbler_rng":
                folds_val: int | None = None
                folds_raw = config.query_one("#folds_select", Select).value
                if folds_raw is not None:
                    try:
                        folds_val = int(str(folds_raw))
                    except (ValueError, TypeError):
                        pass
                self.folds = folds_val if folds_val is not None else 0
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

            # Map device key to device code
            device_code_map = {
                "bitbabbler_rng": "bitb",
                "truerng": "trng",
                "intel_seed": "intel",
                "pseudo_rng": "pseudo",
            }
            device_code = device_code_map.get(device_key, device_key)

            # Generate filename using new convention
            folds_param: int | None = (
                self.folds if device_key == "bitbabbler_rng" else None
            )
            filename_stem = filenames.format_capture_name(
                device=device_code,
                bits=bits,
                interval=int(self.frequency),
                folds=folds_param,
            )
            self.output_file = f"data/raw/{filename_stem}.csv"

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

    def validate_selected_file(self) -> bool:
        """Validate selected file format and existence."""
        panel = self.query_one(AnalysisPanel)
        msg = panel.query_one("#validation_message", Static)

        if not self.selected_file_path:
            msg.update("❌ No file selected")
            return False

        if not os.path.exists(self.selected_file_path):
            msg.update("❌ File does not exist")
            return False

        if not self.selected_file_path.endswith(".csv"):
            msg.update("❌ Selected file must be a CSV file")
            return False

        # Check if file is readable and has valid format
        try:
            with open(self.selected_file_path) as f:
                first_line = f.readline().strip()
                # Expect format: YYYYMMDDTHHMMSS,count
                parts = first_line.split(",")
                if len(parts) != 2:
                    msg.update("❌ Invalid CSV format (expected: time,count)")
                    return False
                # Try parsing count as int
                int(parts[1])
        except Exception as e:
            msg.update(f"❌ File validation failed: {e}")
            return False

        msg.update("✅ File valid")
        return True

    async def action_analyze(self):
        """Perform statistical analysis on selected file."""
        if not self.validate_selected_file():
            return

        # Type guard - selected_file_path must not be None after validation
        file_path = self.selected_file_path
        if file_path is None:
            self.notify("No file selected for analysis", severity="error")
            return

        panel = self.query_one(AnalysisPanel)

        try:
            # Get parameters
            bits = int(panel.query_one("#analysis_bits_input", Input).value)

            # Read CSV
            self.analysis_df = read_csv_counts(file_path)

            # Calculate Z-scores with p-values
            self.analysis_df = self.add_zscore_with_pvalues(self.analysis_df, bits)

            # Update statistics display
            self.update_statistics_display(self.analysis_df, bits)

            # Enable export button
            panel.query_one("#export_btn", Button).disabled = False

            self.notify(
                f"Analysis complete! {len(self.analysis_df)} samples analyzed.",
                severity="information",
            )

        except Exception as e:
            self.notify(f"Analysis failed: {e}", severity="error")

    def add_zscore_with_pvalues(
        self, df: pd.DataFrame, block_bits: int
    ) -> pd.DataFrame:
        """Add Z-score and p-value calculations."""
        expected_mean = 0.5 * block_bits
        expected_std_dev = np.sqrt(block_bits * 0.25)

        # Calculate sample count for each row
        df["sample_count"] = range(1, len(df) + 1)

        # Cumulative mean
        df["cumulative_mean"] = df["ones"].expanding().mean()

        # Z-score (standard error decreases with sqrt(n))
        df["z_test"] = (df["cumulative_mean"] - expected_mean) / (
            expected_std_dev / np.sqrt(df["sample_count"])
        )

        # Two-tailed p-value
        df["p_value"] = 2 * (1 - norm.cdf(np.abs(df["z_test"])))

        return df

    def update_statistics_display(self, df: pd.DataFrame, bits: int):
        """Calculate and display comprehensive statistics."""
        stats = self.query_one("#stats_display", Static)

        # Calculate statistics
        mean_ones = df["ones"].mean()
        total_samples = len(df)

        # Expected values for binomial distribution
        expected_mean = 0.5 * bits

        # Z-score statistics
        z_scores = df["z_test"]
        max_z = z_scores.abs().max()
        mean_z = z_scores.mean()

        # Test for randomness (rough check)
        within_95 = (z_scores.abs() <= 1.96).sum()
        percent_95 = (within_95 / total_samples) * 100

        # Pass/fail assessment
        if percent_95 > 90 and max_z < 3:
            assessment = "✓ PASS"
        else:
            assessment = "⚠ REVIEW"

        # Compact statistics display
        stats.update(
            f"Samples: {total_samples} | Bits: {bits} | Mean: {mean_ones:.1f} (Exp: {expected_mean:.1f}) | "
            f"Z-Score: {mean_z:.3f} (max {max_z:.3f}) | 95% CI: {percent_95:.0f}% | {assessment}"
        )

    async def action_export_excel(self):
        """Export analyzed data to Excel with detailed error handling."""
        if self.analysis_df is None or len(self.analysis_df) == 0:
            self.notify("No data to export. Run analysis first.", severity="warning")
            return

        if not self.selected_file_path:
            self.notify("No file selected.", severity="error")
            return

        panel = self.query_one(AnalysisPanel)

        try:
            bits = int(panel.query_one("#analysis_bits_input", Input).value)
            interval = int(panel.query_one("#analysis_interval_input", Input).value)

            self.notify(
                f"Exporting {len(self.analysis_df)} samples...", severity="information"
            )

            # Use the function from storage module
            excel_path = write_enhanced_excel(
                self.analysis_df, self.selected_file_path, bits, interval
            )

            self.notify(
                f"Excel exported successfully!\nSaved to: {excel_path}",
                severity="information",
                timeout=5,
            )

        except ValueError as e:
            self.notify(f"Invalid parameters: {e}", severity="error")
        except ImportError as e:
            self.notify(f"Missing dependency: {e}", severity="error")
        except Exception as e:
            error_detail = str(e)[:100]
            self.notify(f"Export failed: {error_detail}", severity="error", timeout=8)
            print(f"Excel export error:\n{traceback.format_exc()}")

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
        # Type guards - these should be set before calling this method
        if self.device_module is None:
            self.notify("Device module not initialized", severity="error")
            return
        if self.start_time is None:
            self.notify("Start time not set", severity="error")
            return
        if self.output_file is None:
            self.notify("Output file not set", severity="error")
            return

        stats_panel = self.query_one(StatsPanel)
        data_table = self.query_one(DataTablePanel)

        # Cache local references for performance and type safety
        device_module = self.device_module
        start_time = self.start_time
        output_file = self.output_file

        try:
            while self.is_collecting:
                if self.is_paused:
                    await asyncio.sleep(0.1)
                    continue

                # Collect sample
                timestamp = datetime.now()
                if self.device_key == "bitbabbler_rng":
                    data = await device_module.get_bytes_async(
                        self.sample_bytes, self.folds
                    )
                else:
                    data = await device_module.get_bytes_async(self.sample_bytes)

                # Calculate statistics
                ones = int.from_bytes(data, "big").bit_count()
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
                elapsed = asyncio.get_event_loop().time() - start_time
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
                hex_preview = data.hex()[:9] + "..."
                data_table.add_sample(
                    self.sample_count,
                    timestamp.strftime("%H:%M:%S.%f")[:-3],
                    len(data),
                    ones,
                    zeros,
                    ratio,
                    hex_preview,
                )

                # Write to CSV using storage service
                file_stem = os.path.splitext(output_file)[0]
                write_csv_count(ones, file_stem)

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
