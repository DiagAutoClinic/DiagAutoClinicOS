# Layout 1: The Kinetic Schematic Workspace

## 1. Layout Architecture
**Concept**: A "Digital Twin" approach where the UI mimics the physical reality of the machine. The interface is not a set of lists, but a spatial representation of the system being diagnosed.
**Structure**:
- **The Viewport (Center, 60%)**: A large, interactive schematic or topology map of the selected system. This is the primary work surface.
- **The System Navigator (Left, 15%)**: A hierarchical tree organizing the machine by physical assembly (e.g., Powertrain > Fuel Delivery > Low Pressure Side).
- **The Instrument Deck (Bottom, 25%)**: A persistent "workbench" containing live telemetry tools (scopes, gauges) and the "Action Deck" (actuations).
- **Information Density**: High density is achieved through *progressive disclosure* on the schematic. Nodes (components) show simple status colors (Green/Red) until hovered/clicked, which then expands a "Component Card" with detailed live values.

## 2. Tab System: "The Layer Filter"
**Philosophy**: Rejecting the "functional" tabs (Diagnostics, Live Data) in favor of **"Reality Layers"**.
The mechanic does not switch from "Diagnostics" to "Live Data"; they switch from looking at the *wiring* to looking at the *fluid flow*.
**The Tabs**:
1.  **Physical Layer**: Mechanical assembly, mounting, vibration data.
2.  **Electrical Layer**: Wiring diagrams, voltage drops, pinouts, continuity status.
3.  **Logical Layer**: CAN bus topology, module communication, control strategies.
4.  **Hydraulic/Thermal Layer**: Flow paths, temperatures, pressures.

## 3. Functional Zones
- **Context Anchoring**: Top-left "Breadcrumb Bar" (e.g., `Vehicle: Toyota Hilux > System: 1GD-FTV > Subsystem: Common Rail`).
- **Live Data**: Displayed *in-situ* on the schematic. The Fuel Pressure sensor node on the screen displays "3500 bar" directly next to its icon.
- **Fault Reasoning**: When a DTC exists, the affected component on the schematic pulses Red. Clicking it opens the "Reasoning Drawer" which correlates the DTC with the sensor reading and suggested tests.
- **Action Execution**: The "Action Deck" at the bottom right changes based on selection. Select an Injector -> Deck shows "Kill Cylinder", "Flow Test".
- **Logging**: A scrolling "Event Tape" at the bottom left records every state change and user action automatically.

## 4. Visual Language
- **Metaphor**: Technical Blueprint / CAD drawing.
- **Grid**: Strict technical grid with thin hairlines.
- **Typography**: Monospaced fonts for data (JetBrains Mono/Consolas), DIN-style sans-serif for labels.
- **Contrast**: "Dark Mode Blueprint". Deep navy/charcoal background, cyan lines for signals, white for structure, amber/red for alerts. High contrast for readability in dark workshops.
- **Spacing**: Tight, engineered spacing. No whitespace "breathing room"; every pixel is data.

## 5. Operator Psychology
- **Cognitive Load**: Reduces abstraction. The user doesn't have to map a list item "Fuel Pump Status" to the physical pump in their head; the UI does it for them.
- **Structured Reasoning**: Forces the user to traverse the system physically. You can't just "clear all codes"; you must visit the system generating the code.
- **Preventing Randomness**: Actions are context-bound. You cannot press "Regenerate DPF" unless you are in the "Exhaust System" view, preventing accidental global commands.
- **Feel**: Like operating a complex piece of military or medical hardware.

## Layout Map (ASCII)

```text
+-----------------------------------------------------------------------+
|  [VIN: JT1...] [SYS: 1GD-FTV ENGINE]  |  LAYERS: [MECH] [ELEC] [LOGIC]|
+----------------------+------------------------------------------------+
| SYSTEM NAVIGATOR     |  MAIN VIEWPORT (The Schematic)                 |
|                      |                                                |
| [>] Powertrain       |        [ECU]==========(CAN)========[TCU]       |
|  [v] Fuel System     |          |                           |         |
|   [ ] Supply Pump    |      (Inj 1)----[Cyl 1]              |         |
|   [*] Rail Sensor    |          |                           |         |
|   [ ] Injectors      |      (Inj 2)----[Cyl 2]              |         |
| [>] Chassis          |                                                |
|                      |      * Rail Sensor: 35000 kPa (High)           |
|                      |        [Status: Signal Range Error]            |
|                      |                                                |
+----------------------+-----------------------+------------------------+
| EVENT TAPE           | LIVE SCOPE / METER    | ACTION DECK (Context)  |
| 10:14 DTC P0087 Set  | __________________    | [ ] Reset Relief Valve |
| 10:15 Pump Actuated  |      /   \            | [X] Cut-off Cylinder 1 |
|                      | ____/     \_______    | [ ] Leak Test          |
+----------------------+-----------------------+------------------------+
```
