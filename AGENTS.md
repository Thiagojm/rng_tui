# AGENTS.md

## Rules

You are an expert Python developer helping maintain and evolve this project.
Follow these rules strictly in every interaction.

### Core principles:
- Think step-by-step before writing or changing code.
- Make minimal, focused changes — one feature/fix/refactor at a time.
- Never guess: if something is unclear, ask for clarification instead of assuming.
- Prioritize readability, type safety (use type hints), and modern Python (3.10+).
- Write tests (pytest) for new logic or when fixing bugs.
- Respect existing style (run ruff/black/isort if configured).
- Commit messages: conventional commits style (feat:, fix:, refactor:, chore:, docs: etc.)

### Changelog Rule (mandatory)

Every time you make **any** persistent change to the codebase (new file, modified file, deleted file), you **must** do the following **before** finishing the response:

1. Create or append to CHANGELOG.md (keep newest entries at the top)
2. Use this exact format:

```markdown
## [Unreleased] - YYYY-MM-DD-HH:MM (Year-Month-Day-Hour-Minutes)

### Added
- Short description (file(s) affected)

### Changed
- ...

### Fixed
- ...

### Removed
- ...

## Essential info for agentic coding in `rng_tui`.

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
- **Structure**: Core logic in `lib/`, UI in `app/`.

## File Structure
- `rng_tui.py`: Main TUI app.
- `lib/rng_devices/`: RNG implementations.
- `lib/services/`: Storage and filename services.
- `tests/`: Pytest suite.
- `data/`: `raw/` (CSV) and `processed/` (Excel).
