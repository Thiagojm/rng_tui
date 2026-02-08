"""Entry point for the RNG TUI application."""

from rng_tui import RNGCollectorApp


def main():
    """Launch the RNG data collector TUI application."""
    app = RNGCollectorApp()
    app.run()


if __name__ == "__main__":
    main()
