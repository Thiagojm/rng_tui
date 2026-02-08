"""
Pytest configuration and fixtures for RNG TUI tests.

This module provides:
- Custom pytest marker for hardware-dependent tests
- Fixtures that skip tests when hardware is not available
- Shared test utilities
"""

import pytest


def pytest_configure(config):
    """Add custom markers."""
    config.addinivalue_line(
        "markers", "hardware(name): mark test as requiring specific hardware device"
    )


@pytest.fixture
def skip_if_no_device(request):
    """Skip test if required hardware device is not available."""
    marker = request.node.get_closest_marker("hardware")
    if marker:
        device_name = marker.args[0]

        # Import the device module dynamically
        try:
            if device_name == "pseudo_rng":
                from lib.rng_devices.pseudo_rng import is_device_available
            elif device_name == "truerng":
                from lib.rng_devices.truerng import is_device_available
            elif device_name == "bitbabbler_rng":
                from lib.rng_devices.bitbabbler_rng import is_device_available
            elif device_name == "intel_seed":
                from lib.rng_devices.intel_seed import is_device_available
            else:
                pytest.fail(f"Unknown device: {device_name}")

            if not is_device_available():
                pytest.skip(f"{device_name} hardware not connected or not available")

        except ImportError as e:
            pytest.skip(f"Failed to import {device_name}: {e}")


@pytest.fixture
def small_test_size():
    """Return small test size for fast testing (32 bytes)."""
    return 32
