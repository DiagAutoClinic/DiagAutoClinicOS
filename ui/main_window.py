#!/usr/bin/env python3
# AGENTS: DO NOT TOUCH THIS FILE - THEME IS CENTRALIZED IN shared/theme_constants.py
# ANY CHANGES HERE WILL BE REVERTED

"""
Main Window Module for AutoDiag Pro
Contains the main application window and UI setup
"""

import time
import sys
import os
import logging

# Add project root to Python path to enable imports from shared directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# Import our modules
from ui.login_dialog import LoginDialog
from core.device_manager import DeviceManager
from core.diagnostics import DiagnosticsManager
from core.special_functions import SpecialFunctionsManager
from core.calibrations import CalibrationsManager
from core.security import SecurityManager
from utils.helpers import format_timestamp, get_brand_list, get_theme_info

# Import shared modules
try:
    from shared.style_manager import style_manager
    from shared.brand_database import get_brand_list as shared_get_brand_list, get_brand_info, brand_database
    from shared.dtc_database import DTCDatabase
    from shared.vin_decoder import VINDecoder
    from shared.device_handler import device_handler
    from shared.security_manager import security_manager, SecurityLevel, UserRole
    from shared.special_functions import special_functions_manager, FunctionCategory, EnhancedSpecialFunction
    from shared.calibrations_reset import calibrations_resets_manager, ResetType, CalibrationProcedure
    from shared.circular_gauge import CircularGauge, StatCard
    from shared.animated_bg import AnimatedBackground

    STYLE_MANAGER_AVAILABLE = True
    SHARED_MODULES_AVAILABLE = True
except ImportError as e:
    logging.error(f"Failed to import modules: {e}")
    STYLE_MANAGER_AVAILABLE = False
    SHARED_MODULES_AVAILABLE = False

    # Create comprehensive fallbacks
    class Fallbackstyle_manager:
        def __init__(self):
            self.app = None
        def set_theme(self, theme): pass
        def get_theme_names(self): return ["futuristic", "dark_clinic", "neon_clinic", "security", "dark", "light", "professional", "dacos"]
        def get_theme_info(self): return get_theme_info()
        def set_security_level(self, level): pass
        def set_app(self, app): self.app = app
        def apply_theme(self): pass
    style_manager = Fallbackstyle_manager()

    # Additional fallbacks for missing modules
    class Fallbacksecurity_manager:
        def __init__(self):
            self.current_user = 'demo'
        def authenticate_user(self, username, password):
            self.current_user = username
            return True, "Login successful (fallback)"
        def get_user_info(self):
            return {
                'full_name': 'Demo User',
                'username': 'demo',
                'security_level': 'BASIC',
                'role': 'technician',
                'session_expiry': 0
            }
        def get_security_level(self):
            return type('SecurityLevel', (), {'name': 'BASIC', 'value': 1})()
        def check_security_clearance(self, level):
            return True
        def validate_session(self):
            return True
        def logout(self):
            pass
        def get_audit_log(self, n):
            return []
        def elevate_security(self, username, password, level):
            return True, "Elevated (fallback)"

    security_manager = Fallbacksecurity_manager()

    class SecurityLevel:
        BASIC = 1
        DEALER = 2

    class UserRole:
        TECHNICIAN = 'technician'

    class DTCDatabase:
        pass

    class VINDecoder:
        pass

    class Fallbackdevice_handler:
        pass

    device_handler = Fallbackdevice_handler()

    class FallbackSpecialFunctionsManager:
        def get_brand_functions(self, brand):
            return []
        def get_function(self, brand, fid):
            return None
        def execute_function(self, brand, fid, params):
            return {'success': True}

    special_functions_manager = FallbackSpecialFunctionsManager()

    class FunctionCategory:
        pass

    class EnhancedSpecialFunction:
        pass

    class FallbackCalibrationsResetsManager:
        def get_brand_procedures(self, brand):
            return []
        def get_procedure(self, brand, pid):
            return None
        def execute_procedure(self, brand, pid):
            return {'success': True}

    calibrations_resets_manager = FallbackCalibrationsResetsManager()

    class ResetType:
        pass

    class CalibrationProcedure:
        pass

    class FallbackBrandDatabase:
        pass

    brand_database = FallbackBrandDatabase()

    # Import QWidget for fallbacks
    from PyQt6.QtWidgets import QWidget as FallbackQWidget, QVBoxLayout, QLabel, QFrame

    # Circular gauge fallbacks
    class CircularGauge(FallbackQWidget):
        def __init__(self, *args, **kwargs):
            super().__init__()
            self.setMinimumSize(120, 120)
        def set_value(self, val): pass

    class StatCard(QFrame):
        def __init__(self, title, value, *args, **kwargs):
            super().__init__()
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel(f"{title}\n{value}"))
            self.value_label = QLabel(f"{value}")
            layout.addWidget(self.value_label)

        def update_value(self, val):
            self.value_label.setText(str(val))

    class AnimatedBackground(FallbackQWidget):
        pass

logger = logging.getLogger(__name__)


