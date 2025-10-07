# DiagAutoClinicOS 🚗💻

**Professional Automotive Diagnostic Suite for Modern Technicians**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Downloads](https://img.shields.io/badge/ISO-Download-brightgreen)](https://diagautoclinic.co.za/downloads/build_v1.0.0_release.iso)

![DiagAutoClinicOS Demo](assets/demo-screenshot.png)

## 🌟 Overview

DiagAutoClinicOS is a comprehensive, open-source automotive diagnostic platform designed for professional technicians and enthusiasts. Our suite provides modern, intuitive interfaces for vehicle diagnostics, ECU programming, and key programming with support for 25+ major automotive brands.

### 🎯 Key Features

- **Multi-Application Suite**: Three specialized tools in one platform
- **Brand-Specific Diagnostics**: Intelligent support for 25+ global automotive brands
- **Modern UI/UX**: Dark/Light themes with professional styling
- **Cross-Platform**: Runs on Windows, Linux, and macOS
- **Hardware Integration**: J2534 pass-thru and CAN bus support
- **Open Source**: Fully transparent and community-driven

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

## 🚀 Quick Start

### ISO Download (Recommended)
Download our pre-configured live environment:
```bash
# Download the latest release ISO
https://diagautoclinic.co.za/downloads/build_v1.0.0_release.iso

# Create bootable USB or run in VM
```

## Structure
``` plaintext
. 
├── DiagAutoClinicOS/ 
│ ├── AutoDiag/ # Vehicle diagnostics application 
| | ├── _pycache_/ 
| | ├── venv/ # Virtual enviroment 
| | ├── brand_database.py 
| | ├── style_manager.py 
│ │ └── main.py 
│ ├── AutoECU/ # ECU programming tools 
| | ├──_pycache_/ 
| | ├── style_manager.py 
│ │ └── main.py 
│ ├── AutoKey/ # Key programming utilities 
| | ├── _pycache_/ 
| | ├── style_manager.py 
│ │ └── main.py 
│ ├── shared/ # Common resources and modules 
| | ├── _pycache_/ 
│ │ ├── device_handler.py 
│ │ ├── dtc_database.py 
| | ├── install_linux_deps.sh 
| | ├── style_manager.py 
│ │ └── vin_decoder.py 
│ └── scripts/ # Build and utility scripts 
|     ├── check_connection.py 
|     ├── install_linux_deps.sh 
|     ├── final_instal.sh
|     ├── pair_bluetooth_elm327.py 
|     ├── quick_connect.sh 
|     ├── release_bluetooth.py 
|     ├── setup_bluetooth.py 
|     ├── setup_obd2_bluetooth.py 
|     ├── setup_obd2_bluetooth_enhanced.py 
|     ├── test_bluetooth.py 
|     └── test_elm327.py │ 
└── build_iso.sh 
└── README.md   # this document
└── launcher.py 
└── LICENSE.md
```

System Requirements
    • OS: Windows 10+, Ubuntu 18.04+, macOS 10.15+
    • Python: 3.8 or higher
    • RAM: 4GB minimum, 8GB recommended
    • Storage: 2GB free space
    • Hardware: J2534 compatible interface or ELM327 adapter
🎨 Themes & Customization
DiagAutoClinicOS features a sophisticated theme system:
```python
# Available themes
- Dark Mode (Default)
- Light Mode
- Tech Blue
- Professional
- Security Blue (AutoKey)
- Matrix Green
Switch themes dynamically or create custom color schemes through the StyleManager API.
```
🏎 Supported Brands
Our intelligent brand database includes comprehensive support for:
Brand
Region
Key Protocols
ECU Systems
Toyota
Japan
Smart Key, G-Box
ISO 15765-4
Volkswagen
Germany
VVDI, Immo 4/5
UDS, KWP2000
BMW
Germany
CAS, Comfort Access
ISTA, UDS
Mercedes
Germany
DAS, Keyless Go
XENTRY, UDS
Ford
USA
PATS, Smart Access
MS-CAN, UDS
Hyundai/Kia
Korea
HS Systems, Hitag2
K-Line, CAN
Honda
Japan
Honda Smart
HDS Protocol
Nissan
Japan
NATS, Intelligent Key
CONSULT-III
*Full list of 25+ brands available in our documentation*
🔧 Hardware Support
J2534 Pass-Thru Devices
    • Drew Technologies Tech2
    • Vector VN1610/1630
    • Peak PCAN-USB
    • Kvaser CAN interfaces
    • Intrepid Control Systems
OBD-II Adapters
    • ELM327 compatible devices
    • STN11xx based interfaces
    • OBDLink series
    • Bluetooth/WiFi OBD adapters
Automotive Interfaces
    • J2534-1/-2 compliant devices
    • SAE J1939 heavy-duty
    • ISO 15765 (CAN)
    • ISO 14230 (KWP2000)
    • ISO 9141-2
📚 Documentation
    • User Manual - Complete usage guide
    • Developer Guide - Contribution guidelines
    • API Reference - Code documentation
    • Hardware Setup - Device configuration
    • Troubleshooting - Common issues and solutions
Contributing
We welcome contributions! Please see our Contributing Guide for details.
    1. Fork the repository
    2. Create a feature branch (git checkout -b feature/amazing-feature)
    3. Commit your changes (git commit -m 'Add amazing feature')
    4. Push to the branch (git push origin feature/amazing-feature)
    5. Open a Pull Request
🌐 Website & Community
    • Official Website: https://diagautoclinic.co.za/
    • GitHub Repository: https://github.com/DiagAutoClinic/DiagAutoClinicOS
    • Documentation: https://diagautoclinic.co.za/docs
    • Community Forum: https://diagautoclinic.co.za/forum
    • Issue Tracker: https://github.com/DiagAutoClinic/DiagAutoClinicOS/issues
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
🙏 Acknowledgments
    • PyQt6 team for the excellent GUI framework
    • Python OBD library contributors
    • Automotive standards organizations (SAE, ISO)
    • Our amazing community of testers and contributors
📞 Support
    • Documentation: Check our comprehensive docs first
    • Community Forum: Get help from other users
    • GitHub Issues: Report bugs and request features
    • Email: support@diagautoclinic.co.za

