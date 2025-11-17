#!/usr/bin/env python3
"""
AutoDiag Pro - Professional 25-Brand Diagnostic Suite v2.1
FUTURISTIC GLASSMORPHIC DESIGN
"""

import sys
import os
import logging
from typing import Dict, List

# ----------------------------------------------------------------------
# Security: Import validation
# ----------------------------------------------------------------------
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

# Security modules
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QPushButton, QLabel, QComboBox, QTabWidget, QFrame, QGroupBox,
    QTableWidget, QTableWidgetItem, QProgressBar, QTextEdit, QLineEdit,
    QHeaderView, QMessageBox, QSplitter, QScrollArea, QCheckBox,
    QInputDialog, QDialog, QFormLayout, QFileDialog, QListWidget,
    QListWidgetItem, QStackedWidget, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, QSettings
from PyQt6.QtGui import QFont, QPalette, QColor

# Import shared modules
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared'))
if os.path.exists(shared_path):
    sys.path.append(shared_path)
try:
    from shared.style_manager import style_manager # Global
    from shared.brand_database import get_brand_list, get_brand_info, brand_database
    from shared.dtc_database import DTCDatabase
    from shared.vin_decoder import VINDecoder
    from shared.device_handler import device_handler
    from shared.security_manager import security_manager, SecurityLevel, UserRole
    from shared.special_functions import special_functions_manager, FunctionCategory, EnhancedSpecialFunction
    from shared.calibrations_reset import calibrations_resets_manager, ResetType, CalibrationProcedure
    from shared.circular_gauge import CircularGauge, StatCard

    SECURITY_MANAGER_AVAILABLE = True
except ImportError as e:
    logging.error(f"Failed to import modules: {e}")
    # Create comprehensive fallbacks
    class Fallbackstyle_manager:
        def __init__(self):
            self.app = None
        def set_theme(self, theme): pass
        def get_theme_names(self): return ["futuristic", "dark_clinic", "neon_clinic", "security", "dark", "light", "professional", "dacos"]
        def get_theme_info(self): return {
            "futuristic": {"name": "Futuristic"},
            "dark_clinic": {"name": "Dark Clinic"},
            "neon_clinic": {"name": "Neon Clinic"},
            "security": {"name": "Security"},
            "dark": {"name": "Dark"},
            "light": {"name": "Light"},
            "professional": {"name": "Professional"},
            "dacos": {"name": "Dacos"}
        }
        def set_security_level(self, level): pass
        def set_app(self, app): self.app = app
        def apply_theme(self): pass
    style_manager = Fallbackstyle_manager()
    
    def get_brand_list(): return ["Toyota", "Honda", "Ford"]
    def get_brand_info(brand): return {}
    
    class CircularGauge(QWidget):
        def __init__(self, *args, **kwargs):
            super().__init__()
            self.setMinimumSize(120, 120)
        def set_value(self, val): pass
    
    class StatCard(QFrame):
        def __init__(self, title, value, *args, **kwargs):
            super().__init__()
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel(f"{title}\n{value}"))
        def update_value(self, val): pass

    # Additional fallbacks for missing modules
    class FallbackSecurityManager:
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

    security_manager = FallbackSecurityManager()

    class SecurityLevel:
        BASIC = 1
        DEALER = 2

    class UserRole:
        TECHNICIAN = 'technician'

    class DTCDatabase:
        pass

    class VINDecoder:
        pass

    class FallbackDeviceHandler:
        pass

    device_handler = FallbackDeviceHandler()

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


logger = logging.getLogger(__name__)

class LoginDialog(QDialog):
    """Secure login dialog with futuristic styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AutoDiag Pro - Secure Login")
        self.setModal(True)
        self.setFixedSize(450, 350)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title with futuristic styling
        title = QLabel("🔒 AutoDiag Pro Login")
        title.setProperty("class", "hero-title")
        title_font = QFont("Segoe UI", 20, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #14b8a6; margin-bottom: 10px;")
        
        subtitle = QLabel("Secure Access Required")
        subtitle.setStyleSheet("color: #5eead4; font-size: 11pt; margin-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Form with glassmorphic styling
        form_widget = QFrame()
        form_widget.setProperty("class", "glass-card")
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(15)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setMinimumHeight(40)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.returnPressed.connect(self.attempt_login)
        
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        login_btn = QPushButton("Login")
        login_btn.setProperty("class", "primary")
        login_btn.setMinimumHeight(45)
        login_btn.clicked.connect(self.attempt_login)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "danger")
        cancel_btn.setMinimumHeight(45)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(login_btn)
        button_layout.addWidget(cancel_btn)
        
        # Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #ef4444; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(form_widget)
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def attempt_login(self):
        """Attempt user login"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.status_label.setText("⚠️ Username and password required")
            return
        
        success, message = security_manager.authenticate_user(username, password)
        
        if success:
            self.accept()
        else:
            self.status_label.setText(f"❌ {message}")

