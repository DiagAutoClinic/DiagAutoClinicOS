# Layout 3: The Industrial Logic Interface

## 1. Layout Architecture
**Concept**: Modeled after SCADA (Supervisory Control and Data Acquisition) and PLC logic analyzers (like Siemens TIA Portal or Rockwell Studio 5000). It treats the vehicle as a plant to be monitored and debugged.
**Structure**:
- **The Project Tree (Left, 20%)**: A strict hierarchical view of every addressable module, sensor, and actuator, organized by bus (CAN-C, CAN-B, LIN).
- **The Canvas (Center, 55%)**: A workspace for "Block Diagrams" or "Logic Traces". Not just values, but relationships.
- **The Signal Watch (Right, 25%)**: A pinned list of specific memory addresses or PIDs being watched in real-time with high-precision values.
- **The Terminal (Bottom, Collapsible)**: Raw hex traffic, debug logs, and system messages.

## 2. Tab System: "The Engineer's Perspective"
**Philosophy**: Tabs represent the *level of abstraction*.
**The Tabs (Bottom-aligned or Ribbon)**:
1.  **Network Topology**: The physical bus connections and gateway status.
2.  **Signal Trace**: Time-based logging and graphing of specific signals.
3.  **Memory/Hex**: Direct memory access, EEPROM viewing, hex editing.
4.  **I/O Check**: Inputs and Outputs status table (Digital/Analog).
5.  **Alarms/DTC**: The "Fault Table" view.

## 3. Functional Zones
- **Vehicle Context**: Defined as a "Project". "Project: Ford_Ranger_2022.dacos".
- **Live Data**: Displayed in the "Signal Watch" panel or as "Tags" on the Canvas.
- **Fault Reasoning**: Faults are treated as "Alarms". They appear in a dedicated alarm list with timestamps, occurrence counts, and "Acknowledge" status.
- **Action Execution**: Actions are "Force Values". You don't "Turn on Fan"; you "Force Output DO_FAN_01 = TRUE".
- **Traceability**: Extreme. Every signal change is timestamped to the millisecond in the Terminal.

## 4. Visual Language
- **Metaphor**: Industrial Control Panel.
- **Grid**: Dense data tables, Excel-like structures, collapsible tree nodes.
- **Typography**: Small, high-density sans-serif (Verdana/Tahoma) for maximum data visibility.
- **Contrast**: "Control Room Grey". Light grey backgrounds, dark text, standard Windows-style controls but flattened. Very functional, low fatigue. Color is reserved strictly for status (Green=Run, Red=Stop/Fault).
- **Spacing**: Minimal. Designed for mouse/keyboard input, not touch.

## 5. Operator Psychology
- **Cognitive Load**: Offloads memory by showing the full hierarchy. The user sees exactly where a component fits in the network.
- **Structured Reasoning**: Encourages a "Signal Flow" mindset. Input -> Logic -> Output. If the Output is wrong, check the Logic, then the Input.
- **Preventing Randomness**: The "Force Value" metaphor implies danger and requires explicit enabling (e.g., a "Safety Interlock" toggle before actuations are allowed).
- **Feel**: Engineering-grade. Powerful, raw, and transparent. Nothing is hidden behind a "user-friendly" abstraction.

## Layout Map (ASCII)

```text
+-----------------------------------------------------------------------+
| MENU | TOOLBAR: [CONNECT] [START TRACE] [STOP] [FORCE ENABLE]         |
+----------------------+-----------------------------+------------------+
| PROJECT TREE         | MAIN CANVAS [Logic View]    | SIGNAL WATCH     |
|                      |                             |                  |
| [-] CAN-C (500k)     |  [ECM Input]                | Name     | Val   |
|  [-] ECM (0x7E0)     |       |                     | ---------------- |
|   [+] Memory         |    (Pedal %) > [ 25% ]      | RPM      | 850   |
|   [-] I/O            |       |                     | V_BATT   | 14.1  |
|     - DI_Ignition    |    [Logic Block]            | PEDAL_P  | 25%   |
|     - AI_Pedal_Pos   |       | (Map)               | THR_ANG  | 12%   |
|     - DO_Injector    |       v                     | T_COOL   | 98C   |
|  [+] TCM (0x7E1)     |    (Throttle) < [ 12% ]     |                  |
|  [+] ABS (0x760)     |                             |                  |
+----------------------+-----------------------------+------------------+
| TERMINAL / ALARMS                                                     |
| [10:22:01.450] [CAN-C] ID:120 LEN:8 DATA: 00 A1 FF ...                |
| [10:22:01.455] [ALARM] DTC P2138 Active - Pedal Pos Correlation       |
+-----------------------------------------------------------------------+
| [NETWORK] [SIGNALS] [MEMORY] [I/O] [ALARMS]                           |
+-----------------------------------------------------------------------+
```
