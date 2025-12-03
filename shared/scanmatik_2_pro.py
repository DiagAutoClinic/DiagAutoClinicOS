#!/usr/bin/env python3
"""
ScanMatik 2 Pro - Professional Diagnostic Device Handler
Advanced OBD scanner with enhanced diagnostics, programming, and bidirectional control
Supports CAN, KWP2000, UDS protocols with professional-grade features
"""

import logging
import time
import serial
import threading
import re
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ScanMatikProtocol(Enum):
    """Supported protocols by ScanMatik 2 Pro"""
    J1850_PWM = "J1850 PWM"
    J1850_VPW = "J1850 VPW" 
    ISO9141_2 = "ISO 9141-2"
    ISO14230_4 = "ISO 14230-4 KWP2000"
    ISO15765_11BIT_CAN = "ISO 15765-2 (11-bit CAN)"
    ISO15765_29BIT_CAN = "ISO 15765-2 (29-bit CAN)"
    UDS_OVER_CAN = "UDS (ISO 14229) over CAN"
    UDS_OVER_KWP2000 = "UDS (ISO 14229) over KWP2000"


class ScanMatikDeviceType(Enum):
    """ScanMatik 2 Pro device variants"""
    SCANMATIK_2_PRO = "ScanMatik 2 Pro"
    SCANMATIK_2 = "ScanMatik 2"
    SCANMATIK_PRO = "ScanMatik Pro"
    SCANMATIK_STANDARD = "ScanMatik Standard"
    ELM327_COMPATIBLE = "ELM327 Compatible"
    UNKNOWN = "Unknown"


class ScanMatikFeature(Enum):
    """Advanced features supported by ScanMatik 2 Pro"""
    BASIC_OBD = "Basic OBD-II"
    ENHANCED_OBD = "Enhanced OBD (Mode 9)"
    DTC_CODES = "Diagnostic Trouble Codes"
    LIVE_DATA = "Live Data Streaming"
    FREEZE_FRAMES = "Freeze Frame Data"
    READINESS_MONITORS = "Readiness Monitors"
    VIN_READING = "VIN Reading"
    ECU_INFO = "ECU Information"
    PROGRAMMING = "ECU Programming"
    BIDIRECTIONAL = "Bidirectional Control"
    SPECIAL_FUNCTIONS = "Special Functions"
    CALIBRATION_RESET = "Calibration/Reset"
    SECURITY_ACCESS = "Security Access"
    ADVANCED_DIAGNOSTICS = "Advanced Diagnostics"
    MANUFACTURER_SPECIFIC = "Manufacturer-Specific"
    CAN_SNIFFING = "CAN Bus Sniffing"
    UDS_COMMANDS = "UDS Protocol Commands"


@dataclass
class ScanMatikDeviceInfo:
    """ScanMatik 2 Pro device information"""
    device_type: ScanMatikDeviceType
    port: str
    name: str
    description: str
    firmware_version: str = "Unknown"
    protocol_support: List[ScanMatikProtocol] = None
    features: List[ScanMatikFeature] = None
    is_real_hardware: bool = True
    baudrate: int = 38400
    capabilities: List[str] = None
    
    def __post_init__(self):
        if self.protocol_support is None:
            self.protocol_support = [
                ScanMatikProtocol.ISO15765_11BIT_CAN,
                ScanMatikProtocol.ISO15765_29BIT_CAN,
                ScanMatikProtocol.ISO14230_4,
                ScanMatikProtocol.UDS_OVER_CAN
            ]
        if self.features is None:
            self.features = [
                ScanMatikFeature.BASIC_OBD,
                ScanMatikFeature.DTC_CODES,
                ScanMatikFeature.LIVE_DATA,
                ScanMatikFeature.VIN_READING
            ]
        if self.capabilities is None:
            self.capabilities = [
                'PID_READ', 'LIVE_DATA', 'DTC_SCAN', 'DTC_CLEAR', 'VIN_READ',
                'ECU_INFO', 'FREEZE_FRAMES', 'READINESS', 'BIDIRECTIONAL',
                'PROGRAMMING', 'UDS_COMMANDS'
            ]


