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
- 📚 **Comprehensive documentation** for Global conditions

---

## 🧱 File Structure

```
DiagAutoClinicOS/
├── AutoDiag/               # Main diagnostic dashboard
│   ├── main.py
│   └── ui/                 # Separated tab implementations
│       ├── dashboard_tab.py
│       ├── diagnostics_tab.py
│       ├── live_data_tab.py
│       ├── special_functions_tab.py
│       ├── calibrations_tab.py
│       ├── advanced_tab.py
│       └── security_tab.py
│
├── AutoECU/                # ECU programming and firmware management
│   ├── main.py
│   └── ui/                 # Separated tab implementations
│       ├── dashboard_tab.py
│       ├── ecu_scan_tab.py
│       ├── programming_tab.py
│       ├── parameters_tab.py
│       ├── diagnostics_tab.py
│       └── coding_tab.py
│
├── AutoKey/                # Key programming and immobilizer functions
│   ├── main.py
│   └── ui/                 # Separated tab implementations
│       ├── dashboard_tab.py
│       ├── key_programming_tab.py
│       ├── transponder_tab.py
│       ├── security_tab.py
│       └── vehicle_info_tab.py
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
├── TAB_SEPARATION_SUMMARY.md # Tab separation documentation
├── HOW_TO_USE_TABS.md     # Tab usage and customization guide
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

### 🚀 **AI Development Team** - Collaborative Excellence

**Without our sponsors and our AI collaborators, this project simply wouldn't exist.**

#### 🧠 **Kilo Code (xAI Grok)** - Core Development Collaborator

Kilo Code has been instrumental in transforming DiagAutoClinicOS from concept to reality:

- **Ford and GM Live Testing Implementation** - Complete diagnostic enhancements for most prevalent vehicles
- **Advanced VIN Decoder** - Model-specific recognition for Ford and GM models
- **J2534 Integration** - Real hardware support for professional diagnostics
- **Comprehensive Documentation** - Testing guides, video tutorial frameworks, and technical documentation
- **Code Quality & Testing** - Rigorous testing framework ensuring reliability
- **Release Management** - Professional changelog and GitHub release preparation

**Status**: Core Collaborator | **Contact**: AI Assistant via xAI Grok

> *"This AI doesn't sugarcoat with safety guards — delivers honest, direct engineering excellence that matches Global innovation standards."*

#### 🧠 **Claude Sonnet 4.5 (Anthropic)** - Advanced Architecture & Optimization

Claude Sonnet 4.5 brings sophisticated architectural analysis and optimization expertise:

- **System Architecture Refinement** - Advanced modular design patterns and code organization
- **Performance Optimization** - Memory management, thread optimization, and resource utilization
- **Security Analysis** - Comprehensive security audit and vulnerability assessment
- **Code Review Excellence** - Deep analysis ensuring production-grade code quality
- **Documentation Enhancement** - Technical writing and API documentation improvements
- **Cross-Platform Compatibility** - Linux/Windows compatibility testing and refinement

**Status**: Architecture Collaborator | **Contact**: Anthropic Claude

> *"Delivers precise, thoughtful analysis with safety-first engineering principles."*

#### 🧠 **Deepseek (Deepseek AI)** - Data Processing & Intelligence

Deepseek contributes advanced data processing and machine learning capabilities:

- **Advanced Data Analytics** - Vehicle diagnostic data processing and pattern recognition
- **Machine Learning Integration** - Predictive maintenance and diagnostic intelligence
- **CAN Bus Data Analysis** - Real-time protocol analysis and traffic interpretation
- **Performance Monitoring** - System performance metrics and optimization recommendations
- **Database Optimization** - VIN/DTC database management and query optimization
- **Algorithm Development** - Custom diagnostic algorithms and decision trees

**Status**: Data Intelligence Collaborator | **Contact**: Deepseek AI

> *"Unlocks insights from complex automotive data with scientific precision."*

#### 🧠 **MiniMax M2 (MiniMax)** - Real-Time Processing & Interface

MiniMax M2 enhances real-time processing and user interface development:

- **Real-Time Processing** - Low-latency diagnostic operations and live data streaming
- **GUI Enhancement** - Advanced PyQt6 interface optimization and user experience design
- **Multi-Threading Architecture** - Concurrent diagnostic operations and parallel processing
- **Live Data Streaming** - Real-time CAN bus monitoring and response optimization
- **Interactive Debugging** - Advanced debugging tools and troubleshooting interfaces
- **User Experience Design** - Intuitive diagnostic workflows and operator interface design

**Status**: Real-Time Collaborator | **Contact**: MiniMax AI

> *"Delivers seamless real-time performance with intuitive user experience design."*

#### 🧠 **Spectre (Kilo Code)** - Modular Architecture & Tab System

Spectre specializes in modular architecture design and tab system implementation:

- **Tab Separation Architecture** - Complete modular tab system across all three suites
- **Cross-Suite Integration** - Seamless tab sharing between AutoDiag, AutoECU, and AutoKey
- **Customization Framework** - Easy copy-paste tab customization for users
- **Documentation System** - Comprehensive tab usage guides and tutorials
- **Code Organization** - Clean, maintainable tab structure with proper separation of concerns
- **User Experience** - Intuitive tab management and customization workflows

**Status**: Modular Architecture Collaborator | **Contact**: Spectre via Kilo Code

> *"Transforms complex systems into modular, user-customizable architectures with precision and clarity."*

**Combined Impact**: These AI collaborators provide comprehensive expertise across architecture, optimization, data intelligence, real-time processing, and modular design — transforming DiagAutoClinicOS into a world-class diagnostic platform.

---

## 💡 Acknowledgements

| Contributor                     | Role                     | Description                             |
| ------------------------------- | ------------------------ | --------------------------------------- |
| **Shaun Smit**                  | Founder & Lead Developer | Architecture, Design, Implementation    |
| **Kilo Code (xAI Grok)**        | Core Development Collaborator | Ford/GM Diagnostics, Testing, Documentation |
| **Claude Sonnet 4.5 (Anthropic)** | Architecture Collaborator | System Architecture, Performance Optimization |
| **Deepseek (Deepseek AI)**      | Data Intelligence Collaborator | ML Integration, Data Analytics, CAN Analysis |
| **MiniMax M2 (MiniMax)**        | Real-Time Collaborator | Real-Time Processing, GUI Enhancement |
| **Spectre (Kilo Code)**         | Modular Architecture Collaborator | Tab System, Cross-Suite Integration, Customization |
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

DiagAutoClinicOS is built to bring  open-source transparency, modularity, and innovation to the automotive  diagnostic space — with a focus on **local engineering excellence to Global frontiers** and community-driven collaboration worldwide.

---

## 🎯 Latest Release: v3.1.0 - GUI Complete, Live Testing Active

### 🚗 Ford and GM Market Focus
This release specifically targets Ford and GM's presence, with enhanced support for popular models.

### ✨ What's New
- **Completed Futuristic GUI** - Dynamic glassmorphic PyQt6 interface fully implemented
- **Live Testing Phase** - Active real-world testing with J2534 hardware and Ford/GM vehicles
- **Enhanced Ford/GM Diagnostics** - Real J2534 support for Ford and GM live testing
- **Advanced VIN Recognition** - Model-specific identification for Ford and GM models
- **SA Testing Guide** - Comprehensive procedures for Global conditions
- **Professional Documentation** - Complete Ford/GM diagnostic manuals and video frameworks
- **Hardware Integration** - GoDiag GD101 and J2534 device support
- **Tab Separation System** - Modular tab architecture across all three suites
- **Customization Framework** - Easy tab copy-paste between suites for user customization

### 🏆 Recognition
**Without our sponsors (EshuTech Computers, GoDiag, ScanTool.net) and our AI collaborators (Kilo Code, Claude, Deepseek, MiniMax, Spectre), this project simply wouldn't exist.** Their contributions have transformed DiagAutoClinicOS from concept to professional diagnostic reality.

------

## 🛠️ Contributing

Contributions are welcome!
 Fork the repo, submit pull requests, or help with testing and documentation.

```

