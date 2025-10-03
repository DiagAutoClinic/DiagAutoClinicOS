import time
import random

class DeviceHandler:
    def __init__(self, mock_mode=True):
        self.mock_mode = mock_mode
        self.is_connected = False  # Added this missing attribute
        self.current_protocol = None

    def connect(self, protocol="CAN_11BIT_500K"):
        """Connect to the J2534 device or use mock mode"""
        if self.mock_mode:
            print("[MOCK] Connected to vehicle interface")
            self.is_connected = True
            self.current_protocol = protocol
            return True
        else:
            # REAL J2534 device connection will go here
            try:
                # This will eventually use pyJ2534 or similar library
                print(f"[REAL] Connecting via J2534 using {protocol}...")
                time.sleep(2)  # Simulate connection delay
                self.is_connected = True
                self.current_protocol = protocol
                return True
            except Exception as e:
                print(f"[ERROR] Connection failed: {e}")
                return False

    def disconnect(self):
        self.is_connected = False
        self.current_protocol = None
        print("Disconnected from vehicle interface")

    def scan_dtcs(self):
        """Scan for Diagnostic Trouble Codes"""
        if not self.is_connected:
            return []

        if self.mock_mode:
            # Return some common mock DTCs
            time.sleep(1)  # Simulate scan time
            return [('P0300', 'Misfire Detected'), ('P0420', 'Catalyst Efficiency Below Threshold')]
        else:
            # Real J2534 DTC scan will go here
            pass

    def clear_dtcs(self):
        """Clear all DTCs"""
        if not self.is_connected:
            return False

        if self.mock_mode:
            print("[MOCK] DTCs cleared successfully")
            return True
        else:
            # Real J2534 DTC clear will go here
            pass

    def get_live_data(self, pid):
        """Get live data from ECU"""
        if not self.is_connected:
            return 0

        if self.mock_mode:
            # Simulate live data based on PID
            mock_data = {
                'rpm': random.randint(650, 3500),
                'speed': random.randint(0, 120),
                'coolant_temp': random.randint(80, 105),
                'throttle': random.randint(5, 95),
            }
            return mock_data.get(pid.lower(), 0)
        else:
            # Real J2534 data request will go here
            pass

    def read_ecu_data(self, address, length):
        """Read data from ECU memory"""
        if self.mock_mode:
            return f"[MOCK] Read {length} bytes from address 0x{address:08X}"
        else:
            # Real J2534 ECU read will go here
            pass

    def write_ecu_data(self, address, data):
        """Write data to ECU memory"""
        if self.mock_mode:
            return f"[MOCK] Wrote {len(data)} bytes to address 0x{address:08X}"
        else:
            # Real J2534 ECU write will go here
            pass

# Test
if __name__ == "__main__":
    device = DeviceHandler(mock_mode=True)
    device.connect()
    print("DTCs:", device.scan_dtcs())
    print("RPM:", device.get_live_data('rpm'))
    device.disconnect()
