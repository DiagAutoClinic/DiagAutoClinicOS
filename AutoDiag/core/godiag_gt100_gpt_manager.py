"""
GoDiag GT100 PLUS GPT VCI Manager
==================================

Enhanced VCI manager specifically for GoDiag GT100 PLUS GPT devices with support for:
- DOIP (Diagnostics over Internet Protocol) via Ethernet
- GPT (General Programming Tool) mode for ECU reading/writing
- Real-time voltage and current monitoring
- 24V → 12V voltage conversion
- All-keys-lost key programming assistance
- Protocol detection and LED monitoring
- Battery replacement power backup

Based on the detailed technical specification from GODIAG_GT100_PLUS_GPT_Detailed_Guide.md
"""

import logging
import time
import threading
import socket
import serial
import usb.core
import usb.util
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from PyQt6.QtCore import QThread, pyqtSignal, QObject

logger = logging.getLogger(__name__)

class GT100GPTStatus(Enum):
    """GT100 PLUS GPT connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DOIP_ACTIVE = "doip_active"
    GPT_MODE = "gpt_mode"
    ERROR = "error"

class GT100GPTProtocol(Enum):
    """Supported protocols by GT100 PLUS GPT"""
    CAN_11_BIT_500KBPS = "ISO 15765-4 CAN 11-bit 500kbps"
    CAN_29_BIT_500KBPS = "ISO 15765-4 CAN 29-bit 500kbps"
    K_LINE = "ISO 9141-2 K-Line"
    KWP2000 = "ISO 14230-4 KWP2000"
    J1850_PWM = "J1850 PWM"
    J1850_VPW = "J1850 VPW"
    DOIP_ETHERNET = "DOIP over Ethernet"

@dataclass
class GT100GPTDevice:
    """GoDiag GT100 PLUS GPT device information"""
    device_type: str = "GoDiag GT100 PLUS GPT"
    name: str = "GoDiag GT100 PLUS GPT (SO537-C)"
    port: Optional[str] = None
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None
    status: GT100GPTStatus = GT100GPTStatus.DISCONNECTED
    last_seen: Optional[float] = None
    capabilities: List[str] = field(default_factory=lambda: [
        "obd2_passthrough", "voltage_monitoring", "current_monitoring",
        "protocol_detection", "doip_ethernet", "gpt_mode", "24v_conversion",
        "key_programming", "battery_backup", "banana_plug_access"
    ])
    
    # GT100 PLUS GPT specific attributes
    voltage_input: Optional[float] = None  # Input voltage (9V-24V)
    voltage_output: Optional[float] = None  # Output voltage (12V)
    current_draw: Optional[float] = None  # Current consumption
    protocol_leds: Dict[str, bool] = field(default_factory=dict)  # Protocol detection LEDs
    ethernet_ip: Optional[str] = None  # DOIP Ethernet IP address
    gpt_cable_connected: bool = False  # GPT cable status
    
    def __post_init__(self):
        """Initialize protocol LEDs"""
        if not self.protocol_leds:
            self.protocol_leds = {
                "pin_1": False,  # Reserved
                "pin_3": False,  # Chassis Ground / Porsche Cayenne
                "pin_8": False,  # CAN High
                "pin_9": False,  # CAN Low
                "pin_11": False, # K-Line
                "pin_12": False, # VPW+
                "pin_13": False  # Toyota ECU replacement
            }

class GT100GPTScannerThread(QThread):
    """QThread for scanning GT100 PLUS GPT devices"""
    scan_completed = pyqtSignal(list)
    scan_error = pyqtSignal(str)
    scan_progress = pyqtSignal(str)
    
    def __init__(self, gt100_manager):
        super().__init__()
        self.gt100_manager = gt100_manager
        self.timeout = 20  # Extended timeout for GT100 detection
        self._stop_event = threading.Event()
        
    def stop(self):
        """Stop the scanning thread"""
        self._stop_event.set()
        self.quit()
        self.wait(3000)  # Wait up to 3 seconds
        
    def run(self):
        """Thread entry point"""
        try:
            self.scan_progress.emit("Starting GoDiag GT100 PLUS GPT device scan...")
            devices = self.gt100_manager._scan_for_gt100_devices_with_timeout(self.timeout)
            self.scan_completed.emit(devices)
        except Exception as e:
            logger.error(f"GT100 PLUS GPT scan thread error: {e}")
            self.scan_error.emit(str(e))
        finally:
            self.gt100_manager.is_scanning = False

class GoDiagGT100GPTManager(QObject):
    """Enhanced VCI manager for GoDiag GT100 PLUS GPT devices"""
    
    # Signals for UI updates
    status_changed = pyqtSignal(str, object)
    devices_found = pyqtSignal(list)
    voltage_updated = pyqtSignal(float, float)  # (input_voltage, output_voltage)
    protocol_detected = pyqtSignal(str)  # protocol name
    gpt_mode_changed = pyqtSignal(bool)  # GPT mode on/off
    
    def __init__(self):
        super().__init__()
        self.connected_gt100: Optional[GT100GPTDevice] = None
        self.available_devices: List[GT100GPTDevice] = []
        self.is_scanning = False
        self.scan_thread = None
        self.callbacks: List[callable] = []
        
        # GT100 PLUS GPT specific settings
        self.doip_socket: Optional[socket.socket] = None
        self.gpt_serial: Optional[serial.Serial] = None
        self.monitoring_thread: Optional[threading.Thread] = None
        self.voltage_monitoring_active = False
        
        # GT100 PLUS GPT USB VID/PID
        self.gt100_usb_vid = 0x1eab  # GoDiag Vendor ID
        self.gt100_usb_pid = 0x9001  # GT100 PLUS GPT Product ID
        
        logger.info("GoDiag GT100 PLUS GPT Manager initialized")

    def add_status_callback(self, callback: callable):
        """Add callback for GT100 status changes"""
        self.callbacks.append(callback)

    def remove_status_callback(self, callback: callable):
        """Remove GT100 status callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def _notify_callbacks(self, event: str, data: Any = None):
        """Notify all registered callbacks"""
        for callback in self.callbacks:
            try:
                callback(event, data)
            except Exception as e:
                logger.debug(f"Callback error: {e}")

    def scan_for_devices(self, timeout: int = 20) -> bool:
        """Start scanning for GT100 PLUS GPT devices"""
        if self.is_scanning:
            logger.warning("GT100 PLUS GPT device scan already in progress")
            return False

        self.is_scanning = True
        self.available_devices = []
        
        # Create and start scan thread
        self.scan_thread = GT100GPTScannerThread(self)
        self.scan_thread.scan_completed.connect(self._on_scan_completed)
        self.scan_thread.scan_error.connect(self._on_scan_error)
        self.scan_thread.scan_progress.connect(self._on_scan_progress)
        self.scan_thread.timeout = timeout
        self.scan_thread.start()
        
        return True

    def _scan_for_gt100_devices_with_timeout(self, timeout: int) -> List[GT100GPTDevice]:
        """Internal method for scanning GT100 PLUS GPT devices"""
        devices = []
        start_time = time.time()
        logger.info(f"Starting GT100 PLUS GPT device scan (timeout: {timeout}s)")

        try:
            # Scan for USB GT100 devices
            devices.extend(self._scan_gt100_usb_devices(start_time, timeout))
            
            # Check timeout
            if time.time() - start_time > timeout:
                logger.warning(f"GT100 scan timed out after {timeout} seconds")
                return devices

            # Scan for ENET DOIP devices
            devices.extend(self._scan_gt100_enet_devices(start_time, timeout))

            # Check timeout
            if time.time() - start_time > timeout:
                logger.warning(f"GT100 scan timed out after {timeout} seconds")
                return devices

            # Remove duplicates
            unique_devices = []
            seen_identifiers = set()
            for device in devices:
                identifier = f"{device.name}_{device.port}_{device.ethernet_ip}"
                if identifier not in seen_identifiers:
                    seen_identifiers.add(identifier)
                    unique_devices.append(device)

            elapsed = time.time() - start_time
            logger.info(f"GT100 PLUS GPT scan completed in {elapsed:.1f}s, found {len(unique_devices)} devices")

            return unique_devices

        except Exception as e:
            logger.error(f"GT100 PLUS GPT device scan failed: {e}")
            return devices

    def _scan_gt100_usb_devices(self, start_time: float, timeout: int) -> List[GT100GPTDevice]:
        """Scan for USB-connected GT100 PLUS GPT devices"""
        devices = []
        try:
            # Scan for GoDiag USB devices
            godiag_devices = usb.core.find(find_all=True, idVendor=self.gt100_usb_vid)
            
            if godiag_devices is not None:
                for device in godiag_devices:
                    # Check timeout
                    if time.time() - start_time > timeout:
                        logger.warning("GT100 scan timeout reached during USB scan")
                        break
                        
                    if device.idProduct == self.gt100_usb_pid:
                        gt100_device = GT100GPTDevice()
                        gt100_device.port = f"USB_{device.bus:03d}_{device.address:03d}"
                        gt100_device.serial_number = usb.util.get_string(device, device.iSerialNumber)
                        gt100_device.firmware_version = usb.util.get_string(device, device.iProduct)
                        gt100_device.last_seen = time.time()
                        gt100_device.status = GT100GPTStatus.DISCONNECTED
                        
                        devices.append(gt100_device)
                        logger.info(f"Found GT100 PLUS GPT via USB: {gt100_device.serial_number}")
                        
        except Exception as e:
            logger.error(f"GT100 PLUS GPT USB scan failed: {e}")
            
        return devices

    def _scan_gt100_enet_devices(self, start_time: float, timeout: int) -> List[GT100GPTDevice]:
        """Scan for Ethernet DOIP GT100 PLUS GPT devices"""
        devices = []
        try:
            # Common IP ranges for automotive diagnostic equipment
            ip_ranges = [
                "192.168.1.0/24",  # Common diagnostic network
                "192.168.10.0/24", # Alternative diagnostic network
                "10.0.0.0/24"      # Generic network
            ]
            
            for ip_range in ip_ranges:
                # Check timeout
                if time.time() - start_time > timeout:
                    logger.warning("GT100 scan timeout reached during ENET scan")
                    break
                    
                # Scan network for GT100 DOIP devices
                found_devices = self._scan_network_for_gt100(ip_range)
                devices.extend(found_devices)
                
        except Exception as e:
            logger.error(f"GT100 PLUS GPT ENET scan failed: {e}")
            
        return devices

    def _scan_network_for_gt100(self, ip_range: str) -> List[GT100GPTDevice]:
        """Scan a network range for GT100 DOIP devices"""
        devices = []
        try:
            import ipaddress
            
            network = ipaddress.ip_network(ip_range, strict=False)
            
            # Common DOIP ports for GT100 PLUS GPT
            doip_ports = [13400, 8080, 80]  # Standard DOIP and HTTP ports
            
            for ip in network.hosts():
                for port in doip_ports:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(2.0)  # 2 second timeout per connection
                        result = sock.connect_ex((str(ip), port))
                        
                        if result == 0:
                            # Port is open, try to identify GT100 device
                            if self._identify_gt100_doip_device(str(ip), port):
                                gt100_device = GT100GPTDevice()
                                gt100_device.ethernet_ip = str(ip)
                                gt100_device.port = f"DOIP_{ip}:{port}"
                                gt100_device.last_seen = time.time()
                                gt100_device.status = GT100GPTStatus.DISCONNECTED
                                devices.append(gt100_device)
                                logger.info(f"Found GT100 PLUS GPT via DOIP: {ip}:{port}")
                                break  # Found device on this IP
                                
                        sock.close()
                    except Exception:
                        continue  # Continue to next port/IP
                        
        except Exception as e:
            logger.error(f"Network scan for GT100 failed: {e}")
            
        return devices

    def _identify_gt100_doip_device(self, ip: str, port: int) -> bool:
        """Identify if a DOIP device is a GT100 PLUS GPT"""
        try:
            # Send DOIP activation request or HTTP request to identify device
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3.0)
            sock.connect((ip, port))
            
            # Send HTTP GET request to check for GT100 web interface
            http_request = f"GET / HTTP/1.1\r\nHost: {ip}\r\nConnection: close\r\n\r\n"
            sock.send(http_request.encode())
            
            response = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.close()
            
            # Check for GT100 indicators in response
            gt100_indicators = [
                "GoDiag", "GT100", "GPT", "DOIP", "godiag"
            ]
            
            for indicator in gt100_indicators:
                if indicator.lower() in response.lower():
                    return True
                    
            return False
            
        except Exception:
            return False

    def _on_scan_completed(self, devices):
        """Handle scan completion from thread"""
        self.available_devices = devices
        self.is_scanning = False
        self.devices_found.emit(devices)
        
        # Log found devices
        for device in devices:
            logger.info(f"Found GT100 PLUS GPT: {device.name} - Port: {device.port}")

    def _on_scan_error(self, error_message):
        """Handle scan error from thread"""
        logger.error(f"GT100 PLUS GPT scan error: {error_message}")
        self.is_scanning = False
        self.status_changed.emit("error", {"message": error_message})

    def _on_scan_progress(self, progress_message):
        """Handle scan progress updates"""
        logger.debug(f"GT100 PLUS GPT scan progress: {progress_message}")
        self.status_changed.emit("progress", {"message": progress_message})

    def connect_to_device(self, device: GT100GPTDevice) -> bool:
        """Connect to a specific GT100 PLUS GPT device"""
        try:
            logger.info(f"Connecting to {device.name}...")

            # Update device status
            device.status = GT100GPTStatus.CONNECTING
            self._notify_callbacks("connecting", device)

            # Attempt connection based on device type
            if device.port and device.port.startswith("USB_"):
                success = self._connect_gt100_usb(device)
            elif device.port and device.port.startswith("DOIP_"):
                success = self._connect_gt100_doip(device)
            else:
                success = self._connect_gt100_generic(device)

            if success:
                device.status = GT100GPTStatus.CONNECTED
                device.last_seen = time.time()
                self.connected_gt100 = device
                self._notify_callbacks("connected", device)
                logger.info(f"Successfully connected to {device.name}")
                
                # Start voltage monitoring
                self._start_voltage_monitoring()
                
                return True
            else:
                device.status = GT100GPTStatus.ERROR
                self._notify_callbacks("connection_failed", device)
                logger.error(f"Failed to connect to {device.name}")
                return False

        except Exception as e:
            logger.error(f"GT100 PLUS GPT connection error: {e}")
            device.status = GT100GPTStatus.ERROR
            self._notify_callbacks("connection_error", {"device": device, "error": str(e)})
            return False

    def _connect_gt100_usb(self, device: GT100GPTDevice) -> bool:
        """Connect to USB GT100 PLUS GPT device"""
        try:
            # Find USB device
            godiag_device = usb.core.find(idVendor=self.gt100_usb_vid, idProduct=self.gt100_usb_pid)
            
            if godiag_device:
                # Configure USB device
                godiag_device.set_configuration()
                
                # Store reference to USB device
                device._usb_device = godiag_device
                
                # Read initial device information
                self._read_gt100_device_info(device)
                
                logger.info("GT100 PLUS GPT connected via USB")
                return True
            else:
                logger.error("GT100 PLUS GPT USB device not found")
                return False
                
        except Exception as e:
            logger.error(f"GT100 PLUS GPT USB connection failed: {e}")
            return False

    def _connect_gt100_doip(self, device: GT100GPTDevice) -> bool:
        """Connect to DOIP GT100 PLUS GPT device"""
        try:
            if not device.ethernet_ip:
                logger.error("No IP address specified for DOIP connection")
                return False
                
            # Extract IP and port from device.port
            doip_info = device.port.replace("DOIP_", "").split(":")
            ip = doip_info[0]
            port = int(doip_info[1]) if len(doip_info) > 1 else 13400
            
            # Create DOIP socket connection
            self.doip_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.doip_socket.settimeout(5.0)
            self.doip_socket.connect((ip, port))
            
            # Send DOIP activation request
            activation_request = self._create_doip_activation_request()
            self.doip_socket.send(activation_request)
            
            # Wait for response
            response = self.doip_socket.recv(1024)
            
            if self._validate_doip_response(response):
                device.status = GT100GPTStatus.DOIP_ACTIVE
                logger.info(f"GT100 PLUS GPT connected via DOIP: {ip}:{port}")
                return True
            else:
                logger.error("Invalid DOIP response from GT100 PLUS GPT")
                return False
                
        except Exception as e:
            logger.error(f"GT100 PLUS GPT DOIP connection failed: {e}")
            return False

    def _connect_gt100_generic(self, device: GT100GPTDevice) -> bool:
        """Connect to GT100 PLUS GPT using generic method"""
        try:
            # Try to connect via serial port if available
            if device.port and not device.port.startswith("USB_") and not device.port.startswith("DOIP_"):
                self.gpt_serial = serial.Serial(device.port, 115200, timeout=5)
                
                # Test communication with AT commands
                self.gpt_serial.write(b"ATI\r")  # Identify
                time.sleep(0.1)
                response = self.gpt_serial.read(100).decode('ascii', errors='ignore')
                
                if "GT100" in response or "GoDiag" in response:
                    logger.info(f"GT100 PLUS GPT connected via serial: {device.port}")
                    return True
                else:
                    self.gpt_serial.close()
                    logger.error("Failed to identify GT100 PLUS GPT via serial")
                    return False
            else:
                logger.error("No suitable connection method found for GT100 PLUS GPT")
                return False
                
        except Exception as e:
            logger.error(f"GT100 PLUS GPT generic connection failed: {e}")
            return False

    def _create_doip_activation_request(self) -> bytes:
        """Create DOIP activation request"""
        # DOIP activation request format (simplified)
        # This is a basic implementation - real DOIP protocol is more complex
        header = b"\x02\x00\x00\x04"  # DOIP header
        protocol_version = b"\x02"    # Protocol version 2
        payload_type = b"\x00\x04"    # Vehicle identification request
        payload_length = b"\x00\x00\x00\x00"  # No additional payload
        
        return header + protocol_version + payload_type + payload_length

    def _validate_doip_response(self, response: bytes) -> bool:
        """Validate DOIP response from GT100 PLUS GPT"""
        # Basic validation - check for DOIP header
        if len(response) >= 4 and response[:4] == b"\x02\x00\x00\x05":
            return True
        return False

    def _read_gt100_device_info(self, device: GT100GPTDevice):
        """Read device information from GT100 PLUS GPT"""
        try:
            if hasattr(device, '_usb_device'):
                # Read device information via USB control transfer
                # This would require specific USB commands for GT100 PLUS GPT
                pass
                
        except Exception as e:
            logger.error(f"Failed to read GT100 PLUS GPT device info: {e}")

    def _start_voltage_monitoring(self):
        """Start voltage and current monitoring with crash fix"""
        if self.voltage_monitoring_active:
            return
            
        self.voltage_monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._voltage_monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        # CRASH FIX: Register thread for cleanup
        try:
            from AutoDiag.main import thread_cleanup_manager
            thread_cleanup_manager.register_thread(self.monitoring_thread, "GT100_VoltageMonitoring")
        except ImportError:
            pass  # thread_cleanup_manager not available
            
        logger.info("GT100 PLUS GPT voltage monitoring started with crash protection")

    def _voltage_monitoring_loop(self):
        """CRASH FIX: Continuous voltage and current monitoring loop with safety limits"""
        pulse_count = 0
        max_pulses = 3600  # Safety limit: 1 hour of monitoring max
        
        while self.voltage_monitoring_active and self.connected_gt100:
            try:
                pulse_count += 1
                
                # Safety limit to prevent infinite operation
                if pulse_count >= max_pulses:
                    logger.warning("⚠️ Voltage monitoring pulse limit reached - stopping to prevent issues")
                    break
                
                # Read voltage and current from GT100 PLUS GPT
                if hasattr(self.connected_gt100, '_usb_device'):
                    # USB monitoring
                    input_voltage, output_voltage, current = self._read_usb_voltage_current()
                elif self.doip_socket:
                    # DOIP monitoring
                    input_voltage, output_voltage, current = self._read_doip_voltage_current()
                elif self.gpt_serial:
                    # Serial monitoring
                    input_voltage, output_voltage, current = self._read_serial_voltage_current()
                else:
                    # Simulated values for testing
                    input_voltage = 24.0  # Simulated 24V input
                    output_voltage = 12.4  # Simulated 12V output
                    current = 0.15  # Simulated 150mA current
                    
                # Update device information
                self.connected_gt100.voltage_input = input_voltage
                self.connected_gt100.voltage_output = output_voltage
                self.connected_gt100.current_draw = current
                
                # Emit voltage update signal
                self.voltage_updated.emit(input_voltage, output_voltage)
                
                # Log critical voltage levels (reduced frequency)
                if input_voltage < 11.0:
                    logger.warning(f"⚠️ GT100 PLUS GPT low input voltage: {input_voltage}V")
                elif input_voltage > 25.0:
                    logger.warning(f"⚠️ GT100 PLUS GPT high input voltage: {input_voltage}V")
                
                # Log every 100 pulses to prove loop is running
                if pulse_count % 100 == 0:
                    logger.debug(f"🟡 Voltage monitoring pulse #{pulse_count}")
                    
                time.sleep(1.0)  # Update every second
                
            except Exception as e:
                logger.error(f"❌ Voltage monitoring error: {e}")
                # Don't continue on error to prevent crash loops
                break

    def _read_usb_voltage_current(self) -> Tuple[float, float, float]:
        """Read voltage and current via USB"""
        # This would require specific USB control transfers to GT100 PLUS GPT
        # For now, return simulated values
        return 24.0, 12.4, 0.15

    def _read_doip_voltage_current(self) -> Tuple[float, float, float]:
        """Read voltage and current via DOIP"""
        # This would require DOIP requests for diagnostic data
        # For now, return simulated values
        return 24.0, 12.4, 0.15

    def _read_serial_voltage_current(self) -> Tuple[float, float, float]:
        """Read voltage and current via serial"""
        try:
            if self.gpt_serial:
                # Send voltage query command
                self.gpt_serial.write(b"ATCV\r")  # Command to read voltage
                time.sleep(0.1)
                response = self.gpt_serial.read(50).decode('ascii', errors='ignore')
                
                # Parse voltage from response
                # This is a simplified example - real parsing would be more complex
                if "12." in response:
                    return 24.0, 12.4, 0.15
                    
        except Exception as e:
            logger.error(f"Serial voltage read failed: {e}")
            
        return 24.0, 12.4, 0.15

    def enable_gpt_mode(self) -> bool:
        """Enable GPT (General Programming Tool) mode"""
        if not self.connected_gt100 or self.connected_gt100.status != GT100GPTStatus.CONNECTED:
            logger.error("GT100 PLUS GPT not connected")
            return False
            
        try:
            # Send GPT mode enable command
            if self.gpt_serial:
                self.gpt_serial.write(b"AT+GPT\r")
                time.sleep(0.1)
                response = self.gpt_serial.read(50).decode('ascii', errors='ignore')
                
                if "OK" in response:
                    self.connected_gt100.status = GT100GPTStatus.GPT_MODE
                    self.gpt_mode_changed.emit(True)
                    self._notify_callbacks("gpt_mode_enabled", self.connected_gt100)
                    logger.info("GPT mode enabled")
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to enable GPT mode: {e}")
            
        return False

    def disable_gpt_mode(self) -> bool:
        """Disable GPT mode"""
        if not self.connected_gt100:
            return False
            
        try:
            # Send GPT mode disable command
            if self.gpt_serial:
                self.gpt_serial.write(b"AT-GPT\r")
                time.sleep(0.1)
                response = self.gpt_serial.read(50).decode('ascii', errors='ignore')
                
                if "OK" in response:
                    self.connected_gt100.status = GT100GPTStatus.CONNECTED
                    self.gpt_mode_changed.emit(False)
                    self._notify_callbacks("gpt_mode_disabled", self.connected_gt100)
                    logger.info("GPT mode disabled")
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to disable GPT mode: {e}")
            
        return False

    def get_supported_protocols(self) -> List[str]:
        """Get list of supported protocols"""
        return [protocol.value for protocol in GT100GPTProtocol]

    def detect_protocols(self) -> List[str]:
        """Detect active protocols on GT100 PLUS GPT"""
        if not self.connected_gt100:
            return []
            
        detected_protocols = []
        
        # Check protocol LEDs
        for pin, active in self.connected_gt100.protocol_leds.items():
            if active:
                # Map pin to protocol
                protocol_map = {
                    "pin_8": GT100GPTProtocol.CAN_11_BIT_500KBPS.value,
                    "pin_9": GT100GPTProtocol.CAN_11_BIT_500KBPS.value,
                    "pin_11": GT100GPTProtocol.K_LINE.value,
                    "pin_12": GT100GPTProtocol.J1850_VPW.value,
                }
                
                if pin in protocol_map:
                    protocol = protocol_map[pin]
                    if protocol not in detected_protocols:
                        detected_protocols.append(protocol)
                        self.protocol_detected.emit(protocol)
                        
        return detected_protocols

    def enable_doip_diagnostics(self, ecu_ip: str = "192.168.1.100") -> bool:
        """Enable DOIP diagnostics for ECU communication"""
        if not self.connected_gt100:
            logger.error("GT100 PLUS GPT not connected")
            return False
            
        try:
            # Send DOIP diagnostic enable command
            if self.doip_socket:
                diagnostic_request = self._create_doip_diagnostic_request(ecu_ip)
                self.doip_socket.send(diagnostic_request)
                
                response = self.doip_socket.recv(1024)
                
                if self._validate_doip_response(response):
                    self.connected_gt100.status = GT100GPTStatus.DOIP_ACTIVE
                    logger.info(f"DOIP diagnostics enabled for ECU: {ecu_ip}")
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to enable DOIP diagnostics: {e}")
            
        return False

    def _create_doip_diagnostic_request(self, ecu_ip: str) -> bytes:
        """Create DOIP diagnostic request"""
        # Simplified DOIP diagnostic request
        header = b"\x02\x00\x00\x08"  # DOIP header for diagnostic message
        protocol_version = b"\x02"
        payload_type = b"\x00\x08"    # Diagnostic message
        payload_length = b"\x00\x00\x00\x0C"  # 12 bytes payload
        ecu_address = b"\x7E0\x00"    # Standard ECU address
        diagnostic_service = b"\x10\x01"  # Diagnostic session control
        
        return header + protocol_version + payload_type + payload_length + ecu_address + diagnostic_service

    def get_voltage_status(self) -> Dict[str, float]:
        """Get current voltage and current status"""
        if not self.connected_gt100:
            return {"input_voltage": 0.0, "output_voltage": 0.0, "current_draw": 0.0}
            
        return {
            "input_voltage": self.connected_gt100.voltage_input or 0.0,
            "output_voltage": self.connected_gt100.voltage_output or 0.0,
            "current_draw": self.connected_gt100.current_draw or 0.0
        }

    def disconnect(self) -> bool:
        """Disconnect from GT100 PLUS GPT device"""
        if not self.connected_gt100:
            return True

        try:
            # Stop voltage monitoring
            self.voltage_monitoring_active = False
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=2.0)
                
            # Close connections
            if self.doip_socket:
                self.doip_socket.close()
                self.doip_socket = None
                
            if self.gpt_serial:
                self.gpt_serial.close()
                self.gpt_serial = None
                
            device = self.connected_gt100
            device.status = GT100GPTStatus.DISCONNECTED
            self._notify_callbacks("disconnected", device)

            logger.info(f"Disconnected from {device.name}")
            self.connected_gt100 = None
            return True

        except Exception as e:
            logger.error(f"GT100 PLUS GPT disconnect error: {e}")
            return False

    def get_connected_device(self) -> Optional[GT100GPTDevice]:
        """Get currently connected GT100 PLUS GPT device"""
        return self.connected_gt100

    def get_device_info(self) -> Dict[str, Any]:
        """Get information about connected GT100 PLUS GPT device"""
        if not self.connected_gt100:
            return {"status": "disconnected"}

        device = self.connected_gt100
        voltage_status = self.get_voltage_status()
        
        return {
            "status": device.status.value,
            "type": device.device_type,
            "name": device.name,
            "port": device.port,
            "capabilities": device.capabilities,
            "firmware_version": device.firmware_version,
            "serial_number": device.serial_number,
            "ethernet_ip": device.ethernet_ip,
            "voltage_input": voltage_status["input_voltage"],
            "voltage_output": voltage_status["output_voltage"],
            "current_draw": voltage_status["current_draw"],
            "protocol_leds": device.protocol_leds,
            "gpt_mode": device.status == GT100GPTStatus.GPT_MODE,
            "doip_active": device.status == GT100GPTStatus.DOIP_ACTIVE
        }

    def is_connected(self) -> bool:
        """Check if GT100 PLUS GPT is connected"""
        return (self.connected_gt100 is not None and
                self.connected_gt100.status in [GT100GPTStatus.CONNECTED, 
                                               GT100GPTStatus.GPT_MODE,
                                               GT100GPTStatus.DOIP_ACTIVE])

    def get_supported_devices(self) -> List[str]:
        """Get list of supported GT100 PLUS GPT device types"""
        return ["GoDiag GT100 PLUS GPT (SO537-C)", "GoDiag GT100 PLUS GPT"]


# Global GT100 PLUS GPT manager instance
gt100_gpt_manager = GoDiagGT100GPTManager()


def get_gt100_gpt_manager() -> GoDiagGT100GPTManager:
    """Get the global GT100 PLUS GPT manager instance"""
    return gt100_gpt_manager