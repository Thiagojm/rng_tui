"""
IntelSeed: Python module for Intel RDSEED hardware random number generation.

This module provides access to Intel's RDSEED instruction for generating
cryptographically secure random numbers using hardware entropy.

Compatible API with other RNG modules:
- is_device_available() -> bool
- get_bytes(n: int) -> bytes
- get_bits(n: int) -> bytes
- get_exact_bits(n: int) -> bytes
- random_int(min_val: int = 0, max_val: int | None = None) -> int
- close() -> None

Async API (for GUI applications):
- get_bytes_async(n: int) -> bytes
- get_bits_async(n: int) -> bytes
- get_exact_bits_async(n: int) -> bytes
- random_int_async(min_val: int = 0, max_val: int | None = None) -> int
- close_async() -> None
"""

from .intel_seed import (
    IntelSeed,
    RDSEEDError,
    get_rdseed,
    get_bytes,
    get_bits,
    get_exact_bits,
    is_rdseed_available,
    is_device_available,
    random_int,
    close,
    get_bytes_async,
    get_bits_async,
    get_exact_bits_async,
    random_int_async,
    close_async,
)

__version__ = "1.1.0"
__author__ = "Thiago Jung"
__email__ = "tjm.plastica@gmail.com"

__all__ = [
    # Sync API
    "IntelSeed",
    "RDSEEDError",
    "get_rdseed",
    "get_bytes",
    "get_bits",
    "get_exact_bits",
    "is_rdseed_available",
    "is_device_available",
    "random_int",
    "close",
    # Async API
    "get_bytes_async",
    "get_bits_async",
    "get_exact_bits_async",
    "random_int_async",
    "close_async",
]
