#!/usr/bin/env python3
"""
J2534 PassThru Protocol Handler with OBD2 16-Pin Direct Connection
Supports J2534 devices for UDS/ISO 14229 diagnostics
"""

import logging
import time
import ctypes
from ctypes import c_ulong, c_void_p, byref, POINTER, create_string_buffer
from typing import Optional, List, Dict
from enum import Enum
from abc import ABC, abstractmethod
import os

logger = logging.getLogger(__name__)

# --- J2534 Standard Enums and Structures ---

class J2534Protocol(Enum):
    """J2534 Protocol IDs"""
    J1850_PWM = 1
    J1850_VPW = 2
    ISO9141 = 3
    ISO14230 = 4
    CAN = 5
    ISO15765 = 6
    ISO14229_UDS = 7

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

class J2534FilterType(Enum):
    PASS_FILTER = 0x00000001
    BLOCK_FILTER = 0x00000002
    FLOW_CONTROL_FILTER = 0x00000003

class PASSTHRU_MSG(ctypes.Structure):
    """J2534 Message Structure for ctypes"""
    _fields_ = [
        ("ProtocolID", c_ulong),
        ("RxStatus", c_ulong),
        ("TxFlags", c_ulong),
        ("Timestamp", c_ulong),
        ("DataSize", c_ulong),
        ("ExtraDataIndex", c_ulong),
        ("pData", POINTER(ctypes.c_ubyte)),
    ]

class J2534Message:
    """Python-friendly J2534 Message structure"""
    def __init__(self, protocol: J2534Protocol, tx_flags: int = 0, data: bytes = b''):
        self.protocol = protocol
        self.tx_flags = tx_flags
        self.rx_status = 0
        self.timestamp = 0
        self.data = data

# --- Abstract Base Class ---

class J2534PassThru(ABC):
    """Abstract J2534 PassThru interface"""
    @abstractmethod
    def open(self) -> bool: pass
    @abstractmethod
    def close(self) -> bool: pass
    @abstractmethod
    def connect(self, protocol: J2534Protocol, flags: int = 0, baudrate: int = 500000) -> int: pass
    @abstractmethod
    def disconnect(self, channel_id: int) -> bool: pass
    @abstractmethod
    def send_message(self, channel_id: int, message: J2534Message, timeout_ms: int = 1000) -> bool: pass
    @abstractmethod
    def read_message(self, channel_id: int, timeout_ms: int = 1000) -> Optional[J2534Message]: pass
    @abstractmethod
    def is_connected(self) -> bool: pass
    @abstractmethod
    def get_last_error(self) -> str: pass

