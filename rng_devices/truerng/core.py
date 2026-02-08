"""TrueRNG Module - Hardware random number generator via USB serial.

Interface for TrueRNG devices (TrueRNG3, TrueRNGPro) from ubld.it.
Device connects via USB and appears as a serial port.

Dependencies: pyserial
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from serial.tools import list_ports
import serial
import os
from typing import Optional

# Module-level executor for async operations (1 worker to prevent concurrent hardware access)
_executor = ThreadPoolExecutor(max_workers=1)


def _is_trng_port(port) -> bool:
    """Check if a serial port corresponds to a TrueRNG device.

    Works across platforms by checking description/manufacturer/product strings.
    """
    try:
        # pyserial 3.x exposes attributes on the ListPortInfo object
        desc = getattr(port, "description", None) or ""
        manuf = getattr(port, "manufacturer", None) or ""
        prod = getattr(port, "product", None) or ""
        text = f"{desc} {manuf} {prod}".lower()
        if "truerng" in text:
            return True
    except Exception:
        pass

    try:
        # Fallback for tuple-like entries: (device, description, ...)
        return str(port[1]).lower().startswith("truerng")
    except Exception:
        return False


def _find_port() -> Optional[str]:
    """Find the TrueRNG device port.

    Returns:
        Port path/name if found, None otherwise
    """
    ports = list(list_ports.comports())
    for port in ports:
        if _is_trng_port(port):
            try:
                return getattr(port, "device", None) or str(port[0])
            except Exception:
                return str(port[0])
    return None


def is_device_available() -> bool:
    """Check if TrueRNG device is available and accessible.

    Returns:
        True if device is detected on any serial port
    """
    return _find_port() is not None


def get_bytes(n: int) -> bytes:
    """Generate n random bytes from TrueRNG device.

    Args:
        n: Number of bytes to generate. Must be positive.

    Returns:
        Random bytes from hardware device.

    Raises:
        ValueError: If n <= 0
        RuntimeError: If device not found or read fails
    """
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")

    port = _find_port()
    if port is None:
        raise RuntimeError("TrueRNG device not found")

    ser = serial.Serial(port=port, timeout=10)
    try:
        if not ser.isOpen():
            ser.open()
        ser.setDTR(True)
        ser.flushInput()
        data = ser.read(n)

        # Linux fix: Reset serial port min setting after pyserial usage
        if os.name == "posix":
            import subprocess

            try:
                subprocess.run(
                    ["stty", "-F", port, "min", "1"], check=True, capture_output=True
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

        if len(data) < n:
            raise RuntimeError(f"Read timeout: expected {n} bytes, got {len(data)}")

        return data
    finally:
        try:
            ser.close()
        except Exception:
            pass


def get_bits(n: int) -> bytes:
    """Generate n random bits from TrueRNG device.

    Returns bytes containing at least n random bits.
    May contain extra bits (rounds up to byte boundary).

    Args:
        n: Number of bits to generate. Must be positive.

    Returns:
        Bytes containing at least n random bits.

    Raises:
        ValueError: If n <= 0
        RuntimeError: If device not found
    """
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    n_bytes = (n + 7) // 8
    return get_bytes(n_bytes)


def get_exact_bits(n: int) -> bytes:
    """Generate exactly n random bits from TrueRNG device.

    Returns bytes containing exactly n random bits. The number of bits
    must be divisible by 8 (byte-aligned).

    Args:
        n: Number of bits to generate. Must be positive and divisible by 8.

    Returns:
        Bytes containing exactly n random bits.

    Raises:
        ValueError: If n <= 0 or if n is not divisible by 8
        RuntimeError: If device not found
    """
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    if n % 8 != 0:
        raise ValueError(f"n must be divisible by 8, got {n}")

    n_bytes = n // 8
    return get_bytes(n_bytes)


def _bytes_to_int(data: bytes) -> int:
    """Convert bytes to integer."""
    return int.from_bytes(data, "big")


def random_int(min_val: int = 0, max_val: Optional[int] = None) -> int:
    """Generate a cryptographically secure random integer from TrueRNG.

    Args:
        min_val: Minimum value (inclusive). Defaults to 0.
        max_val: Maximum value (exclusive). If None, generates 32-bit value.

    Returns:
        Random integer in range [min_val, max_val).

    Raises:
        ValueError: If min_val >= max_val
        RuntimeError: If device not found
    """
    if max_val is None:
        # Generate using hardware entropy
        return _bytes_to_int(get_bytes(4))

    if min_val >= max_val:
        raise ValueError(
            f"min_val must be less than max_val, got min_val={min_val}, max_val={max_val}"
        )

    range_size = max_val - min_val

    # Calculate bits needed
    import math

    bits_needed = max(1, math.ceil(math.log2(range_size)))
    n_bytes = (bits_needed + 7) // 8

    # Use rejection sampling for uniform distribution
    while True:
        data = get_bytes(n_bytes)
        val = _bytes_to_int(data)
        # Mask off extra bits to get exactly bits_needed bits
        val &= (1 << bits_needed) - 1
        if val < range_size:
            return min_val + val


def close() -> None:
    """Close and release any resources.

    For truerng, connections are closed after each read.
    This function is a no-op for sync operations.
    Use close_async() to properly shut down async executor.
    """
    pass


# Async versions of all functions


async def get_bytes_async(n: int) -> bytes:
    """Async version of get_bytes.

    Non-blocking for GUI applications. Uses thread pool executor
    to run sync operation in background thread.

    Args:
        n: Number of bytes to generate. Must be positive.

    Returns:
        Random bytes.

    Raises:
        ValueError: If n <= 0
        asyncio.CancelledError: If operation is cancelled
        RuntimeError: If device not found or read fails
    """
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(_executor, get_bytes, n)
    except asyncio.CancelledError:
        # Cleanup on cancellation
        close()
        raise


async def get_bits_async(n: int) -> bytes:
    """Async version of get_bits.

    Args:
        n: Number of bits to generate. Must be positive.

    Returns:
        Bytes containing at least n random bits.

    Raises:
        ValueError: If n <= 0
        asyncio.CancelledError: If operation is cancelled
        RuntimeError: If device not found or read fails
    """
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(_executor, get_bits, n)
    except asyncio.CancelledError:
        close()
        raise


async def get_exact_bits_async(n: int) -> bytes:
    """Async version of get_exact_bits.

    Args:
        n: Number of bits to generate. Must be positive and divisible by 8.

    Returns:
        Bytes containing exactly n random bits.

    Raises:
        ValueError: If n <= 0 or if n is not divisible by 8
        asyncio.CancelledError: If operation is cancelled
        RuntimeError: If device not found or read fails
    """
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(_executor, get_exact_bits, n)
    except asyncio.CancelledError:
        close()
        raise


async def random_int_async(min_val: int = 0, max_val: Optional[int] = None) -> int:
    """Async version of random_int.

    Args:
        min_val: Minimum value (inclusive). Defaults to 0.
        max_val: Maximum value (exclusive). If None, generates using full range.

    Returns:
        Random integer in range [min_val, max_val).

    Raises:
        ValueError: If min_val >= max_val or if min_val < 0 when max_val is None
        asyncio.CancelledError: If operation is cancelled
        RuntimeError: If device not found or read fails
    """
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(_executor, random_int, min_val, max_val)
    except asyncio.CancelledError:
        close()
        raise


async def close_async() -> None:
    """Async version of close.

    Calls sync close() and shuts down the executor.
    """
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(_executor, close)
    finally:
        _executor.shutdown(wait=False)
