# AutoDiag Suite Strict Release Task List

**Target:** Initial Release (v1.0)
**Mandate:** Focus entirely on AutoDiag Suite. AutoECU/AutoKey deferred.

## 1. Critical Path (Release Blockers)

### Hardware Communication & Protocols
- [x] **Protocol Mode Verification**: Confirm `VCIManager` correctly switches between Hardware ISO-TP (J2534) and Software ISO-TP (CAN/ELM327).
- [ ] **Real Hardware Verification**: Test with at least one J2534 device (e.g., Tactrix/Scanmatik) and one ELM327 device.
- [x] **Bus Stability**: Implement bus silence detection/recovery (keep-alive messages) to prevent session drops.

### Core Diagnostics Features
- [x] **DTC Database Integration**: Replace generic DTC descriptions with a real lookup system (SQLite/JSON) for SAE P0xxx and Manufacturer P1xxx codes.
- [x] **Live Data Equation Parsing**: Implement equation solver (e.g., `A*0.5 + 10`) to convert raw bytes to physical values based on PID definitions.
- [x] **Full System Scan Loop**: Implement the logic to iterate through a list of module IDs (ECU, TCU, ABS, SRS, etc.) and query DTCs for each.
- [x] **Security Access (Seed-Key)**: Implement Service 0x27 handling for protected routines (Basic algorithm support).

### Reporting & Output
- [x] **PDF Report Generation**: Implement a reporting engine to export Scan Results/DTCs to PDF with workshop header.

### Licensing & Protection
- [x] **Password Hashing**: Upgraded to Scrypt (Memory-Hard, GPU-Resistant) to prevent brute-force attacks.
- [x] **SQL Injection Audit**: Verified parameterized queries in User, DTC, and CAN databases.
- [x] **Tier Enforcement**: Verify `check_tier_access` locks out Pro/Master features for Basic users.
- [ ] **Offline Token Caching**: Ensure validated license works offline for at least 7 days.

## 2. High Priority (User Experience)

- [ ] **Live Data Graphing**: Simple line graph for up to 4 selected PIDs.
- [ ] **Thread Safety Audit**: Ensure no long-running VCI operations block the Qt Main Thread (prevent "Not Responding").
- [ ] **Log Rotation**: Implement `RotatingFileHandler` for logs.

## 3. Packaging & Distribution

- [ ] **Installer Script**: Create Inno Setup script or PyInstaller spec for standalone executable generation.
- [ ] **Dependency Bundling**: Ensure `python-can`, `pyserial`, `PyQt6` are correctly bundled.

## 4. Deferred (Post-Release)

- AutoECU (Programming/Cloning)
- AutoKey (Immobilizer)
- Remote Diagnostics
- Cloud Sync
- Advanced Bi-Directional Controls (beyond basic resets)

## 5. Completed / Verified
- [x] **ISO-TP Layer**: `isotp_handler.py` implemented (Software SAR).
- [x] **VCI Manager**: `VCIManager` structure complete with J2534/ELM327 abstractions.
- [x] **UDS Basics**: `send_uds_request` implemented and integrated.
- [x] **Architecture**: BaseTab, ResponsiveHeader, and Controller structure validated.
