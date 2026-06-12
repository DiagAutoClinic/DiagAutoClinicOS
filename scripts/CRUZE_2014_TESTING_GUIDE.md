# Chevrolet Cruze 2014 Live Testing Guide

## Vehicle Information
- **Make**: Chevrolet
- **Model**: Cruze  
- **Year**: 2014
- **VIN**: KL1JF6889EK617029
- **Odometer**: 115315km
- **Engine**: 1.6L/1.8L
- **Transmission**: Manual/Automatic

## Hardware Requirements

### Primary Device: GoDiag GT101/GD101 (J2534)
- **Function**: Traditional OBD-II diagnostics
- **Protocols**: UDS/ISO14229, KWP2000, J2534
- **Connection**: USB/Serial
- **Port**: COM3 (auto-detected)
- **Baudrate**: 115200

### Secondary Device: OBDLink MX+ (CAN Sniffer)
- **Function**: Real-time CAN bus monitoring
- **Protocols**: ISO15765-11BIT, ISO15765-29BIT
- **Connection**: Bluetooth RFCOMM
- **Channel**: 1
- **Mac Address**: To be paired during setup

## Software Components

### 1. OBDLink MX+ Configuration
**File**: `shared/obdlink_mxplus.py`

**Chevrolet Cruze 2014 Profile**:
```python
'chevrolet_cruze_2014': {
    'name': 'Chevrolet Cruze 2014',
    'vin': 'KL1JF6889EK617029',
    'protocol': OBDLinkProtocol.ISO15765_11BIT,
    'arbitration_ids': {
        'engine': ['7E8', '7E0', '7E1'],      # ECM primary/secondary
        'transmission': ['7E2', '7EA'],        # TCM
        'brakes': ['7B0', '7B1'],              # ABS/EBCM
        'steering': ['7B2', '7B3'],            # Power Steering
        'body': ['7A0', '7A1'],                # BCM
        'instrument': ['7C0', '7C1'],          # IPC
        'climate': ['7D0', '7D1'],             # HVAC
        'safety': ['7E0', '7E1']               # Airbag/SDM
    }
}
```

### 2. Dual Device Engine Configuration
**File**: `AutoDiag/dual_device_engine.py`

**GM Protocol Configuration**:
- Primary Device: GoDiag GD101 with UDS protocol
- Secondary Device: OBDLink MX+ with ISO15765-11BIT
- Vehicle Profile: chevrolet_cruze_2014
- Mode: SYNCHRONIZED

## Testing Scripts

### 1. Main Testing Script
**File**: `scripts/chevrolet_cruze_2014_live_test.py`

**Features**:
- Comprehensive diagnostic suite
- VIN verification
- DTC scanning
- ECU information reading
- CAN traffic analysis
- GM protocol validation
- Automated report generation

### 2. CAN Sniffing Script
**File**: `scripts/can_sniff_obdlink.py`

**Usage**:
```bash
# Mock mode testing
python scripts/chevrolet_cruze_2014_live_test.py

# Live hardware testing
python scripts/chevrolet_cruze_2014_live_test.py --live

# CAN sniffing only
python scripts/can_sniff_obdlink.py --vehicle=chevrolet_cruze_2014 --mock
```

## Setup Instructions

### Phase 1: Mock Mode Testing (Development)
1. **No hardware required**
2. **Perfect for development and testing**
3. **Command**: `python scripts/chevrolet_cruze_2014_live_test.py`
4. **Expected**: All tests pass with mock data

### Phase 2: Live Hardware Testing
1. **Connect GoDiag GD101 via USB**
2. **Pair OBDLink MX+ via Bluetooth**
3. **Command**: `python scripts/chevrolet_cruze_2014_live_test.py --live`

## Safety Precautions

⚠️ **IMPORTANT SAFETY NOTES**:
- Always connect to vehicle when engine is OFF
- Ensure proper ventilation in testing area
- Have emergency contacts ready
- Follow automotive electrical safety procedures
- Use proper isolation when working with live vehicles

