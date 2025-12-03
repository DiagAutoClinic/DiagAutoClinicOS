#!/usr/bin/env python3
"""
J2534 PassThru Protocol Handler with OBD2 16-Pin Direct Connection
Supports GoDiag GD101 and compatible J2534 devices for UDS/ISO 14229 diagnostics
Direct connection to OBD2 16-pin connector with proper pinout configuration
"""

import logging
import time
from typing import Optional, List, Tuple, Dict
from enum import Enum
from abc import ABC, abstractmethod

# Import OBD2 configuration
from .godiag_gd101_obd2_config import (
    OBD2Pin, OBD2Protocol, GoDiagOBD2Config,
    GoDiagOBD2Connector, OBD2PinMapper, create_godiag_obd2_config
)

logger = logging.getLogger(__name__)


class J2534Protocol(Enum):
    """J2534 Protocol IDs"""
    J1850_PWM = 1
    J1850_VPW = 2
    ISO9141 = 3
    ISO14230 = 4
    CAN = 5
    ISO15765 = 6
    ISO14229_UDS = 7  # UDS over CAN/ISO-TP


class J2534Status(Enum):
    """J2534 Status codes"""
    NOERROR = 0x00
    NOT_SUPPORTED = 0x01
    INVALID_CHANNEL_ID = 0x02
    INVALID_PROTOCOL_ID = 0x03
    NULL_PARAMETER = 0x04
    INVALID_IOCTL_ID = 0x05
    DEVICE_IN_USE = 0x06
    INVALID_MESSAGE_ID = 0x07
    INVALID_ERROR_ID = 0x08
    INVALID_MESSAGE_LENGTH = 0x09
    DEVICE_NOT_CONNECTED = 0x0A
    TIMEOUT = 0x0B
    INVALID_MESSAGE = 0x0C
    UNKNOWN_ERROR = 0xFF


class J2534Message:
    """J2534 Message structure"""
    
    def __init__(self, protocol: J2534Protocol, tx_flags: int = 0, data: bytes = b''):
        self.protocol = protocol
        self.tx_flags = tx_flags
        self.rx_status = 0
        self.timestamp = 0
        self.data = data
        self.extra_data = b''
    
    def to_bytes(self) -> bytes:
        """Convert message to bytes"""
        return self.data + self.extra_data
    
    @staticmethod
    def from_bytes(data: bytes, protocol: J2534Protocol) -> 'J2534Message':
        """Create message from bytes"""
        msg = J2534Message(protocol)
        msg.data = data
        return msg


class J2534PassThru(ABC):
    """Abstract J2534 PassThru interface"""
    
    @abstractmethod
    def open(self) -> bool:
        """Open device connection"""
        pass
    
    @abstractmethod
    def close(self) -> bool:
        """Close device connection"""
        pass
    
    @abstractmethod
    def connect(self, protocol: J2534Protocol, flags: int = 0) -> int:
        """Connect to protocol (returns channel ID)"""
        pass
    
    @abstractmethod
    def disconnect(self, channel_id: int) -> bool:
        """Disconnect from protocol"""
        pass
    
    @abstractmethod
    def send_message(self, channel_id: int, message: J2534Message, timeout_ms: int = 1000) -> bool:
        """Send message on channel"""
        pass
    
    @abstractmethod
    def read_message(self, channel_id: int, timeout_ms: int = 1000) -> Optional[J2534Message]:
        """Read message from channel"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if device is connected"""
        pass


