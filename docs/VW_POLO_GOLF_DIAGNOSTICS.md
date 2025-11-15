# VW Polo & Golf Diagnostic Guide

## Overview
This guide provides comprehensive diagnostic procedures for Volkswagen Polo and Golf models using DiagAutoClinicOS.

## Supported Models

### Polo Series
| Model | Generation | Years | Key Features |
|-------|------------|-------|--------------|
| Polo 6R | 6th Gen | 2017+ | MQB platform, UDS protocol |
| Polo Classic | 6C | 2014-2017 | PQ25 platform, KWP2000 |
| Polo 9N | 4th Gen | 2001-2009 | PQ24 platform, KWP2000 |
| Polo Vivo | AW | 2010-2014 | PQ25 platform, KWP2000 |

### Golf Series
| Model | Generation | Years | Key Features |
|-------|------------|-------|--------------|
| Golf VIII | 8th Gen | 2019+ | MQB Evo, UDS, 48V mild hybrid |
| Golf VII | 7th Gen | 2012-2019 | MQB platform, UDS |
| Golf VI | 6th Gen | 2008-2012 | PQ35 platform, KWP2000/UDS |
| Golf V | 5th Gen | 2003-2008 | PQ35 platform, KWP2000 |
| Golf IV | 4th Gen | 1997-2003 | PQ34 platform, KWP2000 |

## Diagnostic Protocols

### UDS (ISO 14229) - Modern Models
- **Golf VII/VIII, Polo 6R**: Primary protocol
- **Services**: 0x22 (ReadDataByIdentifier), 0x19 (ReadDTC), 0x14 (ClearDTC)
- **ECUs**: Engine, Transmission, ABS, Airbag, Gateway

### KWP2000 (ISO 14230) - Older Models
- **Golf IV/V/VI, Polo 9N/6C/AW**: Legacy protocol
- **Services**: Similar to UDS but different addressing
- **ECUs**: Limited to major control units

## Common Diagnostic Procedures

### 1. Pre-Diagnostic Checks
```bash
# Verify vehicle compatibility
python -c "from shared.vin_decoder import VINDecoder; print(VINDecoder().decode('YOUR_VIN_HERE'))"

# Check J2534 device status
python -c "from shared.j2534_passthru import get_passthru_device; print(get_passthru_device())"
```

### 2. VIN Reading
**Purpose**: Vehicle identification and model verification

**Procedure**:
1. Connect GoDiag GD101 to OBD-II port
2. Turn ignition ON (engine OFF)
3. Launch DiagAutoClinicOS
4. Select Volkswagen brand
5. Click "Read VIN"

**Expected Results**:
- Clean 17-character VIN
- Correct model identification (Polo/Golf + generation)
- No communication errors

### 3. DTC Scanning
**Purpose**: Identify fault codes and system issues

**Procedure**:
1. Successful VIN read
2. Click "Scan DTCs"
3. Wait for scan completion (~30-60 seconds)

**Common Polo DTCs**:
- P0300-P0304: Cylinder misfire codes
- P0171/P0174: Fuel system lean/rich
- U0100: Lost communication with ECM
- P0420: Catalyst efficiency below threshold

**Common Golf DTCs**:
- P0300-P0304: Misfire codes
- C1140: EBCM module malfunction
- P1545: Boost pressure control malfunction
- U0121: Lost communication with ABS

### 4. DTC Clearing
**Purpose**: Reset fault codes after repair

**Procedure**:
1. Complete DTC scan
2. Click "Clear DTCs"
3. Confirm action in dialog
4. Re-scan to verify clearance

**Important Notes**:
- Some codes may reappear if issue persists
- Manufacturer codes may require dealer tools
- Document all cleared codes for warranty purposes

## Model-Specific Considerations

### Polo 6R (MQB Platform)
**ECU Locations**:
- Engine ECU: Under intake manifold
- BCM: Behind glovebox
- ABS: Left rear wheel well

**Common Issues**:
- Start-stop system faults
- AdBlue system (diesel models)
- Electric parking brake

### Golf VII (MQB Platform)
**ECU Locations**:
- Gateway: Under driver's seat
- Engine ECU: Right side of engine bay
- Transmission: Under vehicle, rear

**Common Issues**:
- Infotainment system faults
- DCC (Dynamic Chassis Control)
- Lane keeping assist

### Golf VI (PQ35 Platform)
**ECU Locations**:
- Engine ECU: Left side of engine bay
- ABS/ESP: Under vehicle, front left
- Airbag: Under center console

**Common Issues**:
- Timing chain issues (1.4 TSI)
- DSG transmission faults
- Haldex coupling (4Motion)

## Troubleshooting Guide

