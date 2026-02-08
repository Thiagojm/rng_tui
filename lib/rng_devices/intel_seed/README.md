# IntelSeed

A Python module for Intel RDSEED hardware random number generation.

## Overview

IntelSeed provides access to Intel's RDSEED instruction for generating cryptographically secure random numbers using hardware entropy. This is particularly useful for cryptographic applications that require high-quality entropy.

## Requirements

- Intel/AMD CPU with RDSEED support (Intel Broadwell 2014+ or AMD Zen 2017+)
- Linux x86_64 or Windows x86_64
- Python 3.13+
- For building: GCC (Linux) or MinGW-w64 (Windows/Linux cross-compile)

## Platform Support

| Platform | Status | Library File |
|----------|--------|--------------|
| **Windows** | ✅ Supported | `librdseed.dll` (included) |
| **Linux** | ✅ Supported | `librdseed.so` (included) |
| **macOS** | ❌ Not supported | No `.dylib` available |

The module automatically detects the operating system and loads the appropriate library file. Both Windows (`.dll`) and Linux (`.so`) libraries are included in the package.

## Installation

### Building the Shared Library

#### On Linux (for Linux .so)
1. Compile the C library:
   ```bash
   gcc -shared -fPIC -mrdseed -o librdseed.so rdseed_bytes.c
   ```
   or optimized:
   ```bash
   gcc -fPIC -mrdseed -O2 -Wall -shared -o librdseed.so rdseed_bytes.c
   ```

#### Cross-Compiling for Windows on Linux (.dll)
1. Install MinGW-w64:
   ```bash
   sudo apt update
   sudo apt install mingw-w64
   ```
2. Compile:
   ```bash
   x86_64-w64-mingw32-gcc -fPIC -mrdseed -O2 -Wall -shared -o librdseed.dll rdseed_bytes.c -Wl,--out-implib,liblibrdseed.a
   ```

#### On Windows (native .dll)
1. Install MinGW-w64 (e.g., via MSYS2 or winget: `winget install mingw`).
2. Compile:
   ```bash
   gcc -fPIC -mrdseed -O2 -Wall -shared -o librdseed.dll rdseed_bytes.c
   ```

Place the built library (`librdseed.so` or `librdseed.dll`) in the same directory as the Python module or in your system's library path.

### Installing the Python Module
```bash
pip install -e .
```
or build a wheel:
```bash
python setup.py bdist_wheel
```

## Cross-Platform Support

The IntelSeed module supports both Linux and Windows automatically:

- **OS Detection**: Uses `platform.system()` to detect the operating system. If no `library_path` is provided, it looks for `librdseed.so` on Linux/macOS or `librdseed.dll` on Windows in the module's directory.
- **Usage**: No changes needed in your Python code—the module handles library loading transparently.
- **Fallback**: If the appropriate library is not found, it raises `RDSEEDError`. Ensure the correct library is built and placed correctly.
- **Testing**: On Windows, verify RDSEED support with tools like CPU-Z. The module tests availability during initialization.

For other platforms (e.g., macOS), build a `librdseed.dylib` and extend the detection logic if needed.

## API Reference

### Functions

All functions follow the standard RNG module API for compatibility with other modules in the rng_devices package.

- `is_device_available() -> bool`: Check if RDSEED is available and accessible (standardized API name)
- `is_rdseed_available(library_path: str | None = None) -> bool`: Original function name, same functionality
- `get_bytes(n_bytes: int) -> bytes`: Generate n_bytes of raw entropy
- `get_bits(n_bits: int) -> bytes`: Generate n_bits of raw entropy (may have extra bits, rounds up to byte boundary)
- `get_exact_bits(n_bits: int) -> bytes`: Generate exactly n_bits of raw entropy (must be divisible by 8)
- `random_int(min_val: int = 0, max_val: int | None = None) -> int`: Generate random integer in range [min_val, max_val). If max_val is None, generates 32-bit value.
- `close() -> None`: Reset the global RDSEED instance (for API compatibility)

### Classes

