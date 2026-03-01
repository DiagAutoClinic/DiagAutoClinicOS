# GitHub Copilot Instructions — DiagAutoClinicOS (DACOS)

## 🧭 Project Overview

**DiagAutoClinicOS (DACOS)** is an open-source, modular automotive diagnostic desktop suite built by **Shaun Smit** and the DiagAutoClinic team. It targets independent automotive workshops, with a focus on the **South African market** (Ford and GM prominence).

The platform consists of three suites:

- **AutoDiag** ← 🔴 CURRENT PRIORITY — Complete for production
- **AutoECU** ← Planned for later in 2025
- **AutoKey** ← Planned for later in 2025

Licensed under **GPL-3.0**. All code must remain open-source compatible.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Primary language | Python 3.10+ (3.13 target) |
| UI framework | PyQt6 (glassmorphic design) |
| Hardware protocols | J2534, OBD-II, CAN bus, ISO-TP, ISO15765-11BIT |
| Low-level comms | C / C++ (device drivers, protocol layers) |
| Supported devices | GoDiag GD101, OBDLink MX+, HH OBD Advance, ScanMatik 2 Pro, GT100+GPT, ELM327 Bluetooth |
| Cross-platform | Linux (Ubuntu primary), Windows (Alpha) |
| VIN/DTC | Custom VIN decoder, DTC database with Ford/GM specifics |

---

## 🗂️ Repository Structure

```
DiagAutoClinicOS/
├── AutoDiag/               # 🔴 ACTIVE SUITE — Main diagnostic dashboard
│   ├── main.py
│   └── ui/
│       ├── dashboard_tab.py
│       ├── diagnostics_tab.py
│       ├── live_data_tab.py
│       ├── special_functions_tab.py
│       ├── calibrations_tab.py
│       ├── advanced_tab.py
│       └── security_tab.py
├── AutoECU/                # ECU programming (future)
├── AutoKey/                # Key/immobilizer (future)
├── core/                   # Shared diagnostic engine
│   ├── calibrations.py
│   ├── device_manager.py
│   ├── diagnostics.py
│   ├── security.py
│   └── special_functions.py
├── shared/                 # Shared modules across all suites
│   ├── brand_database.py
│   ├── dtc_database.py
│   ├── vin_decoder.py
│   ├── device_handler.py
│   ├── security_manager.py
│   ├── style_manager.py
│   ├── theme_constants.py
│   └── widgets/
├── ui/                     # App-level UI
├── tests/                  # Full test suite
├── docs/                   # Documentation
├── scripts/                # Build and setup scripts
├── launcher.py             # Entry point
└── config.py
```

---

## 🎯 Current Development Priority: AutoDiag → Production

Copilot's primary focus is to **complete AutoDiag for production release**. This means:

1. All AutoDiag tabs must be fully functional with real J2534 hardware
2. Live data streaming must be stable and performant
3. DTC read/clear operations must complete in < 2 seconds
4. VIN reading must complete in < 1 second
5. The UI must be polished, glassmorphic, and responsive
6. Error handling must be comprehensive — never crash, always recover gracefully

**Do not** make changes to AutoECU or AutoKey unless explicitly asked. Keep those modules stable and untouched while AutoDiag is in focus.

---

## 🚗 Domain Knowledge

### Vehicle Brands
- Primary focus: **Ford** and **GM** (South African market dominant)
- 25+ brand coverage total
- VIN decoding must distinguish Ford/GM models specifically

### Hardware Communication
- J2534 Pass-Through is the primary interface standard
- ELM327 Bluetooth used for consumer-grade connections
- CAN bus captures run at ~18.4 messages/second in live testing
- ISO15765-11BIT protocol confirmed working

### Diagnostic Concepts
- **DTC** = Diagnostic Trouble Code (read, clear, interpret)
- **ECU** = Engine Control Unit (programming handled in AutoECU)
- **VIN** = Vehicle Identification Number (decoded in `shared/vin_decoder.py`)
- **J2534** = SAE standard for vehicle communication interfaces
- **OBD-II** = On-Board Diagnostics standard (Mode 01–0A)
- **CAN bus** = Controller Area Network (vehicle data bus)

