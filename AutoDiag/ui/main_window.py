# AutoDiag/ui/main_window.py
# AutoDiag Pro - Main Window Implementation
# Date: December 20, 2025

#!/usr/bin/env python3

import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout, QWidget, QFrame,
    QLabel, QComboBox, QHBoxLayout, QMessageBox, QPushButton
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# Local imports
from AutoDiag.ui.dashboard_tab import DashboardTab
from AutoDiag.ui.diagnostics_tab import DiagnosticsTab
from AutoDiag.ui.live_data_tab import LiveDataTab
from AutoDiag.ui.special_functions_tab import SpecialFunctionsTab
from AutoDiag.ui.calibrations_tab import CalibrationsTab
from AutoDiag.ui.advanced_tab import AdvancedTab
from AutoDiag.ui.security_tab import SecurityTab
from AutoDiag.ui.can_bus_tab import CANBusDataTab
from AutoDiag.ui.tier_gate_widget import TierGateWidget
from AutoDiag.core.diagnostics import DiagnosticsController
from ai.agent import CharlemaineAgent

logger = logging.getLogger(__name__)

# Brand database
try:
    from shared.brand_database import get_brand_list
    BRAND_DATABASE_AVAILABLE = True
except ImportError:
    logger.error("Brand database not available - hardware required")
    BRAND_DATABASE_AVAILABLE = False

class ResponsiveHeader(QFrame):
    """Responsive header with brand selector and user info"""
    def __init__(self, parent=None, user_info=None):
        super().__init__(parent)
        self.setProperty("class", "glass-card")
        self.setMinimumHeight(120)
        self.setMaximumHeight(140)

        if not user_info:
            raise ValueError("ResponsiveHeader requires authenticated user_info")
        self.user_info = user_info

        layout = QHBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 15)
        layout.setSpacing(20)

        # Logo / Title
        title = QLabel("AutoDiag Pro")
        title.setProperty("class", "header-title")
        title_font = QFont("Segoe UI", 20, QFont.Weight.Bold)
        title.setFont(title_font)
        layout.addWidget(title)

        # User info
        user_label = QLabel(f"👤 {self.user_info['full_name']} ({self.user_info['tier']})")
        user_label.setProperty("class", "header-text")
        layout.addWidget(user_label, alignment=Qt.AlignmentFlag.AlignRight)

        # Brand selector
        brand_label = QLabel("Vehicle Brand:")
        brand_label.setProperty("class", "header-text")
        layout.addWidget(brand_label)

        self.brand_combo = QComboBox()
        self.brand_combo.setProperty("class", "combo-glass")
        self.brand_combo.setMinimumWidth(200)
        
        # Load brands from actual database
        brands = self._load_brands_from_database()
        if brands:
            self.brand_combo.addItems(sorted(brands))
        else:
            # Fallback - should not happen as hardware/database required
            logger.error("No brands loaded from database - hardware/database required")
            self.brand_combo.addItems(["HARDWARE REQUIRED"])
        
        self.brand_combo.currentTextChanged.connect(parent.update_brand if parent else lambda x: None)
        layout.addWidget(self.brand_combo)

        # Legacy/About button
        self.legacy_btn = self.create_legacy_button()
        layout.addWidget(self.legacy_btn)

        layout.addStretch()

    def create_legacy_button(self):
        """Create legacy/about button"""
        legacy_btn = QPushButton("📜 Legacy")
        legacy_btn.setProperty("class", "info")
        legacy_btn.setMinimumHeight(45)
        legacy_btn.setMaximumWidth(120)
        legacy_btn.setToolTip("About DACOS & Legacy")
        legacy_btn.clicked.connect(self.show_legacy_dialog)
        return legacy_btn

    def show_legacy_dialog(self):
        """Show the Legacy/About dialog with the core philosophy"""
        title = "The Road, the Stage, and the Canvas"
        text = (
            "DACOS - Diagnostic Auto Clinic OS\n"
            "Version: 3.1.2 (Professional Teal)\n\n"
            "\"The road stretches endlessly, a symbol of life's journey... "
            "But beneath this restless movement lies a fundamental question... "
            "What remains when movement stops?\"\n\n"
            "Dedicated to the silence beneath all things.\n"
            "Author: Shaun Smit\n\n"
            "\"We can share it and stare it in the face.\"\n"
            "Making our noise last longer."
        )
        QMessageBox.information(self, title, text)


