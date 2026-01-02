<!-- HEADER -->
<p align="center">
  <img src="https://dacos.co.za/assets/dacos_logo.png" alt="DiagAutoClinic Logo" width="900"/>
</p>

<h1 align="center">DiagAuto Suite</h1>
<h3 align="center">Intelligent CAN Diagnostics & Analysis Platform</h3>

<p align="center">
  <strong>Focused • Hardware-Agnostic • Workshop-Grade</strong><br/>
  Built to analyze, understand, and validate vehicle CAN systems with precision.
</p>

---

## Overview

**DiagAuto Suite** is the first production component of **DiagAutoClinicOS (DACOS)**.

Version **v1.0** is intentionally focused on **CAN diagnostics, analysis, and logging**.
ECU programming and key/immobilizer services are planned for **2026** and are **not part of this release**.

This focus ensures stability, reliability, and real-world usability under workshop conditions.

---

## What DiagAuto Suite Does (v1.0)

DiagAuto Suite is designed to **observe, analyze, and understand vehicle networks** — not to modify them.

### Core Capabilities

* **CAN Database Explorer**

  * 300+ curated CAN definitions
  * ECU ↔ message ↔ signal relationships
  * Fast search and filtering

* **Live CAN Monitoring**

  * Read-only, non-destructive
  * Stable under long sessions
  * Suitable for diagnostics and validation

* **Session Logging**

  * Capture live CAN traffic
  * Replay and compare sessions
  * Ideal for fault reproduction and analysis

* **Vehicle & ECU Profiling**

  * Network discovery
  * ECU presence validation
  * Baseline behavior analysis

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
* Ensure measurable progress and delivery within sponsor timelines

The internal architecture remains **platform-agnostic**, allowing future Linux support once hardware abstraction is complete.

---

## Supported Hardware (v1.0)

DiagAuto Suite is hardware-agnostic and operates through known, stable interfaces.

| Device                          | Role               | Status    |
| ------------------------------- | ------------------ | --------- |
| **Scanmatik Pro2**              | Professional J2534 | Supported |
| **OpenPort 2.0**                | J2534 Pass-Thru    | Supported |
| **OBDLink MX+**                 | CAN Logging        | Supported |
| **Breakout Boxes (GT100 etc.)** | Bench / Harness    | Supported |

> Other interfaces may function but are not officially supported in v1.0.

---

## Architecture Philosophy

DiagAuto Suite separates concerns strictly:

* **UI** — PyQt-based, stable, workshop-friendly
* **Logic** — CAN intelligence and analysis
* **Hardware Access** — abstracted, replaceable
* **Data** — CAN databases and logs

This structure allows future expansion **without breaking v1.0 stability**.

---

## Project Roadmap (High-Level)

| Component                 | Status            |
| ------------------------- | ----------------- |
| **DiagAuto Suite**        | ✅ Released (v1.0) |
| **AutoECU (Programming)** | 🔜 2026           |
| **AutoKey (IMMO / Keys)** | 🔜 2026           |
| **DACOS Dedicated VCI**   | 🔜 In development |

---

## Installation (Development)

```bash
git clone https://github.com/DiagAutoClinic/DiagAutoClinicOS.git
cd DiagAutoClinicOS
pip install -r requirements.txt
python launcher.py
```

> A packaged Windows installer is provided for production deployments.

---

## License

Licensed under **GNU GPL v3.0**.

* Free to use and modify
* Source must remain open
* No warranty is provided

---

## Author & Project Lead

**Shaun Smit**
Founder & Lead Engineer — DiagAutoClinic
📧 [shaun@diagautoclinic.co.za](mailto:shaun@diagautoclinic.co.za)

---

> *DiagAuto Suite is not about shortcuts.
> It is about understanding the machine before touching it.*

- SEO-friendly with clear project keywords (Ford, GM, Diagnostics)
