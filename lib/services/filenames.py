import re
from datetime import datetime


def format_capture_name(
    device: str, bits: int, interval: int, folds: int | None = None
) -> str:
    """Return canonical filename stem for a capture.

    Args:
        device: Device code ('bitb', 'trng', 'intel', 'pseudo')
        bits: Number of bits per sample
        interval: Sample interval in seconds
        folds: Folding level for BitBabbler (0-4), None for other devices

    Returns:
        Filename stem in format: YYYYMMDDTHHMMSS_{device}_s{bits}_i{interval}[_f{folds}]

    Example: 20250208T143022_bitb_s2048_i1_f0
    """
    ts = datetime.now().strftime("%Y%m%dT%H%M%S")
    name = f"{ts}_{device}_s{bits}_i{interval}"
    if device == "bitb" and folds is not None:
        name += f"_f{folds}"
    return name


def parse_bits(name: str) -> int:
    m = re.search(r"_s(\d+)_", name)
    if not m:
        raise ValueError("bits not found in name")
    return int(m.group(1))


def parse_interval(name: str) -> int:
    m = re.search(r"_i(\d+)", name)
    if not m:
        raise ValueError("interval not found in name")
    return int(m.group(1))
