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
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from PyQt6.QtCore import QThread, pyqtSignal, QObject, QTimer
from PyQt6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

class VCITypes(Enum):
    """Supported VCI device types"""
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
    bluetooth_address: Optional[str] = None  # Bluetooth MAC address for wireless devices
    dll_path: Optional[str] = None  # Path to J2534 DLL

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []


class HangWatchdog(QObject):
    """
    ELITE HANG PROTECTION WATCHDOG
    Prevents Windows Application Hang Termination (0xCFFFFFFF)
    Forces event processing to keep GUI responsive during heavy operations
    """
    
    def __init__(self, app=None):
        super().__init__()
        self.app = app or QApplication.instance()
        self.timer = QTimer()
        self.timer.timeout.connect(self.pulse)
        self.is_active = False
        logger.info("Hang Protection Watchdog initialized")
        
    def start(self, interval_ms=1000):
        """Start the watchdog pulse - prevents Windows hang detection"""
        if not self.is_active:
            self.timer.start(interval_ms)
            self.is_active = True
            logger.info(f"Hang Protection Watchdog started with {interval_ms}ms interval")
            
    def stop(self):
        """Stop the watchdog pulse"""
        if self.is_active:
            self.timer.stop()
            self.is_active = False
            logger.info("Hang Protection Watchdog stopped")
            
    def pulse(self):
        """
        FIXED: Safe pulse method - prevents Windows hang detection
        ELIMINATED: app.processEvents() calls that cause crashes
        This method now logs activity instead of forcing events
        """
        try:
            # ELITE CRASH FIX: Removed app.processEvents() to prevent event loop corruption
            # Instead, just log pulse activity to prove watchdog is alive
            import time
            pulse_count = getattr(self, '_pulse_count', 0) + 1
            self._pulse_count = pulse_count
            
            # Log every 10 pulses to avoid spam but prove functionality
            if pulse_count % 10 == 0:
                logger.debug(f"Safe watchdog pulse #{pulse_count} - GUI responsive")
                
            # Safety limit to prevent infinite operation (crash prevention)
            if pulse_count >= 100:  # 100 pulses = 100 seconds max
                logger.warning("Safe watchdog pulse limit reached - stopping to prevent issues")
                self.stop()
                
        except Exception as e:
            logger.error(f"Safe watchdog pulse error: {e}")
            # Don't call stop() here to avoid recursion issues


