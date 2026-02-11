# AGENTS.md

Essential info for agentic coding in `rng_tui`.

## Project Overview
Python 3.13+ TUI (Textual) for RNG data collection (Intel RDSEED, TrueRNG, BitBabbler, Pseudo RNG).

## Commands
- **Run**: `uv run python rng_tui.py`
- **Format**: `uv format`
- **Lint**: `uv tool run ruff check --fix`
- **Test**: `uv run pytest` (use `-k "device_name"` for specific hardware)
- **Build**: `uv build`

## Code Style
- **Formatting**: Handled by Ruff.
- **Types**: Use type hints for all functions.
- **Async**: Use `async`/`await` for I/O and device interactions.
- **Structure**: Core logic in `lib/`, UI in `rng_tui.py`.

## File Structure
- `rng_tui.py`: Main TUI app.
- `lib/rng_devices/`: RNG implementations.
- `lib/services/`: Storage and filename services.
- `tests/`: Pytest suite.
- `data/`: `raw/` (CSV) and `processed/` (Excel).

## Guidelines
- Use absolute imports.
- Follow Google-style docstrings.
- Handle hardware errors gracefully.
