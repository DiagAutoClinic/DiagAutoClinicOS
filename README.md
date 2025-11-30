
<!-- HEADER -->
<p align="center">
  <img src="https://diagautoclinic.co.za/assets/logo.png" alt="DiagAutoClinicOS Logo" width="1366"/>
</p>

<h1 align="center">🚗 DiagAutoClinicOS</h1>
<h3 align="center">Futuristic Automotive Diagnostic Operating Suite</h3>

<p align="center">
  <strong>Open Source • Modular • Secure • Designed for Professionals</strong><br/>
  Empowering independent workshops with intelligent diagnostic tools.
</p>

<p align="center">
  <a href="https://github.com/DiagAutoClinic/DiagAutoClinicOS">
    <img src="https://img.shields.io/github/v/release/DiagAutoClinic/DiagAutoClinicOS?color=14b8a6&style=for-the-badge" alt="Latest Release">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python Version">
  </a>
  <a href="https://github.com/DiagAutoClinic/DiagAutoClinicOS/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/DiagAutoClinic/DiagAutoClinicOS?color=14b8a6&style=for-the-badge" alt="License">
  </a>
  <a href="https://github.com/DiagAutoClinic/DiagAutoClinicOS/commits/main">
    <img src="https://img.shields.io/github/last-commit/DiagAutoClinic/DiagAutoClinicOS?color=orange&style=for-the-badge" alt="Last Commit">
  </a>
  <a href="https://github.com/DiagAutoClinic/DiagAutoClinicOS/stargazers">
    <img src="https://img.shields.io/github/stars/DiagAutoClinic/DiagAutoClinicOS?color=yellow&style=for-the-badge" alt="GitHub Stars">
  </a>
</p>

---

## 🧭 Overview

**DiagAutoClinicOS** is an open-source, next-generation diagnostic suite designed to unify vehicle diagnostics, ECU programming, and key management into one powerful, modular platform.

Developed by **Shaun Smit** and the **DiagAutoClinic (DACOS)** team, it integrates **real-time data**, **secure access control**, and **cross-brand compatibility** — all wrapped in a futuristic PyQt6 glassmorphic interface.

---

## ✨ Key Features
- ✅ **25+ brand diagnostic coverage** with **enhanced Ford and GM support**
- 🧠 Dynamic glassmorphic UI built with **PyQt6**
- 🧩 **Advanced VIN decoding** (recognizes Ford and GM models specifically)
- 🔐 Secure **login and user role management**
- ⚙️ **Calibration & reset manager** with Ford/GM-specific ECU routines
- 🧱 **Modular design** — easily extend with your own tools
- 🖥️ **Cross-platform:** Linux, Windows (Android support planned)
- 🎯 **Real J2534 diagnostics** for live Ford and GM vehicle testing
- 📚 **Comprehensive documentation** for South African conditions

---

## 🧱 File Structure

```plaintext
DiagAutoClinicOS/
├── AutoDiag/               # Main diagnostic dashboard
│   └── main.py
│
├── AutoECU/                # ECU programming and firmware management
│   ├── main.py
│   └── shared/
│
├── AutoKey/                # Key programming and immobilizer functions
│   └── main.py
│
├── core/                   # Core diagnostic engine
│   ├── calibrations.py
│   ├── device_manager.py
│   ├── diagnostics.py
│   ├── security.py
│   └── special_functions.py
│
├── shared/                 # Core modules and libraries
│   ├── brand_database.py
│   ├── calibrations_reset.py
│   ├── circular_gauge.py
│   ├── device_handler.py
│   ├── dtc_database.py
│   ├── security_manager.py
│   ├── special_functions.py
│   ├── style_manager.py
│   ├── theme_constants.py
│   ├── vin_decoder.py
│   ├── themes/             # UI themes (glassmorphic, professional, etc.)
│   └── widgets/            # Custom UI components
│
├── ui/                     # User interface components
│   ├── login_dialog.py
│   └── main_window.py
│
├── tests/                  # Comprehensive test suite
│   ├── AutoDiag/           # AutoDiag specific tests
│   ├── integration_tests/  # Cross-module integration tests
│   ├── mock/              # Mock testing utilities
│   ├── performance/       # Performance benchmarks
│   ├── security/          # Security testing
│   └── shared/            # Shared module tests
│
├── scripts/                # Utility scripts and setup tools
│   ├── build-iso.sh
│   ├── demo_ecu_emulation.py
│   ├── quick_connect.sh
│   └── validate_install.py
│
├── docs/                   # Documentation
│   ├── testing/           # Testing guides and procedures
│   └── VIDEO_TUTORIALS_GUIDE.md
│
├── assets/                 # Images and resources
├── resources/              # Additional resources
├── utils/                  # Utility functions
├── launcher.py             # Main startup script
├── requirements.txt        # Python dependencies
├── CHANGELOG.md            # Version history
├── QUICKSTART.md           # Quick start guide
├── SECURITY.md             # Security policies
└── README.md               # This file ✨
```