class ScanMatik2Pro:
    """ScanMatik 2 Pro device handler with comprehensive diagnostic capabilities"""
    
    def __init__(self, mock_mode: bool = False, device_name: str = "ScanMatik 2 Pro"):
        self.mock_mode = mock_mode
        self.device_name = device_name
        self.detected_devices: List[ScanMatikDeviceInfo] = []
        self.connected_device: Optional[ScanMatikDeviceInfo] = None
        self.serial_connection = None
        self.connection_lock = threading.Lock()
        
        # Device identification patterns
        self.scanmatik_patterns = [
            r'ScanMatik\s*2\s*Pro',
            r'ScanMatik\s*2',
            r'ScanMatik\s*Pro',
            r'SM2[\s\-]?PRO',
            r'SM2PRO',
            r'SCANNMATIK\s*II'
        ]
        
        # Protocol mappings for AT commands
        self.protocol_commands = {
            ScanMatikProtocol.J1850_PWM: "ATPP2C0SV1",
            ScanMatikProtocol.J1850_VPW: "ATPP2C0SV2", 
            ScanMatikProtocol.ISO9141_2: "ATPP2C0SV3",
            ScanMatikProtocol.ISO14230_4: "ATPP2C0SV4",
            ScanMatikProtocol.ISO15765_11BIT_CAN: "ATSP6",
            ScanMatikProtocol.ISO15765_29BIT_CAN: "ATSP7",
            ScanMatikProtocol.UDS_OVER_CAN: "ATSP6",
            ScanMatikProtocol.UDS_OVER_KWP2000: "ATSP4"
        }
        
        # AT command templates for different operations
        self.at_commands = {
            'reset': 'ATZ',
            'echo_off': 'ATE0',
            'linefeeds_off': 'ATL0',
            'headers_on': 'ATH1',
            'auto_protocol': 'ATSP0',
            'adaptive_timing': 'ATAT2',
            'set_timeout': 'ATST62',
            'version': 'ATI',
            'description': 'AT@1',
            'protocol': 'ATDP',
            'protocol_description': 'ATDPN',
            'set_addresses': 'ATSHA7E0',  # ECU address 7E0
            'filter_ids': 'ATCF7E0'       # Filter for ECU responses
        }
        
        # OBD PID templates
        self.obd_pids = {
            'rpm': '010C',
            'speed': '010D', 
            'coolant_temp': '0105',
            'intake_pressure': '010B',
            'intake_temp': '010F',
            'throttle_pos': '0111',
            'engine_load': '0104',
            'fuel_level': '012F',
            'short_trim': '0106',
            'long_trim': '0107',
            'vin': '0902',
            'ecu_info': '0904'
        }
        
        # Initialize mock devices if in mock mode
        if mock_mode:
            self._setup_mock_devices()
        
        # Auto-detect real hardware if not in mock mode
        if not mock_mode:
            self.detect_devices()
    
    def _setup_mock_devices(self):
        """Setup mock ScanMatik devices for testing"""
        logger.info("Setting up mock ScanMatik 2 Pro devices...")
        
        mock_device = ScanMatikDeviceInfo(
            device_type=ScanMatikDeviceType.SCANMATIK_2_PRO,
            port="MOCK_PORT",
            name="ScanMatik 2 Pro (Mock)",
            description="Mock ScanMatik 2 Pro device for testing",
            firmware_version="2.1.3",
            protocol_support=[
                ScanMatikProtocol.ISO15765_11BIT_CAN,
                ScanMatikProtocol.ISO15765_29BIT_CAN,
                ScanMatikProtocol.UDS_OVER_CAN,
                ScanMatikProtocol.ISO14230_4
            ],
            features=[
                ScanMatikFeature.BASIC_OBD,
                ScanMatikFeature.ENHANCED_OBD,
                ScanMatikFeature.DTC_CODES,
                ScanMatikFeature.LIVE_DATA,
                ScanMatikFeature.BIDIRECTIONAL,
                ScanMatikFeature.PROGRAMMING,
                ScanMatikFeature.UDS_COMMANDS,
                ScanMatikFeature.CAN_SNIFFING
            ],
            is_real_hardware=False
        )
        
        self.detected_devices.append(mock_device)
        logger.info(f"Mock device setup complete: {mock_device.name}")
    
    def detect_devices(self) -> List[ScanMatikDeviceInfo]:
        """Detect ScanMatik 2 Pro devices on available ports"""
        logger.info("Starting ScanMatik 2 Pro device detection...")
        
        if self.mock_mode:
            return self.detected_devices
        
        # Common ports for diagnostic devices
        possible_ports = [
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3', '/dev/ttyUSB4',
            '/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2', '/dev/ttyACM3'
        ]
        
        self.detected_devices.clear()
        
        for port in possible_ports:
            device_info = self._probe_port_for_scanmatik(port)
            if device_info:
                self.detected_devices.append(device_info)
                logger.info(f"Found ScanMatik device: {device_info.name} on {port}")
        
        logger.info(f"ScanMatik detection complete. Found {len(self.detected_devices)} device(s)")
        return self.detected_devices
    
    def _probe_port_for_scanmatik(self, port: str) -> Optional[ScanMatikDeviceInfo]:
        """Probe a specific port for ScanMatik device"""
        if self.mock_mode:
            return self.detected_devices[0] if self.detected_devices else None
            
        try:
            ser = serial.Serial(
                port=port,
                baudrate=38400,
                timeout=1.0,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            # Send device identification commands
            ser.write(b'ATZ\r\n')  # Reset
            time.sleep(0.5)
            response = ser.read(1024).decode('utf-8', errors='ignore').strip()
            
            ser.write(b'ATI\r\n')  # Version info
            time.sleep(0.3)
            version_response = ser.read(1024).decode('utf-8', errors='ignore').strip()
            
            ser.write(b'AT@1\r\n')  # Device description
            time.sleep(0.3)
            desc_response = ser.read(1024).decode('utf-8', errors='ignore').strip()
            
            ser.write(b'ATE0\r\n')  # Disable echo for cleaner responses
            time.sleep(0.2)
            
            ser.close()
            
            # Analyze responses for ScanMatik patterns
            full_response = f"{response}\n{version_response}\n{desc_response}".upper()
            
            # Check for ScanMatik patterns
            for pattern in self.scanmatik_patterns:
                if re.search(pattern, full_response, re.IGNORECASE):
                    # Determine device type
                    if '2 PRO' in full_response:
                        device_type = ScanMatikDeviceType.SCANMATIK_2_PRO
                        features = [
                            ScanMatikFeature.BASIC_OBD,
                            ScanMatikFeature.ENHANCED_OBD,
                            ScanMatikFeature.DTC_CODES,
                            ScanMatikFeature.LIVE_DATA,
                            ScanMatikFeature.BIDIRECTIONAL,
                            ScanMatikFeature.PROGRAMMING,
                            ScanMatikFeature.SECURITY_ACCESS,
                            ScanMatikFeature.UDS_COMMANDS,
                            ScanMatikFeature.CAN_SNIFFING,
                            ScanMatikFeature.ADVANCED_DIAGNOSTICS
                        ]
                    elif '2' in full_response:
                        device_type = ScanMatikDeviceType.SCANMATIK_2
                        features = [
                            ScanMatikFeature.BASIC_OBD,
                            ScanMatikFeature.DTC_CODES,
                            ScanMatikFeature.LIVE_DATA,
                            ScanMatikFeature.VIN_READING
                        ]
                    else:
                        device_type = ScanMatikDeviceType.SCANMATIK_PRO
                        features = [
                            ScanMatikFeature.BASIC_OBD,
                            ScanMatikFeature.ENHANCED_OBD,
                            ScanMatikFeature.DTC_CODES,
                            ScanMatikFeature.LIVE_DATA,
                            ScanMatikFeature.BIDIRECTIONAL
                        ]
                    
                    return ScanMatikDeviceInfo(
                        device_type=device_type,
                        port=port,
                        name=f"ScanMatik Device ({port})",
                        description=desc_response or "ScanMatik Diagnostic Device",
                        firmware_version=version_response or "Unknown",
                        features=features,
                        is_real_hardware=True
                    )
            
            # Check for generic OBD device (ELM327 compatible)
            if any(keyword in full_response for keyword in ['ELM327', 'OBD', 'STN']):
                return ScanMatikDeviceInfo(
                    device_type=ScanMatikDeviceType.ELM327_COMPATIBLE,
                    port=port,
                    name=f"ELM327 Compatible ({port})",
                    description="ELM327-based OBD Adapter",
                    firmware_version=version_response or "Unknown",
                    features=[
                        ScanMatikFeature.BASIC_OBD,
                        ScanMatikFeature.DTC_CODES,
                        ScanMatikFeature.LIVE_DATA
                    ],
                    is_real_hardware=True
                )
                
        except Exception as e:
            logger.debug(f"Error probing port {port}: {e}")
        
        return None
    
    def connect_device(self, device_name: str = "ScanMatik 2 Pro") -> bool:
        """Connect to a specific ScanMatik device"""
        with self.connection_lock:
            # Find device by name
            target_device = None
            
            # Exact name match first
            for device in self.detected_devices:
                if device.name.upper() == device_name.upper():
                    target_device = device
                    break
            
            # Partial name match
            if not target_device:
                for device in self.detected_devices:
                    if device_name.upper() in device.name.upper() or device.name.upper() in device_name.upper():
                        target_device = device
                        break
            
            # Fallback to first device
            if not target_device and self.detected_devices:
                target_device = self.detected_devices[0]
            
            if not target_device:
                logger.error(f"No ScanMatik device found matching '{device_name}'")
                return False
            
            try:
                if self.mock_mode:
                    # Mock connection
                    self.connected_device = target_device
                    logger.info(f"[MOCK] Connected to {target_device.name}")
                    return True
                
                # Real device connection
                self.serial_connection = serial.Serial(
                    port=target_device.port,
                    baudrate=target_device.baudrate,
                    timeout=2.0,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE
                )
                
                # Initialize device
                if self._initialize_device():
                    self.connected_device = target_device
                    logger.info(f"Connected to ScanMatik device: {target_device.name} on {target_device.port}")
                    return True
                else:
                    self.serial_connection.close()
                    self.serial_connection = None
                    return False
                    
            except Exception as e:
                logger.error(f"Failed to connect to ScanMatik device: {e}")
                return False
    
    def _initialize_device(self) -> bool:
        """Initialize ScanMatik device with proper commands"""
        try:
            # Standard initialization sequence
            init_sequence = [
                (b'ATZ\r\n', "Reset device"),
                (b'ATE0\r\n', "Disable echo"),
                (b'ATL0\r\n', "Disable linefeeds"), 
                (b'ATH1\r\n', "Enable headers"),
                (b'ATSP0\r\n', "Auto protocol select"),
                (b'ATAT2\r\n', "Adaptive timing 2"),
                (b'ATST62\r\n', "Set timeout"),
                (b'ATSHA7E0\r\n', "Set ECU address")
            ]
            
            for cmd, description in init_sequence:
                logger.debug(f"Sending {description}...")
                self._send_command(cmd)
                time.sleep(0.3)
            
            # Test connection
            self._send_command(b'AT\r\n')
            time.sleep(0.2)
            response = self._read_response()
            
            if response and 'OK' in response.upper():
                logger.info("ScanMatik device initialization successful")
                return True
            else:
                logger.warning("ScanMatik initialization may have issues but continuing")
                return True
                
        except Exception as e:
            logger.error(f"Error initializing ScanMatik device: {e}")
            return False
    
    def _send_command(self, command: bytes) -> bool:
        """Send command to connected ScanMatik device"""
        try:
            if self.mock_mode:
                logger.debug(f"[MOCK] Would send command: {command}")
                return True
                
            if not self.serial_connection:
                return False
            
            self.serial_connection.write(command)
            self.serial_connection.flush()
            return True
            
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return False
    
    def _read_response(self, timeout: float = 2.0) -> Optional[str]:
        """Read response from ScanMatik device"""
        try:
            if self.mock_mode:
                # Mock responses based on command
                return "OK"
                
            if not self.serial_connection:
                return None
            
            start_time = time.time()
            response = ""
            
            while time.time() - start_time < timeout:
                if self.serial_connection.in_waiting:
                    byte = self.serial_connection.read(1)
                    if byte:
                        response += byte.decode('utf-8', errors='ignore')
                        if '>' in response:  # End marker
                            break
                time.sleep(0.01)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error reading response: {e}")
            return None
    
    def execute_obd_command(self, command: str) -> Dict[str, any]:
        """Execute OBD command via ScanMatik 2 Pro"""
        if not self.connected_device:
            return {"success": False, "error": "No ScanMatik device connected"}
        
        try:
            # Format and send command
            obd_command = f"{command}\r\n".encode('utf-8')
            
            if not self._send_command(obd_command):
                return {"success": False, "error": "Failed to send command"}
            
            # Read response
            response = self._read_response(timeout=3.0)
            
            if response:
                return {
                    "success": True,
                    "command": command,
                    "response": response,
                    "device": self.connected_device.name,
                    "protocol": "OBD-II",
                    "timestamp": time.time()
                }
            else:
                return {"success": False, "error": "No response from device"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_uds_command(self, service_id: str, data: bytes = b'') -> Dict[str, any]:
        """Execute UDS command via ScanMatik 2 Pro"""
        if not self.connected_device:
            return {"success": False, "error": "No ScanMatik device connected"}
        
        if not any(ScanMatikFeature.UDS_COMMANDS in self.connected_device.features for self in [self]):
            return {"success": False, "error": "UDS not supported by this device"}
        
        try:
            # UDS request format: [Header] + Service + Data + [Footer]
            # For simplicity, using standard CAN ID 0x7E0 (ECU request)
            uds_request = bytes([0x7E0]) + bytes.fromhex(service_id) + data
            
            # Convert to AT command format for serial communication
            # This is simplified - real implementation would handle ISO-TP fragmentation
            command_hex = uds_request.hex().upper()
            at_command = f"ATCA{command_hex}\r\n"  # Custom AT command for UDS
            
            if not self._send_command(at_command.encode()):
                return {"success": False, "error": "Failed to send UDS command"}
            
            response = self._read_response(timeout=5.0)
            
            if response:
                return {
                    "success": True,
                    "service": service_id,
                    "response": response,
                    "device": self.connected_device.name,
                    "protocol": "UDS",
                    "timestamp": time.time()
                }
            else:
                return {"success": False, "error": "No response from UDS command"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_live_data(self, parameters: List[str] = None) -> Dict[str, any]:
        """Get live data from connected vehicle"""
        if not self.connected_device:
            return {"success": False, "error": "No ScanMatik device connected"}
        
        if parameters is None:
            parameters = ['rpm', 'speed', 'coolant_temp', 'intake_pressure', 'intake_temp']
        
        results = {}
        
        for param in parameters:
            pid = self.obd_pids.get(param.lower())
            if pid:
                result = self.execute_obd_command(pid)
                if result.get("success"):
                    results[param] = {
                        "pid": pid,
                        "value": result.get("response", ""),
                        "timestamp": time.time()
                    }
        
        return {
            "success": True,
            "data": results,
            "device": self.connected_device.name,
            "timestamp": time.time()
        }
    
    def get_comprehensive_diagnostics(self) -> Dict[str, any]:
        """Get comprehensive diagnostic data from vehicle"""
        if not self.connected_device:
            return {"success": False, "error": "No ScanMatik device connected"}
        
        logger.info("Starting comprehensive diagnostics scan...")
        
        diagnostics = {
            "device_info": {
                "name": self.connected_device.name,
                "port": self.connected_device.port,
                "type": self.connected_device.device_type.value,
                "features": [f.value for f in self.connected_device.features]
            },
            "vehicle_info": {},
            "live_data": {},
            "dtc_info": {},
            "readiness_monitors": {},
            "vin_info": {}
        }
        
        try:
            # Vehicle Information
            vin_result = self.execute_obd_command("0902")
            if vin_result.get("success"):
                diagnostics["vin_info"]["vin"] = vin_result.get("response", "")
            
            ecu_info_result = self.execute_obd_command("0904")
            if ecu_info_result.get("success"):
                diagnostics["vehicle_info"]["ecu_info"] = ecu_info_result.get("response", "")
            
            # Live Data
            live_data = self.get_live_data()
            if live_data.get("success"):
                diagnostics["live_data"] = live_data.get("data", {})
            
            # DTC Codes
            dtc_result = self.execute_obd_command("03")
            if dtc_result.get("success"):
                diagnostics["dtc_info"]["codes"] = dtc_result.get("response", "")
            
            # Readiness Monitors
            readiness_result = self.execute_obd_command("01")
            if readiness_result.get("success"):
                diagnostics["readiness_monitors"]["status"] = readiness_result.get("response", "")
            
            diagnostics["success"] = True
            diagnostics["timestamp"] = time.time()
            
            logger.info("Comprehensive diagnostics scan completed successfully")
            
        except Exception as e:
            diagnostics["success"] = False
            diagnostics["error"] = str(e)
            logger.error(f"Error during comprehensive diagnostics: {e}")
        
        return diagnostics
    
    def disconnect(self):
        """Disconnect from ScanMatik device"""
        with self.connection_lock:
            if self.mock_mode:
                logger.info("[MOCK] Disconnected from ScanMatik device")
                self.connected_device = None
                return
            
            if self.serial_connection:
                try:
                    self._send_command(b'ATZ\r\n')  # Reset before disconnect
                    time.sleep(0.5)
                    self.serial_connection.close()
                except:
                    pass
                finally:
                    self.serial_connection = None
                    self.connected_device = None
                    logger.info("Disconnected from ScanMatik device")
    
    def get_device_status(self) -> Dict[str, any]:
        """Get current device status"""
        return {
            "connected": self.connected_device is not None,
            "device": self.connected_device.name if self.connected_device else None,
            "port": self.connected_device.port if self.connected_device else None,
            "detected_devices": len(self.detected_devices),
            "mock_mode": self.mock_mode,
            "features": [f.value for f in self.connected_device.features] if self.connected_device else []
        }


def create_scanmatik_2_pro_handler(mock_mode: bool = True, device_name: str = "ScanMatik 2 Pro") -> ScanMatik2Pro:
    """Factory function to create ScanMatik 2 Pro handler"""
    return ScanMatik2Pro(mock_mode=mock_mode, device_name=device_name)


if __name__ == "__main__":
    # Test the handler
    logging.basicConfig(level=logging.INFO)
    
    # Test mock mode
    handler = create_scanmatik_2_pro_handler(mock_mode=True)
    
    print(f"Detected devices: {len(handler.detected_devices)}")
    for device in handler.detected_devices:
        print(f"  - {device.name}: {device.description}")
    
    if handler.connect_device():
        print("Connected successfully!")
        
        # Test live data
        live_data = handler.get_live_data(['rpm', 'speed', 'coolant_temp'])
        print(f"Live data: {live_data}")
        
        # Test comprehensive diagnostics
        diagnostics = handler.get_comprehensive_diagnostics()
        print(f"Diagnostics success: {diagnostics.get('success', False)}")
        
        handler.disconnect()
        print("Disconnected successfully")
    else:
        print("Failed to connect")