<!-- HEADER -->
<p align="center">
  <img src="https://diagautoclinic.co.za/assets/logo.png" alt="DiagAutoClinic Logo" width="900"/>
</p>

<h1 align="center">DiagAuto Suite</h1>
<h3 align="center">Intelligent CAN Diagnostics & Analysis Platform</h3>

<p align="center">
  <strong>Focused • Hardware-Agnostic • Workshop-Grade</strong><br/>
  Built to analyze, understand, and validate vehicle CAN systems with precision.
</p>

---

## 💖 Sponsors / Support

**DiagAutoClinicOS is currently self-funded by the maintainer (Shaun Smit) and is actively seeking sponsors.**

If this project saves you time or helps your workshop, please consider supporting its development:

> **[💳 Support via PayPal → https://paypal.me/diagautoclinic](https://paypal.me/diagautoclinic)**

Funding options are also listed in [.github/FUNDING.yml](.github/FUNDING.yml).

### 🤝 In-Kind Support / Thanks

The following organisations have provided hardware or resources that assisted development and testing:

| Contributor | Contribution |
| ----------- | ------------ |
| **EshuTech Computers** | Provided a development laptop (Acer TravelMate G2 Core i7) for the DACOS build environment. |
| **GoDiag** — [godiag.com](https://godiag.com) | Provided a GT100 Plus GPT device for ECU and protocol testing. |
| **ScanTool.net** — [scantool.net](https://www.scantool.net) | Provided OBDLink MX+ adapters for compatibility and reliability testing. |

> *In-kind support means hardware/resources were made available to the project. It does not imply ongoing financial sponsorship or that the project is externally funded.*

### 📋 Sponsor Policy / Transparency

Sponsor relationships are kept transparent and auditable:

- Sponsor support must never override safety boundaries, Restricted Mode policy, or verification gates.
- Sponsor influence over security controls is not permitted — security is **fail-closed**.
- Any sponsor-provided code, artifacts, or requirements must be reviewable and testable.
- Sponsor acknowledgements and funding references must remain visible in this repository.

---

## Overview

**DiagAuto Suite** is the first production component of **DiagAutoClinicOS (DACOS)**.

Version **v1.0** is intentionally focused on **CAN diagnostics, analysis, and logging**.
ECU programming and key/immobilizer services are planned for **2026** and are **not part of this release**.

This focus ensures stability, reliability, and real-world usability under workshop conditions.

---

## 💬 Statement

> "My software will fight you harder to not brick an ECU than most tools fight to stop piracy."
> — Shaun Smit

---

## Local-Only Artifacts (Not on GitHub)

To protect the DACOS brand and reduce avoidable exposure, certain artifacts are intentionally kept local and are not published to GitHub:

- OEM/proprietary datasets (immobilizer/ODM databases, vendor bundles)
- CAN bus captures and raw workshop data
- AI training datasets, offline training outputs, and model artifacts
- Internal security verification harnesses and hardening reports
- Runtime logs and Restricted Mode lock artifacts

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
- 🗄️ **SQLite CAN Database** — 1,197 vehicles, 8,481 messages, 20,811 signals

---

## What DiagAuto Suite Does *Not* Do (by design)

To avoid risk and instability, **v1.0 does NOT include**:

* ECU flashing or programming
* Key / immobilizer operations
* Security access or bypass functions
* Custom J2534 driver stacks
* Vendor-specific reverse-engineered drivers

Those features are part of the **2026 roadmap**.

---

## Platform Decision: Windows First

DiagAuto Suite v1.0 officially supports **Windows 10 / 11 (64-bit)**.

This decision was made to:

* Maximize compatibility with existing diagnostic hardware
* Avoid vendor driver limitations on Linux
* Ensure measurable progress and delivery within timelines

The internal architecture remains **platform-agnostic**, allowing future Linux support once hardware abstraction is complete.

---

## 📁 Repository Layout / File Structure

```
DiagAutoClinicOS/
├── .github/               # GitHub configuration (FUNDING.yml, workflows, etc.)
├── AutoDiag/              # DiagAuto Suite — CAN diagnostics & analysis (v1.0)
├── AutoECU/               # ECU programming suite (2026 roadmap)
├── AutoKey/               # Key / immobilizer suite (2026 roadmap)
├── assets/                # Images and static assets
├── core/                  # Core shared logic and engine
├── data/                  # CAN databases and reference data
├── docs/                  # Documentation files
├── drivers/               # Hardware driver abstractions
├── installers/            # Windows installer scripts (Inno Setup)
├── layout_samples/        # UI layout examples and prototypes
├── live_tests/            # Real-hardware live test scripts
├── plans/                 # Architecture and feature plans
├── resources/             # Application resources (icons, themes, etc.)
├── scripts/               # Utility and automation scripts
├── shared/                # Shared modules used across suites
├── ui/                    # UI components and widgets
├── utils/                 # General-purpose utilities
├── Windows Test/          # Windows-specific test helpers
├── launcher.py            # Main entry point — launches the selected suite
├── config.py              # Global configuration
├── requirements.txt       # Python dependencies
└── requirements-dev.txt   # Development dependencies
```

---

## 🔌 Supported Hardware

DiagAuto Suite is hardware-agnostic and operates through known, stable interfaces.

| Device                                   | Type                | Status      |
| ---------------------------------------- | ------------------- | ----------- |
| **OBDLink MX+ / EX**                     | OBD-II Adapter      | ✅ Supported |
| **GoDiag GT100 / GT100 Plus GPT**        | Breakout Box + GPT  | ✅ Supported |
| **Scanmatik 2 / Pro2**                   | J2534 Pass-Through  | ✅ Supported |
| **OpenPort 2.0**                         | J2534 Pass-Thru     | ✅ Supported |
| **Generic USB/K-Line/D-Line Interfaces** | Communication Layer | ✅ Supported |

> Other interfaces may function but are not officially supported in v1.0.

---

## 🚀 Installation & Setup

### System Requirements
* **OS:** Windows 10 / 11 (64-bit)
* **Python:** 3.10 or higher
* **Permissions:** Administrator privileges required for hardware access
* **Shell:** PowerShell (via integrated Terminal)

### 🪟 Windows Installer (Recommended)

Download the latest installer from the [Releases](https://github.com/DiagAutoClinic/DiagAutoClinicOS/releases) page:

1. **Download** `AutoDiag_Setup_v3.2.0.exe`
2. **Run** the installer as Administrator
3. **Follow** the installation wizard (supports Afrikaans)
4. **Launch** AutoDiag Pro from the desktop shortcut

**Features:**
- ✅ Complete Python environment included
- ✅ All dependencies pre-installed
- ✅ Desktop shortcuts created
- ✅ File associations configured
- ✅ Afrikaans language support
- ✅ Professional installer with validation

### Running from Source

```bash
git clone https://github.com/DiagAutoClinic/DiagAutoClinicOS.git
cd DiagAutoClinicOS
python -m venv venv
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt
python launcher.py
```

---

## Architecture Philosophy

DiagAuto Suite separates concerns strictly:

* **UI** — PyQt-based, stable, workshop-friendly
* **Logic** — CAN intelligence and analysis
* **Hardware Access** — abstracted, replaceable
* **Data** — CAN databases and logs

This structure allows future expansion **without breaking v1.0 stability**.

---

## Charlemaine Fine-Tuning System

This repository includes a physics-grounded synthetic training pipeline for fine-tuning Charlemaine on diagnostic reasoning.

### Generate Training Data

```bash
python training_generator.py --train-size 2000 --val-size 200 --test-size 300 --augmentation 2 --output-dir training_data
```

### Fine-Tune on OpenAI

```bash
python finetune_runner.py openai --train-file training_data/train_openai.jsonl --val-file training_data/val_openai.jsonl --model gpt-4o-mini-2024-07-18 --monitor
```

### Evaluate Dataset or Models

```bash
python finetune_runner.py evaluate --test-file training_data/test.jsonl --model-type raw
python finetune_runner.py evaluate --test-file training_data/test.jsonl --model-type openai --model-id ft:your-model-id --api-key $OPENAI_API_KEY --max-examples 200
python finetune_runner.py compare --test-file training_data/test.jsonl --model-ids ft:modelA,ft:modelB --api-key $OPENAI_API_KEY --max-examples 200
```

---

## Project Roadmap (High-Level)

| Component                 | Status            |
| ------------------------- | ----------------- |
| **DiagAuto Suite**        | ✅ Released (v1.0) |
| **AutoECU (Programming)** | 🔜 2026           |
| **AutoKey (IMMO / Keys)** | 🔜 2026           |
| **DACOS Dedicated VCI**   | 🔜 In development |

---

## 🛠️ Contributing

Contributions are welcome!
Fork the repo, submit pull requests, or help with testing and documentation.

```bash
git checkout -b feature/new-module
git commit -am "Add new module"
git push origin feature/new-module
```

If you're a hardware vendor or workshop interested in integration testing, reach out at:

📧 **shaun@diagautoclinic.co.za** | **dacos@diagautoclinic.co.za**

---

## 🧾 License

This project is licensed under the **GNU General Public License v3.0**.

- ✅ Free to use, modify, and distribute
- ✅ Source code must remain open
- ✅ Derivative works must use GPL v3
- ⚠️ No warranty provided

See the [LICENSE](LICENSE) file for complete terms.
For commercial licensing inquiries, contact: **dacos@diagautoclinic.co.za**

---

## Author & Project Lead

**Shaun Smit**
Founder & Lead Engineer — DiagAutoClinic
📧 [shaun@diagautoclinic.co.za](mailto:shaun@diagautoclinic.co.za)

---

## 🎯 Release Notes / Highlights

### v3.2.0 — Windows Installer Ready, Enhanced Validation

#### 🚗 Ford and GM Market Focus
This release specifically targets Ford and GM's presence, with enhanced support for popular models.

#### ✨ What's New
- **Completed Futuristic GUI** - Dynamic glassmorphic PyQt6 interface fully implemented
- **Live Testing Phase** - Active real-world testing with J2534 hardware and Ford/GM vehicles
- **Enhanced Ford/GM Diagnostics** - Real J2534 support for Ford and GM live testing
- **Advanced VIN Recognition** - Model-specific identification for Ford and GM models
- **SA Testing Guide** - Comprehensive procedures for Global conditions
- **Professional Documentation** - Complete Ford/GM diagnostic manuals and video frameworks
- **Hardware Integration** - GoDiag GD101 and J2534 device support
- **Tab Separation System** - Modular tab architecture across all three suites
- **Customization Framework** - Easy tab copy-paste between suites for user customization

#### ✅ Installer Validation — December 16, 2025

| Component | Score | Status | Details |
|-----------|-------|---------|---------|
| **Script Syntax** | 95/100 | ✅ Excellent | All syntax validated |
| **File Structure** | 100/100 | ✅ Perfect | 33 files verified |
| **Configuration** | 90/100 | ✅ Very Good | All settings correct |
| **Security** | 80/100 | ✅ Good | Admin privileges handled |
| **Documentation** | 95/100 | ✅ Excellent | Complete guides updated |

#### 📊 Hardware Integration Status — December 1, 2025

| Device | Status | Test Results | Performance |
|--------|--------|--------------|-------------|
| **GoDiag GD101** | ✅ Complete | J2534 PassThru | 100% Success |
| **OBDLink MX+** | ✅ Complete | Dual-Device | 552 CAN msgs |
| **HH OBD Advance** | ✅ Complete | OBD Handler | All tests passed |
| **ScanMatik 2 Pro** | ✅ Complete | Professional | Live testing successful |
| **GoDiag GT100+GPT** | ✅ Complete | Breakout + GPT | 100% Integration |

#### 🚀 Performance Optimization — December 28, 2025

| Metric | Result |
|--------|--------|
| **Startup Time** | Significantly reduced via lazy initialization |
| **Memory Usage** | Optimized with weak references and forced GC |
| **Responsiveness** | Immediate — placeholder tabs defer heavy init |
| **Thread Safety** | Enhanced synchronization and cleanup (0.106s) |
| **Resource Leaks** | Eliminated via automatic WeakSet cleanup |

#### ✅ alpha_v0.0.1 Highlights
- Windows Installer with Afrikaans language support
- 6 hardware integrations validated — 100% test pass rate
- Performance optimization: lazy loading, thread management, resource cleanup
- Tab Separation System — modular tab architecture across all three suites
