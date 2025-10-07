#!/usr/bin/env python3
# setup_obd2_bluetooth.py

import subprocess
import time
import sys


def setup_obd2_bluetooth():
    """Setup script specifically for 'OBD II' ELM327 Bluetooth devices"""

    print("🚗 Setting up OBD II ELM327 Bluetooth connection...")
    print("=" * 50)

    # Step 1: Check if Bluetooth is available
    print("1. Checking Bluetooth capabilities...")
    try:
        result = subprocess.run(['which', 'bluetoothctl'],
                                capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Bluetooth tools not found. Installing bluez...")
            subprocess.run(['sudo', 'apt', 'install',
                           '-y', 'bluez', 'bluez-tools'])
    except Exception as e:
        print(f"❌ Error checking Bluetooth: {e}")
        return False

    # Step 2: Start Bluetooth service
    print("2. Starting Bluetooth service...")
    subprocess.run(['sudo', 'systemctl', 'start', 'bluetooth'])
    subprocess.run(['sudo', 'hciconfig', 'hci0', 'up'])

    # Step 3: Scan for devices
    print("3. Scanning for OBD II devices...")
    print("   Please ensure your ELM327 is in pairing mode (blinking blue light)")

    # Start scan in background
    scan_process = subprocess.Popen(['bluetoothctl', 'scan', 'on'],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Let it scan for 15 seconds
    time.sleep(15)
    scan_process.terminate()

    # Step 4: List devices and find OBD II
    print("4. Looking for OBD II device...")
    result = subprocess.run(['bluetoothctl', 'devices'],
                            capture_output=True, text=True)

    obd_device = None
    for line in result.stdout.split('\n'):
        if 'OBD II' in line or 'OBDII' in line or 'OBD2' in line:
            obd_device = line
            break

    if not obd_device:
        print("❌ No OBD II device found. Please ensure:")
        print("   - Device is in pairing mode (blinking blue light)")
        print("   - Device is within range")
        print("   - Bluetooth is enabled on your computer")
        return False

    # Extract MAC address (format: Device MAC_Address Name)
    parts = obd_device.split()
    if len(parts) < 2:
        print("❌ Could not parse device information")
        return False

    mac_address = parts[1]
    print(f"✅ Found OBD II device with MAC: {mac_address}")

    # Step 5: Pair with device
    print("5. Pairing with device (using PIN 1234)...")
    result = subprocess.run(['bluetoothctl', 'pair', mac_address],
                            capture_output=True, text=True, timeout=30)

    if "Pairing successful" not in result.stdout:
        print("❌ Pairing failed. Trying manual method...")
        print("   Please enter '1234' when prompted for PIN")
        input("   Press Enter after pairing manually via Bluetooth settings...")

    # Step 6: Trust and connect
    print("6. Trusting and connecting to device...")
    subprocess.run(['bluetoothctl', 'trust', mac_address])
    subprocess.run(['bluetoothctl', 'connect', mac_address])

    # Step 7: Bind RFCOMM
    print("7. Binding RFCOMM channel...")
    result = subprocess.run(['sudo', 'rfcomm', 'bind', '/dev/rfcomm0', mac_address, '1'],
                            capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ RFCOMM bind failed. Trying with different channel...")
        # Try alternative channels
        for channel in [1, 2, 3]:
            result = subprocess.run(['sudo', 'rfcomm', 'bind', f'/dev/rfcomm{channel}', mac_address, str(channel)],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Bound to /dev/rfcomm{channel}")
                break

    # Step 8: Test connection
    print("8. Testing connection...")
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


if __name__ == "__main__":
    if setup_obd2_bluetooth():
        print("\n🎉 Setup completed successfully!")
        print("   You can now run DiagAutoClinicOS with your OBD II device")
    else:
        print("\n❌ Setup failed. Please try the manual method:")
        print("   1. Open Bluetooth settings")
        print("   2. Scan for devices")
        print("   3. Pair with 'OBD II' using PIN 1234")
        print("   4. Run: sudo rfcomm bind /dev/rfcomm0 [MAC_ADDRESS] 1")
        sys.exit(1)
