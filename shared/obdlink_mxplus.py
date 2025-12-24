#!/usr/bin/env python3
"""
OBDLink MX+ Device Handler
Bluetooth-based CAN bus sniffer for automotive diagnostics
"""

import logging
import time
import threading
from typing import Optional, List, Dict, Callable, Tuple
from enum import Enum
from dataclasses import dataclass
from collections import deque
import re

logger = logging.getLogger(__name__)


class OBDLinkProtocol(Enum):
    """OBDLink MX+ Protocol Types"""
    AUTO = "AUTO"
    ISO15765_11BIT = "ISO15765_11BIT"  # Standard OBD-II CAN
    ISO15765_29BIT = "ISO15765_29BIT"  # Extended CAN
    J1850_PWM = "J1850_PWM"
    J1850_VPW = "J1850_VPW"
    ISO9141 = "ISO9141"
    ISO14230 = "ISO14230"


@dataclass
class CANMessage:
    """CAN Bus Message Structure"""
    timestamp: float
    arbitration_id: str
    data: str
    raw_message: str
    
    def __str__(self):
        return f"{self.arbitration_id} {self.data}"
    
    @classmethod
    def parse_raw_message(cls, raw_msg: str) -> 'CANMessage':
        """Parse raw CAN message from OBDLink MX+"""
        try:
            # OBDLink MX+ format: "7E8 06 41 0C 0F A0 00 00"
            parts = raw_msg.strip().split()
            if len(parts) >= 2:
                arbitration_id = parts[0]
                data = " ".join(parts[1:])
                return cls(
                    timestamp=time.time(),
                    arbitration_id=arbitration_id,
                    data=data,
                    raw_message=raw_msg
                )
        except Exception as e:
            logger.debug(f"Failed to parse CAN message: {raw_msg} - {e}")
        return cls(time.time(), "", "", raw_msg)


