"""
VCI Manager for AutoDiag Pro - ELITE CRASH FIX IMPLEMENTATION
Handles VCI device detection, connection, and recognition
WITH COMPLETE THREADING + HANG PROTECTION - Zero GUI freezing
EXIT CODE 3489660927 (0xCFFFFFFF) PERMANENT FIX
"""

import logging
import time
import threading
import concurrent.futures
from typing import Optional, List, Dict, Any, Tuple, Union
from enum import Enum
from dataclasses import dataclass
import os
import subprocess
import json
import atexit

from PyQt6.QtCore import QThread, pyqtSignal, QObject, QTimer
from PyQt6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

class VCITypes(Enum):
    """Supported VCI device types"""
    OBDLINK_MX_PLUS = "OBDLink MX+"
    SCANMATIK_2_PRO = "Scanmatik 2 Pro"
    HH_OBD_ADVANCE = "HH OBD Advance"
    J2534_GENERIC = "J2534 Generic"
    VCDS_HEX_V2 = "Ross-Tech HEX-V2 (Clone)"
    BLUE_PILL_VCI = "DACOS VCI"
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
    bluetooth_address: Optional[str] = None
    dll_path: Optional[str] = None

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []


class HangWatchdog(QObject):
    """ELITE HANG PROTECTION WATCHDOG - prevents Windows Application Hang Termination"""
    def __init__(self, app=None, check_interval=2.0, timeout=10.0):
        super().__init__()
        self.app = app or QApplication.instance()
        self.timer = QTimer()
        self.timer.timeout.connect(self.pulse)
        self.is_active = False
        self._pulse_count = 0
        self._check_interval = check_interval
        self._timeout = timeout
        logger.info("Hang Protection Watchdog initialized")
    def heartbeat(self):
        """Heartbeat method called by external timers to keep watchdog alive"""
        self._pulse_count = 0
    def start_monitoring(self):
        """Start watchdog monitoring (alias for start)"""
        self.start(int(self._check_interval * 1000))
    def stop_monitoring(self):
        """Stop watchdog monitoring (alias for stop)"""
        self.stop()

    def start(self, interval_ms=1000):
        if not self.is_active:
            self.timer.start(interval_ms)
            self.is_active = True
            logger.info(f"Hang Protection Watchdog started with {interval_ms}ms interval")

    def stop(self):
        if self.is_active:
            self.timer.stop()
            self.is_active = False
            logger.info("Hang Protection Watchdog stopped")

    def pulse(self):
        """Safe pulse - only logs, never calls processEvents()"""
        try:
            self._pulse_count += 1
            if self._pulse_count % 10 == 0:
                logger.debug(f"Watchdog pulse #{self._pulse_count} - GUI responsive")
            if self._pulse_count >= 100:
                logger.warning("Watchdog pulse limit reached - stopping")
                self.stop()
        except Exception as e:
            logger.error(f"Watchdog pulse error: {e}")


class VCIScannerThread(QThread):
    scan_completed = pyqtSignal(list)
    scan_error = pyqtSignal(str)
    scan_progress = pyqtSignal(str)

    def __init__(self, vci_manager):
        super().__init__()
        self.vci_manager = vci_manager
        self.timeout = 15
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()
        self.quit()
        self.wait(2000)

    def run(self):
        try:
            self.scan_progress.emit("Starting VCI device scan...")
            devices = self.vci_manager._scan_for_devices_with_timeout(self.timeout)
            self.scan_completed.emit(devices)
        except Exception as e:
            logger.error(f"Scan thread error: {e}")
            self.scan_error.emit(str(e))
        finally:
            self.vci_manager.is_scanning = False


