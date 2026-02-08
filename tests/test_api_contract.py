"""
Tests for API contract compliance across all RNG devices.

Ensures all device modules expose the same interface and behave consistently.
"""

import pytest
import inspect
from lib.rng_devices import pseudo_rng, intel_seed, truerng, bitbabbler_rng


class TestAPIContract:
    """Test that all RNG devices follow the same API contract."""

    def test_all_devices_have_required_functions(self):
        """Test that all devices expose the required functions."""
        required_functions = [
            "is_device_available",
            "get_bytes",
            "get_bits",
            "get_exact_bits",
            "random_int",
            "close",
            "get_bytes_async",
            "get_bits_async",
            "get_exact_bits_async",
            "random_int_async",
            "close_async",
        ]

        devices = [pseudo_rng, intel_seed, truerng, bitbabbler_rng]

        for device in devices:
            device_name = device.__name__
            for func_name in required_functions:
                assert hasattr(device, func_name), f"{device_name} missing {func_name}"
                func = getattr(device, func_name)
                assert callable(func), f"{device_name}.{func_name} is not callable"

    def test_function_signatures_consistent(self):
        """Test that function signatures are consistent across devices."""
        # Check get_bytes signatures - parameter names may vary but should be int -> bytes
        devices = [pseudo_rng, intel_seed, truerng]

        for device in devices:
            sig = inspect.signature(device.get_bytes)
            # Should have exactly one positional parameter of type int
            params = list(sig.parameters.values())
            assert len(params) == 1, (
                f"{device.__name__}.get_bytes should have 1 parameter"
            )
            param = params[0]
            assert param.annotation == int, (
                f"{device.__name__}.get_bytes parameter should be int"
            )
            assert sig.return_annotation == bytes, (
                f"{device.__name__}.get_bytes should return bytes"
            )

        # BitBabbler should have 2 parameters: n and folds
        bitbabbler_sig = inspect.signature(bitbabbler_rng.get_bytes)
        params = list(bitbabbler_sig.parameters.values())
        assert len(params) == 2, "bitbabbler_rng.get_bytes should have 2 parameters"
        assert "n" in bitbabbler_sig.parameters, (
            "bitbabbler_rng.get_bytes should have 'n' parameter"
        )
        assert "folds" in bitbabbler_sig.parameters, (
            "bitbabbler_rng.get_bytes should have 'folds' parameter"
        )
        assert bitbabbler_sig.return_annotation == bytes, (
            "bitbabbler_rng.get_bytes should return bytes"
        )

    def test_return_types_consistent(self):
        """Test that functions return consistent types when called with valid inputs."""
        # Test with devices that should be available (pseudo_rng always is)
        devices_to_test = []

        if pseudo_rng.is_device_available():
            devices_to_test.append(("pseudo_rng", pseudo_rng))

        if intel_seed.is_device_available():
            devices_to_test.append(("intel_seed", intel_seed))

        if truerng.is_device_available():
            devices_to_test.append(("truerng", truerng))

        if bitbabbler_rng.is_device_available():
            devices_to_test.append(("bitbabbler_rng", bitbabbler_rng))

        for device_name, device in devices_to_test:
            # Test get_bytes returns bytes
            data = device.get_bytes(16)
            assert isinstance(data, bytes), (
                f"{device_name}.get_bytes should return bytes"
            )
            assert len(data) == 16, (
                f"{device_name}.get_bytes should return correct length"
            )

            # Test get_bits returns bytes
            data = device.get_bits(100)
            assert isinstance(data, bytes), (
                f"{device_name}.get_bits should return bytes"
            )
            assert len(data) * 8 >= 100, (
                f"{device_name}.get_bits should return at least requested bits"
            )

            # Test get_exact_bits returns bytes
            data = device.get_exact_bits(128)
            assert isinstance(data, bytes), (
                f"{device_name}.get_exact_bits should return bytes"
            )
            assert len(data) == 16, (
                f"{device_name}.get_exact_bits should return exactly requested bytes"
            )

            # Test random_int returns int
            result = device.random_int(0, 100)
            assert isinstance(result, int), (
                f"{device_name}.random_int should return int"
            )
            assert 0 <= result < 100, (
                f"{device_name}.random_int should return value in range"
            )

    def test_error_handling_consistent(self):
        """Test that error handling is consistent across devices."""
        devices = [pseudo_rng, intel_seed, truerng, bitbabbler_rng]

        for device in devices:
            device_name = device.__name__

            # All should raise ValueError for invalid inputs
            with pytest.raises(ValueError):
                device.get_bytes(0)

            with pytest.raises(ValueError):
                device.get_bits(-1)

            with pytest.raises(ValueError):
                device.get_exact_bits(100)  # Not divisible by 8

            with pytest.raises(ValueError):
                device.random_int(10, 5)  # min > max

    def test_async_functions_exist(self):
        """Test that async versions of functions exist."""
        devices = [pseudo_rng, intel_seed, truerng, bitbabbler_rng]

        async_functions = [
            "get_bytes_async",
            "get_bits_async",
            "get_exact_bits_async",
            "random_int_async",
            "close_async",
        ]

        for device in devices:
            device_name = device.__name__
            for func_name in async_functions:
                assert hasattr(device, func_name), (
                    f"{device_name} missing async {func_name}"
                )
                func = getattr(device, func_name)
                assert inspect.iscoroutinefunction(func), (
                    f"{device_name}.{func_name} should be async"
                )
