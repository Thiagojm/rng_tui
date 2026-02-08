"""Pseudo RNG Module - Software-based cryptographically secure random number generator.

This module provides a pure Python implementation using the secrets module
from the standard library. It serves as a fallback when hardware RNGs are
not available.

Supports both sync and async APIs for GUI integration.

Example:
    from pseudo_rng import get_bytes, random_int

    # Generate 32 random bytes
    data = get_bytes(32)

    # Generate a random integer between 1 and 100
    num = random_int(1, 100)

Async Example:
    import asyncio
    from pseudo_rng import get_bytes_async

    async def main():
        data = await get_bytes_async(32)
        print(data)

    asyncio.run(main())
"""

from .core import (
    is_device_available,
    get_bytes,
    get_bits,
    get_exact_bits,
    random_int,
    close,
    get_bytes_async,
    get_bits_async,
    get_exact_bits_async,
    random_int_async,
    close_async,
)

__all__ = [
    # Sync API
    "is_device_available",
    "get_bytes",
    "get_bits",
    "get_exact_bits",
    "random_int",
    "close",
    # Async API
    "get_bytes_async",
    "get_bits_async",
    "get_exact_bits_async",
    "random_int_async",
    "close_async",
]