class AutoDiagPro(QMainWindow):
    """Enhanced AutoDiag Professional with FUTURISTIC DESIGN"""
    
    def __init__(self):
        super().__init__()
        
        # Security first - require login
        if not self.secure_login():
            sys.exit(1)
        
        # Initialize managers with security integration
        self.dtc_database = DTCDatabase()
        self.vin_decoder = VINDecoder()
        self.special_functions_manager = special_functions_manager
        self.calibrations_resets_manager = calibrations_resets_manager
        
        # CRITICAL: Inject security manager into all components
        self.special_functions_manager.security_manager = security_manager
        self.calibrations_resets_manager.security_manager = security_manager
        brand_database.security_manager = security_manager
        
        # Set security level for styling
        current_level = security_manager.get_security_level()
        style_manager.set_security_level(current_level.name.lower())
        
        # Selected brand
        self.selected_brand = "Toyota"
        
        # Initialize UI
        self.init_ui()
        
        # Apply old theme
        try:
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
        self.setGeometry(50, 50, 1366, 768)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
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
        header_frame.setMaximumHeight(100)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setSpacing(20)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
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
        self.brand_combo.setMinimumWidth(180)
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
            self.brand_combo.addItems(["Toyota", "Honda", "Ford", "BMW", "Mercedes"])
        
        brand_layout.addWidget(brand_label)
        brand_layout.addWidget(self.brand_combo)
        
        # Theme selector
        theme_layout = QVBoxLayout()
        theme_label = QLabel("Theme:")
        theme_label.setStyleSheet("color: #5eead4; font-size: 9pt;")

        self.theme_combo = QComboBox()
        theme_info = style_manager.get_theme_info()
        for theme_id, info in theme_info.items():
            self.theme_combo.addItem(info['name'], theme_id)
        self.theme_combo.setCurrentText("Neon Clinic")
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        self.theme_combo.setMinimumWidth(150)
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
        
        # Stats Overview Section
        stats_section = QFrame()
        stats_layout = QHBoxLayout(stats_section)
        stats_layout.setSpacing(20)
        
        # System Health
        self.system_health_card = StatCard("System Health", 98, 100, "%")
        
        # Connection Status
        self.connection_quality_card = StatCard("Connection", 85, 100, "%")
        
        # DTCs Found
        self.dtc_count_card = StatCard("Active DTCs", 0, 20, "")
        
        # Security Level
        security_level = security_manager.get_security_level().value
        self.security_level_card = StatCard("Security Level", security_level, 5, "")
        
        stats_layout.addWidget(self.system_health_card)
        stats_layout.addWidget(self.connection_quality_card)
        stats_layout.addWidget(self.dtc_count_card)
        stats_layout.addWidget(self.security_level_card)
        
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
        
        # Quick action buttons
        btn_layout = QGridLayout()
        btn_layout.setSpacing(15)
        
        scan_btn = QPushButton("🔍 Quick Scan")
        scan_btn.setProperty("class", "primary")
        scan_btn.setMinimumHeight(50)
        
        dtc_btn = QPushButton("📋 Read DTCs")
        dtc_btn.setProperty("class", "primary")
        dtc_btn.setMinimumHeight(50)
        
        live_btn = QPushButton("📈 Live Data")
        live_btn.setProperty("class", "success")
        live_btn.setMinimumHeight(50)
        
        ecu_btn = QPushButton("⚙️ ECU Info")
        ecu_btn.setProperty("class", "success")
        ecu_btn.setMinimumHeight(50)
        
        btn_layout.addWidget(scan_btn, 0, 0)
        btn_layout.addWidget(dtc_btn, 0, 1)
        btn_layout.addWidget(live_btn, 1, 0)
        btn_layout.addWidget(ecu_btn, 1, 1)
        
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
        info_grid.addWidget(QLabel(self.format_timestamp(user_info.get('session_expiry', 0))), 2, 1)
        
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
        
        placeholder = QLabel("🚧 Advanced diagnostics interface under development\n\n"
                            "This tab will include:\n"
                            "• Real-time DTC scanning\n"
                            "• Module identification\n"
                            "• Freeze frame data\n"
                            "• Advanced diagnostic protocols")
        placeholder.setStyleSheet("color: #a0d4cc; font-size: 12pt; line-height: 1.8;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        content_layout.addWidget(placeholder)
        
        layout.addWidget(header_frame)
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
        content_splitter.setSizes([350, 850])
        
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
        content_splitter.setSizes([350, 850])
        
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
        
        user_info = security_manager.get_user_info()
        status_text = f"""
            Current User: {user_info.get('full_name', 'Unknown')}
            Username: {user_info.get('username', 'Unknown')}
            Security Level: {user_info.get('security_level', 'BASIC')}
            Role: {user_info.get('role', 'technician')}
            Session Expires: {self.format_timestamp(user_info.get('session_expiry', 0))}
        """
        
        self.security_status = QTextEdit()
        self.security_status.setPlainText(status_text.strip())
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
        """Create FUTURISTIC status bar"""
        status_widget = QFrame()
        status_widget.setProperty("class", "glass-card")
        status_widget.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 41, 59, 0.9), 
                    stop:1 rgba(15, 23, 42, 0.9));
                border: 1px solid rgba(148, 163, 184, 0.3);
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
        status_widget.setMaximumHeight(40)
        
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        self.status_label = QLabel("✨ System Ready")
        self.status_label.setStyleSheet("color: #10b981; font-weight: bold;")
        
        self.connection_status_label = QLabel("⚪ Disconnected")
        self.connection_status_label.setStyleSheet("color: #ef4444;")
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.connection_status_label)
        
        status_widget.setLayout(status_layout)
        self.statusBar().addPermanentWidget(status_widget, 1)
    
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
        
    # Keep all your existing methods from here...
    def update_special_functions_list(self):
        """Update special functions list for current brand"""
        brand = self.sf_brand_combo.currentText()
        functions = self.special_functions_manager.get_brand_functions(brand)
        
        self.special_functions_list.clear()
        
        for function in functions:
            item = QListWidgetItem(f"🔧 {function.name}")
            item.setData(Qt.ItemDataRole.UserRole, function.function_id)
            self.special_functions_list.addItem(item)
        
        self.sf_name_label.setText("Select a function to view details")
        self.sf_description.clear()
        self.sf_security_label.setText("Security Level: --")
        self.sf_execute_btn.setEnabled(False)
        self.clear_parameters()
    
    def on_special_function_selected(self, item):
        """Handle special function selection"""
        brand = self.sf_brand_combo.currentText()
        function_id = item.data(Qt.ItemDataRole.UserRole)
        function = self.special_functions_manager.get_function(brand, function_id)
        
        if not function:
            return
        
        self.sf_name_label.setText(f"🔧 {function.name}")
        self.sf_description.setText(function.description)
        self.sf_security_label.setText(f"Security Level: {function.security_level} "
                                     f"(Current: {security_manager.get_security_level().name})")
        
        self.create_parameter_inputs(function)
        
        has_clearance = security_manager.check_security_clearance(SecurityLevel(function.security_level))
        self.sf_execute_btn.setEnabled(has_clearance)
        
        if not has_clearance:
            self.sf_results.setPlainText(
                f"❌ Insufficient security clearance\n"
                f"Required: Level {function.security_level}\n"
                f"Current: Level {security_manager.get_security_level().value}")
    
    def create_parameter_inputs(self, function):
        """Create parameter input fields"""
        self.clear_parameters()
        
        if not function.parameters:
            no_params = QLabel("✅ No parameters required")
            no_params.setStyleSheet("color: #10b981;")
            self.sf_params_layout.addWidget(no_params)
            return
        
        self.parameter_widgets = {}
        param_widget = QWidget()
        param_layout = QGridLayout(param_widget)
        
        row = 0
        for param_name, param_config in function.parameters.items():
            label = QLabel(f"{param_name}:")
            label.setStyleSheet("color: #5eead4;")
            
            if param_config['type'] == 'bool':
                input_widget = QCheckBox()
            elif param_config['type'] == 'int':
                input_widget = QLineEdit()
                input_widget.setPlaceholderText("Enter number")
            else:
                input_widget = QLineEdit()
                input_widget.setPlaceholderText(f"Enter {param_config['type']}")
            
            param_layout.addWidget(label, row, 0)
            param_layout.addWidget(input_widget, row, 1)
            self.parameter_widgets[param_name] = input_widget
            row += 1
        
        self.sf_params_layout.addWidget(param_widget)
    
    def clear_parameters(self):
        """Clear parameter input section"""
        for i in reversed(range(self.sf_params_layout.count())):
            widget = self.sf_params_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
    
    def execute_special_function(self):
        """Execute selected special function"""
        brand = self.sf_brand_combo.currentText()
        current_item = self.special_functions_list.currentItem()
        
        if not current_item:
            self.sf_results.setPlainText("❌ No function selected")
            return
        
        function_id = current_item.data(Qt.ItemDataRole.UserRole)
        
        parameters = {}
        for param_name, widget in self.parameter_widgets.items():
            if isinstance(widget, QLineEdit):
                parameters[param_name] = widget.text()
            elif isinstance(widget, QCheckBox):
                parameters[param_name] = widget.isChecked()
        
        self.sf_results.setPlainText("⏳ Executing function...")
        
        result = self.special_functions_manager.execute_function(brand, function_id, parameters)
        
        if result.get('success'):
            result_text = "✅ Function executed successfully!\n\n"
            for key, value in result.items():
                if key != 'success':
                    result_text += f"{key}: {value}\n"
        else:
            result_text = f"❌ Execution failed:\n{result.get('error', 'Unknown error')}"
        
        self.sf_results.setPlainText(result_text)
    
    def update_calibrations_list(self):
        """Update calibrations list"""
        brand = self.cr_brand_combo.currentText()
        procedures = self.calibrations_resets_manager.get_brand_procedures(brand)
        
        self.calibrations_list.clear()
        
        for procedure in procedures:
            item = QListWidgetItem(f"⚙️ {procedure.name}")
            item.setData(Qt.ItemDataRole.UserRole, procedure.procedure_id)
            self.calibrations_list.addItem(item)
        
        self.clear_calibration_details()
    
    def on_calibration_selected(self, item):
        """Handle calibration selection"""
        brand = self.cr_brand_combo.currentText()
        procedure_id = item.data(Qt.ItemDataRole.UserRole)
        procedure = self.calibrations_resets_manager.get_procedure(brand, procedure_id)
        
        if not procedure:
            return
        
        self.cr_name_label.setText(f"⚙️ {procedure.name}")
        self.cr_description.setText(procedure.description)
        self.cr_duration_label.setText(f"Duration: {procedure.duration}")
        self.cr_security_label.setText(f"Security: Level {procedure.security_level}")
        self.cr_type_label.setText(f"Type: {procedure.reset_type.value}")
        
        prereq_text = "\n".join([f"• {p}" for p in procedure.prerequisites])
        self.cr_prereq_list.setPlainText(prereq_text or "No prerequisites")
        
        steps_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(procedure.steps)])
        self.cr_steps_list.setPlainText(steps_text)
        
        has_clearance = security_manager.check_security_clearance(SecurityLevel(procedure.security_level))
        self.cr_execute_btn.setEnabled(has_clearance)
        
        if not has_clearance:
            self.cr_results.setPlainText(
                f"❌ Insufficient security clearance\n"
                f"Required: Level {procedure.security_level}")
    
    def clear_calibration_details(self):
        """Clear calibration details"""
        self.cr_name_label.setText("Select a procedure to view details")
        self.cr_description.clear()
        self.cr_duration_label.setText("Duration: --")
        self.cr_security_label.setText("Security Level: --")
        self.cr_type_label.setText("Type: --")
        self.cr_prereq_list.clear()
        self.cr_steps_list.clear()
        self.cr_execute_btn.setEnabled(False)
        self.cr_results.clear()
    
    def execute_calibration(self):
        """Execute calibration procedure"""
        brand = self.cr_brand_combo.currentText()
        current_item = self.calibrations_list.currentItem()
        
        if not current_item:
            self.cr_results.setPlainText("❌ No procedure selected")
            return
        
        procedure_id = current_item.data(Qt.ItemDataRole.UserRole)
        self.cr_results.setPlainText("⏳ Executing procedure...")
        
        result = self.calibrations_resets_manager.execute_procedure(brand, procedure_id)
        
        if result.get('success'):
            result_text = "✅ Procedure executed successfully!\n\n"
            for key, value in result.items():
                if key != 'success':
                    result_text += f"{key}: {value}\n"
        else:
            result_text = f"❌ Execution failed:\n{result.get('error', 'Unknown error')}"
        
        self.cr_results.setPlainText(result_text)
    
    def update_security_status(self):
        """Update security status display"""
        user_info = security_manager.get_user_info()
        status_text = f"""
Current User: {user_info.get('full_name', 'Unknown')}
Username: {user_info.get('username', 'Unknown')}
Security Level: {user_info.get('security_level', 'BASIC')}
Role: {user_info.get('role', 'technician')}
Session Expires: {self.format_timestamp(user_info.get('session_expiry', 0))}
        """
        self.security_status.setPlainText(status_text.strip())
    
    def show_audit_log(self):
        """Display security audit log"""
        audit_log = security_manager.get_audit_log(50)
        
        log_text = "🔒 Security Audit Log (Last 50 Events)\n\n"
        for event in audit_log:
            log_text += f"[{self.format_timestamp(event['timestamp'])}] {event['event_type']} - {event['username']}\n"
            if event['details']:
                log_text += f"    {event['details']}\n"
            log_text += "\n"
        
        QMessageBox.information(self, "Security Audit Log", log_text)
    
    def run_security_check(self):
        """Run comprehensive security check"""
        checks = []
        
        if security_manager.validate_session():
            checks.append("✅ Session is valid")
        else:
            checks.append("❌ Session is invalid")
        
        current_level = security_manager.get_security_level()
        checks.append(f"✅ Current security level: {current_level.name}")
        
        brand = self.sf_brand_combo.currentText()
        functions = self.special_functions_manager.get_brand_functions(brand)
        accessible = sum(1 for f in functions if 
                        security_manager.check_security_clearance(SecurityLevel(f.security_level)))
        checks.append(f"✅ Accessible functions: {accessible}/{len(functions)}")
        
        self.security_check_result.setPlainText("\n".join(checks))
    
    def elevate_security(self):
        """Elevate security level"""
        username, ok = QInputDialog.getText(self, "Security Elevation", "Enter username:")
        if not ok or not username:
            return
        
        password, ok = QInputDialog.getText(self, "Security Elevation",
                                          "Enter password:", 
                                          QLineEdit.EchoMode.Password)
        if not ok or not password:
            return
        
        required_level = SecurityLevel.DEALER
        success, message = security_manager.elevate_security(username, password, required_level)
        
        if success:
            QMessageBox.information(self, "Security Elevated", message)
            self.update_security_status()
        else:
            QMessageBox.warning(self, "Elevation Failed", message)
    
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
        theme_info = style_manager.get_theme_info()
        for theme_id, info in theme_info.items():
            if info.get('name') == theme_name:
                style_manager.set_theme(theme_id)
                style_manager.apply_theme()
                self.status_label.setText(f"✨ Theme changed to: {theme_name}")
                return
        # Fallback if not found
        self.status_label.setText(f"⚠️ Theme '{theme_name}' not found")
    
    def format_timestamp(self, timestamp: float) -> str:
        """Format timestamp for display"""
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    
    def on_brand_changed(self, brand):
        """Handle brand selection change"""
        self.selected_brand = brand
        self.status_label.setText(f"✨ Brand changed to: {brand}")
    
    def closeEvent(self, event):
        """Secure cleanup on close"""
        security_manager.logout()
        logger.info("AutoDiag Pro closed securely")
        event.accept()

def main():
    """Main application entry point"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('autodiag.log', mode='w', encoding='utf-8')
        ]
    )

    app = QApplication(sys.argv)

    app.setApplicationName("AutoDiag Pro Futuristic")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("SecureAutoClinic")

    try:
        window = AutoDiagPro()
        style_manager.set_app(app)
        style_manager.apply_theme()
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"Application crashed: {e}")
        QMessageBox.critical(None, "Fatal Error", f"Application crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
