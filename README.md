
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
- ✅ 25+ brand diagnostic coverage  
- 🧠 Dynamic glassmorphic UI built with **PyQt6**  
- 🧩 **VIN decoding**, **DTC database**, and **live data streaming**  
- 🔐 Secure **login and user role management**  
- ⚙️ **Calibration & reset manager** with custom ECU routines  
- 🧱 **Modular design** — easily extend with your own tools  
- 🖥️ **Cross-platform:** Linux, Windows (Android support planned)  

---

## 🧱 File Structure

```plaintext
DiagAutoClinicOS/
│
├── AutoDiag/               # Main diagnostic dashboard
│   └── main.py
│
├── AutoECU/                # ECU programming and firmware management
│   └── main.py
│
├── AutoKey/                # Key programming and immobilizer functions
│   └── main.py
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
│   └── vin_decoder.py
│
├── scripts/                # Utility scripts and setup tools
│   ├── setup_bluetooth.py
│   ├── release_bluetooth.py
│   └── update_dependencies.py
│
├── tests/                  # Unit and integration tests
│   ├── AutoDiag/
│   ├── shared/
│   └── integration_tests/
│
├── launcher.py             # Main startup script
├── requirements.txt        # Python dependencies
└── README.md               # You are here ✨
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

<p align="center">   <img  src="https://diagautoclinic.co.za/assets/sponsors.png"></p><br/>   <p align="center"><h1><sub>Powered by <strong>Our Proud Sponsors</strong></sub></h1></p>

------

## 💡 Acknowledgements

| Contributor                     | Role                     | Description                             |
| ------------------------------- | ------------------------ | --------------------------------------- |
| **Shaun Smit**                  | Founder & Lead Developer | Architecture, Design, Implementation    |
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

> “Empowering independent workshops — one diagnostic suite at a time.”

DiagAutoClinicOS is built to bring  open-source transparency, modularity, and innovation to the automotive  diagnostic space — with a focus on **local engineering excellence in South Africa** and community-driven collaboration worldwide.

------

## 🛠️ Contributing

Contributions are welcome!
 Fork the repo, submit pull requests, or help with testing and documentation.

```

git checkout -b feature/new-module
git commit -am "Add new module"
git push origin feature/new-module
```

If you’re a hardware vendor or workshop interested in integration testing, reach out at:
 📧 **shaun@diagautoclinic.co.za**

 | **dacos@diagautoclinic.co.za**

------

## 🧾 License

Licensed under the **MIT License**.
 Feel free to use, modify, and distribute — attribution appreciated.

------

### ✅ What’s New in This Version

- Added **dynamic badges** (Release, Python, License, Last Commit, Stars)
- Retains full structure and sponsor recognition
- Ready for GitHub rendering (centered, clean, dark/light theme safe)
- SEO-friendly with clear project keywords (Diagnostic, ECU, Automotive, Open Source