# --- Real J2534 Implementation ---

    def __init__(self, dll_path: Optional[str] = None, **kwargs):
        self._is_open = False
        self.channels: Dict[int, J2534Protocol] = {}
        self.dll_handle = None
        self.device_id = c_ulong(0)
        self.dll_path = dll_path
        self.init_error = None
        if self.dll_path:
            self._load_driver(self.dll_path)

    def _load_driver(self, dll_path: str):
        """Load J2534 driver DLL"""
        try:
            if os.path.exists(dll_path):
                self.dll_handle = ctypes.windll.LoadLibrary(dll_path)
                self._define_api_prototypes()
                logger.info(f"Loaded J2534 driver from {dll_path}")
            else:
                msg = f"J2534 driver not found at {dll_path}"
                logger.error(msg)
                self.init_error = msg
        except OSError as e:
            if hasattr(e, 'winerror') and e.winerror == 193:
                import platform
                arch = platform.architecture()[0]
                msg = f"Architecture Mismatch: Driver is 32-bit but Python is {arch}. Please use 32-bit Python."
                logger.critical(f"ARCHITECTURE MISMATCH: Failed to load driver {dll_path}.")
                logger.critical(f"Current Python is {arch}, but the driver appears to be incompatible (likely 32-bit).")
                logger.critical("SOLUTION: Please run this application using a 32-bit Python interpreter.")
                self.init_error = msg
            else:
                msg = f"Failed to load J2534 driver: {e}"
                logger.error(f"{msg} from {dll_path}")
                self.init_error = msg
            self.dll_handle = None
        except Exception as e:
            msg = f"Failed to load J2534 driver: {e}"
            logger.error(f"{msg} from {dll_path}")
            self.init_error = msg
            self.dll_handle = None

    @staticmethod
    def scan_local_drivers(drivers_dir: str) -> List[str]:
        """Scan a directory for DLL files, including common system paths"""
        dlls = []
        
        # 1. Scan local drivers folder
        if os.path.exists(drivers_dir):
            for root, dirs, files in os.walk(drivers_dir):
                for file in files:
                    if file.lower().endswith(".dll"):
                        dlls.append(os.path.join(root, file))
        
        # 2. Check common system locations for popular VCIs
        common_paths = [
            r"C:\Program Files (x86)\Scanmatik\sm2j2534.dll",
            r"C:\Program Files\Scanmatik\sm2j2534.dll",
            r"C:\Program Files (x86)\Godiag\J2534\Godiag_J2534.dll",
            r"C:\Program Files\Godiag\J2534\Godiag_J2534.dll"
        ]
        
        for path in common_paths:
            if os.path.exists(path) and path not in dlls:
                dlls.append(path)
                
        return dlls

    def _define_api_prototypes(self):
        """Define ctypes function prototypes for the J2534 API"""
        if not self.dll_handle: return
        self.dll_handle.PassThruOpen.argtypes = [c_void_p, POINTER(c_ulong)]
        self.dll_handle.PassThruOpen.restype = c_ulong
        self.dll_handle.PassThruClose.argtypes = [c_ulong]
        self.dll_handle.PassThruClose.restype = c_ulong
        self.dll_handle.PassThruConnect.argtypes = [c_ulong, c_ulong, c_ulong, c_ulong, POINTER(c_ulong)]
        self.dll_handle.PassThruConnect.restype = c_ulong
        self.dll_handle.PassThruDisconnect.argtypes = [c_ulong]
        self.dll_handle.PassThruDisconnect.restype = c_ulong
        self.dll_handle.PassThruWriteMsgs.argtypes = [c_ulong, POINTER(PASSTHRU_MSG), POINTER(c_ulong), c_ulong]
        self.dll_handle.PassThruWriteMsgs.restype = c_ulong
        self.dll_handle.PassThruReadMsgs.argtypes = [c_ulong, POINTER(PASSTHRU_MSG), POINTER(c_ulong), c_ulong]
        self.dll_handle.PassThruReadMsgs.restype = c_ulong
        self.dll_handle.PassThruStartMsgFilter.argtypes = [c_ulong, c_ulong, POINTER(PASSTHRU_MSG), POINTER(PASSTHRU_MSG), POINTER(PASSTHRU_MSG), POINTER(c_ulong)]
        self.dll_handle.PassThruStartMsgFilter.restype = c_ulong
        self.dll_handle.PassThruStopMsgFilter.argtypes = [c_ulong, c_ulong]
        self.dll_handle.PassThruStopMsgFilter.restype = c_ulong
        self.dll_handle.PassThruGetLastError.argtypes = [POINTER(ctypes.c_char * 80)]
        self.dll_handle.PassThruGetLastError.restype = c_ulong

    def open(self) -> bool:
        if not self.dll_handle:
            logger.error("J2534 driver not loaded. Cannot open device.")
            return False
        if self._is_open:
            return True
        
        try:
            # Add timeout protection for DLL operations
            import threading
            
            def open_device():
                return self.dll_handle.PassThruOpen(None, byref(self.device_id))
            
            # Use a thread with timeout to prevent hanging
            result = [None]
            def target():
                result[0] = open_device()
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout=5.0)  # 5 second timeout
            
            if thread.is_alive():
                logger.error("J2534 device open operation timed out after 5 seconds")
                return False
            
            status = result[0]
            if status == J2534Status.NOERROR.value:
                self._is_open = True
                logger.info(f"J2534 device opened successfully with DeviceID: {self.device_id.value}")
                return True
            else:
                logger.error(f"Failed to open J2534 device. Status: {status}. Error: {self.get_last_error()}")
                return False
                
        except Exception as e:
            logger.error(f"J2534 device open failed with exception: {e}")
            return False

    def close(self) -> bool:
        if not self._is_open:
            return True
        
        for channel_id in list(self.channels.keys()):
            self.disconnect(channel_id)
            
        status = self.dll_handle.PassThruClose(self.device_id)
        if status == J2534Status.NOERROR.value:
            self._is_open = False
            self.device_id = c_ulong(0)
            logger.info("J2534 device closed successfully.")
            return True
        else:
            logger.error(f"Failed to close J2534 device. Status: {status}. Error: {self.get_last_error()}")
            return False

    def connect(self, protocol: J2534Protocol, flags: int = 0, baudrate: int = 500000) -> int:
        if not self._is_open:
            logger.error("Device not open. Cannot connect to protocol.")
            return -1
            
        try:
            channel_id = c_ulong(0)
            
            # Add timeout protection for connect operation
            def connect_device():
                return self.dll_handle.PassThruConnect(self.device_id, protocol.value, flags, baudrate, byref(channel_id))
            
            import threading
            result = [None]
            def target():
                result[0] = connect_device()
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout=10.0)  # 10 second timeout for connection
            
            if thread.is_alive():
                logger.error(f"J2534 connection to {protocol.name} timed out after 10 seconds")
                return -1
            
            status = result[0]
            if status == J2534Status.NOERROR.value:
                self.channels[channel_id.value] = protocol
                logger.info(f"Connected to {protocol.name} on ChannelID: {channel_id.value}")
                return channel_id.value
            else:
                logger.error(f"Failed to connect to {protocol.name}. Status: {status}. Error: {self.get_last_error()}")
                return -1
                
        except Exception as e:
            logger.error(f"J2534 connection failed with exception: {e}")
            return -1

    def disconnect(self, channel_id: int) -> bool:
        if channel_id not in self.channels:
            logger.warning(f"Channel {channel_id} not connected or already disconnected.")
            return True
            
        status = self.dll_handle.PassThruDisconnect(channel_id)
        if status == J2534Status.NOERROR.value:
            del self.channels[channel_id]
            logger.info(f"Disconnected ChannelID: {channel_id}")
            return True
        else:
            logger.error(f"Failed to disconnect ChannelID {channel_id}. Status: {status}. Error: {self.get_last_error()}")
            return False

    def start_msg_filter(self, channel_id: int, filter_type: J2534FilterType, mask: Optional[J2534Message], pattern: Optional[J2534Message], flow_control: Optional[J2534Message] = None) -> int:
        if channel_id not in self.channels:
            logger.error(f"Cannot start filter: Invalid channel {channel_id}")
            return -1

        # Helper to convert J2534Message to PASSTHRU_MSG
        def to_struct(msg: Optional[J2534Message]) -> POINTER(PASSTHRU_MSG):
            if not msg:
                return None
            data_buffer = create_string_buffer(msg.data)
            struct = PASSTHRU_MSG(
                ProtocolID=msg.protocol.value,
                TxFlags=msg.tx_flags,
                DataSize=len(msg.data),
                pData=ctypes.cast(data_buffer, POINTER(ctypes.c_ubyte))
            )
            return byref(struct)

        p_mask = to_struct(mask)
        p_pattern = to_struct(pattern)
        p_flow = to_struct(flow_control)
        
        filter_id = c_ulong(0)
        
        status = self.dll_handle.PassThruStartMsgFilter(channel_id, filter_type.value, p_mask, p_pattern, p_flow, byref(filter_id))
        
        if status == J2534Status.NOERROR.value:
            logger.info(f"Started Filter ID: {filter_id.value} on Channel {channel_id}")
            return filter_id.value
        else:
            logger.error(f"Failed to start filter. Status: {status}. Error: {self.get_last_error()}")
            return -1

    def stop_msg_filter(self, channel_id: int, filter_id: int) -> bool:
        if channel_id not in self.channels:
            return False
            
        status = self.dll_handle.PassThruStopMsgFilter(channel_id, filter_id)
        if status == J2534Status.NOERROR.value:
            logger.info(f"Stopped Filter ID: {filter_id}")
            return True
        else:
            logger.error(f"Failed to stop filter. Status: {status}. Error: {self.get_last_error()}")
            return False


    def send_message(self, channel_id: int, message: J2534Message, timeout_ms: int = 1000) -> bool:
        if channel_id not in self.channels:
            logger.error(f"Cannot send message: Invalid channel {channel_id}")
            return False

        # The data must be mutable for the C function
        data_buffer = create_string_buffer(message.data)
        
        msg = PASSTHRU_MSG(
            ProtocolID=message.protocol.value,
            TxFlags=message.tx_flags,
            DataSize=len(message.data),
            pData=ctypes.cast(data_buffer, POINTER(ctypes.c_ubyte))
        )
        num_msgs = c_ulong(1)
        
        status = self.dll_handle.PassThruWriteMsgs(channel_id, byref(msg), byref(num_msgs), timeout_ms)
        
        if status == J2534Status.NOERROR.value:
            logger.debug(f"Sent {len(message.data)} bytes on channel {channel_id}: {message.data.hex()}")
            return True
        else:
            logger.error(f"Failed to write message. Status: {status}. Error: {self.get_last_error()}")
            return False

    def read_message(self, channel_id: int, timeout_ms: int = 1000) -> Optional[J2534Message]:
        if channel_id not in self.channels:
            logger.error(f"Cannot read message: Invalid channel {channel_id}")
            return None

        # Create a buffer for the message data. 4096 is a standard J2534 buffer size.
        data_buffer = create_string_buffer(4096)
        
        msg = PASSTHRU_MSG(
            ProtocolID=self.channels[channel_id].value,
            pData=ctypes.cast(data_buffer, POINTER(ctypes.c_ubyte))
        )
        num_msgs = c_ulong(1)
        
        status = self.dll_handle.PassThruReadMsgs(channel_id, byref(msg), byref(num_msgs), timeout_ms)
        
        if status == J2534Status.NOERROR.value and num_msgs.value > 0:
            read_msg = msg
            # Correctly slice the data from the buffer
            data = data_buffer.raw[0:read_msg.DataSize]
            
            py_msg = J2534Message(
                protocol=J2534Protocol(read_msg.ProtocolID),
                data=data
            )
            py_msg.rx_status = read_msg.RxStatus
            py_msg.timestamp = read_msg.Timestamp
            
            logger.debug(f"Read {len(data)} bytes on channel {channel_id}: {data.hex()}")
            return py_msg
        elif status != J2534Status.TIMEOUT.value:
            # Only log errors that are not timeouts
            logger.error(f"Failed to read message. Status: {status}. Error: {self.get_last_error()}")
            
        return None

    def is_connected(self) -> bool:
        return self._is_open and len(self.channels) > 0

    def get_last_error(self) -> str:
        if not self.dll_handle:
            return "J2534 driver not loaded."
        error_desc = create_string_buffer(80)
        self.dll_handle.PassThruGetLastError(byref(error_desc))
        return error_desc.value.decode('ascii', errors='ignore').strip()