class AutoDiagPro(QMainWindow):
    """Main application window"""
    def __init__(self, current_user_info=None, vci_manager=None, parent=None):
        super().__init__(parent)
        self.user_info = current_user_info or {}
        self.vci_manager = vci_manager
        self.current_brand = "Toyota"

        self.setWindowTitle("AutoDiag Pro - Professional Diagnostic Suite v3.1.2")
        self.setMinimumSize(1200, 800)
        self.showMaximized()

        self.setup_ui()
        self.setup_tabs()
        self.start_timers()

        # Initialize Core Components
        try:
            self.charlemaine = CharlemaineAgent()
            self.diagnostics_controller = DiagnosticsController(charlemaine_agent=self.charlemaine)
            
            # Connect VCI status signals
            self.diagnostics_controller.vci_status_changed.connect(self.on_vci_status_changed)

            # Connect async diagnostic result signals
            self.diagnostics_controller.scan_completed.connect(self._on_scan_completed)
            self.diagnostics_controller.dtc_read.connect(self._on_dtc_read)
            self.diagnostics_controller.dtc_cleared.connect(self._on_dtc_cleared)
            self.diagnostics_controller.pending_dtc_read.connect(self._on_pending_dtc_read)
            self.diagnostics_controller.freeze_frame_read.connect(self._on_freeze_frame_read)
            self.diagnostics_controller.readiness_read.connect(self._on_readiness_read)

            logger.info("Core components (Charlemaine, DiagnosticsController) initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize core components: {e}")
            self.diagnostics_controller = None

        logger.info(f"Main window initialized for user: {self.user_info.get('username', 'unknown')}")

    def setup_ui(self):
        """Setup main layout and header"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        self.header = ResponsiveHeader(parent=self, user_info=self.user_info)
        main_layout.addWidget(self.header)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setProperty("class", "tab-widget")
        main_layout.addWidget(self.tab_widget)

        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setProperty("class", "status-text")
        self.statusBar().addWidget(self.status_label)

    def _get_user_tier(self):
        """Map the logged-in user's SecurityLevel to a subscription Tier enum."""
        try:
            from shared.tier_system import Tier
            mapping = {
                'BASIC':    Tier.FREE,
                'STANDARD': Tier.BASIC,
                'ADVANCED': Tier.INTERMEDIATE,
                'DEALER':   Tier.PROFESSIONAL,
                'FACTORY':  Tier.ADVANCED,
                'SUPER':    Tier.SUPERUSER,
            }
            level_name = self.user_info.get('security_level', 'BASIC')
            return mapping.get(level_name, Tier.FREE)
        except ImportError:
            return None

    def _add_tab(self, key, tab_obj_or_widget, title, required_tier, user_tier, create_kwargs=None):
        """
        Add a tab to the tab widget, gating it behind TierGateWidget if the user's
        tier is insufficient. Locked tabs are visible (hidden tabs don't convert).
        """
        from shared.tier_system import Tier

        # SUPERUSER and None (tier system unavailable) bypass all gates
        is_unlocked = (
            user_tier is None
            or user_tier == Tier.SUPERUSER
            or user_tier.value >= required_tier.value
        )

        if is_unlocked:
            if callable(tab_obj_or_widget):
                # It's a factory callable — build the real tab
                tab_obj = tab_obj_or_widget()
                if create_kwargs:
                    result = tab_obj.create_tab(**create_kwargs)
                else:
                    result = tab_obj.create_tab()
                widget = result[0] if isinstance(result, tuple) else result
                display_title = result[1] if isinstance(result, tuple) else title
                self.tabs[key] = tab_obj
            else:
                widget = tab_obj_or_widget
                display_title = title
                self.tabs[key] = widget
        else:
            widget = TierGateWidget(required_tier, user_tier, title)
            display_title = f"🔒 {title}"
            self.tabs[key] = widget

        self.tab_widget.addTab(widget, display_title)

    def setup_tabs(self):
        """Initialize and add all tabs, gated by the user's subscription tier."""
        from shared.tier_system import Tier
        self.tabs = {}
        user_tier = self._get_user_tier()

        # --- FREE tier (always open) ---
        self._add_tab('dashboard',   lambda: DashboardTab(self),   "🏠 Dashboard",   Tier.FREE, user_tier)
        self._add_tab('live_data',   lambda: LiveDataTab(self),    "📊 Live Data",   Tier.FREE, user_tier)

        # Diagnostics tab returns a plain widget, not a tuple — handle directly
        diagnostics_tab = DiagnosticsTab(self)
        diag_widget = diagnostics_tab.create_tab()
        self.tab_widget.addTab(diag_widget, "🔧 Diagnostics")
        self.tabs['diagnostics'] = diagnostics_tab

        # --- BASIC tier (R249/mo) ---
        self._add_tab('special',       lambda: SpecialFunctionsTab(self), "⚡ Special Functions", Tier.BASIC,        user_tier)

        # --- INTERMEDIATE tier (R599/mo) ---
        self._add_tab('calibrations',  lambda: CalibrationsTab(self),    "🔩 Calibrations",     Tier.INTERMEDIATE, user_tier)

        # --- PROFESSIONAL tier (R1299/mo) ---
        self._add_tab('advanced',      lambda: AdvancedTab(self),        "🧠 Advanced",          Tier.PROFESSIONAL, user_tier)

        # --- ADVANCED tier (R2499/mo) ---
        self._add_tab('can_bus',       lambda: CANBusDataTab(self),      "📡 CAN Bus",           Tier.ADVANCED,     user_tier,
                      create_kwargs={'app': self})

        # --- Security (always open — account management) ---
        self._add_tab('security',      lambda: SecurityTab(self),        "🔐 Security",          Tier.FREE, user_tier)

    def start_timers(self):
        """Start any periodic updates"""
        # Example: periodic status update
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Every 5 seconds

    def update_status(self):
        """Update status bar periodically"""
        current_tab = self.tab_widget.tabText(self.tab_widget.currentIndex())
        self.status_label.setText(f"Ready | Brand: {self.current_brand} | Tab: {current_tab}")

    def update_brand(self, brand: str):
        """Called when brand is changed in header"""
        if brand:
            self.current_brand = brand
            self.status_label.setText(f"Brand changed to: {brand}")
            logger.info(f"Vehicle brand selected: {brand}")

            # Notify tabs that might need brand update
            for tab in self.tabs.values():
                if hasattr(tab, 'update_brand'):
                    try:
                        tab.update_brand(brand)
                    except:
                        pass

    # Quick action proxies (connected from dashboard)
    def run_quick_scan(self):
        self.tab_widget.setCurrentIndex(1)  # Diagnostics tab
        if 'diagnostics' in self.tabs:
            self.tabs['diagnostics'].quick_scan()

    def read_dtcs(self):
        self.tab_widget.setCurrentIndex(1)
        if 'diagnostics' in self.tabs:
            self.tabs['diagnostics'].read_dtcs()

    def show_live_data(self):
        self.tab_widget.setCurrentIndex(2)  # Live Data tab index

    def show_ecu_info(self):
        QMessageBox.information(self, "ECU Info", "ECU Information feature coming soon.")

    # Live stream proxies
    def start_live_stream(self):
        from shared.live_data import start_live_stream
        start_live_stream()

    def stop_live_stream(self):
        from shared.live_data import stop_live_stream
        stop_live_stream()

    def on_vci_status_changed(self, status_info):
        """Handle VCI status updates from controller"""
        # Update diagnostics tab
        if 'diagnostics' in self.tabs:
            self.tabs['diagnostics'].update_vci_status_display(status_info)
        
        # Update header/status bar if needed
        status = status_info.get('status', 'unknown')
        if status == 'connected':
            device = status_info.get('device', {})
            self.status_label.setText(f"VCI Connected: {device.get('name', 'Unknown Device')} | Brand: {self.current_brand}")
        else:
            self.status_label.setText(f"VCI: {status} | Brand: {self.current_brand}")

    def run_full_scan(self):
        """Execute full system scan via controller (async — results arrive via scan_completed signal)"""
        if not self.diagnostics_controller:
            QMessageBox.critical(self, "Error", "Diagnostics Controller not initialized")
            return

        vci_status = self.diagnostics_controller.get_vci_status()
        if vci_status.get('status') != 'connected':
            QMessageBox.warning(self, "VCI Not Connected", "Please connect a VCI device in the VCI Connection tab first.")
            return

        self.status_label.setText("Running Full System Scan...")
        if 'diagnostics' in self.tabs:
            self.tabs['diagnostics'].results_text.append(
                f"\n[{datetime.now().strftime('%H:%M:%S')}] Full System Scan started for {self.current_brand}..."
            )

        try:
            self.diagnostics_controller.run_full_scan(self.current_brand)
        except Exception as e:
            logger.error(f"Scan start failed: {e}")
            if 'diagnostics' in self.tabs:
                self.tabs['diagnostics'].results_text.append(f"❌ Failed to start scan: {e}")
            self.status_label.setText(f"Ready | Brand: {self.current_brand}")

    def _on_scan_completed(self, results: dict):
        """Handle scan_completed signal from DiagnosticsController worker"""
        self.status_label.setText(f"Ready | Brand: {self.current_brand}")
        if 'diagnostics' not in self.tabs:
            return

        tab = self.tabs['diagnostics']
        if results.get('error'):
            tab.results_text.append(f"❌ Scan error: {results['error']}")
            return

        modules = results.get('modules', [])
        dtcs = results.get('dtcs', [])
        output = f"\n✅ Scan completed — {len(modules)} modules, {len(dtcs)} total DTCs\n"

        for module in modules:
            output += f"  [{module.get('name', '?')}] {module.get('status', '?')}\n"
            for dtc in module.get('dtcs', []):
                output += f"    ⚠️ {dtc.get('code')}: {dtc.get('description')}\n"

        if results.get('ai_fault_prediction'):
            ai = results['ai_fault_prediction'].get('ai_analysis', {})
            score = ai.get('health_score', 0.0)
            output += f"\n🧠 AI Health Score: {int(score * 100)}/100\n"
            for p in ai.get('fault_predictions', []):
                output += f"  ⚠️ {p['type'].upper()}: {p['description']} ({int(p['confidence']*100)}%)\n"

        tab.results_text.append(output)

    def _on_dtc_read(self, dtc_data: dict):
        """Handle dtc_read signal"""
        self.status_label.setText(f"Ready | Brand: {self.current_brand}")
        if 'diagnostics' not in self.tabs:
            return
        dtcs = dtc_data.get('dtcs', [])
        if not dtcs:
            self.tabs['diagnostics'].results_text.append("✅ No DTCs found")
        else:
            output = f"\nFound {len(dtcs)} DTC(s):\n"
            for dtc in dtcs:
                output += f"  {dtc.get('code')}: {dtc.get('description')} [{dtc.get('status')}]\n"
            self.tabs['diagnostics'].results_text.append(output)

    def _on_dtc_cleared(self, success: bool):
        """Handle dtc_cleared signal"""
        self.status_label.setText(f"Ready | Brand: {self.current_brand}")
        if 'diagnostics' in self.tabs:
            if success:
                self.tabs['diagnostics'].results_text.append("✅ DTCs cleared. Cycle ignition to confirm.")
            else:
                self.tabs['diagnostics'].results_text.append("❌ DTC clear failed.")

    def _on_pending_dtc_read(self, data: dict):
        """Handle pending_dtc_read signal."""
        self.status_label.setText(f"Ready | Brand: {self.current_brand}")
        if 'diagnostics' not in self.tabs:
            return
        text = self.diagnostics_controller._format_pending_dtc_results(data)
        self.tabs['diagnostics'].results_text.append(f"\n{text}")

    def _on_freeze_frame_read(self, data: dict):
        """Handle freeze_frame_read signal."""
        self.status_label.setText(f"Ready | Brand: {self.current_brand}")
        if 'diagnostics' not in self.tabs:
            return
        text = self.diagnostics_controller._format_freeze_frame(data)
        self.tabs['diagnostics'].results_text.append(f"\n{text}")

    def _on_readiness_read(self, data: dict):
        """Handle readiness_read signal."""
        self.status_label.setText(f"Ready | Brand: {self.current_brand}")
        if 'diagnostics' not in self.tabs:
            return
        text = self.diagnostics_controller._format_readiness_monitors(data)
        self.tabs['diagnostics'].results_text.append(f"\n{text}")

    def read_pending_dtcs(self):
        """Read pending DTCs via controller."""
        if not self.diagnostics_controller:
            return
        if 'diagnostics' in self.tabs:
            self.tabs['diagnostics'].results_text.append(
                f"\n[{datetime.now().strftime('%H:%M:%S')}] Reading pending DTCs..."
            )
        self.status_label.setText("Reading pending DTCs...")
        try:
            self.diagnostics_controller.read_pending_dtcs(self.current_brand)
        except Exception as e:
            logger.error(f"Read pending DTCs failed: {e}")
            if 'diagnostics' in self.tabs:
                self.tabs['diagnostics'].results_text.append(f"❌ Error: {e}")

    def read_freeze_frame(self):
        """Read freeze frame via controller."""
        if not self.diagnostics_controller:
            return
        if 'diagnostics' in self.tabs:
            self.tabs['diagnostics'].results_text.append(
                f"\n[{datetime.now().strftime('%H:%M:%S')}] Reading freeze frame..."
            )
        self.status_label.setText("Reading freeze frame...")
        try:
            self.diagnostics_controller.read_freeze_frame(self.current_brand)
        except Exception as e:
            logger.error(f"Read freeze frame failed: {e}")
            if 'diagnostics' in self.tabs:
                self.tabs['diagnostics'].results_text.append(f"❌ Error: {e}")

    def read_readiness_monitors(self):
        """Read readiness monitors via controller."""
        if not self.diagnostics_controller:
            return
        if 'diagnostics' in self.tabs:
            self.tabs['diagnostics'].results_text.append(
                f"\n[{datetime.now().strftime('%H:%M:%S')}] Reading readiness monitors..."
            )
        self.status_label.setText("Reading readiness monitors...")
        try:
            self.diagnostics_controller.read_readiness_monitors(self.current_brand)
        except Exception as e:
            logger.error(f"Read readiness monitors failed: {e}")
            if 'diagnostics' in self.tabs:
                self.tabs['diagnostics'].results_text.append(f"❌ Error: {e}")

    def read_dtcs(self):
        """Read DTCs via controller (async — results arrive via dtc_read signal)"""
        if not self.diagnostics_controller:
            return

        if 'diagnostics' in self.tabs:
            self.tabs['diagnostics'].results_text.append(
                f"\n[{datetime.now().strftime('%H:%M:%S')}] Reading DTCs..."
            )
        self.status_label.setText("Reading DTCs...")

        try:
            self.diagnostics_controller.read_dtcs()
        except Exception as e:
            logger.error(f"Read DTCs failed: {e}")
            if 'diagnostics' in self.tabs:
                self.tabs['diagnostics'].results_text.append(f"❌ Read DTCs error: {e}")

    def clear_dtcs(self):
        """Clear DTCs via controller"""
        if not self.diagnostics_controller:
            return

        reply = QMessageBox.question(
            self, "Clear DTCs",
            "Are you sure you want to clear all diagnostic trouble codes?\nThis will reset engine check lights.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        if 'diagnostics' in self.tabs:
            self.tabs['diagnostics'].results_text.append(
                f"\n[{datetime.now().strftime('%H:%M:%S')}] Clearing DTCs..."
            )
        self.status_label.setText("Clearing DTCs...")

        try:
            self.diagnostics_controller.clear_dtcs()
        except Exception as e:
            logger.error(f"Clear DTCs failed: {e}")
            if 'diagnostics' in self.tabs:
                self.tabs['diagnostics'].results_text.append(f"❌ Clear DTCs error: {e}")

        except Exception as e:
            logger.error(f"Clear DTCs failed: {e}")

    def closeEvent(self, event):
        """Handle window close"""
        reply = QMessageBox.question(
            self, "Exit", "Are you sure you want to exit AutoDiag Pro?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Stop any running diagnostic workers before exit
            if self.diagnostics_controller:
                for attr in ('_scan_worker', '_dtc_worker', '_clear_worker'):
                    worker = getattr(self.diagnostics_controller, attr, None)
                    if worker and worker.isRunning():
                        worker.quit()
                        worker.wait(2000)
            logger.info("Application closing - goodbye!")
            event.accept()
        else:
            event.ignore()
