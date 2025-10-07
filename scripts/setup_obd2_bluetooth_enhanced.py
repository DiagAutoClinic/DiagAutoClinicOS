#!/usr/bin/env python3
# setup_obd2_bluetooth_enhanced.py

import subprocess
import time
import sys
import os


def setup_obd2_bluetooth():
    """Enhanced setup script for OBD II ELM327 Bluetooth devices"""

    print("🚗 Enhanced OBD II ELM327 Bluetooth Setup")
    print("=" * 50)

    # Step 1: Check if device is already connected via rfcomm
    print("1. Checking for existing connections...")
    if os.path.exists('/dev/rfcomm0'):
        try:
            import serial
            ser = serial.Serial('/dev/rfcomm0', 38400, timeout=2)
            ser.write(b'ATI\r\n')
            time.sleep(2)
            response = ser.read_all().decode().strip()
            ser.close()

            if 'ELM327' in response:
                print("✅ Already connected to ELM327 device!")
                print(f"   Device response: {response}")
                return True
        except Exception as e:
            print(f"   Device exists but not responding: {e}")

    # Step 2: Check if device is paired but not connected
    print("2. Checking for paired devices...")
    result = subprocess.run(['bluetoothctl', 'devices'],
                            capture_output=True, text=True)

    obd_device = None
    for line in result.stdout.split('\n'):
        if any(keyword in line for keyword in [
               'OBD II', 'OBDII', 'OBD2', 'obd', 'OBD']):
            obd_device = line
            break

    if not obd_device:
        print("❌ No OBD device found in paired devices.")
        print("   Please pair your device first via Bluetooth settings.")
        print("   Look for 'OBD II' and use PIN '1234'")
        return False

    # Extract MAC address
    parts = obd_device.split()
    if len(parts) < 2:
        print("❌ Could not parse device information")
        return False

    mac_address = parts[1]
    print(f"✅ Found OBD device with MAC: {mac_address}")

    # Step 3: Establish serial connection
    print("3. Establishing serial connection...")
    try:
        # Release any existing binding
        subprocess.run(['sudo', 'rfcomm', 'release', '/dev/rfcomm0'],
                       capture_output=True)

        # Bind to the device
        result = subprocess.run(['sudo', 'rfcomm', 'bind', '/dev/rfcomm0', mac_address, '1'],
                                capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            print(f"❌ RFCOMM bind failed: {result.stderr}")
            # Try alternative channel
            print("   Trying alternative channel...")
            result = subprocess.run(['sudo', 'rfcomm', 'bind', '/dev/rfcomm0', mac_address, '2'],
                                    capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print(f"❌ RFCOMM bind with channel 2 failed: {result.stderr}")
                return False

        print("✅ Serial connection established!")

        # Step 4: Test connection
        print("4. Testing connection...")
        try:
            import serial
            ser = serial.Serial('/dev/rfcomm0', 38400, timeout=2)
            ser.write(b'ATI\r\n')
            time.sleep(2)
            response = ser.read_all().decode().strip()
            ser.close()

            if 'ELM327' in response:
                print("✅ Successfully connected to ELM327 device!")
                print(f"   Device response: {response}")
                return True
            else:
                print("⚠ Connected but unexpected response:")
                print(f"   {response}")
                return True
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False

    except Exception as e:
        print(f"❌ Error establishing serial connection: {e}")
        return False


if __name__ == "__main__":
    if setup_obd2_bluetooth():
        print("\n🎉 Setup completed successfully!")
        print("   You can now run DiagAutoClinicOS with your OBD II device")
    else:
        print("\n❌ Setup failed. Please try these steps manually:")
        print("   1. Open Bluetooth settings")
        print("   2. Ensure your OBD II device is paired (use PIN 1234)")
        print("   3. Right-click on the device and select 'Serial Connection'")
        print("   4. Or run: sudo rfcomm bind /dev/rfcomm0 [MAC_ADDRESS] 1")
        sys.exit(1)
