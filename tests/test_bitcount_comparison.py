"""
Performance and correctness test for bit counting methods.

Compares two approaches to counting 1-bits in byte data:
1. int.from_bytes(data, "big").bit_count()
2. sum(bin(b).count("1") for b in data)
"""

import timeit

import pytest

from lib.rng_devices.pseudo_rng import get_bytes


class TestBitCountComparison:
    """Test bit counting method equivalence and performance."""

    @staticmethod
    def method_int_bitcount(data: bytes) -> int:
        """Count 1-bits using int.from_bytes and bit_count."""
        return int.from_bytes(data, "big").bit_count()

    @staticmethod
    def method_bin_sum(data: bytes) -> int:
        """Count 1-bits using bin string conversion."""
        return sum(bin(b).count("1") for b in data)

    def test_small_data_correctness(self, small_test_size):
        """Verify both methods return same result for small data."""
        data = get_bytes(small_test_size)

        ones_int = self.method_int_bitcount(data)
        ones_bin = self.method_bin_sum(data)

        assert ones_int == ones_bin, (
            f"Methods returned different results: "
            f"int.bit_count()={ones_int}, bin_sum={ones_bin}"
        )

    @pytest.mark.hardware("pseudo_rng")
    def test_medium_data_correctness(self, skip_if_no_device):
        """Verify both methods return same result for medium data (256 bytes)."""
        data = get_bytes(256)

        ones_int = self.method_int_bitcount(data)
        ones_bin = self.method_bin_sum(data)

        assert ones_int == ones_bin, (
            f"Methods returned different results: "
            f"int.bit_count()={ones_int}, bin_sum={ones_bin}"
        )

    @pytest.mark.hardware("pseudo_rng")
    def test_large_data_correctness(self, skip_if_no_device):
        """Verify both methods return same result for large data (2048 bytes)."""
        data = get_bytes(2048)

        ones_int = self.method_int_bitcount(data)
        ones_bin = self.method_bin_sum(data)

        assert ones_int == ones_bin, (
            f"Methods returned different results: "
            f"int.bit_count()={ones_int}, bin_sum={ones_bin}"
        )

    @pytest.mark.hardware("pseudo_rng")
    def test_performance_comparison(self, skip_if_no_device):
        """Compare execution time of both methods."""
        data_sizes = [32, 256, 1024, 2048]
        iterations = 1000

        print("\n" + "=" * 60)
        print("Bit Counting Performance Comparison")
        print("=" * 60)
        print(f"Iterations per test: {iterations}")
        print("-" * 60)

        results = []

        for size in data_sizes:
            data = get_bytes(size)

            # Time int.from_bytes method
            time_int = timeit.timeit(
                lambda: self.method_int_bitcount(data), number=iterations
            )

            # Time bin string method
            time_bin = timeit.timeit(
                lambda: self.method_bin_sum(data), number=iterations
            )

            ratio = time_bin / time_int if time_int > 0 else float("inf")
            faster = "int.bit_count" if time_int < time_bin else "bin.sum"

            results.append(
                {
                    "size": size,
                    "int_time": time_int,
                    "bin_time": time_bin,
                    "ratio": ratio,
                    "faster": faster,
                }
            )

            print(f"\nData size: {size} bytes")
            print(f"  int.from_bytes(...).bit_count():  {time_int:.4f}s")
            print(f"  sum(bin(b).count('1') for b...):  {time_bin:.4f}s")
            print(f"  Speed difference: {ratio:.2f}x faster ({faster})")

        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)
        avg_ratio = sum(r["ratio"] for r in results) / len(results)
        print(f"Average speedup: int.bit_count is {avg_ratio:.2f}x faster")
        print("=" * 60)

        # Verify all results match
        for r in results:
            data = get_bytes(r["size"])
            assert self.method_int_bitcount(data) == self.method_bin_sum(data)

    def test_edge_cases(self):
        """Test edge cases for both methods."""
        # Empty bytes
        assert self.method_int_bitcount(b"") == 0
        assert self.method_bin_sum(b"") == 0

        # All zeros
        assert self.method_int_bitcount(b"\x00" * 8) == 0
        assert self.method_bin_sum(b"\x00" * 8) == 0

        # All ones
        assert self.method_int_bitcount(b"\xff" * 8) == 64
        assert self.method_bin_sum(b"\xff" * 8) == 64

        # Alternating pattern
        assert self.method_int_bitcount(b"\xaa") == 4  # 10101010
        assert self.method_bin_sum(b"\xaa") == 4

        assert self.method_int_bitcount(b"\x55") == 4  # 01010101
        assert self.method_bin_sum(b"\x55") == 4
