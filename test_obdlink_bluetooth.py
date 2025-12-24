#!/usr/bin/env python3
"""
Test script for OBDLink MX+ Bluetooth connection
Run this to test Bluetooth connectivity with your OBDLink MX+ 53368 device
"""

import logging
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_vci_manager_bluetooth():
    """Test VCI manager Bluetooth detection and connection"""
    print("Testing OBDLink MX+ Bluetooth Connection")
    print("=" * 50)

    try:
        from AutoDiag.core.vci_manager import get_vci_manager

        # Get VCI manager
        vci_manager = get_vci_manager()
        print("[OK] VCI manager initialized")

        # Scan for devices
        print("\nScanning for VCI devices...")
        devices = vci_manager.scan_for_devices(timeout=15)

        print(f"Found {len(devices)} devices:")
        obdlink_devices = []

        for i, device in enumerate(devices):
            print(f"  {i+1}. {device.name} ({device.device_type.value})")
            print(f"     Port: {device.port}")
            print(f"     Bluetooth: {getattr(device, 'bluetooth_address', 'N/A')}")
            print(f"     Capabilities: {', '.join(device.capabilities)}")

            if "OBDLINK" in device.name.upper() or "BTHENUM" in device.name.upper():
                obdlink_devices.append((i, device))

        if not obdlink_devices:
            print("\n[ERROR] No OBDLink devices found!")
            print("\nTroubleshooting steps:")
            print("1. Ensure OBDLink MX+ is powered on and in Bluetooth pairing mode")
            print("2. Check that Bluetooth is enabled on your computer")
            print("3. Try pairing the device manually in Windows Bluetooth settings")
            print("4. Look for 'OBDLink' in the list of available Bluetooth devices")
            print("5. Once paired, it should appear as a COM port in Device Manager")
            return False

        # Try to connect to first OBDLink device
        device_index, device = obdlink_devices[0]
        print(f"\nAttempting to connect to: {device.name}")

        if vci_manager.connect_to_device(device):
            print("[SUCCESS] Successfully connected to OBDLink MX+!")
            print(f"Device info: {vci_manager.get_device_info()}")

            # Test basic functionality
            print("\nTesting device capabilities...")

            # Disconnect
            vci_manager.disconnect()
            print("[OK] Device disconnected successfully")

            return True
        else:
            print("[ERROR] Failed to connect to OBDLink MX+")
            print("\nPossible issues:")
            print("- Device not properly paired")
            print("- Wrong COM port")
            print("- Device not in range")
            print("- Bluetooth connection issues")
            return False

    except Exception as e:
        print(f"[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_manual_connection():
    """Test manual connection to specific COM ports"""
    print("\nTesting manual COM port connections...")
    print("=" * 40)

    try:
        from shared.obdlink_mxplus import OBDLinkMXPlus

        # Common Bluetooth COM ports
        test_ports = ["COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "COM10"]

        for port in test_ports:
            print(f"Testing {port}...")
            try:
                obdlink = OBDLinkMXPlus(mock_mode=False)
                print(f"  Attempting connection to {port}...")
                if obdlink.connect_serial(port, 38400):
                    print(f"[SUCCESS] Successfully connected to OBDLink MX+ on {port}")

                    # Test device identification
                    print("  Testing device initialization...")
                    obdlink._initialize_device()
                    print("[OK] Device initialized successfully")

                    obdlink.disconnect()
                    print(f"[OK] Test completed on {port}")
                    return True
                else:
                    print(f"[FAIL] Connection failed on {port}")
            except Exception as e:
                print(f"[ERROR] Error on {port}: {e}")

        print("[ERROR] No working COM ports found")
        return False

    except ImportError:
        print("[ERROR] OBDLink MX+ module not available")
        return False

if __name__ == "__main__":
    print("OBDLink MX+ 53368 Bluetooth Connection Test")
    print("=" * 50)
    print("This script will test Bluetooth connectivity with your OBDLink MX+ device")
    print()

    # Test VCI manager
    success = test_vci_manager_bluetooth()

    if not success:
        # Try manual connection test
        print("\nTrying manual COM port detection...")
        success = test_manual_connection()

    print("\n" + "=" * 50)
    if success:
        print("[SUCCESS] Your OBDLink MX+ is ready for use!")
        print("You can now run the main AutoDiag application.")
    else:
        print("[FAILURE] Could not connect to OBDLink MX+")
        print("\nManual setup instructions:")
        print("1. Go to Windows Settings > Devices > Bluetooth & other devices")
        print("2. Click 'Add Bluetooth or other device'")
        print("3. Select 'Bluetooth'")
        print("4. Put your OBDLink MX+ in pairing mode (usually press and hold button)")
        print("5. Select 'OBDLink MX+' from the list")
        print("6. Note the COM port assigned in Device Manager")
        print("7. Run this test script again")