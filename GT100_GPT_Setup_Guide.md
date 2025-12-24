# GT100 Plus GPT Test Bench Setup Guide

## Hardware Setup

### Required Components
- **GT100 Plus GPT** - Main power supply and breakout box
- **VCI Device** - Choose one:
  - **USB VCI** (GoDiag GD101, etc.)
  - **Bluetooth VCI** (OBDLink MX+, etc.) 
  - **ENET VCI** (Direct Ethernet)
- **Working ECU** - Target for communication testing
- **Cables**:
  - USB cable for VCI to PC
  - OBD2 cable (GT100 female to VCI)
  - 25-pin cable or ethernet cable for ECU connection
- **12V Power Supply** - For GT100

### Physical Connections

**Connection Architecture:**
```
PC (USB/Bluetooth/ENET) 
    ↓
VCI Device (determined by connection type)
    ↓
GT100 Plus GPT (OBDII-16-pin Female Connector)
    ↓
    ├── ECU via 25-pin Port
    └── OR ECU via Ethernet Cable to Male OBDII Connector
    ↓
12V Power Supply to GT100
```

**VCI Connection Types:**

1. **USB VCI** (e.g., GoDiag GD101):
   ```
   PC (USB) → GD101 → GT100 (OBDII Female)
   ```

2. **Bluetooth VCI** (e.g., OBDLink MX+):
   ```
   PC (Bluetooth) → OBDLink MX+ → GT100 (OBDII Female)
   ```

3. **ENET VCI** (Direct Ethernet):
   ```
   PC (Ethernet) → ENET VCI → GT100 (OBDII Female)
   ```

**ECU Connection Options:**

- **25-pin Port**: Direct ECU connector for bench testing
- **Ethernet to Male OBDII**: Use ethernet cable from ECU to GT100's male OBDII connector
- **24V Support**: Available via ethernet connection for heavy-duty ECUs

### Power Configuration
1. **Set GT100 to 12V mode** (for most ECUs)
2. **Verify power output**: Target 12.5V @ 0.1A
3. **Connect Ground**: Ensure solid ground between all components
4. **Check OBD2 pins**: Pins 4 (Ground), 16 (+12V), 6 (CAN High), 14 (CAN Low)

## Running the Test

### Step 1: Connect Hardware
```bash
# Connect all cables as shown above
# Ensure GT100 power is on
# Connect GPT to PC via USB
```

### Step 2: Run Test Script
```bash
python test_gt100_gpt_vci_connection.py
```

### Step 3: Select VCI Type
```
Select VCI Type connected to GT100:
1. USB VCI (GoDiag GD101, etc.)
2. Bluetooth VCI (OBDLink MX+, etc.)
3. ENET VCI (Direct Ethernet)
4. Auto-detect
```

### Step 4: Enter ECU Details
```
Enter ECU type (or press Enter for Generic): [Your ECU Type]
```

## Expected Results

### Successful Test Sequence
1. ✅ **VCI Connection** - VCI device detected and connected
2. ✅ **Power Supply** - 12.5V @ 0.1A confirmed  
3. ✅ **OBD2 Connection** - All critical pins OK
4. ✅ **Protocol Detection** - At least one protocol detected
5. ✅ **Diagnostic Session** - ECU communication established

### Common Issues & Solutions

#### Issue: "USB device not found"
- **Solution**: Check GPT USB connection and driver installation
- **Verify**: Device Manager shows GoDiag device

#### Issue: "Power specs fail" 
- **Solution**: Adjust GT100 voltage to 12.5V
- **Check**: All power connections secure

#### Issue: "OBD2 pins fail"
- **Solution**: Verify cable connections and ECU connector
- **Check**: Pin 16 (+12V) and Pin 4 (Ground) continuity

#### Issue: "J2534 initialization fail"
- **Solution**: Restart GPT device and check USB connection
- **Verify**: J2534 drivers installed correctly

#### Issue: "No protocols detected"
- **Solution**: Check ECU power and ground connections
- **Try**: Different ECU or protocol settings

## Test Output Files

### Generated Files
- **Log File**: `gt100_gpt_vci_test_YYYYMMDD_HHMMSS.log`
- **Report**: `gt100_gpt_vci_test_report_YYYYMMDD_HHMMSS.json`

### Report Contents
- Individual test results with timestamps
- Power measurements and pin status
- Detected protocols and ECU information
- Success/failure summary with percentages

## Troubleshooting Previous Issues

### GT100 Interface Connection Failures
- Ensure GPT passthru is properly connected to GT100
- Verify J2534 library is installed and accessible
- Check for driver conflicts in Device Manager

### Power Specification Compliance
- Calibrate GT100 to exactly 12.5V output
- Use multimeter to verify actual voltage/current
- Check for voltage drop under load

### N32G42x Port Detection
- Use N32G43x port as shown in previous tests (worked in GD101 test)
- Ensure proper USB connection to GPT device
- Verify port configuration in GT100 settings

## Next Steps After Successful Test

1. **Protocol Selection**: Use detected protocol for further testing
2. **ECU Communication**: Establish diagnostic session
3. **Data Collection**: Start live data monitoring
4. **Trouble Codes**: Read and clear DTCs
5. **Special Functions**: Test ECU-specific commands

## Safety Notes

⚠️ **IMPORTANT SAFETY PRECAUTIONS**
- Ensure proper ventilation when ECU is powered
- Avoid short circuits on OBD2 pins
- Use appropriate fuses for 12V supply
- Disconnect power when making cable changes
- Handle ECU with ESD precautions

---
*Generated for GT100 Plus GPT VCI Connection Testing*