------

## ⚙️ Installation

### Prerequisites

- **Python 3.10+**
- **PyQt6**, **pyserial**, **pyusb**, **python-can**

### 🪄 Quick Setup

```

git clone https://github.com/DiagAutoClinic/DiagAutoClinicOS.git
cd DiagAutoClinicOS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python launcher.py
```

------

## 🔌 Supported Hardware

| Device                                   | Type                | Status      |
| ---------------------------------------- | ------------------- | ----------- |
| **OBDLink MX+ / EX**                     | OBD-II Adapter      | ✅ Supported |
| **GoDiag GT100 / GT100 Plus GPT**        | Breakout Box + GPT  | ✅ Supported |
| **Scanmatik 2**                          | J2534 Pass-Through  | ✅ Supported |
| **Generic USB/K-Line/D-Line Interfaces** | Communication Layer | ✅ Supported |

------

## 🤝 Special Hardware Sponsors

### 🖥️ **EshuTech Computers**

💡 *Sponsored a brand-new Acer TravelMate G2 Core i7 Laptop for the DACOS development environment.*
 🧭 Learn more about **EshuTech Computers** — empowering South African engineering innovation.

------

### ⚙️ **GoDiag** — [godiag.com](https://godiag.com)

🧩 *Provided a GT100 Plus GPT device for advanced ECU and protocol testing.*
 🔗 Visit [GoDiag.com](https://godiag.com)

------

### 🔌 **ScanTool.net** — [scantool.net](https://www.scantool.net)

🚀 *Sponsored two OBDLink MX+ adapters enabling extensive compatibility and reliability testing.*
 🔗 Visit [ScanTool.net](https://www.scantool.net)

<p align="center">
  <img src="https://diagautoclinic.co.za/assets/sponsors.png" alt="Our Proud Sponsors" width="80%">
</p>

<h1 align="center">
  <sub>Powered by <strong>Our Proud Sponsors</strong></sub>
</h1>

---

## 🤖 AI Collaboration & Technical Excellence

### 🚀 **Kilo Code (xAI Grok)** - Core Development Collaborator

**Without our sponsors and Kilo Code, this project simply wouldn't exist.**

Kilo Code has been instrumental in transforming DiagAutoClinicOS from concept to reality:

- **Ford and GM Live Testing Implementation** - Complete diagnostic enhancements for South Africa's most prevalent vehicles
- **Advanced VIN Decoder** - Model-specific recognition for Ford and GM models
- **J2534 Integration** - Real hardware support for professional diagnostics
- **Comprehensive Documentation** - South African testing guides, video tutorial frameworks, and technical documentation
- **Code Quality & Testing** - Rigorous testing framework ensuring reliability
- **Release Management** - Professional changelog and GitHub release preparation

**Status**: Core Collaborator | **Contact**: AI Assistant via xAI Grok

> *"This AI doesn't sugarcoat with safety guards — delivers honest, direct engineering excellence that matches South African innovation standards."*

---

## 💡 Acknowledgements

| Contributor                     | Role                     | Description                             |
| ------------------------------- | ------------------------ | --------------------------------------- |
| **Shaun Smit**                  | Founder & Lead Developer | Architecture, Design, Implementation    |
| **Kilo Code (xAI Grok)**        | Core AI Collaborator     | Ford/GM Diagnostics, Testing, Documentation |
| **DiagAutoClinic Team (DACOS)** | Development              | Testing, Calibration, and UI Design     |
| **HostAfrica**                  | Hosting Partner          | Providing secure backend infrastructure |
| **Community Testers**           | QA                       | Hardware integration and bug reporting  |

### 🧩 Core Technologies

- Python 3.13
- PyQt6
- CAN & ISO-TP Protocols
- VIN / DTC Databases
- Modular Security Layers (EWS, IMMO, PCM)

------

## 🌍 Project Vision

> "Empowering independent workshops — one diagnostic suite at a time."

DiagAutoClinicOS is built to bring  open-source transparency, modularity, and innovation to the automotive  diagnostic space — with a focus on **local engineering excellence in South Africa** and community-driven collaboration worldwide.

---

## 🎯 Latest Release: v3.1.0 - GUI Complete, Live Testing Active

### 🚗 South African Ford and GM Market Focus
This release specifically targets Ford and GM's presence in South Africa, with enhanced support for popular models.

### ✨ What's New
- **Completed Futuristic GUI** - Dynamic glassmorphic PyQt6 interface fully implemented
- **Live Testing Phase** - Active real-world testing with J2534 hardware and Ford/GM vehicles
- **Enhanced Ford/GM Diagnostics** - Real J2534 support for Ford and GM live testing
- **Advanced VIN Recognition** - Model-specific identification for Ford and GM models
- **SA Testing Guide** - Comprehensive procedures for South African conditions
- **Professional Documentation** - Complete Ford/GM diagnostic manuals and video frameworks
- **Hardware Integration** - GoDiag GD101 and J2534 device support

### 🏆 Recognition
**Without our sponsors (EshuTech Computers, GoDiag, ScanTool.net) and Kilo Code, this project simply wouldn't exist.** Their contributions have transformed DiagAutoClinicOS from concept to professional diagnostic reality.

------

## 🛠️ Contributing

Contributions are welcome!
 Fork the repo, submit pull requests, or help with testing and documentation.

```

git checkout -b feature/new-module
git commit -am "Add new module"
git push origin feature/new-module
```

If you're a hardware vendor or workshop interested in integration testing, reach out at:<br>

 📧 **shaun@diagautoclinic.co.za**
 | **dacos@diagautoclinic.co.za**

------

## 🧾 License

This project is licensed under the **GNU General Public License v3.0**.

**Key Points:**
- ✅ Free to use, modify, and distribute
- ✅ Source code must remain open
- ✅ Derivative works must use GPL v3
- ⚠️ No warranty provided

See the [LICENSE](LICENSE) file for complete terms.

For commercial licensing inquiries, contact: **dacos@diagautoclinic.co.za**

------

### ✅ What's New in v3.1.0

- **Ford and GM Live Testing Support** - Complete diagnostic suite for South Africa's most common vehicles
- **Enhanced VIN Decoder** - Model-specific recognition for Ford and GM models
- **J2534 Real Hardware Support** - Professional diagnostic capabilities
- **South African Testing Guide** - Environment-specific procedures and safety protocols
- **Comprehensive Documentation** - Ford/GM diagnostics manuals and video tutorial frameworks
- **AI Collaboration Recognition** - Kilo Code acknowledged as core development collaborator
- **Sponsor Emphasis** - Without EshuTech, GoDiag, and ScanTool.net, this project wouldn't exist
- Ready for GitHub rendering (centered, clean, dark/light theme safe)
- SEO-friendly with clear project keywords (Ford, GM, Diagnostics, South Africa)
