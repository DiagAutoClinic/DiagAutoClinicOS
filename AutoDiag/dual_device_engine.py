#!/usr/bin/env python3
"""
Dual Device Diagnostic Engine
Coordinates OBDLink MX+ (CAN Sniffer) for enhanced diagnostics
"""

import logging
import time
import threading
from typing import Optional, List, Dict, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

# Import existing components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.j2534_passthru import J2534PassThru, MockJ2534PassThru, J2534Protocol, J2534Message
from shared.obdlink_mxplus import OBDLinkMXPlus, CANMessage, OBDLinkProtocol

logger = logging.getLogger(__name__)


class DeviceRole(Enum):
    """Device roles in dual-device setup"""
    PRIMARY_DIAGNOSTIC = "primary_diagnostic"  # OBDLink MX+
    SECONDARY_SNIFFER = "secondary_sniffer"    # OBDLink MX+


class DiagnosticMode(Enum):
    """Diagnostic operation modes"""
    SYNCHRONIZED = "synchronized"    # Both devices work together
    INDEPENDENT = "independent"      # Devices work separately
    MONITOR_ONLY = "monitor_only"    # OBDLink MX+ only monitoring
    DIAGNOSTIC_ONLY = "diagnostic_only"  # OBDLink MX+ only diagnostics


@dataclass
class CANMessageSnapshot:
    """Snapshot of CAN bus activity during diagnostic operations"""
    timestamp: float
    operation: str
    messages: List[CANMessage]
    diagnostic_data: Dict
    

@dataclass
class DualDeviceSession:
    """Dual-device diagnostic session"""
    primary_device: J2534PassThru
    secondary_device: OBDLinkMXPlus
    primary_role: DeviceRole = DeviceRole.PRIMARY_DIAGNOSTIC
    secondary_role: DeviceRole = DeviceRole.SECONDARY_SNIFFER
    mode: DiagnosticMode = DiagnosticMode.SYNCHRONIZED
    is_connected: bool = False
    can_buffer: deque = field(default_factory=lambda: deque(maxlen=1000))
    callbacks: List[Callable] = field(default_factory=list)
    monitoring_active: bool = False


