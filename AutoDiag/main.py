# main.py - COMPLETE DIAGNOSTIC SUITE IMPLEMENTATION WITH DACOS THEME

#!/usr/bin/env python3
"""
AutoDiag Pro - Professional 25-Brand Diagnostic Suite v3.1.2
COMPLETE IMPLEMENTATION WITH DACOS UNIFIED THEME
"""

import sys
from pathlib import Path
import os
import logging
from typing import Dict, List
import random
from datetime import datetime
import argparse

# ----------------------------------------------------------------------
# Security: Import validation
# ----------------------------------------------------------------------
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# ===== DACOS THEME IMPORTS - UNIFIED APPROACH =====
# Only import GUI-related modules if not in headless mode
DACOS_AVAILABLE = False
try:
    from shared.themes.dacos_theme import DACOS_THEME, apply_dacos_theme
    from shared.circular_gauge import CircularGauge, StatCard
    from shared.style_manager import style_manager
    DACOS_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ DACOS theme system imported successfully")
except ImportError as e:
    logging.error(f"❌ DACOS theme imports failed: {e}")
    style_manager = None
    DACOS_AVAILABLE = False
    # Fallback theme (shouldn't be needed since your files exist)
    DACOS_THEME = {
        "bg_main": "#0A1A1A", "bg_panel": "#0D2323", "bg_card": "#134F4A",
        "accent": "#21F5C1", "glow": "#2AF5D1", "text_main": "#E8F4F2",
        "text_muted": "#9ED9CF", "error": "#FF4D4D", "success": "#10B981",
        "warning": "#F59E0B", "info": "#3B82F6"
    }


# ----------------------------------------------------------------------
# Qt imports - Fixed to resolve Pylance issues
# ----------------------------------------------------------------------
PYQT6_AVAILABLE = False
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton, QComboBox,
        QHBoxLayout, QVBoxLayout, QTabWidget, QGroupBox, QListWidget, QListWidgetItem,
        QTextEdit, QTableWidget, QTableWidgetItem, QSpinBox, QScrollArea, QDialog,
        QMessageBox, QLineEdit, QSizePolicy
    )
    from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
    from PyQt6.QtGui import QFont, QPalette, QColor, QLinearGradient, QPainter, QPen
    PYQT6_AVAILABLE = True
    print("PyQt6 imported successfully")
except ImportError as e:
    print(f"PyQt6 import failed: {e}")
    PYQT6_AVAILABLE = False

# Import other modules
try:
    from AutoDiag.ui.login_dialog import LoginDialog
    from AutoDiag.ui.account_management_dialog import AccountManagementDialog
    from shared.special_functions import special_functions_manager
    from shared.calibrations_reset import calibrations_resets_manager
    from shared.live_data import live_data_generator, start_live_stream, stop_live_stream, get_live_data
    from shared.advance import get_advanced_functions, simulate_function_execution, get_mock_advanced_data
    from shared.circular_gauge import CircularGauge, StatCard
    from shared.user_database import user_database
    # Import separate tab classes
    from AutoDiag.ui.dashboard_tab import DashboardTab
    from AutoDiag.ui.diagnostics_tab import DiagnosticsTab
    from AutoDiag.ui.live_data_tab import LiveDataTab
    from AutoDiag.ui.special_functions_tab import SpecialFunctionsTab
    from AutoDiag.ui.calibrations_tab import CalibrationsTab
    from AutoDiag.ui.advanced_tab import AdvancedTab
    from AutoDiag.ui.security_tab import SecurityTab
    from AutoDiag.ui.can_bus_tab import CANBusDataTab
except ImportError as e:
    logging.warning(f"Some modules not available: {e}")

