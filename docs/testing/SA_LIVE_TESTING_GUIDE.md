# South Africa Live Vehicle Testing Guide - VW Polo & Golf

## Overview
This guide provides comprehensive instructions for conducting live diagnostic testing with Volkswagen Polo and Golf vehicles in South African conditions.

## Prerequisites

### Hardware Requirements
- **J2534 Device**: GoDiag GD101 or compatible PassThru device
- **OBD-II Cable**: Standard SAE J1962 connector
- **Computer**: Windows/Linux with DiagAutoClinicOS installed
- **Power Source**: Reliable 12V battery (vehicle or external)

### Software Requirements
- DiagAutoClinicOS v3.1.0+
- Python 3.8+
- PyQt6
- J2534 drivers installed

### Safety Requirements
- Vehicle on level surface with parking brake engaged
- Engine off unless specifically required
- No smoking near vehicle
- Fire extinguisher nearby
- Emergency contact numbers programmed

## Vehicle Preparation

### Polo Models (6R, 6C, 9N, AW)
1. Ensure vehicle is parked in well-ventilated area
2. Turn ignition to ON position (engine off)
3. Verify dashboard lights illuminate
4. Locate OBD-II port (under steering column)

### Golf Models (IV, V, VI, VII, VIII)
1. Park in shaded area (South African heat considerations)
2. Ignition ON, engine OFF
3. Check for any existing dashboard warning lights
4. OBD-II port typically under dashboard left side

## Testing Procedures

### 1. VIN Reading Test
```
Expected Results:
- Polo: WVWZZZ6R* (6R series)
- Golf: WVWZZZ1K* (V series) or WVWZZZ3V* (VII series)
- Clean VIN display without errors
```

### 2. DTC Scan Test
```
Common SA Environment DTCs:
- P0171: System Too Lean (dust/fuel quality)
- P0300: Random Misfire (heat/stress)
- P0420: Catalyst Efficiency (emissions)
- U0100: Lost Communication (electrical noise)
```

### 3. DTC Clear Test
```
Procedure:
1. Scan DTCs first
2. Clear all codes
3. Cycle ignition OFF/ON
4. Re-scan (should be clean)
```

## South African Considerations

### Environmental Factors
- **Heat**: Test in morning hours (before 30°C ambient)
- **Dust**: Clean OBD-II port before connection
- **Humidity**: Coastal areas may affect connections
- **Altitude**: Johannesburg testing vs. coastal

### Fuel Quality Issues
- Common DTCs: P0171, P0174 (lean mixture)
- Solution: Use premium fuel for testing
- Document fuel type used

### Electrical Interference
- Urban areas: High electrical noise
- Rural areas: Generator interference possible
- Solution: Test away from power sources

## Troubleshooting Common Issues

### Connection Problems
```
Symptom: "Failed to connect to vehicle"
Solutions:
1. Verify OBD-II port voltage (should be ~12V)
2. Clean port contacts
3. Try different ignition positions
4. Check fuse box for OBD-II power
```

### Communication Errors
```
Symptom: "No response from ECU"
Solutions:
1. Wait 30 seconds after ignition ON
2. Check for immobilizer issues
3. Verify J2534 device drivers
4. Try different protocol (KWP2000 vs UDS)
```

### Hardware Compatibility
```
GoDiag GD101 Issues:
- Update firmware to latest version
- Use original cable (3m max length)
- Avoid extension cables
```

## Test Reporting Template

### Vehicle Information
- Make/Model: __________
- Year: __________
- VIN: __________
- Engine: __________
- Mileage: __________
- Fuel Type: __________

### Test Environment
- Location: __________
- Ambient Temperature: __________
- Time of Day: __________
- Battery Voltage: __________

### Test Results
- VIN Read: PASS/FAIL
- DTC Scan: PASS/FAIL (list codes)
- DTC Clear: PASS/FAIL
- Connection Stability: GOOD/FAIR/POOR

### Issues Encountered
- Hardware: __________
- Software: __________
- Environmental: __________

## Emergency Procedures

### Vehicle Won't Start After Testing
1. Disconnect all diagnostic equipment
2. Wait 2 minutes
3. Attempt normal start
4. If failed, check battery connections
5. Contact roadside assistance

### Software Crashes
1. Close DiagAutoClinicOS
2. Disconnect J2534 device
3. Restart computer
4. Reconnect and retry

## Contact Information

### Technical Support
- GitHub Issues: https://github.com/DiagAutoClinic/DiagAutoClinicOS/issues
- South African User Group: [Create Discord/Slack group]

### Emergency Services
- Roadside Assistance: 083 000 0000 (Example)
- Nearest Garage: __________

## Legal Considerations

### South African Regulations
- Testing on public roads prohibited
- Private property testing only
- No modifications without authorization
- Data privacy compliance (POPIA)

### Warranty Considerations
- Document all testing activities
- Avoid clearing manufacturer DTCs
- Recommend professional diagnosis for warranty claims

## Success Metrics

### Acceptance Criteria
- 95% successful VIN reads
- 90% successful DTC scans
- 85% successful DTC clears
- No vehicle damage during testing

### Performance Benchmarks
- Connection time: < 30 seconds
- Scan time: < 60 seconds
- Clear time: < 10 seconds

---

*This guide is specific to South African conditions and VW Polo/Golf testing. Always prioritize safety and follow local regulations.*