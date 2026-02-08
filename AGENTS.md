# AGENTS.md

This file provides essential information for agentic coding agents working in this repository. It contains build/lint/test commands, code style guidelines, and other conventions to maintain consistency.

## Project Overview

This is a Python-based Terminal User Interface (TUI) application for collecting random number generator (RNG) data. It supports multiple RNG devices including Intel RDSEED, TrueRNG, BitBabbler, and software-based pseudo RNG. The application uses Textual for the TUI framework.

## Tech Stack

- **Language**: Python 3.13+
- **Package Manager**: uv
- **TUI Framework**: Textual
- **Dependencies**: pyserial, pyusb, textual
- **Linting/Formatting**: Ruff (via uv)
- **Testing**: pytest

## Build/Lint/Test Commands

### Running the Application
```bash
uv run python rng_tui.py
```

### Linting and Formatting
```bash
# Check formatting (non-destructive)
uv format --check

# Apply formatting fixes
uv format

# Check for linting issues
uv tool run ruff check

# Apply auto-fixable linting issues
uv tool run ruff check --fix
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest path/to/test_file.py

# Run single test function
uv run pytest -k "test_function_name"

# Run tests with verbose output
uv run pytest -v

# Run tests and stop on first failure
uv run pytest -x
```

### Building and Distribution
```bash
# Build wheel/distribution
uv build

# Publish to PyPI (requires authentication)
uv publish
```

## Code Style Guidelines

### Imports
- Use absolute imports within the project
- Group imports: standard library, third-party, local modules
- Use type hints for function parameters and return values
- Import specific items rather than entire modules when possible
- Place imports at the top of files, after module docstrings

**Good:**
```python
import asyncio
from typing import Optional

from textual.app import App
from rng_devices import pseudo_rng
```

**Bad:**
```python
import sys, os
from rng_devices.pseudo_rng import *
```

### Naming Conventions
- **Functions/Methods**: snake_case
- **Variables**: snake_case
- **Constants**: UPPER_SNAKE_CASE
- **Classes**: PascalCase
- **Modules**: snake_case
- **Type Variables**: PascalCase with Type suffix

**Examples:**
```python
class RNGCollectorApp(App):  # Class
    def collect_data(self) -> bytes:  # Method
        sample_count = 0  # Variable
        MAX_RETRIES = 3  # Constant
```

### Type Hints
- Use type hints for all function parameters and return values
- Use `Optional` for nullable types
- Use `Union` for multiple possible types
- Use generic types where appropriate (`List`, `Dict`, etc.)
- Import types from `typing` module

**Examples:**
```python
from typing import Optional, List, Dict

def get_bytes(n: int) -> bytes:
    """Generate n random bytes."""

def find_device(name: str) -> Optional[Dict[str, str]]:
    """Find device by name."""

async def collect_samples(count: int) -> List[bytes]:
    """Collect multiple samples asynchronously."""
```

### Documentation
- Use docstrings for all public functions, classes, and modules
- Follow Google-style docstring format
- Include parameter descriptions and return value descriptions
- Document exceptions that may be raised

**Example:**
```python
def get_exact_bits(n: int) -> bytes:
    """Generate exactly n bits of entropy.

    Returns bytes containing exactly n random bits. The number of bits
    must be divisible by 8 (byte-aligned).

    Args:
        n: Number of bits to generate. Must be positive and divisible by 8.

    Returns:
        Bytes containing exactly n random bits.

    Raises:
        ValueError: If n <= 0 or if n is not divisible by 8
    """
```

### Error Handling
- Use specific exception types rather than generic `Exception`
- Provide meaningful error messages
- Log errors appropriately (use print() for console apps, logging module for services)
- Validate inputs at function boundaries
- Use try/except blocks around external operations (USB, serial, file I/O)

**Examples:**
```python
def get_bytes(n: int) -> bytes:
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    if n % 8 != 0:
        raise ValueError(f"n must be divisible by 8, got {n}")
    # ... implementation

try:
    data = device.read_bytes(count)
except USBError as e:
    raise DeviceError(f"Failed to read from device: {e}") from e
```

### Async/Await
- Use async functions for I/O operations and device interactions
- Use `asyncio.create_task()` for concurrent operations
- Handle cancellation properly with try/except around `CancelledError`
- Use thread pools for CPU-bound operations that would block the event loop

**Example:**
```python
async def collect_sample(self) -> bytes:
    """Collect a sample asynchronously."""
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(self._executor, self._sync_collect)
    except asyncio.CancelledError:
        # Cleanup resources
        await self._cleanup()
        raise
```

### Constants and Configuration
- Define constants at module level
- Use descriptive names for magic numbers
- Group related constants together

**Example:**
```python
# Default configuration
DEFAULT_SAMPLE_SIZE = 2048  # bits
DEFAULT_FREQUENCY = 1.0    # seconds
DEFAULT_DURATION = 60      # seconds

# Device-specific constants
BITBABBLER_VENDOR_ID = 0x0403
BITBABBLER_PRODUCT_ID = 0x6001
```