class MockJ2534PassThru(J2534PassThru):
    """Mock J2534 PassThru for testing"""
    
    def __init__(self, device_name: str = "Mock GoDiag GD101"):
        self.device_name = device_name
        self._is_connected = False
        self._is_open = False
        self.channels: Dict[int, J2534Protocol] = {}
        self.next_channel_id = 1
        logger.info(f"Initialized mock J2534 device: {device_name}")
    
    def open(self) -> bool:
        """Open mock device"""
        self._is_open = True
        logger.debug(f"[MOCK] Opened device {self.device_name}")
        return True
    
    def close(self) -> bool:
        """Close mock device"""
        self._is_open = False
        self.channels.clear()
        logger.debug(f"[MOCK] Closed device {self.device_name}")
        return True
    
    def connect(self, protocol: J2534Protocol, flags: int = 0) -> int:
        """Connect to protocol (mock)"""
        if not self._is_open:
            logger.error("Device not open")
            return -1
        
        channel_id = self.next_channel_id
        self.channels[channel_id] = protocol
        self.next_channel_id += 1
        self._is_connected = True
        
        logger.debug(f"[MOCK] Connected to {protocol.name} on channel {channel_id}")
        return channel_id
    
    def disconnect(self, channel_id: int) -> bool:
        """Disconnect from protocol"""
        if channel_id in self.channels:
            del self.channels[channel_id]
            if not self.channels:
                self._is_connected = False
            logger.debug(f"[MOCK] Disconnected channel {channel_id}")
            return True
        return False
    
    def send_message(self, channel_id: int, message: J2534Message, timeout_ms: int = 1000) -> bool:
        """Send message (mock)"""
        if not self._is_connected or channel_id not in self.channels:
            logger.error(f"Invalid channel {channel_id}")
            return False
        
        logger.debug(f"[MOCK] Sent {len(message.data)} bytes on channel {channel_id}: {message.data.hex()}")
        return True
    
    def read_message(self, channel_id: int, timeout_ms: int = 1000) -> Optional[J2534Message]:
        """Read message (mock)"""
        if not self._is_connected or channel_id not in self.channels:
            return None
        
        # Return mock responses based on protocol
        protocol = self.channels[channel_id]
        
        if protocol == J2534Protocol.ISO14229_UDS or protocol == J2534Protocol.CAN:
            # Mock UDS responses - randomly return VIN, DTC scan, or DTC clear response
            import random
            response_type = random.choice(['vin', 'dtc_scan', 'dtc_clear'])
            
            if response_type == 'vin':
                # 0x62 = positive response to 0x22 (ReadDataByIdentifier)
                mock_response = b'\x62\xF1\x90WVWZZZ3CZ7E123456'
            elif response_type == 'dtc_scan':
                # 0x59 = positive response to 0x19 (ReadDTCInformation)
                # Format: P0300 (0x030000) + status 0x08
                mock_response = b'\x59\x01\x03\x00\x00\x08\x03\x01\x00\x08'
            else:  # dtc_clear
                # 0x54 = positive response to 0x14 (ClearDiagnosticInformation)
                mock_response = b'\x54'
            
            msg = J2534Message(protocol, data=mock_response)
            logger.debug(f"[MOCK] Read {len(mock_response)} bytes on channel {channel_id}")
            return msg
        
        return None
    
    def is_connected(self) -> bool:
        """Check mock connection status"""
        return self._is_connected


