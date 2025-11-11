# DiagAutoClinicOS

<div align="center">

![DiagAutoClinicOS Logo](https://diagautoclinic.co.za/assets/logo.png)

**Professional Automotive Diagnostic Suite for Modern Technicians**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux%20|%20Windows%20|%20macOS-lightgrey.svg)](https://github.com/DiagAutoClinic/DiagAutoClinicOS)

[Website](https://diagautoclinic.co.za/) • [Documentation](https://diagautoclinic.co.za/docs) • [Community](https://diagautoclinic.co.za/forum) • [Download ISO](https://diagautoclinic.co.za/downloads/build_v1.0.0_release.iso)

</div>

---

## 🚗 Overview

**DiagAutoClinicOS** is a modern, comprehensive and open-source automotive diagnostic platform built for professional technicians and enthusiasts. This suite provides modular interfaces for vehicle diagnostics, advanced ECU programming, and key programming with support for 25+ major automotive brands.

---

## 🔑 Key Features

- **Multi-Application Suite:** Manage all diagnostic and programming tools in one modular platform (AutoDiag, AutoECU, AutoKey).
- **Brand Specific Diagnostics:** Native support for 25+ global automotive brands.
- **Modern UI/UX:** Professional styling with dark/light themes.
- **Cross-Platform:** Runs on Windows, Linux, and macOS.
- **Integrated Hardware:** J2534 pass-thru and CAN bus device support.
- **Open Source:** Transparent and community-driven.

---

## 📂 Repository Structure

```text
DiagAutoClinicOS/
│
├── .continue/                  # Continuation/templating support files
├── .github/                    # GitHub configuration and workflows
├── .gitignore                  # Git ignore rules
├── AutoDiag/                   # Main vehicle diagnostic application
├── AutoECU/                    # ECU programming tools
├── AutoKey/                    # Key programming & immobilizer modules
├── COMMUNITY_DISCUSSIONS.md    # Community forums and topic hub
├── LICENSE                     # MIT License
├── PULL_REQUEST_TEMPLATE.md    # PR submission template
├── README.md                   # You’re here!
├── SECURITY.md                 # Security policy
├── Windows Test/               # Windows-specific testing & configs
├── add_responsive_behavior.py  # Responsive UI utilities
├── docs/                       # Full project documentation
├── launcher.py                 # App launcher/entry point
├── requirements-dev.txt        # Dev requirements
├── requirements.md             # Dependency explanations
├── requirements.txt            # Python requirements
├── scripts/                    # Build, utility, and integration scripts
├── shared/                     # Core modules and common assets
├── tests/                      # Automated test suite
└── ...                         # Additional modules as project evolves
```

---

## 🎨 Themes & Customization

DiagAutoClinicOS comes with a sophisticated theme system (Dark, Light, Tech Blue, Professional, Security Blue, Matrix Green). You can switch themes dynamically or create custom color schemes through the StyleManager API.

---

## 🏭 Supported Brands

Our intelligent brand database supports comprehensive diagnostics for **25+ manufacturers** (see docs for full list):

| Brand         | Region | Key Protocols / ECUs           | Systems         |
|---------------|--------|--------------------------------|-----------------|
| Toyota        | Japan  | Smart Key, G-Box, ISO 15765-4  | UDS, KWP2000    |
| Ford          | USA    | PATS, Smart Access             | MS-CAN, UDS     |
| Hyundai/Kia   | Korea  | HS Systems, Hitag2             | K-Line, CAN     |
| Honda         | Japan  | Honda Smart                    | HDS Protocol    |
| VAG           | Germany| VVDI, Immo 4/5                 | UDS, KWP2000    |
| Mercedes      | Germany| DAS, Keyless Go                | XENTRY, UDS     |
| ...           | ...    | ...                            | ...             |

*For the complete list, [see documentation](https://diagautoclinic.co.za/docs).*

---

## 🛠 Hardware Support

### J2534 Pass-Thru Devices

- Drew Technologies Tech2
- Vector VN1610/1630
- Peak PCAN-USB
- Kvaser CAN interfaces
- Godiag GD101 (tested 100% on Linux)
- ...and compatible ELM327 interfaces

### OBD-II Adapters

- ELM327 Bluetooth (tested 100% on Linux)
- STN11xx-based interfaces
- OBDLink series
- Bluetooth/WiFi capable adapters

### Automotive Interfaces

- J2534-1/-2 compliant devices
- SAE J1939 heavy-duty
- ISO 15765 (CAN), ISO 14230 (KWP2000)

---

## 🖥️ System Requirements

- **OS:** Windows 10+, Ubuntu 18.04+, macOS 10.15+
- **Python:** 3.8 or newer
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 2GB free space
- **Hardware:** J2534 compatible interface or ELM327 adapter

---

## ⚡ Quick Start

### Live Environment Download

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

# Install Linux dependencies
chmod +x scripts/install_linux_deps.sh
./scripts/install_linux_deps.sh

# Launch the application
python launcher.py
```

---

## 📖 Documentation

- [**User Manual**](https://diagautoclinic.co.za/docs/user-manual) – Complete usage guide
- [**Developer Guide**](https://diagautoclinic.co.za/docs/developer-guide) – Contribution guidelines
- [**API Reference**](https://diagautoclinic.co.za/docs/api) – Code & integrations
- [**Hardware Setup**](https://diagautoclinic.co.za/docs/hardware) – Device configuration
- [**Troubleshooting**](https://diagautoclinic.co.za/docs/troubleshooting) – Common issues & solutions

---

## 👥 Contributing

We welcome contributions! Please see our [Contributing Guide](https://diagautoclinic.co.za/docs/developer-guide) for details.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 🌐 Website & Community

- **Official Website:** https://diagautoclinic.co.za/
- **GitHub Repository:** https://github.com/DiagAutoClinic/DiagAutoClinicOS
- **Documentation:** https://diagautoclinic.co.za/docs
- **Community Forum:** https://diagautoclinic.co.za/forum
- **Issue Tracker:** https://github.com/DiagAutoClinic/DiagAutoClinicOS/issues

---

## 💎 Sponsors

> **Sponsors are the driving force behind our innovation.**

<div align="center">

#### **Special Hardware Sponsors**

- **EshuTech Computers**  
  Sponsored a brand new Acer TravelMate G2 Core i7 Laptop  
  [Learn more about EshuTech Computers](https://eshutech.co.za)

- **Godiag (https://godiag.com)**  
  Provided a GT100 Plus GPT device for advanced testing and integration  
  [Visit Godiag.com](https://godiag.com)

- **ScanTool.net (https://www.scantool.net)**  
  Sponsored 2 x OBDLink MX+ adapters for extensive compatibility testing  
  [Visit ScanTool.net](https://www.scantool.net)

</div>

---

## 🙏 Support This Project

If you find DiagAutoClinicOS useful, consider supporting our development:

- ⭐️ Star this repository
- 🐞 Report bugs and suggest features
- 🛠 Sponsor via [GitHub Sponsors](https://github.com/sponsors/DiagAutoClinic)
- ☕️ Buy us a coffee

---

## ©️ License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

## 📢 Acknowledgments

- **EshuTech Computers** – Development laptop sponsor
- **Godiag.com** – GT100 Plus GPT hardware for bench/ECU testing
- **ScanTool.net** – 2x OBDLink MX+ for OBD-II and CAN diagnostics
- PyQt6 team – for excellent GUI framework
- Python OBD library contributors
- Automotive standards organizations (SAE, ISO)
- Our amazing community of testers and contributors
- **claud.ai** Claude-Code
- **grok.com** Grok 4
- **deepseek.com** Deepseek-Coder
- **My Wife** Patience and support like non-other ❤️❤️❤️

---

<div align="center">

**Made with ❤️ by the Human-AI Colab Team**

*Empowering automotive technicians with open-source tools.
Where Mechanics Meet Future Intelligence*

</div>