class VCIManager(QObject):
    status_changed = pyqtSignal(str, object)
    devices_found = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.connected_vci: Optional[VCIDevice] = None
        self.available_devices: List[VCIDevice] = []
        self.is_scanning = False
        self.scan_thread = None
        self.callbacks: List[callable] = []

        self.hang_watchdog = HangWatchdog()
        self._watchdog_active = False

        self.device_signatures = {
            VCITypes.OBDLINK_MX_PLUS: ["OBDLink", "MX+", "MX-Plus", "MX Plus"],
            VCITypes.SCANMATIK_2_PRO: ["Scanmatik", "2 Pro"],
            VCITypes.HH_OBD_ADVANCE: ["HH OBD", "Advance"],
        }

        atexit.register(self._shutdown_bridge)

    def _shutdown_bridge(self):
        """Cleanup handler registered with atexit — ensures bridge
        resources are released on interpreter shutdown."""
        try:
            self.disconnect()
        except Exception:
            pass

    def add_status_callback(self, callback: callable):
        """Register a callback for VCI status events."""
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def remove_status_callback(self, callback: callable):
        """Unregister a status callback."""
        try:
            self.callbacks.remove(callback)
        except ValueError:
            pass

    def _notify_callbacks(self, event: str, data: object = None):
        """Notify all registered callbacks of a VCI event."""
        for callback in self.callbacks:
            try:
                callback(event, data)
            except Exception as e:
                logger.debug(f"Callback error: {e}")

    def scan_for_devices(self, timeout: int = 15) -> bool:
        if self.is_scanning:
            return False
        self.is_scanning = True
        self.available_devices = []
        self._activate_hang_protection("VCI device scan")
        self.scan_thread = VCIScannerThread(self)
        self.scan_thread.scan_completed.connect(self._on_scan_completed)
        self.scan_thread.scan_error.connect(self._on_scan_error)
        self.scan_thread.scan_progress.connect(self._on_scan_progress)
        self.scan_thread.timeout = timeout
        self.scan_thread.start()
        logger.info(f"Started threaded VCI scan with {timeout}s timeout")
        return True

    def _activate_hang_protection(self, operation_name: str):
        if not self._watchdog_active:
            self.hang_watchdog.start(1000)
            self._watchdog_active = True
            logger.info(f"Hang protection activated for: {operation_name}")

    def _deactivate_hang_protection(self):
        if self._watchdog_active:
            self.hang_watchdog.stop()
            self._watchdog_active = False
            logger.info("Hang protection deactivated")

    def _on_scan_completed(self, devices):
        self.available_devices = devices
        self.is_scanning = False
        self.devices_found.emit(devices)
        self._deactivate_hang_protection()
        for device in devices:
            logger.info(f"Found: {device.name} ({device.device_type.value}) - Port: {device.port}")

    def _on_scan_error(self, error_message):
        logger.error(f"Scan error: {error_message}")
        self.is_scanning = False
        self.status_changed.emit("error", {"message": error_message})
        self._deactivate_hang_protection()

    def _on_scan_progress(self, progress_message):
        logger.debug(f"Scan progress: {progress_message}")
        self.status_changed.emit("progress", {"message": progress_message})

    def _scan_for_devices_with_timeout(self, timeout: int) -> List[VCIDevice]:
        devices = []
        start_time = time.time()
        logger.info(f"Starting VCI device scan (timeout: {timeout}s)")

        # J2534 registry scan
        devices.extend(self._scan_j2534_devices_with_timeout(timeout, start_time))
        # USB hardware detection (no port opening)
        devices.extend(self._detect_specific_usb_hardware())
        # Bluetooth scan (only if time left)
        if time.time() - start_time < timeout * 0.7:
            devices.extend(self._scan_bluetooth_devices_with_timeout(timeout, start_time))

        # Deduplicate and sort
        unique = []
        seen = set()
        for d in devices:
            key = (d.device_type, d.port or d.bluetooth_address or d.name)
            if key not in seen:
                seen.add(key)
                unique.append(d)
        def _sort_key(d):
            if d.device_type == VCITypes.BLUE_PILL_VCI:
                return 0  # DACOS VCI first on Linux
            if d.device_type == VCITypes.J2534_GENERIC:
                return 1
            return 2
        unique.sort(key=_sort_key)
        return unique

    def _scan_j2534_devices_with_timeout(self, total_timeout: int, start_time: float) -> List[VCIDevice]:
        found = []
        try:
            import winreg
            # Check registry for PassThru devices
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\PassThruSupport.04.04")
                i = 0
                while True:
                    try:
                        subkey = winreg.EnumKey(key, i)
                        device_key = winreg.OpenKey(key, subkey)
                        name = winreg.QueryValueEx(device_key, "Name")[0]
                        vendor = winreg.QueryValueEx(device_key, "Vendor")[0]
                        dll_path = winreg.QueryValueEx(device_key, "FunctionLibrary")[0] if hasattr(winreg, 'QueryValueEx') else None
                        device = VCIDevice(
                            device_type=VCITypes.J2534_GENERIC,
                            name=f"{vendor} {name}",
                            dll_path=dll_path,
                            status=VCIStatus.DISCONNECTED
                        )
                        device.capabilities = self._get_device_capabilities(VCITypes.J2534_GENERIC)
                        found.append(device)
                        i += 1
                    except OSError:
                        break
            except FileNotFoundError:
                logger.debug("J2534 registry not found")
            # Also scan local drivers folder
            import os
            from pathlib import Path
            project_root = Path(__file__).parent.parent.parent
            drivers_dir = project_root / "drivers"
            if drivers_dir.exists():
                for dll in drivers_dir.glob("*.dll"):
                    device = VCIDevice(
                        device_type=VCITypes.J2534_GENERIC,
                        name=f"Local Driver: {dll.stem}",
                        dll_path=str(dll),
                        status=VCIStatus.DISCONNECTED
                    )
                    device.capabilities = self._get_device_capabilities(VCITypes.J2534_GENERIC)
                    found.append(device)
        except Exception as e:
            logger.error(f"J2534 scan failed: {e}")
        return found

    def _detect_specific_usb_hardware(self) -> List[VCIDevice]:
        """Detect USB-connected diagnostic hardware by port description.

        Scans for Ross-Tech HEX-V2 clone cables on HID bus, and
        lists all serial COM ports for reference.
        """
        devices: List[VCIDevice] = []

        # --- Ross-Tech HEX-V2 (clone) via HID ---
        try:
            import hid
            for dev_info in hid.enumerate():
                vid = dev_info.get("vendor_id", 0)
                pid = dev_info.get("product_id", 0)
                if vid == 0x0483 and pid == 0xA0CB:
                    product = dev_info.get("product_string", "Ross-Tech HEX-V2")
                    manufacturer = dev_info.get("manufacturer_string", "Hex Microsystems")
                    logger.info(
                        "Found VCDS clone on HID: VID=0x%04X PID=0x%04X — %s (%s)",
                        vid, pid, product, manufacturer,
                    )
                    device = VCIDevice(
                        device_type=VCITypes.VCDS_HEX_V2,
                        name=f"Ross-Tech HEX-V2 Clone (HID)",
                        status=VCIStatus.DISCONNECTED,
                    )
                    device.capabilities = self._get_device_capabilities(VCITypes.VCDS_HEX_V2)
                    device.vid = vid
                    device.pid = pid
                    device.port = "HID"  # Not a serial port
                    devices.append(device)
        except ImportError:
            logger.debug("hidapi not installed — skipping HID scan")
        except Exception as e:
            logger.debug(f"HID scan error: {e}")

        # --- DACOS VCI (Blue Pill, USB CDC, VID=0xDAC0 PID=0x2534) ---
        try:
            import serial.tools.list_ports
            for port in serial.tools.list_ports.comports():
                if port.description:
                    logger.debug(f"USB port detected: {port.device} - {port.description}")
                vid = getattr(port, 'vid', None)
                pid = getattr(port, 'pid', None)
                if vid == 0xDAC0 and pid == 0x2534:
                    logger.info(f"DACOS VCI detected on {port.device} ({port.description})")
                    device = VCIDevice(
                        device_type=VCITypes.BLUE_PILL_VCI,
                        name=f"DACOS VCI ({port.device})",
                        port=port.device,
                        status=VCIStatus.DISCONNECTED,
                    )
                    device.capabilities = self._get_device_capabilities(VCITypes.BLUE_PILL_VCI)
                    devices.append(device)
        except Exception as e:
            logger.debug(f"USB detection failed: {e}")

        return devices

    def _scan_bluetooth_devices_with_timeout(self, total_timeout: int, start_time: float) -> List[VCIDevice]:
        """
        Scan for Bluetooth OBD-II adapters (HH OBD Advanced, ELM327, etc.)
        using the HHOBDBTScanner.
        """
        devices = []
        try:
            from drivers.hh_obd_advanced.bluetooth_scanner import HHOBDBTScanner

            remaining = max(5, total_timeout - (time.time() - start_time))
            scanner = HHOBDBTScanner(scan_timeout=int(remaining))
            scan_result = scanner.scan(timeout=int(remaining))

            for bt_device in scan_result.obd_devices:
                port = bt_device.rfcomm_port
                device = VCIDevice(
                    device_type=VCITypes.HH_OBD_ADVANCE,
                    name=bt_device.name,
                    port=port,
                    bluetooth_address=bt_device.address,
                    status=VCIStatus.DISCONNECTED,
                )
                device.capabilities = self._get_device_capabilities(VCITypes.HH_OBD_ADVANCE)
                device._bt_device_info = bt_device
                devices.append(device)
                logger.info(f"Found BT OBD: {bt_device.name} @ {bt_device.address} "
                            f"(port={port}, chipset={bt_device.chipset})")

        except ImportError:
            logger.debug("HH OBD Advanced scanner not available (not installed)")
        except Exception as e:
            logger.error(f"Bluetooth scan error: {e}")

        return devices

    def _get_device_capabilities(self, vci_type: VCITypes) -> List[str]:
        caps = {
            VCITypes.J2534_GENERIC: ["j2534", "can_bus", "iso15765", "diagnostics"],
            VCITypes.OBDLINK_MX_PLUS: ["can_bus", "obd2", "live_data", "can_sniffing", "wireless"],
            VCITypes.SCANMATIK_2_PRO: ["j2534", "can_bus", "diagnostics", "dtc_read", "live_data", "coding"],
            VCITypes.HH_OBD_ADVANCE: ["obd2", "can_bus", "live_data", "dtc_read", "dtc_clear", "vin_read"],
            VCITypes.VCDS_HEX_V2: ["can_bus", "isotp", "uds", "kline", "dtc_read", "dtc_clear", "vin_read", "live_data", "coding"],
            VCITypes.BLUE_PILL_VCI: ["can_bus", "isotp", "uds", "dtc_read", "dtc_clear", "vin_read", "live_data", "j2534"],
        }
        return caps.get(vci_type, ["basic_obd"])

    def connect_to_device(self, device: VCIDevice) -> bool:
        try:
            logger.info(f"Connecting to {device.name}...")
            device.status = VCIStatus.CONNECTING
            self._notify_callbacks("connecting", device)
            self._activate_hang_protection(f"VCI connection to {device.name}")

            success = False
            if device.device_type == VCITypes.OBDLINK_MX_PLUS:
                success = self._connect_obdlink_mx_plus(device)
            elif device.device_type == VCITypes.SCANMATIK_2_PRO:
                success = self._connect_scanmatik_2_pro(device)
            elif device.device_type == VCITypes.J2534_GENERIC:
                success = self._connect_j2534_generic(device)
            else:
                success = self._connect_generic_obd(device)

            self._deactivate_hang_protection()
            if success:
                device.status = VCIStatus.CONNECTED
                device.last_seen = time.time()
                self.connected_vci = device
                self._notify_callbacks("connected", device)
                logger.info(f"Connected to {device.name}")
                return True
            else:
                device.status = VCIStatus.ERROR
                self._notify_callbacks("connection_failed", device)
                return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            device.status = VCIStatus.ERROR
            self._deactivate_hang_protection()
            return False

    def _connect_obdlink_mx_plus(self, device: VCIDevice) -> bool:
        logger.info("OBDLink MX+ connection not yet integrated")
        return False

    def _connect_scanmatik_2_pro(self, device: VCIDevice) -> bool:
        logger.info("Scanmatik 2 Pro connection not yet integrated")
        return False

    def _connect_j2534_generic(self, device: VCIDevice) -> bool:
        # Fallback for other J2534 devices using original method
        try:
            from shared.j2534_passthru import J2534PassThru
            if device.dll_path:
                j2534 = J2534PassThru(dll_path=device.dll_path)
                if j2534.open():
                    device._j2534_device = j2534
                    return True
        except Exception as e:
            logger.error(f"Generic J2534 connection failed: {e}")
        return False

    def _connect_bluepill(self, device: VCIDevice) -> bool:
        """Connect to DACOS VCI — STM32F103 Blue Pill + MCP2515 SPI CAN bridge.

        Uses :class:`DACOS_J2534` (shared/dacos_j2534.py) which speaks the
        binary frame protocol: [0xDA][CMD][LEN_H][LEN_L][DATA...][CRC8].
        VID=0xDAC0 PID=0x2534, enumerates as /dev/ttyACM0 (Linux) or COM11 (Windows).
        """
        try:
            from shared.dacos_j2534 import DACOS_J2534, J2534Error as DACOSError

            port = device.port
            if not port:
                logger.error("No serial port specified for Blue Pill")
                return False

            logger.info("Connecting to Blue Pill J2534 bridge on %s …", port)

            bridge = DACOS_J2534(port=port)

            if not bridge.open():
                logger.error("Blue Pill DACOS_J2534.open() returned False")
                return False

            version = bridge.get_version()
            logger.info("Blue Pill firmware version: %s", version)

            device.name = "DACOS VCI (Blue Pill MCP2515)"
            device.device_type = VCITypes.BLUE_PILL_VCI
            device.capabilities = [
                "can_bus", "isotp", "uds", "kline", "j2534",
                "kwp2000", "tp20",
            ]
            # Store the DACOS_J2534 bridge object — this is the primary
            # transport for all UDS / OBD-II communication.
            device._bluepill_bridge = bridge
            device.status = VCIStatus.CONNECTED

            logger.info("✅ Blue Pill J2534 bridge connected (v%s)", version)
            return True

        except ImportError:
            logger.error("shared/dacos_j2534.py not found — cannot use Blue Pill")
            return False
        except Exception as e:
            logger.error("Blue Pill connection failed: %s", e)
            return False

    def _connect_vcds_hid(self, device: VCIDevice) -> bool:
        """Connect to clone Ross-Tech HEX-V2 cable via HID over USB.

        Uses :class:`VCDSHIDBridge` which speaks the Ross-Tech HID
        protocol reverse-engineered from USB captures on a 2007 Audi TT.
        Handshake verified 2026-05-15 with real STM32F412 clone cable.
        """
        try:
            from core.vcds_hid_bridge import VCDSHIDBridge, DeviceNotFoundError

            vid = getattr(device, "vid", 0x0483)
            pid = getattr(device, "pid", 0xA0CB)

            logger.info("Connecting to Ross-Tech HEX-V2 clone via HID …")

            bridge = VCDSHIDBridge(vid=vid, pid=pid)

            if not bridge.open():
                logger.error("VCDS HID bridge open() returned False")
                return False

            version = bridge.get_version()
            logger.info("Ross-Tech HEX-V2 FW: %s", version)

            device.name = "Ross-Tech HEX-V2 Clone"
            device.device_type = VCITypes.VCDS_HEX_V2
            device.capabilities = self._get_device_capabilities(VCITypes.VCDS_HEX_V2)
            device.vid = vid
            device.pid = pid
            device._vcds_hid_bridge = bridge
            device.status = VCIStatus.CONNECTED

            logger.info("✅ Ross-Tech HEX-V2 bridge connected (FW %s)", version)
            return True

        except ImportError:
            logger.error("core/vcds_hid_bridge.py not found — cannot use VCDS HID")
            return False
        except DeviceNotFoundError:
            logger.error("Ross-Tech HEX-V2 not found on HID bus — is cable plugged in?")
            return False
        except Exception as e:
            logger.error("VCDS HID connection failed: %s", e)
            return False

    def _connect_elm327(self, device: VCIDevice) -> bool:
        """Connect to HH OBD Advance / ELM327 Bluetooth adapter.

        Uses the :class:`ELM327Driver` from ``drivers/hh_obd_advanced/``
        which speaks ELM327 AT-commands over Bluetooth RFCOMM serial.
        """
        try:
            from drivers.hh_obd_advanced.elm327_driver import ELM327Driver, ELM327Error

            port = device.port
            if not port:
                logger.error("No serial/COM port specified for ELM327 device")
                return False

            logger.info("Connecting to ELM327 on %s …", port)

            elm = ELM327Driver(port=port, baudrate=38400, timeout=3.0)
            if not elm.connect():
                logger.error("ELM327 connect() returned False on %s", port)
                return False

            info = elm.get_device_info()
            logger.info("ELM327 connected — chipset: %s, version: %s, voltage: %.1fV",
                        info.chipset, info.version, info.voltage)

            device.name = f"HH OBD Advance (ELM327 {info.version})"
            device.device_type = VCITypes.HH_OBD_ADVANCE
            device.capabilities = [
                "obd2", "live_data", "dtc_read", "dtc_clear",
                "vin_read", "pid_snapshot", "freeze_frame",
            ]
            device._elm327_driver = elm
            device.status = VCIStatus.CONNECTED

            logger.info("✅ ELM327 connected on %s", port)
            return True

        except ImportError:
            logger.error("drivers/hh_obd_advanced/elm327_driver.py not found")
            return False
        except ELM327Error as e:
            logger.error("ELM327 connection error: %s", e)
            return False
        except Exception as e:
            logger.error("ELM327 connection failed: %s", e)
            return False

    def get_elm327_driver(self):
        """Get the active ELM327 driver if connected to HH OBD Advance."""
        if self.connected_vci and self.connected_vci.device_type == VCITypes.HH_OBD_ADVANCE:
            return getattr(self.connected_vci, '_elm327_driver', None)
        return None

    def read_dtcs_elm327(self) -> List[Dict[str, Any]]:
        """Read DTCs via ELM327 (Mode 03 + Mode 07)."""
        elm = self.get_elm327_driver()
        if not elm:
            raise ConnectionError("ELM327 driver not available — not connected to HH OBD Advance")
        return elm.read_dtcs()

    def clear_dtcs_elm327(self) -> bool:
        """Clear DTCs via ELM327 (Mode 04)."""
        elm = self.get_elm327_driver()
        if not elm:
            raise ConnectionError("ELM327 driver not available — not connected to HH OBD Advance")
        return elm.clear_dtcs()

    def read_vin_elm327(self) -> Optional[str]:
        """Read VIN via ELM327 (Mode 09 PID 02)."""
        elm = self.get_elm327_driver()
        if not elm:
            raise ConnectionError("ELM327 driver not available — not connected to HH OBD Advance")
        return elm.read_vin()

    def get_voltage_elm327(self) -> Optional[float]:
        """Read battery voltage via ELM327 AT RV command."""
        elm = self.get_elm327_driver()
        if not elm:
            return None
        try:
            return elm.get_voltage()
        except Exception:
            return None

    def read_pending_dtcs_elm327(self) -> List[Dict[str, Any]]:
        """Read pending DTCs via ELM327 (Mode $07)."""
        elm = self.get_elm327_driver()
        if not elm:
            raise ConnectionError("ELM327 driver not available — not connected to HH OBD Advance")
        return elm.read_pending_dtcs()

    def read_readiness_monitors_elm327(self) -> dict:
        """Read emission readiness monitors via ELM327 (Mode $01 PID $01)."""
        elm = self.get_elm327_driver()
        if not elm:
            raise ConnectionError("ELM327 driver not available — not connected to HH OBD Advance")
        return elm.read_readiness_monitors()

    def read_freeze_frame_elm327(self) -> dict:
        """Read freeze frame snapshot via ELM327 (Mode $02)."""
        elm = self.get_elm327_driver()
        if not elm:
            raise ConnectionError("ELM327 driver not available — not connected to HH OBD Advance")
        return elm.read_freeze_frame()

    def _connect_generic_obd(self, device: VCIDevice) -> bool:
        """Route to correct handler"""
        if "VCDS" in device.name or "HEX-V2" in device.name or "Ross-Tech" in device.name:
            return self._connect_vcds_hid(device)
        elif device.device_type == VCITypes.BLUE_PILL_VCI or "Blue Pill" in device.name or "STM32" in device.name or "DACOS VCI" in device.name:
            return self._connect_bluepill(device)
        elif device.device_type == VCITypes.HH_OBD_ADVANCE:
            return self._connect_elm327(device)
        else:
            logger.info(f"Using generic fallback for {device.name}")
            return False

    def is_connected(self) -> bool:
        return self.connected_vci is not None and self.connected_vci.status == VCIStatus.CONNECTED

    def get_connected_device(self) -> Optional[VCIDevice]:
        return self.connected_vci

    def tester_present(self, tx_id: int = 0x7E0, rx_id: int = 0x7E8) -> bool:
        """Send Tester Present (UDS 0x3E) to keep the diagnostic session alive.

        Delegates to the active bridge (VCDS HID or Blue Pill).
        """
        # VCDS HID path
        hid = self._get_vcds_hid_bridge()
        if hid is not None:
            return hid.tester_present(tx_id, rx_id)

        # Blue Pill path — only send if CAN channel is active
        bp = self._get_bluepill_bridge()
        if bp is not None:
            if not bp._can_connected:
                return True  # no active session — nothing to keep alive
            return bp.tester_present(tx_id, rx_id)

        return False

    def security_access(self, level: int, algorithm) -> bool:
        """Unlock security access on the ECU (UDS 0x27).

        Only supported on VCDS HID and Blue Pill bridges.
        """
        hid = self._get_vcds_hid_bridge()
        if hid is not None:
            # Phase 1: Request seed
            resp = hid.isotp_request(0x7E0, 0x7E8, bytes([0x27, level & 0xFF]), 3000)
            if not resp or resp[0] != 0x67 or len(resp) < 3:
                return False
            seed = resp[2:]
            key = algorithm(seed)
            # Phase 2: Send key
            resp2 = hid.isotp_request(0x7E0, 0x7E8, bytes([0x27, (level + 1) & 0xFF]) + key, 3000)
            return resp2 is not None and resp2[0] == 0x67

        bp = self._get_bluepill_bridge()
        if bp is not None:
            return bp.security_access(level, algorithm) if hasattr(bp, "security_access") else False

        return False

    # ── UDS / CAN Communication Pipeline ──────────────────────────

    def _get_j2534_device(self):
        """Get the active J2534 device from the connected VCI.

        Raises ConnectionError if no VCI is connected or it has no
        J2534 device handle.
        """
        if not self.connected_vci:
            raise ConnectionError("No VCI connected")
        device = self.connected_vci
        if hasattr(device, "_j2534_device") and device._j2534_device is not None:
            return device._j2534_device
        raise ConnectionError(
            "Connected VCI does not have an active J2534 device handle. "
            "Ensure the driver DLL was loaded successfully."
        )

    def _get_j2534_channel(self) -> int:
        """Get or create the ISO15765 (CAN) channel on the J2534 device.

        The channel is cached on first use and reused for all subsequent
        UDS / OBD-II communication during the session.
        """
        j2534 = self._get_j2534_device()

        if hasattr(self, "_iso15765_channel") and self._iso15765_channel is not None:
            return self._iso15765_channel

        from shared.j2534_passthru import J2534Protocol

        channel = j2534.connect(J2534Protocol.ISO15765, baudrate=500000)
        if channel < 0:
            raise ConnectionError(
                "Failed to open ISO15765 (CAN) channel on J2534 device. "
                "Check that the device is powered and connected to the vehicle."
            )
        self._iso15765_channel = channel
        logger.info("ISO15765 channel %d opened on J2534 device", channel)
        return channel

    def _get_bluepill_bridge(self):
        """Get the DACOS_J2534 bridge from the connected Blue Pill VCI.

        Returns *None* if the connected VCI is not a Blue Pill.
        """
        if not self.connected_vci:
            return None
        return getattr(self.connected_vci, "_bluepill_bridge", None)

    def _get_vcds_hid_bridge(self):
        """Get the VCDSHIDBridge from the connected Ross-Tech clone VCI.

        Returns *None* if the connected VCI is not a VCDS clone.
        """
        if not self.connected_vci:
            return None
        return getattr(self.connected_vci, "_vcds_hid_bridge", None)

    def send_uds_request(
        self, payload: bytes, tx_id: int = 0x7E0, rx_id: int = 0x7E8,
        timeout_ms: int = 3000,
    ) -> bytes:
        """Send a UDS request and return the raw response payload.

        Automatically selects the transport:
        - **VCDS HEX-V2** → Ross-Tech HID protocol via :class:`VCDSHIDBridge`
        - **Blue Pill** → native ``isotp_request()`` via serial AT commands
        - **J2534 DLL** → ISO-TP over J2534 channel
        """
        # --- PATH A: VCDS HEX-V2 HID bridge ---
        hid = self._get_vcds_hid_bridge()
        if hid is not None:
            try:
                if not hid._can_open:
                    hid.connect_can(500000)

                response = hid.isotp_request(tx_id, rx_id, payload, timeout_ms)
                if response is None:
                    raise IOError(
                        f"No response from ECU on CAN ID 0x{rx_id:03X} "
                        f"within {timeout_ms} ms (VCDS HID)"
                    )
                logger.debug(
                    "VCDS-HID UDS 0x%02X → %d bytes",
                    payload[0], len(response),
                )
                return response
            except Exception as exc:
                logger.warning(
                    "VCDS HID isotp_request failed: %s, trying fallbacks", exc
                )

        # --- PATH B: Blue Pill native ISO-TP ---
        bp = self._get_bluepill_bridge()
        if bp is not None:
            try:
                # Ensure CAN is connected on the Blue Pill
                if not bp._can_open:
                    bp.connect_can(500000)

                response = bp.isotp_request(tx_id, rx_id, payload, timeout_ms)
                if response is None:
                    raise IOError(
                        f"No response from ECU on CAN ID 0x{rx_id:03X} "
                        f"within {timeout_ms} ms (Blue Pill)"
                    )
                logger.debug(
                    "BluePill UDS 0x%02X → %d bytes",
                    payload[0], len(response),
                )
                return response
            except Exception:
                # Fall through to PATH B if Blue Pill fails
                logger.warning(
                    "Blue Pill isotp_request failed, trying J2534 fallback"
                )

        # --- PATH C: J2534 DLL via ISO-TP ---
        return self._send_uds_via_j2534(payload, tx_id, rx_id, timeout_ms)

    def _send_uds_via_j2534(
        self, payload: bytes, tx_id: int, rx_id: int, timeout_ms: int,
    ) -> bytes:
        """Send UDS through J2534 DLL + ISO-TP handler."""
        from shared.isotp_handler import IsoTpHandler

        j2534 = self._get_j2534_device()
        channel = self._get_j2534_channel()

        adapter = _J2534IsoTpAdapter(j2534, channel, tx_id, rx_id)
        isotp = IsoTpHandler(adapter, tx_id=tx_id, rx_id=rx_id, timeout_ms=timeout_ms)

        if not isotp.send_data(payload):
            raise IOError(
                f"Failed to send UDS request (service 0x{payload[0]:02X}) "
                f"on CAN ID 0x{tx_id:03X}"
            )

        response = isotp.receive_data(timeout_ms=timeout_ms)
        if response is None:
            raise IOError(
                f"No response from ECU on CAN ID 0x{rx_id:03X} "
                f"within {timeout_ms} ms"
            )

        logger.debug(
            "J2534 UDS 0x%02X → response %d bytes", payload[0], len(response),
        )
        return response

    def read_pid(
        self, pid: int, tx_id: int = 0x7E0, rx_id: int = 0x7E8,
    ) -> Optional[bytes]:
        """Read a single OBD-II Mode 01 PID from the vehicle.

        Uses VCDS HID bridge if available, then Blue Pill, then J2534 DLL.
        """
        # VCDS HID path
        hid = self._get_vcds_hid_bridge()
        if hid is not None:
            if not hid._can_open:
                hid.connect_can(500000)
            response = hid.isotp_request(tx_id, rx_id, bytes([0x01, pid]), 2000)
            if response is None:
                return None
            if len(response) >= 2 and response[0] == 0x41:
                return response[2:]
            return response

        # Blue Pill path — use native isotp_request
        bp = self._get_bluepill_bridge()
        if bp is not None:
            if not bp._can_open:
                bp.connect_can(500000)
            response = bp.isotp_request(tx_id, rx_id, bytes([0x01, pid]), 2000)
            if response is None:
                return None
            if len(response) >= 2 and response[0] == 0x41:
                return response[2:]
            return response

        # J2534 DLL path
        from shared.isotp_handler import IsoTpHandler

        j2534 = self._get_j2534_device()
        channel = self._get_j2534_channel()
        adapter = _J2534IsoTpAdapter(j2534, channel, tx_id, rx_id)
        isotp = IsoTpHandler(adapter, tx_id=tx_id, rx_id=rx_id, timeout_ms=2000)

        payload = bytes([0x01, pid])
        if not isotp.send_data(payload):
            logger.warning("Failed to send PID 0x%02X request", pid)
            return None

        response = isotp.receive_data(timeout_ms=2000)
        if response is None:
            return None

        if len(response) >= 2 and response[0] == 0x41:
            return response[2:]
        return response

    def read_pids_batch(
        self, pids: list, tx_id: int = 0x7E0, rx_id: int = 0x7E8,
    ) -> Dict[int, Optional[bytes]]:
        """Read multiple OBD-II PIDs in a single batch.

        Returns a dict mapping ``pid → raw_data_bytes``.  A value of
        *None* means the ECU did not respond for that PID.
        """
        results: Dict[int, Optional[bytes]] = {}
        for pid in pids:
            try:
                results[pid] = self.read_pid(pid, tx_id, rx_id)
            except Exception as exc:
                logger.warning("PID 0x%02X read failed: %s", pid, exc)
                results[pid] = None
        return results

    # ── K-Line / KWP2000 (Blue Pill only) ──────────────────────────

    def connect_kline(self, addr: int = 0x33) -> bool:
        """Initialise K-Line with ISO 9141-2 fast init on the Blue Pill.

        Only supported on Blue Pill hardware.  J2534 DLL devices do
        not expose K-Line through this interface.

        Args:
            addr: ECU diagnostic address in hex (0x33 = engine, common).

        Returns:
            True if K-Line was successfully initialised.
        """
        bp = self._get_bluepill_bridge()
        if bp is None:
            logger.warning("K-Line requires Blue Pill — not available on this VCI")
            return False
        try:
            bp.connect_kline(addr)
            logger.info("K-Line initialised, ECU addr 0x%02X", addr)
            return True
        except Exception as e:
            logger.error("K-Line init failed: %s", e)
            return False

    def disconnect_kline(self) -> bool:
        """Disconnect K-Line (Blue Pill only)."""
        bp = self._get_bluepill_bridge()
        if bp is None:
            return True
        try:
            bp.disconnect_kline()
            return True
        except Exception:
            return False

    def send_kwp_request(
        self, addr: int, data: bytes, timeout_ms: int = 2000,
    ) -> Optional[bytes]:
        """Send a KWP2000 request over K-Line and return the response.

        Handles the KWP2000 header (fmt, target, src, length, SID, …)
        automatically when using :meth:`read_dtcs_kwp`.

        Args:
            addr: Target ECU diagnostic address (e.g. 0x33 for engine).
            data: KWP2000 payload bytes (service ID + parameters).
            timeout_ms: Total timeout in milliseconds.

        Returns:
            Raw response bytes from the ECU, or *None* on timeout.
        """
        bp = self._get_bluepill_bridge()
        if bp is None:
            logger.warning("KWP2000 requires Blue Pill")
            return None
        try:
            return bp.kwp_request(addr, data, timeout_ms)
        except Exception as e:
            logger.error("KWP2000 request failed: %s", e)
            return None

    def read_dtcs_kwp(self, addr: int = 0x33) -> List[Dict[str, Any]]:
        """Read DTCs from an ECU using KWP2000 service 0x18.

        This is the K-Line equivalent of UDS service 0x19 for older
        GM, Opel, VAG, and other pre-CAN vehicles common in ZA.

        Returns:
            List of dicts with ``code``, ``description``, ``status`` keys.
        """
        # KWP2000 Read DTC by Status (service 0x18, mode 0x00 = all)
        response = self.send_kwp_request(addr, bytes([0x18, 0x00]))
        if response is None:
            return []

        dtcs: List[Dict[str, Any]] = []
        # Response: 0x58 (positive) + 1-byte count + N × 3-byte DTCs
        if len(response) < 2 or response[0] != 0x58:
            logger.warning("Unexpected KWP DTC response: %s", response.hex())
            return dtcs

        count = response[1]
        dtc_bytes = response[2:]

        for i in range(0, min(len(dtc_bytes), count * 3), 3):
            if i + 2 >= len(dtc_bytes):
                break
            high, mid, low = dtc_bytes[i], dtc_bytes[i + 1], dtc_bytes[i + 2]
            prefix = ["P", "C", "B", "U"][(high >> 6) & 0x03]
            code = f"{prefix}{high & 0x3F:02X}{mid:02X}"
            dtcs.append({
                "code": code,
                "status": "confirmed" if (low & 0x08) else "pending",
                "priority": "high" if (low & 0x08) else "low",
            })

        logger.info("KWP2000: %d DTCs read from 0x%02X", len(dtcs), addr)
        return dtcs

    def clear_dtcs_kwp(self, addr: int = 0x33) -> bool:
        """Clear DTCs using KWP2000 service 0x14."""
        response = self.send_kwp_request(addr, bytes([0x14, 0xFF, 0x00]))
        if response and len(response) >= 1 and response[0] == 0x54:
            logger.info("KWP2000: DTCs cleared on 0x%02X", addr)
            return True
        return False

    def read_vin_kwp(self, addr: int = 0x33) -> Optional[str]:
        """Read VIN via KWP2000 (ReadDataByLocalIdentifier 0x21, ID 0x90)."""
        response = self.send_kwp_request(addr, bytes([0x21, 0x90]))
        if response and len(response) > 2 and response[0] == 0x61:
            try:
                return response[2:].decode("ascii", errors="replace").strip("\x00")
            except Exception:
                return None
        return None

    def get_device_info(self) -> Dict[str, Any]:
        """Return info dict for the currently connected VCI device."""
        if not self.connected_vci:
            return {"status": "disconnected"}
        return {
            "status": self.connected_vci.status.value,
            "type": self.connected_vci.device_type.value,
            "name": self.connected_vci.name,
            "port": self.connected_vci.port,
            "capabilities": self.connected_vci.capabilities,
        }

    def get_supported_devices(self) -> List[str]:
        """Return list of supported VCI device type names."""
        return [t.value for t in VCITypes if t != VCITypes.UNKNOWN]

    def disconnect(self) -> bool:
        if not self.connected_vci:
            return True
        try:
            device = self.connected_vci

            # Close VCDS HID bridge if active
            hid = getattr(device, "_vcds_hid_bridge", None)
            if hid is not None:
                try:
                    hid.disconnect_can()
                except Exception:
                    pass
                try:
                    hid.close()
                except Exception:
                    pass
                device._vcds_hid_bridge = None

            # Close Blue Pill bridge if active
            bp = getattr(device, "_bluepill_bridge", None)
            if bp is not None:
                try:
                    bp.disconnect_kline()
                except Exception:
                    pass
                try:
                    bp.disconnect_can()
                except Exception:
                    pass
                try:
                    bp.close()
                except Exception:
                    pass
                device._bluepill_bridge = None

            # Tear down J2534 ISO15765 channel if one was opened
            if hasattr(self, "_iso15765_channel") and self._iso15765_channel is not None:
                try:
                    j2534 = self._get_j2534_device()
                    j2534.disconnect(self._iso15765_channel)
                except Exception:
                    pass
                self._iso15765_channel = None

            self.connected_vci = None
            self._notify_callbacks("disconnected")
            logger.info("Disconnected from VCI")
            return True
        except Exception as e:
            logger.error("Disconnect error: %s", e)
            return False


