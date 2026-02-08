"""
RNG modules for hardware and software random number generation.

This package provides multiple random number generator implementations:
- intel_seed: Intel RDSEED CPU instruction (Intel Broadwell+ or AMD Zen+)
- truerng: TrueRNG hardware devices via USB serial
- bitbabbler_rng: BitBabbler hardware devices via USB FTDI
- pseudo_rng: Software fallback using Python's secrets module

All modules expose a consistent API:
- is_device_available() -> bool
- get_bytes(n: int) -> bytes
- get_bits(n: int) -> bytes
- get_exact_bits(n: int) -> bytes
- random_int(min_val: int = 0, max_val: Optional[int] = None) -> int
- close() -> None

Usage:
    from rng_devices import intel_seed, truerng, bitbabbler_rng, pseudo_rng

    # Check which devices are available
    if intel_seed.is_device_available():
        data = intel_seed.get_bytes(32)
    elif truerng.is_device_available():
        data = truerng.get_bytes(32)
    else:
        data = pseudo_rng.get_bytes(32)
"""

from . import intel_seed
from . import truerng
from . import bitbabbler_rng
from . import pseudo_rng

__all__ = [
    "intel_seed",
    "truerng",
    "bitbabbler_rng",
    "pseudo_rng",
]