# --- Mock Implementation for Testing ---

class MockJ2534PassThru(J2534PassThru):
    """Mock J2534 PassThru for testing without hardware"""
    def __init__(self, **kwargs):
        self._is_open = False
        self.channels: Dict[int, J2534Protocol] = {}
        self.next_channel_id = 1
        logger.info("Initialized mock J2534 device.")
    def open(self) -> bool: self._is_open = True; logger.info("Mock device opened."); return True
    def close(self) -> bool: self._is_open = False; self.channels.clear(); logger.info("Mock device closed."); return True
    def connect(self, protocol: J2534Protocol, **kwargs) -> int:
        if not self._is_open: return -1
        channel_id = self.next_channel_id
        self.channels[channel_id] = protocol
        self.next_channel_id += 1
        logger.info(f"Mock connected to {protocol.name} on channel {channel_id}")
        return channel_id
    def disconnect(self, channel_id: int) -> bool:
        if channel_id in self.channels: del self.channels[channel_id]; logger.info(f"Mock disconnected channel {channel_id}"); return True
        return False
    def send_message(self, channel_id: int, message: J2534Message, **kwargs) -> bool: 
        logger.debug(f"Mock sent: {message.data.hex()}")
        return True
    def read_message(self, channel_id: int, **kwargs) -> Optional[J2534Message]: 
        logger.debug("Mock read returning None.")
        return None
    def is_connected(self) -> bool: return self._is_open and len(self.channels) > 0
    def get_last_error(self) -> str: return "No error in mock device."

