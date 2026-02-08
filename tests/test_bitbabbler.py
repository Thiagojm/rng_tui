"""
Tests for bitbabbler_rng (BitBabbler hardware RNG).

These tests will be skipped if BitBabbler hardware is not connected.
"""

import pytest
from rng_devices.bitbabbler_rng import (
    is_device_available,
    get_bytes,
    get_bits,
    get_exact_bits,
    random_int,
    close,
)


class TestBitBabblerRNG:
    """Test BitBabbler hardware functionality."""

    @pytest.mark.hardware("bitbabbler_rng")
    def test_device_availability(self, skip_if_no_device):
        """Test that BitBabbler device is available."""
        assert is_device_available() is True

    @pytest.mark.hardware("bitbabbler_rng")
    def test_get_bytes(self, skip_if_no_device, small_test_size):
        """Test get_bytes function."""
        data = get_bytes(small_test_size)
        assert isinstance(data, bytes)
        assert len(data) == small_test_size

    @pytest.mark.hardware("bitbabbler_rng")
    def test_get_bytes_with_folds(self, skip_if_no_device, small_test_size):
        """Test get_bytes function with folding parameter."""
        # Test different fold levels (0-4)
        for folds in range(5):
            data = get_bytes(small_test_size, folds=folds)
            assert isinstance(data, bytes)
            assert len(data) == small_test_size

    @pytest.mark.hardware("bitbabbler_rng")
    def test_get_bits(self, skip_if_no_device):
        """Test get_bits function."""
        # Request 100 bits, should get at least 100 bits (rounded up to bytes)
        data = get_bits(100)
        assert isinstance(data, bytes)
        assert len(data) >= 13  # ceil(100/8) = 13 bytes
        # Total bits should be at least 100
        assert len(data) * 8 >= 100

    @pytest.mark.hardware("bitbabbler_rng")
    def test_get_bits_with_folds(self, skip_if_no_device):
        """Test get_bits function with folding."""
        for folds in range(5):
            data = get_bits(100, folds=folds)
            assert isinstance(data, bytes)
            assert len(data) >= 13

    @pytest.mark.hardware("bitbabbler_rng")
    def test_get_exact_bits(self, skip_if_no_device):
        """Test get_exact_bits function."""
        # Request exactly 128 bits (16 bytes)
        data = get_exact_bits(128)
        assert isinstance(data, bytes)
        assert len(data) == 16  # 128 bits = 16 bytes

    @pytest.mark.hardware("bitbabbler_rng")
    def test_get_exact_bits_with_folds(self, skip_if_no_device):
        """Test get_exact_bits function with folding."""
        for folds in range(5):
            data = get_exact_bits(128, folds=folds)
            assert isinstance(data, bytes)
            assert len(data) == 16

    @pytest.mark.hardware("bitbabbler_rng")
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

    @pytest.mark.hardware("bitbabbler_rng")
    def test_close(self, skip_if_no_device):
        """Test close function."""
        # Should not raise any exceptions
        close()

    @pytest.mark.hardware("bitbabbler_rng")
    def test_get_bytes_validation(self, skip_if_no_device):
        """Test input validation for get_bytes."""
        with pytest.raises(ValueError, match="n must be positive"):
            get_bytes(0)

        with pytest.raises(ValueError, match="n must be positive"):
            get_bytes(-1)

    @pytest.mark.hardware("bitbabbler_rng")
    def test_get_bits_validation(self, skip_if_no_device):
        """Test input validation for get_bits."""
        with pytest.raises(ValueError, match="n must be positive"):
            get_bits(0)

        with pytest.raises(ValueError, match="n must be positive"):
            get_bits(-1)

    @pytest.mark.hardware("bitbabbler_rng")
    def test_get_exact_bits_validation(self, skip_if_no_device):
        """Test input validation for get_exact_bits."""
        with pytest.raises(ValueError, match="n must be positive"):
            get_exact_bits(0)

        with pytest.raises(ValueError, match="n must be divisible by 8"):
            get_exact_bits(100)  # 100 % 8 != 0

    @pytest.mark.hardware("bitbabbler_rng")
    def test_random_int_validation(self, skip_if_no_device):
        """Test input validation for random_int."""
        with pytest.raises(ValueError, match="min must be less than max"):
            random_int(10, 10)

        with pytest.raises(ValueError, match="min must be less than max"):
            random_int(20, 10)

    @pytest.mark.hardware("bitbabbler_rng")
    def test_fold_parameter_validation(self, skip_if_no_device, small_test_size):
        """Test fold parameter validation."""
        # Valid folds (0-4)
        for folds in range(5):
            data = get_bytes(small_test_size, folds=folds)
            assert isinstance(data, bytes)

        # Invalid folds should raise ValueError (this depends on implementation)
        # Note: The current implementation may not validate fold range
        # If it does, add tests for invalid fold values
