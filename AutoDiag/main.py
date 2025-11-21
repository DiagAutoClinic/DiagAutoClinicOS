#!/usr/bin/env python3
"""
AutoDiag Pro - Professional 25-Brand Diagnostic Suite v3.1
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
    QListWidgetItem, QStackedWidget, QGridLayout, QSizePolicy, QBoxLayout
)
from PyQt6.QtCore import Qt, QTimer, QSettings
from PyQt6.QtGui import QFont, QPalette, QColor

# ----------------------------------------------------------------------
# Add shared/ to Python path (once)
# ----------------------------------------------------------------------
# Get the project root directory (parent of AutoDiag directory)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
shared_path = os.path.join(project_root, 'shared')
ui_path = os.path.join(project_root, 'ui')

# Add both paths to Python path
for path in [shared_path, ui_path, project_root]:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

# ----------------------------------------------------------------------
# Import shared modules - with fallbacks
# ----------------------------------------------------------------------
SECURITY_MANAGER_AVAILABLE = False
try:
    from shared.style_manager import style_manager
    from shared.brand_database import get_brand_list, get_brand_info, brand_database
    from shared.dtc_database import DTCDatabase
    from shared.vin_decoder import VINDecoder
    from shared.device_handler import DeviceHandler
    from shared.security_manager import security_manager, SecurityLevel, UserRole
    from shared.special_functions import special_functions_manager, FunctionCategory, EnhancedSpecialFunction
    from shared.calibrations_reset import calibrations_resets_manager, ResetType, CalibrationProcedure
    from shared.circular_gauge import CircularGauge, StatCard
    from ui.login_dialog import LoginDialog
    SECURITY_MANAGER_AVAILABLE = True
except ImportError as e:
    logging.error(f"Failed to import modules: {e}")
    SECURITY_MANAGER_AVAILABLE = False

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

class AutoDiagPro(QMainWindow):
    def __init__(self):
        super(AutoDiagPro, self).__init__()  # Or super().__init__() in Python 3

        # Security first - require login
        if not self.secure_login():
            sys.exit(1)
            
        # Initialize managers
        try:
            self.dtc_database = DTCDatabase()
            self.vin_decoder = VINDecoder()
            self.special_functions_manager = special_functions_manager
            self.calibrations_resets_manager = calibrations_resets_manager
        
            # Safely inject security manager if available
            if SECURITY_MANAGER_AVAILABLE:
                self.special_functions_manager.security_manager = security_manager
                self.calibrations_resets_manager.security_manager = security_manager
                brand_database.security_manager = security_manager
                
                # Set security level
                current_level = security_manager.get_security_level()
                style_manager.set_security_level(current_level.name.lower())
        except Exception as e:
            logger.warning(f"Security components not available, using demo mode: {e}")

        # Selected brand
        self.selected_brand = "Toyota"

        # Initialize UI
        self.init_ui()

        # Start live updates
        self.start_live_updates()
    
    def secure_login(self) -> bool:
        """Handle secure user login"""
        try:
            login_dialog = LoginDialog()
            result = login_dialog.exec()

            if result == QDialog.DialogCode.Accepted:
                logger.info("User logged in successfully")
                return True
            else:
                logger.warning("Login cancelled or failed")
                return False
        except ImportError as e:
            logger.warning(f"GUI login failed, falling back to console: {e}")
            return self.console_login()

    def console_login(self) -> bool:
        """Console-based login fallback"""
        print("\n" + "="*50)
        print("🔒 AutoDiag Pro - Console Login")
        print("="*50)
        print("Demo credentials: demo/demo")
        print("Other valid: admin/admin123, technician/tech123, user/user123")
        print("="*50)

        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                username = input(f"Username (attempt {attempt + 1}/{max_attempts}): ").strip()
                password = input("Password: ").strip()

                # Simple validation
                valid_credentials = [
                    ("demo", "demo"),
                    ("admin", "admin123"),
                    ("technician", "tech123"),
                    ("user", "user123")
                ]

                for user, pwd in valid_credentials:
                    if username == user and password == pwd:
                        print(f"✓ Welcome, {username}!")
                        logger.info(f"User {username} logged in via console")
                        return True

                print("❌ Invalid credentials")
                if attempt < max_attempts - 1:
                    print("Please try again.\n")

            except KeyboardInterrupt:
                print("\nLogin cancelled")
                return False
            except EOFError:
                print("\nLogin cancelled")
                return False

        print("❌ Maximum login attempts exceeded")
        return False

    def init_ui(self):
        """Initialize FUTURISTIC user interface with responsive scrolling"""
        self.setWindowTitle("AutoDiag Pro - Futuristic Diagnostics")
        
        # Make window responsive with minimum size but allow growing
        self.setMinimumSize(1280, 700)
        self.resize(1366, 768)  # Start with a reasonable size
        
        # Set dark theme as default
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f172a, stop:1 #1e293b);
                color: #e2e8f0;
            }
            QTabWidget::pane {
                border: 1px solid #334155;
                background: rgba(30, 41, 59, 0.8);
            }
            QTabBar::tab {
                background: rgba(71, 85, 105, 0.7);
                color: #cbd5e1;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background: rgba(14, 184, 166, 0.9);
                color: #0f172a;
                font-weight: bold;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(30, 41, 59, 0.3);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: rgba(14, 184, 166, 0.7);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(14, 184, 166, 0.9);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background: rgba(30, 41, 59, 0.3);
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: rgba(14, 184, 166, 0.7);
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgba(14, 184, 166, 0.9);
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        
        # Create central widget for QMainWindow
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout for central widget
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create header with user info
        self.create_user_header(main_layout)
        
        # Create main tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.tab_widget, 1)  # Give tabs more space
        
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
        header_frame.setMinimumHeight(80)
        header_frame.setMaximumHeight(120)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setSpacing(15)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # User info section
        try:
            if SECURITY_MANAGER_AVAILABLE:
                user_info = security_manager.get_user_info()
            else:
                user_info = {"full_name": "Demo User", "security_level": "BASIC", "role": "technician"}
        except:
            user_info = {"full_name": "Demo User", "security_level": "BASIC", "role": "technician"}
        
        user_section = QFrame()
        user_layout = QVBoxLayout(user_section)
        user_layout.setSpacing(2)
        
        user_name = QLabel(f"👤 {user_info.get('full_name', 'Unknown')}")
        user_name.setStyleSheet("color: #14b8a6; font-size: 12pt; font-weight: bold;")
        
        user_role = QLabel(f"🔐 {user_info.get('security_level', 'BASIC')} • {user_info.get('role', 'technician')}")
        user_role.setStyleSheet("color: #5eead4; font-size: 9pt;")
        
        user_layout.addWidget(user_name)
        user_layout.addWidget(user_role)
        
        # Title section
        title_label = QLabel("AutoDiag Pro")
        title_label.setProperty("class", "hero-title")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Bold)  # Smaller font for better fit
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #14b8a6;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Brand selector
        brand_layout = QVBoxLayout()
        brand_label = QLabel("Vehicle:")
        brand_label.setStyleSheet("color: #5eead4; font-size: 8pt;")
        
        self.brand_combo = QComboBox()
        self.brand_combo.setMinimumWidth(120)  # Smaller width
        self.brand_combo.setMaximumWidth(150)
        self.brand_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(148, 163, 184, 0.5);
                border-radius: 6px;
                padding: 6px;
                color: white;
                min-height: 18px;
                font-size: 9pt;
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
        theme_label.setStyleSheet("color: #5eead4; font-size: 8pt;")
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(style_manager.get_theme_names())
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        self.theme_combo.setMinimumWidth(100)
        self.theme_combo.setMaximumWidth(130)
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(148, 163, 184, 0.5);
                border-radius: 6px;
                padding: 6px;
                color: white;
                min-height: 18px;
                font-size: 9pt;
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
        logout_btn = QPushButton("🚪")
        logout_btn.setProperty("class", "danger")
        logout_btn.setMinimumHeight(35)
        logout_btn.setMaximumWidth(45)
        logout_btn.setToolTip("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ef4444, stop:1 #dc2626);
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                font-size: 12pt;
                padding: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #dc2626, stop:1 #b91c1c);
            }
        """)
        logout_btn.clicked.connect(self.secure_logout)
        
        # Add widgets to header - use responsive layout
        def update_header_layout():
            width = self.width()
            if width < 900:
                # Compact layout for narrow screens
                user_section.hide()
                title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                header_layout.setDirection(QBoxLayout.Direction.LeftToRight)
                header_layout.addWidget(logout_btn, 0)
                header_layout.addWidget(title_label, 1)
                header_layout.addLayout(brand_layout, 0)
                header_layout.addLayout(theme_layout, 0)
            else:
                # Full layout for wider screens
                user_section.show()
                title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                header_layout.setDirection(QBoxLayout.Direction.LeftToRight)
                header_layout.addWidget(user_section, 0)
                header_layout.addWidget(title_label, 1)
                header_layout.addLayout(brand_layout, 0)
                header_layout.addLayout(theme_layout, 0)
                header_layout.addWidget(logout_btn, 0)
        
        # Initial layout setup
        update_header_layout()
        
        # Store reference for resizing
        self._update_header_layout = update_header_layout
        
        layout.addWidget(header_frame)

    def create_dashboard_tab(self):
        """Create FUTURISTIC dashboard with live stats and scrollable content"""
        dashboard_tab = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_tab)
        dashboard_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for scroll area
        
        # Create scroll area for dashboard content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)  # Remove border
        
        # Create scrollable content widget
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Stats Overview Section
        stats_section = QFrame()
        stats_layout = QHBoxLayout(stats_section)
        stats_layout.setSpacing(20)
        
        # Make stats responsive - stack vertically on small screens
        def make_responsive_stats():
            if self.width() < 900:
                stats_layout.setDirection(QBoxLayout.Direction.TopToBottom)
                stats_layout.setSpacing(10)
            else:
                stats_layout.setDirection(QBoxLayout.Direction.LeftToRight)
                stats_layout.setSpacing(20)
        
        # System Health
        self.system_health_card = StatCard("System Health", 98)
        
        # Connection Status
        self.connection_quality_card = StatCard("Connection", 85)
        
        # DTCs Found
        self.dtc_count_card = StatCard("Active DTCs", 0)
        
        # Security Level
        try:
            if SECURITY_MANAGER_AVAILABLE:
                security_level = security_manager.get_security_level().value
            else:
                security_level = 1
        except:
            security_level = 1
        self.security_level_card = StatCard("Security Level", security_level)
        
        # Style the stat cards
        for card in [self.system_health_card, self.connection_quality_card,
                    self.dtc_count_card, self.security_level_card]:
            card.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(30, 41, 59, 0.8),
                        stop:1 rgba(15, 23, 42, 0.9));
                    border: 1px solid rgba(148, 163, 184, 0.3);
                    border-radius: 12px;
                    padding: 15px;
                }
                QLabel {
                    color: #e2e8f0;
                    background: transparent;
                }
            """)
            card.title_label.setStyleSheet("color: #5eead4; font-size: 11pt; font-weight: bold;")
            card.value_label.setStyleSheet("color: #14b8a6; font-size: 18pt; font-weight: bold;")
            # Make cards expandable
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
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
        
        buttons = [
            ("🔍 Quick Scan", "primary"),
            ("📋 Read DTCs", "primary"),
            ("📈 Live Data", "success"),
            ("⚙️ ECU Info", "success")
        ]
        
        for i, (text, style) in enumerate(buttons):
            btn = QPushButton(text)
            btn.setProperty("class", style)
            btn.setMinimumHeight(50)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            color = "#14b8a6" if "primary" in style else "#10b981"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {color}, stop:1 #0d9488);
                    border: none;
                    border-radius: 10px;
                    color: white;
                    font-weight: bold;
                    font-size: 11pt;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #0d9488, stop:1 #0f766e);
                }}
            """)
            row, col = i // 2, i % 2
            btn_layout.addWidget(btn, row, col)
        
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
        
        try:
            if SECURITY_MANAGER_AVAILABLE:
                user_info = security_manager.get_user_info()
            else:
                user_info = {"full_name": "Demo User", "security_level": "BASIC", "session_expiry": 0}
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
        
        # Add all sections to scrollable content
        content_layout.addWidget(stats_section)
        content_layout.addWidget(actions_frame)
        content_layout.addWidget(security_frame)
        content_layout.addStretch()
        
        # Set up scroll area
        scroll_area.setWidget(scroll_content)
        dashboard_layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(dashboard_tab, "📊 Dashboard")

    def create_diagnostics_tab(self):
        """Create diagnostics tab with scrollable content"""
        diagnostics_tab = QWidget()
        tab_layout = QVBoxLayout(diagnostics_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create scrollable content
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
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
        content_layout_frame = QVBoxLayout(content_frame)
        content_layout_frame.setContentsMargins(20, 20, 20, 20)
        
        placeholder = QLabel("🚧 Advanced diagnostics interface under development\n\n"
                            "This tab will include:\n"
                            "• Real-time DTC scanning\n"
                            "• Module identification\n"
                            "• Freeze frame data\n"
                            "• Advanced diagnostic protocols")
        placeholder.setStyleSheet("color: #a0d4cc; font-size: 12pt; line-height: 1.8;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        content_layout_frame.addWidget(placeholder)
        
        # Add content to scrollable area
        content_layout.addWidget(header_frame)
        content_layout.addWidget(content_frame)
        content_layout.addStretch()
        
        # Set up scroll area
        scroll_area.setWidget(scroll_content)
        tab_layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(diagnostics_tab, "🔍 Diagnostics")

    def create_live_data_tab(self):
        """Create live data tab with scrollable content"""
        live_data_tab = QWidget()
        tab_layout = QVBoxLayout(live_data_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create scrollable content
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
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
        content_layout_frame = QVBoxLayout(content_frame)
        content_layout_frame.setContentsMargins(20, 20, 20, 20)
        
        placeholder = QLabel("🚧 Live data monitoring interface under development")
        placeholder.setStyleSheet("color: #a0d4cc; font-size: 12pt;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        content_layout_frame.addWidget(placeholder)
        
        content_layout.addWidget(header_frame)
        content_layout.addWidget(content_frame)
        content_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        tab_layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(live_data_tab, "📈 Live Data")

    def create_special_functions_tab(self):
        """Create special functions tab with scrollable content"""
        functions_tab = QWidget()
        tab_layout = QVBoxLayout(functions_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create scrollable content
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
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
        
        header_label = QLabel("🔧 Special Functions")
        header_label.setStyleSheet("color: #14b8a6; font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(header_label)
        
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
        content_layout_frame = QVBoxLayout(content_frame)
        content_layout_frame.setContentsMargins(20, 20, 20, 20)
        
        placeholder = QLabel("🚧 Special functions interface under development")
        placeholder.setStyleSheet("color: #a0d4cc; font-size: 12pt;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        content_layout_frame.addWidget(placeholder)
        
        content_layout.addWidget(header_frame)
        content_layout.addWidget(content_frame)
        content_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        tab_layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(functions_tab, "🔧 Special Functions")

    def create_calibrations_resets_tab(self):
        """Create calibrations tab with scrollable content"""
        calib_tab = QWidget()
        tab_layout = QVBoxLayout(calib_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create scrollable content
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
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
        
        header_label = QLabel("⚙️ Calibrations & Resets")
        header_label.setStyleSheet("color: #14b8a6; font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(header_label)
        
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
        content_layout_frame = QVBoxLayout(content_frame)
        content_layout_frame.setContentsMargins(20, 20, 20, 20)
        
        placeholder = QLabel("🚧 Calibrations interface under development")
        placeholder.setStyleSheet("color: #a0d4cc; font-size: 12pt;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        content_layout_frame.addWidget(placeholder)
        
        content_layout.addWidget(header_frame)
        content_layout.addWidget(content_frame)
        content_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        tab_layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(calib_tab, "⚙️ Calibrations & Resets")

    def create_advanced_tab(self):
        """Create advanced tab with scrollable content"""
        advanced_tab = QWidget()
        tab_layout = QVBoxLayout(advanced_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create scrollable content
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
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
        
        header_label = QLabel("⚙️ Advanced Functions")
        header_label.setStyleSheet("color: #14b8a6; font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(header_label)
        
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
        content_layout_frame = QVBoxLayout(content_frame)
        content_layout_frame.setContentsMargins(20, 20, 20, 20)
        
        placeholder = QLabel("🚧 Advanced functions interface under development")
        placeholder.setStyleSheet("color: #a0d4cc; font-size: 12pt;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        content_layout_frame.addWidget(placeholder)
        
        content_layout.addWidget(header_frame)
        content_layout.addWidget(content_frame)
        content_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        tab_layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(advanced_tab, "⚙️ Advanced")
    
    def create_security_tab(self):
        """Create security tab with scrollable content"""
        security_tab = QWidget()
        tab_layout = QVBoxLayout(security_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create scrollable content
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
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
        
        try:
            if SECURITY_MANAGER_AVAILABLE:
                user_info = security_manager.get_user_info()
                status_text = f"Current User: {user_info.get('full_name', 'Demo User')}\nSecurity Level: {user_info.get('security_level', 'BASIC')}"
            else:
                status_text = "Current User: Demo User\nSecurity Level: BASIC"
        except:
            status_text = "Current User: Demo User\nSecurity Level: BASIC"
        
        self.security_status = QTextEdit()
        self.security_status.setPlainText(status_text)
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
        
        content_layout.addWidget(header_frame)
        content_layout.addWidget(status_frame)
        content_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        tab_layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(security_tab, "🔒 Security")
    
    def create_status_bar(self):
        """Create status bar"""
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
        self.update_timer.start(2000)
    
    def update_live_data(self):
        """Update live dashboard data"""
        import random
        
        self.system_health_card.update_value(random.randint(95, 99))
        self.connection_quality_card.update_value(random.randint(75, 95))
    
    def change_theme(self, theme_name):
        """Change theme using global style_manager"""
        try:
            style_manager.set_theme(theme_name)
            self.status_label.setText(f"✨ Theme changed to: {theme_name}")
        except Exception as e:
            logger.error(f"Theme change error: {e}")
            self.status_label.setText(f"⚠️ Theme change failed: {theme_name}")
    
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
                if SECURITY_MANAGER_AVAILABLE:
                    security_manager.logout()
            except:
                pass
            self.close()
    
    def closeEvent(self, event):
        """Secure cleanup on close"""
        try:
            if SECURITY_MANAGER_AVAILABLE:
                security_manager.logout()
        except:
            pass
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
        app.setApplicationVersion("2.1.0")
        app.setOrganizationName("SecureAutoClinic")

        # Set the app instance for the style manager
        style_manager.set_app(app)
    
        try:
            window = AutoDiagPro()
            window.show()  # Explicitly show the window
            sys.exit(app.exec())
        except Exception as e:
            logger.critical(f"Application crashed: {e}")
            QMessageBox.critical(None, "Fatal Error", f"Application crashed: {e}")
            sys.exit(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AutoDiagPro()
    window.show()
    sys.exit(app.exec())