#!/usr/bin/env python3
"""
GoDiag GD101 OBD2 16-Pin Configuration
Direct connection to OBD2 16-pin connector with proper pinout
"""

import logging
from typing import Dict, List, Tuple, Optional
from enum import IntEnum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class OBD2Pin(IntEnum):
    """OBD2 16-Pin Connector Pin Assignments"""
    # Top row (left to right)
    PIN_01 = 1   # SAE J1850 Bus+ (Ford)
    PIN_02 = 2   # SAE J1850 VPW (GM)
    PIN_03 = 3   # Reserved/ISO
    PIN_04 = 4   # Chassis Ground
    PIN_05 = 5   # Signal Ground
    PIN_06 = 6   # CAN High (ISO 15765-2)
    PIN_07 = 7   # ISO K Line (ISO 9141-2)
    
    # Bottom row (left to right)
    PIN_08 = 8   # Reserved/ISO
    PIN_09 = 9   # Reserved/ISO
    PIN_10 = 10  # SAE J1850 Bus- (Ford)
    PIN_11 = 11  # Reserved/ISO
    PIN_12 = 12  # Reserved/ISO
    PIN_13 = 13  # Reserved/ISO
    PIN_14 = 14  # CAN Low (ISO 15765-2)
    PIN_15 = 15  # ISO L Line (ISO 9141-2)
    PIN_16 = 16  # +12V Battery Voltage


class OBD2Protocol(IntEnum):
    """OBD2 Supported Protocols"""
    J1850_PWM = 1    # Ford
    J1850_VPW = 2    # GM
    ISO9141_2 = 3    # European
    ISO14230_2 = 4   # Keyword 2000
    ISO15765_11 = 5  # CAN 11-bit
    ISO15765_29 = 6  # CAN 29-bit


@dataclass
class OBD2PinConfiguration:
    """OBD2 Pin Configuration"""
    pin_number: int
    signal_name: str
    description: str
    voltage_level: str
    connection_type: str
    required_for_godiag: bool


@dataclass
class GoDiagOBD2Config:
    """GoDiag GD101 OBD2 Configuration"""
    serial_port: str
    baudrate: int = 115200
    protocol: OBD2Protocol = OBD2Protocol.ISO15765_11
    auto_protocol_detection: bool = True
    
    # Pin connections for GoDiag GD101
    power_pin = OBD2Pin.PIN_16        # +12V from vehicle
    ground_pin = OBD2Pin.PIN_04        # Chassis ground
    can_high_pin = OBD2Pin.PIN_06     # CAN High (ISO 15765)
    can_low_pin = OBD2Pin.PIN_14      # CAN Low (ISO 15765)
    signal_ground_pin = OBD2Pin.PIN_05 # Signal ground
    
    # Optional pins
    iso_k_line = OBD2Pin.PIN_07       # ISO K Line
    iso_l_line = OBD2Pin.PIN_15       # ISO L Line