class AutoDiagPro(QMainWindow):
    """Enhanced AutoDiag Professional with FUTURISTIC DESIGN"""

    def __init__(self):
        super().__init__()
        # Security first - require login
        if not self.secure_login():
            sys.exit(1)

        # Initialize managers
        self.device_manager = DeviceManager()
        self.diagnostics_manager = DiagnosticsManager(self.device_manager)
        self.special_functions_manager = SpecialFunctionsManager(self)
        self.calibrations_manager = CalibrationsManager(self)
        self.security_manager_ui = SecurityManager(self)

        # Initialize DTC database and VIN decoder
        self.dtc_database = DTCDatabase() if SHARED_MODULES_AVAILABLE else None
        self.vin_decoder = VINDecoder() if SHARED_MODULES_AVAILABLE else None

        # Initialize special functions and calibrations managers
        self.special_functions_manager_shared = special_functions_manager if SHARED_MODULES_AVAILABLE else None
        self.calibrations_resets_manager = calibrations_resets_manager if SHARED_MODULES_AVAILABLE else None

        # CRITICAL: Inject security manager into all components
        if SHARED_MODULES_AVAILABLE:
            self.special_functions_manager.security_manager = security_manager
            self.calibrations_resets_manager.security_manager = security_manager
            brand_database.security_manager = security_manager

        # Set security level for styling
        current_level = security_manager.get_security_level()
        if STYLE_MANAGER_AVAILABLE:
            style_manager.set_security_level(current_level.name.lower())

        # Selected brand
        self.selected_brand = "Toyota"  # Default, will be changed based on detection

        # Initialize UI
        self.init_ui()

        # Apply theme
        try:
            if STYLE_MANAGER_AVAILABLE:
                style_manager.set_theme("neon_clinic")
        except Exception as e:
            logger.warning(f"Theme application failed: {e}")

        # Start live updates
        self.start_live_updates()

    def secure_login(self) -> bool:
        """Handle secure user login"""
        login_dialog = LoginDialog()
        result = login_dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            logger.info(f"User logged in: {security_manager.current_user}")
            return True
        else:
            logger.warning("Login cancelled or failed")
            return False

    def init_ui(self):
        """Initialize FUTURISTIC user interface"""
        self.setWindowTitle("AutoDiag Pro - Futuristic Diagnostics")
        
        # Set responsive window size based on screen
        screen = QApplication.primaryScreen()
        screen_size = screen.availableSize()
        
        # Calculate responsive dimensions (80% of available screen, with min/max constraints)
        window_width = min(max(int(screen_size.width() * 0.8), 1000), screen_size.width() - 100)
        window_height = min(max(int(screen_size.height() * 0.8), 700), screen_size.height() - 100)
        
        self.setGeometry(50, 50, window_width, window_height)
        self.setMinimumSize(800, 600)  # Reasonable minimum size

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 20)

        # Create header with user info
        self.create_user_header(main_layout)

        # Create main tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create all tabs
        self.create_dashboard_tab()
        self.create_diagnostics_tab()
        self.create_live_data_tab()
        self.create_special_functions_tab()
        self.create_calibrations_resets_tab()
        self.create_advanced_tab()
        self.create_security_tab()

        # Create status bar
        self.create_status_bar()
        self.show()

    def create_user_header(self, layout):
        """Create FUTURISTIC header with user information"""
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 41, 59, 0.9),
                    stop:1 rgba(15, 23, 42, 0.9));
                border: 1px solid rgba(148, 163, 184, 0.3);
                border-radius: 15px;
            }
        """)
        header_frame.setMaximumHeight(120)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setSpacing(15)
        header_layout.setContentsMargins(20, 15, 20, 15)
        header_layout.setStretch(0, 1)  # User section
        header_layout.setStretch(1, 0)  # Title
        header_layout.setStretch(2, 2)  # Device section (flexible)
        header_layout.setStretch(3, 1)  # ECU section
        header_layout.setStretch(4, 1)  # Brand section (flexible)
        header_layout.setStretch(5, 1)  # Theme section
        header_layout.setStretch(6, 0)  # Logout button

        # User info section
        user_info = security_manager.get_user_info()
        user_section = QFrame()
        user_layout = QVBoxLayout(user_section)
        user_layout.setSpacing(5)
        user_name = QLabel(f"👤 {user_info.get('full_name', 'Unknown')}")
        user_name.setStyleSheet("color: #14b8a6; font-size: 14pt; font-weight: bold;")
        user_role = QLabel(f"🔐 {user_info.get('security_level', 'BASIC')} • {user_info.get('role', 'technician')}")
        user_role.setStyleSheet("color: #5eead4; font-size: 10pt;")
        user_layout.addWidget(user_name)
        user_layout.addWidget(user_role)

        # Title section
        title_label = QLabel("AutoDiag Pro")
        title_label.setProperty("class", "hero-title")
        title_font = QFont("Segoe UI", 22, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #14b8a6;")

        # Brand selector
        brand_layout = QVBoxLayout()
        brand_label = QLabel("Vehicle Brand:")
        brand_label.setStyleSheet("color: #5eead4; font-size: 9pt;")
        self.brand_combo = QComboBox()
        self.brand_combo.setMinimumWidth(120)
        self.brand_combo.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.brand_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(148, 163, 184, 0.5);
                border-radius: 8px;
                padding: 8px;
                color: white;
                min-height: 20px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: rgba(30, 41, 59, 0.95);
                border: 1px solid #334155;
                color: white;
                selection-background-color: #14b8a6;
            }
        """)
        try:
            brands = get_brand_list()
            self.brand_combo.addItems(brands)
            self.brand_combo.setCurrentText(self.selected_brand)
            self.brand_combo.currentTextChanged.connect(self.on_brand_changed)
        except Exception as e:
            logger.error(f"Failed to load brands: {e}")
            # Add default brands
            self.brand_combo.addItems(["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Volkswagen"])
        brand_layout.addWidget(brand_label)
        brand_layout.addWidget(self.brand_combo)

        # Device Connection Controls
        device_layout = QVBoxLayout()
        device_label = QLabel("OBD Device:")
        device_label.setStyleSheet("color: #5eead4; font-size: 9pt;")
        self.device_status_label = QLabel("🔴 Disconnected")
        self.device_status_label.setStyleSheet("color: #ef4444; font-weight: bold;")
        self.device_connect_btn = QPushButton("🔌 Connect")
        self.device_connect_btn.setProperty("class", "primary")
        self.device_connect_btn.setMinimumHeight(30)
        self.device_connect_btn.clicked.connect(self.toggle_device_connection)
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_status_label)
        device_layout.addWidget(self.device_connect_btn)

        # ECU Identification Status
        ecu_layout = QVBoxLayout()
        ecu_label = QLabel("ECU:")
        ecu_label.setStyleSheet("color: #5eead4; font-size: 9pt;")
        self.ecu_status_label = QLabel("❓ Unknown")
        self.ecu_status_label.setStyleSheet("color: #a0d4cc; font-weight: bold;")
        self.ecu_info_label = QLabel("No ECU data")
        self.ecu_info_label.setStyleSheet("color: #a0d4cc; font-size: 8pt;")
        ecu_layout.addWidget(ecu_label)
        ecu_layout.addWidget(self.ecu_status_label)
        ecu_layout.addWidget(self.ecu_info_label)

        # Theme selector
        theme_layout = QVBoxLayout()
        theme_label = QLabel("Theme:")
        theme_label.setStyleSheet("color: #5eead4; font-size: 9pt;")
        self.theme_combo = QComboBox()
        theme_info = get_theme_info()
        for theme_id, info in theme_info.items():
            self.theme_combo.addItem(info['name'], theme_id)
        self.theme_combo.setCurrentText("Neon Clinic")
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        self.theme_combo.setMinimumWidth(100)
        self.theme_combo.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(148, 163, 184, 0.5);
                border-radius: 8px;
                padding: 8px;
                color: white;
                min-height: 20px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: rgba(30, 41, 59, 0.95);
                border: 1px solid #334155;
                color: white;
                selection-background-color: #14b8a6;
            }
        """)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)

        # Logout button
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setProperty("class", "danger")
        logout_btn.setMinimumHeight(45)
        logout_btn.setMaximumWidth(120)
        logout_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ef4444, stop:1 #dc2626);
                border: none;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #dc2626, stop:1 #b91c1c);
            }
        """)
        logout_btn.clicked.connect(self.secure_logout)

        header_layout.addWidget(user_section)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addLayout(device_layout)
        header_layout.addLayout(ecu_layout)
        header_layout.addLayout(brand_layout)
        header_layout.addLayout(theme_layout)
        header_layout.addWidget(logout_btn)
        layout.addWidget(header_frame)

    def create_dashboard_tab(self):
        """Create FUTURISTIC dashboard with live stats"""
        dashboard_tab = QWidget()
        layout = QVBoxLayout(dashboard_tab)
        layout.setSpacing(20)
        layout.setContentsMargins(15, 15, 15, 15)

        # Stats Overview Section - Make responsive using flow layout
        stats_section = QFrame()
        stats_container = QWidget()
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        # Top row for cards
        top_cards_widget = QWidget()
        top_cards_layout = QHBoxLayout(top_cards_widget)
        top_cards_layout.setSpacing(20)
        
        # Bottom row for additional info (optional)
        bottom_info_widget = QWidget()
        bottom_info_layout = QHBoxLayout(bottom_info_widget)
        bottom_info_layout.setSpacing(20)

        # System Health
        self.system_health_card = StatCard("System Health", 98, 100, "%")
        self.system_health_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.system_health_card.setMinimumHeight(120)

        # Connection Status
        self.connection_quality_card = StatCard("Connection", 85, 100, "%")
        self.connection_quality_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.connection_quality_card.setMinimumHeight(120)

        # DTCs Found
        self.dtc_count_card = StatCard("Active DTCs", 0, 20, "")
        self.dtc_count_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.dtc_count_card.setMinimumHeight(120)

        # Security Level
        security_level = security_manager.get_security_level().value
        self.security_level_card = StatCard("Security Level", security_level, 5, "")
        self.security_level_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.security_level_card.setMinimumHeight(120)

        top_cards_layout.addWidget(self.system_health_card)
        top_cards_layout.addWidget(self.connection_quality_card)
        top_cards_layout.addWidget(self.dtc_count_card)
        top_cards_layout.addWidget(self.security_level_card)
        
        stats_layout.addWidget(top_cards_widget)
        stats_layout.addWidget(bottom_info_widget)
        
        # Replace the old stats_section layout with the new one
        # This is handled by the container layout
        stats_section = stats_container

        # Quick Actions Section
        actions_frame = QFrame()
        actions_frame.setProperty("class", "glass-card")
        actions_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 41, 59, 0.8),
                    stop:1 rgba(15, 23, 42, 0.9));
                border: 1px solid rgba(148, 163, 184, 0.3);
                border-radius: 15px;
            }
        """)
        actions_layout = QVBoxLayout(actions_frame)
        actions_layout.setSpacing(15)
        actions_layout.setContentsMargins(20, 20, 20, 20)

        actions_title = QLabel("🚀 Quick Actions")
        actions_title.setStyleSheet("color: #14b8a6; font-size: 16pt; font-weight: bold;")
        actions_layout.addWidget(actions_title)

        # Quick action buttons - Use responsive grid that adapts to screen size
        btn_widget = QWidget()
        btn_layout = QGridLayout(btn_widget)
        btn_layout.setSpacing(15)

        scan_btn = QPushButton("🔍 Quick Scan")
        scan_btn.setProperty("class", "primary")
        scan_btn.setMinimumHeight(50)
        scan_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        dtc_btn = QPushButton("📋 Read DTCs")
        dtc_btn.setProperty("class", "primary")
        dtc_btn.setMinimumHeight(50)
        dtc_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        live_btn = QPushButton("📈 Live Data")
        live_btn.setProperty("class", "success")
        live_btn.setMinimumHeight(50)
        live_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        ecu_btn = QPushButton("⚙️ ECU Info")
        ecu_btn.setProperty("class", "success")
        ecu_btn.setMinimumHeight(50)
        ecu_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        btn_layout.addWidget(scan_btn, 0, 0)
        btn_layout.addWidget(dtc_btn, 0, 1)
        btn_layout.addWidget(live_btn, 1, 0)
        btn_layout.addWidget(ecu_btn, 1, 1)
        
        # Size policies already set during widget creation, no additional work needed

        actions_layout.addLayout(btn_layout)

        # Security Overview
        security_frame = QFrame()
        security_frame.setProperty("class", "glass-card")
        security_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 41, 59, 0.8),
                    stop:1 rgba(15, 23, 42, 0.9));
                border: 1px solid rgba(148, 163, 184, 0.3);
                border-radius: 15px;
            }
        """)
        security_layout = QVBoxLayout(security_frame)
        security_layout.setSpacing(10)
        security_layout.setContentsMargins(20, 20, 20, 20)

        security_title = QLabel("🔒 Security Overview")
        security_title.setStyleSheet("color: #14b8a6; font-size: 14pt; font-weight: bold;")

        user_info = security_manager.get_user_info()

        info_grid = QGridLayout()
        info_grid.setSpacing(10)

        info_grid.addWidget(QLabel("Current User:"), 0, 0)
        info_grid.addWidget(QLabel(user_info.get('full_name', 'Unknown')), 0, 1)

        info_grid.addWidget(QLabel("Security Level:"), 1, 0)
        info_grid.addWidget(QLabel(user_info.get('security_level', 'BASIC')), 1, 1)

        info_grid.addWidget(QLabel("Session Expires:"), 2, 0)
        info_grid.addWidget(QLabel(format_timestamp(user_info.get('session_expiry', 0))), 2, 1)

        # Style the labels
        for i in range(3):
            info_grid.itemAtPosition(i, 0).widget().setStyleSheet("color: #5eead4; font-weight: bold;")
            info_grid.itemAtPosition(i, 1).widget().setStyleSheet("color: #a0d4cc;")

        security_layout.addWidget(security_title)
        security_layout.addLayout(info_grid)

        layout.addWidget(stats_section)
        layout.addWidget(actions_frame)
        layout.addWidget(security_frame)
        layout.addStretch()

        self.tab_widget.addTab(dashboard_tab, "📊 Dashboard")

    def create_diagnostics_tab(self):
        """Create diagnostics tab with futuristic styling"""
        diagnostics_tab = QWidget()
        layout = QVBoxLayout(diagnostics_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 41, 59, 0.8),
                    stop:1 rgba(15, 23, 42, 0.9));
                border: 1px solid rgba(148, 163, 184, 0.3);
                border-radius: 15px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        header_label = QLabel("🔍 Advanced Diagnostics")
        header_label.setStyleSheet("color: #14b8a6; font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(header_label)

        # Diagnostics Controls Section
        controls_frame = QFrame()
        controls_frame.setProperty("class", "glass-card")
        controls_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 41, 59, 0.8),
                    stop:1 rgba(15, 23, 42, 0.9));
                border: 1px solid rgba(148, 163, 184, 0.3);
                border-radius: 15px;
            }
        """)
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(15, 15, 15, 15)

        # Buttons for the core functions
        self.vin_read_btn = QPushButton("🔍 Read VIN")
        self.vin_read_btn.setProperty("class", "primary")
        self.vin_read_btn.setMinimumHeight(45)
        self.vin_read_btn.clicked.connect(lambda: self.diagnostics_manager.read_vin(self))
        self.vin_read_btn.setEnabled(False)  # Disabled until ECU is identified

        self.dtc_read_btn = QPushButton("📋 Read DTCs")
        self.dtc_read_btn.setProperty("class", "primary")
        self.dtc_read_btn.setMinimumHeight(45)
        self.dtc_read_btn.clicked.connect(lambda: self.diagnostics_manager.read_dtcs(self))
        self.dtc_read_btn.setEnabled(False)  # Disabled until ECU is identified

        self.dtc_clear_btn = QPushButton("🗑️ Clear DTCs")
        self.dtc_clear_btn.setProperty("class", "danger")
        self.dtc_clear_btn.setMinimumHeight(45)
        self.dtc_clear_btn.clicked.connect(lambda: self.diagnostics_manager.clear_dtcs(self))
        self.dtc_clear_btn.setEnabled(False)  # Disabled until ECU is identified

        # Add buttons to the layout
        controls_layout.addWidget(self.vin_read_btn)
        controls_layout.addWidget(self.dtc_read_btn)
        controls_layout.addWidget(self.dtc_clear_btn)
        controls_layout.addStretch()  # Push buttons to the left

        # Content placeholder
        content_frame = QFrame()
        content_frame.setProperty("class", "glass-card")
        content_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 41, 59, 0.8),
                    stop:1 rgba(15, 23, 42, 0.9));
                border: 1px solid rgba(148, 163, 184, 0.3);
                border-radius: 15px;
            }
        """)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        placeholder = QLabel("🚧 Advanced diagnostics interface under development\n"
                           "This tab will include:\n"
                           "• Real-time DTC scanning\n"
                           "• Module identification\n"
                           "• Freeze frame data\n"
                           "• Advanced diagnostic protocols")
        placeholder.setStyleSheet("color: #a0d4cc; font-size: 12pt; line-height: 1.8;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(placeholder)

        # Add controls frame above the placeholder
        layout.addWidget(header_frame)
        layout.addWidget(controls_frame)
        layout.addWidget(content_frame)
        layout.addStretch()
        self.tab_widget.addTab(diagnostics_tab, "🔍 Diagnostics")

    def create_live_data_tab(self):
        """Create live data tab with futuristic styling"""
        live_data_tab = QWidget()
        layout = QVBoxLayout(live_data_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 41, 59, 0.8),
                    stop:1 rgba(15, 23, 42, 0.9));
                border: 1px solid rgba(148, 163, 184, 0.3);
                border-radius: 15px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)

        header_label = QLabel("📈 Live Data Monitoring")
        header_label.setStyleSheet("color: #14b8a6; font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(header_label)

        # Content
        content_frame = QFrame()
        content_frame.setProperty("class", "glass-card")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)

        placeholder = QLabel("🚧 Live data monitoring interface under development\n\n"
                           "This tab will include:\n"
                           "• Real-time sensor data\n"
                           "• Parameter graphing\n"
                           "• Data logging\n"
                           "• Custom PIDs")
        placeholder.setStyleSheet("color: #a0d4cc; font-size: 12pt; line-height: 1.8;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)

        content_layout.addWidget(placeholder)

        layout.addWidget(header_frame)
        layout.addWidget(content_frame)
        layout.addStretch()

        self.tab_widget.addTab(live_data_tab, "📈 Live Data")

    def create_advanced_tab(self):
        """Create advanced tab with futuristic styling"""
        advanced_tab = QWidget()
        layout = QVBoxLayout(advanced_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)

        header_label = QLabel("⚙️ Advanced Functions")
        header_label.setStyleSheet("color: #14b8a6; font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(header_label)

        # Content
        content_frame = QFrame()
        content_frame.setProperty("class", "glass-card")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)

        placeholder = QLabel("🚧 Advanced functions interface under development\n\n"
                           "This tab will include:\n"
                           "• Module coding\n"
                           "• Adaptations\n"
                           "• Long coding\n"
                           "• Advanced resets")
        placeholder.setStyleSheet("color: #a0d4cc; font-size: 12pt; line-height: 1.8;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)

        content_layout.addWidget(placeholder)

        layout.addWidget(header_frame)
        layout.addWidget(content_frame)
        layout.addStretch()

        self.tab_widget.addTab(advanced_tab, "⚙️ Advanced")

    def create_special_functions_tab(self):
        """Create FUTURISTIC special functions tab"""
        functions_tab = QWidget()
        layout = QVBoxLayout(functions_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header with brand selection
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)

        header_label = QLabel("🔧 Special Functions")
        header_label.setStyleSheet("color: #14b8a6; font-size: 18pt; font-weight: bold;")

        brand_label = QLabel("Select Brand:")
        brand_label.setStyleSheet("color: #5eead4;")

        self.sf_brand_combo = QComboBox()
        self.sf_brand_combo.addItems(get_brand_list())
        self.sf_brand_combo.setCurrentText(self.selected_brand)
        self.sf_brand_combo.currentTextChanged.connect(self.update_special_functions_list)
        self.sf_brand_combo.setMinimumWidth(180)

        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(brand_label)
        header_layout.addWidget(self.sf_brand_combo)

        # Main content area with splitter
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Functions list
        left_panel = QFrame()
        left_panel.setProperty("class", "glass-card")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)

        list_label = QLabel("Available Functions:")
        list_label.setStyleSheet("color: #5eead4; font-weight: bold; margin-bottom: 10px;")

        self.special_functions_list = QListWidget()
        self.special_functions_list.itemClicked.connect(self.on_special_function_selected)

        left_layout.addWidget(list_label)
        left_layout.addWidget(self.special_functions_list)

        # Right panel - Function details
        right_panel = QFrame()
        right_panel.setProperty("class", "glass-card")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)

        # Function details
        self.sf_name_label = QLabel("Select a function to view details")
        self.sf_name_label.setStyleSheet("color: #14b8a6; font-size: 14pt; font-weight: bold;")

        self.sf_description = QTextEdit()
        self.sf_description.setReadOnly(True)
        self.sf_description.setMaximumHeight(100)
        self.sf_description.setPlaceholderText("Function description will appear here...")

        self.sf_security_label = QLabel("Security Level: --")
        self.sf_security_label.setStyleSheet("color: #5eead4; font-weight: bold;")

        # Parameters section
        self.sf_params_group = QGroupBox("Function Parameters")
        self.sf_params_layout = QVBoxLayout(self.sf_params_group)
        self.sf_params_widget = QWidget()
        self.sf_params_layout.addWidget(self.sf_params_widget)

        # Execute section
        self.sf_execute_btn = QPushButton("⚡ Execute Function")
        self.sf_execute_btn.setProperty("class", "primary")
        self.sf_execute_btn.setMinimumHeight(50)
        self.sf_execute_btn.clicked.connect(self.execute_special_function)
        self.sf_execute_btn.setEnabled(False)

        # Results
        results_label = QLabel("Execution Results:")
        results_label.setStyleSheet("color: #5eead4; font-weight: bold; margin-top: 10px;")

        self.sf_results = QTextEdit()
        self.sf_results.setReadOnly(True)
        self.sf_results.setPlaceholderText("Execution results will appear here...")

        right_layout.addWidget(self.sf_name_label)
        right_layout.addWidget(self.sf_description)
        right_layout.addWidget(self.sf_security_label)
        right_layout.addWidget(self.sf_params_group)
        right_layout.addWidget(self.sf_execute_btn)
        right_layout.addWidget(results_label)
        right_layout.addWidget(self.sf_results)

        content_splitter.addWidget(left_panel)
        content_splitter.addWidget(right_panel)
        # Make splitter responsive - give more space to right panel (details area)
        splitter_width = self.width()
        left_width = max(int(splitter_width * 0.35), 250)  # At least 250px, 35% of total
        right_width = max(int(splitter_width * 0.65), 400)  # At least 400px, 65% of total
        content_splitter.setSizes([left_width, right_width])
        content_splitter.setChildrenCollapsible(True)

        layout.addWidget(header_frame)
        layout.addWidget(content_splitter)

        self.tab_widget.addTab(functions_tab, "🔧 Special Functions")

        # Initial update
        self.update_special_functions_list()

    def create_calibrations_resets_tab(self):
        """Create FUTURISTIC calibrations and resets tab"""
        calib_tab = QWidget()
        layout = QVBoxLayout(calib_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header with brand selection
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)

        header_label = QLabel("⚙️ Calibrations & Resets")
        header_label.setStyleSheet("color: #14b8a6; font-size: 18pt; font-weight: bold;")

        brand_label = QLabel("Select Brand:")
        brand_label.setStyleSheet("color: #5eead4;")

        self.cr_brand_combo = QComboBox()
        self.cr_brand_combo.addItems(get_brand_list())
        self.cr_brand_combo.setCurrentText(self.selected_brand)
        self.cr_brand_combo.currentTextChanged.connect(self.update_calibrations_list)
        self.cr_brand_combo.setMinimumWidth(180)

        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(brand_label)
        header_layout.addWidget(self.cr_brand_combo)

        # Main content
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Procedures list
        left_panel = QFrame()
        left_panel.setProperty("class", "glass-card")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)

        list_label = QLabel("Available Procedures:")
        list_label.setStyleSheet("color: #5eead4; font-weight: bold; margin-bottom: 10px;")

        self.calibrations_list = QListWidget()
        self.calibrations_list.itemClicked.connect(self.on_calibration_selected)

        left_layout.addWidget(list_label)
        left_layout.addWidget(self.calibrations_list)

        # Right panel - Procedure details
        right_panel = QFrame()
        right_panel.setProperty("class", "glass-card")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)

        # Procedure details
        self.cr_name_label = QLabel("Select a procedure to view details")
        self.cr_name_label.setStyleSheet("color: #14b8a6; font-size: 14pt; font-weight: bold;")

        self.cr_description = QTextEdit()
        self.cr_description.setReadOnly(True)
        self.cr_description.setMaximumHeight(80)

        info_layout = QHBoxLayout()
        self.cr_duration_label = QLabel("Duration: --")
        self.cr_security_label = QLabel("Security Level: --")
        self.cr_type_label = QLabel("Type: --")

        for label in [self.cr_duration_label, self.cr_security_label, self.cr_type_label]:
            label.setStyleSheet("color: #5eead4; font-weight: bold;")

        info_layout.addWidget(self.cr_duration_label)
        info_layout.addWidget(self.cr_security_label)
        info_layout.addWidget(self.cr_type_label)
        info_layout.addStretch()

        # Prerequisites
        self.cr_prereq_group = QGroupBox("Prerequisites")
        self.cr_prereq_list = QTextEdit()
        self.cr_prereq_list.setReadOnly(True)
        self.cr_prereq_list.setMaximumHeight(80)
        cr_prereq_layout = QVBoxLayout(self.cr_prereq_group)
        cr_prereq_layout.addWidget(self.cr_prereq_list)

        # Steps
        self.cr_steps_group = QGroupBox("Procedure Steps")
        self.cr_steps_list = QTextEdit()
        self.cr_steps_list.setReadOnly(True)
        cr_steps_layout = QVBoxLayout(self.cr_steps_group)
        cr_steps_layout.addWidget(self.cr_steps_list)

        # Execute
        self.cr_execute_btn = QPushButton("⚡ Execute Procedure")
        self.cr_execute_btn.setProperty("class", "primary")
        self.cr_execute_btn.setMinimumHeight(50)
        self.cr_execute_btn.clicked.connect(self.execute_calibration)
        self.cr_execute_btn.setEnabled(False)

        # Results
        results_label = QLabel("Execution Results:")
        results_label.setStyleSheet("color: #5eead4; font-weight: bold; margin-top: 10px;")

        self.cr_results = QTextEdit()
        self.cr_results.setReadOnly(True)
        self.cr_results.setPlaceholderText("Procedure results will appear here...")

        right_layout.addWidget(self.cr_name_label)
        right_layout.addWidget(self.cr_description)
        right_layout.addLayout(info_layout)
        right_layout.addWidget(self.cr_prereq_group)
        right_layout.addWidget(self.cr_steps_group)
        right_layout.addWidget(self.cr_execute_btn)
        right_layout.addWidget(results_label)
        right_layout.addWidget(self.cr_results)

        content_splitter.addWidget(left_panel)
        content_splitter.addWidget(right_panel)
        # Make splitter responsive - give more space to right panel (details area)
        splitter_width = self.width()
        left_width = max(int(splitter_width * 0.35), 250)  # At least 250px, 35% of total
        right_width = max(int(splitter_width * 0.65), 400)  # At least 400px, 65% of total
        content_splitter.setSizes([left_width, right_width])
        content_splitter.setChildrenCollapsible(True)

        layout.addWidget(header_frame)
        layout.addWidget(content_splitter)

        self.tab_widget.addTab(calib_tab, "⚙️ Calibrations & Resets")

        # Initial update
        self.update_calibrations_list()

    def create_security_tab(self):
        """Create FUTURISTIC security management tab"""
        security_tab = QWidget()
        layout = QVBoxLayout(security_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 41, 59, 0.8),
                    stop:1 rgba(15, 23, 42, 0.9));
                border: 1px solid rgba(148, 163, 184, 0.3);
                border-radius: 15px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)

        header_label = QLabel("🔒 Security & Audit")
        header_label.setStyleSheet("color: #14b8a6; font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(header_label)

        # Security status
        status_frame = QFrame()
        status_frame.setProperty("class", "glass-card")
        status_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 41, 59, 0.8),
                    stop:1 rgba(15, 23, 42, 0.9));
                border: 1px solid rgba(148, 163, 184, 0.3);
                border-radius: 15px;
            }
        """)
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(20, 20, 20, 20)

        status_title = QLabel("Current Session Status")
        status_title.setStyleSheet("color: #14b8a6; font-size: 14pt; font-weight: bold;")

        self.security_status = QTextEdit()
        self.security_status.setReadOnly(True)
        self.security_status.setMaximumHeight(150)
        self.security_status.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(148, 163, 184, 0.5);
                border-radius: 8px;
                color: #e2e8f0;
                padding: 10px;
                font-family: 'Consolas', monospace;
            }
        """)

        status_layout.addWidget(status_title)
        status_layout.addWidget(self.security_status)

        # Security controls
        controls_frame = QFrame()
        controls_frame.setProperty("class", "glass-card")
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setContentsMargins(20, 20, 20, 20)

        controls_title = QLabel("Security Controls")
        controls_title.setStyleSheet("color: #14b8a6; font-size: 14pt; font-weight: bold;")

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        refresh_btn = QPushButton("🔄 Refresh Status")
        refresh_btn.setProperty("class", "primary")
        refresh_btn.setMinimumHeight(45)
        refresh_btn.clicked.connect(self.update_security_status)

        audit_btn = QPushButton("📋 View Audit Log")
        audit_btn.setProperty("class", "success")
        audit_btn.setMinimumHeight(45)
        audit_btn.clicked.connect(self.show_audit_log)

        elevate_btn = QPushButton("⬆️ Elevate Security")
        elevate_btn.setProperty("class", "danger")
        elevate_btn.setMinimumHeight(45)
        elevate_btn.clicked.connect(self.elevate_security)

        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(audit_btn)
        btn_layout.addWidget(elevate_btn)

        controls_layout.addWidget(controls_title)
        controls_layout.addLayout(btn_layout)

        # Quick security check
        check_frame = QFrame()
        check_frame.setProperty("class", "glass-card")
        check_layout = QVBoxLayout(check_frame)
        check_layout.setContentsMargins(20, 20, 20, 20)

        check_title = QLabel("Quick Security Check")
        check_title.setStyleSheet("color: #14b8a6; font-size: 14pt; font-weight: bold;")

        self.security_check_result = QTextEdit()
        self.security_check_result.setReadOnly(True)
        self.security_check_result.setPlaceholderText("Click 'Run Security Check' to verify system status...")

        check_btn = QPushButton("🔍 Run Security Check")
        check_btn.setProperty("class", "primary")
        check_btn.setMinimumHeight(45)
        check_btn.clicked.connect(self.run_security_check)

        check_layout.addWidget(check_title)
        check_layout.addWidget(self.security_check_result)
        check_layout.addWidget(check_btn)

        layout.addWidget(header_frame)
        layout.addWidget(status_frame)
        layout.addWidget(controls_frame)
        layout.addWidget(check_frame)
        layout.addStretch()

        self.tab_widget.addTab(security_tab, "🔒 Security")

    def create_status_bar(self):
        """Create status bar"""
        self.statusBar().showMessage("Ready")

    # Delegate methods to managers
    def toggle_device_connection(self):
        """Toggle device connection"""
        if self.device_manager.device_connected:
            success, message = self.device_manager.disconnect_device()
        else:
            success, message = self.device_manager.connect_device()

        if success:
            if self.device_manager.device_connected:
                self.device_status_label.setText("✅ Connected")
                self.device_status_label.setStyleSheet("color: #10b981; font-weight: bold;")
                self.device_connect_btn.setText("🔌 Disconnect")
                # Attempt ECU identification
                success, message, ecu_info = self.device_manager.identify_ecu()
                if success:
                    self.ecu_status_label.setText("✅ VW ECU Identified")
                    self.ecu_status_label.setStyleSheet("color: #10b981; font-weight: bold;")
                    self.ecu_info_label.setText(f"{ecu_info['ecu_name']} ({ecu_info['model_range']})")
                    # Update brand if VW detected
                    if ecu_info['model_range'].startswith('Polo') or ecu_info['model_range'].startswith('Golf'):
                        self.selected_brand = 'Volkswagen'
                        self.brand_combo.setCurrentText('Volkswagen')
                        self.statusBar().showMessage(f"✅ VW {ecu_info['model_range']} ECU Identified. Brand set to {self.selected_brand}")
                    # Enable diagnostic buttons
                    self.vin_read_btn.setEnabled(True)
                    self.dtc_read_btn.setEnabled(True)
                    self.dtc_clear_btn.setEnabled(True)
                else:
                    self.ecu_status_label.setText("❌ ECU ID Failed")
                    self.ecu_status_label.setStyleSheet("color: #ef4444; font-weight: bold;")
                    self.ecu_info_label.setText("Could not identify ECU or unsupported model")
            else:
                self.device_status_label.setText("🔴 Disconnected")
                self.device_status_label.setStyleSheet("color: #ef4444; font-weight: bold;")
                self.device_connect_btn.setText("🔌 Connect")
        else:
            self.statusBar().showMessage(f"❌ {message}")

    def start_live_updates(self):
        """Start live data updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_live_data)
        self.update_timer.start(2000)  # Update every 2 seconds

    def update_live_data(self):
        """Update live dashboard data"""
        import random

        # Update stat cards with simulated data
        self.system_health_card.update_value(random.randint(95, 99))
        self.connection_quality_card.update_value(random.randint(75, 95))

        # Update connection status label based on device connection state
        if self.device_manager.device_connected:
            self.connection_quality_card.update_value(95)  # High quality when connected
        else:
            self.connection_quality_card.update_value(25)  # Low quality when disconnected

    def update_special_functions_list(self):
        """Update special functions list for current brand"""
        self.special_functions_manager.update_special_functions_list(self.sf_brand_combo.currentText())

    def on_special_function_selected(self, item):
        """Handle special function selection"""
        self.special_functions_manager.on_special_function_selected(item)

    def execute_special_function(self):
        """Execute selected special function"""
        self.special_functions_manager.execute_special_function()

    def update_calibrations_list(self):
        """Update calibrations list"""
        self.calibrations_manager.update_calibrations_list(self.cr_brand_combo.currentText())

    def on_calibration_selected(self, item):
        """Handle calibration selection"""
        self.calibrations_manager.on_calibration_selected(item)

    def execute_calibration(self):
        """Execute calibration procedure"""
        self.calibrations_manager.execute_calibration()

    def update_security_status(self):
        """Update security status display"""
        self.security_manager_ui.update_security_status()

    def show_audit_log(self):
        """Display security audit log"""
        self.security_manager_ui.show_audit_log()

    def run_security_check(self):
        """Run comprehensive security check"""
        self.security_manager_ui.run_security_check()

    def elevate_security(self):
        """Elevate security level"""
        self.security_manager_ui.elevate_security()

    def secure_logout(self):
        """Handle secure logout"""
        reply = QMessageBox.question(self, "Logout",
                                   "Are you sure you want to logout?",
                                   QMessageBox.StandardButton.Yes |
                                   QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            security_manager.logout()
            self.close()

    def change_theme(self, theme_name):
        """Change application theme"""
        if STYLE_MANAGER_AVAILABLE:
            theme_info = style_manager.get_theme_info()
            for theme_id, info in theme_info.items():
                if info.get('name') == theme_name:
                    style_manager.set_theme(theme_id)
                    style_manager.apply_theme()
                    self.statusBar().showMessage(f"✨ Theme changed to: {theme_name}")
                    return
            # Fallback if not found
            self.statusBar().showMessage(f"⚠️ Theme '{theme_name}' not found")
    def resizeEvent(self, event):
        """Handle window resize to maintain responsive layout"""
        super().resizeEvent(event)

        # Update splitter sizes on window resize to maintain proportions
        if hasattr(self, 'tab_widget'):
            current_tab = self.tab_widget.currentWidget()
            if current_tab:
                # Find splitters in the current tab
                splitters = current_tab.findChildren(QSplitter)
                for splitter in splitters:
                    splitter_width = splitter.width()
                    left_width = max(int(splitter_width * 0.35), 250)
                    right_width = max(int(splitter_width * 0.65), 400)
                    splitter.setSizes([left_width, right_width])

    def on_brand_changed(self, brand):
        """Handle brand selection change"""
        self.selected_brand = brand
        self.statusBar().showMessage(f"✨ Brand changed to: {brand}")

    def closeEvent(self, event):
        """Secure cleanup on close"""
        # Disconnect device if connected
        if self.device_manager.device_connected:
            self.device_manager.disconnect_device()
        security_manager.logout()
        logger.info("AutoDiag Pro closed securely")
        event.accept()