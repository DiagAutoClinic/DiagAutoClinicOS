# Layout 2: The Command Center Interface

## 1. Layout Architecture
**Concept**: Derived from "Glass Cockpit" avionics and high-end OEM engineering tools (like BMW ISTA or Mercedes Xentry, but stripped of bloat). It prioritizes *Situational Awareness* and *Command Speed*.
**Structure**:
- **The Status Pillar (Left, 20%)**: A permanent, always-visible column showing the "Health State" of the entire vehicle (Battery V, Ignition, Global DTC count, Connection Status).
- **The Mission Bay (Center, 60%)**: A split-screen capable area for comparing data streams or running tests while watching data.
- **The Soft-Key Rail (Right, 20%)**: A column of large, context-sensitive command buttons (F-Key style) that change based on the active mission.
- **Information Density**: Medium-High. Uses clear, large typography for critical values (RPM, Temp) but allows drilling down into hex data tables.

## 2. Tab System: "The Diagnostic Flight Path"
**Philosophy**: Linear workflow progression. Diagnostics is a procedure with a beginning, middle, and end.
**The Tabs (Top Navigation Bar)**:
1.  **Overview**: Vehicle ID, Global Topology, Quick Health Check.
2.  **Interrogate**: Deep DTC scanning, Freeze Frame analysis.
3.  **Monitor**: Live Data Grid, Custom Parameter Sets.
4.  **Execute**: Bi-directional controls, Actuations.
5.  **Configure**: Coding, Programming, Adaptations.
6.  **Report**: Session logs, customer report generation.

## 3. Functional Zones
- **Vehicle Context**: Integrated into the top header (VIN, Model, Engine Code) with a "Connection Heartbeat" indicator.
- **Live Data**: Presented in the "Mission Bay" as "Data Cards". Users can pin critical PIDs to the top.
- **Fault Reasoning**: "DTCs" are not just a list but clickable objects that open a "Detail overlay" without leaving the main screen.
- **Action Execution**: The Right Rail. If you are in "Monitor" mode looking at Mass Air Flow, the Right Rail offers "Reset Adaptations" or "Calibrate Sensor".
- **Traceability**: A discreet status bar footer shows the last 3 commands sent and their ECU response (e.g., `TX: 22 F1 90 -> RX: 62 F1 90 00 OK`).

## 4. Visual Language
- **Metaphor**: Modern Aviation / Fighter Jet MFD (Multi-Function Display).
- **Grid**: Modular blocks with thick dividers.
- **Typography**: Large, legible HUD-style fonts. Critical warnings in bold caps.
- **Contrast**: "Dark Cockpit". Black background, Slate Grey modules. Active elements are high-intensity Amber (Caution), Red (Critical), or Green (Nominal).
- **Spacing**: Generous touch-target sizing (even for mouse), distinct separation between modules to prevent "wall of text" fatigue.

## 5. Operator Psychology
- **Cognitive Load**: Uses "Heads Up" logic. Key vitals are always in the same place (Left Pillar). The user never has to search for "Battery Voltage" or "Ignition Status".
- **Structured Reasoning**: The top-tab flow (Overview -> Interrogate -> Monitor -> Execute) subtly guides the technician through the correct diagnostic procedure.
- **Preventing Randomness**: The "Soft-Key Rail" limits available actions to those relevant to the current view, preventing invalid commands.
- **Feel**: Authoritative, fast, and responsive. Like a direct line to the ECU's brain.

## Layout Map (ASCII)

```text
+-----------------------------------------------------------------------+
| [AutoDiag] | [1] OVERVIEW  [2] INTERROGATE  [3] MONITOR  [4] EXECUTE  |
+----------------+--------------------------------------+---------------+
| STATUS PILLAR  | MISSION BAY (Split View)             | COMMAND RAIL  |
|                |                                      |               |
| [BATT: 13.8V]  | [ LIVE DATA GROUP: AIR/FUEL ]        | [ SNAPSHOT ]  |
| [IGN:  ON   ]  |                                      |               |
| [VCI:  USB  ]  |  MAF Sensor    [ 4.5 g/s    ]        | [ GRAPH    ]  |
|                |  O2 Sensor B1  [ 0.6 V      ]        |               |
| [GLOBAL DTC]   |  STFT B1       [ +3.5 %     ]        | [ FREEZE   ]  |
|  Engine: 2     |                                      |               |
|  ABS:    0     | ------------------------------------ | [ SELECT   ]  |
|  BCM:    1     | [ DTC DETAIL: P0171 ]                | [ PIDS     ]  |
|                |  System Too Lean (Bank 1)            |               |
| [Quick Erase]  |  > Confirmed                         | [ HELP     ]  |
|                |  > ECU: 0x10 (Engine)                |               |
+----------------+--------------------------------------+---------------+
| LOG: TX 03 ... RX 43 02 01 71 ... [OK]                | [ EXIT     ]  |
+-------------------------------------------------------+---------------+
```
