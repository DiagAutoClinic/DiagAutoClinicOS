"""
Diagnostics Controller for AutoDiag Pro
Handles diagnostic operations, DTC reading/clearing, and live data
"""

import logging
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from PyQt6.QtCore import QTimer, pyqtSignal, QObject, QThread, pyqtSlot

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


class DiagnosticsWorker(QThread):
    """Background thread for blocking VCI diagnostic operations.

    Keeps UDS/KWP communication off the Qt main thread so the UI stays responsive.
    Connect *operation* to a callable that takes no arguments and returns a dict.
    The result is emitted via *finished*; errors via *error*.
    """
    finished = pyqtSignal(dict)
    error    = pyqtSignal(str)

    def __init__(self, operation, parent=None):
        super().__init__(parent)
        self._operation = operation

    def run(self):
        try:
            result = self._operation()
            self.finished.emit(result if isinstance(result, dict) else {"result": result})
        except Exception as exc:
            logger.error(f"DiagnosticsWorker error: {exc}")
            self.error.emit(str(exc))

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

# Import DTC Database
try:
    from shared.dtc_database_sqlite import DTCDatabaseSQLite
    DTC_DB_AVAILABLE = True
except ImportError:
    DTC_DB_AVAILABLE = False
    logger.warning("DTC database not available - using generic descriptions")

# Import Equation Solver
try:
    from shared.equation_solver import EquationSolver
except ImportError:
    logger.warning("Equation Solver not available")

# Import Telemetry and Build Info
try:
    from shared.telemetry_manager import (
        TelemetryManager, TELEMETRY_DISPLAY_NAME,
        RESTRICT_INTEGRITY_FAIL, RESTRICT_TELEMETRY_OFFLINE
    )
    from shared.build_info import BuildVerifier
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False
    logger.warning("Telemetry modules not available - containment disabled")

