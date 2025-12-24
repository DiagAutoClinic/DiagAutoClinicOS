#!/usr/bin/env python3
"""
VCI Discovery Worker - Threaded device discovery to prevent GUI freezing
Implements QRunnable + QThreadPool pattern for non-blocking device discovery
"""

import logging
import time
import threading
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from PyQt6.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject

logger = logging.getLogger(__name__)

class DiscoverySignals(QObject):
    """Signals for VCI discovery worker"""
    finished = pyqtSignal(list)  # List of discovered devices
    error = pyqtSignal(str)      # Error message
    progress = pyqtSignal(str)   # Progress update
    device_found = pyqtSignal(dict)  # Individual device found

@dataclass
class DiscoveredDevice:
    """Discovered device information"""
    name: str
    device_type: str
    port: Optional[str] = None
    bluetooth_address: Optional[str] = None
    capabilities: List[str] = None
    firmware_version: Optional[str] = None
    mock_mode: bool = False
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.firmware_version is None:
            self.firmware_version = "Unknown"

class VCIDiscoveryWorker(QRunnable):
    """
    VCI Discovery Worker using QRunnable pattern
    Runs device discovery in background thread to prevent GUI freezing
    """
    
    def __init__(self, device_handlers: List[Any] = None, timeout: int = 15):
        """
        Initialize VCI discovery worker
        
        Args:
            device_handlers: List of device handler instances to use for discovery
            timeout: Maximum time to spend on discovery in seconds
        """
        super().__init__()
        self.device_handlers = device_handlers or []
        self.timeout = timeout
        self.signals = DiscoverySignals()
        self._is_killed = False
        self.discovered_devices = []
        
    def kill(self):
        """Stop the discovery process"""
        self._is_killed = True
        
    def run(self):
        """
        Run the discovery process in a background thread
        """
        start_time = time.time()
        
        try:
            self.signals.progress.emit("Starting VCI device discovery...")
            
            # Start parallel discovery with different handlers
            devices = self._discover_all_devices()
            
            # Check if killed during discovery
            if self._is_killed:
                self.signals.error.emit("Discovery cancelled by user")
                return
                
            # Remove duplicates and filter
            unique_devices = self._filter_and_deduplicate_devices(devices)
            
            elapsed = time.time() - start_time
            self.signals.progress.emit(f"Discovery completed in {elapsed:.1f}s")
            
            # Emit final results
            self.signals.finished.emit(unique_devices)
            
            # Log results
            logger.info(f"VCI discovery completed: found {len(unique_devices)} devices")
            for device in unique_devices:
                logger.info(f"  Found: {device.name} ({device.device_type}) on {device.port or 'N/A'}")
                
        except Exception as e:
            logger.error(f"VCI discovery failed: {e}")
            self.signals.error.emit(f"Discovery failed: {str(e)}")
            
    def _discover_all_devices(self) -> List[DiscoveredDevice]:
        """
        Discover devices using all available handlers
        """
        devices = []
        
        # Discovery phases with time limits
        phases = [
            ("OBDLink MX+ Bluetooth", self._discover_obdlink_bluetooth, 6),
            ("OBDLink MX+ Serial", self._discover_obdlink_serial, 4),
            ("ScanMatik 2 Pro", self._discover_scanmatik_devices, 3),
            ("Generic OBD", self._discover_generic_obd, 2),
        ]
        
        for phase_name, discovery_func, phase_timeout in phases:
            if self._is_killed:
                break
                
            phase_start = time.time()
            self.signals.progress.emit(f"Scanning {phase_name}...")
            
            try:
                phase_devices = self._run_discovery_with_timeout(discovery_func, phase_timeout)
                devices.extend(phase_devices)
                
                # Emit individual devices as they're found
                for device in phase_devices:
                    self.signals.device_found.emit({
                        'name': device.name,
                        'type': device.device_type,
                        'port': device.port,
                        'bluetooth_address': device.bluetooth_address
                    })
                    
            except Exception as e:
                logger.warning(f"Discovery phase '{phase_name}' failed: {e}")
                self.signals.progress.emit(f"Failed to scan {phase_name}: {e}")
                
            phase_elapsed = time.time() - phase_start
            logger.debug(f"Phase '{phase_name}' completed in {phase_elapsed:.1f}s")
            
        return devices
        
    def _run_discovery_with_timeout(self, discovery_func: Callable, timeout: int) -> List[DiscoveredDevice]:
        """
        Run discovery function with timeout protection
        """
        result = []
        exception = []
        
        def discovery_worker():
            try:
                result.extend(discovery_func())
            except Exception as e:
                exception.append(e)
                
        thread = threading.Thread(target=discovery_worker)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            logger.warning(f"Discovery function timed out after {timeout}s")
            self.signals.progress.emit(f"Discovery timed out after {timeout}s")
            
        if exception:
            raise exception[0]
            
        return result
        
    def _discover_obdlink_bluetooth(self) -> List[DiscoveredDevice]:
        """
        Discover OBDLink MX+ devices via Bluetooth
        """
        devices = []
        
        try:
            # Try using OBDLink handler
            for handler in self.device_handlers:
                if hasattr(handler, 'discover_devices') and not handler.mock_mode:
                    try:
                        # Use shorter timeout for Bluetooth
                        discovered = handler.discover_devices()
                        for device_info in discovered:
                            devices.append(DiscoveredDevice(
                                name=device_info,
                                device_type="OBDLink MX+",
                                bluetooth_address=self._extract_bluetooth_address(device_info),
                                capabilities=["bluetooth", "can_bus", "obd2", "live_data"]
                            ))
                    except Exception as e:
                        logger.debug(f"OBDLink Bluetooth discovery failed: {e}")
                        
        except Exception as e:
            logger.debug(f"OBDLink Bluetooth discovery error: {e}")
            
        return devices
        
    def _discover_obdlink_serial(self) -> List[DiscoveredDevice]:
        """
        Discover OBDLink MX+ devices via serial ports
        """
        devices = []
        
        try:
            import serial.tools.list_ports
            
            # Common ports to check
            ports_to_check = [
                'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8',
                '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyACM0', '/dev/ttyACM1'
            ]
            
            for port in ports_to_check:
                if self._is_killed:
                    break
                    
                try:
                    device = self._probe_obdlink_serial_port(port)
                    if device:
                        devices.append(device)
                except Exception as e:
                    logger.debug(f"Failed to probe {port}: {e}")
                    
        except ImportError:
            logger.debug("Serial tools not available")
        except Exception as e:
            logger.debug(f"Serial port discovery failed: {e}")
            
        return devices
        
    def _probe_obdlink_serial_port(self, port: str) -> Optional[DiscoveredDevice]:
        """
        Probe a specific serial port for OBDLink device
        """
        try:
            import serial
            
            # Quick probe with short timeout
            with serial.Serial(port, 38400, timeout=1.0) as ser:
                # Send identification command
                ser.write(b'ATI\r\n')
                time.sleep(0.3)
                
                # Read response
                response = ser.read(200).decode('utf-8', errors='ignore').strip()
                
                # Check for OBDLink signatures
                if any(sig in response.upper() for sig in ['OBDLINK', 'ELM327']):
                    return DiscoveredDevice(
                        name=f"OBDLink MX+ ({port})",
                        device_type="OBDLink MX+",
                        port=port,
                        capabilities=["serial", "can_bus", "obd2", "live_data"]
                    )
                    
        except Exception:
            pass  # Port not available or not an OBDLink device
            
        return None
        
    def _discover_scanmatik_devices(self) -> List[DiscoveredDevice]:
        """
        Discover ScanMatik 2 Pro devices
        """
        devices = []
        
        try:
            # Try using ScanMatik handler
            for handler in self.device_handlers:
                if hasattr(handler, 'detect_devices') and not handler.mock_mode:
                    try:
                        detected = handler.detect_devices()
                        for device_info in detected:
                            devices.append(DiscoveredDevice(
                                name=device_info.name,
                                device_type="ScanMatik 2 Pro",
                                port=device_info.port,
                                capabilities=["serial", "j2534", "diagnostics", "dtc_read"]
                            ))
                    except Exception as e:
                        logger.debug(f"ScanMatik discovery failed: {e}")
                        
        except Exception as e:
            logger.debug(f"ScanMatik discovery error: {e}")
            
        return devices
        
    def _discover_generic_obd(self) -> List[DiscoveredDevice]:
        """
        Discover generic OBD devices
        """
        devices = []
        
        try:
            import serial.tools.list_ports
            
            ports = serial.tools.list_ports.comports()
            
            for port in ports:
                if self._is_killed:
                    break
                    
                try:
                    # Quick check for OBD device
                    device = self._probe_generic_obd_port(port.device)
                    if device:
                        devices.append(device)
                except Exception as e:
                    logger.debug(f"Failed to probe {port.device}: {e}")
                    
        except ImportError:
            logger.debug("Serial tools not available")
        except Exception as e:
            logger.debug(f"Generic OBD discovery failed: {e}")
            
        return devices
        
    def _probe_generic_obd_port(self, port: str) -> Optional[DiscoveredDevice]:
        """
        Probe a port for generic OBD device
        """
        try:
            import serial
            
            with serial.Serial(port, 9600, timeout=0.5) as ser:
                ser.write(b'ATZ\r\n')  # Reset command
                time.sleep(0.2)
                
                response = ser.read(100).decode('utf-8', errors='ignore')
                
                if 'OK' in response.upper():
                    return DiscoveredDevice(
                        name=f"Generic OBD ({port})",
                        device_type="Generic OBD",
                        port=port,
                        capabilities=["basic_obd", "dtc_read"]
                    )
                    
        except Exception:
            pass
            
        return None
        
    def _extract_bluetooth_address(self, device_info: str) -> Optional[str]:
        """
        Extract Bluetooth address from device info string
        """
        import re
        match = re.search(r'([0-9A-Fa-f:]{17})', device_info)
        return match.group(1) if match else None
        
    def _filter_and_deduplicate_devices(self, devices: List[DiscoveredDevice]) -> List[DiscoveredDevice]:
        """
        Filter and deduplicate discovered devices
        """
        seen = set()
        unique_devices = []
        
        for device in devices:
            # Create a key for deduplication
            key = (device.device_type, device.port or device.bluetooth_address)
            
            if key not in seen:
                seen.add(key)
                unique_devices.append(device)
                
        # Sort by device type priority
        priority = {"OBDLink MX+": 0, "ScanMatik 2 Pro": 1, "Generic OBD": 2}
        unique_devices.sort(key=lambda d: priority.get(d.device_type, 99))
        
        return unique_devices