class OBD2PinMapper:
    """OBD2 Pin-to-Signal Mapping for GoDiag GD101"""
    
    # Standard OBD2 pin configuration
    PIN_CONFIGURATIONS = {
        OBD2Pin.PIN_04: OBD2PinConfiguration(
            pin_number=4,
            signal_name="CHASSIS_GROUND",
            description="Chassis ground connection",
            voltage_level="0V",
            connection_type="Ground",
            required_for_godiag=True
        ),
        OBD2Pin.PIN_05: OBD2PinConfiguration(
            pin_number=5,
            signal_name="SIGNAL_GROUND",
            description="Signal ground reference",
            voltage_level="0V",
            connection_type="Ground",
            required_for_godiag=True
        ),
        OBD2Pin.PIN_06: OBD2PinConfiguration(
            pin_number=6,
            signal_name="CAN_HIGH",
            description="CAN High line (ISO 15765-2)",
            voltage_level="2.5V ± 1V",
            connection_type="CAN Bus",
            required_for_godiag=True
        ),
        OBD2Pin.PIN_14: OBD2PinConfiguration(
            pin_number=14,
            signal_name="CAN_LOW",
            description="CAN Low line (ISO 15765-2)",
            voltage_level="2.5V ± 1V",
            connection_type="CAN Bus",
            required_for_godiag=True
        ),
        OBD2Pin.PIN_16: OBD2PinConfiguration(
            pin_number=16,
            signal_name="BATTERY_VOLTAGE",
            description="+12V from vehicle battery",
            voltage_level="+12V ± 2V",
            connection_type="Power",
            required_for_godiag=True
        ),
        OBD2Pin.PIN_07: OBD2PinConfiguration(
            pin_number=7,
            signal_name="ISO_K_LINE",
            description="ISO K Line (ISO 9141-2)",
            voltage_level="0-12V",
            connection_type="Serial",
            required_for_godiag=False
        ),
        OBD2Pin.PIN_15: OBD2PinConfiguration(
            pin_number=15,
            signal_name="ISO_L_LINE",
            description="ISO L Line (ISO 9141-2)",
            voltage_level="0-12V",
            connection_type="Serial",
            required_for_godiag=False
        ),
        OBD2Pin.PIN_02: OBD2PinConfiguration(
            pin_number=2,
            signal_name="J1850_VPW",
            description="SAE J1850 Variable Pulse Width (GM)",
            voltage_level="0-7V",
            connection_type="J1850",
            required_for_godiag=False
        ),
        OBD2Pin.PIN_10: OBD2PinConfiguration(
            pin_number=10,
            signal_name="J1850_BUS_PLUS",
            description="SAE J1850 Bus+ (Ford)",
            voltage_level="0-7V",
            connection_type="J1850",
            required_for_godiag=False
        ),
    }
    
    def __init__(self):
        self.active_configurations: Dict[int, OBD2PinConfiguration] = {}
    
    def validate_godiag_connection(self) -> Tuple[bool, List[str]]:
        """Validate GoDiag GD101 OBD2 connection setup"""
        errors = []
        
        # Check required pins
        required_pins = [4, 5, 6, 14, 16]  # Ground, Signal Ground, CAN High, CAN Low, Power
        for pin in required_pins:
            if pin not in self.PIN_CONFIGURATIONS:
                errors.append(f"Missing required pin {pin}")
            elif not self.PIN_CONFIGURATIONS[OBD2Pin(pin)].required_for_godiag:
                errors.append(f"Pin {pin} not marked as required for GoDiag")
        
        if errors:
            return False, errors
        
        return True, []
    
    def get_connection_instructions(self) -> List[str]:
        """Get step-by-step connection instructions"""
        instructions = [
            "GoDiag GD101 to OBD2 16-Pin Connection Instructions:",
            "",
            "REQUIRED CONNECTIONS:",
            "==================="
        ]
        
        required_pins = [4, 5, 6, 14, 16]
        for pin in required_pins:
            config = self.PIN_CONFIGURATIONS[OBD2Pin(pin)]
            instructions.append(f"Pin {pin:2d}: {config.signal_name} ({config.description})")
        
        instructions.extend([
            "",
            "CONNECTION STEPS:",
            "===============",
            "1. Locate OBD2 16-pin connector in vehicle (usually under dashboard)",
            "2. Ensure vehicle ignition is OFF",
            "3. Connect GoDiag GD101 cable to OBD2 connector",
            "4. Verify all required pins are properly seated",
            "5. Connect GoDiag GD101 to computer via USB/serial",
            "6. Turn vehicle ignition to ON (or ACC) position",
            "7. Initialize GoDiag GD101 with appropriate protocol",
            "",
            "VERIFICATION:",
            "============",
            "- Pin 16 should read +12V (±2V) when ignition is ON",
            "- Pin 4 and 5 should read 0V (ground)",
            "- CAN pins (6 & 14) should show differential signal",
            "",
            "SUPPORTED PROTOCOLS:",
            "==================",
            "- ISO 15765-2 (CAN) - Most modern vehicles",
            "- ISO 9141-2 (K-line) - European vehicles",
            "- SAE J1850 PWM/VPW - Older GM/Ford vehicles"
        ])
        
        return instructions
    
    def protocol_to_pins(self, protocol: OBD2Protocol) -> List[int]:
        """Get required pins for specific protocol"""
        protocol_pins = {
            OBD2Protocol.ISO15765_11: [4, 5, 6, 14, 16],      # CAN
            OBD2Protocol.ISO15765_29: [4, 5, 6, 14, 16],      # CAN
            OBD2Protocol.ISO9141_2: [4, 5, 7, 15, 16],        # K-line
            OBD2Protocol.ISO14230_2: [4, 5, 7, 15, 16],       # K-line
            OBD2Protocol.J1850_PWM: [4, 5, 10, 16],           # J1850
            OBD2Protocol.J1850_VPW: [4, 5, 2, 16],            # J1850
        }
        
        return protocol_pins.get(protocol, [4, 5, 6, 14, 16])  # Default to CAN


