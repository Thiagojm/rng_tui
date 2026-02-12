"""
RNG Data Collector TUI - Entry Point

A Textual-based TUI for collecting random number generator data.

Usage:
    uv run python rng_tui.py
"""

from app.main import RNGCollectorApp

if __name__ == "__main__":
    app = RNGCollectorApp()
    app.run()