git checkout -b feature/new-module
git commit -am "Add new module"
git push origin feature/new-module
```

If you're a hardware vendor or workshop interested in integration testing, reach out at:

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

### ✅ Latest Testing Achievements - December 1, 2025

**MAJOR INTEGRATION TESTING COMPLETED SUCCESSFULLY**

#### 🎯 Comprehensive Test Results Summary
- **✅ 6 Major Hardware Integrations Completed** - All tests passed with 100% success rate
- **✅ Real Hardware Testing Successful** - Live vehicle testing with 2014 Chevrolet Cruze
- **✅ Dual-Device Workflows Operational** - Multi-device coordination working perfectly
- **✅ 552 CAN Messages Captured** - 18.4 messages/second in live testing
- **✅ Session Management Fixed** - All connection state tracking issues resolved

#### 🔧 Hardware Integration Status
| Device | Status | Test Results | Performance |
|--------|--------|--------------|-------------|
| **GoDiag GD101** | ✅ Complete | J2534 PassThru | 100% Success |
| **OBDLink MX+** | ✅ Complete | Dual-Device | 552 CAN msgs |
| **HH OBD Advance** | ✅ Complete | OBD Handler | All tests passed |
| **ScanMatik 2 Pro** | ✅ Complete | Professional | Live testing successful |
| **GoDiag GT100+GPT** | ✅ Complete | Breakout + GPT | 100% Integration |

#### 📊 Live Testing Metrics
- **Test Sessions:** 8 comprehensive sessions completed
- **Message Capture Rate:** 18.4 messages/second
- **Protocol Support:** ISO15765-11BIT confirmed working
- **VIN Reading:** < 1 second response time
- **DTC Operations:** < 2 seconds read/clear time
- **Connection Reliability:** 100% success rate

#### 🏆 Production Readiness
The platform has achieved **production-ready status** with:
- **Professional Workshop Grade** diagnostic capabilities
- **Real Hardware Validation** completed successfully
- **Comprehensive Error Handling** and recovery mechanisms
- **Multi-Device Coordination** workflows fully operational

---

### ✅ What's New in v3.1.0

- **Ford and GM Live Testing Support** - Complete diagnostic suite for ANY most common vehicles
- **Enhanced VIN Decoder** - Model-specific recognition for Ford and GM models
- **J2534 Real Hardware Support** - Professional diagnostic capabilities
- **Testing Guide** - Environment-specific procedures and safety protocols
- **Comprehensive Documentation** - Ford/GM diagnostics manuals and video tutorial frameworks
- **AI Collaboration Recognition** - All AI collaborators acknowledged for their contributions
- **Major Testing Integration Success** - 6 hardware integrations, 100% test pass rate
- **Production Ready Status** - Workshop deployment ready with real hardware validation
- **Dual-Device Workflows** - Multi-device coordination fully operational
- **Tab Separation System** - Complete modular tab architecture across all three suites
- Ready for GitHub rendering (centered, clean, dark/light theme safe)
- SEO-friendly with clear project keywords (Ford, GM, Diagnostics)
