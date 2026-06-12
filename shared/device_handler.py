# =============================
# shared/device_handler.py
# =============================
import logging
import importlib
import threading
import time
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

logger = logging.getLogger(__name__)

@dataclass
class DeviceInfo:
    """Device information structure"""
    name: str
    device_type: str
    port: Optional[str] = None
    bluetooth_address: Optional[str] = None
    capabilities: List[str] = None
    mock_mode: bool = False
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []

class DeviceHandler:
    """Enhanced device handler with async discovery support"""
    
    def __init__(self, mock_mode=False, ai_data_collector=None):
        self.mock_mode = mock_mode
        if self.mock_mode:
            logger.warning("DeviceHandler running in mock mode (no real hardware required)")

        self.j2534_available = False
        self.socketcan_available = False
        self.usb_available = False
        self.bluetooth_available = False
        self.ai_data_collector = ai_data_collector  # AI data collection integration
        
        # Device handlers
        self.obdlink_handler = None
        self.scanmatik_handler = None
        
        # Detection results
        self.detected_devices: List[DeviceInfo] = []
        self.detection_lock = threading.Lock()
        
        # Initialize device handlers
        self._initialize_handlers()
        
        # Run initial detection
        if not self.mock_mode:
            self.detect_devices()

    def _initialize_handlers(self):
        """Initialize individual device handlers"""
        try:
            # OBDLink MX+ handler
            from shared.obdlink_mxplus import create_obdlink_mxplus
            self.obdlink_handler = create_obdlink_mxplus(mock_mode=self.mock_mode)
            logger.info("✓ OBDLink MX+ handler initialized")
        except Exception as e:
            logger.warning(f"OBDLink MX+ handler initialization failed: {e}")
            
        try:
            # ScanMatik 2 Pro handler
            from shared.scanmatik_2_pro import create_scanmatik_2_pro_handler
            self.scanmatik_handler = create_scanmatik_2_pro_handler(mock_mode=self.mock_mode)
            logger.info("✓ ScanMatik 2 Pro handler initialized")
        except Exception as e:
            logger.warning(f"ScanMatik 2 Pro handler initialization failed: {e}")

    def detect_devices(self):
        """Detect available diagnostic devices"""
        logger.info("Starting device detection...")

        # --- J2534 Interface ---
        try:
            import winreg  # Only on Windows
            self.j2534_available = True
            logger.info("✓ J2534 registry detected (Windows environment)")
        except Exception as e:
            logger.debug(f"J2534 detection: {e}")

        # --- SocketCAN ---
        try:
            import socket
            self.socketcan_available = True
            logger.info("✓ SocketCAN base available")
        except Exception as e:
            logger.debug(f"SocketCAN detection: {e}")

        # --- USB backend ---
        try:
            import usb.core
            import usb.util
            self.usb_available = True
            logger.info("✓ USB backend loaded successfully")
        except Exception as e:
            logger.debug(f"USB detection error: {e}")

        # --- Bluetooth ---
        try:
            import bluetooth
            self.bluetooth_available = True
            logger.info("✓ Bluetooth backend active")
        except ImportError:
            logger.warning("Bluetooth module not available - Bluetooth features disabled")

    def detect_professional_devices(self):
        """Return list of detected professional diagnostic devices"""
        if self.mock_mode:
            # Return mock devices for testing
            return [
                DeviceInfo("OBDLink MX+ (Mock)", "OBDLink MX+", mock_mode=True,
                          capabilities=["bluetooth", "serial", "can_bus", "obd2"]),
                DeviceInfo("ScanMatik 2 Pro (Mock)", "ScanMatik 2 Pro", mock_mode=True,
                          capabilities=["serial", "j2534", "diagnostics"])
            ]

        devices = []
        if self.j2534_available:
            devices.append(DeviceInfo("J2534 Interface", "J2534",
                                    capabilities=["j2534", "can_bus"]))
        if self.usb_available:
            devices.append(DeviceInfo("USB Device", "USB",
                                    capabilities=["usb", "serial"]))
        if self.bluetooth_available:
            devices.append(DeviceInfo("Bluetooth Adapter", "Bluetooth",
                                    capabilities=["bluetooth", "wireless"]))
        if self.socketcan_available:
            devices.append(DeviceInfo("SocketCAN", "SocketCAN",
                                    capabilities=["can_bus", "linux"]))
        return devices

    def discover_devices_async(self, timeout: int = 15, callback: Optional[Callable] = None) -> bool:
        """
        Start async device discovery to prevent GUI freezing
        
        Args:
            timeout: Maximum time to spend on discovery
            callback: Optional callback function to receive results
            
        Returns:
            True if discovery started successfully
        """
        try:
            from shared.vci_discovery_worker import start_vci_discovery_async
            
            # Prepare device handlers for discovery
            handlers = []
            if self.obdlink_handler:
                handlers.append(self.obdlink_handler)
            if self.scanmatik_handler:
                handlers.append(self.scanmatik_handler)
            
            # Set up callback to store results
            def on_discovery_finished(devices):
                with self.detection_lock:
                    self.detected_devices = devices
                if callback:
                    callback(devices)
                    
            # Add callback to discovery manager
            from shared.vci_discovery_worker import async_discovery_manager
            async_discovery_manager.add_callback('finished', on_discovery_finished)
            
            # Start async discovery
            return start_vci_discovery_async(handlers, timeout)
            
        except Exception as e:
            logger.error(f"Failed to start async device discovery: {e}")
            return False

    def discover_devices_blocking(self, timeout: int = 15) -> List[DeviceInfo]:
        """
        Discover devices with timeout protection (blocking version)
        Use only when async discovery is not suitable
        """
        devices = []
        start_time = time.time()
        
        try:
            # OBDLink MX+ discovery
            if self.obdlink_handler and time.time() - start_time < timeout:
                try:
                    obdlink_devices = self._discover_obdlink_devices(timeout - (time.time() - start_time))
                    devices.extend(obdlink_devices)
                except Exception as e:
                    logger.debug(f"OBDLink discovery failed: {e}")
            
            # ScanMatik 2 Pro discovery  
            if self.scanmatik_handler and time.time() - start_time < timeout:
                try:
                    scanmatik_devices = self._discover_scanmatik_devices(timeout - (time.time() - start_time))
                    devices.extend(scanmatik_devices)
                except Exception as e:
                    logger.debug(f"ScanMatik discovery failed: {e}")
                    
            # Generic device detection
            if time.time() - start_time < timeout:
                try:
                    generic_devices = self.detect_professional_devices()
                    devices.extend(generic_devices)
                except Exception as e:
                    logger.debug(f"Generic device detection failed: {e}")
                    
        except Exception as e:
            logger.error(f"Device discovery failed: {e}")
            
        # Store results
        with self.detection_lock:
            self.detected_devices = devices
            
        elapsed = time.time() - start_time
        logger.info(f"Device discovery completed in {elapsed:.1f}s, found {len(devices)} devices")
        
        return devices

    def _discover_obdlink_devices(self, timeout: float) -> List[DeviceInfo]:
        """Discover OBDLink MX+ devices with timeout"""
        devices = []
        
        try:
            # Use thread pool for timeout protection
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._safe_obdlink_discovery)
                try:
                    discovered = future.result(timeout=timeout)
                    devices.extend(discovered)
                except FutureTimeoutError:
                    logger.warning("OBDLink discovery timed out")
                    
        except Exception as e:
            logger.debug(f"OBDLink discovery error: {e}")
            
        return devices

    def _safe_obdlink_discovery(self) -> List[DeviceInfo]:
        """Safe OBDLink discovery (called in thread)"""
        devices = []
        
        try:
            if self.obdlink_handler:
                discovered = self.obdlink_handler.discover_devices()
                for device_info in discovered:
                    devices.append(DeviceInfo(
                        name=device_info,
                        device_type="OBDLink MX+",
                        bluetooth_address=self._extract_bluetooth_address(device_info),
                        capabilities=["bluetooth", "serial", "can_bus", "obd2"]
                    ))
        except Exception as e:
            logger.debug(f"OBDLink discovery failed: {e}")
            
        return devices

    def _discover_scanmatik_devices(self, timeout: float) -> List[DeviceInfo]:
        """Discover ScanMatik 2 Pro devices with timeout"""
        devices = []
        
        try:
            # Use thread pool for timeout protection
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._safe_scanmatik_discovery)
                try:
                    discovered = future.result(timeout=timeout)
                    devices.extend(discovered)
                except FutureTimeoutError:
                    logger.warning("ScanMatik discovery timed out")
                    
        except Exception as e:
            logger.debug(f"ScanMatik discovery error: {e}")
            
        return devices

    def _safe_scanmatik_discovery(self) -> List[DeviceInfo]:
        """Safe ScanMatik discovery (called in thread)"""
        devices = []
        
        try:
            if self.scanmatik_handler:
                discovered = self.scanmatik_handler.detect_devices()
                for device_info in discovered:
                    devices.append(DeviceInfo(
                        name=device_info.name,
                        device_type="ScanMatik 2 Pro",
                        port=device_info.port,
                        capabilities=["serial", "j2534", "diagnostics", "dtc_read"]
                    ))
        except Exception as e:
            logger.debug(f"ScanMatik discovery failed: {e}")
            
        return devices

    def _extract_bluetooth_address(self, device_info: str) -> Optional[str]:
        """Extract Bluetooth address from device info string"""
        import re
        match = re.search(r'([0-9A-Fa-f:]{17})', device_info)
        return match.group(1) if match else None

    def cancel_discovery(self):
        """Cancel ongoing async discovery"""
        try:
            from shared.vci_discovery_worker import cancel_vci_discovery
            cancel_vci_discovery()
        except Exception as e:
            logger.debug(f"Failed to cancel discovery: {e}")

    def get_detected_devices(self) -> List[DeviceInfo]:
        """Get last detected devices"""
        with self.detection_lock:
            return self.detected_devices.copy()

    def clear_detection_results(self):
        """Clear cached detection results"""
        with self.detection_lock:
            self.detected_devices.clear()

    def is_discovery_in_progress(self) -> bool:
        """Check if discovery is currently in progress"""
        try:
            from shared.vci_discovery_worker import async_discovery_manager
            return len(async_discovery_manager.active_workers) > 0
        except Exception:
            return False

# Global device handler instance
device_handler = DeviceHandler()