# --- Factory Function ---

def get_passthru_device(dll_path: Optional[str] = None, mock_mode: bool = False, **kwargs) -> J2534PassThru:
    """Factory function to get J2534 PassThru device"""
    # If a specific DLL path is provided, we use the real implementation (checking for existence first)
    if dll_path and os.path.exists(dll_path):
        logger.info(f"Using real J2534 PassThru device via DLL: {dll_path}")
        return J2534PassThru(dll_path=dll_path, **kwargs)
        
    if mock_mode:
        logger.info("Using Mock J2534 PassThru device.")
        return MockJ2534PassThru(**kwargs)
    
    # If no path and mock_mode is False, we typically can't do much unless we default to something.
    # But for backward compatibility with existing calls:
    logger.info("No DLL path provided. Defaulting to J2534PassThru (empty init).")
    return J2534PassThru(dll_path=None, **kwargs)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # --- Real Device Test ---
    # Set mock_mode=False to test with the actual GODIAG_PT32.dll
    print("--- Starting Real J2534 Device Test ---")
    device = get_passthru_device(mock_mode=False)
    
    if device.open():
        print("Device opened successfully.")
        # Connect to ISO15765 protocol (standard for modern CAN diagnostics)
        channel = device.connect(protocol=J2534Protocol.ISO15765, baudrate=500000)
        
        if channel > 0:
            print(f"Connected to channel {channel}.")
            # Example: Send a UDS request for VIN (Service 0x22, DID 0xF190)
            # This requires a CAN ID, which depends on the vehicle. Using a common diagnostic request ID 0x7DF.
            can_id = b'\x00\x00\x07\xDF'
            uds_request = b'\x02\x22\xF1\x90' # Length=2, Service=22, DID=F190
            
            # J2534 message data for ISO15765 includes the CAN ID as the first 4 bytes.
            msg_data = can_id + uds_request
            
            msg = J2534Message(J2534Protocol.ISO15765, data=msg_data)
            
            if device.send_message(channel, msg):
                print(f"Sent VIN request: {msg_data.hex()}")
                print("Reading response...")
                
                # Loop to read potential multi-frame responses or wait for a single response
                start_time = time.time()
                vin_parts = []
                full_vin = ""
                
                while time.time() - start_time < 5: # 5 second timeout for response
                    response = device.read_message(channel, timeout_ms=500)
                    if response:
                        # The response data also includes the CAN ID. The actual UDS data follows.
                        # Response ID is typically Request ID + 8 (e.g., 0x7E8 for a 0x7E0 request)
                        response_can_id = response.data[:4]
                        response_uds_data = response.data[4:]
                        print(f"Received response: {response_uds_data.hex()} from CAN ID {response_can_id.hex()}")

                        # Check for a positive response to ReadDataByIdentifier (0x62)
                        if response_uds_data.startswith(b'\x62\xF1\x90'): # Single frame response
                            vin_bytes = response_uds_data[3:]
                            full_vin = vin_bytes.decode('ascii', errors='ignore')
                            print(f"SUCCESS: Decoded VIN: {full_vin}")
                            break
                        # Check for multi-frame response (First Frame = 0x10)
                        elif response_uds_data.startswith(b'\x10'):
                            # This is the first frame of a multi-frame response
                            total_len = int.from_bytes(response_uds_data[0:2], 'big') & 0x0FFF
                            vin_parts.append(response_uds_data[3:])
                            # We would need to send a Flow Control message here, but for simplicity, we just keep reading
                            print("Multi-frame response started. Reading subsequent frames...")
                        # Check for consecutive frames (starts with 0x2x)
                        elif response_uds_data[0] & 0xF0 == 0x20:
                             vin_parts.append(response_uds_data[1:])
                             # If we have all parts, assemble the VIN
                             assembled_data = b''.join(vin_parts)
                             if len(assembled_data) >= 17: # A VIN is 17 chars
                                 full_vin = assembled_data[:17].decode('ascii', errors='ignore')
                                 print(f"SUCCESS: Assembled VIN from multi-frame: {full_vin}")
                                 break
                    else:
                        time.sleep(0.1) # Wait a bit before polling again
                
                if not full_vin:
                    print("Failed to get a complete VIN response.")

            else:
                print("Failed to send VIN request.")

            device.disconnect(channel)
            print("Disconnected from channel.")
        
        device.close()
        print("Device closed.")
    else:
        print("Failed to open J2534 device. Check driver installation and device connection.")
    
    print("--- Real J2534 Device Test Finished ---")
