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

# 💖 Sponsors / Support

**DiagAutoClinicOS is currently self-funded by the maintainer (Shaun Smit) and is actively seeking sponsors.**

If this project saves you time or helps your workshop, please consider supporting its development.

> **Support via PayPal → https://paypal.me/diagautoclinic**

Funding options are also listed in `.github/FUNDING.yml`.

---

## 🤝 In-Kind Support / Thanks

The following organizations have provided hardware or resources used during development and testing.

| Contributor                             | Contribution                                                                |
| --------------------------------------- | --------------------------------------------------------------------------- |
| **EshuTech Computers**                  | Development laptop (Acer TravelMate G2 Core i7) for DACOS build environment |
| **GoDiag** — https://godiag.com         | GT100 Plus GPT device for ECU and protocol testing                          |
| **ScanTool.net** — https://scantool.net | OBDLink MX+ adapters for compatibility and reliability testing              |

> In-kind support means hardware or resources were made available to assist development.
> It does **not** imply ongoing financial sponsorship or external funding.

---

## 📋 Sponsor Policy / Transparency

Sponsor relationships remain transparent and auditable.

* Sponsor support must never override safety boundaries, Restricted Mode policy, or verification gates.
* Sponsor influence over security controls is **not permitted**.
* Security mechanisms remain **fail-closed**.
* Sponsor-provided code or artifacts must be reviewable and testable.
* Sponsor acknowledgements remain visible in this repository.

---

# Overview

**DiagAuto Suite** is the first production component of **DiagAutoClinicOS (DACOS)**.

The current release focuses exclusively on:

* **CAN diagnostics**
* **signal analysis**
* **vehicle communication logging**

ECU flashing, immobilizer operations, and security access tooling are **intentionally excluded** from this release and are planned separately in the long-term roadmap.

This design choice prioritizes **stability, safety, and workshop reliability**.

---

## Versioning (clarified)

This project uses multiple version identifiers for different purposes.

| Label                      | Meaning                          | Value     |
| -------------------------- | -------------------------------- | --------- |
| **DiagAuto Suite Version** | Product / public release version | **1.0**   |
| **Installer Version**      | Windows installer build          | **3.2.0** |
| **Internal Build**         | Runtime build lineage            | **3.2.x** |

Implementation note:

`config.py` currently sets:

```
APP_VERSION = "3.2.0"
```

This value represents the **runtime / build identifier** used by the application.

---

## 💬 Statement

> "My software will fight you harder to not brick an ECU than most tools fight to stop piracy."
> — Shaun Smit

---

# Local-Only Artifacts (Not on GitHub)

To protect the DACOS platform and avoid legal or security exposure, certain artifacts are intentionally **not published** in this repository.

These include:

* OEM or proprietary datasets
* Immobilizer / ODM vendor bundles
* Raw workshop CAN captures
* AI training datasets
* Offline training outputs and model artifacts
* Internal verification harnesses
* Security hardening reports
* Runtime logs and Restricted Mode lock artifacts

---

# ✨ Key Features

* Vehicle compatibility tested across **25+ manufacturers** using standard interfaces (**CAN, OBD-II, and J2534**)
* Glassmorphic diagnostic interface built with **PyQt6**
* **Advanced VIN decoding** with Ford and GM recognition
* Secure **user authentication and role management**
* **Calibration and reset manager** with Ford / GM service routines
* Modular architecture allowing tool extensions
* Cross-platform codebase (Windows-first support for v1.0)
* Real **J2534 diagnostic communication**
* Structured CAN reference datasets and signal libraries

### CAN Reference Dataset

The project includes structured CAN reference datasets containing:

* reference CAN captures
* decoded signals
* diagnostic patterns
* workshop research datasets

These datasets support analysis and testing.

> This does **not imply distribution of proprietary OEM databases**.

---

# What DiagAuto Suite Does **NOT** Do

To avoid risk and instability, **v1.0 intentionally excludes**:

* ECU flashing or programming
* key programming
* immobilizer bypass operations
* security access routines
* reverse-engineered vendor drivers
* custom J2534 driver stacks

These capabilities may be introduced in **future modules**, but are not part of this release.

---

# Platform Decision: Windows First

DiagAuto Suite **v1.0** officially supports:

**Windows 10 / 11 (64-bit)**

This decision was made to:

* maximize compatibility with existing diagnostic hardware
* avoid vendor driver limitations on Linux
* ensure reliable workshop deployment

The internal architecture remains **platform-agnostic**, allowing future Linux support once hardware abstraction is complete.

---

# Repository Layout