- `IntelSeed`: Main class for RDSEED operations
- `RDSEEDError`: Exception raised when RDSEED operations fail

### IntelSeed Class Methods

- `IntelSeed.get_bytes(n_bytes: int) -> bytes`: Generate n_bytes of raw entropy
- `IntelSeed.get_bits(n_bits: int) -> bytes`: Generate n_bits of raw entropy
- `IntelSeed.get_exact_bits(n_bits: int) -> bytes`: Generate exactly n_bits of raw entropy
- `IntelSeed.random_int(min_val: int = 0, max_val: int | None = None) -> int`: Generate random integer in range [min_val, max_val)

## Usage

### Basic Usage

```python
from intel_seed import is_device_available, get_bytes, get_bits, get_exact_bits, random_int

# Check if RDSEED is available
if is_device_available():
    # Generate 32 bytes of entropy
    data = get_bytes(32)
    print(f"32 bytes: {data.hex()}")
    
    # Generate 256 bits of entropy (returns 32 bytes)
    data = get_bits(256)
    print(f"256 bits: {data.hex()}")
    
    # Generate exactly 128 bits of entropy (returns 16 bytes)
    data = get_exact_bits(128)
    print(f"128 bits: {data.hex()}")
    
    # Generate random integer 0-99
    num = random_int(0, 100)
    print(f"Random 0-99: {num}")
else:
    print("RDSEED not available on this CPU")
```

### Advanced Usage

```python
from intel_seed import IntelSeed, RDSEEDError

try:
    # Create an instance
    rdseed = IntelSeed()
    
    # Generate various amounts of entropy
    data_1_bit = rdseed.get_exact_bits(1)
    data_7_bits = rdseed.get_exact_bits(7)
    data_128_bits = rdseed.get_exact_bits(128)
    
    print(f"1 bit: {data_1_bit.hex()}")
    print(f"7 bits: {data_7_bits.hex()}")
    print(f"128 bits: {data_128_bits.hex()}")
    
except RDSEEDError as e:
    print(f"RDSEED Error: {e}")
```

### Checking RDSEED Availability

```python
from intel_seed import is_device_available, RDSEEDError

# Check if RDSEED is available (fast and safe)
if is_device_available():
    print("RDSEED is supported! You can now use hardware entropy.")
    from intel_seed import get_bytes
    data = get_bytes(32)
else:
    print("RDSEED not available - falling back to software RNG.")
    import os
    data = os.urandom(32)
```

### Generating Random Integers

```python
from intel_seed import random_int, is_device_available

if is_device_available():
    # Random int from 0 to 99 (range [0, 100) - exclusive upper bound)
    num = random_int(0, 100)
    print(f"Random 0-99: {num}")
    
    # Random int from 1 to 6 (like a die, range [1, 7))
    die_roll = random_int(1, 7)
    print(f"Die roll 1-6: {die_roll}")
    
    # Random 32-bit integer (when max_val is None)
    big_num = random_int()
    print(f"Random 32-bit: {big_num}")
```

### Using with Other RNG Modules

```python
from rng_devices import intel_seed, pseudo_rng

# Try hardware RNG first, fallback to software
if intel_seed.is_device_available():
    data = intel_seed.get_bytes(32)
    print("Using Intel RDSEED hardware RNG")
else:
    data = pseudo_rng.get_bytes(32)
    print("Using software RNG fallback")
```

## Testing

Run the test script:
```bash
python test_intel_seed.py
```

## Error Handling

The module raises `RDSEEDError` when:
- The RDSEED library cannot be loaded
- The CPU doesn't support RDSEED
- RDSEED operations fail

```python
from intel_seed import RDSEEDError

try:
    data = intel_seed.get_bytes(32)
except RDSEEDError as e:
    print(f"RDSEED not available: {e}")
```

## API Compatibility

This module is compatible with the rng_devices package API:
- Uses `is_device_available()` for consistency with other modules
- `random_int(min_val, max_val)` uses exclusive upper bound (max_val is not included)
- Includes `close()` function for resource cleanup (resets global instance)

## License

MIT License
