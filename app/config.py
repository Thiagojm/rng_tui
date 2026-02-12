"""
Configuration for RNG TUI application.
"""

from typing import Any

from lib.rng_devices import bitbabbler_rng, intel_seed, pseudo_rng, truerng

DEVICES: dict[str, dict[str, Any]] = {
    "intel_seed": {"name": "Intel RDSEED", "module": intel_seed, "type": "Hardware"},
    "truerng": {"name": "TrueRNG", "module": truerng, "type": "Hardware"},
    "bitbabbler_rng": {
        "name": "BitBabbler",
        "module": bitbabbler_rng,
        "type": "Hardware",
    },
    "pseudo_rng": {"name": "Pseudo RNG", "module": pseudo_rng, "type": "Software"},
}
