# DiagAutoClinicOS

<div align="center">

![DiagAutoClinicOS Logo](https://diagautoclinic.co.za/assets/logo.png)

**Professional Automotive Diagnostic Suite for Modern Technicians**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/) [![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg)](https://github.com/DiagAutoClinic/DiagAutoClinicOS)

[Website](https://diagautoclinic.co.za/) • [Documentation](https://diagautoclinic.co.za/docs) • [Community](https://diagautoclinic.co.za/forum) • [Download ISO](https://diagautoclinic.co.za/downloads/build_v1.0.0_release.iso)

</div>

------

## 📋 Overview

DiagAutoClinicOS is a comprehensive, open-source automotive diagnostic platform designed for professional technicians and enthusiasts. Our suite provides modern, intuitive interfaces for vehicle diagnostics, ECU programming, and key programming with support for 25+ major automotive brands.

### ✨ Key Features

- **Multi-Application Suite**: Three specialized tools in one platform
- **Brand-Specific Diagnostics**: Intelligent support for 25+ global automotive brands
- **Modern UI/UX**: Dark/Light themes with professional styling
- **Cross-Platform**: Runs on Windows, Linux, and macOS
- **Hardware Integration**: J2534 pass-thru and CAN bus support
- **Open Source**: Fully transparent and community-driven

------

## 🚗 Application Suite

### 1. **AutoDiag** - Vehicle Diagnostics

- Complete OBD-II compliance (SAE J1979)
- Real-time parameter monitoring
- DTC reading/clearing with enhanced descriptions
- Live data graphing and logging
- Brand-specific diagnostic procedures
- Freeze frame data analysis

### 2. **AutoECU** - ECU Programming

- ECU reading/writing operations
- Parameter calibration editing
- Immobilizer system programming
- Flash memory operations
- Checksum verification
- Backup and restore functionality

### 3. **AutoKey** - Key Programming

- Transponder key programming
- Remote key fob synchronization
- Immobilizer code calculation
- Key cloning capabilities
- Security system reset procedures

------

## 📁 Repository Structure

```
DiagAutoClinicOS/
│
├── .github/
│   └── FUNDING.yml                    # GitHub sponsorship configuration
│
├── AutoDiag/                          # Vehicle Diagnostics Application
│   ├── main.py                        # Main diagnostic interface
│   └── main_v2_beta.py                # Beta version with new features
│
├── AutoECU/                           # ECU Programming Tools
│   └── main.py                        # ECU flash and calibration interface
│
├── AutoKey/                           # Key Programming Utilities
│   └── main.py                        # Key programming and immobilizer tools
│
├── Windows Test/                      # Windows-specific testing environment
│   ├── Config/                        # Windows configuration files
│   ├── shared/                        # Windows shared resources
│   ├── WINDOWS_TEST.md                # Windows testing documentation
│   └── update_windows_req.py          # Windows requirements updater
│
├── scripts/                           # Build and Utility Scripts
│   ├── build-iso.sh                   # ISO builder for live environment
│   ├── final_install.sh               # Post-installation configuration
│   ├── install_linux_deps.sh          # Linux dependency installer
│   ├── quick_connect.sh               # Quick device connection utility
│   ├── release_bluetooth.py           # Bluetooth release management
│   └── setup_bluetooth.py             # Bluetooth device setup
│
├── shared/                            # Common Resources and Modules
│   ├── .editorconfig                  # Editor configuration
│   ├── brand_database.py              # 25+ vehicle brand definitions
│   ├── calibrations_reset.py          # ECU calibration reset utilities
│   ├── device_handler.py              # Hardware device management
│   ├── dtc_database.py                # Diagnostic Trouble Code database
│   ├── enhanced_integration.py        # Advanced integration features
│   ├── enhanced_style_manager.py      # Enhanced UI theme management
│   ├── install_linux_deps.sh          # Linux dependencies installer
│   ├── install_professional_deps.sh   # Professional tools installer
│   ├── integration_autodiag.py        # AutoDiag integration module
│   ├── security_manager.py            # Security and authentication
│   ├── special_functions.py           # Brand-specific special functions
│   ├── style_manager.py               # UI styling and themes
│   └── vin_decoder.py                 # VIN decoding and validation
│
├── .gitignore                         # Git ignore rules
├── COMMUNITY_DISCUSSIONS.md           # Community guidelines
├── LICENSE                            # MIT License
├── PULL_REQUEST_TEMPLATE.md           # PR submission template
├── README.md                          # This document
├── SECURITY.md                        # Security policy
├── add_responsive_behavior.py         # UI responsiveness utilities
├── launcher.py                        # Application launcher
├── requirements.md                    # Requirements documentation
└── requirements.txt                   # Python dependencies
```

------

## 🎨 Themes & Customization

DiagAutoClinicOS features a sophisticated theme system with multiple built-in options:

```python
# Available themes
- Dark Mode (Default)
- Light Mode
- Tech Blue
- Professional
- Security Blue (AutoKey)
- Matrix Green
```

Switch themes dynamically or create custom color schemes through the StyleManager API.

------

## 🏎 Supported Brands

Our intelligent brand database includes comprehensive support for 25+ manufacturers:

| Brand       | Region  | Key Protocols         | ECU Systems  |
| ----------- | ------- | --------------------- | ------------ |
| Toyota      | Japan   | Smart Key, G-Box      | ISO 15765-4  |
| Volkswagen  | Germany | VVDI, Immo 4/5        | UDS, KWP2000 |
| BMW         | Germany | CAS, Comfort Access   | ISTA, UDS    |
| Mercedes    | Germany | DAS, Keyless Go       | XENTRY, UDS  |
| Ford        | USA     | PATS, Smart Access    | MS-CAN, UDS  |
| Hyundai/Kia | Korea   | HS Systems, Hitag2    | K-Line, CAN  |
| Honda       | Japan   | Honda Smart           | HDS Protocol |
| Nissan      | Japan   | NATS, Intelligent Key | CONSULT-III  |

*Full list of 25+ brands available in our documentation*

------

## 🔧 Hardware Support

### J2534 Pass-Thru Devices

- Drew Technologies Tech2
- Vector VN1610/1630
- Peak PCAN-USB
- Kvaser CAN interfaces
- Intrepid Control Systems
- **GodiagGD101 (Tested 100% working on Linux)**

### OBD-II Adapters

- **ELM327 Bluetooth (Tested 100% working on Linux)**
- STN11xx based interfaces
- OBDLink series
- Bluetooth/WiFi OBD adapters

### Automotive Interfaces

- J2534-1/-2 compliant devices
- SAE J1939 heavy-duty
- ISO 15765 (CAN)
- ISO 14230 (KWP2000)
- ISO 9141-2

------

## 💻 System Requirements

- **OS**: Windows 10+, Ubuntu 18.04+, macOS 10.15+
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Hardware**: J2534 compatible interface or ELM327 adapter

------

## 🚀 Quick Start

### Download Live Environment

Download our pre-configured live environment:

```bash
# Download the latest release ISO
wget https://diagautoclinic.co.za/downloads/build_v1.0.0_release.iso

# Create bootable USB or run in VM
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/DiagAutoClinic/DiagAutoClinicOS.git
cd DiagAutoClinicOS

# Install dependencies (Linux)
chmod +x scripts/install_linux_deps.sh
./scripts/install_linux_deps.sh

# Install dependencies (Windows)
python Windows\ Test/update_windows_req.py

# Launch the application
python launcher.py
```

------

## 📚 Documentation

- [**User Manual**](https://diagautoclinic.co.za/docs/user-manual) - Complete usage guide
- [**Developer Guide**](https://diagautoclinic.co.za/docs/developer-guide) - Contribution guidelines
- [**API Reference**](https://diagautoclinic.co.za/docs/api) - Code documentation
- [**Hardware Setup**](https://diagautoclinic.co.za/docs/hardware) - Device configuration
- [**Troubleshooting**](https://diagautoclinic.co.za/docs/troubleshooting) - Common issues and solutions

------

## 🤝 Contributing

We welcome contributions! Please see our Contributing Guide for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

------

## 🌐 Website & Community

- **Official Website**: https://diagautoclinic.co.za/
- **GitHub Repository**: https://github.com/DiagAutoClinic/DiagAutoClinicOS
- **Documentation**: https://diagautoclinic.co.za/docs
- **Community Forum**: https://diagautoclinic.co.za/forum
- **Issue Tracker**: https://github.com/DiagAutoClinic/DiagAutoClinicOS/issues

------

## 💖 Sponsors

### 🎉 Special Thanks to Our Sponsors

<div align="center">

#### **EshuTech Computors**

We are incredibly grateful to **EshuTech Computors** for sponsoring us with a brand new **Acer TravelMate G2 Core i7 Laptop**. This powerful machine has enabled us to continue our development work and significantly accelerate the progress of DiagAutoClinicOS. Thank you for believing in our mission and supporting open-source automotive diagnostics!

[Learn more about EshuTech Computors](https://eshutech.co.za)

------

### Support This Project

If you find DiagAutoClinicOS useful, consider supporting our development:

- ⭐ Star this repository
- 🐛 Report bugs and suggest features
- 💻 Contribute code and documentation
- 💰 Sponsor via [GitHub Sponsors](https://github.com/sponsors/DiagAutoClinic)
- ☕ Buy us a coffee

</div>

------

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

------

## 🙏 Acknowledgments

- **EshuTech Computors** - For sponsoring our development hardware
- PyQt6 team for the excellent GUI framework
- Python OBD library contributors
- Automotive standards organizations (SAE, ISO)
- Our amazing community of testers and contributors

------

## 📞 Support

- **Documentation**: Check our [comprehensive docs](https://diagautoclinic.co.za/docs) first
- **Community Forum**: Get help from [other users](https://diagautoclinic.co.za/forum)
- **GitHub Issues**: [Report bugs](https://github.com/DiagAutoClinic/DiagAutoClinicOS/issues) and request features
- **Email**: [support@diagautoclinic.co.za](mailto:support@diagautoclinic.co.za)

------

<div align="center">

**Made with ❤️ by the DiagAutoClinic Team**

*Empowering automotive technicians with open-source tools*

</div>