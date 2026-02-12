## [Unreleased] - 2026-02-12-17:45

### Fixed
- Added missing imports (`bitbabbler_rng`, `intel_seed`) in `app/main.py`
- Fixed type errors in `_collection_loop` with null checks for device_module, start_time, output_file
- Fixed Select.value type handling with proper validation
- Fixed missing type guards in analysis functions

## [Unreleased] - 2026-02-12-17:38

### Changed
- Split `rng_tui.py` into modular structure: `app/main.py`, `app/panels.py`, `app/config.py`
- Moved `style.css` to `app/static/style.css`
- Updated `rng_tui.py` to thin entry point