class OBDLinkMXPlus:
    """OBDLink MX+ CAN Bus Sniffer with Bluetooth Support"""
    
    def __init__(self, mock_mode: bool = False, device_name: str = "OBDLink MX+"):
        self.mock_mode = mock_mode
        self.device_name = device_name
        self.is_connected = False
        self.is_monitoring = False
        self.current_protocol = OBDLinkProtocol.AUTO
        
        # Connection parameters
        self.bluetooth_address = None
        self.rfcomm_socket = None
        self.serial_port = None
        
        # CAN bus monitoring
        self.message_buffer = deque(maxlen=1000)
        self.callbacks = []
        self.monitor_thread = None
        self._stop_monitor = threading.Event()
        
        # Vehicle configuration (GM/Chevrolet, Ford, and BMW focus)
        self.vehicle_profiles = {
            'chevrolet_cruze_2014': {
                'name': 'Chevrolet Cruze 2014',
                'vin': 'KL1JF6889EK617029',
                'protocol': OBDLinkProtocol.ISO15765_11BIT,
                'arbitration_ids': {
                    'engine': ['7E8', '7E0', '7E1'],  # ECM primary/secondary
                    'transmission': ['7E2', '7EA'],    # TCM
                    'brakes': ['7B0', '7B1'],          # ABS/EBCM
                    'steering': ['7B2', '7B3'],        # Power Steering
                    'body': ['7A0', '7A1'],            # BCM
                    'instrument': ['7C0', '7C1'],      # IPC
                    'climate': ['7D0', '7D1'],         # HVAC
                    'safety': ['7E0', '7E1']           # Airbag/SDM
                }
            },
            'bmw_e90_2005': {
                'name': 'BMW E90 320d 2005',
                'vin': 'WBAVC36020NC55225',
                'odo': '255319km',
                'engine': '2.0L Diesel (M47)',
                'protocol': OBDLinkProtocol.ISO15765_29BIT,
                'arbitration_ids': {
                    'engine': ['6F1', '6F9'],          # DDE/DME (Diesel Engine Management)
                    'transmission': ['6D1', '6D9'],    # EGS (Transmission Control)
                    'brakes': ['6B1', '6B9'],          # ABS (Anti-lock Braking System)
                    'safety': ['6A1', '6A9'],          # Airbag/SRS (Safety Restraint System)
                    'instrument': ['6E1', '6E9'],      # KOMBI (Instrument Cluster)
                    'body': ['6C1', '6C9'],            # ZKE (Central Body Electronics)
                    'climate': ['6H1', '6H9'],         # IHKA (Climate Control System)
                    'parking': ['6E5', '6E6']          # PDC (Parking Distance Control)
                }
            },
            'generic_bmw': {
                'name': 'Generic BMW',
                'protocol': OBDLinkProtocol.ISO15765_29BIT,
                'arbitration_ids': {
                    'engine': ['6F1', '6F9'],          # DME/DDE
                    'transmission': ['6D1', '6D9'],    # EGS
                    'brakes': ['6B1', '6B9'],          # ABS
                    'safety': ['6A1', '6A9'],          # Airbag
                    'instrument': ['6E1', '6E9'],      # KOMBI
                    'body': ['6C1', '6C9'],            # ZKE
                    'climate': ['6H1', '6H9']          # IHKA
                }
            },
            'generic_gm': {
                'name': 'Generic GM/Chevrolet',
                'protocol': OBDLinkProtocol.ISO15765_11BIT,
                'arbitration_ids': {
                    'engine': ['7E8', '7E0'],
                    'transmission': ['7E2', '7EA'],
                    'brakes': ['7B0', '7B1'],
                    'steering': ['7B2', '7B3'],
                    'body': ['7A0', '7A1'],
                    'instrument': ['7C0', '7C1'],
                    'climate': ['7D0', '7D1']
                }
            },
            'ford_ranger_2014': {
                'protocol': OBDLinkProtocol.ISO15765_11BIT,
                'arbitration_ids': {
                    'engine': ['7E8', '7E0'],
                    'transmission': ['7E1', '7E9'],
                    'brakes': ['730', '735'],
                    'steering': ['740', '745'],
                    'body': ['720', '725'],
                    'instrument': ['720', '721']
                }
            },
            'ford_figo': {
                'protocol': OBDLinkProtocol.ISO15765_11BIT,
                'arbitration_ids': {
                    'engine': ['7E8', '7E0'],
                    'transmission': ['7E1', '7E9'],
                    'brakes': ['730', '735'],
                    'steering': ['740', '745'],
                    'body': ['720', '725'],
                    'instrument': ['720', '721'],
                    'climate': ['730', '731']
                }
            },
            'generic_ford': {
                'protocol': OBDLinkProtocol.ISO15765_11BIT,
                'arbitration_ids': {
                    'engine': ['7E8', '7E0'],
                    'transmission': ['7E1', '7E9'],
                    'brakes': ['730', '735'],
                    'steering': ['740', '745'],
                    'body': ['720', '725']
                }
            }
        }
        
        self.current_vehicle_profile = None
        
        # Mock message generation for testing
        if mock_mode:
            self._setup_mock_messages()
    
    def _setup_mock_messages(self):
        """Setup mock CAN messages for testing"""
        self.mock_messages = [
            "7E8 06 41 0C 0F A0 00 00",  # Engine RPM
            "7E8 04 41 0D 32",           # Vehicle speed
            "7E8 03 41 05 80",           # Coolant temperature
            "7E8 04 41 2F 20 10",        # Fuel level input
            "7E0 02 3E 00",              # Tester present response
            "7E8 03 7F 01 78",           # Pending response
            "720 08 44 50 52 45 53 53 20 55",  # Body control message
            "740 06 35 53 54 45 45 52 20",     # Steering angle message
        ]
        self.mock_message_index = 0
    
    def discover_devices(self, timeout: int = 6) -> List[str]:
        """Discover OBDLink MX+ devices via Bluetooth with timeout protection"""
        if self.mock_mode:
            return ["OBDLink-MXPlus-001", "OBDLink-MXPlus-002"]
        
        try:
            # Import required modules
            import bluetooth
            import threading
            import time
            from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
            
            # Use thread pool for timeout protection
            def bluetooth_discovery():
                try:
                    # Use shorter duration to avoid hanging
                    duration = min(timeout, 6)  # Max 6 seconds
                    devices = bluetooth.discover_devices(duration=duration, lookup_names=True, flush_cache=True)
                    obdlink_devices = []
                    
                    for addr, name in devices:
                        if "OBD" in name.upper() or "OBDLink" in name.upper():
                            obdlink_devices.append(f"{name} ({addr})")
                    
                    return obdlink_devices
                except Exception as e:
                    logger.debug(f"Bluetooth discovery error: {e}")
                    return []
            
            # Run discovery with timeout
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(bluetooth_discovery)
                try:
                    return future.result(timeout=timeout)
                except FutureTimeoutError:
                    logger.warning(f"Bluetooth discovery timed out after {timeout}s")
                    return []
                    
        except ImportError:
            logger.warning("Bluetooth module not available - mock mode only")
            return []
        except Exception as e:
            logger.error(f"Bluetooth discovery failed: {e}")
            return []
    
    def connect_bluetooth(self, device_address: str) -> bool:
        """Connect to OBDLink MX+ via Bluetooth"""
        if self.mock_mode:
            self.bluetooth_address = device_address
            self.is_connected = True
            logger.info(f"[MOCK] Connected to {device_address}")
            return True
        
        try:
            import bluetooth
            
            # Extract MAC address from device string "Name (MAC)"
            mac_match = re.search(r'\(([0-9A-Fa-f:]{17})\)', device_address)
            if not mac_match:
                logger.error("Invalid device format - expected 'Name (MAC)'")
                return False
            
            mac_address = mac_match.group(1)
            logger.info(f"Connecting to OBDLink MX+ at {mac_address}")
            
            # Connect to RFCOMM channel (typically channel 1 for OBDLink)
            self.rfcomm_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.rfcomm_socket.connect((mac_address, 1))
            
            self.bluetooth_address = mac_address
            self.is_connected = True
            
            # Initialize device
            return self._initialize_device()
            
        except ImportError:
            logger.error("Bluetooth module not available")
            return False
        except Exception as e:
            logger.error(f"Bluetooth connection failed: {e}")
            return False
    
    def connect_serial(self, port: str, baudrate: int = 38400) -> bool:
        """Connect to OBDLink MX+ via serial port (USB)"""
        if self.mock_mode:
            self.serial_port = port
            self.is_connected = True
            logger.info(f"[MOCK] Connected to {port}")
            return True

        logger.info(f"Attempting to connect to OBDLink MX+ on {port} at {baudrate} baud")
        try:
            import serial

            self.serial_port = serial.Serial(port, baudrate, timeout=2)
            logger.info(f"Serial port {port} opened successfully")

            # Initialize device
            init_success = self._initialize_device()
            if init_success:
                logger.info(f"Successfully connected and initialized OBDLink MX+ on {port}")
                self.is_connected = True
            else:
                logger.error(f"Device initialization failed on {port}")
                self.serial_port.close()
                self.serial_port = None
            return init_success

        except ImportError:
            logger.error("pyserial module not available")
            return False
        except Exception as e:
            logger.error(f"Serial connection failed on {port}: {e}")
            return False
    
    def _initialize_device(self) -> bool:
        """Initialize OBDLink MX+ device"""
        if self.mock_mode:
            logger.info("[MOCK] Device initialized")
            return True

        logger.info("Starting OBDLink MX+ device initialization")
        try:
            # Send initialization commands
            commands = [
                (b'ATZ\r\n', 'Reset device'),
                (b'ATE0\r\n', 'Disable echo'),
                (b'ATL0\r\n', 'Linefeeds off'),
                (b'ATH1\r\n', 'Headers on'),
            ]

            for cmd, desc in commands:
                logger.debug(f"Sending command: {cmd.decode().strip()} ({desc})")
                success = self._send_command(cmd)
                if not success:
                    logger.error(f"Failed to send command: {cmd.decode().strip()}")
                    return False
                time.sleep(0.5)

            # Check device response
            logger.debug("Reading initialization response")
            response = self._read_response()
            logger.info(f"Device response: {response.strip()}")
            if 'ELM327' in response.upper() or 'OBDLINK' in response.upper():
                logger.info("OBDLink MX+ initialized successfully")
                return True
            else:
                logger.warning(f"Device initialization response unclear: '{response.strip()}'")
                return True  # Continue anyway

        except Exception as e:
            logger.error(f"Device initialization failed: {e}")
            return False
    
    def set_vehicle_profile(self, profile_name: str) -> bool:
        """Set vehicle-specific configuration"""
        if profile_name not in self.vehicle_profiles:
            logger.warning(f"Unknown vehicle profile: {profile_name}")
            return False
        
        self.current_vehicle_profile = self.vehicle_profiles[profile_name]
        self.current_protocol = self.current_vehicle_profile['protocol']
        
        logger.info(f"Vehicle profile set to: {profile_name}")
        return True
    
    def configure_can_sniffing(self, protocol: OBDLinkProtocol = OBDLinkProtocol.AUTO) -> bool:
        """Configure OBDLink MX+ for CAN bus sniffing"""
        if not self.is_connected:
            logger.error("Device not connected")
            return False
        
        if self.mock_mode:
            logger.info("[MOCK] CAN sniffing configured")
            return True
        
        try:
            # Configure protocol based on settings
            protocol_commands = {
                OBDLinkProtocol.ISO15765_11BIT: b'ATSP6\r\n',  # ISO 15765-4 CAN (11 bit ID)
                OBDLinkProtocol.ISO15765_29BIT: b'ATSP7\r\n',  # ISO 15765-4 CAN (29 bit ID)
                OBDLinkProtocol.AUTO: b'ATSP0\r\n',             # Auto detect
            }
            
            # Send configuration commands
            commands = [
                protocol_commands.get(protocol, b'ATSP6\r\n'),  # Default to 11-bit CAN
                b'ATCAF0\r\n',  # CAN auto formatting off
                b'ATH0\r\n',    # Headers off for cleaner output
                b'ATST64\r\n',  # Set timeout to 100ms
                b'ATAT2\r\n',   # Adaptive timing on
            ]
            
            for cmd in commands:
                self._send_command(cmd)
                time.sleep(0.2)
            
            self.current_protocol = protocol
            logger.info(f"CAN sniffing configured for {protocol.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure CAN sniffing: {e}")
            return False
    
    def start_monitoring(self) -> bool:
        """Start continuous CAN bus monitoring"""
        if not self.is_connected:
            logger.error("Device not connected")
            return False
        
        if self.mock_mode:
            logger.info("[MOCK] CAN monitoring started")
            self.is_monitoring = True
            self._start_mock_monitoring()
            return True
        
        try:
            # Start monitor mode
            self._send_command(b'ATMA\r\n')
            
            self.is_monitoring = True
            self._stop_monitor.clear()
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self._monitor_can_bus, daemon=True)
            self.monitor_thread.start()
            
            logger.info("CAN bus monitoring started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            return False
    
    def _start_mock_monitoring(self):
        """Start mock CAN monitoring in background thread"""
        def mock_monitor():
            while self.is_monitoring and not self._stop_monitor.is_set():
                if self.mock_message_index >= len(self.mock_messages):
                    self.mock_message_index = 0
                
                message = self.mock_messages[self.mock_message_index]
                can_msg = CANMessage.parse_raw_message(message)
                
                if can_msg.arbitration_id:  # Valid message
                    self.message_buffer.append(can_msg)
                    
                    # Notify callbacks
                    for callback in self.callbacks:
                        try:
                            callback(can_msg)
                        except Exception as e:
                            logger.debug(f"Callback error: {e}")
                
                self.mock_message_index += 1
                time.sleep(0.1)  # 10Hz message rate
        
        self.monitor_thread = threading.Thread(target=mock_monitor, daemon=True)
        self.monitor_thread.start()
    
    def _monitor_can_bus(self):
        """Background thread for CAN bus monitoring"""
        while self.is_monitoring and not self._stop_monitor.is_set():
            try:
                if self.serial_port and self.serial_port.in_waiting:
                    data = self.serial_port.readline().decode(errors='ignore').strip()
                    if data:
                        can_msg = CANMessage.parse_raw_message(data)
                        if can_msg.arbitration_id:  # Valid message
                            self.message_buffer.append(can_msg)
                            
                            # Notify callbacks
                            for callback in self.callbacks:
                                try:
                                    callback(can_msg)
                                except Exception as e:
                                    logger.debug(f"Callback error: {e}")
                
                time.sleep(0.01)  # 100Hz polling
                
            except Exception as e:
                logger.error(f"CAN monitoring error: {e}")
                time.sleep(0.1)
    
    def stop_monitoring(self) -> bool:
        """Stop CAN bus monitoring"""
        if not self.is_monitoring:
            return True
        
        if self.mock_mode:
            self.is_monitoring = False
            logger.info("[MOCK] CAN monitoring stopped")
            return True
        
        try:
            # Stop monitoring
            self._send_command(b'\r\n')  # Send any character to stop
            time.sleep(0.1)
            
            self.is_monitoring = False
            self._stop_monitor.set()
            
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=2)
            
            logger.info("CAN bus monitoring stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")
            return False
    
    def read_messages(self, count: int = 10, timeout_ms: int = 1000) -> List[CANMessage]:
        """Read captured CAN messages"""
        messages = []
        start_time = time.time()
        
        # Collect existing messages
        while self.message_buffer and len(messages) < count:
            try:
                messages.append(self.message_buffer.popleft())
            except IndexError:
                break
        
        # Wait for more messages if needed
        while len(messages) < count and (time.time() - start_time) * 1000 < timeout_ms:
            if self.message_buffer:
                try:
                    messages.append(self.message_buffer.popleft())
                except IndexError:
                    break
            time.sleep(0.01)
        
        return messages
    
    def get_message_statistics(self) -> Dict:
        """Get statistics about captured CAN messages"""
        if not self.message_buffer:
            return {'total_messages': 0}
        
        # Analyze arbitration IDs
        id_counts = {}
        for msg in self.message_buffer:
            id_counts[msg.arbitration_id] = id_counts.get(msg.arbitration_id, 0) + 1
        
        # Categorize messages if vehicle profile is set
        categories = {}
        if self.current_vehicle_profile:
            for category, patterns in self.current_vehicle_profile['arbitration_ids'].items():
                categories[category] = sum(
                    id_counts.get(pattern, 0) for pattern in patterns
                )
        
        return {
            'total_messages': len(self.message_buffer),
            'unique_ids': len(id_counts),
            'arbitration_id_counts': dict(sorted(id_counts.items(), key=lambda x: x[1], reverse=True)),
            'categories': categories,
            'recent_messages': len([msg for msg in self.message_buffer if time.time() - msg.timestamp < 10])
        }
    
    def add_message_callback(self, callback: Callable[[CANMessage], None]):
        """Add callback for real-time message processing"""
        self.callbacks.append(callback)
    
    def remove_message_callback(self, callback: Callable[[CANMessage], None]):
        """Remove message callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def clear_buffer(self):
        """Clear the message buffer"""
        self.message_buffer.clear()
        logger.info("CAN message buffer cleared")
    
    def disconnect(self):
        """Disconnect from OBDLink MX+ device"""
        self.stop_monitoring()
        
        if self.mock_mode:
            self.is_connected = False
            logger.info("[MOCK] Disconnected from OBDLink MX+")
            return
        
        try:
            if self.rfcomm_socket:
                self.rfcomm_socket.close()
                self.rfcomm_socket = None
            
            if self.serial_port:
                self.serial_port.close()
                self.serial_port = None
            
            self.is_connected = False
            logger.info("Disconnected from OBDLink MX+")
            
        except Exception as e:
            logger.error(f"Error during disconnection: {e}")
    
    def _send_command(self, command: bytes) -> bool:
        """Send command to device"""
        try:
            if self.serial_port:
                self.serial_port.write(command)
                self.serial_port.flush()
                return True
            elif self.rfcomm_socket:
                self.rfcomm_socket.send(command)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            return False
    
    def _read_response(self, timeout: float = 2.0) -> str:
        """Read response from device"""
        try:
            if self.serial_port:
                start_time = time.time()
                response = ""
                logger.debug(f"Reading response with timeout {timeout}s")
                while (time.time() - start_time) < timeout:
                    if self.serial_port.in_waiting:
                        data = self.serial_port.readline().decode(errors='ignore')
                        logger.debug(f"Read data: '{data.strip()}'")
                        response += data
                        if '>' in data:  # Prompt indicates end of response
                            logger.debug("End of response detected (prompt '>' found)")
                            break
                    else:
                        time.sleep(0.01)  # Small delay to avoid busy waiting
                logger.debug(f"Final response: '{response.strip()}'")
                return response
            elif self.rfcomm_socket:
                # For Bluetooth, would need to implement proper read logic
                logger.warning("Bluetooth response reading not implemented")
                return ""
            logger.warning("No active connection for reading response")
            return ""
        except Exception as e:
            logger.error(f"Failed to read response: {e}")
            return ""


def create_obdlink_mxplus(mock_mode: bool = True) -> OBDLinkMXPlus:
    """Factory function to create OBDLink MX+ instance"""
    return OBDLinkMXPlus(mock_mode=mock_mode)


if __name__ == "__main__":
    # Test the OBDLink MX+ implementation
    logging.basicConfig(level=logging.INFO)
    
    # Test mock mode
    obdlink = create_obdlink_mxplus(mock_mode=True)
    
    print("OBDLink MX+ Test")
    print("=" * 30)
    
    # Test connection
    if obdlink.connect_serial("COM1"):  # Mock connection
        print("✓ Connected to OBDLink MX+")
        
        # Set vehicle profile
        obdlink.set_vehicle_profile("ford_ranger_2014")
        
        # Configure CAN sniffing
        obdlink.configure_can_sniffing()
        
        # Start monitoring
        obdlink.start_monitoring()
        
        # Collect some messages
        time.sleep(2)
        messages = obdlink.read_messages(5)
        
        print(f"Captured {len(messages)} messages:")
        for msg in messages[:5]:
            print(f"  {msg}")
        
        # Get statistics
        stats = obdlink.get_message_statistics()
        print(f"\nStatistics: {stats}")
        
        # Stop and disconnect
        obdlink.stop_monitoring()
        obdlink.disconnect()
        print("✓ Test completed")
    
    # Test device discovery (mock)
    print("\nDevice Discovery Test:")
    devices = obdlink.discover_devices()
    for device in devices:
        print(f"  Found: {device}")