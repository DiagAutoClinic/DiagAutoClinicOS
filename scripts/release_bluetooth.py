#!/usr/bin/env python3
# release_bluetooth.py

import subprocess
import os
import time


def release_bluetooth_connection():
    """Release Bluetooth connections and kill processes using rfcomm"""

    print("🔓 Releasing Bluetooth connections...")

    # Step 1: Find and kill processes using rfcomm devices
    print("1. Finding processes using Bluetooth devices...")
    try:
        # Check for processes using any rfcomm device
        result = subprocess.run(['lsof', '/dev/rfcomm*'],
                                capture_output=True, text=True)
        if result.returncode == 0 and result.stdout:
            print("   Processes found using Bluetooth:")
            print(result.stdout)

            # Kill all processes using rfcomm
            subprocess.run(['sudo', 'pkill', '-f', '/dev/rfcomm'])
            print("   Terminated processes using Bluetooth devices")
    except Exception as e:
        print(f"   Error finding processes: {e}")

    # Step 2: Release all rfcomm bindings
    print("2. Releasing RFCOMM bindings...")
    try:
        # List all rfcomm devices
        result = subprocess.run(['rfcomm'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'rfcomm' in line:
                    parts = line.split()
                    if parts and parts[0].startswith('rfcomm'):
                        device = parts[0]
                        print(f"   Releasing {device}...")
                        subprocess.run(['sudo', 'rfcomm', 'release', device])
        else:
            print("   No RFCOMM devices found or error listing devices")
    except Exception as e:
        print(f"   Error releasing RFCOMM: {e}")

    # Step 3: Disconnect Bluetooth devices
    print("3. Disconnecting Bluetooth devices...")
    try:
        # Get list of connected devices
        result = subprocess.run(['bluetoothctl', 'devices'],
                                capture_output=True, text=True)
        if result.returncode == 0:
            devices = []
            for line in result.stdout.split('\n'):
                if 'OBD II' in line or 'OBDII' in line or 'OBD2' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        mac_address = parts[1]
                        devices.append(mac_address)

            # Disconnect each device
            for mac in devices:
                print(f"   Disconnecting {mac}...")
                subprocess.run(['bluetoothctl', 'disconnect', mac])
    except Exception as e:
        print(f"   Error disconnecting devices: {e}")

    # Step 4: Remove any stale lock files
    print("4. Cleaning up lock files...")
    lock_files = [
        '/var/lock/LCK..ttyRFCOMM0',
        '/var/lock/LCK..ttyRFCOMM1',
        '/var/lock/LCK..ttyRFCOMM2',
        '/run/lock/LCK..ttyRFCOMM0',
        '/run/lock/LCK..ttyRFCOMM1',
        '/run/lock/LCK..ttyRFCOMM2'
    ]

    for lock_file in lock_files:
        if os.path.exists(lock_file):
            try:
                os.remove(lock_file)
                print(f"   Removed {lock_file}")
            except Exception as e:
                print(f"   Error removing {lock_file}: {e}")

    print("✅ Bluetooth resources released successfully!")
    print("   You can now reconnect your device.")


if __name__ == "__main__":
    release_bluetooth_connection()