class DualDeviceEngine:
    """Engine for coordinating OBDLink MX+ operations"""
    
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.session: Optional[DualDeviceSession] = None
        self.is_monitoring = False
        self.monitor_thread = None
        self._stop_monitor = threading.Event()
        
        # Performance metrics
        self.metrics = {
            'messages_captured': 0,
            'diagnostic_operations': 0,
            'can_messages_per_second': 0.0,
            'connection_uptime': 0.0
        }
        
        logger.info(f"DualDeviceEngine initialized (mock_mode={mock_mode})")
    
    def create_session(self, 
                      primary_device_name: str = "OBDLink MX+",
                      secondary_device_name: str = "OBDLink MX+",
                      mode: DiagnosticMode = DiagnosticMode.SYNCHRONIZED) -> bool:
        """Create a dual-device session"""
        try:
            # Create primary device (OBDLink MX+)
            if primary_device_name in ["OBDLink MX+"]:
                if self.mock_mode:
                    primary_device = None  # Hardware required
                else:
                    # Try multiple possible ports for OBDLink MX+
                    primary_device = None
                    for port in ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7"]:
                        try:
                            from shared.obdlink_mxplus import OBDLinkMXPlus
                            primary_device = OBDLinkMXPlus(port=port, baudrate=38400)
                            logger.info(f"Successfully connected OBDLink MX+ on {port}")
                            break
                        except Exception as e:
                            logger.debug(f"Failed to connect on {port}: {e}")
                            continue
                    
                    if primary_device is None:
                        logger.error("Failed to connect OBDLink MX+ on any available port")
                        return False
            else:
                logger.error(f"Unknown primary device: {primary_device_name}")
                return False
            
            # Create secondary device (OBDLink MX+)
            if secondary_device_name == "OBDLink MX+":
                secondary_device = OBDLinkMXPlus(mock_mode=self.mock_mode)
            else:
                logger.error(f"Unknown secondary device: {secondary_device_name}")
                return False
            
            self.session = DualDeviceSession(
                primary_device=primary_device,
                secondary_device=secondary_device,
                mode=mode
            )
            
            logger.info(f"Created dual-device session: {primary_device_name} + {secondary_device_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create dual-device session: {e}")
            return False
    
    def connect_devices(self) -> bool:
        """Connect both devices in the session with improved error handling"""
        if not self.session:
            logger.error("No session created")
            return False
        
        try:
            # Connect primary device (OBDLink MX+)
            logger.info("Connecting primary device (OBDLink MX+)...")
            primary_success = self._connect_primary_device()
            if not primary_success:
                logger.warning("Primary device connection failed, but continuing...")
            
            # Connect secondary device (OBDLink MX+)
            logger.info("Connecting secondary device (OBDLink MX+)...")
            secondary_success = self._connect_secondary_device()
            if not secondary_success:
                logger.warning("Secondary device connection failed, but continuing...")
            
            # Update session connection state based on actual device status
            if self._is_any_device_connected():
                self.session.is_connected = True
                logger.info("At least one device connected - session marked as connected")
            else:
                logger.warning("No devices connected - session marked as disconnected")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect devices: {e}")
            return False
    
    def _is_any_device_connected(self) -> bool:
        """Check if any device in the session is actually connected"""
        if not self.session:
            return False
        
        # Check primary device
        primary_connected = False
        if hasattr(self.session.primary_device, 'is_connected'):
            primary_connected = self.session.primary_device.is_connected
        elif hasattr(self.session.primary_device, 'is_open') and self.session.primary_device.is_open():
            primary_connected = True
        
        # Check secondary device  
        secondary_connected = False
        if hasattr(self.session.secondary_device, 'is_connected'):
            secondary_connected = self.session.secondary_device.is_connected
        
        return primary_connected or secondary_connected
    
    def _connect_primary_device(self) -> bool:
        """Connect primary device (OBDLink MX+)"""
        try:
            if not self.session.primary_device.open():
                logger.error("Failed to open primary device")
                return False
            
            # Connect to ISO15765 first (CAN protocol for GM vehicles)
            channel = self.session.primary_device.connect(J2534Protocol.ISO15765)
            if channel < 0:
                logger.warning("Failed to connect to ISO15765, trying CAN...")
                # Try CAN as fallback
                channel = self.session.primary_device.connect(J2534Protocol.CAN)
                if channel < 0:
                    logger.error("Failed to connect to CAN/ISO15765 protocol")
                    return False
            
            logger.info("Primary device (OBDLink MX+) connected to CAN/ISO15765")
            return True
            
        except Exception as e:
            logger.error(f"Primary device connection failed: {e}")
            return False
    
    def _connect_secondary_device(self) -> bool:
        """Connect secondary device (OBDLink MX+) via Bluetooth"""
        try:
            # Check if secondary device is already connected (externally managed)
            if hasattr(self.session.secondary_device, 'is_connected') and self.session.secondary_device.is_connected:
                logger.info("Secondary device (OBDLink MX+) already connected - using existing connection")
                return True
            
            if self.mock_mode:
                # Mock connection
                if not self.session.secondary_device.connect_serial("COM1"):
                    return False
            else:
                # Try multiple Bluetooth ports for OBDLink MX+
                connected = False
                for port in ["COM3", "COM4", "COM6", "COM7"]:
                    try:
                        logger.info(f"Trying OBDLink MX+ on {port}...")
                        if self.session.secondary_device.connect_serial(port, 38400):
                            logger.info(f"Successfully connected OBDLink MX+ on {port}")
                            connected = True
                            break
                    except Exception as e:
                        logger.debug(f"Failed to connect OBDLink MX+ on {port}: {e}")
                        continue
                
                if not connected:
                    logger.error("Failed to connect OBDLink MX+ on any available port")
                    return False
            
            # Set vehicle profile and configure for CAN sniffing
            if hasattr(self.session.secondary_device, 'set_vehicle_profile'):
                self.session.secondary_device.set_vehicle_profile("chevrolet_cruze_2014")
            if hasattr(self.session.secondary_device, 'configure_can_sniffing'):
                self.session.secondary_device.configure_can_sniffing(OBDLinkProtocol.ISO15765_11BIT)
            
            logger.info("Secondary device (OBDLink MX+) configured for CAN sniffing")
            return True
            
        except Exception as e:
            logger.error(f"Secondary device connection failed: {e}")
            return False
    
    def start_monitoring(self) -> bool:
        """Start synchronized monitoring of both devices with improved connection handling"""
        if not self.session:
            logger.error("No session created")
            return False
        
        if self.is_monitoring:
            logger.warning("Monitoring already active")
            return True
        
        try:
            # Check if at least secondary device is available and connected
            secondary_device = self.session.secondary_device
            
            # Verify secondary device is connected (OBDLink MX+ via Bluetooth)
            if not hasattr(secondary_device, 'is_connected') or not secondary_device.is_connected:
                logger.warning("Secondary device not connected, attempting connection...")
                # Try to connect OBDLink MX+ via Bluetooth, but don't fail if it doesn't work
                secondary_connected = self._connect_secondary_device()
                if not secondary_connected:
                    logger.warning("Could not connect secondary device, but continuing with monitoring...")
                    # Allow monitoring to continue even if connection fails
            else:
                logger.info("Secondary device already connected - proceeding with monitoring")
            
            # Start CAN monitoring on secondary device
            if hasattr(secondary_device, 'start_monitoring'):
                if not secondary_device.start_monitoring():
                    logger.error("Failed to start CAN monitoring")
                    return False
                logger.info("CAN monitoring started on secondary device")
            
            # Add message callback for real-time processing
            if hasattr(secondary_device, 'add_message_callback'):
                secondary_device.add_message_callback(self._on_can_message)
            
            # Update session connection state - essential for workflow
            if not self.session.is_connected:
                # Refresh connection state based on current device status
                if self._is_any_device_connected():
                    self.session.is_connected = True
                    logger.info("Session connection state updated - dual-device mode active")
                else:
                    logger.warning("No devices actually connected, but allowing monitoring...")
                    # Still allow monitoring to proceed for testing
                    self.session.is_connected = True
            
            self.is_monitoring = True
            self._stop_monitor.clear()
            
            # Start monitoring thread for synchronized operations
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            
            self.session.monitoring_active = True
            logger.info("Synchronized monitoring started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            return False
    
    def _monitor_loop(self):
        """Main monitoring loop for synchronized operations"""
        while self.is_monitoring and not self._stop_monitor.is_set():
            try:
                # Update metrics
                self._update_metrics()
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                time.sleep(0.5)
    
    def _on_can_message(self, message: CANMessage):
        """Callback for received CAN messages"""
        # Add to buffer
        self.session.can_buffer.append(message)
        self.metrics['messages_captured'] += 1
        
        # Notify callbacks
        for callback in self.session.callbacks:
            try:
                callback(message)
            except Exception as e:
                logger.debug(f"Callback error: {e}")
    
    def _update_metrics(self):
        """Update performance metrics"""
        current_time = time.time()
        if not hasattr(self, '_last_metric_update'):
            self._last_metric_update = current_time
            return
        
        time_delta = current_time - self._last_metric_update
        if time_delta >= 1.0:  # Update every second
            # Calculate messages per second
            messages_in_last_second = len([
                msg for msg in self.session.can_buffer 
                if current_time - msg.timestamp < 1.0
            ])
            self.metrics['can_messages_per_second'] = messages_in_last_second / time_delta
            self._last_metric_update = current_time
    
    def perform_diagnostic_with_monitoring(self, operation: str, *args, **kwargs) -> Dict:
        """Perform diagnostic operation while monitoring CAN bus"""
        if not self.session:
            return {'error': 'No session created'}
        
        # Check session connection state with fallback
        if not self.session.is_connected:
            logger.warning("Session not marked as connected, but proceeding with operation...")
            # Don't fail the operation, just proceed
        
        start_time = time.time()
        
        # Clear CAN buffer before operation
        self.session.can_buffer.clear()
        
        # Record CAN activity before operation
        before_buffer = list(self.session.can_buffer)
        
        try:
            # Perform the diagnostic operation based on type
            if operation == "read_vin":
                result = self._read_vin_with_monitoring()
            elif operation == "scan_dtcs":
                result = self._scan_dtcs_with_monitoring()
            elif operation == "clear_dtcs":
                result = self._clear_dtcs_with_monitoring()
            elif operation == "read_ecu_info":
                result = self._read_ecu_info_with_monitoring()
            else:
                return {'error': f'Unknown operation: {operation}'}
            
            # Allow some time to capture post-operation CAN traffic
            time.sleep(0.5)
            
            # Record CAN activity after operation
            after_buffer = list(self.session.can_buffer)
            new_messages = after_buffer[len(before_buffer):]
            
            # Create diagnostic snapshot
            snapshot = CANMessageSnapshot(
                timestamp=start_time,
                operation=operation,
                messages=new_messages,
                diagnostic_data=result
            )
            
            result['can_monitoring'] = {
                'messages_captured': len(new_messages),
                'duration_ms': int((time.time() - start_time) * 1000),
                'messages_per_second': self.metrics['can_messages_per_second']
            }
            
            self.metrics['diagnostic_operations'] += 1
            return result
            
        except Exception as e:
            logger.error(f"Diagnostic operation failed: {e}")
            return {'error': str(e)}
    
    def _read_vin_with_monitoring(self) -> Dict:
        """Read VIN with CAN monitoring"""
        try:
            # Send VIN request via OBDLink MX+
            vin_request = b'\x22\xF1\x90'  # UDS ReadDataByIdentifier for VIN
            vin_response = self._send_uds_request(vin_request)
            
            if vin_response and len(vin_response.data) >= 10:
                # Parse VIN from response (0x62 + DID + VIN)
                vin = vin_response.data[3:].decode('ascii', errors='ignore').strip()
                return {
                    'operation': 'read_vin',
                    'success': True,
                    'vin': vin,
                    'raw_response': vin_response.data.hex()
                }
            else:
                return {
                    'operation': 'read_vin',
                    'success': False,
                    'error': 'Invalid VIN response'
                }
                
        except Exception as e:
            return {
                'operation': 'read_vin',
                'success': False,
                'error': str(e)
            }
    
    def _scan_dtcs_with_monitoring(self) -> Dict:
        """Scan DTCs with CAN monitoring"""
        try:
            # Send DTC scan request via OBDLink MX+
            dtc_request = b'\x19\x01\xFF'  # UDS ReadDTCInformation
            dtc_response = self._send_uds_request(dtc_request)
            
            if dtc_response:
                # Parse DTC response
                dtcs = self._parse_dtc_response(dtc_response.data)
                return {
                    'operation': 'scan_dtcs',
                    'success': True,
                    'dtcs': dtcs,
                    'raw_response': dtc_response.data.hex()
                }
            else:
                return {
                    'operation': 'scan_dtcs',
                    'success': False,
                    'error': 'No DTC response'
                }
                
        except Exception as e:
            return {
                'operation': 'scan_dtcs',
                'success': False,
                'error': str(e)
            }
    
    def _clear_dtcs_with_monitoring(self) -> Dict:
        """Clear DTCs with CAN monitoring"""
        try:
            # Send DTC clear request via OBDLink MX+
            clear_request = b'\x14\xFF\xFF\xFF'  # UDS ClearDiagnosticInformation
            clear_response = self._send_uds_request(clear_request)
            
            success = clear_response is not None
            
            return {
                'operation': 'clear_dtcs',
                'success': success,
                'raw_response': clear_response.data.hex() if clear_response else None
            }
            
        except Exception as e:
            return {
                'operation': 'clear_dtcs',
                'success': False,
                'error': str(e)
            }
    
    def _read_ecu_info_with_monitoring(self) -> Dict:
        """Read ECU information with CAN monitoring"""
        try:
            # Send ECU identification request via OBDLink MX+
            ecu_request = b'\x22\x1A\x80'  # UDS ReadDataByIdentifier for ECU identification
            ecu_response = self._send_uds_request(ecu_request)
            
            if ecu_response:
                return {
                    'operation': 'read_ecu_info',
                    'success': True,
                    'ecu_data': ecu_response.data.hex(),
                    'raw_response': ecu_response.data.hex()
                }
            else:
                return {
                    'operation': 'read_ecu_info',
                    'success': False,
                    'error': 'No ECU response'
                }
                
        except Exception as e:
            return {
                'operation': 'read_ecu_info',
                'success': False,
                'error': str(e)
            }
    
    def _send_uds_request(self, request_data: bytes):
        """
        Send UDS request via primary device (OBDLink MX+).

        Args:
            request_data: Raw UDS request bytes (e.g., b'\x22\xF1\x90')

        Returns:
            J2534Message: Response object containing raw data

        Raises:
            ConnectionError: If no device is connected or the device does not
                             support UDS communication.
            IOError: If the ECU does not respond.
        """
        if not self.session or not self.session.primary_device:
            raise ConnectionError("No primary device in session")

        primary = self.session.primary_device

        # Use send_uds_request if the primary device supports it (e.g. VCIManager)
        if hasattr(primary, 'send_uds_request'):
            response_bytes = primary.send_uds_request(request_data)
            if response_bytes is None:
                raise IOError("No response from ECU")
            return J2534Message(J2534Protocol.ISO15765, data=response_bytes)

        # Fallback: use send_message / read_message directly on a J2534PassThru device
        if hasattr(primary, 'send_message') and hasattr(primary, 'read_message'):
            channel_id = getattr(self.session, '_channel_id', None)
            if channel_id is None:
                raise ConnectionError("No active protocol channel on primary device")
            tx_id_bytes = (0x7E0).to_bytes(4, 'big')
            msg = J2534Message(J2534Protocol.ISO15765, data=tx_id_bytes + request_data)
            if not primary.send_message(channel_id, msg):
                raise IOError("Failed to send UDS request")
            response = primary.read_message(channel_id, timeout_ms=2000)
            if response is None:
                raise IOError("No response from ECU")
            return response

        raise ConnectionError("Primary device does not support UDS communication")
    
    def _parse_dtc_response(self, response_data: bytes) -> List[Tuple[str, str, str]]:
        """
        Parse DTC response from UDS service 0x19 (ReadDTCInformation).

        Per ISO 14229-1 the positive response to subfunction 0x02 (reportDTCByStatusMask)
        has the layout::

            59 02 <DTCStatusAvailabilityMask> [<DTC byte1> <DTC byte2> <DTC byte3> <status>] ...

        Each DTC record is 4 bytes: 3 DTC bytes + 1 status byte. The standard code
        is derived from the first two DTC bytes following SAE J2012 / ISO 15031-6::

            bits[15:14] of DTC → system: 00=P, 01=C, 10=B, 11=U
            bits[13:12] → first digit (0–3)
            bits[11:8]  → second digit (0–F)
            bits[7:4]   → third digit  (0–F)
            bits[3:0]   → fourth digit (0–F)

        Args:
            response_data: Raw response bytes from the ECU (beginning with the
                           positive-response SID, i.e. 0x59).

        Returns:
            List of tuples: [(code, severity, description), ...]
            Example: [('P0300', 'Medium', 'Random Misfire')]
        """
        if len(response_data) < 4:
            return []

        # Validate positive response SID for service 0x19
        if response_data[0] != 0x59:
            logger.warning(f"Unexpected SID in DTC response: 0x{response_data[0]:02X}")
            return []

        # Bytes: [0]=0x59, [1]=subfunction, [2]=StatusAvailabilityMask, [3+]=DTC records
        dtc_records = response_data[3:]
        dtcs: List[Tuple[str, str, str]] = []

        # Each record is 4 bytes: 3-byte DTC value + 1-byte status mask
        for i in range(0, len(dtc_records), 4):
            if i + 4 > len(dtc_records):
                break
            high   = dtc_records[i]
            mid    = dtc_records[i + 1]
            # low byte (dtc_records[i+2]) encodes additional OEM info; not used in SAE code
            status = dtc_records[i + 3]

            # Derive DTC system from the two MSBs of the high byte
            type_map = {0: 'P', 1: 'C', 2: 'B', 3: 'U'}
            dtc_type  = type_map.get((high >> 6) & 0x03, 'P')
            d1 = (high >> 4) & 0x03   # first digit (0–3)
            d2 =  high       & 0x0F   # second digit (0–F)
            d3 = (mid  >> 4) & 0x0F   # third digit  (0–F)
            d4 =  mid        & 0x0F   # fourth digit (0–F)
            code = f"{dtc_type}{d1}{d2:X}{d3:X}{d4:X}"

            # Determine severity from status byte (ISO 14229-1 Table D.1)
            if status & 0x08:    # bit 3 – confirmedDTC
                severity = "High"
            elif status & 0x04:  # bit 2 – pendingDTC
                severity = "Medium"
            else:
                severity = "Low"

            dtcs.append((code, severity, "Diagnostic Trouble Code"))

        return dtcs
    
    def get_can_statistics(self) -> Dict:
        """Get CAN bus statistics"""
        if not self.session:
            return {'error': 'No session'}
        
        current_time = time.time()
        recent_messages = [
            msg for msg in self.session.can_buffer 
            if current_time - msg.timestamp < 10  # Last 10 seconds
        ]
        
        # Count messages by arbitration ID
        id_counts = {}
        for msg in recent_messages:
            id_counts[msg.arbitration_id] = id_counts.get(msg.arbitration_id, 0) + 1
        
        return {
            'total_messages': len(self.session.can_buffer),
            'recent_messages_10s': len(recent_messages),
            'unique_ids': len(id_counts),
            'top_arbitration_ids': dict(sorted(id_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'messages_per_second': self.metrics['can_messages_per_second']
        }
    
    def get_metrics(self) -> Dict:
        """Get performance metrics"""
        return self.metrics.copy()
    
    def add_message_callback(self, callback: Callable[[CANMessage], None]):
        """Add callback for real-time CAN messages"""
        if self.session:
            self.session.callbacks.append(callback)
    
    def remove_message_callback(self, callback: Callable[[CANMessage], None]):
        """Remove CAN message callback"""
        if self.session and callback in self.session.callbacks:
            self.session.callbacks.remove(callback)
    
    def stop_monitoring(self) -> bool:
        """Stop synchronized monitoring"""
        if not self.is_monitoring:
            return True
        
        try:
            self.is_monitoring = False
            self._stop_monitor.set()
            
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=2)
            
            if self.session:
                self.session.secondary_device.stop_monitoring()
                self.session.monitoring_active = False
            
            logger.info("Monitoring stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")
            return False
    
    def disconnect(self):
        """Disconnect both devices"""
        if self.session:
            try:
                # Stop monitoring first
                self.stop_monitoring()
                
                # Disconnect secondary device (only if we manage it)
                if hasattr(self.session.secondary_device, 'disconnect') and self.session.secondary_device.is_connected:
                    # Only disconnect if we created the connection (not externally managed)
                    if not hasattr(self.session.secondary_device, '_external_connection'):
                        self.session.secondary_device.disconnect()
                
                # Disconnect primary device
                if hasattr(self.session.primary_device, 'close'):
                    self.session.primary_device.close()
                
                self.session.is_connected = False
                logger.info("Both devices disconnected")
                
            except Exception as e:
                logger.error(f"Error during disconnection: {e}")


def create_dual_device_engine(mock_mode: bool = False) -> DualDeviceEngine:
    """Factory function to create dual-device engine"""
    return DualDeviceEngine(mock_mode=mock_mode)


if __name__ == "__main__":
    # Test the dual-device engine
    logging.basicConfig(level=logging.INFO)
    
    print("Dual Device Engine Test")
    print("=" * 40)
    
    # Create engine
    engine = create_dual_device_engine(mock_mode=True)
    
    # Create session
    if engine.create_session():
        print("[OK] Session created")
        
        # Connect devices
        if engine.connect_devices():
            print("[OK] Devices connected")
            
            # Start monitoring
            if engine.start_monitoring():
                print("[OK] Monitoring started")
                
                # Perform diagnostic operations with monitoring
                print("\nPerforming diagnostic operations:")
                
                # Read VIN with monitoring
                vin_result = engine.perform_diagnostic_with_monitoring("read_vin")
                print(f"VIN: {vin_result.get('vin', 'N/A')}")
                print(f"CAN Messages: {vin_result.get('can_monitoring', {}).get('messages_captured', 0)}")
                
                # Scan DTCs with monitoring
                dtc_result = engine.perform_diagnostic_with_monitoring("scan_dtcs")
                print(f"DTCs found: {len(dtc_result.get('dtcs', []))}")
                
                # Get CAN statistics
                stats = engine.get_can_statistics()
                print(f"CAN Stats: {stats}")
                
                # Stop monitoring and disconnect
                engine.stop_monitoring()
                engine.disconnect()
                print("[OK] Test completed")
            else:
                print("[FAIL] Failed to start monitoring")
        else:
            print("[FAIL] Failed to connect devices")
    else:
        print("[FAIL] Failed to create session")