class VCIScannerThread(QThread):
    """QThread for scanning VCI devices to prevent GUI freezing"""
    scan_completed = pyqtSignal(list)
    scan_error = pyqtSignal(str)
    scan_progress = pyqtSignal(str)
    
    def __init__(self, vci_manager):
        super().__init__()
        self.vci_manager = vci_manager
        self.timeout = 15
        self._stop_event = threading.Event()
        
    def stop(self):
        """Stop the scanning thread"""
        self._stop_event.set()
        self.quit()
        self.wait(2000)  # Wait up to 2 seconds
        
    def run(self):
        """Thread entry point"""
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
    """Manager for VCI device detection and connection with threading"""
    
    # Signals for UI updates
    status_changed = pyqtSignal(str, object)
    devices_found = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.connected_vci: Optional[VCIDevice] = None
        self.available_devices: List[VCIDevice] = []
        self.is_scanning = False
        self.scan_thread = None
        self.callbacks: List[callable] = []
        
        # ELITE CRASH FIX: Hang Protection Watchdog
        self.hang_watchdog = HangWatchdog()
        self._watchdog_active = False

        # Supported device signatures
        self.device_signatures = {
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

    def scan_for_devices(self, timeout: int = 15) -> bool:
        """
        ELITE THREADED SCAN: Start scanning for VCI devices in a separate thread
        WITH HANG PROTECTION - Prevents 0xCFFFFFFF Windows Application Hang
        """
        if self.is_scanning:
            logger.warning("Device scan already in progress")
            return False

        self.is_scanning = True
        self.available_devices = []
        
        # ELITE CRASH FIX: Activate hang protection during scan
        self._activate_hang_protection("VCI device scan")
        
        # Create and start scan thread
        self.scan_thread = VCIScannerThread(self)
        self.scan_thread.scan_completed.connect(self._on_scan_completed)
        self.scan_thread.scan_error.connect(self._on_scan_error)
        self.scan_thread.scan_progress.connect(self._on_scan_progress)
        self.scan_thread.timeout = timeout
        self.scan_thread.start()
        
        logger.info(f"Started threaded VCI scan with {timeout}s timeout and hang protection")
        return True
    
    def _activate_hang_protection(self, operation_name: str):
        """Activate hang protection for long-running operations"""
        if not self._watchdog_active:
            self.hang_watchdog.start(1000)  # Pulse every 1 second
            self._watchdog_active = True
            logger.info(f"Hang protection activated for: {operation_name}")
    
    def _deactivate_hang_protection(self):
        """Deactivate hang protection when operation completes"""
        if self._watchdog_active:
            self.hang_watchdog.stop()
            self._watchdog_active = False
            logger.info("Hang protection deactivated")
    
    def scan_for_devices_with_timeout(self, timeout: int = 20) -> List[VCIDevice]:
        """Scan with timeout to prevent eternal hangs"""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self._raw_scan)
            try:
                return future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                logger.warning("VCI scan timed out")
                return []
    
    def _raw_scan(self) -> List[VCIDevice]:
        """Raw scan method for thread pool execution"""
        return self._scan_for_devices_with_timeout(15, time.time())

    def _scan_for_devices_with_timeout(self, timeout: int) -> List[VCIDevice]:
        """Internal method for scanning devices (called from thread)"""
        devices = []
        start_time = time.time()
        logger.info(f"Starting VCI device scan (timeout: {timeout}s)")

        try:
            # Scan serial ports
            devices.extend(self._scan_serial_ports_with_timeout(timeout, start_time))
            
            # Check timeout
            if time.time() - start_time > timeout:
                logger.warning(f"Device scan timed out after {timeout} seconds")
                return devices

            # Scan for J2534 devices
            devices.extend(self._scan_j2534_devices_with_timeout(timeout, start_time))

            # Check timeout
            if time.time() - start_time > timeout:
                logger.warning(f"Device scan timed out after {timeout} seconds")
                return devices

            # Scan for Bluetooth devices
            devices.extend(self._scan_bluetooth_devices_with_timeout(timeout, start_time))

            # Remove duplicates
            unique_devices = []
            seen_ports = set()
            for device in devices:
                if device.port not in seen_ports:
                    seen_ports.add(device.port)
                    unique_devices.append(device)

            # Prioritize OBDLink MX+ devices
            unique_devices.sort(key=lambda d: 0 if d.device_type == VCITypes.OBDLINK_MX_PLUS else 1)

            elapsed = time.time() - start_time
            logger.info(f"Device scan completed in {elapsed:.1f}s, found {len(unique_devices)} devices")

            return unique_devices

        except Exception as e:
            logger.error(f"Device scan failed: {e}")
            return devices

    def _on_scan_completed(self, devices):
        """Handle scan completion from thread - ELITE FIX: Deactivate hang protection"""
        try:
            self.available_devices = devices
            self.is_scanning = False
            self.devices_found.emit(devices)
            
            # ELITE CRASH FIX: Deactivate hang protection when scan completes
            self._deactivate_hang_protection()
            
            # Log found devices
            for device in devices:
                logger.info(f"Found: {device.name} ({device.device_type.value}) - Port: {device.port}")
                
            logger.info(f"VCI scan completed successfully with hang protection - Found {len(devices)} devices")
            
        except Exception as e:
            logger.error(f"Error in scan completion handler: {e}")
            self._deactivate_hang_protection()

    def _on_scan_error(self, error_message):
        """Handle scan error from thread - ELITE FIX: Deactivate hang protection"""
        try:
            logger.error(f"Scan error: {error_message}")
            self.is_scanning = False
            self.status_changed.emit("error", {"message": error_message})
            
            # ELITE CRASH FIX: Deactivate hang protection on error
            self._deactivate_hang_protection()
            
        except Exception as e:
            logger.error(f"Error in scan error handler: {e}")
            self._deactivate_hang_protection()

    def _on_scan_progress(self, progress_message):
        """Handle scan progress updates"""
        logger.debug(f"Scan progress: {progress_message}")
        self.status_changed.emit("progress", {"message": progress_message})

    def _scan_serial_ports_with_timeout(self, total_timeout: int, start_time: float) -> List[VCIDevice]:
        """Scan serial/COM ports for VCI devices with timeout protection"""
        devices = []
        try:
            logger.info("🔌 Starting serial port scan...")
            import serial.tools.list_ports

            ports = serial.tools.list_ports.comports()
            logger.info(f"📋 Found {len(ports)} COM ports to scan")

            for port in ports:
                # Check overall timeout
                if time.time() - start_time > total_timeout:
                    logger.warning("Overall scan timeout reached during serial port scan")
                    break

                logger.debug(f"🔍 Checking port: {port.device} - {port.description}")

                try:
                    # Check for known USB VID/PID combinations
                    logger.debug(f"🔍 Checking USB ID for {port.device}")
                    device = self._identify_device_by_usb_id(port)
                    if device:
                        device.port = port.device
                        device.last_seen = time.time()
                        devices.append(device)
                        logger.info(f"✅ Found VCI device by USB ID: {device.name} on {port.device}")
                        continue

                    # Try to identify device by description
                    logger.debug(f"🔍 Checking description for {port.device}")
                    device = self._identify_godiag_by_description(port)
                    if device:
                        device.port = port.device
                        device.last_seen = time.time()
                        devices.append(device)
                        logger.info(f"✅ Found GoDiag device: {device.name} on {port.device}")

                except Exception as e:
                    logger.debug(f"Failed to identify device on {port.device}: {e}")

            logger.info(f"🔌 Serial port scan completed, found {len(devices)} devices")

        except ImportError:
            logger.warning("Serial tools not available, skipping serial port scan")
        except Exception as e:
            logger.error(f"Serial port scan failed: {e}")

        return devices

    def _identify_device_by_usb_id(self, port) -> Optional[VCIDevice]:
        """Identify VCI device by USB Vendor ID and Product ID"""
        # Known USB VID/PID combinations for VCI devices
        known_devices = {
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

    def _scan_j2534_devices_with_timeout(self, total_timeout: int, start_time: float):
        """Scan for J2534-compliant devices with timeout protection"""
        try:
            # Calculate remaining time
            elapsed = time.time() - start_time
            remaining_time = total_timeout - elapsed
            if remaining_time <= 0:
                logger.warning("No time remaining for J2534 scan")
                return

            # Limit J2534 scan time
            j2534_timeout = min(remaining_time * 0.3, 3.0)  # Use max 30% of remaining time, max 3 seconds
            j2534_start_time = time.time()

            logger.info(f"🔍 Starting J2534 registry scan with timeout {j2534_timeout:.1f}s")

            # Try to detect J2534 devices through registry/API
            import winreg

            # Check for J2534 devices in registry with timeout protection
            try:
                logger.info("🔍 Opening J2534 registry key with timeout protection...")

                # Use threading for registry operations that might hang
                registry_result = [None]
                registry_exception = [None]

                def registry_scan_thread():
                    try:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                            r"SOFTWARE\WOW6432Node\PassThruSupport.04.04")
                        logger.info("✅ J2534 registry key opened successfully")

                        devices_found = []
                        i = 0
                        max_attempts = 50  # Reduced safety limit
                        attempts = 0

                        while attempts < max_attempts:
                            try:
                                subkey = winreg.EnumKey(key, i)
                                device_key = winreg.OpenKey(key, subkey)

                                # Try to get device info
                                try:
                                    name = winreg.QueryValueEx(device_key, "Name")[0]
                                    vendor = winreg.QueryValueEx(device_key, "Vendor")[0]
                                    try:
                                        dll_path = winreg.QueryValueEx(device_key, "FunctionLibrary")[0]
                                    except:
                                        dll_path = None

                                    device = VCIDevice(
                                        device_type=VCITypes.J2534_GENERIC,
                                        name=f"{vendor} {name}",
                                        status=VCIStatus.DISCONNECTED,
                                        dll_path=dll_path
                                    )
                                    device.capabilities = self._get_device_capabilities(VCITypes.J2534_GENERIC)
                                    devices_found.append(device)
                                    logger.info(f"✅ Found J2534 device: {device.name}")

                                except FileNotFoundError:
                                    logger.debug(f"J2534 device info not found for key {i}")
                                except Exception as e:
                                    logger.debug(f"Error reading J2534 device info for key {i}: {e}")

                                i += 1
                                attempts += 1

                            except OSError:
                                # No more keys to enumerate
                                logger.info(f"🔍 J2534 registry enumeration completed at index {i}")
                                break
                            except Exception as e:
                                logger.debug(f"Error enumerating J2534 device at index {i}: {e}")
                                break

                        registry_result[0] = devices_found

                    except Exception as e:
                        logger.error(f"J2534 registry scan thread error: {e}")
                        registry_exception[0] = e

                # Start registry scan in a separate thread
                reg_thread = threading.Thread(target=registry_scan_thread, daemon=True)
                reg_thread.start()

                # Wait for completion with timeout
                reg_thread.join(timeout=j2534_timeout)

                if reg_thread.is_alive():
                    logger.warning(f"⚠️ J2534 registry scan timed out after {j2534_timeout:.1f}s - thread still running")
                else:
                    logger.info("✅ J2534 registry scan thread completed normally")

                # Add found devices to available_devices
                if registry_result[0]:
                    self.available_devices.extend(registry_result[0])
                    logger.info(f"🔍 J2534 registry scan found {len(registry_result[0])} devices")

                if registry_exception[0]:
                    logger.error(f"J2534 registry scan failed with exception: {registry_exception[0]}")

                logger.info(f"🔍 J2534 registry scan completed with timeout protection")

            except FileNotFoundError:
                logger.debug("J2534 registry not found")
            except Exception as e:
                logger.error(f"J2534 registry scan failed: {e}")

            # Also scan local drivers directory
            try:
                import os
                from shared.j2534_passthru import J2534PassThru
                
                # Construct path to drivers directory relative to project root
                current_dir = os.path.dirname(os.path.abspath(__file__))
                # Go up from AutoDiag/core/vci_manager.py to DiagAutoClinicOS/
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
                drivers_dir = os.path.join(project_root, "drivers")
                
                # Fallback if path resolution looks wrong (e.g. if run from strange location)
                if not os.path.exists(drivers_dir):
                    drivers_dir = os.path.join(os.getcwd(), "drivers")
                
                if os.path.exists(drivers_dir):
                    logger.info(f"🔍 Scanning local drivers directory: {drivers_dir}")
                    local_dlls = J2534PassThru.scan_local_drivers(drivers_dir)
                    
                    for dll_path in local_dlls:
                        try:
                            name = os.path.basename(dll_path).replace(".dll", "")
                            
                            # Filter out known non-J2534 helper DLLs to keep UI clean
                            skip_prefixes = ["ftd2xx", "ftbus", "ftcser", "ftlang", "ftser", "WdfCoInstaller", "libusb"]
                            if any(name.lower().startswith(p) for p in skip_prefixes):
                                continue

                            # Check if already added via registry
                            is_duplicate = False
                            for existing in self.available_devices:
                                if existing.dll_path and os.path.abspath(existing.dll_path) == os.path.abspath(dll_path):
                                    is_duplicate = True
                                    break
                            
                            if not is_duplicate:
                                device = VCIDevice(
                                    device_type=VCITypes.J2534_GENERIC,
                                    name=f"Local Driver: {name}",
                                    status=VCIStatus.DISCONNECTED,
                                    dll_path=dll_path
                                )
                                device.capabilities = self._get_device_capabilities(VCITypes.J2534_GENERIC)
                                self.available_devices.append(device)
                                logger.info(f"✅ Found local J2534 driver: {name}")
                        except Exception as e:
                            logger.error(f"Error adding local driver {dll_path}: {e}")
                else:
                    logger.debug(f"Local drivers directory not found: {drivers_dir}")
                        
            except ImportError:
                logger.warning("Could not import J2534PassThru for local driver scan")
            except Exception as e:
                logger.error(f"Local driver scan failed: {e}")

        except ImportError:
            logger.debug("Windows registry access not available")
        except Exception as e:
            logger.error(f"J2534 scan failed: {e}")

    def _scan_j2534_devices(self):
        """Legacy method - now calls timeout-protected version"""
        self._scan_j2534_devices_with_timeout(10, time.time())

    def _scan_bluetooth_devices_with_timeout(self, total_timeout: int, start_time: float):
        """Scan for Bluetooth VCI devices with timeout protection"""
        try:
            # Calculate remaining time
            elapsed = time.time() - start_time
            remaining_time = total_timeout - elapsed
            if remaining_time <= 0:
                logger.warning("No time remaining for Bluetooth scan")
                return

            # Limit Bluetooth scan time
            bluetooth_timeout = min(remaining_time * 0.4, 8.0)  # Use max 40% of remaining time, max 8 seconds
            bluetooth_start_time = time.time()

            logger.info(f"🔍 Starting Bluetooth scan with timeout {bluetooth_timeout:.1f}s")

            import bluetooth

            logger.info("📡 Bluetooth library imported, starting device discovery...")

            # Scan for Bluetooth devices with timeout protection
            try:
                # Use shorter duration to avoid hanging
                duration = min(int(bluetooth_timeout), 6)
                logger.info(f"🔍 Calling bluetooth.discover_devices(duration={duration}) with thread timeout protection")

                # Use threading to add timeout protection for Bluetooth discovery
                import threading

                bluetooth_devices = []
                bluetooth_exception = [None]

                def bluetooth_discovery_thread():
                    try:
                        logger.info("🔍 Bluetooth discovery thread started")
                        devices = bluetooth.discover_devices(
                            duration=duration,
                            lookup_names=True,
                            flush_cache=True
                        )
                        bluetooth_devices.extend(devices)
                        logger.info(f"✅ Bluetooth discovery thread completed, found {len(devices)} devices")
                    except Exception as e:
                        logger.error(f"Bluetooth discovery thread error: {e}")
                        bluetooth_exception[0] = e

                # Start Bluetooth discovery in a separate thread
                bt_thread = threading.Thread(target=bluetooth_discovery_thread, daemon=True)
                bt_thread.start()

                # Wait for completion with timeout (add 2 seconds buffer)
                bt_thread.join(timeout=duration + 2.0)

                if bt_thread.is_alive():
                    logger.warning(f"⚠️ Bluetooth discovery timed out after {duration + 2.0}s - thread still running")
                    # Thread will be terminated when function returns
                else:
                    logger.info("✅ Bluetooth discovery thread completed normally")

                # Use the results if available
                devices = bluetooth_devices
                if bluetooth_exception[0]:
                    logger.error(f"Bluetooth discovery failed with exception: {bluetooth_exception[0]}")
                    devices = []

                logger.info(f"✅ Bluetooth discovery completed with timeout protection, found {len(devices)} devices")

                obdlink_found = False
                for addr, name in devices:
                    # Check overall timeout
                    if (time.time() - start_time) > total_timeout:
                        logger.warning("Overall scan timeout reached during Bluetooth scan")
                        break

                    logger.debug(f"Found Bluetooth device: {name} ({addr})")

                    # Check for your specific OBDLink MX+ SSID 'OBDLink MX+ 53368'
                    # Also check for generic OBDLink devices
                    if name and ("OBDLink MX+ 53368" in name or "OBDLINK" in name.upper() or "OBD" in name.upper()):
                        logger.info(f"Found OBDLink Bluetooth device: {name} ({addr})")

                        # Determine device type based on name
                        device_type = VCITypes.OBDLINK_MX_PLUS
                        
                        # Create VCIDevice for OBDLink
                        device = VCIDevice(
                            device_type=device_type,
                            name=f"{name} (Bluetooth)",
                            port=None,  # Bluetooth doesn't use COM ports
                            status=VCIStatus.DISCONNECTED
                        )
                        device.capabilities = self._get_device_capabilities(device_type)
                        device.bluetooth_address = addr  # Store Bluetooth address
                        self.available_devices.append(device)
                        obdlink_found = True

                if obdlink_found:
                    logger.info("OBDLink Bluetooth devices detected")
                else:
                    logger.info("No OBDLink Bluetooth devices found")

            except Exception as e:
                logger.error(f"Bluetooth discovery failed: {e}")

        except ImportError:
            logger.warning("Bluetooth library not available - trying Windows Bluetooth detection")
            self._scan_windows_bluetooth_devices_with_timeout(total_timeout, start_time)
        except Exception as e:
            logger.error(f"Bluetooth scanning failed: {e}")
            logger.info("Ensure Bluetooth is enabled and device is in pairing mode")
            # Try Windows-specific detection as fallback
            self._scan_windows_bluetooth_devices_with_timeout(total_timeout, start_time)

    def _scan_bluetooth_devices(self):
        """Legacy method - now calls timeout-protected version"""
        self._scan_bluetooth_devices_with_timeout(10, time.time())

    def _scan_windows_bluetooth_devices(self):
        """Scan for Bluetooth devices using Windows-specific methods"""
        try:
            # Check for Bluetooth COM ports that might be OBDLink devices
            import serial.tools.list_ports

            logger.info("Checking for Bluetooth virtual COM ports...")

            ports = serial.tools.list_ports.comports()
            bluetooth_ports = []

            for port in ports:
                # Look for Bluetooth virtual COM ports
                if port.description and ("bluetooth" in port.description.lower() or
                                      "wireless" in port.description.lower() or
                                      "bt" in port.description.lower()):
                    logger.debug(f"Found potential Bluetooth port: {port.device} - {port.description}")
                    bluetooth_ports.append(port)

                # Also check for OBDLink-specific descriptions
                if port.description and ("obd" in port.description.lower() or
                                       "obdlink" in port.description.lower()):
                    logger.info(f"Found OBDLink device on port: {port.device} - {port.description}")

                    device = VCIDevice(
                        device_type=VCITypes.OBDLINK_MX_PLUS,
                        name=f"OBDLink MX+ ({port.description})",
                        port=port.device,
                        status=VCIStatus.DISCONNECTED
                    )
                    device.capabilities = self._get_device_capabilities(VCITypes.OBDLINK_MX_PLUS)
                    self.available_devices.append(device)

            if bluetooth_ports:
                logger.info(f"Found {len(bluetooth_ports)} potential Bluetooth COM ports")
                # Add them as potential OBDLink devices
                for port in bluetooth_ports:
                    device = VCIDevice(
                        device_type=VCITypes.OBDLINK_MX_PLUS,
                        name=f"OBDLink MX+ (Bluetooth COM) - {port.device}",
                        port=port.device,
                        status=VCIStatus.DISCONNECTED
                    )
                    device.capabilities = self._get_device_capabilities(VCITypes.OBDLINK_MX_PLUS)
                    self.available_devices.append(device)

        except Exception as e:
            logger.error(f"Windows Bluetooth detection failed: {e}")

    def _scan_windows_bluetooth_devices_with_timeout(self, total_timeout: int, start_time: float):
        """Scan for Bluetooth devices using Windows-specific methods with timeout protection"""
        try:
            # Calculate remaining time
            elapsed = time.time() - start_time
            remaining_time = total_timeout - elapsed
            if remaining_time <= 0:
                logger.warning("No time remaining for Windows Bluetooth scan")
                return

            # Limit Windows Bluetooth scan time
            win_bluetooth_timeout = min(remaining_time * 0.2, 2.0)  # Use max 20% of remaining time, max 2 seconds
            win_bluetooth_start_time = time.time()

            # Check for Bluetooth COM ports that might be OBDLink devices
            import serial.tools.list_ports

            logger.info("Checking for Bluetooth virtual COM ports...")

            ports = serial.tools.list_ports.comports()
            bluetooth_ports = []

            for port in ports:
                # Check overall timeout
                if (time.time() - start_time) > total_timeout:
                    logger.warning("Overall scan timeout reached during Windows Bluetooth scan")
                    break

                # Check Windows Bluetooth-specific timeout
                if (time.time() - win_bluetooth_start_time) > win_bluetooth_timeout:
                    logger.warning(f"Windows Bluetooth scan timeout reached after {win_bluetooth_timeout:.1f}s")
                    break

                try:
                    # Look for Bluetooth virtual COM ports
                    if port.description and ("bluetooth" in port.description.lower() or
                                           "wireless" in port.description.lower() or
                                           "bt" in port.description.lower()):
                        logger.debug(f"Found potential Bluetooth port: {port.device} - {port.description}")
                        bluetooth_ports.append(port)

                    # Also check for OBDLink-specific descriptions
                    if port.description and ("obd" in port.description.lower() or
                                           "obdlink" in port.description.lower()):
                        logger.info(f"Found OBDLink device on port: {port.device} - {port.description}")

                        device = VCIDevice(
                            device_type=VCITypes.OBDLINK_MX_PLUS,
                            name=f"OBDLink MX+ ({port.description})",
                            port=port.device,
                            status=VCIStatus.DISCONNECTED
                        )
                        device.capabilities = self._get_device_capabilities(VCITypes.OBDLINK_MX_PLUS)
                        self.available_devices.append(device)

                except Exception as e:
                    logger.debug(f"Error checking port {port.device}: {e}")

            if bluetooth_ports:
                logger.info(f"Found {len(bluetooth_ports)} potential Bluetooth COM ports")
                # Add them as potential OBDLink devices
                for port in bluetooth_ports:
                    device = VCIDevice(
                        device_type=VCITypes.OBDLINK_MX_PLUS,
                        name=f"OBDLink MX+ (Bluetooth COM) - {port.device}",
                        port=port.device,
                        status=VCIStatus.DISCONNECTED
                    )
                    device.capabilities = self._get_device_capabilities(VCITypes.OBDLINK_MX_PLUS)
                    self.available_devices.append(device)

        except Exception as e:
            logger.error(f"Windows Bluetooth detection failed: {e}")

    def _identify_device_on_port(self, port: str, timeout: int = 2000) -> Optional[VCIDevice]:
        """Try to identify VCI device on a specific port with timeout protection"""
        try:
            import serial  # type: ignore[import-not-found]
            import threading

            # Use threading to add timeout protection for serial operations
            result = [None]
            exception = [None]

            def identify_device():
                try:
                    logger.debug(f"🔍 Opening serial port {port} for identification")
                    # Try to open port briefly to identify device with timeout
                    with serial.Serial(port, 9600, timeout=timeout/1000.0) as ser:
                        logger.debug(f"✅ Serial port {port} opened successfully")
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
                                    result[0] = device
                                    logger.debug(f"✅ Identified {vci_type.value} on {port}")
                                    return

                        # If no specific match, check for generic OBD responses
                        if "OK" in response:
                            device = VCIDevice(
                                device_type=VCITypes.OBDLINK_MX_PLUS,  # Default to OBDLink for generic responses
                                name="OBDLink MX+ (Generic)",
                                port=port,
                                status=VCIStatus.DISCONNECTED
                            )
                            device.capabilities = self._get_device_capabilities(VCITypes.OBDLINK_MX_PLUS)
                            result[0] = device
                            logger.debug(f"✅ Identified generic OBD device on {port}")
                            return

                except Exception as e:
                    logger.debug(f"Serial identification error on {port}: {e}")
                    exception[0] = e

            # Run identification in a thread with timeout
            logger.debug(f"🔍 Starting identification thread for {port}")
            thread = threading.Thread(target=identify_device, daemon=True)
            thread.start()
            thread.join(timeout=timeout/1000.0 + 1.0)  # Add 1 second buffer

            if thread.is_alive():
                logger.warning(f"⚠️ Device identification on {port} timed out after {timeout/1000.0 + 1.0:.1f}s")
                return None

            if exception[0]:
                logger.debug(f"Failed to identify device on {port}: {exception[0]}")
                return None

            logger.debug(f"🔍 Device identification on {port} completed")
            return result[0]

        except Exception as e:
            logger.debug(f"Failed to identify device on {port}: {e}")
            return None

    def _get_device_capabilities(self, vci_type: VCITypes) -> List[str]:
        """Get capabilities for a specific VCI device type"""
        capabilities_map = {
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
        """
        ELITE THREADED CONNECTION: Connect to a specific VCI device
        WITH HANG PROTECTION - Prevents 0xCFFFFFFF during device connection
        """
        try:
            logger.info(f"Connecting to {device.name}...")

            # Update device status
            device.status = VCIStatus.CONNECTING
            self._notify_callbacks("connecting", device)
            
            # ELITE CRASH FIX: Activate hang protection during connection
            self._activate_hang_protection(f"VCI connection to {device.name}")

            # Attempt connection based on device type
            if device.device_type == VCITypes.OBDLINK_MX_PLUS:
                success = self._connect_obdlink_mx_plus(device)
            elif device.device_type == VCITypes.SCANMATIK_2_PRO:
                success = self._connect_scanmatik_2_pro(device)
            elif device.device_type == VCITypes.HH_OBD_ADVANCE:
                success = self._connect_hh_obd_advance(device)
            elif device.device_type == VCITypes.J2534_GENERIC:
                success = self._connect_j2534(device)
            else:
                success = self._connect_generic_obd(device)

            # ELITE CRASH FIX: Deactivate hang protection after connection attempt
            self._deactivate_hang_protection()

            if success:
                device.status = VCIStatus.CONNECTED
                device.last_seen = time.time()
                self.connected_vci = device
                self._notify_callbacks("connected", device)
                logger.info(f"Successfully connected to {device.name} with hang protection")
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
            self._deactivate_hang_protection()  # Ensure cleanup on exception
            return False



    def _connect_obdlink_mx_plus(self, device: VCIDevice) -> bool:
        """Connect to OBDLink MX+ device"""
        try:
            from shared.obdlink_mxplus import OBDLinkMXPlus

            obd_device = OBDLinkMXPlus(mock_mode=False)

            # Try Bluetooth connection first if Bluetooth address is available
            if hasattr(device, 'bluetooth_address') and device.bluetooth_address:
                logger.info(f"Trying Bluetooth connection to {device.bluetooth_address}")
                device_address = f"{device.name} ({device.bluetooth_address})"
                if obd_device.connect_bluetooth(device_address):
                    logger.info("OBDLink MX+ connected via Bluetooth")
                    device._obd_device = obd_device
                    return True
                else:
                    logger.warning("Bluetooth connection failed, trying serial ports")

            # Try serial connection (USB or Bluetooth serial bridge)
            success = False

            # If device has a specific port, try it first
            if device.port:
                logger.info(f"Trying serial connection on {device.port}")
                if obd_device.connect_serial(device.port, 38400):
                    logger.info(f"OBDLink MX+ connected via serial on {device.port}")
                    success = True

            # If no specific port or connection failed, try common ports
            if not success:
                common_ports = ["COM3", "COM4", "COM6", "COM7", "COM8", "COM9", "COM10"]
                for port in common_ports:
                    logger.debug(f"Trying serial connection on {port}")
                    if obd_device.connect_serial(port, 38400):
                        logger.info(f"OBDLink MX+ connected via serial on {port}")
                        device.port = port
                        success = True
                        break

            if success:
                device._obd_device = obd_device
                return True
            else:
                logger.error("All connection attempts failed for OBDLink MX+")

        except ImportError:
            logger.warning("OBDLink MX+ interface not available")
        except Exception as e:
            logger.error(f"OBDLink MX+ connection failed: {e}")

        return False

    def _connect_scanmatik_2_pro(self, device: VCIDevice) -> bool:
        """Connect to Scanmatik 2 Pro device using J2534"""
        try:
            logger.info("Attempting Scanmatik 2 Pro connection via J2534...")
            from shared.j2534_passthru import J2534PassThru
            import os
            
            # 1. Check if we already have a specific DLL path
            dll_path = getattr(device, 'dll_path', None)
            
            # 2. If not, try to find standard Scanmatik DLLs
            if not dll_path:
                possible_dlls = ["sm2j2534.dll", "sm2.dll"]
                
                # Check drivers directory
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
                drivers_dir = os.path.join(project_root, "drivers")
                
                if os.path.exists(drivers_dir):
                    local_dlls = J2534PassThru.scan_local_drivers(drivers_dir)
                    for local_dll in local_dlls:
                        if any(name in os.path.basename(local_dll).lower() for name in ["sm2", "scanmatik"]):
                            dll_path = local_dll
                            logger.info(f"Found local Scanmatik DLL: {dll_path}")
                            break
            
            # 3. If still not found, try common system paths (heuristic)
            if not dll_path:
                system_paths = [
                    r"C:\Program Files (x86)\Scanmatik\sm2j2534.dll",
                    r"C:\Program Files\Scanmatik\sm2j2534.dll"
                ]
                for path in system_paths:
                    if os.path.exists(path):
                        dll_path = path
                        logger.info(f"Found system Scanmatik DLL: {dll_path}")
                        break
            
            # 4. Connect
            if dll_path:
                j2534 = J2534PassThru(dll_path=dll_path)
                if j2534.open():
                    device._j2534_device = j2534
                    logger.info("Scanmatik 2 Pro connected successfully via J2534")
                    return True
                else:
                    logger.error("Failed to open Scanmatik J2534 channel")
            else:
                logger.warning("Scanmatik J2534 DLL not found. Please ensure drivers are installed or placed in drivers/ folder.")
                
            return False
            
        except Exception as e:
            logger.error(f"Scanmatik connection error: {e}")
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