## Expected Results

### Mock Mode Results
- VIN Reading: KL1JF6889EK617029 ✓
- DTC Scanning: 2 codes detected ✓
- ECU Info: Available ✓
- CAN Messages: ~50-100 messages ✓
- Protocol Validation: All systems supported ✓

### Live Mode Results (Expected)
- VIN Reading: Should match KL1JF6889EK617029
- DTC Scanning: Actual vehicle codes
- ECU Info: Real ECU data
- CAN Messages: Variable based on vehicle activity
- Protocol Validation: GM-specific compliance

## Troubleshooting

### Common Issues
1. **Bluetooth Connection Failed**
   - Ensure OBDLink MX+ is in pairing mode
   - Check MAC address in device discovery
   - Verify RFCOMM channel 1 is available

2. **J2534 Connection Failed**
   - Check USB connection to GoDiag GD101
   - Verify COM port assignment
   - Try different baudrates (9600, 115200)

3. **CAN Messages Not Captured**
   - Verify ISO15765 protocol configuration
   - Check arbitration ID patterns
   - Ensure vehicle ignition is ON

### Debug Commands
```bash
# Test OBDLink MX+ connection
python -c "from shared.obdlink_mxplus import create_obdlink_mxplus; obd = create_obdlink_mxplus(mock_mode=False); print(obd.discover_devices())"

# Test dual device engine
python -c "from AutoDiag.dual_device_engine import create_dual_device_engine; eng = create_dual_device_engine(mock_mode=False); print(eng.create_session())"
```

## File Outputs

### Test Reports
- **Format**: `cruze_2014_test_report_YYYYMMDD_HHMMSS.txt`
- **Location**: `scripts/` directory
- **Contents**: Complete diagnostic results with CAN analysis

### CAN Captures
- **Format**: `chevrolet_cruze_2014_can_capture_YYYYMMDD_HHMMSS.txt`
- **Location**: `scripts/` directory
- **Contents**: Raw CAN messages with timestamps

## Protocol Analysis

### GM/Chevrolet Specific Features
- **Engine ECUs**: 7E8, 7E0, 7E1 (primary, secondary, backup)
- **Transmission**: 7E2 (TCM)
- **ABS/Brakes**: 7B0, 7B1 (EBCM)
- **Body Control**: 7A0, 7A1 (BCM)
- **Instrument Cluster**: 7C0, 7C1 (IPC)
- **HVAC**: 7D0, 7D1 (Climate)
- **Safety Systems**: 7E0, 7E1 (Airbag SDM)

### Expected Message Rates
- **Idle**: 2-5 messages/second
- **Active**: 10-20 messages/second
- **Diagnostic Activity**: 50-100 messages/second

## Performance Metrics

### Connection Times
- **OBDLink MX+ Discovery**: <10 seconds
- **J2534 Connection**: <5 seconds
- **Vehicle Initialization**: <30 seconds

### Response Times
- **VIN Reading**: <2 seconds
- **DTC Scanning**: <5 seconds
- **ECU Identification**: <3 seconds

## Next Steps After Testing

1. **Validate Results**
   - Compare actual vs expected VIN
   - Analyze DTC codes for accuracy
   - Verify CAN traffic patterns

2. **Performance Optimization**
   - Adjust message filtering
   - Optimize polling rates
   - Fine-tune arbitration IDs

3. **Protocol Enhancement**
   - Add GM-specific PIDs
   - Implement enhanced DTC parsing
   - Create manufacturer-specific reports

4. **Production Deployment**
   - Integrate with main application
   - Add UI controls
   - Implement user management

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-01  
**Target Vehicle**: Chevrolet Cruze 2014 (KL1JF6889EK617029)  
**Hardware**: GoDiag GT100 + OBDLink MX+  
**Status**: Ready for Live Testing