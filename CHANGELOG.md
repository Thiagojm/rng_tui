## [Unreleased] - 2026-02-16-17:02

### Added
- Live Z-Score graph in Collect tab (replaces DataTable)
- Real-time cumulative Z-Score calculation during collection
- `textual-plotext` dependency to pyproject.toml
- `plotit_textual_plot.py` - mock live plot using textual-plot
- `plotit_plotext.py` - mock live plot using textual-plotext

### Changed
- Replaced `DataTablePanel` with `LivePlotPanel` in Collect tab

### Removed
- Old DataTable from Collect tab (replaced with live graph)

## [Unreleased] - 2026-02-16

### Changed
- Statistics field now shows cumulative Z-score (last row) instead of mean Z-score
- Export to Excel now auto-analyzes the file if not already analyzed
- Export Excel button is now enabled by default
- Statistics field is now cleared when selecting a different file

### Fixed
- Replaced deprecated `asyncio.get_event_loop().time()` with `loop.time()` in `app/main.py`
- Fixed ThreadPoolExecutor `_shutdown` private attribute access using `getattr()` fallback
- Removed redundant serial port `isOpen()` check in `truerng/core.py`
- Fixed button label persistence in `_update_buttons()` using instance variable
- Added retry logic (3 attempts) for partial RDSEED reads in `intel_seed.py`
- Fixed setup script to auto-request sudo instead of exiting with error

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