class VCIAsyncDiscoveryManager:
    """
    Manager for async VCI discovery operations
    Provides high-level interface for GUI integration
    """
    
    def __init__(self):
        self.thread_pool = QThreadPool.globalInstance()
        self.active_workers = []
        self.callbacks = {
            'finished': [],
            'error': [],
            'progress': [],
            'device_found': []
        }
        
    def discover_devices_async(self, device_handlers: List[Any] = None, timeout: int = 15) -> bool:
        """
        Start async device discovery
        
        Args:
            device_handlers: List of device handlers to use
            timeout: Discovery timeout in seconds
            
        Returns:
            True if discovery started successfully
        """
        # Cancel any ongoing discovery
        self.cancel_discovery()
        
        # Create and configure worker
        worker = VCIDiscoveryWorker(device_handlers, timeout)
        
        # Connect signals
        worker.signals.finished.connect(self._on_discovery_finished)
        worker.signals.error.connect(self._on_discovery_error)
        worker.signals.progress.connect(self._on_discovery_progress)
        worker.signals.device_found.connect(self._on_device_found)
        
        # Store reference to prevent garbage collection
        self.active_workers.append(worker)
        
        # Start discovery
        return self.thread_pool.tryStart(worker)
        
    def cancel_discovery(self):
        """
        Cancel any ongoing discovery
        """
        for worker in self.active_workers:
            if hasattr(worker, 'kill'):
                worker.kill()
                
        self.active_workers.clear()
        
    def add_callback(self, event_type: str, callback: Callable):
        """
        Add callback for discovery events
        """
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
            
    def remove_callback(self, event_type: str, callback: Callable):
        """
        Remove discovery event callback
        """
        if event_type in self.callbacks and callback in self.callbacks[event_type]:
            self.callbacks[event_type].remove(callback)
            
    def _on_discovery_finished(self, devices: List[DiscoveredDevice]):
        """
        Handle discovery completion
        """
        self.active_workers.clear()
        
        # Notify callbacks
        for callback in self.callbacks['finished']:
            try:
                callback(devices)
            except Exception as e:
                logger.debug(f"Callback error: {e}")
                
    def _on_discovery_error(self, error_message: str):
        """
        Handle discovery error
        """
        self.active_workers.clear()
        
        # Notify callbacks
        for callback in self.callbacks['error']:
            try:
                callback(error_message)
            except Exception as e:
                logger.debug(f"Callback error: {e}")
                
    def _on_discovery_progress(self, progress_message: str):
        """
        Handle discovery progress update
        """
        # Notify callbacks
        for callback in self.callbacks['progress']:
            try:
                callback(progress_message)
            except Exception as e:
                logger.debug(f"Callback error: {e}")
                
    def _on_device_found(self, device_info: Dict[str, Any]):
        """
        Handle individual device found
        """
        # Notify callbacks
        for callback in self.callbacks['device_found']:
            try:
                callback(device_info)
            except Exception as e:
                logger.debug(f"Callback error: {e}")


