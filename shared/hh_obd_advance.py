#!/usr/bin/env python3
"""
HH OBD Advance - Enhanced OBD Device Handler
Advanced OBD device detection and management for HH OBD Advance functionality
Supports "OBDII" device name detection and enhanced diagnostic capabilities
"""

import logging
import time
import serial
import threading
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)


class OBDDeviceType(Enum):
    """OBD device types for HH OBD Advance"""
    OBDLINK_MX_PLUS = "OBDLink MX+"
    GODIAG_GT100 = "GoDiag GT100"
    OBDII_GENERIC = "OBDII"  # The specific device name to look for
    ELM327 = "ELM327"
    STN11XX = "STN11XX"
    UNKNOWN = "Unknown"


@dataclass
class OBDDeviceInfo:
    """OBD device information"""
    device_type: OBDDeviceType
    port: str
    name: str
    description: str
    capabilities: List[str]
    is_real_hardware: bool = True
    protocol_support: List[str] = None
    baudrate: int = 38400


class HHOBDAdvanceHandler:
    """HH OBD Advance device handler with enhanced OBDII detection"""
    
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.detected_devices: List[OBDDeviceInfo] = []
        self.connected_device: Optional[OBDDeviceInfo] = None
        self.serial_connection = None
        self.connection_lock = threading.Lock()
        
        # Common OBDII device patterns
        self.obdii_patterns = [
            r'OBDII',
            r'OBD[-\s]?II',
            r'OBD2',
            r'ELM327',
            r'STN11',
            r'Waveshare',
            r'Veepeak',
            r'Autel',
            r'Launch'
        ]
        
        # Protocol mappings
        self.protocol_mapping = {
            '6': 'ISO15765_11BIT_CAN',  # Standard OBD-II CAN
            '7': 'ISO15765_29BIT_CAN',  # Extended CAN
            '5': 'ISO14230_4',          # KWP2000 fast init
            '4': 'ISO14230_4',          # KWP2000 slow init
            '3': 'ISO9141_2',           # ISO 9141-2
            '2': 'J1850_PWM',           # J1850 PWM
            '1': 'J1850_VPW'            # J1850 VPW
        }
        
        if not mock_mode:
            self.detect_obdii_devices()
    
    def detect_obdii_devices(self) -> List[OBDDeviceInfo]:
        """Detect OBDII devices, specifically looking for "OBDII" device name"""
        logger.info("Starting OBDII device detection...")
        
        # Common COM ports for OBDII devices
        possible_ports = [
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8',
            '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3',
            '/dev/ttyAMA0', '/dev/ttyAMA1'
        ]
        
        self.detected_devices.clear()
        
        for port in possible_ports:
            device_info = self._probe_port_for_obdii(port)
            if device_info:
                self.detected_devices.append(device_info)
                logger.info(f"Found OBDII device: {device_info.name} on {port}")
        
        # Specifically look for devices named "OBDII"
        obdii_devices = [d for d in self.detected_devices if d.device_type == OBDDeviceType.OBDII_GENERIC]
        if obdii_devices:
            logger.info(f"Found {len(obdii_devices)} device(s) named 'OBDII'")
            for device in obdii_devices:
                logger.info(f"  - {device.name} on {device.port}: {device.description}")
        
        return self.detected_devices
    
    def _probe_port_for_obdii(self, port: str) -> Optional[OBDDeviceInfo]:
        """Probe a specific port for OBDII device with enhanced detection"""
        try:
            # Try to open serial connection
            ser = serial.Serial(
                port=port,
                baudrate=38400,
                timeout=1.0,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            # Send ATZ command to reset and get device info
            ser.write(b'ATZ\r\n')
            time.sleep(0.5)
            
            # Read response
            response = ser.read(1024).decode('utf-8', errors='ignore').strip()
            
            # Send ATI command to get device info
            ser.write(b'ATI\r\n')
            time.sleep(0.3)
            device_info_response = ser.read(1024).decode('utf-8', errors='ignore').strip()
            
            # Send ATE0 to disable echo for cleaner responses
            ser.write(b'ATE0\r\n')
            time.sleep(0.2)
            
            # Send ATL0 to disable linefeeds
            ser.write(b'ATL0\r\n')
            time.sleep(0.2)
            
            ser.close()
            
            # Analyze responses to determine device type
            full_response = f"{response}\n{device_info_response}".upper()
            
            # Check for "OBDII" specifically
            if 'OBDII' in full_response or 'OBD-II' in full_response or 'OBD2' in full_response:
                return OBDDeviceInfo(
                    device_type=OBDDeviceType.OBDII_GENERIC,
                    port=port,
                    name="OBDII",
                    description="OBDII Generic Device",
                    capabilities=self._get_obdii_capabilities(),
                    is_real_hardware=True,
                    protocol_support=list(self.protocol_mapping.values())
                )
            
            # Check for other known device patterns
            if 'ELM327' in full_response:
                return OBDDeviceInfo(
                    device_type=OBDDeviceType.ELM327,
                    port=port,
                    name="ELM327",
                    description="ELM327 OBD Adapter",
                    capabilities=['PID', 'LIVE_DATA', 'DTC'],
                    is_real_hardware=True,
                    protocol_support=list(self.protocol_mapping.values())
                )
            
            if 'STN11' in full_response:
                return OBDDeviceInfo(
                    device_type=OBDDeviceType.STN11XX,
                    port=port,
                    name="STN11xx",
                    description="STN11xx OBD Adapter",
                    capabilities=['PID', 'LIVE_DATA', 'DTC', 'ADVANCED'],
                    is_real_hardware=True,
                    protocol_support=list(self.protocol_mapping.values())
                )
            
            # Generic OBD device detection
            if any(pattern in full_response for pattern in ['OK', 'ELM', 'STN']):
                return OBDDeviceInfo(
                    device_type=OBDDeviceType.UNKNOWN,
                    port=port,
                    name=f"OBD Device ({port})",
                    description="Generic OBD Adapter",
                    capabilities=['PID', 'LIVE_DATA', 'DTC'],
                    is_real_hardware=True,
                    protocol_support=list(self.protocol_mapping.values())
                )
                
        except Exception as e:
            logger.debug(f"Error probing port {port}: {e}")
        
        return None
    
    def _get_obdii_capabilities(self) -> List[str]:
        """Get capabilities specific to OBDII devices"""
        return [
            'PID',
            'LIVE_DATA',
            'DTC',
            'VIN_READ',
            'FREEZE_FRAMES',
            'OXYGEN_SENSOR',
            'READINESS_MONITORS',
            'VEHICLE_INFO',
            'CLEAR_CODES',
            'ECU_INFO',
            'MEMORY_READ',
            'MEMORY_WRITE'
        ]
    
    def connect_obdii_device(self, device_name: str = "OBDII") -> bool:
        """Connect to specific OBDII device"""
        with self.connection_lock:
            # Find device by name (prioritizing "OBDII")
            target_device = None
            
            # First, look for exact "OBDII" name match
            for device in self.detected_devices:
                if device.name.upper() == device_name.upper():
                    target_device = device
                    break
            
            # If not found, look for any OBDII-compatible device
            if not target_device:
                for device in self.detected_devices:
                    if device.device_type == OBDDeviceType.OBDII_GENERIC:
                        target_device = device
                        break
            
            # Fallback to first available OBD device
            if not target_device and self.detected_devices:
                target_device = self.detected_devices[0]
            
            if not target_device:
                logger.error(f"No OBDII device found matching '{device_name}'")
                return False
            
            try:
                # Connect to the device
                self.serial_connection = serial.Serial(
                    port=target_device.port,
                    baudrate=target_device.baudrate,
                    timeout=2.0,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE
                )
                
                # Initialize device
                if self._initialize_obdii_device():
                    self.connected_device = target_device
                    logger.info(f"Connected to OBDII device: {target_device.name} on {target_device.port}")
                    return True
                else:
                    self.serial_connection.close()
                    self.serial_connection = None
                    return False
                    
            except Exception as e:
                logger.error(f"Failed to connect to OBDII device: {e}")
                return False
    
    def _initialize_obdii_device(self) -> bool:
        """Initialize OBDII device with proper AT commands"""
        try:
            # Send initialization sequence
            init_commands = [
                (b'ATZ\r\n', "Reset device"),
                (b'ATE0\r\n', "Disable echo"),
                (b'ATL0\r\n', "Disable linefeeds"),
                (b'ATH1\r\n', "Enable headers"),
                (b'ATSP0\r\n', "Auto protocol select"),
                (b'ATAT2\r\n', "Adaptive timing 2"),
                (b'ATST62\r\n', "Set timeout to 62 * 4ms = 248ms"),
                (b'ATD1\r\n', "Set default settings")
            ]
            
            for cmd, description in init_commands:
                logger.debug(f"Sending {description}...")
                self._send_command(cmd)
                time.sleep(0.3)
            
            # Test connection with ATSH command
            self._send_command(b'ATSH\r\n')
            time.sleep(0.2)
            response = self._read_response()
            
            if response and 'OK' in response.upper():
                logger.info("OBDII device initialization successful")
                return True
            else:
                logger.warning("OBDII device initialization may have failed")
                return True  # Some devices don't respond to ATSH
                
        except Exception as e:
            logger.error(f"Error initializing OBDII device: {e}")
            return False
    
    def _send_command(self, command: bytes) -> bool:
        """Send command to connected OBDII device"""
        try:
            if not self.serial_connection:
                return False
            
            self.serial_connection.write(command)
            return True
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return False
    
    def _read_response(self, timeout: float = 1.0) -> Optional[str]:
        """Read response from OBDII device"""
        try:
            if not self.serial_connection:
                return None
            
            start_time = time.time()
            response = ""
            
            while time.time() - start_time < timeout:
                if self.serial_connection.in_waiting:
                    byte = self.serial_connection.read(1)
                    if byte:
                        response += byte.decode('utf-8', errors='ignore')
                        if '>' in response:  # End of response marker
                            break
                time.sleep(0.01)
            
            return response.strip()
        except Exception as e:
            logger.error(f"Error reading response: {e}")
            return None
    
    def execute_obd_command(self, command: str) -> Dict[str, any]:
        """Execute OBD command with enhanced HH OBD Advance features"""
        if not self.connected_device:
            return {"success": False, "error": "No OBDII device connected"}
        
        try:
            # Format command for OBDII device
            obd_command = f"{command}\r\n".encode('utf-8')
            
            # Send command
            if not self._send_command(obd_command):
                return {"success": False, "error": "Failed to send command"}
            
            # Read response
            response = self._read_response(timeout=2.0)
            
            if response:
                return {
                    "success": True,
                    "command": command,
                    "response": response,
                    "device": self.connected_device.name,
                    "timestamp": time.time()
                }
            else:
                return {"success": False, "error": "No response from device"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_advanced_obd_data(self) -> Dict[str, any]:
        """Get advanced OBD data with HH OBD Advance features"""
        if not self.connected_device:
            return {"success": False, "error": "No OBDII device connected"}
        
        results = {}
        
        # Standard OBD PIDs
        standard_pids = [
            ('010C', 'Engine RPM'),
            ('010D', 'Vehicle Speed'),
            ('0105', 'Coolant Temperature'),
            ('010B', 'Intake Pressure'),
            ('010F', 'Intake Temperature'),
            ('0111', 'Throttle Position'),
            ('0104', 'Engine Load'),
            ('012F', 'Fuel Level Input'),
            ('0106', 'Short Term Fuel Trim'),
            ('0107', 'Long Term Fuel Trim')
        ]
        
        for pid, description in standard_pids:
            result = self.execute_obd_command(pid)
            if result.get("success"):
                results[pid] = {
                    "description": description,
                    "value": result.get("response", ""),
                    "timestamp": time.time()
                }
        
        # Vehicle Information
        vin_result = self.execute_obd_command("0902")
        if vin_result.get("success"):
            results["VIN"] = {
                "description": "Vehicle Identification Number",
                "value": vin_result.get("response", ""),
                "timestamp": time.time()
            }
        
        # ECU Information
        ecu_result = self.execute_obd_command("0904")
        if ecu_result.get("success"):
            results["ECU_INFO"] = {
                "description": "ECU Information",
                "value": ecu_result.get("response", ""),
                "timestamp": time.time()
            }
        
        return {
            "success": True,
            "device_info": {
                "name": self.connected_device.name,
                "port": self.connected_device.port,
                "type": self.connected_device.device_type.value
            },
            "data": results,
            "timestamp": time.time()
        }
    
    def disconnect(self):
        """Disconnect from OBDII device"""
        with self.connection_lock:
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
                    logger.info("Disconnected from OBDII device")
    
    def get_device_status(self) -> Dict[str, any]:
        """Get current device status"""
        return {
            "connected": self.connected_device is not None,
            "device": self.connected_device.name if self.connected_device else None,
            "port": self.connected_device.port if self.connected_device else None,
            "detected_devices": len(self.detected_devices),
            "mock_mode": self.mock_mode
        }


def create_hh_obd_advance_handler(mock_mode: bool = False) -> HHOBDAdvanceHandler:
    """Factory function to create HH OBD Advance handler"""
    return HHOBDAdvanceHandler(mock_mode=mock_mode)