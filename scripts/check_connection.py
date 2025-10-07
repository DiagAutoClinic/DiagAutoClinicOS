#!/usr/bin/env python3
# check_connection.py

import subprocess
import os


def check_connection():
    """Check the status of the OBD II connection"""

    print("🔍 Checking OBD II connection status...")
    print("=" * 40)

    # Check if rfcomm0 exists
    if os.path.exists('/dev/rfcomm0'):
        print("✅ /dev/rfcomm0 exists")

        # Try to communicate with the device
        try:
            import serial
            ser = serial.Serial('/dev/rfcomm0', 38400, timeout=2)
            ser.write(b'ATI\r\n')
            time.sleep(2)
            response = ser.read_all().decode().strip()
            ser.close()

            if 'ELM327' in response:
                print("✅ ELM327 device is responding!")
                print(f"   Device info: {response}")
            else:
                print("⚠ Device responded but not recognized as ELM327:")
                print(f"   {response}")
        except Exception as e:
            print(f"❌ Cannot communicate with device: {e}")
    else:
        print("❌ /dev/rfcomm0 does not exist")

    # Check Bluetooth connections
    print("\n📊 Bluetooth status:")
    result = subprocess.run(['bluetoothctl', 'devices'],
                            capture_output=True, text=True)

    obd_devices = []
    for line in result.stdout.split('\n'):
        if any(keyword in line for keyword in [
               'OBD II', 'OBDII', 'OBD2', 'obd', 'OBD']):
            obd_devices.append(line)

    if obd_devices:
        print("✅ Paired OBD devices:")
        for device in obd_devices:
            print(f"   {device}")
    else:
        print("❌ No OBD devices paired")


if __name__ == "__main__":
    check_connection()
