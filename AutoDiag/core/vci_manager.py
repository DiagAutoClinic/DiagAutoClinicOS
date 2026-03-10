import atexit
import logging
import threading
import time
import os
import sys
from typing import List, Dict, Any, Optional, Callable
from enum import Enum

# Import J2534 and ISO-TP support
try:
    from shared.j2534_passthru import J2534PassThru, J2534Protocol, J2534Message, get_passthru_device
    from shared.isotp_handler import IsoTpHandler
    from AutoDiag.core.j2534_bridge_client import J2534BridgeClient
except ImportError:
    # Fallback/Mock for environment without shared modules (e.g. testing)
    pass

# Optional Qt signal support
try:
    from PyQt6.QtCore import pyqtSignal, QObject
    HAS_QT = True
except ImportError:
    HAS_QT = False

logger = logging.getLogger(__name__)

class VCITypes(Enum):
    J2534 = "J2534"
    ELM327 = "ELM327"
    SIMULATOR = "SIMULATOR"

# --- HARDWARE REFERENCE: GODIAG GD101 ---
# Driver: GODIAG_PT32.dll (32-bit ONLY) - Requires Python 32-bit environment.
# Protocols: ISO15765 (CAN), ISO9141, ISO14230 (KWP), J1850 PWM/VPW.
# ELM327 Mode: Version 1.5a Command Set.
# Pinout:
#   - CAN High/Low: Pins 6/14 (Up to 1000Kbps)
#   - K-Line: Pins 7/15 (ISO9141/ISO14230)
#   - J1850 PWM: Pins 2/10
#   - J1850 VPW: Pin 2
#   - Prog Voltage: Pins 12 or 13 (Up to 20V)
#   - Short to GND: Pin 9 -> Pin 5


class VCIStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

class VCIDevice:
    def __init__(self, name: str, device_type: VCITypes, port: str = "", path: str = ""):
        self.name = name
        self.device_type = device_type
        self.port = port
        self.bluetooth_address = ""
        self.path = path # DLL path for J2534
        self.capabilities = ["can_bus", "iso15765", "dtc_read", "dtc_clear"]
        self._j2534_device: Optional[Any] = None
        self._obd_device = None

class HangWatchdog:
    """
    Simple watchdog to detect application hangs.
    Intended to run in a separate thread and monitor main thread responsiveness.
    """
    def __init__(self, check_interval: float = 5.0, timeout: float = 30.0):
        self.check_interval = check_interval
        self.timeout = timeout
        self.running = False
        self.last_heartbeat = time.time()
        self._thread = None
        
    def start_monitoring(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True, name="HangWatchdog")
        self._thread.start()
        
    def stop(self):
        self.running = False
        
    def heartbeat(self):
        """Call this from the main thread to indicate aliveness"""
        self.last_heartbeat = time.time()
        
    def _monitor_loop(self):
        while self.running:
            time.sleep(self.check_interval)
            if time.time() - self.last_heartbeat > self.timeout:
                logger.warning("Application hang detected! (No heartbeat received)")

