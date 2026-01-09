# Raspberry Pi J2534 VCI Engineering Guide for DACOS

## Overview
This guide outlines the architecture for building a custom High-Performance VCI (Vehicle Communication Interface) using a Raspberry Pi, specifically tailored for DiagAutoClinicOS (DACOS).

**Target Specs:**
- **Core:** Raspberry Pi 4 Model B or 5 (64-bit ARM)
- **Interfaces:** 2x CAN High-Speed, eNET (DoIP), Bluetooth 5.0, WiFi 6
- **Protocols:** ISO15765 (CAN), ISO13400 (DoIP), J2534 PassThru
- **OS:** Linux (Raspberry Pi OS Lite 64-bit)

## 1. Hardware Architecture

### Components
1.  **Compute Module:** Raspberry Pi 4/5 (USB 3.0, Gigabit Ethernet).
2.  **CAN Interface:**
    -   **Recommendation:** 2x MCP2518FD (SPI to CAN FD) HATs or Waveshare 2-CH CAN FD HAT.
    -   **Why:** Supports CAN FD (Flexible Data-rate) required for 2020+ vehicles.
3.  **Physical Layer (PHY):**
    -   TJA1051/3 transceiver (High Speed CAN).
    -   Galvanic Isolation (ISO7741) is CRITICAL to protect the Pi from vehicle voltage spikes.
4.  **Connector:** OBD-II Male connector (J1962).
    -   Pin 6/14: CAN High/Low (Primary).
    -   Pin 3/11: CAN High/Low (Secondary/Multimedia).
    -   Pin 16: Battery Voltage (Need voltage divider to measure on Pi ADC).
    -   Pin 4/5: Ground.

### Schematic Concept
```
[Vehicle OBD-II] <==> [Protection/Isolation] <==> [CAN Transceivers] <==> [SPI Bus] <==> [Raspberry Pi]
       ||                                                                        ||
       ==> [Voltage Divider (12V -> 3.3V)] ====================================> [ADC GPIO]
```

## 2. Firmware (Raspberry Pi Side)

The Pi will run a lightweight Linux daemon that bridges `socketcan` interfaces to a network socket (TCP/UDP) or USB Serial Gadget.

### Software Stack
-   **OS:** Raspberry Pi OS Lite (Headless).
-   **Drivers:** `mcp251x` or `mcp251xfd` kernel modules (Standard in Linux).
-   **Interface:** `can0` and `can1` via SocketCAN.
-   **Daemon:** A Python or C++ application ("DacosVciServer") that:
    1.  Listens on TCP Port 2534.
    2.  Accepts J2534-like commands (Open, Filter, Write, Read).
    3.  Forwards frames to/from `can0`/`can1`.

## 3. Windows Integration (DACOS Side)

Since DACOS runs on Windows 11 (64-bit), it needs a way to talk to the Linux RPi.

### Method A: Network VCI (Recommended for DoIP/WiFi)
-   **Connection:** Ethernet cable (Direct) or WiFi Hotspot.
-   **Driver:** You don't strictly need a J2534 DLL if we modify DACOS to support "Network VCI".
-   **Implementation:**
    -   Modify `vci_manager.py` to add `VCITypes.NETWORK_VCI`.
    -   Use Python `socket` to connect to RPi IP.
    -   **Latency:** < 5ms over Ethernet (Excellent).

### Method B: USB Gadget Mode (Recommended for USB)
-   **Config:** Configure RPi USB-C port as "Ethernet Gadget" (RNDIS) or "Serial Gadget" (CDC-ACM).
-   **Result:** Windows sees a new COM port or Network Adapter when Pi is plugged in.
-   **Advantage:** Looks like a standard USB VCI to Windows.

## 4. Driver Development (J2534 DLL)

If you want the RPi to be compatible with *other* software (like Xentry, ODIS), you must write a J2534 DLL (`dacos_vci.dll`).

1.  **Language:** C/C++.
2.  **Architecture:** 64-bit DLL (for Win 11).
3.  **Function:**
    -   Exports standard J2534 functions (`PassThruOpen`, `PassThruReadMsgs`, etc.).
    -   Internally: Wraps these calls into TCP packets sent to the RPi.
4.  **Registry:** Register the DLL in `HKLM\SOFTWARE\PassThruSupport.04.04\DacosVCI`.

## 5. Development Roadmap

1.  **Phase 1 (Prototype):**
    -   Get RPi 4 + 2-CH CAN HAT.
    -   Install `can-utils` (`candump`, `cansend`).
    -   Verify reading vehicle data via SSH.

2.  **Phase 2 (Python Bridge):**
    -   Write `server.py` on Pi (Socket -> CAN).
    -   Write `client.py` on Windows (PC -> Socket).
    -   Test latency.

3.  **Phase 3 (DACOS Integration):**
    -   Update `AutoDiag` to talk to `client.py` logic.

4.  **Phase 4 (PCB Design):**
    -   Design a "Hat" that fits inside an OBD-II enclosure.
    -   Include 12V-5V buck converter (power Pi from car).

## DACOS Support
I have already updated `j2534_passthru.py` to support dynamic DLL loading, so once you build your `dacos_vci.dll`, you can simply drop it in the `drivers/` folder, and DACOS will recognize it!
