from textual.app import ComposeResult
from textual.containers import (
    Horizontal,
    HorizontalGroup,
    Vertical,
    VerticalGroup,
)
from textual.reactive import reactive
from textual.widgets import (
    Button,
    DataTable,
    DirectoryTree,
    Input,
    Label,
    ProgressBar,
    Select,
    Static,
)

from .config import DEVICES


class StatsPanel(VerticalGroup):
    """Panel displaying real-time statistics."""

    current_ratio = reactive(50.0)
    running_avg = reactive(50.0)
    total_samples = reactive(0)
    elapsed_time = reactive("00:00:00")
    is_collecting = reactive(False)

    def compose(self) -> ComposeResult:
        yield Label("📊 Real-time Statistics", classes="title")
        yield Label("Current Ratio: 50.00%", id="current_ratio")
        yield Label("Running Avg: 50.00%", id="running_avg")
        yield Label("Total Samples: 0", id="total_samples")
        yield Label("Elapsed: 00:00:00", id="elapsed_time")
        yield ProgressBar(total=100, show_percentage=True, id="progress")

        # Buttons row within StatsPanel
        with Horizontal(classes="stats-buttons"):
            yield Button("▶ Start", id="start_btn", variant="success")
            yield Button("⏸ Pause", id="pause_btn", variant="warning", disabled=True)
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


class ConfigPanel(VerticalGroup):
    """Panel for configuration inputs."""

    def compose(self) -> ComposeResult:
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
        with HorizontalGroup():
            with VerticalGroup():
                yield Label("Sample Size (bits):")
                yield Input(value="2048", id="bits_input", type="integer")
            with VerticalGroup():
                yield Label("Frequency (seconds):")
                yield Input(value="1.0", id="freq_input", type="number")
        with HorizontalGroup():
            with VerticalGroup():
                yield Label("Duration (seconds, 0 = infinite):")
                yield Input(value="0", id="duration_input", type="integer")
            with VerticalGroup():
                yield Label("Folds (BitBabbler only, 0=raw):")
                yield Select(
                    [(str(i), i) for i in range(5)],
                    id="folds_select",
                    value=0,
                    disabled=True,
                )

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle device selection changes."""
        if event.select.id == "device_select":
            folds_select = self.query_one("#folds_select", Select)
            folds_select.disabled = event.value != "bitbabbler_rng"


class DataTablePanel(VerticalGroup):
    """Panel displaying collected data in a table."""

    def compose(self) -> ComposeResult:
        yield Label("📋 Collected Data", classes="title")
        table = DataTable(id="data_table")
        table.add_column("#", width=4)
        table.add_column("Time", width=9)
        table.add_column("Bytes", width=5)
        table.add_column("Ones", width=4)
        table.add_column("Zeros", width=4)
        table.add_column("Ratio%", width=7)
        table.add_column("Hex", width=12)
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


class AnalysisPanel(VerticalGroup):
    """Panel for statistical analysis and Excel export."""

    def compose(self) -> ComposeResult:
        with Horizontal():
            # Left: File Browser
            with Vertical(classes="file-browser-panel"):
                yield Label("📁 Select CSV File", classes="title")
                yield DirectoryTree("data/raw", id="file_tree")
                yield Button("🔄 Refresh", id="refresh_tree_btn", variant="default")

            # Right: Analysis Controls & Results
            with VerticalGroup(classes="analysis-content"):
                yield Label("⚙️ Configuration", classes="title")

                # Selected file display
                with Horizontal():
                    yield Label("File:", classes="field-label")
                    yield Input(
                        value="",
                        id="analysis_file_input",
                        placeholder="Select a file from the tree...",
                        disabled=True,
                    )

                # Parameters
                with Horizontal():
                    yield Label("Bits:", classes="field-label")
                    yield Input(
                        value="2048",
                        id="analysis_bits_input",
                        type="integer",
                        classes="short-input",
                    )
                    yield Label("Interval (s):", classes="field-label")
                    yield Input(
                        value="1",
                        id="analysis_interval_input",
                        type="integer",
                        classes="short-input",
                    )

                # Action Buttons
                with Horizontal(classes="button-row"):
                    yield Button("🔍 Analyze", id="analyze_btn", variant="primary")
                    yield Button(
                        "📊 Export Excel",
                        id="export_btn",
                        variant="success",
                    )

                # Validation message
                yield Static("", id="validation_message")

                # Compact Statistics Summary
                yield Label("📊 Statistics", classes="section-title")
                yield Static(
                    "No data analyzed yet. Select a file and click Analyze.",
                    id="stats_display",
                )
