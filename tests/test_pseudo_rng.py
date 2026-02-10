"""
Tests for pseudo_rng (software RNG fallback).

Since this is software-only, all tests should pass regardless of hardware.
"""

import pytest

from lib.rng_devices.pseudo_rng import (
    close,
    get_bits,
    get_bytes,
    get_exact_bits,
    is_device_available,
    random_int,
)


class TestPseudoRNG:
    """Test pseudo RNG functionality."""

    @pytest.mark.hardware("pseudo_rng")
    def test_device_availability(self, skip_if_no_device):
        """Test that pseudo RNG is always available."""
        assert is_device_available() is True

    @pytest.mark.hardware("pseudo_rng")
    def test_get_bytes(self, skip_if_no_device, small_test_size):
        """Test get_bytes function."""
        data = get_bytes(small_test_size)
        assert isinstance(data, bytes)
        assert len(data) == small_test_size

    @pytest.mark.hardware("pseudo_rng")
    def test_get_bits(self, skip_if_no_device):
        """Test get_bits function."""
        # Request 100 bits, should get at least 100 bits (rounded up to bytes)
        data = get_bits(100)
        assert isinstance(data, bytes)
        assert len(data) >= 13  # ceil(100/8) = 13 bytes
        # Total bits should be at least 100
        assert len(data) * 8 >= 100

    @pytest.mark.hardware("pseudo_rng")
    def test_get_exact_bits(self, skip_if_no_device):
        """Test get_exact_bits function."""
        # Request exactly 128 bits (16 bytes)
        data = get_exact_bits(128)
        assert isinstance(data, bytes)
        assert len(data) == 16  # 128 bits = 16 bytes

    @pytest.mark.hardware("pseudo_rng")
    def test_random_int(self, skip_if_no_device):
        """Test random_int function."""
        # Test with default range (0 to sys.maxsize)
        result = random_int()
        assert isinstance(result, int)
        assert result >= 0

        # Test with specified range
        result = random_int(10, 20)
        assert isinstance(result, int)
        assert 10 <= result < 20

    @pytest.mark.hardware("pseudo_rng")
    def test_random_int_edge_cases(self, skip_if_no_device):
        """Test random_int edge cases."""
        # Single value range
        result = random_int(5, 6)
        assert result == 5

        # Large range
        result = random_int(0, 1000000)
        assert 0 <= result < 1000000

    @pytest.mark.hardware("pseudo_rng")
    def test_close(self, skip_if_no_device):
        """Test close function (should be no-op for pseudo_rng)."""
        # Should not raise any exceptions
        close()

    @pytest.mark.hardware("pseudo_rng")
    def test_get_bytes_validation(self, skip_if_no_device):
        """Test input validation for get_bytes."""
        with pytest.raises(ValueError, match="n must be positive"):
            get_bytes(0)

        with pytest.raises(ValueError, match="n must be positive"):
            get_bytes(-1)

    @pytest.mark.hardware("pseudo_rng")
    def test_get_bits_validation(self, skip_if_no_device):
        """Test input validation for get_bits."""
        with pytest.raises(ValueError, match="n must be positive"):
            get_bits(0)

        with pytest.raises(ValueError, match="n must be positive"):
            get_bits(-1)

    @pytest.mark.hardware("pseudo_rng")
    def test_get_exact_bits_validation(self, skip_if_no_device):
        """Test input validation for get_exact_bits."""
        with pytest.raises(ValueError, match="n must be positive"):
            get_exact_bits(0)

        with pytest.raises(ValueError, match="n must be divisible by 8"):
            get_exact_bits(100)  # 100 % 8 != 0

    @pytest.mark.hardware("pseudo_rng")
    def test_random_int_validation(self, skip_if_no_device):
        """Test input validation for random_int."""
        with pytest.raises(ValueError, match="min_val must be less than max_val"):
            random_int(10, 10)

        with pytest.raises(ValueError, match="min_val must be less than max_val"):
            random_int(20, 10)
