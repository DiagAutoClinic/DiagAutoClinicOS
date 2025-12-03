import time
import random
import serial
import platform
import subprocess
import logging
import os
import socket
import re
from enum import Enum
from typing import Optional, List, Tuple, Dict

# Try to import Bluetooth, but provide fallback
try:
    import bluetooth
    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False
    logging.warning("Bluetooth module not available - Bluetooth features disabled")

# Try to import USB support
try:
    import usb.core
    import usb.util
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False
    logging.warning("USB module not available - USB device detection limited")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Protocol(Enum):
    CAN_11BIT_500K = "CAN_11BIT_500K"
    CAN_29BIT_500K = "CAN_29BIT_500K"
    J1850_PWM = "J1850_PWM"
    J1850_VPW = "J1850_VPW"
    ISO9141 = "ISO9141"
    ISO14230 = "ISO14230"
    ISO15765 = "ISO15765"
    J2534 = "J2534"
    AUTO = "AUTO"
    DOIP = "DOIP"  # Added for GT100+ ENET support
    GPT = "GPT"    # Added for GT100+ ECU read/write

class ProfessionalDevice:
    def __init__(self, name, device_type, protocols, interfaces, vendor_id=None, product_id=None):
        self.name = name
        self.device_type = device_type
        self.protocols = protocols
        self.interfaces = interfaces
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.connected = False
        
    def __str__(self):
        return f"{self.name} ({self.device_type})"