```
DiagAutoClinicOS/
├── .github/              GitHub configuration
├── AutoDiag/             CAN diagnostics suite
├── AutoECU/              ECU programming module (future)
├── AutoKey/              Key / immobilizer module (future)
├── assets/               Images and static assets
├── core/                 Core shared logic
├── data/                 Reference datasets
├── docs/                 Documentation
├── drivers/              Hardware driver abstraction
├── installers/           Windows installer scripts
├── layout_samples/       UI prototypes
├── live_tests/           Hardware test scripts
├── plans/                Architecture plans
├── pulls/                PR planning notes
├── resources/            Application resources
├── scripts/              Utility scripts
├── shared/               Shared modules
├── tests/                Automated tests
├── ui/                   UI components
├── utils/                General utilities
├── Windows Test/         Windows-specific testing
├── launcher.py           Application entry point
├── config.py             Global configuration
├── requirements.txt      Runtime dependencies
└── requirements-dev.txt  Development dependencies
```

---

# Supported Hardware

DiagAuto Suite communicates through **standard diagnostic interfaces**.

| Device                        | Type                | Status    |
| ----------------------------- | ------------------- | --------- |
| OBDLink MX+ / EX              | OBD-II Adapter      | Supported |
| GoDiag GT100 / GT100 Plus GPT | Breakout + GPT      | Supported |
| Scanmatik 2 / Pro2            | J2534 Pass-Through  | Supported |
| OpenPort 2.0                  | J2534 Interface     | Supported |
| Generic USB K-Line Interfaces | Communication Layer | Supported |

Other devices may function but are not officially validated.

---

# Installation

## System Requirements

* Windows 10 / 11 (64-bit)
* Python 3.10+
* Administrator privileges for hardware drivers
* PowerShell terminal

---

## Windows Installer

Download from the **GitHub Releases page**.

```
AutoDiag_Setup_v3.2.0.exe
```

Installation steps:

1. Download installer
2. Run as Administrator
3. Follow installation wizard
4. Launch AutoDiag from desktop shortcut

Installer features include:

* embedded Python runtime
* pre-installed dependencies
* desktop shortcuts
* Afrikaans language support
* installer validation checks

---

## Running from Source

```
git clone https://github.com/DiagAutoClinic/DiagAutoClinicOS.git
cd DiagAutoClinicOS

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

python launcher.py
```

---

# Architecture Philosophy

DiagAuto Suite separates system responsibilities into clear layers.

* **UI Layer** — PyQt interface
* **Logic Layer** — CAN intelligence and analysis
* **Hardware Layer** — device abstraction
* **Data Layer** — reference datasets and logs

This separation allows future expansion **without breaking v1.0 stability**.

---

# Diagnostic Philosophy

Modern vehicles behave as **distributed computer networks**.

DiagAuto Suite approaches diagnostics using systems analysis principles.

* **ECUs** behave as compute nodes
* **CAN buses** are communication networks
* **Gateways** act as routing boundaries
* diagnostics focus on **signal behavior over time**, not only fault codes

This approach enables deeper insight into vehicle behavior beyond traditional scan tools.

---

# Project Roadmap

| Component             | Status            |
| --------------------- | ----------------- |
| DiagAuto Suite        | Public v1.0 scope |
| AutoECU (Programming) | Planned 2026      |
| AutoKey (IMMO / Keys) | Planned 2026      |
| DACOS Dedicated VCI   | In development    |

---

# Contributing

Contributions are welcome.

Please review **CONTRIBUTING.md** before submitting a pull request.

```
git checkout -b feature/new-module
git commit -am "Add new module"
git push origin feature/new-module
```

Hardware vendors or workshops interested in testing can contact:

**[shaun@diagautoclinic.co.za](mailto:shaun@diagautoclinic.co.za)**
**[dacos@diagautoclinic.co.za](mailto:dacos@diagautoclinic.co.za)**

---

# License

This project is licensed under the **GNU General Public License v3.0**.

You may:

* use
* modify
* redistribute

with the condition that derivative works remain **GPL-licensed**.

No warranty is provided.

---

# Author

**Shaun Smit**
Founder & Lead Engineer — DiagAutoClinic

[shaun@diagautoclinic.co.za](mailto:shaun@diagautoclinic.co.za)

---

# Release Highlights

### Build 3.2.0

Major improvements include:

* completed PyQt6 diagnostic interface
* live vehicle testing with J2534 hardware
* enhanced Ford / GM diagnostic workflows
* VIN recognition improvements
* modular tab architecture
* improved performance and resource handling

---

### Performance Optimization

| Metric         | Result                           |
| -------------- | -------------------------------- |
| Startup Time   | Reduced via lazy initialization  |
| Memory Usage   | Improved through weak references |
| Responsiveness | Faster UI loading                |
| Thread Safety  | Improved synchronization         |
| Resource Leaks | Automatic cleanup mechanisms     |

---

### Hardware Validation

| Device           | Status   | Result                  |
| ---------------- | -------- | ----------------------- |
| GoDiag GD101     | Complete | 100% success            |
| OBDLink MX+      | Complete | 552 CAN messages        |
| Scanmatik 2 Pro  | Complete | Live testing successful |
| GoDiag GT100+GPT | Complete | Full integration        |
