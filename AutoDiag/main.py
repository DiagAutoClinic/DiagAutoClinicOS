#!/usr/bin/env python3
"""
AutoDiag Pro - Professional 25-Brand Diagnostic Suite v2.1
FUTURISTIC GLASSMORPHIC DESIGN - FIXED: Global theme support
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

# ----------------------------------------------------------------------
# Qt imports
# ----------------------------------------------------------------------
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

# ----------------------------------------------------------------------
# Add shared/ to Python path (once)
# ----------------------------------------------------------------------
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared'))
if os.path.exists(shared_path) and shared_path not in sys.path:
    sys.path.append(shared_path)

# ----------------------------------------------------------------------
# Import shared modules - with fallbacks
# ----------------------------------------------------------------------
try:
    from style_manager import style_manager
    from brand_database import get_brand_list, get_brand_info, brand_database
    from dtc_database import DTCDatabase
    from vin_decoder import VINDecoder
    from device_handler import DeviceHandler, Protocol
    from security_manager import security_manager, SecurityLevel, UserRole
    from special_functions import special_functions_manager, FunctionCategory, SpecialFunction
    from calibrations_reset import calibrations_resets_manager, ResetType, CalibrationProcedure
    from circular_gauge import CircularGauge, StatCard
except ImportError as e:
    logging.error(f"Failed to import modules: {e}")

    # ---------- FALLBACKS ----------
    class FallbackStyleManager:
        def set_theme(self, theme): pass
        def get_theme_names(self): return ["futuristic", "neon_clinic", "security", "dark", "light", "professional"]
        def set_security_level(self, level): pass
    style_manager = FallbackStyleManager()

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
            self.title_label = QLabel(title)
            self.value_label = QLabel(str(value))
            layout.addWidget(self.title_label)
            layout.addWidget(self.value_label)
        def update_value(self, val):
            if hasattr(self, 'value_label'):
                self.value_label.setText(str(val))

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
        self.username_input.setMinimumHeight(20)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(20)
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
        
        try:
            success, message = security_manager.authenticate_user(username, password)
            
            if success:
                self.accept()
            else:
                self.status_label.setText(f"❌ {message}")
        except:
            # If security_manager not available, allow demo login
            if username == "demo" and password == "demo":
                self.accept()
            else:
                self.status_label.setText("❌ Invalid credentials")

class AutoDiagPro(QMainWindow):
    """Enhanced AutoDiag Professional with FUTURISTIC DESIGN"""
    
    def __init__(self):
        super().__init__()
        
        # Security first - require login
        if not self.secure_login():
            sys.exit(1)
        
        # Initialize managers
        try:
            self.dtc_database = DTCDatabase()
            self.vin_decoder = VINDecoder()
            self.special_functions_manager = special_functions_manager
            self.calibrations_resets_manager = calibrations_resets_manager
            
            # Inject security manager
            self.special_functions_manager.security_manager = security_manager
            self.calibrations_resets_manager.security_manager = security_manager
            brand_database.security_manager = security_manager
            
            # Set security level
            current_level = security_manager.get_security_level()
            style_manager.set_security_level(current_level.name.lower())
        except:
            logger.warning("Security components not available, using demo mode")
        
        # Selected brand
        self.selected_brand = "Toyota"
        
        # Initialize UI
        self.init_ui()
        
        # FIXED: Don't force theme - respect current setting
        
        # Start live updates
        self.start_live_updates()
    
    def secure_login(self) -> bool:
        """Handle secure user login"""
        login_dialog = LoginDialog()
        result = login_dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            logger.info("User logged in successfully")
            return True
        else:
            logger.warning("Login cancelled or failed")
            return False
    
    def init_ui(self):
        """Initialize FUTURISTIC user interface"""
        self.setWindowTitle("AutoDiag Pro - Futuristic Diagnostics")
        self.setGeometry(50, 50, 1600, 1000)
        
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
        header_frame.setMaximumHeight(100)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setSpacing(20)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # User info section
        try:
            user_info = security_manager.get_user_info()
        except:
            user_info = {"full_name": "Demo User", "security_level": "BASIC", "role": "technician"}
        
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
        
        try:
            brands = get_brand_list()
            self.brand_combo.addItems(brands)
            self.brand_combo.setCurrentText(self.selected_brand)
            self.brand_combo.currentTextChanged.connect(self.on_brand_changed)
        except Exception as e:
            logger.error(f"Failed to load brands: {e}")
        
        brand_layout.addWidget(brand_label)
        brand_layout.addWidget(self.brand_combo)
        
        # FIXED: Theme selector with ALL themes
        theme_layout = QVBoxLayout()
        theme_label = QLabel("Theme:")
        theme_label.setStyleSheet("color: #5eead4; font-size: 9pt;")
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(style_manager.get_theme_names())
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        self.theme_combo.setMinimumWidth(150)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        
        # Logout button
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setProperty("class", "danger")
        logout_btn.setMinimumHeight(45)
        logout_btn.setMaximumWidth(120)
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
        try:
            security_level = security_manager.get_security_level().value
        except:
            security_level = 1
        self.security_level_card = StatCard("Security Level", security_level, 5, "")
        
        stats_layout.addWidget(self.system_health_card)
        stats_layout.addWidget(self.connection_quality_card)
        stats_layout.addWidget(self.dtc_count_card)
        stats_layout.addWidget(self.security_level_card)
        
        # Quick Actions Section
        actions_frame = QFrame()
        actions_frame.setProperty("class", "glass-card")
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
        security_layout = QVBoxLayout(security_frame)
        security_layout.setSpacing(10)
        security_layout.setContentsMargins(20, 20, 20, 20)
        
        security_title = QLabel("🔒 Security Overview")
        security_title.setStyleSheet("color: #14b8a6; font-size: 14pt; font-weight: bold;")
        
        try:
            user_info = security_manager.get_user_info()
        except:
            user_info = {"full_name": "Demo User", "security_level": "BASIC", "session_expiry": 0}
        
        info_grid = QGridLayout()
        info_grid.setSpacing(10)
        
        info_grid.addWidget(QLabel("Current User:"), 0, 0)
        info_grid.addWidget(QLabel(user_info.get('full_name', 'Unknown')), 0, 1)
        
        info_grid.addWidget(QLabel("Security Level:"), 1, 0)
        info_grid.addWidget(QLabel(user_info.get('security_level', 'BASIC')), 1, 1)
        
        info_grid.addWidget(QLabel("Session Status:"), 2, 0)
        info_grid.addWidget(QLabel("Active"), 2, 1)
        
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
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        header_label = QLabel("🔍 Advanced Diagnostics")
        header_label.setStyleSheet("color: #14b8a6; font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(header_label)
        
        # Content placeholder
        content_frame = QFrame()
        content_frame.setProperty("class", "glass-card")
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
        """Create live data tab"""
        live_data_tab = QWidget()
        layout = QVBoxLayout(live_data_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        header_label = QLabel("📈 Live Data Monitoring")
        header_label.setStyleSheet("color: #14b8a6; font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(header_label)
        
        content_frame = QFrame()
        content_frame.setProperty("class", "glass-card")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        placeholder = QLabel("🚧 Live data monitoring interface under development")
        placeholder.setStyleSheet("color: #a0d4cc; font-size: 12pt;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        content_layout.addWidget(placeholder)
        
        layout.addWidget(header_frame)
        layout.addWidget(content_frame)
        layout.addStretch()
        
        self.tab_widget.addTab(live_data_tab, "📈 Live Data")

    def create_special_functions_tab(self):
        """Create special functions tab"""
        functions_tab = QWidget()
        layout = QVBoxLayout(functions_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        header_label = QLabel("🔧 Special Functions")
        header_label.setStyleSheet("color: #14b8a6; font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(header_label)
        
        content_frame = QFrame()
        content_frame.setProperty("class", "glass-card")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        placeholder = QLabel("🚧 Special functions interface under development")
        placeholder.setStyleSheet("color: #a0d4cc; font-size: 12pt;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        content_layout.addWidget(placeholder)
        
        layout.addWidget(header_frame)
        layout.addWidget(content_frame)
        layout.addStretch()
        
        self.tab_widget.addTab(functions_tab, "🔧 Special Functions")

    def create_calibrations_resets_tab(self):
        """Create calibrations tab"""
        calib_tab = QWidget()
        layout = QVBoxLayout(calib_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        header_label = QLabel("⚙️ Calibrations & Resets")
        header_label.setStyleSheet("color: #14b8a6; font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(header_label)
        
        content_frame = QFrame()
        content_frame.setProperty("class", "glass-card")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        placeholder = QLabel("🚧 Calibrations interface under development")
        placeholder.setStyleSheet("color: #a0d4cc; font-size: 12pt;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        content_layout.addWidget(placeholder)
        
        layout.addWidget(header_frame)
        layout.addWidget(content_frame)
        layout.addStretch()
        
        self.tab_widget.addTab(calib_tab, "⚙️ Calibrations & Resets")

    def create_advanced_tab(self):
        """Create advanced tab"""
        advanced_tab = QWidget()
        layout = QVBoxLayout(advanced_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        header_label = QLabel("⚙️ Advanced Functions")
        header_label.setStyleSheet("color: #14b8a6; font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(header_label)
        
        content_frame = QFrame()
        content_frame.setProperty("class", "glass-card")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        placeholder = QLabel("🚧 Advanced functions interface under development")
        placeholder.setStyleSheet("color: #a0d4cc; font-size: 12pt;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        content_layout.addWidget(placeholder)
        
        layout.addWidget(header_frame)
        layout.addWidget(content_frame)
        layout.addStretch()
        
        self.tab_widget.addTab(advanced_tab, "⚙️ Advanced")
    
    def create_security_tab(self):
        """Create security tab"""
        security_tab = QWidget()
        layout = QVBoxLayout(security_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        header_label = QLabel("🔒 Security & Audit")
        header_label.setStyleSheet("color: #14b8a6; font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(header_label)
        
        status_frame = QFrame()
        status_frame.setProperty("class", "glass-card")
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(20, 20, 20, 20)
        
        status_title = QLabel("Current Session Status")
        status_title.setStyleSheet("color: #14b8a6; font-size: 14pt; font-weight: bold;")
        
        try:
            user_info = security_manager.get_user_info()
            status_text = f"Current User: {user_info.get('full_name', 'Demo User')}\nSecurity Level: {user_info.get('security_level', 'BASIC')}"
        except:
            status_text = "Current User: Demo User\nSecurity Level: BASIC"
        
        self.security_status = QTextEdit()
        self.security_status.setPlainText(status_text)
        self.security_status.setReadOnly(True)
        self.security_status.setMaximumHeight(150)
        
        status_layout.addWidget(status_title)
        status_layout.addWidget(self.security_status)
        
        layout.addWidget(header_frame)
        layout.addWidget(status_frame)
        layout.addStretch()
        
        self.tab_widget.addTab(security_tab, "🔒 Security")
    
    def create_status_bar(self):
        """Create status bar"""
        status_widget = QFrame()
        status_widget.setProperty("class", "glass-card")
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
        self.update_timer.start(2000)
    
    def update_live_data(self):
        """Update live dashboard data"""
        import random
        
        self.system_health_card.update_value(random.randint(95, 99))
        self.connection_quality_card.update_value(random.randint(75, 95))
    
    def change_theme(self, theme_name):
        """FIXED: Change theme using global style_manager"""
        style_manager.set_theme(theme_name)
        self.status_label.setText(f"✨ Theme changed to: {theme_name}")
    
    def on_brand_changed(self, brand):
        """Handle brand selection change"""
        self.selected_brand = brand
        self.status_label.setText(f"✨ Brand changed to: {brand}")
    
    def secure_logout(self):
        """Handle secure logout"""
        reply = QMessageBox.question(self, "Logout", 
                                   "Are you sure you want to logout?",
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                security_manager.logout()
            except:
                pass
            self.close()
    
    def closeEvent(self, event):
        """Secure cleanup on close"""
        try:
            security_manager.logout()
        except:
            pass
        logger.info("AutoDiag Pro closed securely")
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    app.setApplicationName("AutoDiag Pro Futuristic")
    app.setApplicationVersion("2.1.0")
    app.setOrganizationName("SecureAutoClinic")
    
    try:
        window = AutoDiagPro()
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"Application crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()