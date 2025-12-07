"""
VCI Manager for AutoDiag Pro
Handles VCI device detection, connection, and recognition
"""

import logging
import time
import threading
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class VCITypes(Enum):
    """Supported VCI device types"""
    GODIAG_GD101 = "GoDiag GD101"
    OBDLINK_MX_PLUS = "OBDLink MX+"
    SCANMATIK_2_PRO = "Scanmatik 2 Pro"
    HH_OBD_ADVANCE = "HH OBD Advance"
    J2534_GENERIC = "J2534 Generic"
    UNKNOWN = "Unknown"


class VCIStatus(Enum):
    """VCI connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class VCIDevice:
    """VCI device information"""
    device_type: VCITypes
    name: str
    port: Optional[str] = None
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None
    status: VCIStatus = VCIStatus.DISCONNECTED
    last_seen: Optional[float] = None
    capabilities: List[str] = None

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []


class VCIManager:
    """Manager for VCI device detection and connection"""

    def __init__(self):
        self.connected_vci: Optional[VCIDevice] = None
        self.available_devices: List[VCIDevice] = []
        self.is_scanning = False
        self.scan_thread = None
        self.callbacks: List[callable] = []

        # Supported device signatures
        self.device_signatures = {
            VCITypes.GODIAG_GD101: ["GoDiag", "GD101", "GT100"],
            VCITypes.OBDLINK_MX_PLUS: ["OBDLink", "MX+", "MX-Plus", "MX Plus"],
            VCITypes.SCANMATIK_2_PRO: ["Scanmatik", "2 Pro"],
            VCITypes.HH_OBD_ADVANCE: ["HH OBD", "Advance"],
        }

    def add_status_callback(self, callback: callable):
        """Add callback for VCI status changes"""
        self.callbacks.append(callback)

    def remove_status_callback(self, callback: callable):
        """Remove VCI status callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def _notify_callbacks(self, event: str, data: Any = None):
        """Notify all registered callbacks"""
        for callback in self.callbacks:
            try:
                callback(event, data)
            except Exception as e:
                logger.debug(f"Callback error: {e}")

    def scan_for_devices(self, timeout: int = 10) -> List[VCIDevice]:
        """Scan for available VCI devices"""
        if self.is_scanning:
            logger.warning("Device scan already in progress")
            return self.available_devices.copy()

        self.is_scanning = True
        self.available_devices = []

        try:
            import time
            start_time = time.time()

            # Run scan synchronously for reliability with timeout protection
            self._scan_serial_ports()

            # Check timeout before J2534 scan
            if time.time() - start_time > timeout:
                logger.warning(f"Device scan timed out after {timeout} seconds")
                return self.available_devices.copy()

            self._scan_j2534_devices()

            # Check timeout before Bluetooth scan
            if time.time() - start_time > timeout:
                logger.warning(f"Device scan timed out after {timeout} seconds")
                return self.available_devices.copy()

            self._scan_bluetooth_devices()

            logger.info(f"Device scan completed, found {len(self.available_devices)} devices")

        except Exception as e:
            logger.error(f"Device scan failed: {e}")
        finally:
            self.is_scanning = False

        return self.available_devices.copy()

    def _scan_worker(self, timeout: int):
        """Worker thread for device scanning"""
        start_time = time.time()

        try:
            # Scan serial ports for known VCI devices
            self._scan_serial_ports()

            # Scan for J2534 devices
            self._scan_j2534_devices()

            # Scan for Bluetooth devices (for wireless VCIs)
            self._scan_bluetooth_devices()

            elapsed = time.time() - start_time
            logger.info(f"Device scan completed in {elapsed:.1f}s, found {len(self.available_devices)} devices")

        except Exception as e:
            logger.error(f"Scan worker error: {e}")

    def _scan_serial_ports(self):
        """Scan serial/COM ports for VCI devices"""
        try:
            import serial.tools.list_ports  # type: ignore[import-not-found]

            ports = serial.tools.list_ports.comports()
            logger.info(f"Scanning {len(ports)} COM ports for VCI devices...")

            for port in ports:
                try:
                    logger.debug(f"Checking port {port.device}: {port.description}, VID:PID={port.vid}:{port.pid}")

                    # Check for known USB VID/PID combinations
                    device = self._identify_device_by_usb_id(port)
                    if device:
                        device.port = port.device
                        device.last_seen = time.time()
                        self.available_devices.append(device)
                        logger.info(f"Found VCI device by USB ID: {device.name} on {port.device}")
                        continue

                    # Try to identify device by opening port briefly
                    device = self._identify_device_on_port(port.device)
                    if device:
                        device.port = port.device
                        device.last_seen = time.time()
                        self.available_devices.append(device)
                        logger.info(f"Found VCI device: {device.name} on {port.device}")

                except Exception as e:
                    logger.debug(f"Failed to identify device on {port.device}: {e}")

        except ImportError:
            logger.warning("Serial tools not available, skipping serial port scan")

    def _identify_device_by_usb_id(self, port) -> Optional[VCIDevice]:
        """Identify VCI device by USB Vendor ID and Product ID"""
        # Known USB VID/PID combinations for VCI devices
        known_devices = {
            # GoDiag GD101 / GT100 - common FTDI or CH340 chips
            (0x0403, 0x6001): VCITypes.GODIAG_GD101,  # FTDI FT232R
            (0x1A86, 0x7523): VCITypes.GODIAG_GD101,  # CH340
            (0x10C4, 0xEA60): VCITypes.GODIAG_GD101,  # CP2102
            (0xE327, 0x2534): VCITypes.GODIAG_GD101,  # GoDiag GD101 specific
            (58151, 9524): VCITypes.GODIAG_GD101,     # GoDiag GD101 (decimal)
            # OBDLink MX+
            (0x0403, 0x6015): VCITypes.OBDLINK_MX_PLUS,  # FTDI FT231X
        }

        if port.vid and port.pid:
            device_type = known_devices.get((port.vid, port.pid))
            if device_type:
                device = VCIDevice(
                    device_type=device_type,
                    name=f"{device_type.value}",
                    port=port.device,
                    status=VCIStatus.DISCONNECTED
                )
                device.capabilities = self._get_device_capabilities(device_type)
                return device

        # Also check description for known device names
        if port.description:
            desc_lower = port.description.lower()
            for vci_type, signatures in self.device_signatures.items():
                for signature in signatures:
                    if signature.lower() in desc_lower:
                        device = VCIDevice(
                            device_type=vci_type,
                            name=f"{vci_type.value}",
                            port=port.device,
                            status=VCIStatus.DISCONNECTED
                        )
                        device.capabilities = self._get_device_capabilities(vci_type)
                        return device

        return None

    def _scan_j2534_devices(self):
        """Scan for J2534-compliant devices"""
        try:
            # Try to detect J2534 devices through registry/API
            import winreg

            # Check for J2534 devices in registry
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                   r"SOFTWARE\WOW6432Node\PassThruSupport.04.04")

                i = 0
                max_attempts = 100  # Safety limit to prevent infinite loops
                attempts = 0

                while attempts < max_attempts:
                    try:
                        subkey = winreg.EnumKey(key, i)
                        device_key = winreg.OpenKey(key, subkey)

                        # Try to get device info
                        try:
                            name = winreg.QueryValueEx(device_key, "Name")[0]
                            vendor = winreg.QueryValueEx(device_key, "Vendor")[0]

                            device = VCIDevice(
                                device_type=VCITypes.J2534_GENERIC,
                                name=f"{vendor} {name}",
                                status=VCIStatus.DISCONNECTED
                            )
                            self.available_devices.append(device)
                            logger.info(f"Found J2534 device: {device.name}")

                        except FileNotFoundError:
                            pass

                        i += 1
                        attempts += 1

                    except OSError:
                        # No more keys to enumerate
                        break
                    except Exception as e:
                        logger.debug(f"Error enumerating J2534 device at index {i}: {e}")
                        break

            except FileNotFoundError:
                logger.debug("J2534 registry not found")

        except ImportError:
            logger.debug("Windows registry access not available")

    def _scan_bluetooth_devices(self):
        """Scan for Bluetooth VCI devices"""
        # This would require Bluetooth scanning libraries
        # For now, we'll simulate detection of known Bluetooth VCIs
        pass

    def _identify_device_on_port(self, port: str) -> Optional[VCIDevice]:
        """Try to identify VCI device on a specific port"""
        try:
            import serial  # type: ignore[import-not-found]

            # Try to open port briefly to identify device
            with serial.Serial(port, 9600, timeout=1) as ser:
                # Send identification command
                ser.write(b"ATI\r")  # Standard OBD identification command
                time.sleep(0.1)

                response = ser.read(100).decode('ascii', errors='ignore').strip()
                logger.debug(f"ATI response on {port}: {response}")

                # Check response against known signatures
                for vci_type, signatures in self.device_signatures.items():
                    for signature in signatures:
                        if signature.lower() in response.lower():
                            device = VCIDevice(
                                device_type=vci_type,
                                name=f"{vci_type.value}",
                                port=port,
                                status=VCIStatus.DISCONNECTED
                            )

                            # Set capabilities based on device type
                            device.capabilities = self._get_device_capabilities(vci_type)
                            return device

                # ELM327-based devices (like GoDiag GD101) - identify as GoDiag
                if "ELM327" in response or "ELM" in response:
                    device = VCIDevice(
                        device_type=VCITypes.GODIAG_GD101,
                        name="GoDiag GD101 (ELM327)",
                        port=port,
                        status=VCIStatus.DISCONNECTED
                    )
                    device.capabilities = self._get_device_capabilities(VCITypes.GODIAG_GD101)
                    return device

                # If no specific match, check for generic OBD responses
                if "OK" in response:
                    device = VCIDevice(
                        device_type=VCITypes.GODIAG_GD101,
                        name="GoDiag GD101",
                        port=port,
                        status=VCIStatus.DISCONNECTED
                    )
                    device.capabilities = self._get_device_capabilities(VCITypes.GODIAG_GD101)
                    return device

        except Exception as e:
            logger.debug(f"Failed to identify device on {port}: {e}")

        return None

    def _get_device_capabilities(self, vci_type: VCITypes) -> List[str]:
        """Get capabilities for a specific VCI device type"""
        capabilities_map = {
            VCITypes.GODIAG_GD101: [
                "j2534", "can_bus", "iso15765", "diagnostics",
                "dtc_read", "dtc_clear", "live_data", "ecu_programming"
            ],
            VCITypes.OBDLINK_MX_PLUS: [
                "can_bus", "obd2", "live_data", "can_sniffing",
                "multiple_protocols", "wireless"
            ],
            VCITypes.SCANMATIK_2_PRO: [
                "j2534", "can_bus", "diagnostics", "dtc_read",
                "live_data", "coding", "adaptation"
            ],
            VCITypes.HH_OBD_ADVANCE: [
                "obd2", "can_bus", "live_data", "basic_diagnostics"
            ],
            VCITypes.J2534_GENERIC: [
                "j2534", "can_bus", "iso15765", "diagnostics"
            ]
        }

        return capabilities_map.get(vci_type, ["basic_obd"])

    def connect_to_device(self, device: VCIDevice) -> bool:
        """Connect to a specific VCI device"""
        try:
            logger.info(f"Connecting to {device.name}...")

            # Update device status
            device.status = VCIStatus.CONNECTING
            self._notify_callbacks("connecting", device)

            # Attempt connection based on device type
            if device.device_type == VCITypes.GODIAG_GD101:
                success = self._connect_godiag_gd101(device)
            elif device.device_type == VCITypes.OBDLINK_MX_PLUS:
                success = self._connect_obdlink_mx_plus(device)
            elif device.device_type == VCITypes.SCANMATIK_2_PRO:
                success = self._connect_scanmatik_2_pro(device)
            elif device.device_type == VCITypes.HH_OBD_ADVANCE:
                success = self._connect_hh_obd_advance(device)
            else:
                success = self._connect_generic_obd(device)

            if success:
                device.status = VCIStatus.CONNECTED
                device.last_seen = time.time()
                self.connected_vci = device
                self._notify_callbacks("connected", device)
                logger.info(f"Successfully connected to {device.name}")
                return True
            else:
                device.status = VCIStatus.ERROR
                self._notify_callbacks("connection_failed", device)
                logger.error(f"Failed to connect to {device.name}")
                return False

        except Exception as e:
            logger.error(f"Connection error: {e}")
            device.status = VCIStatus.ERROR
            self._notify_callbacks("connection_error", {"device": device, "error": str(e)})
            return False

    def _connect_godiag_gd101(self, device: VCIDevice) -> bool:
        """Connect to GoDiag GD101 device"""
        try:
            # Try to import and use the J2534 interface
            from shared.j2534_passthru import GoDiagGD101PassThru

            # Get list of available COM ports
            available_ports = []
            try:
                import serial.tools.list_ports  # type: ignore[import-not-found]
                available_ports = [p.device for p in serial.tools.list_ports.comports()]
                logger.info(f"Available COM ports: {available_ports}")
            except ImportError:
                # Fallback to common ports - COM2 is prioritized for GoDiag GD101
                available_ports = ["COM2", "COM1", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "COM10"]

            # If device has a specific port, try that first
            ports_to_try = []
            if device.port:
                ports_to_try = [device.port] + [p for p in available_ports if p != device.port]
            else:
                ports_to_try = available_ports

            j2534_device = None
            for port in ports_to_try:
                try:
                    logger.info(f"Trying to connect GoDiag GD101 on {port}...")
                    j2534_device = GoDiagGD101PassThru(port=port, baudrate=115200)

                    if j2534_device.open():
                        device.port = port
                        device._j2534_device = j2534_device
                        logger.info(f"Successfully connected GoDiag GD101 on {port}")

                        # Get OBD2 connection status
                        obd2_status = j2534_device.get_obd2_status()
                        logger.info(f"OBD2 Status: {obd2_status}")

                        return True
                    else:
                        logger.debug(f"Failed to open GoDiag GD101 on {port}")

                except Exception as e:
                    logger.debug(f"Failed to connect GoDiag GD101 on {port}: {e}")
                    continue

            logger.error("Could not connect to GoDiag GD101 on any available port")
            return False

        except ImportError as e:
            logger.error(f"J2534 interface not available: {e}")
            return False
        except Exception as e:
            logger.error(f"GoDiag GD101 connection failed: {e}")
            return False

    def _connect_obdlink_mx_plus(self, device: VCIDevice) -> bool:
        """Connect to OBDLink MX+ device"""
        try:
            from shared.obdlink_mxplus import OBDLinkMXPlus

            obd_device = OBDLinkMXPlus(mock_mode=False)

            # Try Bluetooth connection first, then serial
            if device.port:
                success = obd_device.connect_serial(device.port, 38400)
            else:
                # Try common Bluetooth ports
                success = False
                for port in ["COM3", "COM4", "COM6", "COM7"]:
                    if obd_device.connect_serial(port, 38400):
                        device.port = port
                        success = True
                        break

            if success:
                device._obd_device = obd_device
                return True

        except ImportError:
            logger.warning("OBDLink MX+ interface not available")
        except Exception as e:
            logger.error(f"OBDLink MX+ connection failed: {e}")

        return False

    def _connect_scanmatik_2_pro(self, device: VCIDevice) -> bool:
        """Connect to Scanmatik 2 Pro device"""
        # Implementation would be similar to GoDiag
        logger.info("Scanmatik 2 Pro connection not yet implemented")
        return False

    def _connect_hh_obd_advance(self, device: VCIDevice) -> bool:
        """Connect to HH OBD Advance device"""
        # Implementation for HH OBD Advance
        logger.info("HH OBD Advance connection not yet implemented")
        return False

    def _connect_generic_obd(self, device: VCIDevice) -> bool:
        """Connect to generic OBD device"""
        try:
            import serial  # type: ignore[import-not-found]

            if device.port:
                ser = serial.Serial(device.port, 9600, timeout=1)
                # Test connection with basic OBD command
                ser.write(b"ATZ\r")  # Reset
                time.sleep(0.1)
                response = ser.read(100)

                if response:
                    device._serial_device = ser
                    return True
                else:
                    ser.close()

        except Exception as e:
            logger.error(f"Generic OBD connection failed: {e}")

        return False

    def disconnect(self) -> bool:
        """Disconnect from current VCI device"""
        if not self.connected_vci:
            return True

        try:
            device = self.connected_vci

            # Close device-specific connections
            if hasattr(device, '_j2534_device'):
                device._j2534_device.close()
            elif hasattr(device, '_obd_device'):
                device._obd_device.disconnect()
            elif hasattr(device, '_serial_device'):
                device._serial_device.close()

            device.status = VCIStatus.DISCONNECTED
            self._notify_callbacks("disconnected", device)

            logger.info(f"Disconnected from {device.name}")
            self.connected_vci = None
            return True

        except Exception as e:
            logger.error(f"Disconnect error: {e}")
            return False

    def get_connected_device(self) -> Optional[VCIDevice]:
        """Get currently connected VCI device"""
        return self.connected_vci

    def get_device_info(self) -> Dict[str, Any]:
        """Get information about connected device"""
        if not self.connected_vci:
            return {"status": "disconnected"}

        device = self.connected_vci
        return {
            "status": device.status.value,
            "type": device.device_type.value,
            "name": device.name,
            "port": device.port,
            "capabilities": device.capabilities,
            "firmware_version": device.firmware_version,
            "serial_number": device.serial_number
        }

    def is_connected(self) -> bool:
        """Check if a VCI device is connected"""
        return (self.connected_vci is not None and
                self.connected_vci.status == VCIStatus.CONNECTED)

    def get_supported_devices(self) -> List[str]:
        """Get list of supported VCI device types"""
        return [vci_type.value for vci_type in VCITypes if vci_type != VCITypes.UNKNOWN]


# Global VCI manager instance
vci_manager = VCIManager()


def get_vci_manager() -> VCIManager:
    """Get the global VCI manager instance"""
    return vci_manager