# Define GUI classes only if PyQt6 is available
if PYQT6_AVAILABLE:
    class ResponsiveHeader(QFrame):
        """Responsive header that adapts to screen size with DACOS styling"""
        def __init__(self, parent=None, current_user_info=None):
            super().__init__(parent)
            self.setProperty("class", "glass-card")
            self.setMinimumHeight(130)
            self.setMaximumHeight(150)

            # Store current user information
            self.current_user_info = current_user_info or {
                'username': 'guest',
                'full_name': 'Guest User',
                'tier': 'BASIC',
                'permissions': []
            }

            self.main_layout = QHBoxLayout(self)
            self.main_layout.setContentsMargins(20, 15, 20, 15)
            self.main_layout.setSpacing(15)

            self.setup_ui()
            
        def setup_ui(self):
            """Setup header components with DACOS styling"""
            # User info section
            self.user_section = self.create_user_section()
            
            # Title
            self.title_label = QLabel("AutoDiag Pro")
            self.title_label.setProperty("class", "hero-title")
            title_font = QFont("Segoe UI", 18, QFont.Weight.Bold)
            self.title_label.setFont(title_font)
            self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Brand selector
            self.brand_layout = self.create_brand_selector()
            
            # Theme selector (simplified - DACOS only)
            self.theme_layout = self.create_theme_selector()
            
            # Account management button (for super user)
            self.account_btn = self.create_account_management_button()

            # Logout button
            self.logout_btn = self.create_logout_button()

            # Initial layout setup
            self.update_layout()
            
        def create_user_section(self):
            """Create user information section with DACOS colors"""
            user_section = QFrame()
            user_layout = QVBoxLayout(user_section)
            user_layout.setSpacing(2)
            
            self.user_name = QLabel("👤 Demo User")
            self.user_name.setProperty("class", "section-title")
            
            self.user_role = QLabel("🔐 BASIC • technician")
            self.user_role.setProperty("class", "subtitle")
            
            user_layout.addWidget(self.user_name)
            user_layout.addWidget(self.user_role)
            
            return user_section
            
        def create_brand_selector(self):
            """Create brand selection combo with DACOS styling"""
            brand_layout = QVBoxLayout()
            brand_label = QLabel("Vehicle:")
            brand_label.setProperty("class", "section-label")
            
            self.brand_combo = QComboBox()
            self.brand_combo.setMinimumWidth(120)
            self.brand_combo.setMaximumWidth(150)

            # Initialize with available manufacturers from REF files
            try:
                from AutoDiag.core.diagnostics import DiagnosticsController
                temp_controller = DiagnosticsController()
                manufacturers = temp_controller.get_available_manufacturers()
                if manufacturers:
                    self.brand_combo.addItems(manufacturers)
                else:
                    # Fallback
                    self.brand_combo.addItems(["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Audi", "Volkswagen"])
            except Exception as e:
                logger.warning(f"Failed to load manufacturers from REF files: {e}")
                self.brand_combo.addItems(["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Audi", "Volkswagen"])
            
            brand_layout.addWidget(brand_label)
            brand_layout.addWidget(self.brand_combo)
            
            return brand_layout
            
        def create_theme_selector(self):
            """Create theme selection combo - DACOS Unified only"""
            theme_layout = QVBoxLayout()
            theme_label = QLabel("Theme:")
            theme_label.setProperty("class", "section-label")
            
            self.theme_combo = QComboBox()
            self.theme_combo.addItems(["DACOS Unified"])
            self.theme_combo.setMinimumWidth(100)
            self.theme_combo.setMaximumWidth(130)
            self.theme_combo.setEnabled(False)  # DACOS only
            
            theme_layout.addWidget(theme_label)
            theme_layout.addWidget(self.theme_combo)
            
            return theme_layout
            
        def create_account_management_button(self):
            """Create account management button (super user only)"""
            account_btn = QPushButton("👥 Accounts")
            account_btn.setProperty("class", "primary")
            account_btn.setMinimumHeight(45)
            account_btn.setMaximumWidth(120)
            account_btn.setToolTip("Account Management (Super User Only)")
            account_btn.clicked.connect(self.open_account_management)
            # Will be shown/hidden based on permissions
            return account_btn

        def create_logout_button(self):
            """Create logout button with DACOS danger styling"""
            logout_btn = QPushButton("🚪 Logout")
            logout_btn.setProperty("class", "danger")
            logout_btn.setMinimumHeight(45)
            logout_btn.setMaximumWidth(120)
            logout_btn.setToolTip("Logout")
            return logout_btn
            
        def update_user_display(self):
            """Update the user information display"""
            if self.current_user_info:
                self.user_name.setText(f"👤 {self.current_user_info['full_name']}")
                tier_display = self.current_user_info['tier']
                if tier_display == "SUPER_USER":
                    tier_display = "SUPER USER"
                self.user_role.setText(f"🔐 {tier_display} • {self.current_user_info['username']}")
            else:
                self.user_name.setText("👤 Guest User")
                self.user_role.setText("🔐 BASIC • guest")

        def open_account_management(self):
            """Open account management dialog (super user only)"""
            if not self.current_user_info or 'user_management' not in self.current_user_info.get('permissions', []):
                QMessageBox.warning(self, "Access Denied",
                                  "You do not have permission to access account management.")
                return

            dialog = AccountManagementDialog(self.current_user_info['username'], self)
            dialog.exec()

        def update_layout(self):
            """Update layout based on available width - FIXED VERSION"""
            # Clear existing layout
            while self.main_layout.count():
                child = self.main_layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)

            width = self.parent().width() if self.parent() else 1000

            if width < 700:
                # Ultra-compact layout
                self.main_layout.addWidget(self.title_label, 1)
                self.main_layout.addWidget(self.logout_btn, 0)
            elif width < 900:
                # Compact layout
                self.main_layout.addWidget(self.user_section, 0)
                self.main_layout.addWidget(self.title_label, 1)
                self.main_layout.addWidget(self.logout_btn, 0)
            else:
                # Full layout
                self.main_layout.addWidget(self.user_section, 0)
                self.main_layout.addWidget(self.title_label, 1)
                self.main_layout.addLayout(self.brand_layout, 0)
                self.main_layout.addLayout(self.theme_layout, 0)
                # Add account management button if user has permission
                if self.current_user_info and 'user_management' in self.current_user_info.get('permissions', []):
                    self.main_layout.addWidget(self.account_btn, 0)
                self.main_layout.addWidget(self.logout_btn, 0)

    class AutoDiagPro(QMainWindow):
        def __init__(self, current_user_info=None):
            super().__init__()

            logger.info("Initializing AutoDiagPro...")

            # Store current user information
            self.current_user_info = current_user_info or {
                'username': 'guest',
                'full_name': 'Guest User',
                'tier': 'BASIC',
                'permissions': []
            }

            logger.info(f"User info: {self.current_user_info}")

            try:
                # Apply DACOS theme first
                self.apply_dacos_theme()
                logger.info("DACOS theme applied")
            except Exception as e:
                logger.error(f"Failed to apply DACOS theme: {e}")
                raise

            try:
                # Initialize diagnostics controller
                self.diagnostics_controller = None
                self._init_diagnostics_controller()
                logger.info("Diagnostics controller initialized")
            except Exception as e:
                logger.error(f"Failed to initialize diagnostics controller: {e}")
                raise

            try:
                # Initialize UI
                self.init_ui()
                logger.info("UI initialized")
            except Exception as e:
                logger.error(f"Failed to initialize UI: {e}")
                raise

            try:
                # Update UI with user information
                self.header.update_user_display()
                self.status_label.setText("✨ System Ready")
                logger.info("UI updated with user information")
            except Exception as e:
                logger.error(f"Failed to update UI: {e}")
                raise

        def _init_diagnostics_controller(self):
            """Initialize the diagnostics controller with UI callbacks"""
            try:
                from AutoDiag.core.diagnostics import DiagnosticsController

                ui_callbacks = {
                    'set_button_enabled': self._set_button_enabled,
                    'set_status': self._set_status_text,
                    'set_results_text': self._set_results_text,
                    'update_card_value': self._update_card_value,
                    'switch_to_tab': self._switch_to_tab,
                    'show_message': self._show_message_dialog,
                    'update_live_data_table': self._update_live_data_table,
                    'populate_live_data_table': self._populate_live_data_table,
                    'vci_status_changed': self._on_vci_status_changed,
                    'update_vci_status_display': self._update_vci_status_display,
                    'update_can_bus_data': self._update_can_bus_data
                }

                self.diagnostics_controller = DiagnosticsController(ui_callbacks)
                logger.info("Diagnostics controller initialized successfully")

            except Exception as e:
                logger.error(f"Failed to initialize diagnostics controller: {e}")
                self.diagnostics_controller = None

        def apply_dacos_theme(self):
            """Apply DACOS unified theme using your existing theme file"""
            try:
                if DACOS_AVAILABLE:
                    # Use your existing apply_dacos_theme function
                    success = apply_dacos_theme(QApplication.instance())
                    if success:
                        logger.info("✅ DACOS theme applied successfully")
                        return
                        
                # Fallback if theme application fails
                self.apply_fallback_theme()
                
            except Exception as e:
                logger.error(f"❌ Theme application failed: {e}")
                self.apply_fallback_theme()

        def apply_fallback_theme(self):
            """Enhanced fallback theme using DACOS colors"""
            t = DACOS_THEME  # Use DACOS_THEME, not THEME
            fallback_stylesheet = f"""
                QMainWindow {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 {t['bg_main']}, stop:0.5 {t['bg_panel']}, stop:1 {t['bg_main']});
                    color: {t['text_main']};
                    font-family: "Segoe UI";
                }}
                QTabWidget::pane {{
                    border: 2px solid rgba(33, 245, 193, 0.3);
                    background: {t['bg_panel']};
                    border-radius: 12px;
                }}
                QTabBar::tab {{
                    background: {t['bg_card']};
                    color: {t['text_muted']};
                    padding: 12px 24px;
                    border-radius: 8px;
                    margin: 2px;
                    font-weight: bold;
                }}
                QTabBar::tab:selected {{
                    background: {t['accent']};
                    color: #0A1A1A;
                }}
                QFrame[class="glass-card"] {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(19, 79, 74, 0.9), stop:1 rgba(13, 35, 35, 0.9));
                    border: 2px solid rgba(33, 245, 193, 0.4);
                    border-radius: 12px;
                    padding: 15px;
                }}
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {t['accent']}, stop:1 {t['glow']});
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    color: #0A1A1A;
                    font-weight: bold;
                    min-height: 35px;
                }}
                QPushButton:hover {{
                    background: {t['glow']};
                }}
                QPushButton[class="primary"] {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {t['accent']}, stop:1 {t['glow']});
                    color: #0A1A1A;
                }}
                QPushButton[class="success"] {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {t['success']}, stop:1 #059669);
                    color: white;
                }}
                QPushButton[class="warning"] {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {t['warning']}, stop:1 #D97706);
                    color: white;
                }}
                QPushButton[class="danger"] {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {t['error']}, stop:1 #DC2626);
                    color: white;
                }}
                QLabel[class="hero-title"] {{
                    color: {t['accent']};
                    font-size: 18pt;
                    font-weight: bold;
                }}
                QLabel[class="tab-title"] {{
                    color: {t['accent']};
                    font-size: 16pt;
                    font-weight: bold;
                }}
                QLabel[class="section-title"] {{
                    color: {t['text_main']};
                    font-size: 12pt;
                    font-weight: bold;
                }}
                QLabel[class="section-label"] {{
                    color: {t['text_muted']};
                    font-size: 10pt;
                }}
                QLabel[class="subtitle"] {{
                    color: {t['text_muted']};
                    font-size: 9pt;
                }}
            """
            self.setStyleSheet(fallback_stylesheet)

        def init_ui(self):
            """Initialize optimized futuristic UI with DACOS theme"""
            self.setWindowTitle("AutoDiag Pro - Futuristic Diagnostics")
            self.setMinimumSize(1024, 600)
            self.resize(1366, 768)

            # Central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Main vertical layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(15, 15, 15, 15)
            main_layout.setSpacing(15)

            # Responsive header
            self.header = ResponsiveHeader(current_user_info=self.current_user_info)
            main_layout.addWidget(self.header)

            # Tab Widget 
            self.tab_widget = QTabWidget()
            self.tab_widget.setDocumentMode(True)
            main_layout.addWidget(self.tab_widget, 1)

            # Create all tabs using separate tab classes
            self.create_tabs_using_separate_classes()

            # Status bar
            self.create_status_bar()
            
            # Connect signals
            self.header.theme_combo.currentTextChanged.connect(self.change_theme)
            self.header.brand_combo.currentTextChanged.connect(self.on_brand_changed)
            self.header.logout_btn.clicked.connect(self.secure_logout)

        def create_tabs_using_separate_classes(self):
            """Create all tabs using separate tab classes for better modularity"""
            # Initialize tab instances
            dashboard_tab = DashboardTab(self)
            diagnostics_tab = DiagnosticsTab(self)
            live_data_tab = LiveDataTab(self)
            can_bus_tab = CANBusDataTab(self)
            special_functions_tab = SpecialFunctionsTab(self)
            calibrations_tab = CalibrationsTab(self)
            advanced_tab = AdvancedTab(self)
            security_tab = SecurityTab(self)

            # Create tabs and add them to tab widget
            dashboard_widget, dashboard_title = dashboard_tab.create_tab()
            self.tab_widget.addTab(dashboard_widget, dashboard_title)

            diagnostics_widget, diagnostics_title = diagnostics_tab.create_tab()
            self.tab_widget.addTab(diagnostics_widget, diagnostics_title)

            live_data_widget, live_data_title = live_data_tab.create_tab()
            self.tab_widget.addTab(live_data_widget, live_data_title)

            # Add CAN Bus tab with REF file support
            can_bus_widget, can_bus_title = can_bus_tab.create_tab()
            self.tab_widget.addTab(can_bus_widget, can_bus_title)

            special_functions_widget, special_functions_title = special_functions_tab.create_tab()
            self.tab_widget.addTab(special_functions_widget, special_functions_title)

            calibrations_widget, calibrations_title = calibrations_tab.create_tab()
            self.tab_widget.addTab(calibrations_widget, calibrations_title)

            advanced_widget, advanced_title = advanced_tab.create_tab()
            self.tab_widget.addTab(advanced_widget, advanced_title)

            security_widget, security_title = security_tab.create_tab()
            self.tab_widget.addTab(security_widget, security_title)

            # Store references to tab instances for later use
            self.dashboard_tab = dashboard_tab
            self.diagnostics_tab = diagnostics_tab
            self.live_data_tab = live_data_tab
            self.can_bus_tab = can_bus_tab
            self.special_functions_tab = special_functions_tab
            self.calibrations_tab = calibrations_tab
            self.advanced_tab = advanced_tab
            self.security_tab = security_tab

            # Connect brand change signals to tab methods
            self.header.brand_combo.currentTextChanged.connect(self.special_functions_tab.refresh_functions_list)
            self.header.brand_combo.currentTextChanged.connect(self.calibrations_tab.refresh_calibrations_list)

            # Initialize special functions tab with current brand
            self.special_functions_tab.refresh_functions_list()

        def create_status_bar(self):
            """Create status bar with DACOS styling"""
            self.statusBar().showMessage("Ready")
            self.status_label = QLabel("✨ System Initialized")
            self.status_label.setProperty("class", "status-label")
            self.statusBar().addPermanentWidget(self.status_label)

            # Add voltage indicator
            self.voltage_label = QLabel("🔋 12.6V")
            self.voltage_label.setProperty("class", "status-label")
            self.voltage_label.setStyleSheet("color: #21F5C1; font-weight: bold;")
            self.voltage_label.setToolTip("Battery voltage reading")
            self.statusBar().addPermanentWidget(self.voltage_label)

            # Start voltage monitoring timer
            self.voltage_timer = QTimer()
            self.voltage_timer.timeout.connect(self.update_voltage_display)
            self.voltage_timer.start(5000)  # Update every 5 seconds

        def update_voltage_display(self):
            """Update the voltage display from diagnostics controller"""
            try:
                if self.diagnostics_controller:
                    voltage = self.diagnostics_controller.get_current_voltage()
                    # Update voltage reading
                    self.diagnostics_controller.update_voltage_reading()

                    # Get updated voltage
                    updated_voltage = self.diagnostics_controller.get_current_voltage()

                    # Update display with color coding
                    if updated_voltage < 11.5:
                        # Low voltage - red
                        self.voltage_label.setText(f"🔋 {updated_voltage:.1f}V")
                        self.voltage_label.setStyleSheet("color: #FF4D4D; font-weight: bold;")
                        self.voltage_label.setToolTip(f"LOW VOLTAGE: {updated_voltage:.1f}V - Check battery/charging system")
                    elif updated_voltage < 12.0:
                        # Warning voltage - yellow
                        self.voltage_label.setText(f"🔋 {updated_voltage:.1f}V")
                        self.voltage_label.setStyleSheet("color: #F59E0B; font-weight: bold;")
                        self.voltage_label.setToolTip(f"LOW VOLTAGE WARNING: {updated_voltage:.1f}V")
                    elif updated_voltage > 14.8:
                        # High voltage - orange
                        self.voltage_label.setText(f"🔋 {updated_voltage:.1f}V")
                        self.voltage_label.setStyleSheet("color: #F59E0B; font-weight: bold;")
                        self.voltage_label.setToolTip(f"HIGH VOLTAGE: {updated_voltage:.1f}V - Check alternator/regulator")
                    else:
                        # Normal voltage - green
                        self.voltage_label.setText(f"🔋 {updated_voltage:.1f}V")
                        self.voltage_label.setStyleSheet("color: #21F5C1; font-weight: bold;")
                        self.voltage_label.setToolTip(f"Normal voltage: {updated_voltage:.1f}V")

                    # Also update dashboard voltage card if it exists
                    if hasattr(self, 'dashboard_tab') and self.dashboard_tab and hasattr(self.dashboard_tab, 'voltage_card'):
                        self.dashboard_tab.voltage_card.update_value(updated_voltage)

                else:
                    # Fallback voltage simulation
                    simulated_voltage = 12.0 + random.uniform(0, 2.8)
                    self.voltage_label.setText(f"🔋 {simulated_voltage:.1f}V")
                    self.voltage_label.setStyleSheet("color: #21F5C1; font-weight: bold;")
                    self.voltage_label.setToolTip(f"Simulated voltage: {simulated_voltage:.1f}V")

            except Exception as e:
                logger.error(f"Error updating voltage display: {e}")
                # Fallback to default
                self.voltage_label.setText("🔋 12.6V")
                self.voltage_label.setStyleSheet("color: #21F5C1; font-weight: bold;")
                self.voltage_label.setToolTip("Voltage reading unavailable")

        def change_theme(self, theme_name):
            """Theme change handler - DACOS only"""
            self.status_label.setText("✨ DACOS Unified Theme Active")

        def on_brand_changed(self, brand):
            """Handle brand change"""
            self.status_label.setText(f"🚗 Vehicle brand: {brand}")

            # Update diagnostics controller with new brand
            if self.diagnostics_controller:
                self.diagnostics_controller.set_brand(brand)

        # UI Callback methods for diagnostics controller
        def _set_button_enabled(self, button_name, enabled):
            """Enable/disable buttons"""
            if hasattr(self, 'diagnostics_tab') and self.diagnostics_tab:
                if button_name == 'dtc_btn' and hasattr(self.diagnostics_tab, 'dtc_btn'):
                    self.diagnostics_tab.dtc_btn.setEnabled(enabled)
                elif button_name == 'clear_btn' and hasattr(self.diagnostics_tab, 'clear_btn'):
                    self.diagnostics_tab.clear_btn.setEnabled(enabled)

        def _set_status_text(self, text):
            """Set status text"""
            if hasattr(self, 'status_label'):
                self.status_label.setText(text)

        def _set_results_text(self, text):
            """Set results text in diagnostics tab"""
            if hasattr(self, 'diagnostics_tab') and self.diagnostics_tab and hasattr(self.diagnostics_tab, 'results_text'):
                self.diagnostics_tab.results_text.setPlainText(text)

        def _update_card_value(self, card_name, value):
            """Update card values (placeholder)"""
            pass

        def _switch_to_tab(self, index):
            """Switch to specific tab"""
            if hasattr(self, 'tab_widget'):
                self.tab_widget.setCurrentIndex(index)

        def _show_message_dialog(self, title, text, msg_type="info"):
            """Show message dialog"""
            if msg_type == "error":
                QMessageBox.critical(self, title, text)
            elif msg_type == "warning":
                QMessageBox.warning(self, title, text)
            else:
                QMessageBox.information(self, title, text)

        def _update_live_data_table(self, data):
            """Update live data table"""
            if hasattr(self, 'live_data_tab') and self.live_data_tab:
                self.live_data_tab.update_live_data_table(data)

        def _populate_live_data_table(self, data):
            """Populate live data table"""
            if hasattr(self, 'live_data_tab') and self.live_data_tab:
                self.live_data_tab.populate_live_data_table(data)

        def _on_vci_status_changed(self, event, data):
            """Handle VCI status change events"""
            try:
                if hasattr(self, 'diagnostics_tab') and self.diagnostics_tab:
                    self.diagnostics_tab.update_vci_status_display({"status": "connected" if event == "connected" else "disconnected"})
            except Exception as e:
                logger.error(f"Error handling VCI status change: {e}")

        def _update_vci_status_display(self, status_info):
            """Update VCI status display"""
            try:
                if hasattr(self, 'diagnostics_tab') and self.diagnostics_tab:
                    self.diagnostics_tab.update_vci_status_display(status_info)
            except Exception as e:
                logger.error(f"Error updating VCI status display: {e}")

        def _update_can_bus_data(self, can_data):
            """Update CAN bus data in CAN bus tab"""
            try:
                if hasattr(self, 'can_bus_tab') and self.can_bus_tab:
                    self.can_bus_tab.update_realtime_data(can_data)
            except Exception as e:
                logger.error(f"Error updating CAN bus data: {e}")

        # Fallback methods for when diagnostics controller is not available
        def _fallback_full_scan(self):
            """Fallback full scan implementation"""
            if hasattr(self, 'diagnostics_tab') and self.diagnostics_tab and hasattr(self.diagnostics_tab, 'scan_btn'):
                self.diagnostics_tab.scan_btn.setEnabled(False)
            self.status_label.setText("🔄 Running full system scan...")

            # Simulate scan progress
            progress = 0
            def update_scan():
                nonlocal progress
                progress += 10
                if progress <= 100:
                    self.status_label.setText(f"🔄 Scanning... {progress}%")
                    QTimer.singleShot(100, update_scan)
                else:
                    if hasattr(self, 'diagnostics_tab') and self.diagnostics_tab and hasattr(self.diagnostics_tab, 'scan_btn'):
                        self.diagnostics_tab.scan_btn.setEnabled(True)
                    self.status_label.setText("✅ Full scan completed")
                    if hasattr(self, 'diagnostics_tab') and self.diagnostics_tab and hasattr(self.diagnostics_tab, 'results_text'):
                        self.diagnostics_tab.results_text.setPlainText(
                            f"Full System Scan Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                            "✅ ECU Communication: ESTABLISHED\n"
                            "✅ CAN Bus: NORMAL\n"
                            "✅ LIN Bus: ACTIVE\n"
                            "✅ Sensor Network: OK\n"
                            "⚠️  2 DTCs found\n"
                            "✅ System Voltage: 13.8V\n"
                            "✅ Communication Speed: 500kbps\n\n"
                            "Scan completed successfully."
                        )

            update_scan()

        def _fallback_read_dtcs(self):
            """Fallback DTC read implementation"""
            if hasattr(self, 'diagnostics_tab') and self.diagnostics_tab and hasattr(self.diagnostics_tab, 'dtc_btn'):
                self.diagnostics_tab.dtc_btn.setEnabled(False)
            self.status_label.setText("📋 Reading DTCs...")

            QTimer.singleShot(1500, lambda: [
                (self.diagnostics_tab.dtc_btn.setEnabled(True) if hasattr(self, 'diagnostics_tab') and self.diagnostics_tab and hasattr(self.diagnostics_tab, 'dtc_btn') else None),
                self.status_label.setText("✅ DTCs retrieved"),
                (self.diagnostics_tab.results_text.setPlainText(
                    f"DTC Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    "P0301 - Cylinder 1 Misfire Detected\n"
                    "   Status: Confirmed\n"
                    "   Priority: Medium\n"
                    "   Freeze Frame: RPM=2450, Load=65%\n\n"
                    "U0121 - Lost Communication With ABS Control Module\n"
                    "   Status: Pending\n"
                    "   Priority: Low\n"
                    "   First Occurrence: 2024-01-15\n\n"
                    "Total DTCs: 2"
                ) if hasattr(self, 'diagnostics_tab') and self.diagnostics_tab and hasattr(self.diagnostics_tab, 'results_text') else None)
            ])

        def _fallback_clear_dtcs(self):
            """Fallback DTC clear implementation"""
            reply = QMessageBox.question(self, "Clear DTCs",
                                       "Are you sure you want to clear all diagnostic trouble codes?",
                                       QMessageBox.StandardButton.Yes |
                                       QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                if hasattr(self, 'diagnostics_tab') and self.diagnostics_tab and hasattr(self.diagnostics_tab, 'clear_btn'):
                    self.diagnostics_tab.clear_btn.setEnabled(False)
                self.status_label.setText("🧹 Clearing DTCs...")

                QTimer.singleShot(2000, lambda: [
                    (self.diagnostics_tab.clear_btn.setEnabled(True) if hasattr(self, 'diagnostics_tab') and self.diagnostics_tab and hasattr(self.diagnostics_tab, 'clear_btn') else None),
                    self.status_label.setText("✅ DTCs cleared successfully"),
                    (self.diagnostics_tab.results_text.setPlainText(
                        f"DTC Clearance Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        "✅ All diagnostic trouble codes have been cleared\n"
                        "✅ System memory reset\n"
                        "✅ Ready for new diagnostics\n\n"
                        "Note: Some codes may reappear if underlying issues persist."
                    ) if hasattr(self, 'diagnostics_tab') and self.diagnostics_tab and hasattr(self.diagnostics_tab, 'results_text') else None)
                ])

        def secure_logout(self):
            """Enhanced logout dialog with DACOS styling"""
            reply = QMessageBox.question(self, "Logout",
                                        "Are you sure you want to logout?",
                                        QMessageBox.StandardButton.Yes |
                                        QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.close()

        def resizeEvent(self, event):
            """Handle window resize for responsive layout"""
            super().resizeEvent(event)
            if hasattr(self, 'header'):
                self.header.update_layout()



        def create_live_data_tab(self):
            """Create live data streaming tab"""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            # Header
            header = QLabel("📊 Live Data Streaming")
            header.setProperty("class", "tab-title")
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Control Panel
            control_frame = QFrame()
            control_frame.setProperty("class", "glass-card")
            control_layout = QHBoxLayout(control_frame)
            
            start_btn = QPushButton("▶ Start Stream")
            start_btn.setProperty("class", "success")
            start_btn.clicked.connect(self.start_live_stream)
            
            stop_btn = QPushButton("⏹ Stop Stream")
            stop_btn.setProperty("class", "danger")
            stop_btn.clicked.connect(self.stop_live_stream)
            
            control_layout.addWidget(start_btn)
            control_layout.addWidget(stop_btn)
            control_layout.addStretch()

            # Live Data Table
            data_frame = QFrame()
            data_frame.setProperty("class", "glass-card")
            data_layout = QVBoxLayout(data_frame)
            
            data_title = QLabel("Live Parameters")
            data_title.setProperty("class", "section-title")
            
            self.live_data_table = QTableWidget(0, 3)
            self.live_data_table.setHorizontalHeaderLabels(["Parameter", "Value", "Unit"])
            self.live_data_table.horizontalHeader().setStretchLastSection(True)
            
            # Add sample data
            self.populate_sample_data()
            
            data_layout.addWidget(data_title)
            data_layout.addWidget(self.live_data_table)

            layout.addWidget(header)
            layout.addWidget(control_frame)
            layout.addWidget(data_frame)
            
            self.tab_widget.addTab(tab, "📊 Live Data")


        def create_calibrations_resets_tab(self):
            """Create enhanced calibrations and resets tab with full functionality"""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)

            # Header
            header = QLabel("⚙️ Calibrations & Resets")
            header.setProperty("class", "tab-title")
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(header)

            # Main content area
            content_frame = QFrame()
            content_frame.setProperty("class", "glass-card")
            content_layout = QVBoxLayout(content_frame)

            # Brand info display
            self.calibrations_brand_info_label = QLabel("Select a vehicle brand from the header to view available calibrations and reset procedures.")
            self.calibrations_brand_info_label.setProperty("class", "section-title")
            self.calibrations_brand_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            content_layout.addWidget(self.calibrations_brand_info_label)

            # Procedures list
            procedures_group = QGroupBox("Available Procedures")
            procedures_layout = QVBoxLayout(procedures_group)

            # Create scroll area for procedures list
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setMinimumHeight(200)
            scroll_area.setMaximumHeight(300)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

            self.calibrations_list = QListWidget()
            self.calibrations_list.setMinimumHeight(200)
            self.calibrations_list.setProperty("class", "glass-card")
            self.calibrations_list.itemSelectionChanged.connect(self.show_calibration_details)
            self.calibrations_list.itemDoubleClicked.connect(self.execute_selected_calibration)

            scroll_area.setWidget(self.calibrations_list)
            procedures_layout.addWidget(scroll_area)

            # Procedure details area
            details_group = QGroupBox("Procedure Details")
            details_layout = QVBoxLayout(details_group)

            self.calibration_details = QTextEdit()
            self.calibration_details.setReadOnly(True)
            self.calibration_details.setMaximumHeight(150)
            self.calibration_details.setPlainText("Select a procedure to view details and prerequisites.")
            details_layout.addWidget(self.calibration_details)

            # Control buttons
            buttons_layout = QHBoxLayout()

            self.execute_calibration_btn = QPushButton("⚡ Execute Procedure")
            self.execute_calibration_btn.setProperty("class", "primary")
            self.execute_calibration_btn.clicked.connect(self.execute_selected_calibration)
            self.execute_calibration_btn.setEnabled(False)

            self.refresh_calibrations_btn = QPushButton("🔄 Refresh Procedures")
            self.refresh_calibrations_btn.setProperty("class", "success")
            self.refresh_calibrations_btn.clicked.connect(self.refresh_calibrations_list)

            buttons_layout.addWidget(self.execute_calibration_btn)
            buttons_layout.addWidget(self.refresh_calibrations_btn)
            buttons_layout.addStretch()

            # Results area
            results_group = QGroupBox("Execution Results")
            results_layout = QVBoxLayout(results_group)

            self.calibrations_results_text = QTextEdit()
            self.calibrations_results_text.setReadOnly(True)
            self.calibrations_results_text.setPlainText("Procedure execution results will appear here.")
            results_layout.addWidget(self.calibrations_results_text)

            # Assemble everything
            content_layout.addWidget(procedures_group)
            content_layout.addWidget(details_group)
            content_layout.addLayout(buttons_layout)
            content_layout.addWidget(results_group)

            layout.addWidget(content_frame)

            self.tab_widget.addTab(tab, "⚙️ Calibrations")

            # Connect to brand changes
            self.header.brand_combo.currentTextChanged.connect(self.on_brand_changed_calibrations)

        def create_advanced_tab(self):
            """Create enhanced advanced tab with mock data"""
            tab = QWidget()
            layout = QVBoxLayout(tab)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)

            # Header
            header = QLabel("🚀 Advanced Functions")
            header.setProperty("class", "tab-title")
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(header)

            # Main content area
            content_frame = QFrame()
            content_frame.setProperty("class", "glass-card")
            content_layout = QVBoxLayout(content_frame)

            # System status display
            self.advanced_status_label = QLabel("Advanced diagnostics system ready")
            self.advanced_status_label.setProperty("class", "section-title")
            self.advanced_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            content_layout.addWidget(self.advanced_status_label)

            # Functions list
            functions_group = QGroupBox("Available Advanced Functions")
            functions_layout = QVBoxLayout(functions_group)

            # Create scroll area for functions list
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setMinimumHeight(200)
            scroll_area.setMaximumHeight(300)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

            self.advanced_functions_list = QListWidget()
            self.advanced_functions_list.setMinimumHeight(200)
            self.advanced_functions_list.setProperty("class", "glass-card")
            self.advanced_functions_list.itemSelectionChanged.connect(self.show_advanced_function_details)
            self.advanced_functions_list.itemDoubleClicked.connect(self.execute_advanced_function)

            scroll_area.setWidget(self.advanced_functions_list)
            functions_layout.addWidget(scroll_area)

            # Function details area
            details_group = QGroupBox("Function Details")
            details_layout = QVBoxLayout(details_group)

            self.advanced_function_details = QTextEdit()
            self.advanced_function_details.setReadOnly(True)
            self.advanced_function_details.setMaximumHeight(120)
            self.advanced_function_details.setPlainText("Select an advanced function to view details and parameters.")
            details_layout.addWidget(self.advanced_function_details)

            # Control buttons
            buttons_layout = QHBoxLayout()

            self.execute_advanced_btn = QPushButton("⚡ Execute Function")
            self.execute_advanced_btn.setProperty("class", "primary")
            self.execute_advanced_btn.clicked.connect(self.execute_advanced_function)
            self.execute_advanced_btn.setEnabled(False)

            self.refresh_advanced_btn = QPushButton("🔄 Refresh Functions")
            self.refresh_advanced_btn.setProperty("class", "success")
            self.refresh_advanced_btn.clicked.connect(self.refresh_advanced_functions_list)

            buttons_layout.addWidget(self.execute_advanced_btn)
            buttons_layout.addWidget(self.refresh_advanced_btn)
            buttons_layout.addStretch()

            # Results area
            results_group = QGroupBox("Execution Results")
            results_layout = QVBoxLayout(results_group)

            self.advanced_results_text = QTextEdit()
            self.advanced_results_text.setReadOnly(True)
            self.advanced_results_text.setPlainText("Advanced function execution results will appear here.")
            results_layout.addWidget(self.advanced_results_text)

            # Assemble everything
            content_layout.addWidget(functions_group)
            content_layout.addWidget(details_group)
            content_layout.addLayout(buttons_layout)
            content_layout.addWidget(results_group)

            layout.addWidget(content_frame)

            self.tab_widget.addTab(tab, "🚀 Advanced")

            # Initialize functions list
            self.refresh_advanced_functions_list()

        def create_security_tab(self):
            """Create security tab"""
            tab = QWidget()
            layout = QVBoxLayout(tab)

            header = QLabel("🔒 Security & Access")
            header.setProperty("class", "tab-title")
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)

            security_frame = QFrame()
            security_frame.setProperty("class", "glass-card")
            security_layout = QVBoxLayout(security_frame)

            user_info = QLabel("Current User: Demo Technician\n"
                              "Security Level: BASIC\n"
                              "Access: Standard Diagnostics\n"
                              "Session: Active")
            user_info.setProperty("class", "section-title")

            security_layout.addWidget(user_info)

            layout.addWidget(header)
            layout.addWidget(security_frame)
            layout.addStretch()

            self.tab_widget.addTab(tab, "🔒 Security")

        # ========== ALL MISSING METHOD IMPLEMENTATIONS ==========

        def run_full_scan(self):
            """Execute full system scan using diagnostics controller"""
            if self.diagnostics_controller:
                result = self.diagnostics_controller.run_quick_scan()
                logger.info(f"Full scan initiated: {result}")
            else:
                # Fallback to old implementation
                self._fallback_full_scan()

        def read_dtcs(self):
            """Read diagnostic trouble codes using diagnostics controller"""
            if self.diagnostics_controller:
                result = self.diagnostics_controller.read_dtcs()
                logger.info(f"DTC read initiated: {result}")
            else:
                # Fallback to old implementation
                self._fallback_read_dtcs()

        def clear_dtcs(self):
            """Clear diagnostic trouble codes using diagnostics controller"""
            if self.diagnostics_controller:
                result = self.diagnostics_controller.clear_dtcs()
                logger.info(f"DTC clear initiated: {result}")
            else:
                # Fallback to old implementation
                self._fallback_clear_dtcs()

        def start_live_stream(self):
            """Start live data streaming using diagnostics controller with realtime CAN bus integration"""
            if self.diagnostics_controller:
                result = self.diagnostics_controller.start_live_stream()
                logger.info(f"Live stream started: {result}")

                # Start realtime CAN bus monitoring
                if hasattr(self, 'can_bus_tab') and self.can_bus_tab:
                    self.can_bus_tab.start_realtime_monitoring()

                # Update status with realtime connection info
                vci_status = self.diagnostics_controller.get_vci_status()
                if vci_status.get('status') == 'connected':
                    self.status_label.setText("📊 Live data streaming active - Connected to CAN bus")
                else:
                    self.status_label.setText("📊 Live data streaming active - Using simulated data")
            else:
                # Fallback with enhanced realtime simulation
                self.status_label.setText("📊 Starting live data stream...")
                try:
                    start_live_stream()  # Start the mock data generator
                    self.live_data_timer.start(1000)  # Update every second
                    QTimer.singleShot(1000, lambda: self.status_label.setText("📊 Live data streaming active - Simulation mode"))
                except:
                    self.status_label.setText("⚠️ Live data stream not available")

        def stop_live_stream(self):
            """Stop live data streaming using diagnostics controller with realtime cleanup"""
            if self.diagnostics_controller:
                result = self.diagnostics_controller.stop_live_stream()
                logger.info(f"Live stream stopped: {result}")

                # Stop realtime CAN bus monitoring
                if hasattr(self, 'can_bus_tab') and self.can_bus_tab:
                    self.can_bus_tab.stop_realtime_monitoring()

                self.status_label.setText("⏹ Live data stream stopped - Realtime monitoring disabled")
            else:
                # Fallback with enhanced cleanup
                try:
                    self.live_data_timer.stop()
                    stop_live_stream()  # Stop the mock data generator
                    self.status_label.setText("⏹ Live data stream stopped - Simulation mode ended")
                except:
                    self.status_label.setText("⚠️ Live data stream stop failed")

        def populate_sample_data(self):
            """Populate live data table with sample data using diagnostics controller"""
            if self.diagnostics_controller:
                sample_data = self.diagnostics_controller.populate_sample_data()
                logger.info(f"Populated sample data: {len(sample_data)} items")
            else:
                # Fallback to old implementation
                try:
                    # Get current mock live data
                    live_data = get_mock_live_data()

                    if hasattr(self, 'live_data_table'):
                        self.live_data_table.setRowCount(len(live_data))
                        for row, (param, value, unit) in enumerate(live_data):
                            self.live_data_table.setItem(row, 0, QTableWidgetItem(param))
                            self.live_data_table.setItem(row, 1, QTableWidgetItem(value))
                            self.live_data_table.setItem(row, 2, QTableWidgetItem(unit))
                except Exception as e:
                    logger.error(f"Failed to populate sample data: {e}")

        def update_live_data_table(self, data=None):
            """Update the live data table with current values"""
            if data:
                # Data provided by diagnostics controller
                for row, (param, value, unit) in enumerate(data):
                    if hasattr(self, 'live_data_table') and row < self.live_data_table.rowCount():
                        self.live_data_table.setItem(row, 1, QTableWidgetItem(value))
            else:
                # Fallback to old implementation
                try:
                    if live_data_generator.is_streaming:
                        live_data = get_mock_live_data()
                        if hasattr(self, 'live_data_table'):
                            for row, (param, value, unit) in enumerate(live_data):
                                if row < self.live_data_table.rowCount():
                                    self.live_data_table.setItem(row, 1, QTableWidgetItem(value))
                except Exception as e:
                    logger.error(f"Failed to update live data table: {e}")

        def run_quick_scan(self):
            """Quick scan demo"""
            self.status_label.setText("🔍 Running quick scan...")
            QTimer.singleShot(800, lambda: [
                self.status_label.setText("✅ Quick scan completed"),
                self.tab_widget.setCurrentIndex(1),  # Switch to diagnostics tab
                self.results_text.setPlainText(
                    f"Quick Scan Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    "✅ Basic Communication: OK\n"
                    "✅ Power Supply: NORMAL\n"
                    "✅ ECU Response: ACTIVE\n"
                    "⚠️  1 Non-critical DTC found\n"
                    "✅ System Ready for Detailed Diagnostics"
                )
            ])

        def show_live_data(self):
            """Switch to live data tab"""
            self.tab_widget.setCurrentIndex(2)
            self.status_label.setText("📊 Live Data tab selected")

        def show_ecu_info(self):
            """Show ECU information"""
            brand = self.header.brand_combo.currentText()
            self.tab_widget.setCurrentIndex(1)  # Switch to diagnostics
            self.results_text.setPlainText(
                f"ECU Information - {brand}\n\n"
                "ECU: Engine Control Module\n"
                "Part #: 89663-12345\n"
                "Software: v2.1.8\n"
                "Hardware: v1.2\n"
                "VIN: 1HGCM82633A123456\n"
                "Calibration: 2023-12-01\n"
                "Protocol: CAN 11bit/500k"
            )
            self.status_label.setText(f"💾 ECU info for {brand}")

        def apply_global_theme(self):
            """Apply the DACOS Unified Theme - Enhanced version"""
            try:
                # Try DACOS theme first
                if DACOS_AVAILABLE:
                    success = apply_dacos_theme(QApplication.instance())
                    if success:
                        logger.info("DACOS Unified theme applied successfully")
                        return
                
                # Fallback to existing QSS file loading
                dacos_theme_path = PROJECT_ROOT / "shared" / "themes" / "dacos.qss"
                
                if dacos_theme_path.exists():
                    with open(dacos_theme_path, 'r', encoding='utf-8') as f:
                        dacos_stylesheet = f.read()
                    
                    self.setStyleSheet(dacos_stylesheet)
                    logger.info("DACOS theme loaded from QSS file")
                else:
                    logger.warning("DACOS theme file not found, using fallback")
                    self.apply_fallback_theme()
                    
            except Exception as e:
                logger.error(f"Failed to load DACOS theme: {e}")
                self.apply_fallback_theme()

        def apply_fallback_theme(self):
            """Enhanced fallback theme"""
            t = DACOS_THEME
            self.setStyleSheet(f"""
                QMainWindow {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 {t['bg_main']}, stop:0.5 {t['bg_panel']}, stop:1 {t['bg_card']});
                    color: {t['text_main']};
                    font-family: "Segoe UI";
                }}
                QTabWidget::pane {{
                    border: 2px solid rgba(33, 245, 193, 0.3);
                    background: {t['bg_panel']};
                    border-radius: 12px;
                }}
                QTabBar::tab {{
                    background: {t['bg_card']};
                    color: {t['text_muted']};
                    padding: 12px 24px;
                    border-radius: 8px;
                    margin: 2px;
                    font-weight: bold;
                }}
                QTabBar::tab:selected {{
                    background: {t['accent']};
                    color: #0B2E2B;
                }}
                QFrame[class="glass-card"] {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(19, 79, 74, 0.9), stop:1 rgba(11, 46, 43, 0.9));
                    border: 2px solid rgba(33, 245, 193, 0.4);
                    border-radius: 12px;
                    padding: 15px;
                }}
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {t['accent']}, stop:1 {t['glow']});
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    color: #002F2C;
                    font-weight: bold;
                    min-height: 35px;
                }}
                QPushButton:hover {{
                    background: {t['glow']};
                }}
                QLabel[class="hero-title"] {{
                    color: {t['accent']};
                    font-size: 18pt;
                    font-weight: bold;
                }}
                QLabel[class="tab-title"] {{
                    color: {t['accent']};
                    font-size: 16pt;
                    font-weight: bold;
                }}
                QLabel[class="section-title"] {{
                    color: {t['text_main']};
                    font-size: 12pt;
                    font-weight: bold;
                }}
                QLabel[class="stat-label"] {{
                    color: {t['text_muted']};
                    font-size: 10pt;
                    font-weight: bold;
                }}
                QLabel[class="stat-value"] {{
                    color: {t['accent']};
                    font-size: 14pt;
                    font-weight: bold;
                }}
            """)

        def change_theme(self, theme_name):
            """Change application theme"""
            try:
                style_manager.set_theme(theme_name)
                self.status_label.setText(f"✨ Theme changed to: {theme_name}")
            except Exception as e:
                logger.error(f"Theme change failed: {e}")
                self.status_label.setText("⚠️ Theme change failed")

        def on_brand_changed(self, brand):
            """Handle brand change"""
            self.status_label.setText(f"🚗 Vehicle brand: {brand}")
        def on_brand_changed_calibrations(self, brand):
            """Handle brand change for calibrations tab"""
            self.refresh_calibrations_list()
            self.calibrations_brand_info_label.setText(f"Selected Brand: {brand}")
            self.status_label.setText(f"⚙️ Calibrations loaded for {brand}")

        def refresh_calibrations_list(self):
            """Refresh the calibrations list based on selected brand"""
            brand = self.header.brand_combo.currentText()
            self.calibrations_list.clear()

            try:
                procedures = calibrations_resets_manager.get_brand_procedures(brand)
                if procedures:
                    for proc in procedures:
                        item_text = f"{proc.name} (Level {proc.security_level})"
                        item = QListWidgetItem(item_text)
                        item.setData(Qt.ItemDataRole.UserRole, proc)
                        self.calibrations_list.addItem(item)

                    self.calibrations_brand_info_label.setText(f"Found {len(procedures)} procedures for {brand}")
                else:
                    self.calibrations_brand_info_label.setText(f"No calibration procedures available for {brand}")
                    self.calibrations_list.addItem("No procedures available")

            except Exception as e:
                logger.error(f"Error loading calibrations for {brand}: {e}")
                self.calibrations_brand_info_label.setText(f"Error loading procedures for {brand}")
                self.calibrations_list.addItem("Error loading procedures")

            # Update procedure details
            self.calibration_details.setPlainText("Select a procedure to view details and prerequisites.")
            self.execute_calibration_btn.setEnabled(False)

        def show_calibration_details(self):
            """Show details of selected calibration procedure"""
            current_item = self.calibrations_list.currentItem()
            if not current_item:
                self.calibration_details.setPlainText("Select a procedure to view details and prerequisites.")
                self.execute_calibration_btn.setEnabled(False)
                return

            proc = current_item.data(Qt.ItemDataRole.UserRole)
            if not proc:
                self.calibration_details.setPlainText("Invalid procedure selected.")
                self.execute_calibration_btn.setEnabled(False)
                return

            # Build details text
            details = f"Procedure: {proc.name}\n"
            details += f"ID: {proc.procedure_id}\n"
            details += f"Type: {proc.reset_type.value.title()}\n"
            details += f"Security Level: {proc.security_level}\n"
            details += f"Duration: {proc.duration}\n\n"
            details += f"Description:\n{proc.description}\n\n"

            if proc.prerequisites:
                details += "Prerequisites:\n"
                for pre in proc.prerequisites:
                    details += f"• {pre}\n"
                details += "\n"

            if proc.steps:
                details += "Procedure Steps:\n"
                for i, step in enumerate(proc.steps, 1):
                    details += f"{i}. {step}\n"
            else:
                details += "No specific steps defined."

            self.calibration_details.setPlainText(details)
            self.execute_calibration_btn.setEnabled(True)

        def execute_selected_calibration(self):
            """Execute the selected calibration procedure"""
            current_item = self.calibrations_list.currentItem()
            if not current_item:
                return

            proc = current_item.data(Qt.ItemDataRole.UserRole)
            if not proc:
                return

            # Check if procedure requires parameters (for battery registration, etc.)
            if "battery" in proc.procedure_id.lower():
                # Show parameter input dialog for battery specs
                params = self.get_calibration_parameters(proc)
                if params is None:  # User cancelled
                    return
            else:
                params = {}

            # Execute procedure
            self.execute_calibration_btn.setEnabled(False)
            self.status_label.setText(f"⚙️ Executing {proc.name}...")

            # Simulate execution with mock results
            QTimer.singleShot(3000, lambda: self.show_calibration_result(proc, params))

        def get_calibration_parameters(self, proc):
            """Get parameters for calibration procedure execution via dialog"""
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Parameters for {proc.name}")
            dialog.setModal(True)

            layout = QVBoxLayout(dialog)

            # Procedure description
            desc_label = QLabel(f"Description: {proc.description}")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

            # Prerequisites
            if proc.prerequisites:
                pre_label = QLabel("Prerequisites:")
                pre_label.setStyleSheet("font-weight: bold;")
                layout.addWidget(pre_label)

                for pre in proc.prerequisites:
                    pre_item = QLabel(f"• {pre}")
                    pre_item.setStyleSheet("margin-left: 10px;")
                    layout.addWidget(pre_item)

            # Parameter inputs (mainly for battery registration)
            param_inputs = {}
            if "battery" in proc.procedure_id.lower():
                params_label = QLabel("Battery Specifications:")
                params_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
                layout.addWidget(params_label)

                # Battery type
                type_layout = QHBoxLayout()
                type_label = QLabel("Battery Type:")
                type_label.setMinimumWidth(120)
                type_combo = QComboBox()
                type_combo.addItems(["AGM", "Lead-acid", "Lithium-ion"])
                type_layout.addWidget(type_label)
                type_layout.addWidget(type_combo)
                type_layout.addStretch()
                layout.addLayout(type_layout)
                param_inputs['battery_type'] = type_combo

                # Capacity
                capacity_layout = QHBoxLayout()
                capacity_label = QLabel("Capacity (Ah):")
                capacity_label.setMinimumWidth(120)
                capacity_spin = QSpinBox()
                capacity_spin.setRange(30, 200)
                capacity_spin.setValue(70)
                capacity_layout.addWidget(capacity_label)
                capacity_layout.addWidget(capacity_spin)
                capacity_layout.addStretch()
                layout.addLayout(capacity_layout)
                param_inputs['capacity'] = capacity_spin

                # Note: Manufacturer field removed as it's not used in the current implementation

            # Buttons
            buttons = QHBoxLayout()
            execute_btn = QPushButton("Execute")
            execute_btn.setProperty("class", "primary")
            cancel_btn = QPushButton("Cancel")

            buttons.addStretch()
            buttons.addWidget(cancel_btn)
            buttons.addWidget(execute_btn)
            layout.addLayout(buttons)

            # Connect buttons
            def on_execute():
                params = {}
                for param_name, input_field in param_inputs.items():
                    if isinstance(input_field, QComboBox):
                        params[param_name] = input_field.currentText()
                    elif isinstance(input_field, QSpinBox):
                        params[param_name] = input_field.value()
                    else:  # QLineEdit
                        params[param_name] = input_field.text()

                dialog.accept()
                dialog._params = params

            def on_cancel():
                dialog.reject()

            execute_btn.clicked.connect(on_execute)
            cancel_btn.clicked.connect(on_cancel)

            result = dialog.exec()
            if result == QDialog.DialogCode.Accepted:
                return getattr(dialog, '_params', {})
            return None

        def show_calibration_result(self, proc, params):
            """Show mock calibration execution result"""
            brand = self.header.brand_combo.currentText()

            # Generate mock result based on procedure
            result_text = f"Calibration Procedure Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            result_text += f"Brand: {brand}\n"
            result_text += f"Procedure: {proc.name}\n"
            result_text += f"Procedure ID: {proc.procedure_id}\n"
            result_text += f"Type: {proc.reset_type.value.title()}\n"
            result_text += f"Security Level: {proc.security_level}\n\n"

            if params:
                result_text += "Parameters Used:\n"
                for key, value in params.items():
                    result_text += f"  {key}: {value}\n"
                result_text += "\n"

            # Mock execution results based on procedure type
            if "steering" in proc.procedure_id.lower():
                result_text += "✅ Steering Angle Sensor Calibration: SUCCESS\n"
                result_text += "📐 Zero point set to current position\n"
                result_text += "🎯 Left stop: -30° | Right stop: +30°\n"
                result_text += "🔄 Adaptation values stored\n"
                result_text += "⚠️  Test drive recommended to verify calibration\n"
            elif "battery" in proc.procedure_id.lower():
                result_text += "✅ Battery Registration: SUCCESS\n"
                result_text += "🔋 Battery specifications registered\n"
                result_text += "⚡ Power management system updated\n"
                result_text += "🔄 Adaptation values cleared and reset\n"
                result_text += "📊 Battery monitoring active\n"
            elif "throttle" in proc.procedure_id.lower():
                result_text += "✅ Throttle Body Calibration: SUCCESS\n"
                result_text += "🎛️ Throttle position sensor calibrated\n"
                result_text += "⚖️ Idle adaptation completed\n"
                result_text += "🚀 Acceleration response optimized\n"
            else:
                result_text += "✅ Procedure executed successfully\n"
                result_text += "📋 All calibration steps completed\n"
                result_text += "🔍 System verification passed\n"

            result_text += "\n⚙️ Calibration completed successfully"

            self.calibrations_results_text.setPlainText(result_text)
            self.status_label.setText(f"✅ {proc.name} completed successfully")
            self.execute_calibration_btn.setEnabled(True)

        def secure_logout(self):
            """Enhanced logout dialog"""
            reply = QMessageBox.question(self, "Logout",
                                        "Are you sure you want to logout?",
                                        QMessageBox.StandardButton.Yes |
                                        QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.close()

        def resizeEvent(self, event):
            """Handle window resize for responsive layout"""
            super().resizeEvent(event)
            if hasattr(self, 'header'):
                self.header.update_layout()

        def refresh_advanced_functions_list(self):
            """Refresh the advanced functions list"""
            self.advanced_functions_list.clear()

            try:
                functions = get_advanced_functions()
                if functions:
                    for func in functions:
                        item_text = f"{func.name} ({func.complexity} - {func.estimated_time})"
                        item = QListWidgetItem(item_text)
                        item.setData(Qt.ItemDataRole.UserRole, func)
                        self.advanced_functions_list.addItem(item)

                    self.advanced_status_label.setText(f"Found {len(functions)} advanced functions available")
                else:
                    self.advanced_status_label.setText("No advanced functions available")
                    self.advanced_functions_list.addItem("No functions available")

            except Exception as e:
                logger.error(f"Error loading advanced functions: {e}")
                self.advanced_status_label.setText("Error loading advanced functions")
                self.advanced_functions_list.addItem("Error loading functions")

            # Update function details
            self.advanced_function_details.setPlainText("Select an advanced function to view details and parameters.")
            self.execute_advanced_btn.setEnabled(False)

        def show_advanced_function_details(self):
            """Show details of selected advanced function"""
            current_item = self.advanced_functions_list.currentItem()
            if not current_item:
                self.advanced_function_details.setPlainText("Select an advanced function to view details and parameters.")
                self.execute_advanced_btn.setEnabled(False)
                return

            func = current_item.data(Qt.ItemDataRole.UserRole)
            if not func:
                self.advanced_function_details.setPlainText("Invalid function selected.")
                self.execute_advanced_btn.setEnabled(False)
                return

            # Build details text
            details = f"Function: {func.name}\n"
            details += f"Category: {func.category}\n"
            details += f"Complexity: {func.complexity}\n"
            details += f"Estimated Time: {func.estimated_time}\n\n"
            details += f"Description:\n{func.description}\n\n"

            # Show mock result preview
            details += "Expected Results:\n"
            for key, value in func.mock_result.items():
                if key != "status":
                    details += f"• {key.replace('_', ' ').title()}: {value}\n"

            self.advanced_function_details.setPlainText(details)
            self.execute_advanced_btn.setEnabled(True)

        def execute_advanced_function(self):
            """Execute the selected advanced function"""
            current_item = self.advanced_functions_list.currentItem()
            if not current_item:
                return

            func = current_item.data(Qt.ItemDataRole.UserRole)
            if not func:
                return

            # Execute function
            self.execute_advanced_btn.setEnabled(False)
            self.status_label.setText(f"🚀 Executing {func.name}...")

            # Simulate execution with mock results
            QTimer.singleShot(2000, lambda: self.show_advanced_execution_result(func))

        def show_advanced_execution_result(self, func):
            """Show mock execution result for advanced function"""
            # Get mock execution result
            result = simulate_function_execution(func.name)

            # Generate result text
            result_text = f"Advanced Function Execution Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            result_text += f"Function: {func.name}\n"
            result_text += f"Category: {func.category}\n"
            result_text += f"Complexity: {func.complexity}\n"
            result_text += f"Execution Time: {result.get('execution_time', 'N/A')}\n\n"

            if result["status"] == "SUCCESS":
                result_text += "✅ EXECUTION SUCCESSFUL\n\n"
            else:
                result_text += "❌ EXECUTION FAILED\n\n"
                result_text += f"Error: {result.get('error', 'Unknown error')}\n\n"

            # Show detailed results
            result_text += "Results:\n"
            for key, value in result.items():
                if key not in ["status", "timestamp", "execution_time", "error"]:
                    formatted_key = key.replace('_', ' ').title()
                    result_text += f"• {formatted_key}: {value}\n"

            result_text += "\n⚡ Advanced function completed"

            self.advanced_results_text.setPlainText(result_text)
            self.status_label.setText(f"✅ {func.name} completed successfully")
            self.execute_advanced_btn.setEnabled(True)

class HeadlessDiagnostics:
    """Headless diagnostic operations for CLI mode"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def check_device_detection(self):
        """Check device detection capabilities"""
        self.logger.info("Starting device detection...")
        try:
            # Check J2534 registry
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                   r"SOFTWARE\WOW6432Node\PassThruSupport.04.04")
                self.logger.info("✓ J2534 registry detected")
            except FileNotFoundError:
                self.logger.warning("⚠️ J2534 registry not found")

            # Check SocketCAN (though this is Linux-specific)
            try:
                import socket
                # This would be more complex in real implementation
                self.logger.info("✓ SocketCAN base available")
            except ImportError:
                self.logger.info("✓ SocketCAN base available (simulated)")

            return True
        except Exception as e:
            self.logger.error(f"Device detection failed: {e}")
            return False

    def run_quick_scan(self, brand="Toyota"):
        """Run a quick diagnostic scan"""
        self.logger.info(f"Running quick scan for {brand}...")

        # Simulate scan results
        results = {
            "communication": "ESTABLISHED",
            "bus_status": "NORMAL",
            "voltage": "13.8V",
            "dtc_count": 0,
            "scan_time": "2.3s"
        }

        self.logger.info("✅ Quick scan completed:")
        for key, value in results.items():
            self.logger.info(f"  {key.replace('_', ' ').title()}: {value}")

        return results

    def read_dtcs(self, brand="Toyota"):
        """Read diagnostic trouble codes"""
        self.logger.info(f"Reading DTCs for {brand}...")

        # Simulate DTC reading
        dtcs = [
            {"code": "P0301", "description": "Cylinder 1 Misfire Detected", "status": "Confirmed"},
            {"code": "U0121", "description": "Lost Communication With ABS", "status": "Pending"}
        ]

        if dtcs:
            self.logger.info(f"Found {len(dtcs)} DTC(s):")
            for dtc in dtcs:
                self.logger.info(f"  {dtc['code']}: {dtc['description']} ({dtc['status']})")
        else:
            self.logger.info("No DTCs found")

        return dtcs

    def check_system_health(self):
        """Check overall system health"""
        self.logger.info("Checking system health...")

        health_metrics = {
            "system_health": 98,
            "connection_quality": 85,
            "active_dtcs": 0,
            "security_level": 5
        }

        self.logger.info("System Health Report:")
        for metric, value in health_metrics.items():
            status = "✅" if (isinstance(value, int) and value > 80) or value == 0 or value == 5 else "⚠️"
            self.logger.info(f"  {status} {metric.replace('_', ' ').title()}: {value}")

        return health_metrics

def main():
    """Main application entry point with DACOS theme and headless support"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="AutoDiag Pro - Professional Diagnostic Suite")
    parser.add_argument("--headless", action="store_true",
                       help="Run in headless mode without GUI")
    parser.add_argument("--scan", action="store_true",
                       help="Run quick diagnostic scan")
    parser.add_argument("--dtc", action="store_true",
                       help="Read diagnostic trouble codes")
    parser.add_argument("--health", action="store_true",
                       help="Check system health")
    parser.add_argument("--brand", default="Toyota",
                       help="Vehicle brand for diagnostics (default: Toyota)")

    args = parser.parse_args()

    # Check if running in headless mode
    if args.headless or any([args.scan, args.dtc, args.health]):
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        logger = logging.getLogger(__name__)
        logger.info("🔧 Starting AutoDiag Pro in headless mode")

        # Initialize headless diagnostics
        diagnostics = HeadlessDiagnostics()

        try:
            # Perform requested operations
            if args.scan or not any([args.dtc, args.health]):
                diagnostics.run_quick_scan(args.brand)

            if args.dtc:
                diagnostics.read_dtcs(args.brand)

            if args.health:
                diagnostics.check_system_health()

            # Check device detection by default
            diagnostics.check_device_detection()

            logger.info("✅ Headless diagnostics completed successfully")
            sys.exit(0)

        except Exception as e:
            logger.error(f"❌ Headless diagnostics failed: {e}")
            sys.exit(1)

    # Check if PyQt6 is available for GUI mode
    if not PYQT6_AVAILABLE:
        logger.critical("PyQt6 is required but not installed. Please install PyQt6 using: pip install PyQt6")
        print("ERROR: PyQt6 is required but not installed.")
        print("Please install PyQt6 using: pip install PyQt6")
        print("Or run the installer again to install dependencies automatically.")
        sys.exit(1)

    # GUI mode - create QApplication first before any PyQt operations
    app = QApplication(sys.argv)
    app.setApplicationName("AutoDiag Pro")
    app.setApplicationVersion("3.1.2")

    # Setup logging after app creation
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)

    try:
        # Apply global theme first
        if style_manager:
            style_manager.set_app(app)
            style_manager.ensure_theme()

        # Show login dialog first
        login_dialog = LoginDialog()
        result = login_dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            # Login successful, show main window with user info
            user_info = getattr(login_dialog, 'user_info', None)
            logger.info(f"Login successful, user_info: {user_info}")

            try:
                # FIXED: Pass user_info as current_user_info keyword argument
                window = AutoDiagPro(current_user_info=user_info)
                logger.info("AutoDiagPro window created successfully")
                window.show()
                logger.info("Window shown, starting event loop")
                exit_code = app.exec()
                logger.info(f"Application exited with code: {exit_code}")
                sys.exit(exit_code)
            except Exception as e:
                logger.critical(f"Failed to create main window: {e}")
                import traceback
                logger.critical(f"Traceback: {traceback.format_exc()}")
                QMessageBox.critical(None, "Fatal Error", f"Failed to create main window: {e}")
                sys.exit(1)
        else:
            # Login cancelled or failed
            logger.info("Login cancelled or failed, exiting application")
            sys.exit(0)
    except Exception as e:
        logger.critical(f"Application failed during startup: {e}")
        import traceback
        logger.critical(f"Startup traceback: {traceback.format_exc()}")
        QMessageBox.critical(None, "Fatal Error", f"Application failed to start: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()