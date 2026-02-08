# RNG TUI - Random Number Generator Data Collector

A modern Terminal User Interface (TUI) application for collecting random number generator data from various hardware and software entropy sources. Built with [Textual](https://textual.textualize.io/) for a rich, interactive experience.

![Screenshot](https://via.placeholder.com/800x400/000000/00FF00?text=RNG+TUI+Screenshot)

## ✨ Features

- **Multiple RNG Sources**: Support for hardware RNG devices and software fallbacks
- **Real-time Statistics**: Live display of entropy quality metrics
- **Interactive TUI**: Rich terminal interface with color-coded indicators
- **CSV Export**: Save collected data with timestamps and statistics
- **Configurable Collection**: Adjustable sample size, frequency, and duration
- **Cross-platform**: Windows and Linux support
- **Async Operation**: Non-blocking collection with pause/resume controls

## 🔧 Supported Devices

| Device | Type | Interface | Features |
|--------|------|-----------|----------|
| **Intel RDSEED** | Hardware | CPU Instruction | CPU-based entropy (Broadwell+ or Zen+) |
| **TrueRNG** | Hardware | USB Serial | ubld.it TrueRNG3/Pro devices |
| **BitBabbler** | Hardware | USB FTDI | BitBabbler RNG with XOR folding |
| **Pseudo RNG** | Software | Python secrets | Cryptographically secure fallback |

## 🚀 Installation

### Requirements

- Python 3.13+
- Supported RNG hardware (optional, software fallback available)

### Install with uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/rng-tui.git
cd rng-tui

# Install with uv
uv sync

# Run the application
uv run python main.py
```

### Alternative: Install with pip

```bash
# Install dependencies
pip install textual pyserial pyusb

# Run directly
python main.py
```

### Hardware Setup

#### Intel RDSEED
- Requires Intel Broadwell+ (5th gen) or AMD Zen+ processors
- No additional setup required

#### TrueRNG
- Connect TrueRNG device via USB
- Device appears as serial port (auto-detected)

#### BitBabbler
- Connect BitBabbler device via USB
- Requires libusb drivers (included for Windows)

## 🎯 Usage

### Basic Operation

```bash
# Launch the application
uv run python main.py

# Or directly
python main.py
```

### Interface Overview

The TUI consists of three main panels:

1. **Configuration Panel** (Left)
   - Device selection
   - Sample size (bits)
   - Collection frequency (seconds)
   - Duration (0 = infinite)
   - Output file path

2. **Statistics Panel** (Right)
   - Real-time ratio analysis (color-coded)
   - Running average
   - Sample count and elapsed time
   - Progress bar for timed collections
   - Start/Pause/Stop controls

3. **Data Table** (Bottom)
   - Live data display
   - Sample number, timestamp, bytes, ones/zeros ratio
   - Hexadecimal preview

### Keyboard Shortcuts

- `q` - Quit application
- `s` - Start collection
- `p` - Pause/Resume collection
- `x` - Stop collection

### Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| Device | RNG source to use | pseudo_rng |
| Sample Size | Bits per sample (must be divisible by 8) | 2048 |
| Frequency | Seconds between samples | 1.0 |
| Duration | Collection time in seconds (0 = infinite) | 60 |
| Output File | CSV export path (auto-generated if empty) | auto |

### BitBabbler Specific

- **Folds**: XOR folding level (0-4)
  - 0: Raw entropy
  - 1-4: Progressive whitening

## 📊 Output Format

Data is exported to CSV with the following columns:

```csv
datetime,ones,zeros,ratio_percent,sample_bytes,device
2024-01-15T10:30:45.123456,1024,1024,50.00,256,pseudo_rng
```

## 🧪 Testing

Manual test scripts are provided for each device:

```bash
# Test BitBabbler
python tests/manual/test_bit_manual.py

# Test TrueRNG
python tests/manual/test_true_manual.py
```

## 🛠️ Development

### Setup Development Environment

```bash
# Install in development mode
uv sync --dev

# Run linting
uv tool run ruff check

# Run formatting
uv format

# Run tests (when implemented)
uv run pytest
```

### Project Structure

```
rng_tui/
├── main.py                 # Application entry point
├── rng_tui.py             # Main TUI application
├── style.css              # Textual styling
├── pyproject.toml         # Project configuration
├── lib/                   # Library modules
│   ├── __init__.py
│   └── rng_devices/       # RNG device implementations
│       ├── __init__.py
│       ├── pseudo_rng/    # Software fallback
│       ├── truerng/       # TrueRNG hardware
│       ├── bitbabbler_rng/# BitBabbler hardware
│       └── intel_seed/    # Intel RDSEED CPU
├── tests/                 # Automated test suite
│   ├── conftest.py        # Test configuration
│   └── test_*.py          # Test files
└── AGENTS.md              # Developer guidelines
```

### API Reference

All RNG devices implement a consistent API:

```python
from lib.rng_devices import pseudo_rng

# Check availability
if pseudo_rng.is_device_available():
    # Generate entropy
    data = pseudo_rng.get_bytes(32)      # 32 random bytes
    data = pseudo_rng.get_bits(256)      # At least 256 bits
    data = pseudo_rng.get_exact_bits(256) # Exactly 256 bits

    # Generate integers
    num = pseudo_rng.random_int(0, 100)  # Random int 0-99

    # Cleanup
    pseudo_rng.close()
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the code style guidelines in `AGENTS.md`
4. Run linting and formatting
5. Submit a pull request

## 📈 Performance Considerations

- Hardware RNGs provide better entropy than software fallbacks
- Collection frequency affects UI responsiveness
- Large sample sizes may impact performance on slower devices
- Async operations prevent UI blocking during collection

## 🔒 Security

- Uses cryptographically secure random number generation
- Hardware RNGs preferred over software when available
- Proper input validation and error handling
- No sensitive data logging

## 📝 License

[MIT License](LICENSE) - see LICENSE file for details.

## 🙏 Acknowledgments

- [Textual](https://textual.textualize.io/) - Terminal UI framework
- ubld.it - TrueRNG hardware
- BitBabbler - Open source RNG hardware
- Intel - RDSEED CPU instruction

## 📞 Support

- [Issues](https://github.com/yourusername/rng-tui/issues)
- [Discussions](https://github.com/yourusername/rng-tui/discussions)

---

**Note**: This application is for research and development purposes. For cryptographic applications requiring high-quality entropy, consult security experts and consider using multiple entropy sources.