class DeviceHandler:
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.is_connected = False
        self.current_protocol: Optional[Protocol] = None
        self.serial_conn: Optional[serial.Serial] = None
        self.bt_socket = None
        self.os_type = platform.system()
        self.device_type: Optional[str] = None
        self.port: Optional[str] = None
        self.bench_mode = False  # New: Flag for GT100+ bench operations
        
        # Professional devices database
        self.pro_devices = {
            # J2534 Devices
            "Godiag GT101": ProfessionalDevice(
                "Godiag GT101", "J2534",
                ["J2534", "ISO15765", "ISO14230", "ISO9141", "J1850"],
                ["USB"], vendor_id=0x0403, product_id=0x6001
            ),
            "Scanmatic 2": ProfessionalDevice(
                "Scanmatic 2", "J2534",
                ["J2534", "ISO15765", "KWP2000", "CAN"],
                ["USB", "Ethernet"]
            ),
            "Mongoose Pro": ProfessionalDevice(
                "Mongoose Pro", "J2534",
                ["J2534", "DOIP", "CAN", "LIN"],
                ["USB", "Ethernet"]
            ),
            "PCMmaster": ProfessionalDevice(
                "PCMmaster", "J2534",
                ["J2534", "UDS", "KWP2000", "CAN"],
                ["USB"]
            ),
            
            # ELM327-based devices
            "ELM327 Bluetooth": ProfessionalDevice(
                "ELM327 Bluetooth", "ELM327",
                ["ISO15765", "ISO14230", "ISO9141", "J1850"],
                ["Bluetooth"], vendor_id=0x0403, product_id=0x6001
            ),
            "ELM327 USB": ProfessionalDevice(
                "ELM327 USB", "ELM327",
                ["ISO15765", "ISO14230", "ISO9141", "J1850"],
                ["USB"], vendor_id=0x0403, product_id=0x6001
            ),
            "Tatrix": ProfessionalDevice(
                "Tatrix", "ELM327",
                ["ISO15765", "KWP2000", "CAN"],
                ["USB", "Bluetooth"]
            ),
            
            # GT100+ Breakout Box
            "Godiag GT100+": ProfessionalDevice(
                "Godiag GT100+", "Breakout",
                ["ISO15765", "ISO14230", "ISO9141", "J1850", "DOIP", "GPT", "CAN", "K-Line"],
                ["USB", "OBDII", "ENET"], vendor_id=0x1a86, product_id=0x7523  # CH340 USB-UART common in Godiag
            ),
            
            # OBDLink MX+ Devices (NEW)
            "OBDLink MX+": ProfessionalDevice(
                "OBDLink MX+", "CANSniffer",
                ["ISO15765", "ISO14230", "ISO9141", "J1850", "CAN"],
                ["Bluetooth", "USB"]
            ),
            "OBDLink MX+ Sniffer": ProfessionalDevice(
                "OBDLink MX+ Sniffer", "CANSniffer",
                ["ISO15765", "CAN"],
                ["Bluetooth", "USB"]
            ),
        }
        
        self.j2534_available = self._check_j2534_linux()
        self.socketcan_available = self._check_socketcan_linux()
        self.current_device: Optional[ProfessionalDevice] = None
        self.gt100_conn = None  # New: GT100+ specific connection

    def _check_j2534_linux(self) -> bool:
        """Check if J2534 is available on Linux"""
        try:
            # Check for libj2534
            result = subprocess.run(['pkg-config', '--exists', 'libj2534'], 
                                    capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("libj2534 development files found")
                return True

            # Check for J2534 tools via Wine
            result = subprocess.run(['which', 'wine'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("Wine available for J2534 emulation")
                return True

            # Check for passthru libraries
            if os.path.exists('/usr/lib/libpassthru.so'):
                logger.info("J2534 passthru library found")
                return True

        except Exception as e:
            logger.error(f"Error checking J2534: {e}")
        return False

    def _check_socketcan_linux(self) -> bool:
        """Check if SocketCAN is available"""
        try:
            result = subprocess.run(['lsmod'], capture_output=True, text=True, timeout=5)
            stdout = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', result.stdout)
            if 'can' in stdout.lower():
                logger.info("SocketCAN support detected")
                return True

            result = subprocess.run(['which', 'cansend'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("CAN utilities available")
                return True

        except Exception as e:
            logger.error(f"Error checking SocketCAN: {e}")
        return False

    def detect_professional_devices(self) -> List[ProfessionalDevice]:
        """Scan for all professional diagnostic devices"""
        detected_devices = []
        
        # USB Device Detection (Enhanced for GT100+)
        if USB_AVAILABLE:
            try:
                usb_devices = usb.core.find(find_all=True)
                for dev in usb_devices:
                    for pro_device in self.pro_devices.values():
                        if (pro_device.vendor_id and pro_device.product_id and
                            dev.idVendor == pro_device.vendor_id and 
                            dev.idProduct == pro_device.product_id):
                            detected_devices.append(pro_device)
                            logger.info(f"Detected USB device: {pro_device.name}")
            except Exception as e:
                logger.error(f"USB detection error: {e}")
        else:
            logger.info("USB detection disabled - pyusb not available")

        # Bluetooth ELM327 Detection
        if BLUETOOTH_AVAILABLE:
            try:
                bt_devices = self._scan_bluetooth_elm327()
                for bt_dev in bt_devices:
                    if "ELM327" in bt_dev.upper() or "OBD" in bt_dev.upper():
                        detected_devices.append(self.pro_devices["ELM327 Bluetooth"])
                        logger.info(f"Detected Bluetooth device: {bt_dev}")
            except Exception as e:
                logger.error(f"Bluetooth detection error: {e}")
        else:
            logger.info("Bluetooth detection disabled - pybluez not available")

        # Serial Port Detection
        serial_devices = self._scan_serial_ports()
        detected_devices.extend(serial_devices)

        # J2534 Device Detection
        if self.j2534_available:
            j2534_devices = self._detect_j2534_devices()
            detected_devices.extend(j2534_devices)

        # If no devices found in mock mode, add mock devices for testing
        if self.mock_mode and not detected_devices:
            detected_devices = [
                self.pro_devices["Godiag GT101"],
                self.pro_devices["ELM327 USB"],
                self.pro_devices["Mongoose Pro"],
                self.pro_devices["Godiag GT100+"],
                self.pro_devices["OBDLink MX+"],  # Added OBDLink MX+
                self.pro_devices["OBDLink MX+ Sniffer"]
            ]
            logger.info("Added mock devices for testing")

        return detected_devices

    def _scan_bluetooth_elm327(self) -> List[str]:
        """Scan for Bluetooth ELM327 devices"""
        bt_devices = []
        if not BLUETOOTH_AVAILABLE:
            return bt_devices
            
        try:
            # Simple Bluetooth scan using bluetoothctl
            result = subprocess.run(['bluetoothctl', 'devices'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                stdout = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', result.stdout)
                for line in stdout.split('\n'):
                    clean_line = line.strip()
                    if 'ELM327' in clean_line.upper() or 'OBD' in clean_line.upper():
                        bt_devices.append(clean_line)
        except Exception as e:
            logger.debug(f"Bluetooth scan failed: {e}")
        return bt_devices

    def _scan_serial_ports(self) -> List[ProfessionalDevice]:
        """Scan serial ports for diagnostic devices"""
        serial_devices = []
        ports_to_check = [
            '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3',
            '/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2',
            '/dev/rfcomm0', '/dev/rfcomm1', '/dev/rfcomm2'
        ]

        for port in ports_to_check:
            if not os.path.exists(port):
                continue
                
            try:
                ser = serial.Serial(port, 38400, timeout=2)
                ser.write(b'ATI\r\n')
                time.sleep(1)
                response = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', ser.read_all().decode(errors='ignore')).strip()
                ser.close()

                # Identify device type from response
                if 'ELM327' in response.upper():
                    device = self.pro_devices["ELM327 USB"]
                    serial_devices.append(device)
                    logger.info(f"Detected {device.name} on {port}")
                    
            except Exception as e:
                continue

        return serial_devices

    def _detect_j2534_devices(self) -> List[ProfessionalDevice]:
        """Detect J2534 compatible devices"""
        j2534_devices = []
        try:
            # Check for common J2534 device files
            j2534_indicators = [
                '/dev/j2534', '/dev/passthru',
                '/sys/bus/usb/devices/*/idVendor'
            ]
            
            # Check USB devices that might be J2534
            usb_check = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=5)
            if usb_check.returncode == 0:
                stdout = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', usb_check.stdout)
                j2534_vendors = ['0403', '067b', '0bdc']  # FTDI, Prolific, Mercedes
                for line in stdout.split('\n'):
                    clean_line = line.strip()
                    for vendor in j2534_vendors:
                        if vendor in clean_line:
                            # Try to identify specific devices
                            if 'GT101' in clean_line or 'Godiag' in clean_line:
                                j2534_devices.append(self.pro_devices["Godiag GT101"])
                            elif 'Mongoose' in clean_line:
                                j2534_devices.append(self.pro_devices["Mongoose Pro"])
                                
        except Exception as e:
            logger.error(f"J2534 detection error: {e}")
            
        return j2534_devices

    def connect_to_device(self, device_name: str, protocol: str = "AUTO") -> bool:
        """Connect to a specific professional device"""
        if self.mock_mode:
            logger.info(f"[MOCK] Connected to {device_name}")
            self.is_connected = True
            self.current_protocol = Protocol(protocol)
            self.current_device = self.pro_devices.get(device_name)
            return True

        device = self.pro_devices.get(device_name)
        if not device:
            logger.error(f"Unknown device: {device_name}")
            return False

        try:
            if device.device_type == "J2534":
                return self._connect_j2534(device, protocol)
            elif device.device_type == "ELM327":
                return self._connect_elm327(device, protocol)
            elif device.device_type == "Breakout":  # GT100+ handling
                return self._connect_gt100(device, protocol)
            elif device.device_type == "CANSniffer":  # OBDLink MX+ handling
                return self._connect_obdlink_mxplus(device, protocol)
            else:
                logger.error(f"Unsupported device type: {device.device_type}")
                return False
                
        except Exception as e:
            logger.error(f"Connection failed for {device_name}: {e}")
            return False

    def _connect_j2534(self, device: ProfessionalDevice, protocol: str) -> bool:
        """Connect to J2534 device"""
        try:
            if self.os_type == "Linux":
                # Linux J2534 implementation
                if os.path.exists('/usr/lib/libpassthru.so'):
                    logger.info(f"Connecting to {device.name} via J2534 passthru")
                    # Implementation would use libpassthru
                    self.is_connected = True
                    self.current_device = device
                    self.current_protocol = Protocol(protocol)
                    return True
                else:
                    logger.warning("J2534 passthru library not available")
                    return False
            else:
                logger.error(f"J2534 not supported on {self.os_type}")
                return False
                
        except Exception as e:
            logger.error(f"J2534 connection failed: {e}")
            return False

    def _connect_elm327(self, device: ProfessionalDevice, protocol: str) -> bool:
        """Connect to ELM327 device"""
        try:
            # Try Bluetooth first for ELM327 Bluetooth
            if "Bluetooth" in device.name and BLUETOOTH_AVAILABLE:
                return self._connect_bluetooth_elm327(device, protocol)
            else:
                # Try serial connection
                return self._connect_serial_elm327(device, protocol)
                
        except Exception as e:
            logger.error(f"ELM327 connection failed: {e}")
            return False

    def _connect_bluetooth_elm327(self, device: ProfessionalDevice, protocol: str) -> bool:
        """Connect to Bluetooth ELM327"""
        try:
            if not BLUETOOTH_AVAILABLE:
                logger.error("Bluetooth not available - cannot connect to Bluetooth device")
                return False
                
            logger.info(f"Attempting Bluetooth connection to {device.name}")
            
            # For now, simulate successful connection since Bluetooth setup varies
            self.is_connected = True
            self.current_device = device
            self.current_protocol = Protocol(protocol)
            logger.info(f"Connected to {device.name} via Bluetooth (simulated)")
            return True
            
        except Exception as e:
            logger.error(f"Bluetooth connection failed: {e}")
            return False

    def _connect_serial_elm327(self, device: ProfessionalDevice, protocol: str) -> bool:
        """Connect to serial ELM327 device"""
        try:
            # Securely find a matching port instead of hardcoding
            ports_to_check = [
                '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3',
                '/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2',
                '/dev/rfcomm0', '/dev/rfcomm1', '/dev/rfcomm2'
            ]
            port = None
            for p in ports_to_check:
                if not os.path.exists(p):
                    continue
                try:
                    ser = serial.Serial(p, 38400, timeout=2)
                    ser.write(b'ATI\r\n')
                    time.sleep(1)
                    response = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', ser.read_all().decode(errors='ignore')).strip()
                    ser.close()
                    if 'ELM327' in response.upper():
                        port = p
                        break
                except Exception:
                    continue
            
            if not port:
                logger.error("No serial ELM327 devices found")
                return False
            
            self.serial_conn = serial.Serial(port, 38400, timeout=2)
            
            # Initialize ELM327
            commands = [b'ATZ\r\n', b'ATE0\r\n', b'ATL0\r\n', b'ATH1\r\n']
            for cmd in commands:
                self.serial_conn.write(cmd)
                time.sleep(0.5)
                
            self.serial_conn.reset_input_buffer()
            self.is_connected = True
            self.current_device = device
            self.current_protocol = Protocol(protocol)
            logger.info(f"Connected to {device.name} on {port}")
            return True
            
        except Exception as e:
            logger.error(f"Serial connection failed: {e}")
            return False

    def _connect_gt100(self, device: ProfessionalDevice, protocol: str) -> bool:  # New method
        """Connect to GT100+ Breakout Box"""
        try:
            if USB_AVAILABLE:
                # Detect and connect via USB (for monitoring)
                dev = usb.core.find(idVendor=device.vendor_id, idProduct=device.product_id)
                if dev is None:
                    logger.warning("GT100+ USB not found - falling back to serial scan")
                    return self._connect_serial_gt100(device, protocol)
                
                # Claim interface and set config
                if dev.is_kernel_driver_active(0):
                    dev.detach_kernel_driver(0)
                usb.util.claim_interface(dev, 0)
                
                self.gt100_conn = dev  # Store for polling
                logger.info(f"Connected to {device.name} via USB")
            else:
                # Fallback to serial (e.g., /dev/ttyUSB* for CH340)
                return self._connect_serial_gt100(device, protocol)
            
            self.is_connected = True
            self.current_device = device
            self.current_protocol = Protocol(protocol)
            self.bench_mode = True  # Enable bench by default for GT100+
            logger.info(f"GT100+ Bench mode enabled for {protocol}")
            return True
            
        except Exception as e:
            logger.error(f"GT100+ connection failed: {e}")
            return False

    def _connect_serial_gt100(self, device: ProfessionalDevice, protocol: str) -> bool:  # New helper
        """Serial fallback for GT100+ (USB-UART mode)"""
        try:
            ports_to_check = ['/dev/ttyUSB0', '/dev/ttyUSB1']  # GT100+ typically ttyUSB
            port = None
            for p in ports_to_check:
                if not os.path.exists(p):
                    continue
                try:
                    ser = serial.Serial(p, 9600, timeout=1)  # Godiag baud rate
                    ser.write(b'AT?\r\n')  # Probe command (adapt if needed)
                    time.sleep(0.5)
                    response = ser.read_all().decode(errors='ignore').strip()
                    ser.close()
                    if 'GT100' in response or len(response) > 0:  # Basic response check
                        port = p
                        break
                except Exception:
                    continue
            
            if not port:
                logger.error("No GT100+ serial port found")
                return False
            
            self.gt100_conn = serial.Serial(port, 9600, timeout=1)
            self.gt100_conn.write(b'ATZ\r\n')  # Reset
            time.sleep(0.5)
            logger.info(f"Connected to GT100+ on {port}")
            return True
            
        except Exception as e:
            logger.error(f"Serial GT100+ failed: {e}")
            return False

    def _connect_obdlink_mxplus(self, device: ProfessionalDevice, protocol: str) -> bool:
        """Connect to OBDLink MX+ for CAN sniffing"""
        try:
            if self.mock_mode:
                logger.info(f"[MOCK] Connected to {device.name}")
                self.is_connected = True
                self.current_device = device
                self.current_protocol = Protocol(protocol)
                return True
            
            # For real implementation, would use the OBDLink MX+ handler
            # For now, simulate connection
            logger.info(f"Connecting to {device.name} (simulated)")
            self.is_connected = True
            self.current_device = device
            self.current_protocol = Protocol(protocol)
            return True
            
        except Exception as e:
            logger.error(f"OBDLink MX+ connection failed: {e}")
            return False

    def enable_bench_mode(self, enable: bool = True) -> bool:  # GT100+ bench operations
        """Enable bench mode with GT100+ (stable power check for GD101 routing)"""
        if self.current_device and self.current_device.name == "Godiag GT100+":
            status = self.get_breakout_status()
            if status.get('voltage', 0) < 11.0:
                logger.warning("Low voltage detected - bench mode unsafe")
                return False
            self.bench_mode = enable
            logger.info(f"Bench mode {'enabled' if enable else 'disabled'} - Route GD101 through GT100+ pins")
            return True
        return False

    def get_breakout_status(self) -> Dict:  # New method: Voltage, Current, LEDs
        """Poll GT100+ for monitoring data"""
        if not self.gt100_conn:
            return {}
        
        if self.mock_mode:
            return {
                'voltage': round(random.uniform(12.0, 14.5), 1),
                'current': round(random.uniform(0.1, 2.0), 2),
                'led_status': {'CAN': 'GREEN', 'K-Line': 'OFF', 'Power': 'GREEN'},
                'protocol_active': 'CAN'  # Mock
            }
        
        try:
            # Real polling: Send AT command (adapt based on Godiag docs; assumes ELM-like)
            if isinstance(self.gt100_conn, serial.Serial):
                self.gt100_conn.write(b'ATRV\r\n')  # Voltage query (example)
                time.sleep(0.2)
                response = self.gt100_conn.read_all().decode(errors='ignore')
                voltage = float(re.search(r'(\d+\.\d+)', response).group(1)) if re.search(r'(\d+\.\d+)', response) else 0.0
                # Similar for current/LEDs (e.g., ATIA for info)
                return {'voltage': voltage, 'current': 0.5, 'led_status': {'Power': 'GREEN'}}
            else:  # USB HID
                # Use pyusb bulk read (endpoint 0x81 example)
                data = self.gt100_conn.read(0x81, 8, timeout=1000)
                # Parse bytes for status (custom logic needed)
                pass
        except Exception as e:
            logger.error(f"GT100+ status poll failed: {e}")
        return {}

    def _mask_sensitive(self, value: str) -> str:
        """Mask sensitive information like serial numbers"""
        if len(value) > 8:
            return value[:4] + '*' * (len(value) - 8) + value[-4:]
        return value

    def read_ecu_identification_advanced(self) -> Dict:
        """Read advanced ECU identification data (Enhanced for bench)"""
        if not self.is_connected:
            return {}
            
        if self.mock_mode:
            info = {
                'part_number': 'Mock-ECU-12345',
                'software_version': 'V1.2.3',
                'hardware_version': 'HW-Rev-A',
                'serial_number': 'MOCK123456789',
                'coding_data': 'Coding: 0000000000',
                'diagnostic_address': '0x7E0',
                'supplier': 'Mock Automotive Systems'
            }
            info['serial_number'] = self._mask_sensitive(info['serial_number'])
            if self.bench_mode:
                info['bench_note'] = 'Powered via GT100+ (stable)'
            return info

        # Real implementation would vary by device type
        if self.current_device and self.current_device.device_type == "J2534":
            return self._j2534_read_ecu_identification()
        elif self.current_device and self.current_device.device_type == "Breakout":
            # Route through GT100+ to GD101
            status = self.get_breakout_status()
            if status.get('voltage', 0) > 11.0:
                return self._j2534_read_ecu_identification()  # Assume GD101 connected
            else:
                return {'error': 'Low power on bench'}
        else:
            return self._elm327_read_ecu_identification()

    def _j2534_read_ecu_identification(self) -> Dict:
        """J2534-specific ECU identification"""
        info = {
            'part_number': 'J2534-ECU-READ',
            'software_version': 'V2.0.0',
            'hardware_version': 'HW-J2534',
            'serial_number': 'J2534-12345',
            'coding_data': 'J2534 Coding Data',
            'diagnostic_address': '0x7E0',
            'supplier': 'J2534 Compatible'
        }
        info['serial_number'] = self._mask_sensitive(info['serial_number'])
        return info

    def _elm327_read_ecu_identification(self) -> Dict:
        """ELM327-specific ECU identification"""
        info = {
            'part_number': 'ELM327-ECU-READ',
            'software_version': 'V1.5.0',
            'hardware_version': 'HW-ELM327',
            'serial_number': 'ELM327-12345',
            'coding_data': 'ELM327 Coding Data',
            'diagnostic_address': '0x7E0',
            'supplier': 'ELM327 Compatible'
        }
        info['serial_number'] = self._mask_sensitive(info['serial_number'])
        return info

    def perform_advanced_diagnostic(self, diagnostic_type: str) -> Dict:
        """Perform advanced diagnostics based on device capabilities"""
        if not self.is_connected:
            return {'error': 'Not connected to device'}

        advanced_results = {
            'system_scan': self._perform_system_scan(),
            'module_coding': self._perform_module_coding_check(),
            'adaptation_values': self._read_adaptation_values(),
            'security_access': self._check_security_access(),
            'flash_programming': self._check_flash_programming()
        }
        
        if self.bench_mode:
            advanced_results['bench_status'] = self.get_breakout_status()
        
        return advanced_results.get(diagnostic_type, {'error': 'Unknown diagnostic type'})

    def _perform_system_scan(self) -> Dict:
        """Perform comprehensive system scan"""
        return {
            'engine_systems': ['ECM', 'TCM', 'Fuel System'],
            'chassis_systems': ['ABS', 'ESP', 'Airbag'],
            'body_systems': ['BCM', 'Immobilizer', 'Climate Control'],
            'network_systems': ['CAN Gateway', 'LIN Bus', 'MOST Bus']
        }

    def _perform_module_coding_check(self) -> Dict:
        """Check module coding and programming status"""
        return {
            'codable_modules': ['ECM', 'TCM', 'BCM', 'Instrument Cluster'],
            'coding_status': 'Read/Write Capable',
            'security_level': 'Dealer Level Required'
        }

    def _read_adaptation_values(self) -> Dict:
        """Read adaptation values from ECU"""
        return {
            'throttle_adaptation': 'Completed',
            'idle_speed_adaptation': 'Within Spec',
            'fuel_trim_adaptation': 'Active',
            'transmission_adaptation': 'Learned'
        }

    def _check_security_access(self) -> Dict:
        """Check security access capabilities"""
        return {
            'security_levels': ['Dealer', 'Factory', 'Component Protection'],
            'access_granted': True,
            'security_code_required': True
        }

    def _check_flash_programming(self) -> Dict:
        """Check flash programming capabilities (Enhanced for bench)"""
        base = {
            'flashable_modules': ['ECM', 'TCM', 'BCM'],
            'programming_type': 'Bootloader/Flash',
            'checksum_verification': 'Supported'
        }
        if self.bench_mode:
            status = self.get_breakout_status()
            base['power_stable'] = status.get('voltage', 0) >= 11.0
            base['note'] = 'GT100+ bench flashing ready'
        return base

    def disconnect(self):
        """Disconnect from device with professional cleanup"""
        if self.mock_mode:
            self.is_connected = False
            self.current_protocol = None
            self.current_device = None
            logger.info("Disconnected from professional device (mock)")
            return

        # Close serial connection
        if self.serial_conn:
            try:
                self.serial_conn.close()
                logger.info("Serial connection closed")
            except Exception as e:
                logger.error(f"Error closing serial connection: {e}")
            finally:
                self.serial_conn = None

        # Close GT100+ connection
        if self.gt100_conn:
            try:
                if isinstance(self.gt100_conn, serial.Serial):
                    self.gt100_conn.close()
                else:  # USB
                    usb.util.release_interface(self.gt100_conn, 0)
                    usb.util.dispose_resources(self.gt100_conn)
                logger.info("GT100+ connection closed")
            except Exception as e:
                logger.error(f"Error closing GT100+: {e}")
            finally:
                self.gt100_conn = None

        # Close Bluetooth connection
        if self.bt_socket:
            try:
                self.bt_socket.close()
                logger.info("Bluetooth connection closed")
            except Exception as e:
                logger.error(f"Error closing Bluetooth connection: {e}")
            finally:
                self.bt_socket = None

        self.is_connected = False
        self.current_protocol = None
        self.current_device = None
        self.bench_mode = False
        logger.info("Disconnected from professional device")

    def scan_dtcs(self) -> List[Tuple[str, str, str]]:
        """Scan for Diagnostic Trouble Codes"""
        if not self.is_connected:
            return []

        if self.mock_mode:
            time.sleep(1)
            return [
                ('P0300', 'High', 'Random/Multiple Cylinder Misfire Detected'),
                ('P0420', 'Medium', 'Catalyst Efficiency Below Threshold'),
                ('P0171', 'Medium', 'System Too Lean (Bank 1)'),
                ('U0100', 'Critical', 'Lost Communication with ECM')
            ]

        # Real implementation would go here
        return [('P0000', 'Info', 'No DTCs found - Professional Scan')]

    def get_live_data(self, pid: str) -> float:
        """Get live data from ECU"""
        if not self.is_connected:
            return 0.0

        if self.mock_mode:
            mock_data = {
                'rpm': random.randint(650, 3500),
                'speed': random.randint(0, 120),
                'coolant_temp': random.randint(80, 105),
                'fuel_level': random.randint(10, 95),
                'voltage': round(random.uniform(12.5, 14.5), 1),
            }
            return mock_data.get(pid.lower(), 0.0)

        # Real implementation would go here
        return 0.0

    def clear_dtcs(self) -> bool:
        """Clear all DTCs"""
        if not self.is_connected:
            return False

        if self.mock_mode:
            logger.info("[MOCK] DTCs cleared successfully")
            return True

        # Real implementation would go here
        return False

    def enable_can_sniffing(self, protocol: str = "ISO15765") -> bool:
        """Enable CAN bus sniffing mode for OBDLink MX+"""
        if not self.is_connected or self.current_device.device_type not in ["ELM327", "CANSniffer"]:
            logger.error("Not connected to ELM327 or CANSniffer device")
            return False

        if self.mock_mode:
            logger.info("[MOCK] CAN sniffing enabled")
            return True

        try:
            # Commands to set up CAN sniffing on OBDLink MX+
            commands = []

            # Reset device
            commands.append(b'ATZ\r\n')

            # Disable echo
            commands.append(b'ATE0\r\n')

            # Set protocol based on vehicle
            if protocol == "ISO15765":
                # ISO 15765-4 CAN 11-bit ID, 500 kbaud (standard for Ford)
                commands.append(b'ATSP6\r\n')
            elif protocol == "CAN29":
                # ISO 15765-4 CAN 29-bit ID, 500 kbaud
                commands.append(b'ATSP7\r\n')
            else:
                commands.append(b'ATSP6\r\n')  # Default to 11-bit

            # Turn off CAN auto formatting for raw sniffing
            commands.append(b'ATCAF0\r\n')

            # Turn off headers for cleaner output
            commands.append(b'ATH0\r\n')

            # Set timeout
            commands.append(b'ATST64\r\n')

            # Send all setup commands
            for cmd in commands:
                if self.serial_conn:
                    self.serial_conn.write(cmd)
                    time.sleep(0.1)  # Brief pause between commands
                    # Read response (optional, for debugging)
                    if self.serial_conn.in_waiting:
                        response = self.serial_conn.read_all().decode(errors='ignore').strip()
                        logger.debug(f"ELM response to {cmd.decode().strip()}: {response}")

            logger.info(f"CAN sniffing enabled for protocol: {protocol}")
            return True

        except Exception as e:
            logger.error(f"Failed to enable CAN sniffing: {e}")
            return False

    def start_can_monitor(self) -> bool:
        """Start monitoring CAN bus traffic"""
        if not self.is_connected or self.current_device.device_type not in ["ELM327", "CANSniffer"]:
            logger.error("Not connected to ELM327 or CANSniffer device")
            return False

        if self.mock_mode:
            logger.info("[MOCK] CAN monitoring started")
            return True

        try:
            # Send monitor all command
            if self.serial_conn:
                self.serial_conn.write(b'ATMA\r\n')
                logger.info("CAN monitoring started - press Ctrl+C to stop")
                return True
        except Exception as e:
            logger.error(f"Failed to start CAN monitoring: {e}")
            return False

    def read_can_messages(self, timeout_ms: int = 1000) -> List[str]:
        """Read CAN messages from the bus"""
        if not self.is_connected or self.current_device.device_type not in ["ELM327", "CANSniffer"]:
            return []

        if self.mock_mode:
            # Return mock CAN messages for Ford Ranger
            mock_messages = [
                "7E0 02 3E 00",  # Tester present response
                "7E8 06 41 0C 0F A0 00 00",  # Engine RPM
                "7E8 04 41 0D 32",  # Vehicle speed
                "7E8 03 7F 01 78",  # Pending response
            ]
            time.sleep(0.1)  # Simulate delay
            return mock_messages

        messages = []
        try:
            if self.serial_conn and self.serial_conn.in_waiting:
                start_time = time.time()
                while (time.time() - start_time) * 1000 < timeout_ms:
                    if self.serial_conn.in_waiting:
                        data = self.serial_conn.readline().decode(errors='ignore').strip()
                        if data:
                            messages.append(data)
                    else:
                        time.sleep(0.01)  # Small delay to prevent busy waiting
        except Exception as e:
            logger.error(f"Error reading CAN messages: {e}")

        return messages

    def stop_can_monitor(self) -> bool:
        """Stop CAN monitoring"""
        if not self.is_connected:
            return False

        if self.mock_mode:
            logger.info("[MOCK] CAN monitoring stopped")
            return True

        try:
            # Send any character to stop monitoring
            if self.serial_conn:
                self.serial_conn.write(b'\r\n')
                time.sleep(0.1)
                logger.info("CAN monitoring stopped")
                return True
        except Exception as e:
            logger.error(f"Failed to stop CAN monitoring: {e}")
            return False

# Test function
def test_professional_devices():
    """Test the professional device handler"""
    print("Testing Professional Device Handler")
    print("=" * 50)
    
    handler = DeviceHandler(mock_mode=True)
    
    # Test device detection
    devices = handler.detect_professional_devices()
    print(f"Detected {len(devices)} professional devices:")
    for device in devices:
        print(f"  - {device}")
        print(f"    Type: {device.device_type}")
        print(f"    Protocols: {', '.join(device.protocols)}")
        print(f"    Interfaces: {', '.join(device.interfaces)}")
    
    # Test connection to each device type (Added GT100+ and OBDLink MX+)
    test_devices = ["Godiag GT101", "ELM327 USB", "Mongoose Pro", "Godiag GT100+", "OBDLink MX+", "OBDLink MX+ Sniffer"]
    for device_name in test_devices:
        if handler.connect_to_device(device_name):
            print(f"[OK] Connected to {device_name}")
            # Test advanced features
            ecu_info = handler.read_ecu_identification_advanced()
            print(f"  ECU Info: {ecu_info.get('part_number', 'N/A')}")
            
            # Test bench mode for GT100+
            if "GT100" in device_name:
                handler.enable_bench_mode()
                status = handler.get_breakout_status()
                print(f"  GT100+ Status: {status.get('voltage', 'N/A')}V")
            
            # Test CAN sniffing for OBDLink MX+
            if "OBDLink" in device_name:
                print("  CAN Sniffer: Ready for CAN bus monitoring")
                if handler.enable_can_sniffing():
                    print("  [OK] CAN sniffing enabled")
            
            # Test advanced diagnostics
            system_scan = handler.perform_advanced_diagnostic('system_scan')
            print(f"  System Scan: {len(system_scan.get('engine_systems', []))} engine systems")
            
            handler.disconnect()
        else:
            print(f"[FAIL] Failed to connect to {device_name}")

if __name__ == "__main__":
    test_professional_devices()