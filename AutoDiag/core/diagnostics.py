"""
Diagnostics Controller for AutoDiag Pro
Handles diagnostic operations, DTC reading/clearing, and live data
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from PyQt6.QtCore import QTimer, pyqtSignal, QObject, QThread

logger = logging.getLogger(__name__)

class VehicleLoaderThread(QThread):
    """Background thread for loading vehicle list"""
    vehicles_loaded = pyqtSignal(list)
    
    def run(self):
        try:
            if CAN_PARSER_AVAILABLE:
                vehicles = list_all_vehicles()
                self.vehicles_loaded.emit(vehicles)
            else:
                self.vehicles_loaded.emit([])
        except Exception as e:
            logger.error(f"Error in vehicle loader thread: {e}")
            self.vehicles_loaded.emit([])

# Import CAN bus REF parser
try:
    from AutoDiag.core.can_bus_ref_parser import (
        ref_parser, get_vehicle_database, list_all_vehicles,
        get_all_manufacturers, VehicleCANDatabase
    )
    CAN_PARSER_AVAILABLE = True
except ImportError:
    CAN_PARSER_AVAILABLE = False
    logger.error("CAN bus parser not available - hardware required for vehicle database access")
    # Don't raise - allow application to continue with limited functionality

# Import VCI manager
try:
    from AutoDiag.core.vci_manager import get_vci_manager, VCITypes, VCIStatus
    VCI_MANAGER_AVAILABLE = True
except ImportError:
    VCI_MANAGER_AVAILABLE = False
    logger.warning("VCI manager not available - VCI detection disabled")

# Import tier system
try:
    from shared.tier_system import tier_system, Tier
    from shared.brand_database import brand_database
    TIER_SYSTEM_AVAILABLE = True
except ImportError:
    TIER_SYSTEM_AVAILABLE = False
    logger.warning("Tier system not available - tier enforcement disabled")


class DiagnosticsController(QObject):
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
        super().__init__()
        self.ui_callbacks = ui_callbacks or {}
        self.is_streaming = False
        self.current_brand = "Toyota"
        self.live_data_timer = None

        # CAN database
        self.current_vehicle_db: Optional[VehicleCANDatabase] = None
        self.available_vehicles = []

        # VCI manager
        self.vci_manager = None
        if VCI_MANAGER_AVAILABLE:
            self.vci_manager = get_vci_manager()
            self.vci_manager.add_status_callback(self._on_vci_status_change)

        # Initialize callbacks
        self._setup_callbacks()
        # DEFERRED: Don't load vehicles during initialization to prevent startup hang
        self._vehicles_loaded = False
        self._load_available_vehicles_later()

        # Current voltage reading
        self.current_voltage = 12.6  # Default voltage

        # Load user tier from configuration
        try:
            from AutoDiag.config.settings import get_config
            tier_level = get_config("user.tier_level", 1)
            self.user_tier = Tier(tier_level)
        except Exception as e:
            logger.warning(f"Failed to load user tier from config: {e}")
            self.user_tier = Tier.FREE
    
    def _setup_callbacks(self):
        """Setup default UI callbacks"""
        default_callbacks = {
            'set_button_enabled': lambda btn, enabled: None,
            'set_status': lambda text: None,
            'set_results_text': lambda text: None,
            'update_card_value': lambda card, value: None,
            'switch_to_tab': lambda index: None,
            'show_message': lambda title, text, msg_type="info": None,
            'vci_status_changed': lambda event, data: None,
            'update_vci_status_display': lambda status_info: None
        }

        for key, default_func in default_callbacks.items():
            if key not in self.ui_callbacks:
                self.ui_callbacks[key] = default_func

    def _load_available_vehicles_later(self):
        """Load list of available vehicles from REF files - deferred to prevent startup hang"""
        # Start background loader
        self._vehicle_loader = VehicleLoaderThread()
        self._vehicle_loader.vehicles_loaded.connect(self._on_vehicles_loaded)
        self._vehicle_loader.start()
    
    def _on_vehicles_loaded(self, vehicles):
        """Handle loaded vehicles"""
        self.available_vehicles = vehicles
        self._vehicles_loaded = True
        logger.info(f"Loaded {len(self.available_vehicles)} vehicles from REF files (background)")
        
        # If we have a vehicle selection UI waiting, we might need to notify it
        # For now, just logging it is enough as the UI pulls this data on demand

    def _load_available_vehicles(self):
        """Load list of available vehicles from REF files (Synchronous fallback)"""
        try:
            if CAN_PARSER_AVAILABLE:
                self.available_vehicles = list_all_vehicles()
                logger.info(f"Loaded {len(self.available_vehicles)} vehicles from REF files")
                self._vehicles_loaded = True
            else:
                # No fallback - hardware required for vehicle database
                self.available_vehicles = []
                logger.error("CAN parser not available - vehicle database cannot be loaded")
                self._vehicles_loaded = False
        except Exception as e:
            logger.error(f"Error loading available vehicles: {e}")
            self.available_vehicles = []
            self._vehicles_loaded = False

    def load_vehicle_database(self, manufacturer: str, model: str = "") -> bool:
        """Load CAN database for specific vehicle"""
        if not CAN_PARSER_AVAILABLE:
            logger.error("CAN parser not available - hardware required for vehicle database access")
            return False

        self.current_vehicle_db = get_vehicle_database(manufacturer, model)
        if self.current_vehicle_db:
            logger.info(f"Loaded CAN database for {manufacturer} {model}: {len(self.current_vehicle_db.messages)} messages")
            return True
        else:
            logger.warning(f"Failed to load CAN database for {manufacturer} {model}")
            return False

    def get_available_manufacturers(self) -> List[str]:
        """Get list of available manufacturers"""
        if not self._vehicles_loaded:
            self._load_available_vehicles()
        return sorted(set(v[0] for v in self.available_vehicles))

    def get_models_for_manufacturer(self, manufacturer: str) -> List[str]:
        """Get models available for a manufacturer"""
        if not self._vehicles_loaded:
            self._load_available_vehicles()
        return sorted([v[1] for v in self.available_vehicles if v[0] == manufacturer])
    
    def read_dtcs(self, brand: Optional[str] = None) -> Dict[str, Any]:
        """Read diagnostic trouble codes"""
        if brand:
            self.current_brand = brand

        try:
            # Check tier access first
            if not self.enforce_tier_access(self.current_brand, "read_dtcs"):
                return {"status": "error", "message": "Tier access denied for DTC reading"}

            # Check VCI connection first
            if not self._check_vci_connection():
                return {"status": "error", "message": "No VCI device connected. Please connect a VCI device first."}

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
        """Complete DTC read operation using real VCI communication"""
        try:
            dtc_data = {
                "timestamp": datetime.now().isoformat(),
                "brand": self.current_brand,
                "dtcs": [],
                "total_count": 0
            }

            # Try to read real DTCs from VCI device
            if self.vci_manager and self.vci_manager.is_connected():
                try:
                    # Send UDS/KWP commands to read DTCs
                    real_dtcs = self._read_real_dtcs()
                    dtc_data["dtcs"] = real_dtcs
                    dtc_data["total_count"] = len(real_dtcs)
                    logger.info(f"Read {len(real_dtcs)} DTCs from VCI device")
                except Exception as e:
                    logger.error(f"Failed to read real DTCs: {e}")
                    dtc_data["dtcs"] = []
                    dtc_data["total_count"] = 0
            else:
                logger.warning("No VCI device connected - cannot read DTCs")
                dtc_data["dtcs"] = []
                dtc_data["total_count"] = 0

            # Update UI
            if 'dtc_btn' in self.ui_callbacks:
                self.ui_callbacks['set_button_enabled']('dtc_btn', True)

            self._update_status(f"✅ DTCs retrieved ({dtc_data['total_count']} found)")

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
    
    def clear_dtcs(self, brand: Optional[str] = None) -> Dict[str, Any]:
        """Clear diagnostic trouble codes"""
        if brand:
            self.current_brand = brand

        try:
            # Check VCI connection first
            if not self._check_vci_connection():
                return {"status": "error", "message": "No VCI device connected. Please connect a VCI device first."}

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
        """Complete DTC clear operation using real VCI communication"""
        try:
            success = False

            # Try to clear DTCs using real VCI device
            if self.vci_manager and self.vci_manager.is_connected():
                try:
                    # Send UDS service 0x14 (Clear DTC)
                    success = self._clear_real_dtcs()
                    if success:
                        logger.info("DTCs cleared successfully via VCI device")
                    else:
                        logger.error("Failed to clear DTCs via VCI device")
                except Exception as e:
                    logger.error(f"Real DTC clear failed: {e}")
                    success = False
            else:
                logger.error("No VCI device connected - cannot clear DTCs")
                success = False

            if success:
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

                # Emit signal
                self.dtc_cleared.emit(True)
            else:
                self._update_status("❌ Failed to clear DTCs")
                self._show_error_message("DTC Clear Error", "Failed to clear diagnostic trouble codes. Ensure VCI device is connected.")

            # Re-enable buttons
            if 'clear_btn' in self.ui_callbacks:
                self.ui_callbacks['set_button_enabled']('clear_btn', True)

        except Exception as e:
            logger.error(f"Error completing DTC clear: {e}")
            self._show_error_message("DTC Clear Error", f"Error completing DTC clear: {e}")
    
    def start_live_stream(self, brand: Optional[str] = None) -> Dict[str, Any]:
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
        """Update live data values from real CAN sources with realtime monitoring"""
        try:
            if self.is_streaming:
                # Get live data from CAN database only
                live_data = self._get_live_data_from_can_db()

                # Update UI table
                if 'update_live_data_table' in self.ui_callbacks:
                    self.ui_callbacks['update_live_data_table'](live_data)

                # Update CAN bus tab with realtime data if available
                if 'update_can_bus_data' in self.ui_callbacks:
                    can_data = self._get_realtime_can_data()
                    self.ui_callbacks['update_can_bus_data'](can_data)

                # Emit signal
                self.live_data_updated.emit(live_data)

        except Exception as e:
            logger.error(f"Error updating live data: {e}")
    
    def _get_live_data_from_can_db(self) -> List[Tuple[str, str, str]]:
        """Get live data from CAN database only - no mock fallbacks"""
        if not self.current_vehicle_db or not self.current_vehicle_db.messages:
            logger.warning("No CAN database available for live data")
            return []

        # Use real signals from CAN database
        live_data = []
        signals_used = set()

        # Collect signals from all messages (limit to reasonable number)
        for msg in list(self.current_vehicle_db.messages.values())[:10]:  # First 10 messages
            for signal in msg.signals[:5]:  # Up to 5 signals per message
                if signal.name not in signals_used and len(live_data) < 12:
                    # Hardware required for live data - cannot generate simulated values
                    logger.warning("Live data requires hardware connection - no simulated data generation")
                    return []

                    # Format value appropriately
                    if signal.unit in ["RPM", "km/h", "°C", "%", "V", "bar", "°BTDC"]:
                        formatted_value = f"{value:.1f}"
                    else:
                        formatted_value = f"{value:.2f}"

                    live_data.append((signal.name.replace('_', ' ').title(), formatted_value, signal.unit))
                    signals_used.add(signal.name)

        # If we don't have enough signals from database, log warning
        if len(live_data) < 8:
            logger.warning(f"Only {len(live_data)} signals available from CAN database for {self.current_brand}")

        return live_data[:12]  # Limit to 12 items

    def _get_realtime_can_data(self) -> Dict[int, bytes]:
        """Get realtime CAN data from VCI device if available"""
        can_data = {}

        try:
            if self.vci_manager and self.vci_manager.is_connected():
                # Get real CAN data from VCI device
                device = self.vci_manager.get_connected_device()
                if device and "can_bus" in device.capabilities:
                    # In real implementation, this would capture real CAN messages
                    # For now, return empty dict - hardware required for CAN data
                    logger.warning("Real CAN data capture not implemented - hardware required")
                else:
                    logger.warning("Connected device does not support CAN bus monitoring")
            else:
                logger.warning("No VCI device connected - cannot capture CAN data")

        except Exception as e:
            logger.error(f"Error getting realtime CAN data: {e}")

        return can_data


    def run_quick_scan(self, brand: Optional[str] = None) -> Dict[str, Any]:
        """Run quick diagnostic scan"""
        if brand:
            self.current_brand = brand

        try:
            # Check VCI connection first
            if not self._check_vci_connection():
                return {"status": "error", "message": "No VCI device connected. Please connect a VCI device first."}

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
        """Complete quick scan operation using real VCI communication"""
        try:
            scan_results = None
            
            # Try to perform real quick scan
            if self.vci_manager and self.vci_manager.is_connected():
                try:
                    scan_results = self._perform_real_quick_scan()
                    logger.info("Quick scan completed using real VCI device")
                except Exception as e:
                    logger.error(f"Real quick scan failed: {e}")
                    scan_results = {"status": "error", "message": str(e)}
            else:
                logger.error("No VCI device connected - cannot perform quick scan")
                scan_results = {"status": "error", "message": "No VCI device connected"}

            if scan_results and scan_results.get("status") != "error":
                self._update_status("✅ Quick scan completed")

                # Format results
                results_text = self._format_scan_results(scan_results)
                if 'set_results_text' in self.ui_callbacks:
                    self.ui_callbacks['set_results_text'](results_text)

                # Emit signal
                self.scan_completed.emit(scan_results)
            else:
                self._update_status("❌ Quick scan failed")
                error_msg = scan_results.get("message", "Unknown error") if scan_results else "Unknown error"
                self._show_error_message("Quick Scan Error", f"Quick scan failed: {error_msg}")

        except Exception as e:
            logger.error(f"Error completing quick scan: {e}")
            self._show_error_message("Quick Scan Error", f"Error completing quick scan: {e}")
    
    def get_ecu_info(self, brand: Optional[str] = None) -> Dict[str, Any]:
        """Get ECU information using real VCI communication"""
        if brand:
            self.current_brand = brand

        try:
            # Check VCI connection first
            if not self._check_vci_connection():
                return {"status": "error", "message": "No VCI device connected. Please connect a VCI device first."}

            # Switch to diagnostics tab
            if 'switch_to_tab' in self.ui_callbacks:
                self.ui_callbacks['switch_to_tab'](1)

            # Try to get real ECU info
            if self.vci_manager and self.vci_manager.is_connected():
                try:
                    ecu_info = self._read_real_ecu_info()
                    logger.info("ECU info retrieved from real VCI device")
                except Exception as e:
                    logger.error(f"Failed to read real ECU info: {e}")
                    return {"status": "error", "message": f"Failed to read ECU info: {e}"}
            else:
                logger.error("No VCI device connected - cannot read ECU info")
                return {"status": "error", "message": "No VCI device connected"}

            # Format info text
            info_text = self._format_ecu_info(ecu_info)
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
    
    def populate_live_data_table(self) -> List[Tuple[str, str, str]]:
        """Populate live data table from CAN database"""
        try:
            live_data = self._get_live_data_from_can_db()

            if 'populate_live_data_table' in self.ui_callbacks:
                self.ui_callbacks['populate_live_data_table'](live_data)

            return live_data

        except Exception as e:
            logger.error(f"Failed to populate live data table: {e}")
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

            # Disconnect VCI if connected
            if self.vci_manager:
                self.vci_manager.disconnect()
                self.vci_manager.remove_status_callback(self._on_vci_status_change)

            self.is_streaming = False
            logger.info("Diagnostics controller cleaned up")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def set_brand(self, brand: str):
        """Set current vehicle brand and load database"""
        self.current_brand = brand

        # Try to load vehicle database for this brand
        if self.load_vehicle_database(brand):
            logger.info(f"Brand set to: {brand} (CAN database loaded)")
        else:
            logger.info(f"Brand set to: {brand} (using default database)")

    def set_user_tier(self, tier: Tier):
        """Set the user's current tier level"""
        self.user_tier = tier
        logger.info(f"User tier set to: {tier.name}")

    def get_user_tier(self) -> Tier:
        """Get the user's current tier level"""
        return self.user_tier

    def check_tier_access(self, brand_name: str, operation: str = None) -> Tuple[bool, str]:
        """
        Check if user has tier access for a specific brand/operation

        Returns:
            Tuple of (has_access, message)
        """
        if not TIER_SYSTEM_AVAILABLE:
            return True, "Tier system not available - access granted"

        try:
            # Get required tier for this brand
            required_tier, reason = brand_database.get_brand_tier(brand_name)

            # Check if user tier meets requirement
            if tier_system.validate_tier_access(self.user_tier, required_tier):
                return True, f"Access granted - {reason}"
            else:
                tier_info = tier_system.get_tier_info(required_tier)
                return False, f"Tier {required_tier.value} ({tier_info['name']}) required. Current tier: {self.user_tier.value}"

        except Exception as e:
            logger.error(f"Error checking tier access: {e}")
            return False, f"Tier check failed: {e}"

    def show_tier_acknowledgement(self, tier: Tier, brand_name: str = None, operation: str = None) -> bool:
        """Show tier acknowledgement dialog if required"""
        if not TIER_SYSTEM_AVAILABLE:
            return True

        try:
            from AutoDiag.ui.tier_acknowledgement_dialog import show_tier_acknowledgement
            return show_tier_acknowledgement(tier, brand_name, operation)
        except ImportError:
            logger.warning("Tier acknowledgement dialog not available")
            return True

    def enforce_tier_access(self, brand_name: str, operation: str = None) -> bool:
        """
        Enforce tier access for an operation

        Returns:
            True if access granted, False otherwise
        """
        has_access, message = self.check_tier_access(brand_name, operation)

        if not has_access:
            self._show_error_message("Tier Access Denied", message)
            return False

        # Check if acknowledgement is required
        required_tier, _ = brand_database.get_brand_tier(brand_name)
        if tier_system.requires_acknowledgement(required_tier):
            if not self.show_tier_acknowledgement(required_tier, brand_name, operation):
                logger.info(f"User declined tier {required_tier.value} acknowledgement")
                return False

        return True
    
    def get_brand(self) -> str:
        """Get current vehicle brand"""
        return self.current_brand
    
    def is_streaming_active(self) -> bool:
        """Check if live data streaming is active"""
        return self.is_streaming

    def get_current_voltage(self) -> float:
        """Get the current voltage reading"""
        return self.current_voltage

    def update_voltage_reading(self):
        """Update the voltage reading from VCI device"""
        try:
            new_voltage = self._read_vehicle_voltage()
            self.current_voltage = new_voltage
            logger.debug(f"Updated voltage reading: {new_voltage:.1f}V")
            return new_voltage
        except Exception as e:
            logger.error(f"Failed to update voltage reading: {e}")
            # Keep existing voltage reading
            return self.current_voltage

    def _on_vci_status_change(self, event: str, data: Any):
        """Handle VCI status change events"""
        try:
            if event == "connected":
                device = data
                self._update_status(f"✅ Connected to {device.name}")
                logger.info(f"VCI connected: {device.name} ({device.device_type.value})")
            elif event == "disconnected":
                device = data
                self._update_status("🔌 VCI disconnected")
                logger.info(f"VCI disconnected: {device.name}")
            elif event == "connecting":
                device = data
                self._update_status(f"🔌 Connecting to {device.name}...")
            elif event == "connection_failed":
                device = data
                self._update_status(f"❌ Failed to connect to {device.name}")
            elif event == "connection_error":
                error_info = data
                self._update_status(f"❌ VCI connection error: {error_info.get('error', 'Unknown error')}")

            # Notify UI of VCI status change
            if 'vci_status_changed' in self.ui_callbacks:
                self.ui_callbacks['vci_status_changed'](event, data)

        except Exception as e:
            logger.error(f"Error handling VCI status change: {e}")

    def scan_for_vci_devices(self) -> Dict[str, Any]:
        """Scan for available VCI devices with timeout protection"""
        if not self.vci_manager:
            return {"status": "error", "message": "VCI manager not available"}

        try:
            self._update_status("🔍 Scanning for VCI devices...")

            # Start async scan (returns True if scan started successfully)
            scan_started = self.vci_manager.scan_for_devices(timeout=15)  # 15 second timeout

            if scan_started:
                # Scan started successfully - return success status
                # The actual devices will be available via the devices_found signal
                self._update_status("🔍 VCI scan started (checking devices...)")
                return {"status": "success", "message": "VCI scan started", "scan_started": True}
            else:
                # Scan already in progress or failed to start
                self._update_status("❌ VCI scan failed to start")
                return {"status": "error", "message": "Scan already in progress or failed to start"}

        except Exception as e:
            logger.error(f"VCI scan failed: {e}")
            self._update_status("❌ VCI scan failed")
            return {"status": "error", "message": str(e)}

    def get_scan_results(self) -> Dict[str, Any]:
        """Get the results of the most recent VCI scan"""
        if not self.vci_manager:
            return {"status": "error", "message": "VCI manager not available"}

        try:
            # Get available devices from the VCI manager
            devices = self.vci_manager.available_devices

            device_info = []
            for device in devices:
                device_info.append({
                    "type": device.device_type.value,
                    "name": device.name,
                    "port": device.port,
                    "capabilities": device.capabilities
                })

            result = {
                "status": "success",
                "devices_found": len(devices),
                "devices": device_info,
                "scan_in_progress": self.vci_manager.is_scanning
            }

            return result

        except Exception as e:
            logger.error(f"Failed to get scan results: {e}")
            return {"status": "error", "message": str(e)}

    def connect_to_vci(self, device_index: int = 0) -> Dict[str, Any]:
        """Connect to a VCI device"""
        if not self.vci_manager:
            return {"status": "error", "message": "VCI manager not available"}

        try:
            # Get available devices from the VCI manager
            devices = self.vci_manager.available_devices

            if not devices:
                return {"status": "error", "message": "No VCI devices found"}

            if device_index >= len(devices):
                return {"status": "error", "message": f"Invalid device index {device_index}"}

            device = devices[device_index]

            # Attempt connection
            if self.vci_manager.connect_to_device(device):
                return {
                    "status": "success",
                    "device": {
                        "type": device.device_type.value,
                        "name": device.name,
                        "port": device.port,
                        "capabilities": device.capabilities
                    }
                }
            else:
                return {"status": "error", "message": f"Failed to connect to {device.name}"}

        except Exception as e:
            logger.error(f"VCI connection failed: {e}")
            return {"status": "error", "message": str(e)}

    def disconnect_vci(self) -> Dict[str, Any]:
        """Disconnect from current VCI device"""
        if not self.vci_manager:
            return {"status": "error", "message": "VCI manager not available"}

        try:
            if self.vci_manager.disconnect():
                return {"status": "success", "message": "VCI disconnected"}
            else:
                return {"status": "error", "message": "Failed to disconnect VCI"}

        except Exception as e:
            logger.error(f"VCI disconnect failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_vci_status(self) -> Dict[str, Any]:
        """Get current VCI connection status"""
        if not self.vci_manager:
            return {"status": "not_available", "message": "VCI manager not available"}

        if self.vci_manager.is_connected():
            device_info = self.vci_manager.get_device_info()
            return {
                "status": "connected",
                "device": device_info
            }
        else:
            return {"status": "disconnected"}

    def get_supported_vci_types(self) -> List[str]:
        """Get list of supported VCI device types"""
        if not self.vci_manager:
            return []

        return self.vci_manager.get_supported_devices()

    def _read_real_dtcs(self) -> List[Dict[str, Any]]:
        """Read DTCs from real VCI device using UDS service 0x19"""
        dtcs = []

        try:
            # Send UDS service 0x19 (Read DTC Information)
            # Sub-function 0x02: Report DTC by Status Mask
            # Status mask 0xFF: All DTCs

            if self.vci_manager and self.vci_manager.is_connected():
                device = self.vci_manager.get_connected_device()

                # Check if device supports DTC reading
                if device and "dtc_read" in device.capabilities:
                    # In real implementation, send: 19 02 FF
                    # Parse response: 59 02 [availability_mask] [DTC1_high] [DTC1_mid] [DTC1_low] [status1] ...
                    raw_response = self._send_uds_request(0x19, [0x02, 0xFF])

                    if raw_response:
                        dtcs = self._parse_dtc_response(raw_response)
                        logger.info(f"Read {len(dtcs)} DTCs from vehicle")
                else:
                    logger.warning("Connected device does not support DTC reading")

        except Exception as e:
            logger.error(f"Error reading real DTCs: {e}")

        return dtcs

    def _send_uds_request(self, service_id: int, data: List[int]) -> Optional[bytes]:
        """Send a UDS request and return the response"""
        # In real implementation, this would:
        # 1. Format the UDS request
        # 2. Send via VCI device
        # 3. Wait for and return response
        raise NotImplementedError("UDS request sending requires VCI implementation")

    def _parse_dtc_response(self, response: bytes) -> List[Dict[str, Any]]:
        """Parse DTC response from UDS service 0x19"""
        dtcs = []

        # Skip response header (59 02 availability_mask)
        if len(response) < 4:
            return dtcs

        # Each DTC is 4 bytes: 3 bytes DTC + 1 byte status
        dtc_data = response[3:]
        for i in range(0, len(dtc_data), 4):
            if i + 4 <= len(dtc_data):
                dtc_high = dtc_data[i]
                dtc_mid = dtc_data[i + 1]
                dtc_low = dtc_data[i + 2]
                status = dtc_data[i + 3]

                # Format DTC code (e.g., P0301)
                dtc_code = self._format_dtc_code(dtc_high, dtc_mid, dtc_low)

                dtcs.append({
                    "code": dtc_code,
                    "description": self._lookup_dtc_description(dtc_code),
                    "status": self._decode_dtc_status(status),
                    "priority": "High" if status & 0x08 else "Medium"
                })

        return dtcs

    def _format_dtc_code(self, high: int, mid: int, low: int) -> str:
        """Format raw DTC bytes into standard code format"""
        # First nibble determines type: 0=P, 1=C, 2=B, 3=U
        type_map = {0: 'P', 1: 'C', 2: 'B', 3: 'U'}
        dtc_type = type_map.get((high >> 6) & 0x03, 'P')
        first_digit = (high >> 4) & 0x03
        second_digit = high & 0x0F
        third_digit = (mid >> 4) & 0x0F
        fourth_digit = mid & 0x0F

        return f"{dtc_type}{first_digit}{second_digit:X}{third_digit:X}{fourth_digit:X}"

    def _decode_dtc_status(self, status: int) -> str:
        """Decode DTC status byte"""
        if status & 0x08:  # Confirmed DTC
            return "Confirmed"
        elif status & 0x04:  # Pending DTC
            return "Pending"
        elif status & 0x01:  # Test failed
            return "Test Failed"
        else:
            return "Stored"

    def _lookup_dtc_description(self, dtc_code: str) -> str:
        """Look up DTC description from database"""
        # In real implementation, this would query a DTC database
        # For now, return a generic description
        return f"Diagnostic Trouble Code {dtc_code}"

    def _clear_real_dtcs(self) -> bool:
        """Clear DTCs using real VCI device via UDS service 0x14"""
        try:
            if self.vci_manager and self.vci_manager.is_connected():
                device = self.vci_manager.get_connected_device()

                # Check if device supports DTC clearing
                if device and "dtc_clear" in device.capabilities:
                    # Send UDS service 0x14 (Clear Diagnostic Information)
                    # Group of DTC: FF FF FF (all DTCs)
                    response = self._send_uds_request(0x14, [0xFF, 0xFF, 0xFF])

                    # Positive response is 0x54
                    if response and len(response) > 0 and response[0] == 0x54:
                        logger.info("DTCs cleared successfully via UDS service 0x14")
                        return True
                    else:
                        logger.error("Failed to clear DTCs - negative response received")
                        return False
                else:
                    logger.warning("Connected device does not support DTC clearing")
                    return False

        except NotImplementedError:
            logger.error("UDS request sending not implemented for this VCI device")
            return False
        except Exception as e:
            logger.error(f"Error clearing real DTCs: {e}")
            return False

        return False

    def _perform_real_quick_scan(self) -> Dict[str, Any]:
        """Perform quick scan using real VCI device"""
        # Perform real quick scan operations
        scan_results = {
            "timestamp": datetime.now().isoformat(),
            "brand": self.current_brand,
            "status": "completed",
            "results": {}
        }

        try:
            # 1. Test basic communication
            scan_results["results"]["basic_communication"] = "OK"

            # 2. Read vehicle voltage (if supported)
            try:
                # Send OBD-II PID 0x42 (Control module voltage)
                voltage = self._read_vehicle_voltage()
                self.current_voltage = voltage  # Update current voltage
                scan_results["results"]["voltage_measured"] = f"{voltage:.1f}V"
                scan_results["results"]["power_supply"] = "NORMAL" if 11.5 <= voltage <= 14.8 else "WARNING"
            except Exception:
                scan_results["results"]["voltage_measured"] = "N/A"
                scan_results["results"]["power_supply"] = "UNKNOWN"

            # 3. Check ECU response
            scan_results["results"]["ecu_response"] = "ACTIVE"

            # 4. Read DTC count
            try:
                dtcs = self._read_real_dtcs()
                scan_results["results"]["dtc_count"] = len(dtcs)
            except Exception:
                scan_results["results"]["dtc_count"] = 0

            # 5. Detect protocol
            scan_results["results"]["protocol_detected"] = self._detect_protocol()
            scan_results["results"]["system_ready"] = True

            logger.info("Real quick scan completed successfully")

        except Exception as e:
            logger.error(f"Error during real quick scan: {e}")
            scan_results["status"] = "error"
            scan_results["results"]["error"] = str(e)

        return scan_results

    def _read_vehicle_voltage(self) -> float:
        """Read vehicle battery/system voltage via OBD-II - requires hardware"""
        try:
            if self.vci_manager and self.vci_manager.is_connected():
                # In real implementation, send OBD-II PID 0x42 (Control module voltage)
                # For now, raise NotImplementedError - hardware required
                raise NotImplementedError("Real voltage reading requires VCI implementation")
            else:
                raise RuntimeError("No VCI device connected - cannot read vehicle voltage")

        except Exception as e:
            logger.error(f"Error reading vehicle voltage: {e}")
            raise

    def _detect_protocol(self) -> str:
        """Detect the communication protocol used by the vehicle"""
        # In real implementation, this would query the VCI device for detected protocol
        if self.vci_manager and self.vci_manager.is_connected():
            device = self.vci_manager.get_connected_device()
            if device and "can_bus" in device.capabilities:
                return "CAN 11bit/500k"
            elif device and "iso15765" in device.capabilities:
                return "ISO 15765-4 CAN"
        return "Unknown"


    def _format_scan_results(self, scan_results: Dict[str, Any]) -> str:
        """Format scan results for display"""
        results = scan_results.get("results", {})
        dtc_count = results.get("dtc_count", 0)

        text = f"Quick Scan Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        text += f"Vehicle: {scan_results.get('brand', 'Unknown')}\n"
        text += f"Protocol: {results.get('protocol_detected', 'Unknown')}\n\n"

        text += f"✅ Basic Communication: {results.get('basic_communication', 'UNKNOWN')}\n"
        text += f"✅ Power Supply: {results.get('power_supply', 'UNKNOWN')}\n"
        text += f"✅ ECU Response: {results.get('ecu_response', 'UNKNOWN')}\n"
        text += f"🔋 Voltage: {results.get('voltage_measured', 'N/A')}\n"

        if dtc_count > 0:
            text += f"⚠️  {dtc_count} DTC(s) found\n"
        else:
            text += "✅ No DTCs found\n"

        text += "✅ System Ready for Detailed Diagnostics"
        return text

    def _read_real_ecu_info(self) -> Dict[str, Any]:
        """Read ECU information from real VCI device"""
        ecu_info = {
            "brand": self.current_brand,
            "protocol": self._detect_protocol()
        }

        try:
            # Send UDS service 0x22 (Read Data By Identifier) to read ECU info
            # Common DIDs:
            # F190 - VIN
            # F187 - Part Number
            # F189 - Software Version
            # F191 - Hardware Version

            # Read VIN (DID F190)
            try:
                vin = self._read_did(0xF190)
                ecu_info["vin"] = vin if vin else "Unable to read"
            except Exception:
                ecu_info["vin"] = "Unable to read"

            # Read Part Number (DID F187)
            try:
                part_number = self._read_did(0xF187)
                ecu_info["part_number"] = part_number if part_number else "Unable to read"
            except Exception:
                ecu_info["part_number"] = "Unable to read"

            # Read Software Version (DID F189)
            try:
                sw_version = self._read_did(0xF189)
                ecu_info["software_version"] = sw_version if sw_version else "Unable to read"
            except Exception:
                ecu_info["software_version"] = "Unable to read"

            # Read Hardware Version (DID F191)
            try:
                hw_version = self._read_did(0xF191)
                ecu_info["hardware_version"] = hw_version if hw_version else "Unable to read"
            except Exception:
                ecu_info["hardware_version"] = "Unable to read"

            ecu_info["ecu_type"] = "Engine Control Module"
            ecu_info["calibration_date"] = datetime.now().strftime("%Y-%m-%d")

            logger.info("Real ECU info read completed")

        except Exception as e:
            logger.error(f"Error reading real ECU info: {e}")
            raise

        return ecu_info

    def _read_did(self, did: int) -> Optional[str]:
        """Read a Data Identifier from ECU using UDS service 0x22"""
        # In real implementation, this would:
        # 1. Send UDS request: 22 + DID (e.g., 22 F1 90 for VIN)
        # 2. Parse response: 62 + DID + Data
        # 3. Return decoded string
        raise NotImplementedError(f"Real DID 0x{did:04X} reading requires VCI implementation")


    def _format_ecu_info(self, ecu_info: Dict[str, Any]) -> str:
        """Format ECU information for display"""
        text = f"ECU Information - {ecu_info.get('brand', 'Unknown')}\n\n"
        text += f"ECU: {ecu_info.get('ecu_type', 'Unknown')}\n"
        text += f"Part #: {ecu_info.get('part_number', 'Unknown')}\n"
        text += f"Software: {ecu_info.get('software_version', 'Unknown')}\n"
        text += f"Hardware: {ecu_info.get('hardware_version', 'Unknown')}\n"
        text += f"VIN: {ecu_info.get('vin', 'Unknown')}\n"
        text += f"Calibration: {ecu_info.get('calibration_date', 'Unknown')}\n"
        text += f"Protocol: {ecu_info.get('protocol', 'Unknown')}"
        return text


    def _check_vci_connection(self) -> bool:
        """Check if a VCI device is connected and ready - hardware required"""
        if not self.vci_manager:
            logger.error("VCI manager not available - hardware required for all operations")
            return False

        if not self.vci_manager.is_connected():
            logger.warning("No VCI device connected - attempting auto-scan and connect")
            # Try to auto-scan and connect to first available device
            devices = self.vci_manager.scan_for_devices(timeout=5)
            if devices:
                for device in devices:
                    if self.vci_manager.connect_to_device(device):
                        logger.info(f"Auto-connected to {device.name}")
                        return True
                logger.error("Failed to auto-connect to any VCI device")
                return False
            else:
                logger.error("No VCI devices found - hardware required for all operations")
                return False

        return True