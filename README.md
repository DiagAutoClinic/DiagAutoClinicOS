<!-- HEADER -->

<p align="center">
  <img src="https://diagautoclinic.co.za/assets/logo.png" alt="DiagAutoClinic Logo" width="900"/>
</p>

<h1 align="center">DiagAuto Suite</h1>
<h3 align="center">Intelligent CAN Diagnostics &amp; Analysis Platform</h3>

<p align="center">
  <strong>Focused • Hardware-Agnostic • Workshop-Grade</strong><br/>
  Built to analyze, understand, and validate vehicle CAN systems with precision.
</p>

---

# Sponsors / Support (most important)

**DiagAutoClinicOS is currently self-funded by the maintainer (Shaun Smit) and is actively seeking sponsors.**

If this project saves you time or helps your workshop, please consider supporting its development.

> **Support via PayPal → https://paypal.me/diagautoclinic**

Funding options are also listed in `.github/FUNDING.yml`.

---

## Hardware Validation

![GD101 Validated](https://img.shields.io/badge/GD101-Validated-green) ![Real-time CAN](https://img.shields.io/badge/Real--time_CAN-500kbps-blue) ![Security Access](https://img.shields.io/badge/Security_Access-<100ms-orange)

**Validated on:**
- Godiag GD101 J2534 device
- 500kbps CAN timing with microsecond precision
- ISO-TP fragmentation (FF/CF/FC with BS/STmin)
- Sub-100ms security access (0x27 service)
- USB hotplug recovery with auto-reconnect
- Concurrent session isolation (8 sessions)

**Test vehicles:** Pre-2010 vehicles (per safety protocol)

---

## In-Kind Support / Thanks

The following organizations have provided hardware or resources used during development and testing.

| Contributor                             | Contribution                                                                |
| --------------------------------------- | --------------------------------------------------------------------------- |
| **EshuTech Computers**                  | Development laptop (Acer TravelMate G2 Core i7) for DACOS build environment |
| **GoDiag** — https://godiag.com         | GT100 Plus GPT device for ECU and protocol testing                          |
| **ScanTool.net** — https://scantool.net | OBDLink MX+ adapters for compatibility and reliability testing              |

> In-kind support means hardware or resources were made available to assist development.
> It does **not** imply ongoing financial sponsorship or external funding.

---

## Sponsor Policy / Transparency

Sponsor relationships remain transparent and auditable.

- Sponsor support must never override safety boundaries, Restricted Mode policy, or verification gates.
- Sponsor influence over security controls is **not permitted**.
- Security mechanisms remain **fail-closed**.
- Sponsor-provided code or artifacts must be reviewable and testable.
- Sponsor acknowledgements remain visible in this repository.

---

# Overview

**DiagAuto Suite** is the first production component of **DiagAutoClinicOS (DACOS)**.

The current release focuses exclusively on:

- **CAN diagnostics**
- **signal analysis**
- **vehicle communication logging**

ECU flashing, immobilizer operations, and security access tooling are **intentionally excluded** from the AutoDiag alpha scope and are planned separately in the long-term roadmap.

This design choice prioritizes **stability, safety, and workshop reliability**.

---

## Versioning

This repository contains multiple components with different maturity levels.

- **AutoDiag**: diagnostics module (alpha readiness target: `v0.1`)
- **AutoECU**: programming module (alpha readiness target: `v0.1`, safety-gated)
- **AutoKey**: security/IMMO module (planned)

`config.py` currently sets the runtime/build version (example):

```python
APP_VERSION = "3.2.0"
```

---

## Statement

> "My software will fight you harder to not brick an ECU than most tools fight to stop piracy."
> — Shaun Smit

---

# Repository Layout

This tree is kept in sync with the repository root.

```text
DiagAutoClinicOS/
├── .github/                 GitHub configuration (CI, funding, templates)
├── AutoDiag/                CAN diagnostics suite (PyQt6)
├── AutoECU/                 ECU programming module (alpha / safety-gated)
├── AutoKey/                 Key / immobilizer module (planned)
├── assets/                  Images and static assets
├── core/                    Core shared logic
├── data/                    Reference datasets
├── docs/                    Documentation
├── drivers/                 Hardware driver abstraction / J2534 DLL drop-in
├── installers/              Windows installer scripts
├── layout_samples/          UI prototypes / layout concepts
├── live_tests/              Hardware test scripts
├── plans/                   Architecture plans
├── pulls/                   PR planning notes
├── resources/               Application resources
├── scripts/                 Utility scripts
├── shared/                  Shared modules
├── tests/                   Automated tests
├── ui/                      UI components (shared)
├── utils/                   General utilities
├── Windows Test/            Windows-specific testing
├── check_theme.py           Theme verification helper
├── check_vci.py             VCI verification helper
├── config.py                Global configuration
├── dtc_faults_dataset.json  DTC dataset
├── launcher.py              Suite launcher (PyQt6)
├── launch_autodiag.bat      Convenience launcher for AutoDiag
├── requirements.txt         Runtime dependencies
├── requirements-dev.txt     Development dependencies
├── requirements_32bit.txt   32-bit dependency set
├── pytest.ini               Test configuration
└── version_info.txt         Version info
```

---

# Installation

## System Requirements

- Windows 10 / 11 (64-bit)
- Python 3.10+
- Administrator privileges for hardware drivers

## Running from Source

```bash
git clone https://github.com/DiagAutoClinic/DiagAutoClinicOS.git
cd DiagAutoClinicOS
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
python launcher.py
```

---

# License

This project is licensed under the **GNU General Public License v3.0**.

---

# Author

**Shaun Smit**  
Founder & Lead Engineer — DiagAutoClinic  
[shaun@diagautoclinic.co.za](mailto:shaun@diagautoclinic.co.za)
