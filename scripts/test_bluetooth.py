#!/usr/bin/env python3

import serial
import time


def test_bluetooth_port(port):
    try:
        print(f"Testing {port}...")
        ser = serial.Serial(port, 38400, timeout=2)
        ser.write(b'ATZ\r\n')
        time.sleep(2)
        response = ser.read_all().decode().strip()
        ser.close()
        print(f"Response from {port}: {response}")
        return 'ELM327' in response.upper()
    except Exception as e:
        print(f"Error testing {port}: {e}")
        return False


# Test common Bluetooth ports
ports = ['/dev/rfcomm0', '/dev/rfcomm1', '/dev/rfcomm2']
for port in ports:
    if test_bluetooth_port(port):
        print(f"ELM327 found on {port}")
        break
else:
    print("No ELM327 devices found on Bluetooth ports")
