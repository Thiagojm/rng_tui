"""Pseudo RNG core implementation.

Software-based cryptographically secure random number generator using Python's
secrets module. Serves as a fallback when hardware RNGs are not available.
"""

import asyncio
import secrets
from concurrent.futures import ThreadPoolExecutor

# Module-level executor (1 worker for async operations)
_executor = ThreadPoolExecutor(max_workers=1)


def _get_executor() -> ThreadPoolExecutor:
    """Get the executor, recreating it if it was shut down."""
    global _executor
    if _executor._shutdown:
        _executor = ThreadPoolExecutor(max_workers=1)
    return _executor


def is_device_available() -> bool:
    """Check if the pseudo RNG is available.

    The pseudo RNG is always available as it uses Python's standard library.

    Returns:
        Always True
    """
    return True


def get_bytes(n: int) -> bytes:
    """Generate n random bytes of entropy.

    Args:
        n: Number of bytes to generate. Must be positive.

    Returns:
        Random bytes string of length n.

    Raises:
        ValueError: If n <= 0
    """
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    return secrets.token_bytes(n)


def get_bits(n: int) -> bytes:
    """Generate n bits of entropy.

    Returns bytes containing at least n random bits. The result may
    contain extra bits (rounds up to nearest byte boundary).

    Args:
        n: Number of bits to generate. Must be positive.

    Returns:
        Bytes containing at least n random bits.

    Raises:
        ValueError: If n <= 0
    """
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    n_bytes = (n + 7) // 8
    return secrets.token_bytes(n_bytes)


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
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    if n % 8 != 0:
        raise ValueError(f"n must be divisible by 8, got {n}")

    n_bytes = n // 8
    return secrets.token_bytes(n_bytes)


def random_int(min_val: int = 0, max_val: int | None = None) -> int:
    """Generate a cryptographically secure random integer.

    Args:
        min_val: Minimum value (inclusive). Defaults to 0.
        max_val: Maximum value (exclusive). If None, generates using full range.

    Returns:
        Random integer in range [min_val, max_val) if max_val is specified.

    Raises:
        ValueError: If min_val >= max_val or if min_val < 0 when max_val is None
    """
    if max_val is None:
        if min_val < 0:
            raise ValueError("min_val must be non-negative when max_val is None")
        return secrets.randbelow(min_val) if min_val > 0 else secrets.randbits(32)

    if min_val >= max_val:
        raise ValueError(
            f"min_val must be less than max_val, got min_val={min_val}, max_val={max_val}"
        )

    return min_val + secrets.randbelow(max_val - min_val)


def close() -> None:
    """Close and release any resources.

    For pseudo_rng, this is a no-op for sync operations.
    Provided for API consistency with hardware RNG modules.
    Note: Does not shut down async executor to allow reuse.
    Use close_async() to properly shut down async resources.
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
    """
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(_get_executor(), get_bytes, n)
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
    """
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(_get_executor(), get_bits, n)
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
    """
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(_get_executor(), get_exact_bits, n)
    except asyncio.CancelledError:
        close()
        raise


async def random_int_async(min_val: int = 0, max_val: int | None = None) -> int:
    """Async version of random_int.

    Args:
        min_val: Minimum value (inclusive). Defaults to 0.
        max_val: Maximum value (exclusive). If None, generates using full range.

    Returns:
        Random integer in range [min_val, max_val).

    Raises:
        ValueError: If min_val >= max_val or if min_val < 0 when max_val is None
        asyncio.CancelledError: If operation is cancelled
    """
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(_get_executor(), random_int, min_val, max_val)
    except asyncio.CancelledError:
        close()
        raise


async def close_async() -> None:
    """Async version of close.

    Calls sync close() and shuts down the executor.
    """
    global _executor
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(_get_executor(), close)
    finally:
        _executor.shutdown(wait=False)
