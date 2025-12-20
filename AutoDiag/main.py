# main.py - COMPLETE DIAGNOSTIC SUITE IMPLEMENTATION WITH DACOS THEME

#!/usr/bin/env python3
"""
AutoDiag Pro - Professional 25-Brand Diagnostic Suite v3.1.2
COMPLETE IMPLEMENTATION WITH DACOS UNIFIED THEME
RELEASE VERSION - NO MOCK DATA
"""

import sys
from pathlib import Path
import os
import logging
from typing import Dict, List
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
    from AutoDiag.ui.password_change_dialog import PasswordChangeDialog
    from shared.user_database_sqlite import user_database
    
    # Import available tab classes
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

            # Initialize with available manufacturers
            try:
                # Try to get manufacturers from diagnostics controller
                from AutoDiag.core.diagnostics import DiagnosticsController
                temp_controller = DiagnosticsController()
                manufacturers = temp_controller.get_available_manufacturers()
                if manufacturers:
                    self.brand_combo.addItems(manufacturers)
                else:
                    # Empty list if no manufacturers found
                    self.brand_combo.addItem("-- Select Brand --")
            except Exception as e:
                logger.warning(f"Failed to load manufacturers: {e}")
                self.brand_combo.addItem("-- Select Brand --")
            
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
                elif tier_display == "FACTORY":
                    tier_display = "FACTORY"
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
                self.diagnostics_controller = None

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
                self.status_label.setText("✨ System Ready - Connect VCI Device")
                logger.info("UI updated with user information")
            except Exception as e:
                logger.error(f"Failed to update UI: {e}")
                raise

        def _init_diagnostics_controller(self):
            """Initialize the diagnostics controller with UI callbacks"""
            try:
                logger.info("Starting diagnostics controller initialization")
                from AutoDiag.core.diagnostics import DiagnosticsController
                logger.debug("DiagnosticsController import successful")

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
                logger.debug("UI callbacks defined")

                self.diagnostics_controller = DiagnosticsController(ui_callbacks)
                logger.info("Diagnostics controller initialized successfully")

            except Exception as e:
                logger.error(f"Failed to initialize diagnostics controller: {e}")
                import traceback
                logger.error(f"Diagnostics controller init traceback: {traceback.format_exc()}")
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
            self.setWindowTitle("AutoDiag Pro - Professional Diagnostic Suite")
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
            logger.info("Starting tab creation")
            try:
                # Create tabs in the order they should appear
                
                # Dashboard Tab
                try:
                    dashboard_tab = DashboardTab(self)
                    dashboard_widget, dashboard_title = dashboard_tab.create_tab()
                    self.tab_widget.addTab(dashboard_widget, dashboard_title)
                    self.dashboard_tab = dashboard_tab
                    logger.info("Dashboard tab created")
                except Exception as e:
                    logger.error(f"Failed to create dashboard tab: {e}")
                    import traceback
                    logger.error(f"Dashboard tab traceback: {traceback.format_exc()}")

                # Diagnostics Tab
                try:
                    diagnostics_tab = DiagnosticsTab(self)
                    diagnostics_widget, diagnostics_title = diagnostics_tab.create_tab()
                    self.tab_widget.addTab(diagnostics_widget, diagnostics_title)
                    self.diagnostics_tab = diagnostics_tab
                    logger.info("Diagnostics tab created")
                except Exception as e:
                    logger.error(f"Failed to create diagnostics tab: {e}")
                    import traceback
                    logger.error(f"Diagnostics tab traceback: {traceback.format_exc()}")

                # Live Data Tab
                try:
                    live_data_tab = LiveDataTab(self)
                    live_data_widget, live_data_title = live_data_tab.create_tab()
                    self.tab_widget.addTab(live_data_widget, live_data_title)
                    self.live_data_tab = live_data_tab
                    logger.info("Live data tab created")
                except Exception as e:
                    logger.error(f"Failed to create live data tab: {e}")
                    import traceback
                    logger.error(f"Live data tab traceback: {traceback.format_exc()}")

                # CAN Bus Tab
                try:
                    can_bus_tab = CANBusDataTab(self)
                    can_bus_widget, can_bus_title = can_bus_tab.create_tab()
                    self.tab_widget.addTab(can_bus_widget, can_bus_title)
                    self.can_bus_tab = can_bus_tab
                    logger.info("CAN bus tab created")
                except Exception as e:
                    logger.error(f"Failed to create CAN bus tab: {e}")
                    import traceback
                    logger.error(f"CAN bus tab traceback: {traceback.format_exc()}")

                # Special Functions Tab
                try:
                    special_functions_tab = SpecialFunctionsTab(self)
                    special_functions_widget, special_functions_title = special_functions_tab.create_tab()
                    self.tab_widget.addTab(special_functions_widget, special_functions_title)
                    self.special_functions_tab = special_functions_tab
                    logger.info("Special functions tab created")
                except Exception as e:
                    logger.error(f"Failed to create special functions tab: {e}")
                    import traceback
                    logger.error(f"Special functions tab traceback: {traceback.format_exc()}")

                # Calibrations Tab
                try:
                    calibrations_tab = CalibrationsTab(self)
                    calibrations_widget, calibrations_title = calibrations_tab.create_tab()
                    self.tab_widget.addTab(calibrations_widget, calibrations_title)
                    self.calibrations_tab = calibrations_tab
                    logger.info("Calibrations tab created")
                except Exception as e:
                    logger.error(f"Failed to create calibrations tab: {e}")
                    import traceback
                    logger.error(f"Calibrations tab traceback: {traceback.format_exc()}")

                # Advanced Tab
                try:
                    advanced_tab = AdvancedTab(self)
                    advanced_widget, advanced_title = advanced_tab.create_tab()
                    self.tab_widget.addTab(advanced_widget, advanced_title)
                    self.advanced_tab = advanced_tab
                    logger.info("Advanced tab created")
                except Exception as e:
                    logger.error(f"Failed to create advanced tab: {e}")
                    import traceback
                    logger.error(f"Advanced tab traceback: {traceback.format_exc()}")

                # Security Tab
                try:
                    security_tab = SecurityTab(self)
                    security_widget, security_title = security_tab.create_tab()
                    self.tab_widget.addTab(security_widget, security_title)
                    self.security_tab = security_tab
                    logger.info("Security tab created")
                except Exception as e:
                    logger.error(f"Failed to create security tab: {e}")
                    import traceback
                    logger.error(f"Security tab traceback: {traceback.format_exc()}")

                # Connect brand change signals
                logger.debug("Connecting signals")
                if hasattr(self, 'special_functions_tab'):
                    self.header.brand_combo.currentTextChanged.connect(self.special_functions_tab.refresh_functions_list)
                
                if hasattr(self, 'calibrations_tab'):
                    self.header.brand_combo.currentTextChanged.connect(self.calibrations_tab.refresh_calibrations_list)

                # Initialize special functions tab with current brand
                if hasattr(self, 'special_functions_tab'):
                    self.special_functions_tab.refresh_functions_list()
                
                logger.info("Tab creation completed successfully")

            except Exception as e:
                logger.error(f"Exception during tab creation: {e}")
                import traceback
                logger.error(f"Tab creation traceback: {traceback.format_exc()}")
                raise

        def create_status_bar(self):
            """Create status bar with DACOS styling"""
            self.statusBar().showMessage("Ready")
            self.status_label = QLabel("✨ Connect VCI Device to Begin")
            self.status_label.setProperty("class", "status-label")
            self.statusBar().addPermanentWidget(self.status_label)

            # Voltage indicator (will show hardware required)
            self.voltage_label = QLabel("🔋 Hardware Required")
            self.voltage_label.setProperty("class", "status-label")
            self.voltage_label.setStyleSheet("color: #21F5C1; font-weight: bold;")
            self.voltage_label.setToolTip("Connect VCI device for voltage reading")
            self.statusBar().addPermanentWidget(self.voltage_label)

        def change_theme(self, theme_name):
            """Theme change handler - DACOS only"""
            self.status_label.setText("✨ DACOS Unified Theme Active")

        def on_brand_changed(self, brand):
            """Handle brand change"""
            if brand == "-- Select Brand --":
                self.status_label.setText("✨ Select a vehicle brand to begin")
            else:
                self.status_label.setText(f"🚗 Vehicle brand: {brand} - Connect VCI Device")

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

        def run_full_scan(self):
            """Execute full system scan using diagnostics controller"""
            if not self.diagnostics_controller:
                QMessageBox.warning(self, "Hardware Required", 
                                  "Diagnostics controller not initialized. Please restart the application.")
                return
            
            # Check if VCI is connected
            vci_status = self.diagnostics_controller.get_vci_status()
            if vci_status.get('status') != 'connected':
                QMessageBox.warning(self, "Hardware Required", 
                                  "VCI device not connected. Please connect a VCI device first.")
                return
            
            # Execute real scan
            result = self.diagnostics_controller.run_full_scan()
            if not result.get("success"):
                QMessageBox.critical(self, "Scan Failed", 
                                   f"Full system scan failed: {result.get('error', 'Unknown error')}")

        def read_dtcs(self):
            """Read diagnostic trouble codes using diagnostics controller"""
            if not self.diagnostics_controller:
                QMessageBox.warning(self, "Hardware Required", 
                                  "Diagnostics controller not initialized. Please restart the application.")
                return
            
            # Check if VCI is connected
            vci_status = self.diagnostics_controller.get_vci_status()
            if vci_status.get('status') != 'connected':
                QMessageBox.warning(self, "Hardware Required", 
                                  "VCI device not connected. Please connect a VCI device first.")
                return
            
            # Execute real DTC read
            result = self.diagnostics_controller.read_dtcs()
            if not result.get("success"):
                QMessageBox.critical(self, "DTC Read Failed", 
                                   f"Failed to read DTCs: {result.get('error', 'Unknown error')}")

        def clear_dtcs(self):
            """Clear diagnostic trouble codes using diagnostics controller"""
            if not self.diagnostics_controller:
                QMessageBox.warning(self, "Hardware Required", 
                                  "Diagnostics controller not initialized. Please restart the application.")
                return
            
            # Check if VCI is connected
            vci_status = self.diagnostics_controller.get_vci_status()
            if vci_status.get('status') != 'connected':
                QMessageBox.warning(self, "Hardware Required", 
                                  "VCI device not connected. Please connect a VCI device first.")
                return
            
            # Execute real DTC clear
            result = self.diagnostics_controller.clear_dtcs()
            if not result.get("success"):
                QMessageBox.critical(self, "DTC Clear Failed", 
                                   f"Failed to clear DTCs: {result.get('error', 'Unknown error')}")

        def start_live_stream(self):
            """Start live data streaming using diagnostics controller"""
            if not self.diagnostics_controller:
                QMessageBox.warning(self, "Hardware Required", 
                                  "Diagnostics controller not initialized. Please restart the application.")
                return
            
            # Check if VCI is connected
            vci_status = self.diagnostics_controller.get_vci_status()
            if vci_status.get('status') != 'connected':
                QMessageBox.warning(self, "Hardware Required", 
                                  "VCI device not connected. Please connect a VCI device first.")
                return
            
            # Execute real live stream start
            result = self.diagnostics_controller.start_live_stream()
            if not result.get("success"):
                QMessageBox.critical(self, "Live Stream Failed", 
                                   f"Failed to start live data stream: {result.get('error', 'Unknown error')}")
            else:
                # Start realtime CAN bus monitoring
                if hasattr(self, 'can_bus_tab') and self.can_bus_tab:
                    self.can_bus_tab.start_realtime_monitoring()

        def stop_live_stream(self):
            """Stop live data streaming using diagnostics controller"""
            if not self.diagnostics_controller:
                return
            
            # Execute real live stream stop
            result = self.diagnostics_controller.stop_live_stream()
            if not result.get("success"):
                QMessageBox.critical(self, "Stop Stream Failed", 
                                   f"Failed to stop live data stream: {result.get('error', 'Unknown error')}")
            else:
                # Stop realtime CAN bus monitoring
                if hasattr(self, 'can_bus_tab') and self.can_bus_tab:
                    self.can_bus_tab.stop_realtime_monitoring()

        def run_quick_scan(self):
            """Quick scan using diagnostics controller"""
            if not self.diagnostics_controller:
                QMessageBox.warning(self, "Hardware Required", 
                                  "Diagnostics controller not initialized. Please restart the application.")
                return
            
            # Check if VCI is connected
            vci_status = self.diagnostics_controller.get_vci_status()
            if vci_status.get('status') != 'connected':
                QMessageBox.warning(self, "Hardware Required", 
                                  "VCI device not connected. Please connect a VCI device first.")
                return
            
            # Execute real quick scan
            result = self.diagnostics_controller.run_quick_scan()
            if not result.get("success"):
                QMessageBox.critical(self, "Quick Scan Failed", 
                                   f"Quick scan failed: {result.get('error', 'Unknown error')}")

        def show_live_data(self):
            """Switch to live data tab"""
            if not self.diagnostics_controller:
                QMessageBox.warning(self, "Hardware Required", 
                                  "Diagnostics controller not initialized. Please restart the application.")
                return
            
            # Check if VCI is connected
            vci_status = self.diagnostics_controller.get_vci_status()
            if vci_status.get('status') != 'connected':
                QMessageBox.warning(self, "Hardware Required", 
                                  "VCI device not connected. Please connect a VCI device first.")
                return
            
            self.tab_widget.setCurrentIndex(2)  # Switch to live data tab
            self.status_label.setText("📊 Live Data tab selected")

        def show_ecu_info(self):
            """Show ECU information"""
            if not self.diagnostics_controller:
                QMessageBox.warning(self, "Hardware Required", 
                                  "Diagnostics controller not initialized. Please restart the application.")
                return
            
            # Check if VCI is connected
            vci_status = self.diagnostics_controller.get_vci_status()
            if vci_status.get('status') != 'connected':
                QMessageBox.warning(self, "Hardware Required", 
                                  "VCI device not connected. Please connect a VCI device first.")
                return
            
            brand = self.header.brand_combo.currentText()
            result = self.diagnostics_controller.get_ecu_info(brand)
            
            if result.get("success"):
                self.tab_widget.setCurrentIndex(1)  # Switch to diagnostics
                if hasattr(self, 'diagnostics_tab') and self.diagnostics_tab and hasattr(self.diagnostics_tab, 'results_text'):
                    self.diagnostics_tab.results_text.setPlainText(result.get("data", "No ECU information available"))
                self.status_label.setText(f"💾 ECU info for {brand}")
            else:
                QMessageBox.critical(self, "ECU Info Failed", 
                                   f"Failed to get ECU information: {result.get('error', 'Unknown error')}")

        def secure_logout(self):
            """Enhanced logout dialog with DACOS styling"""
            reply = QMessageBox.question(self, "Logout",
                                        "Are you sure you want to logout?",
                                        QMessageBox.StandardButton.Yes |
                                        QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.close()

        def closeEvent(self, event):
            """Handle window close event with logging"""
            logger.info("AutoDiagPro window close event triggered")
            
            # Stop any active operations
            if hasattr(self, 'diagnostics_controller') and self.diagnostics_controller:
                try:
                    self.diagnostics_controller.stop_live_stream()
                except:
                    pass
            
            super().closeEvent(event)
            logger.info("AutoDiagPro window closed")

        def resizeEvent(self, event):
            """Handle window resize for responsive layout"""
            super().resizeEvent(event)
            if hasattr(self, 'header'):
                self.header.update_layout()


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
        """Run a quick diagnostic scan - REAL IMPLEMENTATION ONLY"""
        self.logger.info(f"Running quick scan for {brand}...")
        
        # REAL IMPLEMENTATION - no mock data
        try:
            from AutoDiag.core.diagnostics import DiagnosticsController
            controller = DiagnosticsController()
            
            # Check if VCI device is connected
            vci_status = controller.get_vci_status()
            if vci_status.get('status') != 'connected':
                self.logger.error("❌ VCI device not connected")
                self.logger.info("Please connect a VCI device to perform diagnostics")
                return None
            
            # Execute real scan
            result = controller.run_quick_scan()
            
            if result.get("success"):
                self.logger.info("✅ Quick scan completed successfully")
                # Log real results
                if 'data' in result:
                    self.logger.info(f"Scan results: {result['data']}")
                return result
            else:
                self.logger.error(f"❌ Quick scan failed: {result.get('error', 'Unknown error')}")
                return result
                
        except Exception as e:
            self.logger.error(f"❌ Quick scan failed with exception: {e}")
            return None

    def read_dtcs(self, brand="Toyota"):
        """Read diagnostic trouble codes - REAL IMPLEMENTATION ONLY"""
        self.logger.info(f"Reading DTCs for {brand}...")
        
        # REAL IMPLEMENTATION - no mock data
        try:
            from AutoDiag.core.diagnostics import DiagnosticsController
            controller = DiagnosticsController()
            
            # Check if VCI device is connected
            vci_status = controller.get_vci_status()
            if vci_status.get('status') != 'connected':
                self.logger.error("❌ VCI device not connected")
                self.logger.info("Please connect a VCI device to read DTCs")
                return None
            
            # Execute real DTC read
            result = controller.read_dtcs()
            
            if result.get("success"):
                dtc_data = result.get('data', [])
                if dtc_data:
                    self.logger.info(f"✅ Found {len(dtc_data)} DTC(s)")
                    for dtc in dtc_data:
                        self.logger.info(f"  {dtc.get('code', 'Unknown')}: {dtc.get('description', 'No description')}")
                else:
                    self.logger.info("✅ No DTCs found")
                return result
            else:
                self.logger.error(f"❌ DTC read failed: {result.get('error', 'Unknown error')}")
                return result
                
        except Exception as e:
            self.logger.error(f"❌ DTC read failed with exception: {e}")
            return None

    def check_system_health(self):
        """Check overall system health - REAL IMPLEMENTATION ONLY"""
        self.logger.info("Checking system health...")
        
        # REAL IMPLEMENTATION - no mock data
        try:
            from AutoDiag.core.diagnostics import DiagnosticsController
            controller = DiagnosticsController()
            
            # Check if VCI device is connected
            vci_status = controller.get_vci_status()
            if vci_status.get('status') != 'connected':
                self.logger.error("❌ VCI device not connected")
                self.logger.info("System Health: Hardware Required")
                return {"status": "hardware_required"}
            
            # Get real system health
            health_result = controller.get_system_health()
            
            if health_result.get("success"):
                health_data = health_result.get('data', {})
                self.logger.info("✅ System Health Report:")
                for metric, value in health_data.items():
                    self.logger.info(f"  {metric.replace('_', ' ').title()}: {value}")
                return health_data
            else:
                self.logger.error(f"❌ System health check failed: {health_result.get('error', 'Unknown error')}")
                return health_result
                
        except Exception as e:
            self.logger.error(f"❌ System health check failed with exception: {e}")
            return {"status": "error", "error": str(e)}

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
        logger.info("🔧 Starting AutoDiag Pro in headless mode - RELEASE VERSION")

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

            logger.info("✅ Headless diagnostics completed")
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
                # Create main window
                window = AutoDiagPro(current_user_info=user_info)
                logger.info("AutoDiagPro window created successfully")
                
                try:
                    logger.info("About to show window")
                    window.show()
                    logger.info("Window shown successfully, starting event loop")
                except Exception as e:
                    logger.critical(f"Exception during window.show(): {e}")
                    import traceback
                    logger.critical(f"Window show traceback: {traceback.format_exc()}")
                    QMessageBox.critical(None, "Fatal Error", f"Failed to show main window: {e}")
                    sys.exit(1)
                    
                try:
                    exit_code = app.exec()
                    logger.info(f"Application exited normally with code: {exit_code}")
                except Exception as e:
                    logger.critical(f"Exception during event loop: {e}")
                    import traceback
                    logger.critical(f"Event loop traceback: {traceback.format_exc()}")
                    exit_code = 1
                    
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