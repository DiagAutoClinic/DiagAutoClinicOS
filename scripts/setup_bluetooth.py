#!/usr/bin/env python3

import subprocess
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_bluetooth_elm327():
    """Setup Bluetooth connection for ELM327 device"""
    try:
        # Check if Bluetooth is available
        result = subprocess.run(
            ['which', 'bluetoothctl'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(
                "bluetoothctl not found. Please install bluez package.")
            return False

        logger.info("Setting up Bluetooth ELM327 connection...")

        # This is a simplified approach - in practice, you might need to
        # pair and trust the device first via bluetoothctl

        # Bind RFCOMM channel (replace XX:XX:XX:XX:XX:XX with your device's MAC
        # address)
        mac_address = input(
            "Enter your ELM327 Bluetooth MAC address (XX:XX:XX:XX:XX:XX): ")

        if mac_address:
            result = subprocess.run(['sudo', 'rfcomm', 'bind', '/dev/rfcomm0', mac_address, '1'],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Bluetooth ELM327 bound to /dev/rfcomm0")
                return True
            else:
                logger.error(f"Failed to bind Bluetooth device: {result.stderr}")

        return False

    except Exception as e:
        logger.error(f"Bluetooth setup failed: {e}")
        return False


if __name__ == "__main__":
    setup_bluetooth_elm327()
