"""BitBabbler RNG Module - Hardware random number generator via USB/FTDI.

Interface for BitBabbler devices (Black, White) from bitbabbler.org.
Uses USB with FTDI chipset for high-speed entropy generation.

Dependencies: pyusb
Includes: libusb-1.0.dll (Windows)

Supports both sync and async APIs for GUI integration.

Example:
    from bitbabbler_rng import is_device_available, get_bytes

    if is_device_available():
        # Get raw entropy
        data = get_bytes(1024)

        # Get folded entropy (XOR whitening)
        folded = get_bytes(1024, folds=2)
    else:
        print("BitBabbler not found")

Async Example:
    import asyncio
    from bitbabbler_rng import get_bytes_async

    async def main():
        data = await get_bytes_async(1024, folds=2)
        print(data)

    asyncio.run(main())
"""

from .core import (
    close,
    close_async,
    get_bits,
    get_bits_async,
    get_bytes,
    get_bytes_async,
    get_exact_bits,
    get_exact_bits_async,
    is_device_available,
    random_int,
    random_int_async,
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