---

## 💻 Coding Standards & Conventions

### General
- Python: Follow **PEP 8** strictly
- All functions and classes must have **docstrings**
- Use **type hints** on all function signatures
- Prefer explicit over implicit — no magic numbers, use named constants from `shared/theme_constants.py` and `config.py`
- Never hardcode device paths or credentials

### PyQt6 UI
- All UI must use the **glassmorphic theme** defined in `shared/style_manager.py` and `shared/theme_constants.py`
- Use the existing **custom widgets** in `shared/widgets/` before creating new ones
- UI updates from background threads must always use **Qt signals/slots** — never call UI methods directly from threads
- All tabs follow the existing **tab separation architecture** documented in `TAB_SEPARATION_SUMMARY.md`

### Hardware / Device Communication
- All device I/O must be in **separate threads** — never block the main UI thread
- Use `core/device_manager.py` as the single point of device access
- Always implement **timeout handling** and **retry logic** for hardware calls
- Log all hardware interactions with timestamps for diagnostics

### C / C++
- Used only for low-level device drivers and protocol layers
- Must compile cleanly with no warnings on both Linux (GCC) and Windows (MSVC)
- Python bindings via `ctypes` or `cffi` — document the interface clearly

### Error Handling
- Use structured exception handling — catch specific exceptions, not bare `except:`
- All hardware failures must surface a user-friendly message in the UI
- Log errors to file with full stack traces
- The app must **never crash** — implement fallback/recovery for all failure modes

---

## 🧪 Testing

- Tests live in `tests/` with subdirectories per suite and concern
- **Always write or update tests** when adding or modifying features
- Use mock hardware in `tests/mock/` for unit tests — real hardware only in `live_tests/`
- Performance benchmarks go in `tests/performance/`
- Security tests go in `tests/security/`
- Target: all AutoDiag features must have test coverage before production release

---

## 📝 Documentation

- All new features must include documentation in `docs/`
- Public-facing API/module docs use **Google-style docstrings**
- Hardware setup and usage guides go in `docs/testing/`
- Update `CHANGELOG.md` with every significant change using semantic versioning (e.g. `v3.2.0`)
- Keep `README.md` current — it is the public face of the project

---

## 🔐 Security

- Refer to `SECURITY.md` for the project's security policy
- User roles and login are managed via `shared/security_manager.py` — do not bypass
- No secrets, API keys, or credentials in source code — use environment variables or config files excluded via `.gitignore`
- All security-sensitive changes must include a note for human review

---

## 🌍 Context: South African Market

- Primary users are **independent automotive workshops** in South Africa
- Ford and GM are the most common vehicles serviced
- Internet connectivity may be limited — the app must function **fully offline**
- Documentation should be practical and workshop-floor friendly
- Hardware must be tested against South African vehicle populations (see `docs/testing/`)

---

## 🤝 Collaboration Notes

- The lead developer (**Shaun Smit**) reviews all Copilot-generated code before merging
- When multiple approaches exist, prefer the one that is **most maintainable** and fits the existing architecture
- If a task requires modifying `core/` or `shared/` modules, **note the impact** on AutoECU and AutoKey even if those suites are not the current focus
- Flag any TODO items clearly with `# TODO(copilot):` comments for human review
- Do not refactor working code speculatively — only refactor when it directly enables a feature or fixes a bug

---

## ✅ Definition of "Production Ready" for AutoDiag

AutoDiag is production-ready when:

- [ ] All 7 tabs are fully functional (`dashboard`, `diagnostics`, `live_data`, `special_functions`, `calibrations`, `advanced`, `security`)
- [ ] Real J2534 hardware integration is stable across all supported devices
- [ ] DTC read/clear < 2 seconds, VIN read < 1 second
- [ ] Glassmorphic UI is complete and consistent
- [ ] All critical paths have test coverage
- [ ] Documentation is complete for workshop users
- [ ] No known crashes or data loss scenarios
- [ ] `CHANGELOG.md` updated for release version
