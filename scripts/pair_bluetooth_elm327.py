#!/usr/bin/env python3

import subprocess
import time
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def pair_elm327_device():
    """Complete Bluetooth pairing process for ELM327 device"""
    try:
        print("🔵 Starting ELM327 Bluetooth pairing process...")

        # Check if bluetoothctl is available
        result = subprocess.run(
            ['which', 'bluetoothctl'], capture_output=True, text=True)
        if result.returncode != 0:
            print(
                "❌ bluetoothctl not found. Please install bluez: sudo apt install bluez bluez-tools")
            return False

        # Start Bluetooth controller
        print("🔄 Turning on Bluetooth...")
        subprocess.run(['sudo', 'systemctl', 'start', 'bluetooth'])
        subprocess.run(['sudo', 'hciconfig', 'hci0', 'up'])

        # Start bluetoothctl in interactive mode
        print("🔍 Scanning for Bluetooth devices...")
        scan_process = subprocess.Popen(['bluetoothctl', 'scan', 'on'],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Let it scan for a bit
        time.sleep(10)
        scan_process.terminate()

        # List discovered devices
        print("📋 Listing discovered devices...")
        list_process = subprocess.Popen(['bluetoothctl', 'devices'],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        text=True)
        stdout, stderr = list_process.communicate()

        # Look for ELM327 devices (typically start with "OBD" or "ELM")
        elm_devices = []
        for line in stdout.split('\n'):
            if any(keyword in line for keyword in [
                   'OBD', 'ELM', 'obd', 'elm']):
                elm_devices.append(line)

        if not elm_devices:
            print(
                "❌ No ELM327 devices found. Please ensure your device is in pairing mode.")
            print(
                "💡 Tip: ELM327 devices usually have a blinking blue light when in pairing mode.")
            return False

        print("✅ Found ELM327 devices:")
        for i, device in enumerate(elm_devices):
            print(f"{i + 1}. {device}")

        # Let user select device
        if len(elm_devices) > 1:
            choice = input("Enter the number of your device: ")
            try:
                selected_device = elm_devices[int(choice) - 1]
            except BaseException:
                selected_device = elm_devices[0]
        else:
            selected_device = elm_devices[0]

        # Extract MAC address (format: Device MAC_Address Name)
        mac_address = selected_device.split()[1]
        print(f"📱 Selected device MAC: {mac_address}")

        # Pair with the device
        print("🔐 Pairing with device (using PIN 1234)...")
        pair_process = subprocess.Popen(['bluetoothctl', 'pair', mac_address],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        text=True)
        stdout, stderr = pair_process.communicate()

        if "Pairing successful" in stdout or "Failed" not in stdout:
            print("✅ Pairing successful!")

            # Trust the device
            print("🤝 Trusting device...")
            trust_process = subprocess.Popen(['bluetoothctl', 'trust', mac_address],
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                             text=True)
            trust_process.communicate()

            # Connect to the device
            print("🔗 Connecting to device...")
            connect_process = subprocess.Popen(['bluetoothctl', 'connect', mac_address],
                                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                               text=True)
            connect_process.communicate()

            # Bind RFCOMM channel
            print("📡 Binding RFCOMM channel...")
            bind_process = subprocess.Popen(['sudo', 'rfcomm', 'bind', '/dev/rfcomm0', mac_address, '1'],
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                            text=True)
            bind_process.communicate()

            print("🎉 Bluetooth setup complete!")
            print(f"📋 Device bound to: /dev/rfcomm0")
            print("\n💡 You may need to run this script with sudo for full functionality.")
            return True
        else:
            print("❌ Pairing failed. Please try again.")
            print(f"Error: {stderr}")
            return False

    except Exception as e:
        print(f"❌ Error during pairing process: {e}")
        return False


if __name__ == "__main__":
    if pair_elm327_device():
        print("\n✨ Pairing successful! You can now use your ELM327 device with DiagAutoClinicOS.")
    else:
        print("\n❌ Pairing failed. Please check:")
        print("1. Your ELM327 is in pairing mode (blinking blue light)")
        print("2. Bluetooth is enabled on your computer")
        print("3. You have permission to access Bluetooth devices")
        sys.exit(1)
