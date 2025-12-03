"""
Diagnostics Controller for AutoDiag Pro
Handles diagnostic operations, DTC reading/clearing, and live data
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import QWidget, QMessageBox, QTableWidgetItem

logger = logging.getLogger(__name__)


class DiagnosticsController:
    """Controller for diagnostic operations"""
    
    # Signals for communication with UI
    status_changed = pyqtSignal(str)
    dtc_read = pyqtSignal(dict)
    dtc_cleared = pyqtSignal(bool)
    live_data_updated = pyqtSignal(list)
    scan_completed = pyqtSignal(dict)
    ecu_info_updated = pyqtSignal(dict)
    
    def __init__(self, ui_callbacks: Optional[Dict[str, callable]] = None):
        """Initialize diagnostics controller"""
        self.ui_callbacks = ui_callbacks or {}
        self.is_streaming = False
        self.current_brand = "Toyota"
        self.live_data_timer = None
        
        # Initialize callbacks
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """Setup default UI callbacks"""
        default_callbacks = {
            'set_button_enabled': lambda btn, enabled: None,
            'set_status': lambda text: None,
            'set_results_text': lambda text: None,
            'update_card_value': lambda card, value: None,
            'switch_to_tab': lambda index: None,
            'show_message': lambda title, text, msg_type="info": None
        }
        
        for key, default_func in default_callbacks.items():
            if key not in self.ui_callbacks:
                self.ui_callbacks[key] = default_func
    
    def read_dtcs(self, brand: str = None) -> Dict[str, Any]:
        """Read diagnostic trouble codes"""
        if brand:
            self.current_brand = brand
            
        try:
            # Disable button during operation
            if 'dtc_btn' in self.ui_callbacks:
                self.ui_callbacks['set_button_enabled']('dtc_btn', False)
            
            self._update_status("📋 Reading DTCs...")
            
            # Simulate diagnostic operation
            QTimer.singleShot(1500, self._complete_dtc_read)
            
            return {"status": "started", "operation": "read_dtcs", "brand": self.current_brand}
            
        except Exception as e:
            logger.error(f"Failed to read DTCs: {e}")
            self._show_error_message("DTC Read Error", f"Failed to read DTCs: {e}")
            return {"status": "error", "message": str(e)}
    
    def _complete_dtc_read(self):
        """Complete DTC read operation"""
        try:
            # Mock DTC data
            dtc_data = {
                "timestamp": datetime.now().isoformat(),
                "brand": self.current_brand,
                "dtcs": [
                    {
                        "code": "P0301",
                        "description": "Cylinder 1 Misfire Detected",
                        "status": "Confirmed",
                        "priority": "Medium",
                        "freeze_frame": {"RPM": 2450, "Load": "65%"}
                    },
                    {
                        "code": "U0121",
                        "description": "Lost Communication With ABS Control Module",
                        "status": "Pending", 
                        "priority": "Low",
                        "first_occurrence": "2024-01-15"
                    }
                ],
                "total_count": 2
            }
            
            # Update UI
            if 'dtc_btn' in self.ui_callbacks:
                self.ui_callbacks['set_button_enabled']('dtc_btn', True)
            
            self._update_status("✅ DTCs retrieved")
            
            # Format results text
            results_text = self._format_dtc_results(dtc_data)
            if 'set_results_text' in self.ui_callbacks:
                self.ui_callbacks['set_results_text'](results_text)
            
            # Emit signal
            self.dtc_read.emit(dtc_data)
            
        except Exception as e:
            logger.error(f"Error completing DTC read: {e}")
            self._show_error_message("DTC Read Error", f"Error completing DTC read: {e}")
    
    def _format_dtc_results(self, dtc_data: Dict[str, Any]) -> str:
        """Format DTC data for display"""
        text = f"DTC Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for dtc in dtc_data.get('dtcs', []):
            text += f"{dtc['code']} - {dtc['description']}\n"
            text += f"   Status: {dtc['status']}\n"
            text += f"   Priority: {dtc['priority']}\n"
            
            if 'freeze_frame' in dtc:
                freeze_frame = dtc['freeze_frame']
                text += f"   Freeze Frame: RPM={freeze_frame.get('RPM', 'N/A')}, Load={freeze_frame.get('Load', 'N/A')}\n\n"
            elif 'first_occurrence' in dtc:
                text += f"   First Occurrence: {dtc['first_occurrence']}\n\n"
        
        text += f"Total DTCs: {dtc_data.get('total_count', 0)}"
        return text
    
    def clear_dtcs(self, brand: str = None) -> Dict[str, Any]:
        """Clear diagnostic trouble codes"""
        if brand:
            self.current_brand = brand
            
        try:
            # Show confirmation dialog
            self._show_confirmation_dialog(
                "Clear DTCs", 
                "Are you sure you want to clear all diagnostic trouble codes?",
                self._confirm_clear_dtcs
            )
            
            return {"status": "confirmed", "operation": "clear_dtcs", "brand": self.current_brand}
            
        except Exception as e:
            logger.error(f"Failed to clear DTCs: {e}")
            self._show_error_message("DTC Clear Error", f"Failed to clear DTCs: {e}")
            return {"status": "error", "message": str(e)}
    
    def _confirm_clear_dtcs(self):
        """Confirm and execute DTC clearing"""
        try:
            # Disable button during operation
            if 'clear_btn' in self.ui_callbacks:
                self.ui_callbacks['set_button_enabled']('clear_btn', False)
            
            self._update_status("🧹 Clearing DTCs...")
            
            # Simulate clearing operation
            QTimer.singleShot(2000, self._complete_dtc_clear)
            
        except Exception as e:
            logger.error(f"Error in DTC clear confirmation: {e}")
    
    def _complete_dtc_clear(self):
        """Complete DTC clear operation"""
        try:
            # Mock clear results
            self._update_status("✅ DTCs cleared successfully")
            
            # Format clear results
            results_text = (
                f"DTC Clearance Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                "✅ All diagnostic trouble codes have been cleared\n"
                "✅ System memory reset\n"
                "✅ Ready for new diagnostics\n\n"
                "Note: Some codes may reappear if underlying issues persist."
            )
            
            if 'set_results_text' in self.ui_callbacks:
                self.ui_callbacks['set_results_text'](results_text)
            
            # Update DTC card
            if 'update_card_value' in self.ui_callbacks:
                self.ui_callbacks['update_card_value']('dtc_card', 0)
            
            # Re-enable buttons
            if 'clear_btn' in self.ui_callbacks:
                self.ui_callbacks['set_button_enabled']('clear_btn', True)
            
            # Emit signal
            self.dtc_cleared.emit(True)
            
        except Exception as e:
            logger.error(f"Error completing DTC clear: {e}")
    
    def start_live_stream(self, brand: str = None) -> Dict[str, Any]:
        """Start live data streaming"""
        if brand:
            self.current_brand = brand
            
        try:
            self._update_status("📊 Starting live data stream...")
            
            # Initialize live data timer if needed
            if not self.live_data_timer:
                self.live_data_timer = QTimer()
                self.live_data_timer.timeout.connect(self._update_live_data)
            
            # Start streaming
            self.is_streaming = True
            self.live_data_timer.start(1000)  # Update every second
            
            # Delay status update
            QTimer.singleShot(1000, lambda: self._update_status("📊 Live data streaming active"))
            
            return {"status": "started", "operation": "start_live_stream", "brand": self.current_brand}
            
        except Exception as e:
            logger.error(f"Failed to start live stream: {e}")
            self._show_error_message("Live Stream Error", f"Failed to start live stream: {e}")
            return {"status": "error", "message": str(e)}
    
    def stop_live_stream(self) -> Dict[str, Any]:
        """Stop live data streaming"""
        try:
            if self.live_data_timer:
                self.live_data_timer.stop()
            
            self.is_streaming = False
            self._update_status("⏹ Live data stream stopped")
            
            return {"status": "stopped", "operation": "stop_live_stream"}
            
        except Exception as e:
            logger.error(f"Failed to stop live stream: {e}")
            self._show_error_message("Live Stream Error", f"Failed to stop live stream: {e}")
            return {"status": "error", "message": str(e)}
    
    def _update_live_data(self):
        """Update live data values"""
        try:
            if self.is_streaming:
                # Get mock live data
                live_data = self._get_mock_live_data()
                
                # Update UI table
                if 'update_live_data_table' in self.ui_callbacks:
                    self.ui_callbacks['update_live_data_table'](live_data)
                
                # Emit signal
                self.live_data_updated.emit(live_data)
                
        except Exception as e:
            logger.error(f"Error updating live data: {e}")
    
    def _get_mock_live_data(self) -> List[Tuple[str, str, str]]:
        """Get mock live data for simulation"""
        return [
            ("Engine RPM", "2,450", "RPM"),
            ("Vehicle Speed", "65", "km/h"),
            ("Coolant Temp", "87", "°C"),
            ("Throttle Position", "25", "%"),
            ("Fuel Trim", "2.3", "%"),
            ("O2 Sensor", "0.45", "V"),
            ("Engine Load", "65", "%"),
            ("Ignition Timing", "12", "°BTDC")
        ]
    
    def run_quick_scan(self, brand: str = None) -> Dict[str, Any]:
        """Run quick diagnostic scan"""
        if brand:
            self.current_brand = brand
            
        try:
            self._update_status("🔍 Running quick scan...")
            
            # Switch to diagnostics tab
            if 'switch_to_tab' in self.ui_callbacks:
                self.ui_callbacks['switch_to_tab'](1)
            
            # Simulate scan
            QTimer.singleShot(800, self._complete_quick_scan)
            
            return {"status": "started", "operation": "quick_scan", "brand": self.current_brand}
            
        except Exception as e:
            logger.error(f"Failed to run quick scan: {e}")
            self._show_error_message("Quick Scan Error", f"Failed to run quick scan: {e}")
            return {"status": "error", "message": str(e)}
    
    def _complete_quick_scan(self):
        """Complete quick scan operation"""
        try:
            scan_results = {
                "timestamp": datetime.now().isoformat(),
                "brand": self.current_brand,
                "status": "completed",
                "results": {
                    "basic_communication": "OK",
                    "power_supply": "NORMAL",
                    "ecu_response": "ACTIVE",
                    "dtc_count": 1,
                    "system_ready": True
                }
            }
            
            self._update_status("✅ Quick scan completed")
            
            # Format results
            results_text = (
                f"Quick Scan Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                "✅ Basic Communication: OK\n"
                "✅ Power Supply: NORMAL\n"
                "✅ ECU Response: ACTIVE\n"
                "⚠️  1 Non-critical DTC found\n"
                "✅ System Ready for Detailed Diagnostics"
            )
            
            if 'set_results_text' in self.ui_callbacks:
                self.ui_callbacks['set_results_text'](results_text)
            
            # Emit signal
            self.scan_completed.emit(scan_results)
            
        except Exception as e:
            logger.error(f"Error completing quick scan: {e}")
    
    def get_ecu_info(self, brand: str = None) -> Dict[str, Any]:
        """Get ECU information"""
        if brand:
            self.current_brand = brand
            
        try:
            # Switch to diagnostics tab
            if 'switch_to_tab' in self.ui_callbacks:
                self.ui_callbacks['switch_to_tab'](1)
            
            # Mock ECU info
            ecu_info = {
                "ecu_type": "Engine Control Module",
                "part_number": "89663-12345",
                "software_version": "v2.1.8",
                "hardware_version": "v1.2",
                "vin": "1HGCM82633A123456",
                "calibration_date": "2023-12-01",
                "protocol": "CAN 11bit/500k",
                "brand": self.current_brand
            }
            
            # Format info text
            info_text = (
                f"ECU Information - {self.current_brand}\n\n"
                f"ECU: {ecu_info['ecu_type']}\n"
                f"Part #: {ecu_info['part_number']}\n"
                f"Software: {ecu_info['software_version']}\n"
                f"Hardware: {ecu_info['hardware_version']}\n"
                f"VIN: {ecu_info['vin']}\n"
                f"Calibration: {ecu_info['calibration_date']}\n"
                f"Protocol: {ecu_info['protocol']}"
            )
            
            if 'set_results_text' in self.ui_callbacks:
                self.ui_callbacks['set_results_text'](info_text)
            
            self._update_status(f"💾 ECU info for {self.current_brand}")
            
            # Emit signal
            self.ecu_info_updated.emit(ecu_info)
            
            return {"status": "success", "ecu_info": ecu_info}
            
        except Exception as e:
            logger.error(f"Failed to get ECU info: {e}")
            self._show_error_message("ECU Info Error", f"Failed to get ECU info: {e}")
            return {"status": "error", "message": str(e)}
    
    def populate_sample_data(self) -> List[Tuple[str, str, str]]:
        """Populate sample data for live data table"""
        try:
            sample_data = self._get_mock_live_data()
            
            if 'populate_live_data_table' in self.ui_callbacks:
                self.ui_callbacks['populate_live_data_table'](sample_data)
            
            return sample_data
            
        except Exception as e:
            logger.error(f"Failed to populate sample data: {e}")
            return []
    
    def _update_status(self, message: str):
        """Update status message"""
        self._update_ui_callback('set_status', message)
        self.status_changed.emit(message)
    
    def _update_ui_callback(self, callback_name: str, *args):
        """Safely update UI callback"""
        if callback_name in self.ui_callbacks:
            try:
                self.ui_callbacks[callback_name](*args)
            except Exception as e:
                logger.error(f"Error in UI callback {callback_name}: {e}")
    
    def _show_error_message(self, title: str, message: str):
        """Show error message to user"""
        self._update_ui_callback('show_message', title, message, "error")
    
    def _show_confirmation_dialog(self, title: str, message: str, confirm_callback: callable):
        """Show confirmation dialog"""
        try:
            # For now, auto-confirm in headless/testing mode
            # In real implementation, this would show a dialog
            confirm_callback()
        except Exception as e:
            logger.error(f"Error showing confirmation dialog: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.live_data_timer:
                self.live_data_timer.stop()
                self.live_data_timer = None
            
            self.is_streaming = False
            logger.info("Diagnostics controller cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def set_brand(self, brand: str):
        """Set current vehicle brand"""
        self.current_brand = brand
        logger.info(f"Brand set to: {brand}")
    
    def get_brand(self) -> str:
        """Get current vehicle brand"""
        return self.current_brand
    
    def is_streaming_active(self) -> bool:
        """Check if live data streaming is active"""
        return self.is_streaming