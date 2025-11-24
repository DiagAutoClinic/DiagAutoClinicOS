#!/usr/bin/env python3
"""
AutoDiag Pro - Professional 25-Brand Diagnostic Suite v3.1.2
FUTURISTIC GLASSMORPHIC DESIGN - Theme synchronized with launcher.py and login dialog
"""

import sys
from pathlib import Path
# Always add the project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]   # two levels up from current file
sys.path.insert(0, str(PROJECT_ROOT))
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

from shared.theme_constants import THEME

# ==============================
# Theme Configuration
# ==============================
BG_MAIN   = THEME["bg_main"]
BG_PANEL  = THEME["bg_panel"]
BG_CARD   = THEME["bg_card"]
ACCENT    = THEME["accent"]
GLOW      = THEME["glow"]
TEXT_MAIN = THEME["text_main"]
TEXT_MUTED= THEME["text_muted"]
ERROR     = THEME["error"]

FONT_TITLE = ("Segoe UI", 26, "bold")
FONT_SUB = ("Segoe UI", 12)
FONT_BTN = ("Segoe UI", 11, "bold")
FONT_SMALL = ("Segoe UI", 10)

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
# ─────── Fix Python path so "shared" and "ui" are always found ───────
current_file = os.path.abspath(__file__)                     # main.py
autodiag_dir = os.path.dirname(current_file)                 # .../AutoDiag
project_root = os.path.dirname(autodiag_dir)                 # project root

shared_path = os.path.join(project_root, "shared")
ui_path     = os.path.join(project_root, "ui")

for p in [shared_path, ui_path, project_root]:
    if p not in sys.path:
        sys.path.insert(0, p)