class VCIManager:
    _instance = None
    
    @staticmethod
    def get_instance():
        if VCIManager._instance is None:
            VCIManager._instance = VCIManager()
        return VCIManager._instance

    def __init__(self):
        self.status = VCIStatus.DISCONNECTED
        self.connected_vci: Optional[VCIDevice] = None
        self.available_devices: List[VCIDevice] = []
        self.status_callbacks: List[Callable] = []
        self.is_scanning = False
        self.active_channel_id = None
        self.active_protocol_name = None
        
        # Register cleanup on exit to prevent zombie VCI handles
        atexit.register(self.disconnect)
        
    def add_status_callback(self, callback: Callable):
        if callback not in self.status_callbacks:
            self.status_callbacks.append(callback)
            
    def remove_status_callback(self, callback: Callable):
        if callback in self.status_callbacks:
            self.status_callbacks.remove(callback)
            
    def _notify_status(self, event: str, data: Any = None):
        # 1. Notify callbacks
        for callback in self.status_callbacks:
            try:
                callback(event, data)
            except Exception as e:
                logger.error(f"Error in status callback: {e}")

        # 2. Emit Signals (if Qt available)
        if HAS_QT:
            try:
                self.status_changed.emit(event, data)
                
                # Special mapping for devices_found
                if event == "scan_complete":
                    # data is the list of found devices
                    self.devices_found.emit(data)
            except Exception as e:
                logger.error(f"Signal emit error: {e}")

    def scan_for_devices(self, timeout: int = 15) -> bool:
        if self.is_scanning:
            return False
        
        self.is_scanning = True
        
        # NOTE: For Godiag GD101, we must prioritize J2534 scanning over Serial port scanning.
        # Serial scanning locks the COM port, preventing the J2534 driver from accessing it.
        # We start J2534 scan immediately.
        threading.Thread(target=self._scan_worker, args=(timeout,), daemon=True).start()
        return True

    def scan_for_devices_with_timeout(self, timeout: int = 15) -> List[VCIDevice]:
        started = self.scan_for_devices(timeout=timeout)
        start_time = time.time()

        if not started and not self.is_scanning:
            return list(self.available_devices)

        while self.is_scanning and (time.time() - start_time) < float(timeout):
            time.sleep(0.05)

        return list(self.available_devices)

    def get_scan_results(self) -> List[VCIDevice]:
        return list(self.available_devices)
        
    def _scan_worker(self, timeout: int):
        try:
            found_devices = []
            
            # 1. PRIORITY SCAN: J2534 Drivers (Crucial for GD101)
            # We must load J2534 drivers BEFORE any serial port operations occur.
            try:
                # Scan project-local drivers folder
                import os
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                drivers_dir = os.path.join(project_root, "drivers")
                
                drivers = J2534PassThru.scan_local_drivers(drivers_dir)
                
                # Add common paths
                extra_paths = [
                    r"C:\Program Files\Scanmatik\sm2j2534.dll",
                    r"C:\Program Files (x86)\Scanmatik\smj2534.dll", # Scanmatik 2 Pro (x86)
                    r"C:\Program Files (x86)\Scanmatik\sm2j2534.dll",
                    r"C:\Program Files (x86)\Godiag\J2534\Godiag_J2534.dll", # Godiag GD101
                    r"C:\Program Files\Godiag\J2534\Godiag_J2534.dll"
                ]
                for p in extra_paths:
                    if p not in drivers:
                        drivers.append(p)
                
                for dll in drivers:
                    if os.path.exists(dll):
                        name = os.path.basename(dll).replace(".dll", "")
                        vci = VCIDevice(f"J2534: {name}", VCITypes.J2534, path=dll)
                        vci.capabilities.append("j2534")
                        found_devices.append(vci)
                        
            except Exception as e:
                logger.error(f"Error scanning J2534 drivers: {e}")

            # 2. SECONDARY SCAN: Serial/ELM327 Devices
            # Only perform this IF we haven't found a J2534 device, or explicitly requested.
            # For now, we skip aggressive serial scanning to protect GD101 connectivity.
            # Only passive detection (list_ports) should be used here if implemented.
            
            self.available_devices = found_devices
            self._notify_status("scan_complete", found_devices)
            
        except Exception as e:
            logger.error(f"Scan worker error: {e}")
            self._notify_status("scan_error", str(e))
        finally:
            self.is_scanning = False

    def is_connected(self) -> bool:
        return self.status == VCIStatus.CONNECTED and self.connected_vci is not None

    def _get_python32_path(self) -> Optional[str]:
        """
        Locate a 32-bit Python interpreter for the J2534 Bridge.
        """
        # 1. Check local project venv (.venv32)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        venv32_python = os.path.join(project_root, ".venv32", "Scripts", "python.exe")
        if os.path.exists(venv32_python):
            return venv32_python
            
        # 2. Check py launcher for 3.10-32
        try:
            import subprocess
            result = subprocess.run(["py", "-3.10-32", "-c", "import sys; print(sys.executable)"], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
            
        return None

    def connect_to_device(self, device: VCIDevice) -> bool:
        if self.is_connected():
            self.disconnect()
            
        self.status = VCIStatus.CONNECTING
        self._notify_status("connecting", device)
        
        try:
            if device.device_type == VCITypes.J2534:
                try:
                    # Special Handling for GODIAG GD101 and Scanmatik on 64-bit Python
                    # Both often use 32-bit DLLs that require bridging
                    name_upper = device.name.upper()
                    path_upper = device.path.upper()
                    
                    is_godiag = "GODIAG" in name_upper or "GODIAG" in path_upper
                    is_scanmatik = "SCANMATIK" in name_upper or "SM2" in name_upper or "SM2" in path_upper or "SCANMATIK" in path_upper
                    
                    import platform
                    is_64bit = platform.architecture()[0] == '64bit'
                    
                    if (is_godiag or is_scanmatik) and is_64bit:
                        logger.info(f"Detected 32-bit VCI ({device.name}) on 64-bit system. Attempting to use J2534 Bridge...")
                        python32 = self._get_python32_path()
                        if python32:
                            try:
                                bridge = J2534BridgeClient(device.path, python32)
                                if bridge.open():
                                    device._j2534_device = bridge
                                    self.connected_vci = device
                                    self.status = VCIStatus.CONNECTED
                                    self._notify_status("connected", device)
                                    return True
                                else:
                                    logger.error(f"Bridge failed to open device: {bridge.get_last_error()}")
                            except Exception as e:
                                logger.error(f"Failed to start J2534 Bridge: {e}")
                        else:
                            logger.error("32-bit Python not found. Cannot use Godiag Bridge.")
                    
                    # Standard Connection (Direct Load)
                    passthru = get_passthru_device(device.path)
                    if passthru.open():
                         device._j2534_device = passthru
                         self.connected_vci = device
                         self.status = VCIStatus.CONNECTED
                         self._notify_status("connected", device)
                         return True
                    else:
                        error_msg = getattr(passthru, 'init_error', "Failed to open J2534 device (Driver load failed)")
                        logger.error(f"Failed to connect J2534: {error_msg}")
                        self.status = VCIStatus.ERROR
                        self._notify_status("connect_error", error_msg)
                        return False
                except Exception as e:
                     logger.error(f"Failed to connect J2534: {e}")
                     self.status = VCIStatus.ERROR
                     self._notify_status("connect_error", f"Connection Exception: {e}")
                     return False
                     
            self.status = VCIStatus.ERROR
            self._notify_status("connect_error", "Failed to connect")
            return False
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.status = VCIStatus.ERROR
            return False

    def disconnect(self) -> bool:
        if not self.is_connected():
            return True
            
        try:
            if self.connected_vci:
                if self.connected_vci.device_type == VCITypes.J2534:
                     if self.connected_vci._j2534_device:
                         self.connected_vci._j2534_device.close()
                         self.connected_vci._j2534_device = None
            
            self.connected_vci = None
            self.status = VCIStatus.DISCONNECTED
            self.active_channel_id = None
            self._notify_status("disconnected")
            return True
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
            return False

    def get_device_info(self) -> Dict[str, Any]:
        if not self.connected_vci:
            return {}
        return {
            "name": self.connected_vci.name,
            "type": self.connected_vci.device_type.value,
            "port": self.connected_vci.port
        }

    def initialize_protocol(self, protocol_name: str) -> bool:
        """Initialize a specific protocol on the connected VCI"""
        if not self.connected_vci:
            return False
            
        device = self.connected_vci
        self.active_protocol_name = protocol_name
        
        if device.device_type == VCITypes.J2534:
            try:
                if not hasattr(device, '_j2534_device') or not device._j2534_device:
                    return False
                    
                # Map protocol name to J2534 ID
                protocol_id = J2534Protocol.ISO15765 # Default
                if protocol_name == "ISO15765":
                    protocol_id = J2534Protocol.ISO15765
                elif protocol_name == "ISO9141":
                    protocol_id = J2534Protocol.ISO9141
                elif protocol_name == "CAN":
                    protocol_id = J2534Protocol.CAN
                    
                channel_id = device._j2534_device.connect(protocol_id, 0, 500000) # 500k baud default
                
                if channel_id > 0:
                    self.active_channel_id = channel_id
                    logger.info(f"Protocol {protocol_name} initialized on Channel {channel_id}")
                    return True
                else:
                    logger.error(f"Failed to initialize protocol {protocol_name}")
                    return False
            except Exception as e:
                logger.error(f"Protocol initialization error: {e}")
                return False
        
        # Serial/OBDLink Protocol Initialization
        elif hasattr(device, '_obd_device') and device._obd_device:
            return True

        return False

    def send_to_channel(self, message: J2534Message) -> bool:
        """
        Send a J2534 message to the active channel.
        Used by IsoTpHandler as the transport interface.
        """
        if not self.connected_vci:
            return False
            
        device = self.connected_vci
        
        if hasattr(device, '_j2534_device') and device._j2534_device:
            if not hasattr(self, 'active_channel_id') or self.active_channel_id is None:
                logger.error("Cannot send: No active protocol channel")
                return False
                
            return device._j2534_device.send_message(self.active_channel_id, message)
            
        return False

    def read_message(self, timeout_ms: int = 1000) -> Optional[J2534Message]:
        """
        Read a J2534 message from the active channel.
        Used by IsoTpHandler as the transport interface.
        """
        if not self.connected_vci:
            return None
            
        device = self.connected_vci
        
        if hasattr(device, '_j2534_device') and device._j2534_device:
            if not hasattr(self, 'active_channel_id') or self.active_channel_id is None:
                return None
                
            return device._j2534_device.read_message(self.active_channel_id, timeout_ms)
            
        return None

    def send_uds_request(self, data: bytes, tx_id: int = 0x7E0, rx_id: int = 0x7E8, timeout_ms: int = 2000) -> Optional[bytes]:
        """
        Send a UDS request using ISO-TP and return the response data.
        This is the main entry point for diagnostic operations.
        """
        if not self.connected_vci:
            logger.error("Not connected to VCI")
            return None

        # Ensure protocol is initialized (default to ISO15765 if not set)
        if not hasattr(self, 'active_channel_id') or self.active_channel_id is None:
            if not self.initialize_protocol("ISO15765"):
                return None

        # Hardware ISO-TP (J2534 ISO15765)
        if hasattr(self, 'active_protocol_name') and self.active_protocol_name == "ISO15765" and self.connected_vci.device_type == VCITypes.J2534:
            try:
                # Construct J2534 Message (ID + Data)
                tx_id_bytes = tx_id.to_bytes(4, 'big')
                full_data = tx_id_bytes + data
                
                msg = J2534Message(J2534Protocol.ISO15765, data=full_data)
                
                if self.send_to_channel(msg):
                    # Read response
                    # Note: J2534 ReadMsgs for ISO15765 typically returns the reassembled message
                    # The first 4 bytes are the RxID (e.g. 0x7E8)
                    response_msg = self.read_message(timeout_ms)
                    if response_msg and response_msg.data:
                        if len(response_msg.data) > 4:
                            return response_msg.data[4:]
                    return None
                return None
            except Exception as e:
                logger.error(f"Hardware ISO-TP error: {e}")
                return None

        # Software ISO-TP (CAN / ELM327)
        # Create ISO-TP handler
        isotp = IsoTpHandler(self, tx_id, rx_id, timeout_ms)
        
        # Send
        if not isotp.send_data(data):
            logger.error("Failed to send UDS request")
            return None
            
        # Receive
        response = isotp.receive_data(timeout_ms)
        return response

    def tester_present(self, tx_id: int = 0x7E0, rx_id: int = 0x7E8) -> bool:
        """
        Send Tester Present (Service 0x3E) to keep session alive.
        Sub-function 0x00 (Response Required) or 0x80 (No Response Required)
        """
        # We usually use 0x80 (No response) for periodic keep-alive to reduce bus load
        # But here we use 0x00 to verify connection if called manually
        response = self.send_uds_request(bytes([0x3E, 0x00]), tx_id, rx_id)
        
        if response and len(response) > 0 and response[0] == 0x7E: # Positive response
            return True
        return False

    def security_access(self, level: int, seed_key_callback: Callable[[bytes], bytes], tx_id: int = 0x7E0, rx_id: int = 0x7E8) -> bool:
        """
        Perform Security Access (Service 0x27).
        
        Args:
            level: Security level (odd number, e.g., 0x01, 0x03, 0x11)
            seed_key_callback: Function that takes seed (bytes) and returns key (bytes)
            tx_id: Transmit ID
            rx_id: Receive ID
            
        Returns:
            True if access granted, False otherwise
        """
        if not self.is_connected():
            return False
            
        try:
            # 1. Request Seed
            # Service 0x27 + Level
            response = self.send_uds_request(bytes([0x27, level]), tx_id, rx_id)
            
            if not response or len(response) < 2:
                logger.error("Failed to receive seed")
                return False
                
            # Check for positive response (0x67)
            if response[0] != 0x67 or response[1] != level:
                logger.error(f"Negative response to seed request: {response.hex()}")
                return False
                
            # Seed is remaining bytes
            seed = response[2:]
            
            # If seed is all zeros, we might already be unlocked
            if all(b == 0 for b in seed):
                logger.info("Security access already granted (Zero Seed)")
                return True
                
            # 2. Calculate Key
            try:
                key = seed_key_callback(seed)
            except Exception as e:
                logger.error(f"Error calculating key: {e}")
                return False
                
            # 3. Send Key
            # Service 0x27 + Level + 1 (Send Key) + Key
            send_key_level = level + 1
            payload = bytes([0x27, send_key_level]) + key
            
            response = self.send_uds_request(payload, tx_id, rx_id)
            
            if response and len(response) >= 2 and response[0] == 0x67 and response[1] == send_key_level:
                logger.info(f"Security Access Level {level} Granted")
                return True
            else:
                logger.warning("Security Access Denied (Invalid Key)")
                return False
                
        except Exception as e:
            logger.error(f"Security Access Error: {e}")
            return False


def get_vci_manager():
    return VCIManager.get_instance()