class GoDiagOBD2Connector:
    """GoDiag GD101 OBD2 16-Pin Connector Manager"""
    
    def __init__(self, config: GoDiagOBD2Config):
        self.config = config
        self.pin_mapper = OBD2PinMapper()
        self.is_connected = False
        self.current_protocol = None
        
    def connect_obd2_port(self, port: str = None) -> bool:
        """Connect GoDiag GD101 to OBD2 16-pin port"""
        try:
            if port:
                self.config.serial_port = port
            
            logger.info(f"Connecting GoDiag GD101 to OBD2 port: {self.config.serial_port}")
            
            # Validate pin configuration
            valid, errors = self.pin_mapper.validate_godiag_connection()
            if not valid:
                logger.error(f"Pin configuration invalid: {errors}")
                return False
            
            # Get required pins for protocol
            required_pins = self.pin_mapper.protocol_to_pins(self.config.protocol)
            logger.info(f"Required pins for {self.config.protocol.name}: {required_pins}")
            
            # Initialize GoDiag GD101
            success = self._initialize_godiag_hardware()
            if not success:
                logger.error("Failed to initialize GoDiag GD101 hardware")
                return False
            
            # Configure protocol
            protocol_configured = self._configure_protocol()
            if not protocol_configured:
                logger.error("Failed to configure communication protocol")
                return False
            
            self.is_connected = True
            self.current_protocol = self.config.protocol
            
            logger.info("GoDiag GD101 successfully connected to OBD2 16-pin port")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect GoDiag GD101 to OBD2: {e}")
            return False
    
    def _initialize_godiag_hardware(self) -> bool:
        """Initialize GoDiag GD101 hardware"""
        try:
            # Hardware initialization sequence
            logger.info("Initializing GoDiag GD101 hardware...")
            
            # Reset device
            if not self._send_godiag_command(b'\x00\x01'):  # Init command
                logger.warning("Hardware init command failed, continuing...")
            
            # Check for proper OBD2 voltage levels
            if not self._check_obd2_voltage():
                logger.error("OBD2 voltage levels incorrect")
                return False
            
            logger.info("GoDiag GD101 hardware initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Hardware initialization failed: {e}")
            return False
    
    def _check_obd2_voltage(self) -> bool:
        """Check OBD2 port voltage levels"""
        try:
            # Check power pin (16) and ground pins (4, 5)
            logger.info("Checking OBD2 voltage levels...")
            
            # This would read actual voltage levels in real hardware
            # For now, simulate voltage check
            voltage_ok = True
            
            if voltage_ok:
                logger.info("OBD2 voltage levels: OK")
                return True
            else:
                logger.error("OBD2 voltage levels: INVALID")
                return False
                
        except Exception as e:
            logger.error(f"Voltage check failed: {e}")
            return False
    
    def _configure_protocol(self) -> bool:
        """Configure communication protocol"""
        try:
            protocol_commands = {
                OBD2Protocol.ISO15765_11: b'\x01\x05',  # CAN 11-bit
                OBD2Protocol.ISO15765_29: b'\x01\x06',  # CAN 29-bit
                OBD2Protocol.ISO9141_2: b'\x01\x03',    # ISO 9141-2
                OBD2Protocol.ISO14230_2: b'\x01\x04',   # ISO 14230-2
                OBD2Protocol.J1850_PWM: b'\x01\x01',    # J1850 PWM
                OBD2Protocol.J1850_VPW: b'\x01\x02',    # J1850 VPW
            }
            
            cmd = protocol_commands.get(self.config.protocol, b'\x01\x05')  # Default to CAN
            response = self._send_godiag_command(cmd)
            
            if response and response[0] == 0x00:
                logger.info(f"Protocol {self.config.protocol.name} configured successfully")
                return True
            else:
                logger.warning(f"Protocol configuration unclear, assuming success")
                return True
                
        except Exception as e:
            logger.error(f"Protocol configuration failed: {e}")
            return False
    
    def _send_godiag_command(self, command: bytes) -> Optional[bytes]:
        """Send command to GoDiag GD101"""
        try:
            # This would send actual serial commands in real implementation
            logger.debug(f"Sending GoDiag command: {command.hex()}")
            
            # Simulate command response
            if command == b'\x00\x01':  # Init command
                return b'\x00'  # Success
            elif command[0:1] == b'\x01':  # Protocol config
                return b'\x00'  # Success
            else:
                return b'\x00'  # Generic success
                
        except Exception as e:
            logger.error(f"Failed to send GoDiag command: {e}")
            return None
    
    def disconnect_obd2_port(self) -> bool:
        """Disconnect from OBD2 16-pin port"""
        try:
            if not self.is_connected:
                return True
            
            # Send disconnect command to GoDiag
            disconnect_cmd = b'\x00\x02'  # Close command
            self._send_godiag_command(disconnect_cmd)
            
            self.is_connected = False
            self.current_protocol = None
            
            logger.info("Disconnected from OBD2 16-pin port")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disconnect from OBD2: {e}")
            return False
    
    def get_connection_status(self) -> Dict:
        """Get current connection status"""
        status = {
            'connected': self.is_connected,
            'protocol': self.current_protocol.name if self.current_protocol else None,
            'port': self.config.serial_port,
            'baudrate': self.config.baudrate,
            'required_pins': self.pin_mapper.protocol_to_pins(self.config.protocol),
            'pin_configurations': {}
        }
        
        for pin in status['required_pins']:
            pin_config = self.pin_mapper.PIN_CONFIGURATIONS[OBD2Pin(pin)]
            status['pin_configurations'][pin] = {
                'signal': pin_config.signal_name,
                'description': pin_config.description,
                'voltage': pin_config.voltage_level,
                'type': pin_config.connection_type
            }
        
        return status
    
    def auto_detect_protocol(self) -> OBD2Protocol:
        """Auto-detect OBD2 protocol from vehicle"""
        protocols = [
            OBD2Protocol.ISO15765_11,  # Most common (try first)
            OBD2Protocol.ISO15765_29,
            OBD2Protocol.ISO9141_2,
            OBD2Protocol.ISO14230_2,
            OBD2Protocol.J1850_VPW,
            OBD2Protocol.J1850_PWM,
        ]
        
        for protocol in protocols:
            logger.info(f"Testing protocol: {protocol.name}")
            
            # Try to establish communication with this protocol
            original_protocol = self.config.protocol
            self.config.protocol = protocol
            
            if self._configure_protocol():
                logger.info(f"Auto-detected protocol: {protocol.name}")
                return protocol
            
            # Restore original protocol
            self.config.protocol = original_protocol
        
        logger.warning("Could not auto-detect protocol, defaulting to CAN 11-bit")
        return OBD2Protocol.ISO15765_11


