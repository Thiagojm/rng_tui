# RNG TUI - Random Number Generator Data Collector

A modern Terminal User Interface (TUI) application for collecting and analyzing random number generator data from various hardware and software entropy sources. Built with [Textual](https://textual.textualize.io/) for a rich, interactive experience.

![Screenshot](https://via.placeholder.com/800x400/000000/00FF00?text=RNG+TUI+Screenshot) <!-- Replace with actual screenshot -->

## ✨ Features

- **Multiple RNG Sources**: Support for hardware RNG devices and software fallbacks
- **Real-time Statistics**: Live display of entropy quality metrics
- **Interactive TUI**: Rich terminal interface with tabs for Collection and Analysis
- **Statistical Analysis**: Z-score calculations, p-values, and randomness assessment
- **File Browser**: Navigate and select CSV files for analysis
- **Excel Export**: Comprehensive reports with charts and statistics sheets
- **CSV Export**: Save collected data with standardized timestamps and statistics
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

### 🪟 Windows Installation

#### Hardware Setup

1. **TrueRNG/TrueRNGPro**:
   - Navigate to `app/tools/installers/TrueRng/` folder
   - Right-click `TrueRNG.inf` or `TrueRNGpro.inf`
   - Select "Install" and follow the prompts

2. **BitBabbler**:
   - Run `vcredist_x64.exe` from `app/tools/installers/BitBabbler/`
   - Insert BitBabbler device into USB port
   - Run `zadig-2.8.exe` and install driver for your device

### 🐧 Linux Installation

#### Automated Setup (Recommended)
```bash
./app/tools/installers/setup_rng_devices_linux_python.sh
```

This script will:
- ✅ Set up udev rules for device access
- ✅ Create required user groups
- ✅ Configure device permissions

#### Manual Setup
```bash
# Install system dependencies
sudo apt-get install libusb-1.0-0-dev

# Add user to bit-babbler group
sudo usermod -aG bit-babbler $USER

# Log out and back in for group changes to take effect
```

### Requirements

- Python 3.13+
- Supported RNG hardware (optional, software fallback available)

### Install with uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/Thiagojm/rng_tui.git
cd rng_tui

# Install with uv
uv sync

# Run the application
uv run rng_tui.py
```

### Alternative: Install with pip

```bash
# Install dependencies
pip install textual pyserial pyusb

# Run directly
python rng_tui.py
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
uv run rng_tui.py

# Or directly
python rng_tui.py
```

### Interface Overview

The TUI consists of two main tabs:

#### **Collect Tab**
Collects RNG data with real-time statistics:

1. **Configuration Panel** (Left)
   - Device selection
   - Sample size (bits, must be divisible by 8)
   - Collection frequency (seconds)
   - Duration (0 = infinite)
   - Output file path (auto-generated with timestamp)

2. **Statistics Panel** (Right)
   - Real-time entropy analysis (color-coded)
   - Running average and standard deviation
   - Sample count and elapsed time
   - Progress bar for timed collections
   - Start/Pause/Stop controls

3. **Data Table** (Bottom)
   - Live data display
   - Sample number, timestamp, bit counts, hex preview

#### **Analysis Tab**
Analyzes previously collected CSV data:

1. **File Browser** (Left)
   - Directory tree navigation
   - Select CSV files for analysis

2. **Analysis Panel** (Right)
   - File selection display
   - Analysis parameters (bits per sample, interval)
   - Statistical results with Z-scores and p-values
   - Randomness assessment (PASS/REVIEW)
   - Excel export button

3. **Statistics Display** (Bottom)
   - Comprehensive statistical summary
   - Sample count, mean, Z-score analysis
   - 95% confidence interval coverage

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

### BitBabbler Specific

- **Folds**: XOR folding level (0-4)
  - 0: Raw entropy
  - 1-4: Progressive whitening

## 📊 Output Formats

### CSV Format
Data is exported to CSV with timestamp and bit count:

```csv
time,count
20240115T103045,1024
20240115T103046,1032
```

**Filename Convention**: `YYYYMMDDTHHMMSS_{device}_s{bits}_i{interval}[_f{folds}].csv`
- `YYYYMMDDTHHMMSS`: Timestamp when collection started
- `{device}`: Device name (pseudo_rng, truerng, bitbabbler_rng, intel_seed)
- `s{bits}`: Sample size in bits
- `i{interval}`: Interval between samples in seconds
- `f{folds}`: BitBabbler XOR folding level (optional)

### Excel Export
Analysis results can be exported to Excel with:
- **Analysis Sheet**: All data columns (time, ones, cumulative_mean, z_test, p_value)
- **Statistics Sheet**: Summary metrics, Z-score analysis, randomness assessment
- **Chart**: Z-score over time with reference lines (when supported)

Files are saved to `data/processed/` folder with `.xlsx` extension.

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
├── rng_tui.py             # Thin entry point
├── app/                   # TUI application code
│   ├── __init__.py
│   ├── main.py            # Main App class
│   ├── panels.py          # UI panels
│   ├── config.py          # Device config
│   ├── static/
│   │   └── style.css      # Styling
│   └── tools/
│       └── installers/    # Device setup scripts
│           ├── setup_rng_devices_linux_python.sh
│           ├── TrueRng/   # Windows drivers
│           └── BitBabbler/ # Windows drivers
├── lib/                   # Core library
│   ├── __init__.py
│   ├── services/          # Storage/filename services
│   │   ├── __init__.py
│   │   ├── storage.py     # CSV/Excel processing
│   │   └── filenames.py   # Filename generation
│   └── rng_devices/       # RNG implementations
│       ├── __init__.py
│       ├── pseudo_rng/    # Software fallback
│       │   ├── __init__.py
│       │   └── core.py
│       ├── truerng/       # TrueRNG hardware
│       │   ├── __init__.py
│       │   └── core.py
│       ├── bitbabbler_rng/# BitBabbler hardware
│       │   ├── __init__.py
│       │   ├── core.py
│       │   ├── ftdi.py
│       │   └── bitbabbler.py
│       └── intel_seed/    # Intel RDSEED CPU
│           ├── __init__.py
│           ├── intel_seed.py
│           ├── librdseed.so  # Precompiled library
│           └── librdseed.dll
├── tests/                 # Pytest suite
│   ├── __init__.py
│   ├── conftest.py        # Test configuration
│   ├── test_*.py          # Unit tests
│   └── manual/            # Manual test scripts
│       ├── __init__.py
│       ├── test_bit_manual.py
│       └── test_true_manual.py
├── data/                  # Data directories
│   ├── raw/               # CSV data from collection
│   └── processed/         # Excel analysis reports
├── CHANGELOG.md           # Release notes
├── AGENTS.md              # Agent guidelines
├── pyproject.toml         # Dependencies
└── README.md              # This file
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