### Connection Issues
**Symptom**: "Failed to connect to vehicle"
```
Solutions:
1. Verify ignition position (ON, engine OFF)
2. Check OBD-II port voltage (~12V)
3. Clean port contacts
4. Try different J2534 protocol
5. Update GoDiag firmware
```

### Communication Errors
**Symptom**: "No response from ECU"
```
Solutions:
1. Wait 30+ seconds after ignition ON
2. Check for immobilizer activation
3. Verify battery voltage (>11.5V)
4. Try different OBD-II port if multiple
5. Check fuse box for OBD-II power
```

### Model Recognition Issues
**Symptom**: Incorrect model displayed
```
Solutions:
1. Verify VIN format (17 characters)
2. Check WMI code (WVW for VW)
3. Update VIN decoder patterns
4. Manual model selection if needed
```

## Advanced Diagnostics

### Live Data Streaming
**Available Parameters**:
- Engine RPM, coolant temp, intake air temp
- Battery voltage, throttle position
- ABS wheel speeds, brake pressure
- Transmission temperature, gear position

### Special Functions
**VW-Specific Functions**:
- DPF Regeneration (diesel models)
- Throttle Valve Adaptation
- Steering Angle Calibration
- Battery Adaptation (start-stop systems)

## Maintenance Schedules

### Polo Service Intervals
- Oil change: Every 15,000 km or 12 months
- Brake fluid: Every 2 years
- Timing belt: 120,000 km (if equipped)
- AdBlue: Top up as needed (diesel)

### Golf Service Intervals
- Oil change: Every 15,000-30,000 km (varies by engine)
- Brake fluid: Every 2 years
- Timing chain: Lifetime (some models)
- DSG fluid: Every 60,000 km

## Safety Precautions

### Electrical Safety
- Never work on high-voltage systems without training
- Disconnect battery before ECU work
- Use insulated tools
- Avoid static discharge near ECUs

### Vehicle Safety
- Park on level surface with parking brake
- Chock wheels when working underneath
- Never run engine in enclosed spaces
- Have fire extinguisher nearby

## Warranty Considerations

### South African Warranty
- 2-year/60,000 km manufacturer warranty
- Extended warranty options available
- Service history critical for resale
- Independent repairs may void warranty

### Documentation Requirements
- Keep all service records
- Document DTC codes and repairs
- Use genuine VW parts for warranty work
- Follow VW service schedules

## Tools and Equipment

### Required Hardware
- GoDiag GD101 or compatible J2534 device
- OBD-II extension cable (optional)
- Multimeter for voltage checks
- Service manual (digital preferred)

### Software Tools
- DiagAutoClinicOS v3.1+
- VCDS (for comparison, optional)
- ODIS (dealer software, optional)

## Training Resources

### Online Resources
- VW Service Training manuals
- iATN (International Automotive Technicians Network)
- YouTube VW diagnostic channels

### Local SA Resources
- VWSA (Volkswagen South Africa) training
- Independent workshop networks
- Automotive training colleges

## Emergency Procedures

### Vehicle Won't Start After Diagnostics
1. Disconnect all diagnostic equipment
2. Wait 2 minutes
3. Attempt normal start
4. Check battery connections if failed
5. Contact VW dealer or roadside assistance

### ECU Communication Lost
1. Turn ignition OFF for 5 minutes
2. Check fuse box
3. Try different OBD-II port
4. Reset ECU (consult service manual)
5. Professional diagnosis if persistent

---

## Quick Reference Tables

### Polo Engine Codes
| Engine | Code | Displacement | Fuel |
|--------|------|--------------|------|
| 1.0 TSI | CHYA | 1.0L | Petrol |
| 1.2 TSI | CJZC | 1.2L | Petrol |
| 1.4 TDI | CUSA | 1.4L | Diesel |
| 1.6 TDI | CAYC | 1.6L | Diesel |

### Golf Engine Codes
| Engine | Code | Displacement | Fuel |
|--------|------|--------------|------|
| 1.0 TSI | CHPA | 1.0L | Petrol |
| 1.4 TSI | CAXC | 1.4L | Petrol |
| 1.6 TDI | CAYC | 1.6L | Diesel |
| 2.0 TDI | CKFC | 2.0L | Diesel |

### Common DTC Patterns
| DTC Range | System |
|-----------|--------|
| P0100-P0199 | Fuel/Air System |
| P0200-P0299 | Fuel Injectors |
| P0300-P0399 | Ignition/Misfire |
| P0400-P0499 | Emissions/EGR |
| P0500-P0599 | Speed/Idle Control |

---

*This guide is specific to VW Polo and Golf diagnostics. Always consult service manuals for model-specific procedures.*