class GoDiagGD101PassThru(J2534PassThru):
    """Real GoDiag GD101 J2534 PassThru with OBD2 16-Pin Direct Connection"""
    
    def __init__(self, port: str = "COM1", baudrate: int = 115200, obd2_protocol: str = "ISO15765_11"):
        self.port = port
        self.baudrate = baudrate
        self._is_connected = False
        self._is_open = False
        self.channels: Dict[int, J2534Protocol] = {}
        self.next_channel_id = 1
        self.serial_conn = None
        
        # Initialize OBD2 16-pin connector
        self.obd2_config = create_godiag_obd2_config(port, obd2_protocol)
        self.obd2_connector = GoDiagOBD2Connector(self.obd2_config)
        
        try:
            import serial
            self.serial = serial
        except ImportError:
            logger.warning("pyserial not available - GoDiag GD101 will not work")
            self.serial = None
    
    def open(self) -> bool:
        """Open GoDiag GD101 device with OBD2 16-Pin connection"""
        try:
            if not self.serial:
                logger.error("Serial module not available")
                return False
            
            # Connect to OBD2 16-pin port
            logger.info("Establishing OBD2 16-pin connection...")
            obd2_success = self.obd2_connector.connect_obd2_port(self.port)
            
            if not obd2_success:
                logger.error("Failed to establish OBD2 16-pin connection")
                return False
            
            # Open serial connection to GoDiag GD101
            self.serial_conn = self.serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=2
            )
            
            # Send initialization command
            self._send_command(b'\x00\x01')  # Init GoDiag
            time.sleep(0.5)
            
            self._is_open = True
            logger.info(f"Opened GoDiag GD101 on {self.port} with OBD2 16-Pin connection")
            
            # Log connection details
            status = self.obd2_connector.get_connection_status()
            logger.info(f"OBD2 Status: Protocol={status['protocol']}, Required Pins={status['required_pins']}")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to open GoDiag GD101: {e}")
            return False
    
    def close(self) -> bool:
        """Close GoDiag GD101 device and OBD2 connection"""
        try:
            # Disconnect OBD2 connection first
            if hasattr(self, 'obd2_connector') and self.obd2_connector:
                self.obd2_connector.disconnect_obd2_port()
            
            if self.serial_conn:
                self._send_command(b'\x00\x02')  # Close GoDiag
                self.serial_conn.close()
            
            self._is_open = False
            self._is_connected = False
            self.channels.clear()
            logger.info("Closed GoDiag GD101 and OBD2 16-Pin connection")
            return True
        
        except Exception as e:
            logger.error(f"Error closing GoDiag GD101: {e}")
            return False
    
    def connect(self, protocol: J2534Protocol, flags: int = 0) -> int:
        """Connect to protocol via GoDiag"""
        try:
            if not self._is_open:
                logger.error("Device not open")
                return -1
            
            # Map J2534 protocol to GoDiag protocol ID
            protocol_map = {
                J2534Protocol.ISO14229_UDS: 0x14,
                J2534Protocol.CAN: 0x05,
                J2534Protocol.ISO15765: 0x06,
                J2534Protocol.ISO14230: 0x04,
            }
            
            gd_proto = protocol_map.get(protocol, 0xFF)
            
            # Send connect command to GoDiag
            cmd = bytes([0x01, gd_proto, flags >> 8, flags & 0xFF])
            response = self._send_command(cmd)
            
            if response and response[0] == 0x00:  # Success
                channel_id = self.next_channel_id
                self.channels[channel_id] = protocol
                self.next_channel_id += 1
                self._is_connected = True
                
                logger.info(f"Connected to {protocol.name} on channel {channel_id}")
                return channel_id
            else:
                logger.error(f"Failed to connect to {protocol.name}")
                return -1
        
        except Exception as e:
            logger.error(f"Connect error: {e}")
            return -1
    
    def disconnect(self, channel_id: int) -> bool:
        """Disconnect from protocol"""
        try:
            if channel_id in self.channels:
                cmd = bytes([0x02, channel_id])
                response = self._send_command(cmd)
                
                if response and response[0] == 0x00:
                    del self.channels[channel_id]
                    if not self.channels:
                        self._is_connected = False
                    logger.debug(f"Disconnected channel {channel_id}")
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
            return False
    
    def send_message(self, channel_id: int, message: J2534Message, timeout_ms: int = 1000) -> bool:
        """Send message via GoDiag"""
        try:
            if not self._is_connected or channel_id not in self.channels:
                logger.error(f"Invalid channel {channel_id}")
                return False
            
            # Build GoDiag message frame
            data = message.to_bytes()
            cmd = bytes([0x03, channel_id]) + bytes([len(data) >> 8, len(data) & 0xFF]) + data
            
            response = self._send_command(cmd, timeout_ms=timeout_ms)
            
            if response and response[0] == 0x00:
                logger.debug(f"Sent {len(data)} bytes on channel {channel_id}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Send error: {e}")
            return False
    
    def read_message(self, channel_id: int, timeout_ms: int = 1000) -> Optional[J2534Message]:
        """Read message from GoDiag"""
        try:
            if not self._is_connected or channel_id not in self.channels:
                return None
            
            cmd = bytes([0x04, channel_id])
            start_time = time.time()
            
            while (time.time() - start_time) * 1000 < timeout_ms:
                response = self._send_command(cmd, timeout_ms=100)
                
                if response and len(response) > 3:
                    status = response[0]
                    data_len = (response[1] << 8) | response[2]
                    data = response[3:3 + data_len]
                    
                    msg = J2534Message(self.channels[channel_id], data=data)
                    msg.rx_status = status
                    logger.debug(f"Read {len(data)} bytes on channel {channel_id}")
                    return msg
                
                time.sleep(0.01)
            
            return None
        
        except Exception as e:
            logger.error(f"Read error: {e}")
            return None
    
    def is_connected(self) -> bool:
        """Check connection status"""
        return self._is_connected
    
    def _send_command(self, cmd: bytes, timeout_ms: int = 1000) -> Optional[bytes]:
        """Send command to GoDiag and receive response"""
        try:
            if not self.serial_conn or not self.serial_conn.is_open:
                return None
            
            # Send command
            self.serial_conn.write(cmd)
            self.serial_conn.flush()
            
            # Read response
            start_time = time.time()
            response = b''
            
            while (time.time() - start_time) * 1000 < timeout_ms:
                if self.serial_conn.in_waiting:
                    response += self.serial_conn.read(self.serial_conn.in_waiting)
                    break
                time.sleep(0.01)
            
            return response if response else None
        
        except Exception as e:
            logger.error(f"Command error: {e}")
            return None
    def get_obd2_status(self) -> Dict:
        """Get OBD2 16-pin connection status"""
        if hasattr(self, 'obd2_connector') and self.obd2_connector:
            return self.obd2_connector.get_connection_status()
        return {'connected': False, 'protocol': None}
    
    def validate_obd2_connection(self) -> Tuple[bool, List[str]]:
        """Validate OBD2 16-pin connection setup"""
        if hasattr(self, 'obd2_connector') and self.obd2_connector:
            return self.obd2_connector.pin_mapper.validate_godiag_connection()
        return False, ["OBD2 connector not initialized"]
    
    def get_obd2_pin_instructions(self) -> List[str]:
        """Get step-by-step OBD2 pin connection instructions"""
        if hasattr(self, 'obd2_connector') and self.obd2_connector:
            return self.obd2_connector.pin_mapper.get_connection_instructions()
        return ["OBD2 connector not initialized"]
    
    def auto_detect_protocol(self) -> bool:
        """Auto-detect OBD2 protocol from vehicle"""
        if hasattr(self, 'obd2_connector') and self.obd2_connector:
            detected_protocol = self.obd2_connector.auto_detect_protocol()
            logger.info(f"Auto-detected OBD2 protocol: {detected_protocol.name}")
            return True
        return False


def get_passthru_device(mock_mode: bool = True, device_name: str = "GoDiag GD101", 
                       port: str = "COM1") -> J2534PassThru:
    """Factory function to get J2534 PassThru device"""
    if mock_mode:
        return MockJ2534PassThru(device_name)
    else:
        return GoDiagGD101PassThru(port)


if __name__ == "__main__":
    # Test mock device
    logging.basicConfig(level=logging.DEBUG)
    
    device = get_passthru_device(mock_mode=True)
    
    if device.open():
        channel = device.connect(J2534Protocol.ISO14229_UDS)
        
        if channel > 0:
            # Send mock UDS request
            msg = J2534Message(J2534Protocol.ISO14229_UDS, data=b'\x22\xF1\x90')
            if device.send_message(channel, msg):
                # Read response
                response = device.read_message(channel)
                if response:
                    print(f"Response: {response.data.hex()}")
            
            device.disconnect(channel)
        
        device.close()
