#!/usr/bin/env python3
# test_elm327.py

import serial
import time


def test_elm327_connection():
    try:
        print("Testing ELM327 connection on /dev/rfcomm0...")

        # Try to connect to the Bluetooth device
        ser = serial.Serial('/dev/rfcomm0', 38400, timeout=2)

        # Send ATZ command (reset)
        ser.write(b'ATZ\r\n')
        time.sleep(1)
        response = ser.read_all().decode().strip()
        print(f"Response to ATZ: {response}")

        # Send ATI command (get device info)
        ser.write(b'ATI\r\n')
        time.sleep(1)
        response = ser.read_all().decode().strip()
        print(f"Response to ATI: {response}")

        # Check if it's an ELM327 device
        if 'ELM327' in response.upper():
            print("✓ ELM327 device detected successfully!")
            return True
        else:
            print("⚠ Device responded but doesn't appear to be ELM327")
            return False

    except Exception as e:
        print(f"Error connecting to ELM327: {e}")
        return False
    finally:
        if 'ser' in locals():
            ser.close()


if __name__ == "__main__":
    test_elm327_connection()