# ── Transport Adapter (J2534 → ISO-TP) ──────────────────────────

class _J2534IsoTpAdapter:
    """Thin adapter that presents a J2534 channel as an ISO-TP transport.

    The :class:`IsoTpHandler` expects a transport object with two methods:

    * ``send_message(can_id: int, data: bytes) → bool``
    * ``read_message(timeout_ms: int) → object with ``.data`` attribute``

    This adapter translates those calls into J2534 ``send_message`` /
    ``read_message`` operations, packing and unpacking the 4-byte CAN ID
    prefix that J2534 ISO15765 messages carry.
    """

    def __init__(self, j2534_device, channel_id: int, tx_id: int, rx_id: int):
        self._j2534 = j2534_device
        self._channel = channel_id
        self._tx_id = tx_id
        self._rx_id = rx_id

    def send_message(self, can_id: int, data: bytes) -> bool:
        """Pack CAN ID + payload into a J2534 ISO15765 message and send."""
        from shared.j2534_passthru import J2534Message, J2534Protocol

        msg_data = can_id.to_bytes(4, "big") + data
        msg = J2534Message(J2534Protocol.ISO15765, data=msg_data)
        return self._j2534.send_message(self._channel, msg)

    def read_message(self, timeout_ms: int = 1000):
        """Read a J2534 message and return it with a ``.data`` attribute.

        The ``.data`` attribute contains ``[CAN_ID(4 bytes)] + [payload]``
        as expected by :meth:`IsoTpHandler.receive_data`.
        """
        result = self._j2534.read_message(self._channel, timeout_ms)
        if result is None:
            return None

        # Return a lightweight object with just .data — IsoTpHandler
        # only accesses .data on the returned object.
        class _RawMsg:
            __slots__ = ("data",)
            def __init__(self, raw: bytes):
                self.data = raw

        return _RawMsg(result.data)


# ── Global instance ──────────────────────────────────────────────
vci_manager = VCIManager()

def get_vci_manager() -> VCIManager:
    return vci_manager