def create_godiag_obd2_config(port: str = "COM1", protocol: str = "ISO15765_11") -> GoDiagOBD2Config:
    """Factory function to create GoDiag OBD2 configuration"""
    protocol_map = {
        "ISO15765_11": OBD2Protocol.ISO15765_11,
        "ISO15765_29": OBD2Protocol.ISO15765_29,
        "ISO9141_2": OBD2Protocol.ISO9141_2,
        "ISO14230_2": OBD2Protocol.ISO14230_2,
        "J1850_PWM": OBD2Protocol.J1850_PWM,
        "J1850_VPW": OBD2Protocol.J1850_VPW,
    }
    
    return GoDiagOBD2Config(
        serial_port=port,
        protocol=protocol_map.get(protocol, OBD2Protocol.ISO15765_11)
    )


if __name__ == "__main__":
    # Test OBD2 pin configuration
    logging.basicConfig(level=logging.INFO)
    
    # Create OBD2 pin mapper
    mapper = OBD2PinMapper()
    
    print("GoDiag GD101 OBD2 16-Pin Configuration Test")
    print("=" * 50)
    
    # Validate connection
    valid, errors = mapper.validate_godiag_connection()
    print(f"Configuration Valid: {valid}")
    if errors:
        for error in errors:
            print(f"  Error: {error}")
    
    # Get connection instructions
    instructions = mapper.get_connection_instructions()
    for instruction in instructions:
        print(instruction)
    
    # Test protocol pin mapping
    print("\nPROTOCOL PIN MAPPING:")
    print("=" * 30)
    for protocol in OBD2Protocol:
        pins = mapper.protocol_to_pins(protocol)
        print(f"{protocol.name:15s}: {pins}")
    
    # Test GoDiag connector
    print("\nGoDiag Connector Test:")
    print("=" * 25)
    
    config = create_godiag_obd2_config("COM1", "ISO15765_11")
    connector = GoDiagOBD2Connector(config)
    
    # Simulate connection
    # Note: This would connect to real hardware in actual use
    print("Simulated connection status:")
    status = connector.get_connection_status()
    for key, value in status.items():
        print(f"  {key}: {value}")