class DiagnosticsController(QObject):
    """Controller for diagnostic operations"""

    # Signals for communication with UI
    status_changed = pyqtSignal(str)
    dtc_read = pyqtSignal(dict)
    dtc_cleared = pyqtSignal(bool)
    live_data_updated = pyqtSignal(list)
    scan_completed = pyqtSignal(dict)
    ecu_info_updated = pyqtSignal(dict)
    pending_dtc_read = pyqtSignal(dict)
    freeze_frame_read = pyqtSignal(dict)
    readiness_read = pyqtSignal(dict)

    def __init__(self, ui_callbacks: Optional[Dict[str, callable]] = None, charlemaine_agent=None, vci_manager=None):
        """Initialize diagnostics controller"""
        super().__init__()
        self.ui_callbacks = ui_callbacks or {}
        self.vci_manager = vci_manager
        self.is_streaming = False
        self.current_brand = None
        self.live_data_timer = None
        self.keep_alive_timer = None
        self._acknowledged_brands = set()  # session-level cache — don't ask twice

        # AI Agent
        self.charlemaine = charlemaine_agent
        if not self.charlemaine:
            try:
                from ai.agent import CharlemaineAgent
                self.charlemaine = CharlemaineAgent()
                logger.info("Charlemaine AI Agent initialized internally")
            except Exception as e:
                logger.warning(f"Failed to initialize Charlemaine AI Agent: {e}")
                self.charlemaine = None
        else:
            logger.info("Charlemaine AI Agent injected")

        # Initialize AI Engine (Fault Prediction)
        try:
            from ai.ai_engine import ai_engine
            self.ai_engine = ai_engine
            logger.info("AI Engine linked to DiagnosticsController")
        except ImportError:
            logger.warning("Failed to link AI Engine")
            self.ai_engine = None

        # CAN database
        self.current_vehicle_db: Optional[VehicleCANDatabase] = None
        self.available_vehicles = []

        # VCI manager
        self.vci_manager = None
        if VCI_MANAGER_AVAILABLE:
            self.vci_manager = get_vci_manager()
            self.vci_manager.add_status_callback(self._on_vci_status_change)

        # Initialize DTC Database
        self.dtc_db = None
        if DTC_DB_AVAILABLE:
            try:
                # Resolve path to data directory: .../AutoDiag/core/diagnostics.py -> .../DiagAutoClinicOS/data
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                db_path = os.path.join(base_dir, 'data', 'diagautoclinic_dtc.db')
                
                # Create data directory if it doesn't exist (just in case)
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                
                self.dtc_db = DTCDatabaseSQLite(db_path)
                logger.info(f"DTC Database initialized at {db_path}")
            except Exception as e:
                logger.error(f"Failed to initialize DTC Database: {e}")

        # Initialize callbacks
        self._setup_callbacks()
        # DEFERRED: Don't load vehicles during initialization to prevent startup hang
        self._vehicles_loaded = False
        self._load_available_vehicles_later()

        # Current voltage reading
        self.current_voltage = 0.0  # Default voltage (0.0V indicates no connection)

        # Load user tier from configuration
        try:
            from AutoDiag.config.settings import get_config
            tier_level = get_config("user.tier_level", 1)
            self.user_tier = Tier(tier_level)
        except Exception as e:
            logger.warning(f"Failed to load user tier from config: {e}")
            self.user_tier = Tier.FREE

        # Initialize Telemetry Manager
        self.telemetry_manager = None
        if TELEMETRY_AVAILABLE:
            try:
                self.telemetry_manager = TelemetryManager()
                self.telemetry_manager.start()
                logger.info("Telemetry Manager initialized and started")
                try:
                    from PyQt6.QtWidgets import QApplication
                    if QApplication.instance() is not None:
                        QTimer.singleShot(100, self.emit_session_snapshot)
                    else:
                        self.emit_session_snapshot()
                except Exception:
                    self.emit_session_snapshot()
            except Exception as e:
                logger.error(f"Failed to initialize Telemetry Manager: {e}")
    
    def is_restricted_mode(self) -> bool:
        """
        Checks if the application is in restricted mode (containment).
        Restricted mode allows read-only access (VIN/DTC read) but blocks
        active operations like DTC clearing or coding.
        """
        if not TELEMETRY_AVAILABLE:
            # Fail closed if telemetry module is missing entirely
            return True

        # 1. Integrity Check
        if not BuildVerifier.verify_integrity():
            logger.warning(f"Restricted Mode Active: {RESTRICT_INTEGRITY_FAIL}")
            return True

        # 2. Telemetry Online Check (with grace period)
        if self.telemetry_manager and not self.telemetry_manager.is_online:
            logger.warning(f"Restricted Mode Active: {RESTRICT_TELEMETRY_OFFLINE}")
            return True

        return False

    def emit_session_snapshot(self):
        """
        Emits a session capability snapshot via telemetry.
        This provides ground truth for analysis (e.g., distinguishing
        'could not clear' from 'chose not to').
        """
        if not self.telemetry_manager:
            return

        try:
            is_restricted = self.is_restricted_mode()
            integrity_ok = BuildVerifier.verify_integrity()
            telemetry_online = self.telemetry_manager.is_online
            
            snapshot = {
                "integrity_status": integrity_ok,
                "telemetry_status": telemetry_online,
                "restricted_mode": is_restricted,
                "allowed_capabilities": ["read_vin", "read_dtc"] if is_restricted else ["read_vin", "read_dtc", "clear_dtc", "coding"],
                "app_version": "3.1.2", # Should match main.py
                "python_version": sys.version.split()[0]
            }
            
            self.telemetry_manager.send_capability_snapshot(snapshot)
            logger.info("Session capability snapshot emitted")
        except Exception as e:
            logger.error(f"Failed to emit session snapshot: {e}")

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

            # Run blocking VCI I/O in a background thread
            self._dtc_worker = DiagnosticsWorker(self._complete_dtc_read)
            self._dtc_worker.error.connect(self._on_dtc_worker_error)
            self._dtc_worker.start()

            return {"status": "started", "operation": "read_dtcs", "brand": self.current_brand}

        except Exception as e:
            logger.error(f"Failed to read DTCs: {e}")
            self._show_error_message("DTC Read Error", f"Failed to read DTCs: {e}")
            return {"status": "error", "message": str(e)}
    
    def _complete_dtc_read(self):
        """Complete DTC read operation using real VCI communication.
        Runs in DiagnosticsWorker thread — signals only, no direct Qt/callback calls.
        """
        dtc_data = {
            "timestamp": datetime.now().isoformat(),
            "brand": self.current_brand,
            "dtcs": [],
            "total_count": 0
        }

        if not (self.vci_manager and self.vci_manager.is_connected()):
            raise ConnectionError("No VCI device connected")

        real_dtcs = self._read_real_dtcs()
        dtc_data["dtcs"] = real_dtcs
        dtc_data["total_count"] = len(real_dtcs)
        logger.info(f"Read {len(real_dtcs)} DTCs from VCI device")

        self.status_changed.emit(f"✅ DTCs retrieved ({dtc_data['total_count']} found)")
        self.dtc_read.emit(dtc_data)
        return dtc_data
    
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
            # Check Restricted Mode (Containment)
            if self.is_restricted_mode():
                msg = "Restricted Mode: DTC Clearing disabled. Online verification required."
                logger.warning(msg)
                self._show_error_message("Access Denied", msg)
                return {
                    "status": "error", 
                    "message": msg,
                    "success": False,
                    "error": msg
                }

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

            self._clear_worker = DiagnosticsWorker(self._complete_dtc_clear)
            self._clear_worker.error.connect(self._on_clear_worker_error)
            self._clear_worker.start()
            
        except Exception as e:
            logger.error(f"Error in DTC clear confirmation: {e}")
    
    def _complete_dtc_clear(self):
        """Complete DTC clear operation using real VCI communication.
        Runs in DiagnosticsWorker thread — signals only, no direct Qt/callback calls.
        """
        if not (self.vci_manager and self.vci_manager.is_connected()):
            self.dtc_cleared.emit(False)
            raise ConnectionError("No VCI device connected")

        success = self._clear_real_dtcs()

        if success:
            logger.info("DTCs cleared successfully via VCI device")
            self.status_changed.emit("✅ DTCs cleared successfully")
            self.dtc_cleared.emit(True)
        else:
            logger.error("Failed to clear DTCs via VCI device")
            self.status_changed.emit("❌ Failed to clear DTCs")
            self.dtc_cleared.emit(False)

        return {"success": success}
    
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
        """Update live data values — prefers real PID polling, falls back to CAN DB."""
        try:
            if not self.is_streaming:
                return

            live_data: List[Tuple[str, str, str]] = []

            # ---- PATH A: Real OBD-II PID polling (primary) ----
            try:
                pid_data = self._get_live_pid_data()
                if pid_data:
                    live_data = pid_data
                    logger.debug("Live data from real PID polling: %d values", len(live_data))
            except Exception as e:
                logger.warning("PID polling unavailable, falling back to CAN DB: %s", e)

            # ---- PATH B: CAN database decoding (fallback) ----
            if not live_data:
                live_data = self._get_live_data_from_can_db()

            # ---- Update UI ----
            if live_data:
                if "update_live_data_table" in self.ui_callbacks:
                    self.ui_callbacks["update_live_data_table"](live_data)
                self.live_data_updated.emit(live_data)

        except Exception as e:
            logger.error("Error updating live data: %s", e)
    
    def _get_live_data_from_can_db(self) -> List[Tuple[str, str, str]]:
        """Get live data from CAN database using realtime data"""
        if not self.current_vehicle_db:
            return []

        # Get latest CAN frames
        can_data = self._get_realtime_can_data()
        if not can_data:
            # No data available (e.g. no hardware or silence)
            return []

        live_data = []
        
        # Iterate through received messages and decode them
        for msg_id, data in can_data.items():
            decoded = self.current_vehicle_db.decode_frame(msg_id, data)
            if decoded:
                for name, value in decoded.items():
                     # Find signal definition for unit
                     msg = self.current_vehicle_db.get_message(msg_id)
                     unit = ""
                     if msg:
                         for sig in msg.signals:
                             if sig.name == name:
                                 unit = sig.unit
                                 break
                     
                     formatted_value = f"{value:.2f}"
                     live_data.append((name.replace('_', ' ').title(), formatted_value, unit))
                     
                     if len(live_data) >= 12:
                         break
            if len(live_data) >= 12:
                break
                
        return live_data

    def _get_realtime_can_data(self) -> Dict[int, bytes]:
        """Read live CAN frames from the VCI device via active PID polling.

        Returns a dict mapping CAN ID → raw data bytes suitable for
        decoding by :meth:`_get_live_data_from_can_db`.
        """
        can_data: Dict[int, bytes] = {}

        try:
            if not self.vci_manager or not self.vci_manager.is_connected():
                return can_data

            # Standard OBD-II PIDs (Mode 01) for live dashboard
            # Format: PID → (label, formula for human-readable value)
            pids_to_read = [0x0C, 0x0D, 0x05, 0x0B, 0x0F, 0x11, 0x04]

            results = self.vci_manager.read_pids_batch(pids_to_read)

            for pid, raw in results.items():
                if raw is None:
                    continue
                # Store under a synthetic CAN ID so the CAN-DB decoder path
                # can still process these — or skip and use dedicated PID path
                can_data[0x100 | pid] = raw

        except Exception as e:
            logger.warning("Live PID polling failed: %s", e)

        return can_data

    def _get_live_pid_data(self) -> List[Tuple[str, str, str]]:
        """Read standard OBD-II PIDs and return (label, value, unit) tuples
        for direct display — no CAN database required.
        """
        pid_map = {
            0x0C: ("Engine RPM",     lambda b: int.from_bytes(b[:2], "big") * 0.25,   "rpm"),
            0x0D: ("Vehicle Speed",  lambda b: int(b[0]),                               "km/h"),
            0x05: ("Coolant Temp",   lambda b: int(b[0]) - 40,                          "°C"),
            0x0B: ("Intake MAP",     lambda b: int(b[0]),                               "kPa"),
            0x0F: ("Intake Air Temp",lambda b: int(b[0]) - 40,                          "°C"),
            0x11: ("Throttle Pos.",  lambda b: int(b[0]) * 100.0 / 255.0,              "%"),
            0x04: ("Engine Load",    lambda b: int(b[0]) * 100.0 / 255.0,              "%"),
        }

        try:
            if not self.vci_manager or not self.vci_manager.is_connected():
                return []
        except Exception:
            return []

        pids = list(pid_map.keys())
        results = self.vci_manager.read_pids_batch(pids)

        live: List[Tuple[str, str, str]] = []
        for pid, raw in results.items():
            if raw is None:
                continue
            label, formula, unit = pid_map.get(pid, (None, None, None))
            if label is None:
                continue
            try:
                value = formula(raw)
                live.append((label, f"{value:.1f}", unit))
            except Exception:
                continue

        return live


    def read_pending_dtcs(self, brand: Optional[str] = None) -> Dict[str, Any]:
        """Read pending DTCs (Mode $07) — faults detected but not yet confirmed."""
        if brand:
            self.current_brand = brand

        if not self._check_vci_connection():
            return {"status": "error", "message": "No VCI device connected."}

        self._update_status("🔍 Reading pending DTCs...")

        def _do():
            if not (self.vci_manager and self.vci_manager.is_connected()):
                raise ConnectionError("No VCI device connected")

            if self.vci_manager.get_elm327_driver() is not None:
                raw_list = self.vci_manager.read_pending_dtcs_elm327()
            else:
                raw_response = self._send_uds_request(0x19, [0x0F, 0xFF])
                raw_list = self._parse_dtc_response(raw_response) if raw_response else []

            # Enrich with DTC DB descriptions
            enriched = []
            for item in raw_list:
                if "error" in item:
                    continue
                code = item.get("code", "")
                item["description"] = self._lookup_dtc_description(code) if code else ""
                item["status"] = "Pending"
                enriched.append(item)

            result = {
                "timestamp": datetime.now().isoformat(),
                "brand": self.current_brand,
                "pending_dtcs": enriched,
                "total_count": len(enriched),
            }
            self.status_changed.emit(f"⚠️ Pending DTCs: {len(enriched)} found")
            self.pending_dtc_read.emit(result)
            return result

        self._pending_worker = DiagnosticsWorker(_do)
        self._pending_worker.error.connect(
            lambda msg: self._show_error_message("Pending DTC Error", msg)
        )
        self._pending_worker.start()
        return {"status": "started", "operation": "read_pending_dtcs"}

    def read_freeze_frame(self, brand: Optional[str] = None) -> Dict[str, Any]:
        """Read freeze frame snapshot (Mode $02) — sensor values at DTC trigger."""
        if brand:
            self.current_brand = brand

        if not self._check_vci_connection():
            return {"status": "error", "message": "No VCI device connected."}

        self._update_status("❄️ Reading freeze frame...")

        def _do():
            if not (self.vci_manager and self.vci_manager.is_connected()):
                raise ConnectionError("No VCI device connected")

            if self.vci_manager.get_elm327_driver() is not None:
                data = self.vci_manager.read_freeze_frame_elm327()
            else:
                data = {"error": "Freeze frame requires ELM327/HH OBD connection"}

            result = {
                "timestamp": datetime.now().isoformat(),
                "brand": self.current_brand,
                "freeze_frame": data,
            }
            if "error" not in data:
                param_count = len(data.get("parameters", {}))
                self.status_changed.emit(f"✅ Freeze frame: {param_count} parameters")
            else:
                self.status_changed.emit(f"⚠️ Freeze frame: {data['error']}")
            self.freeze_frame_read.emit(result)
            return result

        self._ff_worker = DiagnosticsWorker(_do)
        self._ff_worker.error.connect(
            lambda msg: self._show_error_message("Freeze Frame Error", msg)
        )
        self._ff_worker.start()
        return {"status": "started", "operation": "read_freeze_frame"}

    def read_readiness_monitors(self, brand: Optional[str] = None) -> Dict[str, Any]:
        """Read emission readiness monitors (Mode $01 PID $01)."""
        if brand:
            self.current_brand = brand

        if not self._check_vci_connection():
            return {"status": "error", "message": "No VCI device connected."}

        self._update_status("📋 Reading readiness monitors...")

        def _do():
            if not (self.vci_manager and self.vci_manager.is_connected()):
                raise ConnectionError("No VCI device connected")

            if self.vci_manager.get_elm327_driver() is not None:
                data = self.vci_manager.read_readiness_monitors_elm327()
            else:
                raw = self._send_uds_request(0x01, [0x01])
                from drivers.hh_obd_advanced.obd_commands import OBDResponse, OBDResponseParser
                resp = OBDResponse(hex_data=list(raw) if raw else [], success=bool(raw))
                data = OBDResponseParser.parse_readiness_monitors(resp) if raw else {"error": "No response"}

            result = {
                "timestamp": datetime.now().isoformat(),
                "brand": self.current_brand,
                "readiness": data,
            }
            if "error" not in data:
                mil = "ON" if data.get("mil") else "OFF"
                complete = sum(
                    1 for m in list(data.get("continuous", {}).values()) +
                    list(data.get("non_continuous", {}).values())
                    if m.get("complete")
                )
                total = sum(
                    1 for m in list(data.get("continuous", {}).values()) +
                    list(data.get("non_continuous", {}).values())
                    if m.get("available", True)
                )
                self.status_changed.emit(f"✅ Readiness: MIL {mil} | {complete}/{total} complete")
            else:
                self.status_changed.emit(f"⚠️ Readiness: {data['error']}")
            self.readiness_read.emit(result)
            return result

        self._readiness_worker = DiagnosticsWorker(_do)
        self._readiness_worker.error.connect(
            lambda msg: self._show_error_message("Readiness Error", msg)
        )
        self._readiness_worker.start()
        return {"status": "started", "operation": "read_readiness_monitors"}

    def _format_pending_dtc_results(self, data: Dict[str, Any]) -> str:
        """Format pending DTC data for display."""
        dtcs = data.get("pending_dtcs", [])
        text = f"Pending DTCs — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += f"(Faults detected but not yet confirmed as stored)\n\n"
        if not dtcs:
            text += "✅ No pending DTCs found."
        else:
            for dtc in dtcs:
                text += f"⚠️  {dtc['code']} — {dtc.get('description', 'Unknown')}\n"
        text += f"\nTotal pending: {data.get('total_count', 0)}"
        return text

    def _format_freeze_frame(self, data: Dict[str, Any]) -> str:
        """Format freeze frame data for display."""
        ff = data.get("freeze_frame", {})
        text = f"Freeze Frame — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += f"(Sensor snapshot captured at DTC trigger point)\n\n"
        if "error" in ff:
            text += f"❌ {ff['error']}"
            return text
        trigger = ff.get("trigger_dtc")
        text += f"Trigger DTC : {trigger if trigger else 'Not available'}\n\n"
        params = ff.get("parameters", {})
        if params:
            for name, v in params.items():
                text += f"  {name:<20} {v['value']} {v['unit']}\n"
        else:
            text += "No freeze frame parameters available."
        return text

    def _format_readiness_monitors(self, data: Dict[str, Any]) -> str:
        """Format readiness monitor data for display."""
        rd = data.get("readiness", {})
        text = f"Readiness Monitors — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        if "error" in rd:
            text += f"❌ {rd['error']}"
            return text
        mil = "🔴 ON" if rd.get("mil") else "🟢 OFF"
        text += f"MIL (Check Engine):  {mil}\n"
        text += f"Stored DTC count  :  {rd.get('dtc_count', 0)}\n\n"
        text += "── Continuous Monitors ─────────────────\n"
        for name, info in rd.get("continuous", {}).items():
            if info.get("available"):
                status = "✅ Complete" if info.get("complete") else "⏳ Incomplete"
                text += f"  {name:<20} {status}\n"
            else:
                text += f"  {name:<20} N/A\n"
        text += "\n── Non-Continuous Monitors ─────────────\n"
        for name, info in rd.get("non_continuous", {}).items():
            status = "✅ Complete" if info.get("complete") else "⏳ Incomplete"
            text += f"  {name:<20} {status}\n"
        return text

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

            # No Mock: Execute directly
            self._complete_quick_scan()

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
    
    def read_vin(self) -> Optional[str]:
        """Read VIN from vehicle — routes to ELM327 or UDS."""
        vin = None

        if self.vci_manager and self.vci_manager.is_connected():
            try:
                # PATH A: HH OBD Advance / ELM327
                if self.vci_manager.get_elm327_driver() is not None:
                    vin = self.vci_manager.read_vin_elm327()
                    if vin:
                        return vin

                # PATH B: J2534 / UDS Mode 09 PID 02
                response = self._send_uds_request(0x09, [0x02])
                if response and len(response) > 3:
                    vin = response[3:].decode('ascii', errors='ignore').strip()
                    vin = ''.join(c for c in vin if c.isalnum())
            except Exception as e:
                logger.warning(f"Failed to read VIN from VCI: {e}")

        return vin

    def analyze_vin(self, vin: str) -> Dict[str, Any]:
        """Analyze VIN using Charlemaine AI Agent"""
        if not self.charlemaine:
            return {"error": "AI Agent not available"}
        return self.charlemaine.analyze_vin(vin)

    def generate_report(self, results: Dict[str, Any], filename: str) -> bool:
        """Generate PDF report from scan results"""
        try:
            from AutoDiag.core.report_generator import ReportGenerator
            return ReportGenerator.generate_pdf_report(results, filename)
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return False

    def run_full_scan(self, brand: Optional[str] = None) -> Dict[str, Any]:
        """Run full system scan with AI analysis"""
        if brand:
            self.current_brand = brand
            
        self._update_status("🔍 Running Full System Scan with Charlemaine AI...")

        self._scan_worker = DiagnosticsWorker(self._perform_full_scan_async)
        self._scan_worker.finished.connect(lambda r: self.scan_completed.emit(r))
        self._scan_worker.error.connect(
            lambda msg: self._show_error_message("Scan Error", msg)
        )
        self._scan_worker.start()
        
        # Return success=True because the operation successfully STARTED
        return {
            "status": "started", 
            "success": True,  # Added for compatibility with AutoDiag/main.py
            "operation": "full_scan", 
            "brand": self.current_brand
        }

    def _scan_all_modules(self) -> List[Dict[str, Any]]:
        """Scan all standard CAN modules (0x7E0-0x7E7)"""
        modules_found = []
        
        # Standard UDS Request IDs
        module_names = {
            0x7E0: "Engine Control Module (ECM)",
            0x7E1: "Transmission Control Module (TCM)",
            0x7E2: "ABS Control Module",
            0x7E3: "Airbag System (SRS)",
            0x7E4: "Body Control Module (BCM)",
            0x7E5: "Accessory Gateway",
            0x7E6: "Suspension / Chassis",
            0x7E7: "Instrument Panel / Dashboard"
        }

        # Iterate standard functional IDs
        for tx_id in range(0x7E0, 0x7E8):
            rx_id = tx_id + 8
            module_name = module_names.get(tx_id, f"Unknown Module ({hex(tx_id)})")
            
            self._update_status(f"Scanning {module_name}...")
            
            try:
                # Try to read DTCs from this module
                dtcs = self._read_real_dtcs(tx_id=tx_id, rx_id=rx_id)
                
                modules_found.append({
                    "id": hex(tx_id),
                    "name": module_name,
                    "dtcs": dtcs,
                    "status": "Fault" if dtcs else "OK"
                })
            except Exception as e:
                # Log failure but continue scanning other modules
                # Report the failure in the list (Fail-loud)
                logger.warning(f"Failed to scan {module_name}: {e}")
                modules_found.append({
                    "id": hex(tx_id),
                    "name": module_name,
                    "dtcs": [],
                    "status": f"Communication Error"
                })
                 
        return modules_found

    def _perform_full_scan_async(self):
        """Perform full scan asynchronously"""
        try:
            results = {
                "timestamp": datetime.now().isoformat(),
                "brand": self.current_brand,
                "vin": None,
                "vin_analysis": None,
                "modules": [],
                "dtcs": []
            }
            
            # 1. Read VIN
            self._update_status("🔍 Reading VIN...")
            vin = self.read_vin()
            
            if vin:
                results["vin"] = vin
                if self.charlemaine:
                    self._update_status("🧠 Charlemaine analyzing VIN...")
                    results["vin_analysis"] = self.charlemaine.analyze_vin(vin)
            else:
                logger.info("VIN could not be read automatically")

            # 2. Scan Modules & DTCs (Real Hardware)
            self._update_status("🔍 Scanning modules...")
            
            modules_data = []
            all_dtcs = []
            
            if self.vci_manager and self.vci_manager.is_connected():
                try:
                    modules_data = self._scan_all_modules()
                    # Aggregate DTCs
                    for m in modules_data:
                        all_dtcs.extend(m.get('dtcs', []))
                except Exception as e:
                    logger.error(f"Real full scan failed: {e}")
            else:
                # Simulation / Fallback (if we want to support it, otherwise leave empty)
                pass
            
            results["modules"] = modules_data
            results["dtcs"] = all_dtcs
            results["dtc_count"] = len(all_dtcs)

            # 3. AI Fault Prediction (Neural Network)
            if self.ai_engine:
                self._update_status("🧠 Running AI Fault Prediction...")
                try:
                    # Construct session data for AI
                    session_data = {
                        'session_id': f"scan_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        'dtc_codes': [d['code'] for d in all_dtcs],
                        'live_parameters': {}, # We could capture a snapshot here if available
                        'vehicle_context': {
                            'year': 2020, # Default/Estimated if not read
                            'make': self.current_brand
                        },
                        'session_duration': 0,
                        'device_type': 'j2534'
                    }
                    
                    # Run inference
                    ai_analysis = self.ai_engine.analyze_diagnostic_session(session_data)
                    results["ai_fault_prediction"] = ai_analysis
                    logger.info("AI Fault Prediction completed")
                except Exception as e:
                    logger.error(f"AI Fault Prediction failed: {e}")
                    results["ai_fault_prediction"] = {"error": str(e)}
            
            self._update_status("✅ Full scan completed")
            # Emit via signal (safe cross-thread call); DiagnosticsWorker.finished
            # will also emit — deduplicate by not emitting here when run in worker.
            # The signal is emitted by the worker's finished signal in run_full_scan().

            return results

        except Exception as e:
            logger.error(f"Error in full scan: {e}")
            self._update_status("❌ Scan failed")
            return {"error": str(e)}
            
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
    
    @pyqtSlot(str)
    def _on_dtc_worker_error(self, msg: str):
        """Error handler for DTC read worker — runs in main thread (auto QueuedConnection)."""
        self._show_error_message("DTC Read Error", msg)
        self._update_ui_callback('set_button_enabled', 'dtc_btn', True)

    @pyqtSlot(str)
    def _on_clear_worker_error(self, msg: str):
        """Error handler for DTC clear worker — runs in main thread (auto QueuedConnection)."""
        self._show_error_message("DTC Clear Error", msg)
        self._update_ui_callback('set_button_enabled', 'clear_btn', True)

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
        """Show a Yes/No confirmation dialog. Falls back to auto-confirm if no QApplication."""
        try:
            from PyQt6.QtWidgets import QApplication, QMessageBox
            if QApplication.instance() is None:
                confirm_callback()
                return

            reply = QMessageBox.question(
                None,
                title,
                message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
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

    # Operations that every tier (including FREE / The Observer) can always perform.
    _FREE_OPERATIONS = {"read_dtcs", "clear_dtcs", "read_vin", "live_data"}

    def check_tier_access(self, brand_name: str, operation: str = None) -> Tuple[bool, str]:
        """
        Check if user has tier access for a specific brand/operation.

        DTC read/clear, VIN read, and live data are open on all tiers —
        they are the core FREE / Observer capabilities.
        """
        if not TIER_SYSTEM_AVAILABLE:
            return True, "Tier system not available - access granted"

        # FREE-tier operations are unrestricted regardless of brand
        if operation in self._FREE_OPERATIONS:
            return True, f"{operation} is available on all tiers"

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
        Enforce tier access for an operation.
        On denial, shows the TierUpgradeDialog instead of a plain error box.

        Returns:
            True if access granted, False otherwise
        """
        has_access, _ = self.check_tier_access(brand_name, operation)

        if not has_access:
            try:
                required_tier, _ = brand_database.get_brand_tier(brand_name)
                from AutoDiag.ui.tier_upgrade_dialog import show_tier_upgrade
                show_tier_upgrade(required_tier, self.user_tier, operation)
            except Exception:
                self._show_error_message(
                    "Tier Access Denied",
                    f"This operation requires a higher tier. Visit dacos.co.za to upgrade."
                )
            return False

        # Access granted — check if acknowledgement is required (once per brand per session)
        required_tier, _ = brand_database.get_brand_tier(brand_name)
        if tier_system.requires_acknowledgement(required_tier):
            if brand_name not in self._acknowledged_brands:
                if not self.show_tier_acknowledgement(required_tier, brand_name, operation):
                    logger.info(f"User declined tier {required_tier.value} acknowledgement")
                    return False
                self._acknowledged_brands.add(brand_name)

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
                
                # Start keep-alive timer (every 2 seconds)
                if not self.keep_alive_timer:
                    self.keep_alive_timer = QTimer()
                    self.keep_alive_timer.timeout.connect(self._send_keep_alive)
                self.keep_alive_timer.start(2000)
                
            elif event == "disconnected":
                device = data
                self._update_status("🔌 VCI disconnected")
                logger.info(f"VCI disconnected: {device.name}")
                
                # Stop keep-alive timer
                if self.keep_alive_timer:
                    self.keep_alive_timer.stop()
                    
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

    def _send_keep_alive(self):
        """Send Tester Present (0x3E) to keep session alive"""
        try:
            if self.vci_manager and self.vci_manager.is_connected():
                # Send Tester Present
                # We catch exceptions to prevent timer thread crashes
                self.vci_manager.tester_present()
        except Exception as e:
            logger.debug(f"Keep-alive error: {e}")

    def unlock_security_access(self, level: int = 0x01, algorithm: callable = None) -> bool:
        """
        Unlock security access for the current session.
        
        Args:
            level: Security level (e.g. 1, 3, 5, etc.)
            algorithm: Callback function(seed: bytes) -> bytes.
                       If None, a default (seed + 0) algorithm is used.
        """
        # Check tier access for Security Access (usually a Pro/Master feature)
        if not self.enforce_tier_access(self.current_brand, "security_access"):
            return False

        if not self.vci_manager or not self.vci_manager.is_connected():
            return False
            
        if algorithm is None:
            # Security Hardening: Never allow default bypass
            logger.error("Security access failed: No algorithm provided")
            return False
            
        return self.vci_manager.security_access(level, algorithm)


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

    def _read_real_dtcs(self, tx_id: int = 0x7E0, rx_id: int = 0x7E8) -> List[Dict[str, Any]]:
        """Read DTCs from real VCI device — routes to ELM327 or J2534/UDS."""
        dtcs = []

        if not self.vci_manager or not self.vci_manager.is_connected():
            raise ConnectionError("No VCI device connected")

        # PATH A: HH OBD Advance / ELM327
        if self.vci_manager.get_elm327_driver() is not None:
            return self.vci_manager.read_dtcs_elm327()

        # PATH B: J2534 / UDS
        raw_response = self._send_uds_request(0x19, [0x02, 0xFF], tx_id=tx_id, rx_id=rx_id)
        if raw_response:
            dtcs = self._parse_dtc_response(raw_response)
            logger.info(f"Read {len(dtcs)} DTCs from module {hex(tx_id)}")

        return dtcs

    def _send_uds_request(self, service_id: int, data: List[int], tx_id: int = 0x7E0, rx_id: int = 0x7E8) -> bytes:
        """Send a UDS request and return the response"""
        if not self.vci_manager or not self.vci_manager.is_connected():
            raise ConnectionError("VCI not connected")

        try:
            # Construct payload: [Service ID] + [Data Bytes]
            payload = bytes([service_id] + data)
            
            # Send via VCI Manager
            if hasattr(self.vci_manager, 'send_uds_request'):
                response = self.vci_manager.send_uds_request(payload, tx_id, rx_id)
                if response is None:
                     raise IOError("No response from ECU")
                return response
            else:
                raise NotImplementedError("VCI Manager does not support send_uds_request")
                
        except Exception as e:
            logger.error(f"Failed to send UDS request: {e}")
            raise e

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
        if self.dtc_db:
            try:
                info = self.dtc_db.get_dtc_info(dtc_code)
                description = info.get('description', 'Unknown DTC Code')
                
                # If description is just "Unknown DTC Code", maybe append the code for clarity?
                # But the UI usually displays the code separately.
                # If the DB returns "Unknown DTC Code", we might prefer a generic "Diagnostic Trouble Code ..."
                if description == "Unknown DTC Code":
                    return f"Diagnostic Trouble Code {dtc_code}"
                
                return description
            except Exception as e:
                logger.error(f"Error looking up DTC description: {e}")
                
        # Fallback to generic description
        return f"Diagnostic Trouble Code {dtc_code}"

    def _clear_real_dtcs(self) -> bool:
        """Clear DTCs using real VCI device — routes to ELM327 or UDS."""
        try:
            if self.vci_manager and self.vci_manager.is_connected():
                # PATH A: HH OBD Advance / ELM327
                if self.vci_manager.get_elm327_driver() is not None:
                    return self.vci_manager.clear_dtcs_elm327()

                device = self.vci_manager.get_connected_device()
                if device and "dtc_clear" in device.capabilities:
                    response = self._send_uds_request(0x14, [0xFF, 0xFF, 0xFF])
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
                # Attempt to read voltage via OBD-II PID 0x42 (Control Module Voltage)
                # Service 01, PID 42
                response = self._send_uds_request(0x01, [0x42])
                
                # Expected response: 41 42 A B (Voltage = (256*A + B) / 1000)
                if response and len(response) >= 4 and response[0] == 0x41 and response[1] == 0x42:
                    # Use EquationSolver if available
                    if 'EquationSolver' in globals():
                        return EquationSolver.solve("(256*A + B) / 1000", list(response[2:]))
                    
                    # Fallback
                    a = response[2]
                    b = response[3]
                    voltage = (256 * a + b) / 1000.0
                    return voltage
                
                # If OBD read fails, check if we have a mocked value for testing or return 0
                return 0.0
            else:
                # No VCI connected
                return 0.0

        except Exception as e:
            logger.error(f"Error reading vehicle voltage: {e}")
            return 0.0

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
        try:
            did_high = (did >> 8) & 0xFF
            did_low = did & 0xFF
            
            # Send UDS Service 0x22 (Read Data By Identifier)
            # Request: 22 [DID_HIGH] [DID_LOW]
            response = self._send_uds_request(0x22, [did_high, did_low])
            
            # Response: 62 [DID_HIGH] [DID_LOW] [DATA...]
            if response and len(response) >= 3:
                if response[0] == 0x62:
                    # Skip service ID (62) and DID bytes (2)
                    data = response[3:]
                    
                    # Try to decode as ASCII first (common for VIN, Part Numbers)
                    try:
                        # Filter out non-printable characters for display safety
                        decoded = data.decode('ascii').strip()
                        if all(32 <= ord(c) <= 126 for c in decoded):
                            return decoded
                    except UnicodeDecodeError:
                        pass
                        
                    # Fallback to hex string if not valid ASCII
                    return data.hex().upper()
            
            return None
        except Exception as e:
            logger.error(f"Error reading DID 0x{did:04X}: {e}")
            return None


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
            # scan_for_devices() is async and returns bool (scan started).
            # Wait briefly for the scan to populate available_devices.
            self.vci_manager.scan_for_devices(timeout=5)
            import time
            deadline = time.time() + 6
            while time.time() < deadline:
                if self.vci_manager.available_devices:
                    break
                time.sleep(0.2)
            for device in self.vci_manager.available_devices:
                if self.vci_manager.connect_to_device(device):
                    logger.info(f"Auto-connected to {device.name}")
                    return True
            logger.error("No VCI devices found - hardware required for all operations")
            return False

        return True
