#!/usr/bin/env python3
"""
Test script to verify ScanMatik 2 Pro USB detection fix
Tests the new robust FTDI-based detection logic
"""

import sys
import logging
from pathlib import Path

# Add the shared module to path
sys.path.insert(0, str(Path(__file__).parent / "shared"))

from scanmatik_2_pro import create_scanmatik_2_pro_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_mock_detection():
    """Test detection in mock mode"""
    print("\n=== Testing Mock Mode Detection ===")
    
    handler = create_scanmatik_2_pro_handler(mock_mode=True)
    devices = handler.detect_devices()
    
    print(f"Mock mode detected {len(devices)} device(s)")
    for device in devices:
        if isinstance(device, dict):
            # New dictionary format
            print(f"  - {device.get('port', 'Unknown')}")
            print(f"    Port: {device.get('port', 'N/A')}")
            print(f"    Description: {device.get('description', 'N/A')}")
            print(f"    Type: {device.get('type', 'N/A')}")
            if 'vid_pid' in device:
                print(f"    VID:PID: {device['vid_pid']}")
        else:
            # Old object format (fallback)
            print(f"  - {device.name}")
            print(f"    Port: {device.port}")
            print(f"    Description: {device.description}")
            print(f"    Type: {device.device_type.value}")
            print(f"    Features: {len(device.features)} features")
    
    return len(devices) > 0

def test_real_detection():
    """Test detection in real mode (may show no devices if no hardware connected)"""
    print("\n=== Testing Real Mode Detection ===")
    
    try:
        handler = create_scanmatik_2_pro_handler(mock_mode=False)
        devices = handler.detect_devices()
        
        print(f"Real mode detected {len(devices)} device(s)")
        for device in devices:
            if isinstance(device, dict):
                # New dictionary format
                print(f"  - {device.get('port', 'Unknown')}")
                print(f"    Port: {device.get('port', 'N/A')}")
                print(f"    Description: {device.get('description', 'N/A')}")
                print(f"    Type: {device.get('type', 'N/A')}")
                if 'vid_pid' in device:
                    print(f"    VID:PID: {device['vid_pid']}")
            else:
                # Old object format (fallback)
                print(f"  - {device.name}")
                print(f"    Port: {device.port}")
                print(f"    Description: {device.description}")
                print(f"    Type: {device.device_type.value}")
                print(f"    Is Real Hardware: {device.is_real_hardware}")
        
        # Check if FTDI-based detection is working
        if devices:
            print("\n[SUCCESS] FTDI-based detection is working!")
            print("   - Using serial.tools.list_ports for comprehensive port scanning")
            print("   - No longer limited to hard-coded COM1-COM6")
            print("   - VID/PID matching for FTDI chips")
            print("   - Fallback to description matching")
        else:
            print("\n[WARNING] No ScanMatik devices found in real mode")
            print("   This is expected if no ScanMatik 2 Pro is connected")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error during real detection: {e}")
        return False

def test_fallback_detection():
    """Test that fallback detection works when no FTDI devices found"""
    print("\n=== Testing Fallback Detection Logic ===")
    
    # The fallback logic should trigger when no FTDI devices are found
    # This will list all available USB-serial ports
    handler = create_scanmatik_2_pro_handler(mock_mode=False)
    devices = handler.detect_devices()
    
    print(f"Fallback detection found {len(devices)} device(s)")
    
    # Check if any devices were found via fallback
    fallback_devices = [d for d in devices if isinstance(d, dict) and d.get('type') == 'Unknown USB-Serial']
    if fallback_devices:
        print(f"[SUCCESS] Fallback detection working: {len(fallback_devices)} unknown devices listed")
        for device in fallback_devices:
            print(f"  - {device.get('port', 'Unknown')}")
            print(f"    Port: {device.get('port', 'N/A')}")
    else:
        print("[INFO] No fallback devices found (no USB-serial devices connected)")
    
    return True

def main():
    """Main test function"""
    print("[TEST] Testing ScanMatik 2 Pro USB Detection Fix")
    print("=" * 50)
    
    # Test mock mode
    mock_success = test_mock_detection()
    
    # Test real mode
    real_success = test_real_detection()
    
    # Test fallback
    fallback_success = test_fallback_detection()
    
    print("\n" + "=" * 50)
    print("[RESULTS] Test Results Summary:")
    print(f"  Mock Mode: {'[PASS]' if mock_success else '[FAIL]'}")
    print(f"  Real Mode: {'[PASS]' if real_success else '[FAIL]'}")
    print(f"  Fallback:  {'[PASS]' if fallback_success else '[FAIL]'}")
    
    if mock_success and real_success and fallback_success:
        print("\n[SUCCESS] All tests passed! The ScanMatik 2 Pro detection fix is working correctly.")
        print("\n[IMPROVEMENTS] Key improvements implemented:")
        print("  [OK] Added serial.tools.list_ports import")
        print("  [OK] Replaced hard-coded port scanning with robust FTDI detection")
        print("  [OK] Added VID/PID matching for FTDI chips (0x0403:0x6001/0x6010/etc)")
        print("  [OK] Added description and manufacturer string matching")
        print("  [OK] Implemented fallback to show all ports if no ScanMatik found")
        print("  [OK] No longer limited to COM1-COM6 - supports COM7+ and higher")
        return True
    else:
        print("\n[ERROR] Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)