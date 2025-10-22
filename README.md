# DiagAutoClinicOS 🚗💻

**"Where Mechanics Meet an Intelligent Future"**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Coverage](https://img.shields.io/badge/Coverage-93%25-brightgreen.svg)]()

## 🌟 Overview

DiagAutoClinicOS is a comprehensive, open-source automotive diagnostic platform designed for professional technicians and enthusiasts. Our suite provides modern, intuitive interfaces for vehicle diagnostics, ECU programming, and key programming with support for 25+ major automotive brands.

**Professional-grade tools. No vendor lock-in. Fully transparent.**

### 🎯 Key Features

- **Multi-Application Suite**: Three specialized tools in one platform
- **Brand-Specific Diagnostics**: Intelligent support for 25+ global automotive brands
- **Modern UI/UX**: Dark/Light themes with professional styling
- **Cross-Platform**: Runs on Windows, Linux, and macOS
- **Hardware Integration**: J2534 pass-thru and CAN bus support
- **Open Source**: Fully transparent and community-driven
- **93% Test Coverage**: Production-ready code with comprehensive testing

---

## 🛠 Applications

### 1. AutoDiag - Vehicle Diagnostics
- Complete OBD-II compliance (SAE J1979)
- Real-time parameter monitoring
- DTC reading/clearing with enhanced descriptions
- Live data graphing and logging
- Brand-specific diagnostic procedures
- Freeze frame data analysis

### 2. AutoECU - ECU Programming
- ECU reading/writing operations
- Parameter calibration editing
- Immobilizer system programming
- Flash memory operations
- Checksum verification
- Backup and restore functionality

### 3. AutoKey - Key Programming
- Transponder key programming
- Remote key fob synchronization
- Immobilizer code calculation
- Key cloning capabilities
- Security system reset procedures

---

## 🚀 Quick Start

### Prerequisites
- **OS**: Windows 10+, Ubuntu 18.04+, macOS 10.15+
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space
- **Hardware**: J2534 compatible interface or ELM327 adapter

### Installation

```bash
# Clone the repository
git clone https://github.com/DiagAutoClinic/DiagAutoClinicOS.git
cd DiagAutoClinicOS

# Install dependencies
pip install -r requirements.txt

# Run the launcher
python launcher.py
```

### ISO Download
Pre-configured live environment: **Coming Soon**

---

## 📁 Project Structure

```plaintext
DiagAutoClinicOS/
├── .github/
│   ├── workflows/              # CI/CD pipelines
│   │   ├── autodiag-tests.yml
│   │   ├── coverage-report.yml
│   │   └── full-suite-tests.yml
│   └── FUNDING.yml
├── AutoDiag/                   # Vehicle diagnostics app
│   ├── main.py
│   └── main_v2_beta.py
├── AutoECU/                    # ECU programming tools
│   └── main.py
├── AutoKey/                    # Key programming utilities
│   └── main.py
├── Windows Test/               # Windows compatibility
│   ├── Config/
│   └── shared/
├── docs/                       # Documentation
│   └── testing/
├── scripts/                    # Build & utility scripts
│   ├── build-iso.sh
│   ├── final_install.sh
│   └── install_linux_deps.sh
├── shared/                     # Common modules
│   ├── brand_database.py
│   ├── calibrations_reset.py
│   ├── device_handler.py
│   ├── dtc_database.py
│   ├── security_manager.py
│   ├── special_functions.py
│   ├── style_manager.py
│   └── vin_decoder.py
├── tests/                      # Comprehensive test suite
│   ├── AutoDiag/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── functional/
│   ├── shared/
│   ├── mock/
│   ├── fixtures/
│   └── conftest.py
├── launcher.py                 # Main application launcher
├── requirements.txt
└── README.md
```

---

## 🎨 Themes & Customization

DiagAutoClinicOS features a sophisticated theme system with dynamic switching:

**Available Themes:**
- Dark Mode (Default)
- Light Mode
- Tech Blue
- Professional
- Security Blue (AutoKey)
- Matrix Green

```python
# Switch themes dynamically or create custom color schemes
from shared.style_manager import StyleManager
StyleManager.set_theme("dark")
```

---

## 🏎 Supported Brands

Comprehensive support for 25+ automotive manufacturers:

| Brand | Region | Key Protocols | ECU Systems |
|-------|--------|---------------|-------------|
| Toyota | Japan | Smart Key, G-Box | ISO 15765-4 |
| Volkswagen | Germany | VVDI, Immo 4/5 | UDS, KWP2000 |
| BMW | Germany | CAS, Comfort Access | ISTA, UDS |
| Mercedes | Germany | DAS, Keyless Go | XENTRY, UDS |
| Ford | USA | PATS, Smart Access | MS-CAN, UDS |
| Hyundai/Kia | Korea | HS Systems, Hitag2 | K-Line, CAN |
| Honda | Japan | Honda Smart | HDS Protocol |
| Nissan | Japan | NATS, Intelligent Key | CONSULT-III |

*Full brand list available in our [documentation](https://diagautoclinic.co.za/docs)*

---

## 🔧 Hardware Support

### J2534 Pass-Thru Devices
- Drew Technologies Tech2
- Vector VN1610/1630
- Peak PCAN-USB
- Kvaser CAN interfaces
- Intrepid Control Systems

### OBD-II Adapters
- ELM327 compatible devices
- STN11xx based interfaces
- OBDLink series
- Bluetooth/WiFi OBD adapters

### Automotive Protocols
- J2534-1/-2 compliant
- SAE J1939 (heavy-duty)
- ISO 15765 (CAN)
- ISO 14230 (KWP2000)
- ISO 9141-2

---

## 📚 Documentation

- [User Manual](https://diagautoclinic.co.za/docs/user-manual) - Complete usage guide
- [Developer Guide](https://diagautoclinic.co.za/docs/developer) - Contribution guidelines
- [API Reference](https://diagautoclinic.co.za/docs/api) - Code documentation
- [Hardware Setup](https://diagautoclinic.co.za/docs/hardware) - Device configuration
- [Testing Guide](docs/testing/TESTING_GUIDE.md) - Comprehensive testing documentation
- [Troubleshooting](https://diagautoclinic.co.za/docs/troubleshooting) - Common issues

---

## 🤝 Contributing

We welcome contributions from developers and automotive professionals!

**How to contribute:**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See our [Contributing Guide](CONTRIBUTING.md) for detailed guidelines.

---

## 🙏 Sponsorship & Support

### Hardware Sponsors

<div align="center">

[![Godiag](https://img.shields.io/badge/Godiag-.com-green.svg?style=for-the-badge)](https://godiag.com)
[![ScanTool.net](https://img.shields.io/badge/ScanTool-.net-green.svg?style=for-the-badge)](https://scantool.net)

</div>

**Special thanks to Godiag and ScanTool.net** for sponsoring their latest devices for robust testing and integration across all three suites. Your support makes this project possible.

### Development Partnership

**Built with Claude AI** - Our trusted development partner. The combination of automotive expertise and intelligent coding collaboration enabled us to achieve 490+ comprehensive tests and 93% coverage in record time.

---

## 🌐 Community & Resources

- **Official Website**: [diagautoclinic.co.za](https://diagautoclinic.co.za/)
- **GitHub Repository**: [DiagAutoClinicOS](https://github.com/DiagAutoClinic/DiagAutoClinicOS)
- **Documentation**: [diagautoclinic.co.za/docs](https://diagautoclinic.co.za/docs)
- **Community Forum**: [diagautoclinic.co.za/forum](https://diagautoclinic.co.za/forum)
- **Issue Tracker**: [GitHub Issues](https://github.com/DiagAutoClinic/DiagAutoClinicOS/issues)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **PyQt6 Team** - Excellent GUI framework
- **Python OBD Contributors** - Foundation for diagnostics protocols
- **Automotive Standards Organizations** (SAE, ISO) - Protocol specifications
- **Our Community** - Testers, contributors, and supporters worldwide

---

## 📞 Support

- **Documentation**: Check our [comprehensive docs](https://diagautoclinic.co.za/docs) first
- **Community Forum**: Get help from other users at [diagautoclinic.co.za/forum](https://diagautoclinic.co.za/forum)
- **GitHub Issues**: [Report bugs](https://github.com/DiagAutoClinic/DiagAutoClinicOS/issues) and request features
- **Email**: dacos@diagautoclinic.co.za

---

<div align="center">

**Making professional automotive diagnostics accessible to every mechanic.**

*No gatekeeping. No vendor lock-in. Just intelligence.*

</div>