### File Structure
- Organize code into logical modules/packages
- Use `__init__.py` files for package initialization
- Separate core logic from UI code
- Place test files in appropriate locations (currently in `rng_devices/`)

**Current structure:**
```
rng_tui/
├── rng_tui.py          # Main TUI application
├── main.py             # Entry point
├── style.css           # Textual CSS styles
├── pyproject.toml      # Project configuration
├── uv.lock             # Lockfile
├── lib/                # Library modules
│   ├── __init__.py
│   └── rng_devices/    # RNG device implementations
│       ├── __init__.py
│       ├── pseudo_rng/
│       ├── truerng/
│       ├── bitbabbler_rng/
│       └── intel_seed/
├── tests/              # Automated test suite
│   ├── __init__.py
│   ├── conftest.py     # Pytest configuration and fixtures
│   ├── test_*.py       # Automated tests for each device
│   └── manual/         # Manual test scripts
│       ├── __init__.py
│       ├── test_bit_manual.py
│       └── test_true_manual.py
├── data/               # Data directories
│   ├── processed/      # Processed statistical analysis
│   └── raw/            # Raw CSV data from TUI
└── .gitignore
```

### Security Considerations
- Never commit secrets, API keys, or sensitive configuration
- Use secure random number generation for cryptographic purposes
- Validate all external inputs
- Handle USB/serial device access securely
- Avoid logging sensitive data

### Performance
- Use async operations for I/O to avoid blocking the UI
- Cache expensive operations where appropriate
- Profile performance-critical sections
- Use appropriate data structures for the use case

### Testing
- Write integration tests for hardware devices and unit tests for software RNG
- Use `@pytest.mark.hardware("device_name")` to mark hardware-dependent tests
- Tests gracefully skip when hardware is not available
- Test error conditions and edge cases
- Use descriptive test names and assertions

**Example test structure:**
```python
import pytest
from rng_devices.pseudo_rng import get_bytes

@pytest.mark.hardware("pseudo_rng")
def test_get_bytes_positive(skip_if_no_device, small_test_size):
    """Test get_bytes with positive input."""
    result = get_bytes(small_test_size)
    assert len(result) == small_test_size
    assert isinstance(result, bytes)

@pytest.mark.hardware("pseudo_rng")
def test_get_bytes_zero_raises(skip_if_no_device):
    """Test get_bytes raises ValueError for zero input."""
    with pytest.raises(ValueError, match="n must be positive"):
        get_bytes(0)

@pytest.mark.hardware("truerng")
def test_truerng_integration(skip_if_no_device, small_test_size):
    """Integration test for TrueRNG hardware."""
    from rng_devices.truerng import get_bytes
    result = get_bytes(small_test_size)
    assert isinstance(result, bytes)
    assert len(result) == small_test_size
```

**Running tests:**
```bash
# Run all tests (hardware tests skip if devices not connected)
uv run pytest

# Run only software tests (pseudo_rng)
uv run pytest -k "pseudo_rng"

# Run tests for specific hardware
uv run pytest -k "truerng" --tb=short
```

### Commit Messages
- Use imperative mood ("Add feature" not "Added feature")
- Start with a summary of what changed
- Reference issue numbers when applicable
- Keep first line under 50 characters

**Examples:**
```
Add CSV export functionality for collected data
Fix device availability check for BitBabbler
Update dependencies to latest versions
```

### Version Control
- Use feature branches for new development
- Keep commits focused on single changes
- Write clear commit messages
- Rebase interactive commits before merging

## Development Workflow

1. Create a feature branch: `git checkout -b feature/new-feature`
2. Make changes following the style guidelines
3. Run linting and formatting: `uv format && uv tool run ruff check --fix`
4. Test changes: `uv run pytest` (when tests are implemented)
5. Commit with clear message: `git commit -m "Add new feature"`
6. Push and create pull request

## Additional Tools

### Pre-commit Hooks (if implemented)
- Consider setting up pre-commit hooks for automatic linting/formatting
- Use tools like `pre-commit` framework with ruff and other checks

### IDE Configuration
- Configure editors to use ruff for Python formatting
- Enable type checking with mypy (if added to project)
- Use editor extensions for Python development

## Troubleshooting

### Common Issues
- **Import errors**: Ensure dependencies are installed with `uv sync`
- **Device not found**: Check USB connections and permissions
- **Linting failures**: Run `uv format` to auto-fix formatting issues
- **Test failures**: Check test setup and mock external dependencies

### Getting Help
- Check existing code for patterns and conventions
- Review commit history for similar changes
- Ask in code reviews or issues for clarification

---

This document should be updated as the project evolves and new conventions are established.</content>
<parameter name="filePath">D:\Projetos\rng_tui\AGENTS.md