# Global async discovery manager instance
async_discovery_manager = VCIAsyncDiscoveryManager()


def start_vci_discovery_async(device_handlers: List[Any] = None, timeout: int = 15) -> bool:
    """
    Convenience function to start async VCI discovery
    
    Args:
        device_handlers: Device handlers to use for discovery
        timeout: Discovery timeout in seconds
        
    Returns:
        True if discovery started successfully
    """
    return async_discovery_manager.discover_devices_async(device_handlers, timeout)


def cancel_vci_discovery():
    """
    Cancel ongoing VCI discovery
    """
    async_discovery_manager.cancel_discovery()


if __name__ == "__main__":
    # Test the async discovery worker
    import sys
    from PyQt6.QtCore import QCoreApplication
    
    app = QCoreApplication(sys.argv)
    
    def on_finished(devices):
        print(f"Discovery completed! Found {len(devices)} devices:")
        for device in devices:
            print(f"  - {device.name} ({device.device_type}) on {device.port or 'N/A'}")
        app.quit()
        
    def on_progress(message):
        print(f"Progress: {message}")
        
    def on_error(error):
        print(f"Error: {error}")
        app.quit()
    
    # Set up callbacks
    async_discovery_manager.add_callback('finished', on_finished)
    async_discovery_manager.add_callback('progress', on_progress)
    async_discovery_manager.add_callback('error', on_error)
    
    # Start discovery
    print("Starting async VCI discovery...")
    if start_vci_discovery_async(timeout=10):
        print("Discovery started successfully")
    else:
        print("Failed to start discovery")
        app.quit()
    
    sys.exit(app.exec())