# ─────────────────────────────────────────────────────────────────────
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
        """Initialize the full futuristic UI"""
        self.setWindowTitle("AutoDiag Pro - Futuristic Diagnostics")
        self.setMinimumSize(1280, 600)
        self.resize(1366, 768)

        # Apply DACOS teal glowing theme
        self.apply_global_theme()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main vertical layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # User header at the top
        self.create_user_header(main_layout)

        # Tab Widget 
        self.tab_widget = QTabWidget()
        self.tab_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.tab_widget, stretch=1)

        # Now create all tabs
        self.create_dashboard_tab()
        self.create_diagnostics_tab()
        self.create_live_data_tab()
        self.create_special_functions_tab()
        self.create_calibrations_resets_tab()
        self.create_advanced_tab()
        self.create_security_tab()

        # Status bar at bottom
        self.create_status_bar()

        self.show()
        
    def apply_global_theme(self):
        """Apply the DACOS Unified Theme - Load from QSS file"""
        try:
            # Load the DACOS unified theme from QSS file
            dacos_theme_path = PROJECT_ROOT / "shared" / "themes" / "dacos.qss"
            
            if dacos_theme_path.exists():
                with open(dacos_theme_path, 'r', encoding='utf-8') as f:
                    dacos_stylesheet = f.read()
                
                # Apply the DACOS stylesheet
                self.setStyleSheet(dacos_stylesheet)
                logger.info("DACOS Unified theme loaded successfully")
            else:
                logger.warning(f"DACOS theme file not found at {dacos_theme_path}, falling back to default theme")
                self.apply_fallback_theme()
                
        except Exception as e:
            logger.error(f"Failed to load DACOS theme: {e}")
            self.apply_fallback_theme()
    
    def apply_fallback_theme(self):
        """Fallback theme if DACOS QSS fails to load"""
        t = THEME
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {t['bg_main']},
                    stop:0.5 {t['bg_panel']},
                    stop:1 {t['bg_card']});
                color: {t['text_main']};
                font-family: "Segoe UI", sans-serif;
            }}

            QTabWidget::pane {{
                border: 1px solid rgba(33, 245, 193, 0.15);
                background: {t['bg_panel']};
                border-radius: 16px;
                margin-top: 6px;
            }}

            QTabBar::tab {{
                background: {t['bg_card']};
                color: {t['text_muted']};
                padding: 14px 28px;
                min-width: 140px;
                border-top-left-radius: 14px;
                border-top-right-radius: 14px;
                font-weight: 600;
                margin-right: 4px;
            }}

            QTabBar::tab:selected {{
                background: {t['accent']};
                color: #0B2E2B;
                font-weight: bold;
            }}

            QTabBar::tab:hover:!selected {{
                background: rgba(33, 245, 193, 0.25);
                color: {t['glow']};
            }}

            /* Glassmorphic cards – used everywhere */
            QFrame[class="glass-card"] {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(19, 79, 74, 0.92),
                    stop:1 rgba(11, 46, 43, 0.92));
                border: 1.5px solid rgba(42, 245, 209, 0.5);
                border-radius: 18px;
            }}

            QFrame[class="glass-card"]:hover {{
                border: 1.5px solid {t['glow']};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(25, 95, 90, 0.95),
                    stop:1 rgba(15, 55, 50, 0.95));
            }}

            QLabel {{
                color: {t['text_main']};
                background: transparent;
            }}

            QPushButton {{
                background: rgba(33, 245, 193, 0.15);
                color: {t['text_main']};
                border: 1.5px solid {t['accent']};
                border-radius: 12px;
                padding: 12px 24px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background: rgba(33, 245, 193, 0.35);
                border-color: {t['glow']};
            }}

            QScrollBar:vertical, QScrollBar:horizontal {{
                background: rgba(11, 46, 43, 0.4);
                width: 14px;
                border-radius: 7px;
            }}

            QScrollBar::handle {{
                background: {t['accent']};
                border-radius: 7px;
                min-height: 30px;
            }}

            QScrollBar::handle:hover {{ background: {t['glow']}; }}
        """)
    
    def create_user_header(self, layout):
        """Create FUTURISTIC header with user information"""
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_frame.setStyleSheet(f"""
            QFrame {{ background: qlinear-gradient(x1:0, y: 0, x2: 1, y: 0,
            stop: 0 #0F3D3A, stop: 1 #134F4A, stop: 0.6 #21F5C1, stop: 0.5 #0B2E2B;
            border-bottom: 2px solid #21F5C1;
            border-radius: 16px;
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
        logout_btn.setMinimumHeight(45)
        logout_btn.setMaximumWidth(85)
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
            if width < 768:
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
        """Ultra-sexy animated dashboard with glowing circular gauges"""
        from shared.circular_gauge import CircularGauge, StatCard, StatusIndicator
        import random

        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)
        self.tab_widget.addTab(scroll, "Dashboard")

        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 30, 20, 30)

        # === TOP ROW: 4 BIG GLOWING GAUGES ===
        top_grid = QGridLayout()
        top_grid.setSpacing(25)

        self.system_health_card = StatCard("System Health", 98, unit="%", max_value=100)
        self.connection_card     = StatCard("Connection Quality", 85, unit="%", max_value=100)
        self.dtc_card            = StatCard("Active DTCs", 0, unit="", max_value=50)
        self.security_card       = StatCard("Security Level", 5, unit="/5", max_value=5)

        # Make them huge and sexy
        for card in [self.system_health_card, self.connection_card, self.dtc_card, self.security_card]:
            card.setMinimumSize(260, 280)
            card.gauge.setMinimumSize(200, 200)

        top_grid.addWidget(self.system_health_card, 0, 0)
        top_grid.addWidget(self.connection_card,     0, 1)
        top_grid.addWidget(self.dtc_card,            0, 2)
        top_grid.addWidget(self.security_card,       0, 3)

        # === QUICK ACTIONS ROW ===
        actions_frame = QFrame()
        actions_frame.setProperty("class", "glass-card")
        actions_layout = QGridLayout(actions_frame)
        actions_layout.setSpacing(15)

        btn_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1F5E5A, stop:1 #134F4A);
                color: #E8FFFB;
                border: 2px solid #21F5C1;
                border-radius: 16px;
                padding: 20px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2AF5D1, stop:1 #21F5C1);
                border: 2px solid #2AF5D1;
                color: #0B2E2B;
            }
        """

        btn1 = QPushButton("Quick Scan")
        btn2 = QPushButton("Read DTCs")
        btn3 = QPushButton("Live Data")
        btn4 = QPushButton("ECU Info")

        for btn in (btn1, btn2, btn3, btn4):
            btn.setStyleSheet(btn_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        actions_layout.addWidget(btn1, 0, 0)
        actions_layout.addWidget(btn2, 0, 1)
        actions_layout.addWidget(btn3, 1, 0)
        actions_layout.addWidget(btn4, 1, 1)

        # Title for actions
        actions_title = QLabel("Quick Actions")
        actions_title.setStyleSheet("font-size: 18pt; color: #21F5C1; font-weight: bold; padding: 10px;")
        actions_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # === STATUS INDICATORS (bottom row) ===
        status_layout = QHBoxLayout()
        status_layout.setSpacing(40)
        status_layout.addStretch()

        self.status_obd = StatusIndicator("ready")
        self.status_j2534 = StatusIndicator("success")
        self.status_security = StatusIndicator("ready")

        status_layout.addWidget(QLabel("OBD-II"))
        status_layout.addWidget(self.status_obd)
        status_layout.addSpacing(40)
        status_layout.addWidget(QLabel("J2534"))
        status_layout.addWidget(self.status_j2534)
        status_layout.addSpacing(40)
        status_layout.addWidget(QLabel("Security"))
        status_layout.addWidget(self.status_security)
        status_layout.addStretch()

        # === ASSEMBLE EVERYTHING ===
        layout.addLayout(top_grid)
        layout.addWidget(actions_title)
        layout.addWidget(actions_frame)
        layout.addSpacing(20)
        layout.addLayout(status_layout)
        layout.addStretch()

        # === LIVE RANDOM UPDATES (for demo) ===
        self.dashboard_timer = QTimer()
        self.dashboard_timer.timeout.connect(lambda: [
            self.system_health_card.update_value(random.randint(94, 99)),
            self.connection_card.update_value(random.randint(72, 98)),
            self.dtc_card.update_value(random.randint(0, 3)),
        ])
        self.dashboard_timer.start(3000)

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
        """Create live data streaming tab"""
        live_data_tab = QWidget()
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Title
        title = QLabel("📊 Live Data Streaming")
        title.setStyleSheet(f"color: {TEXT_MAIN}; font-size: 18pt; font-weight: bold; margin-bottom: 15px;")
        scroll_layout.addWidget(title)
        
        # Connection controls
        connection_group = QGroupBox("Data Stream Controls")
        connection_layout = QHBoxLayout(connection_group)
        
        start_button = QPushButton("▶ Start Stream")
        stop_button = QPushButton("⏹ Stop Stream")
        refresh_button = QPushButton("🔄 Refresh")
        
        connection_layout.addWidget(start_button)
        connection_layout.addWidget(stop_button)
        connection_layout.addWidget(refresh_button)
        
        scroll_layout.addWidget(connection_group)
        
        # Live data display
        data_group = QGroupBox("Live Data Parameters")
        data_layout = QVBoxLayout(data_group)
        
        # Create a table for live data
        self.live_data_table = QTableWidget(0, 3)
        self.live_data_table.setHorizontalHeaderLabels(["Parameter", "Value", "Unit"])
        self.live_data_table.horizontalHeader().setStretchLastSection(True)
        
        data_layout.addWidget(self.live_data_table)
        
        scroll_layout.addWidget(data_group)
        
        # Add some sample data
        sample_data = [
            ("Engine RPM", "2500", "RPM"),
            ("Vehicle Speed", "65", "km/h"),
            ("Coolant Temperature", "90", "°C"),
            ("Throttle Position", "45", "%"),
            ("Fuel Level", "75", "%")
        ]
        
        for param, value, unit in sample_data:
            row_position = self.live_data_table.rowCount()
            self.live_data_table.insertRow(row_position)
            self.live_data_table.setItem(row_position, 0, QTableWidgetItem(param))
            self.live_data_table.setItem(row_position, 1, QTableWidgetItem(value))
            self.live_data_table.setItem(row_position, 2, QTableWidgetItem(unit))
        
        scroll_area.setWidget(scroll_content)
        live_data_tab.setLayout(QVBoxLayout())
        live_data_tab.layout().addWidget(scroll_area)
        
        self.tab_widget.addTab(live_data_tab, "📊 Live Data")

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
        """Perfect glassmorphic logout dialog – NO Qt warnings, pure beauty"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
        from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
        from PyQt6.QtGui import QColor

        dialog = QDialog(self)
        dialog.setWindowTitle(" ")
        dialog.setFixedSize(680, 420)
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Main glass panel
        panel = QFrame(dialog)
        panel.setFixedSize(680, 420)
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(19, 79, 74, 245),
                    stop:1 rgba(11, 46, 43, 245));
                border: 2.5px solid #21F5C1;
                border-radius: 24px;
            }
        """)

        # Real drop shadow using Qt (this works!)
        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(40)
        shadow.setXOffset = 0
        shadow.setYOffset = 20
        shadow.setColor(QColor(0, 255, 200, 180))
        panel.setGraphicsEffect(shadow)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(20)

        # Title
        title = QLabel("Logout")
        title.setStyleSheet("color: #21F5C1; font-size: 28pt; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Message - CLEAN & FIXED
        user_info = security_manager.get_user_info() if SECURITY_MANAGER_AVAILABLE else {"full_name": "User", "security_level": "BASIC"}
        
        message = QLabel()
        message.setTextFormat(Qt.TextFormat.RichText)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setWordWrap(True)
        message.setStyleSheet("color: #E8FFFB; font-size: 15pt; background: transparent;")
        
        message.setText(
            "<div style='line-height: 1.6;'>"
            "Are you sure you want to log out?<br><br>"
            f"<b style='font-size: 18pt;'>{user_info.get('full_name', 'User')}</b><br>"
            f"Security Level: <span style='color:#21F5C1; font-weight:bold;'>{user_info.get('security_level', 'BASIC')}</span><br><br>"
            "<small>All unsaved data will be lost.</small>"
            "</div>"
        )

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(25)

        yes = QPushButton("Yes, Logout")
        no  = QPushButton("Cancel")

        yes.setFixedSize(160, 50)
        no.setFixedSize(160, 50)

        yes.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #21F5C1, stop:1 #2AF5D1);
                color: #0B2E2B;
                border-radius: 16px;
                font-weight: bold;
                font-size: 13pt;
            }
            QPushButton:hover { background: #2AF5D1; }
        """)

        no.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.08);
                color: #9ED9CF;
                border: 2px solid #21F5C1;
                border-radius: 16px;
                font-weight: bold;
                font-size: 13pt;
            }
            QPushButton:hover { background: rgba(33,245,193,0.25); color: #E8FFFB; }
        """)

        btn_layout.addWidget(no)
        btn_layout.addWidget(yes)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(message)
        layout.addStretch()
        layout.addLayout(btn_layout)
        layout.addStretch()

        # Connect buttons
        yes.clicked.connect(lambda: [security_manager.logout() if SECURITY_MANAGER_AVAILABLE else None, self.close(), dialog.accept()])
        no.clicked.connect(dialog.reject)

        # Fade-in animation because why not
        dialog.setWindowOpacity(0)
        anim = QPropertyAnimation(dialog, b"windowOpacity")
        anim.setDuration(300)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        dialog.show()
        anim.start()

        dialog.exec()

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
    app.setApplicationVersion("3.1.2")
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