"""TrueRNG Module - Hardware random number generator via USB serial.

Interface for TrueRNG devices (TrueRNG3, TrueRNGPro) from ubld.it.
Connects via USB and appears as a serial port.

Dependencies: pyserial

Supports both sync and async APIs for GUI integration.

Example:
    from truerng import is_device_available, get_bytes

    if is_device_available():
        data = get_bytes(32)
    else:
        print("TrueRNG device not found")

Async Example:
    import asyncio
    from truerng import get_bytes_async

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
