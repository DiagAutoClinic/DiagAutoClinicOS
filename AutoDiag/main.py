#!/usr/bin/env python3
"""
AutoDiag Pro - Professional 25-Brand Diagnostic Suite v3.1.2
FUTURISTIC GLASSMORPHIC DESIGN - Theme synchronized with launcher.py and login dialog
"""

import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import os
import logging
from typing import Dict, List

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

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QComboBox, QTabWidget, QFrame, QGroupBox,
    QTableWidget, QTableWidgetItem, QProgressBar, QTextEdit, QLineEdit,
    QHeaderView, QMessageBox, QSplitter, QScrollArea, QCheckBox,
    QInputDialog, QDialog, QFormLayout, QFileDialog, QListWidget,
    QListWidgetItem, QStackedWidget, QGridLayout, QSizePolicy,
    QGraphicsDropShadowEffect  # ← MOVED HERE IN PyQt6
)
from PyQt6.QtCore import Qt, QTimer, QSettings, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPalette, QColor

# Import shared modules with fallbacks
SECURITY_MANAGER_AVAILABLE = False
try:
    from shared.style_manager import style_manager
    from shared.brand_database import get_brand_list
    from shared.dtc_database import DTCDatabase
    from shared.vin_decoder import VINDecoder
    from shared.device_handler import DeviceHandler
    from shared.security_manager import security_manager, SecurityLevel
    from shared.special_functions import special_functions_manager
    from shared.calibrations_reset import calibrations_resets_manager
    from shared.circular_gauge import CircularGauge, StatCard
    from ui.login_dialog import LoginDialog
    SECURITY_MANAGER_AVAILABLE = True
except ImportError as e:
    logging.error(f"Failed to import modules: {e}")
    SECURITY_MANAGER_AVAILABLE = False

class FallbackStyleManager:
    def set_theme(self, theme): pass
    def get_theme_names(self): return ["futuristic"]
    def set_security_level(self, level): pass

if not SECURITY_MANAGER_AVAILABLE:
    style_manager = FallbackStyleManager()

logger = logging.getLogger(__name__)

class AutoDiagPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoDiag Pro - Futuristic Diagnostics")
        self.setGeometry(100, 100, 1400, 900)

        if not self.secure_login():
            sys.exit(1)

        try:
            self.dtc_database = DTCDatabase()
            self.vin_decoder = VINDecoder()
        except:
            pass

        self.init_ui()

    def secure_login(self):
        dialog = LoginDialog(self)
        return dialog.exec() == QDialog.DialogCode.Accepted

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.create_header()
        layout.addWidget(self.header)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabWidget::pane { border: none; } QTabBar::tab { padding: 12px 24px; }")
        layout.addWidget(self.tabs)

        self.create_dashboard_tab()
        self.create_diagnostics_tab()

        self.status_label = QLabel("System Ready")
        self.status_label.setStyleSheet("color: #21F5C1; padding: 8px; background: #0F3D3A;")
        layout.addWidget(self.status_label)

        style_manager.set_app(QApplication.instance())
        style_manager.set_theme("dacos_unified")

    def create_header(self):
        self.header = QFrame()
        self.header.setFixedHeight(90)
        self.header.setStyleSheet(f"background: {BG_MAIN}; border-bottom: 2px solid #21F5C1;")

        hbox = QHBoxLayout(self.header)
        hbox.setContentsMargins(20, 10, 20, 10)

        title = QLabel("AutoDiag Pro")
        title.setStyleSheet("color: #21F5C1; font-size: 28pt; font-weight: bold;")
        hbox.addWidget(title)

        hbox.addStretch()

        vehicle = QComboBox()
        vehicle.addItems(["Toyota", "Honda", "Ford", "BMW", "Mercedes"])
        vehicle.setStyleSheet("padding: 8px; border-radius: 8px; background: #0F3D3A; color: white;")
        hbox.addWidget(QLabel("Vehicle:"))
        hbox.addWidget(vehicle)

        theme = QComboBox()
        theme.addItems(["futuristic", "neon_clinic", "dark"])
        hbox.addWidget(QLabel("Theme:"))
        hbox.addWidget(theme)

        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("background: #21F5C1; color: #002F2C; padding: 10px 20px; border-radius: 12px; font-weight: bold;")
        logout_btn.clicked.connect(self.secure_logout)
        hbox.addWidget(logout_btn)

    def create_dashboard_tab(self):
        dashboard_widget = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_widget)
        dashboard_layout.setContentsMargins(20, 20, 20, 20)
        dashboard_layout.setSpacing(25)

        # === STAT CARDS ROW ===
        stats_row = QHBoxLayout()
        stats_row.setSpacing(25)

        self.gauge_health = CircularGauge("System Health", "%", 0, 100)
        self.gauge_health.set_value(95)
        stats_row.addWidget(self.gauge_health)

        self.gauge_conn = CircularGauge("Connection", "%", 0, 100)
        self.gauge_conn.set_value(88)
        stats_row.addWidget(self.gauge_conn)

        self.gauge_faults = CircularGauge("Active Faults", "", 0, 50)
        self.gauge_faults.set_value(0)
        stats_row.addWidget(self.gauge_faults)

        self.gauge_security = CircularGauge("Security Level", "/5", 0, 5)
        self.gauge_security.set_value(5)
        stats_row.addWidget(self.gauge_security)

        dashboard_layout.addLayout(stats_row)

        # === QUICK ACTIONS – PERFECT LAUNCHER STYLE ===
        quick_frame = QFrame()
        quick_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0B2E2B, stop:0.5 #0F3D3A, stop:1 #0B2E2B);
                border-radius: 20px;
                margin: 20px;
            }
        """)

        quick_layout = QVBoxLayout(quick_frame)
        quick_layout.setSpacing(20)
        quick_layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Quick Actions")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #21F5C1; font-size: 20pt; font-weight: bold; background: transparent;")
        quick_layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(20)

        btn_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #21F5C1, stop:1 #2AF5D1);
                color: #002F2C;
                border-radius: 18px;
                font-weight: bold;
                font-size: 14pt;
                min-height: 70px;
                padding: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2AF5D1, stop:1 #30FFDD);
            }
            QPushButton:pressed {
                background: #134F4A;
                color: #21F5C1;
            }
        """

        actions = [
            ("Quick Scan", self.on_quick_scan),
            ("Read DTCs", self.on_read_dtcs),
            ("Live Data", self.on_live_data),
            ("ECU Info", self.on_ecu_info),
        ]

        for i, (text, callback) in enumerate(actions):
            btn = QPushButton(text)
            btn.setStyleSheet(btn_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(callback)
            grid.addWidget(btn, i // 2, i % 2)

        quick_layout.addLayout(grid)
        dashboard_layout.addWidget(quick_frame)
        dashboard_layout.addStretch()

        self.tabs.addTab(dashboard_widget, "Dashboard")

    def create_diagnostics_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Diagnostics Tab - Coming Soon"))
        self.tabs.addTab(widget, "Diagnostics")

    # ================================================================
    # QUICK ACTION CALLBACKS
    # ================================================================
    def on_quick_scan(self):
        self.status_label.setText("Quick Scan initiated...")
        QMessageBox.information(self, "Quick Scan", "Quick vehicle health scan started.\n\nNo faults detected (demo mode).")
        self.status_label.setText("Quick Scan complete – System healthy")

    def on_read_dtcs(self):
        self.status_label.setText("Reading DTCs...")
        dtcs = ["P0300 - Random/Multiple Cylinder Misfire", "P0420 - Catalyst Efficiency Low"]
        msg = "\n".join(dtcs) if dtcs else "No DTCs found"
        QMessageBox.warning(self, "DTCs Found", f"{len(dtcs)} fault(s):\n\n{msg}")
        self.status_label.setText(f"Read DTCs – {len(dtcs)} faults")

    def on_live_data(self):
        self.status_label.setText("Live Data active")
        QMessageBox.information(self, "Live Data", "Real-time sensor streaming active")

    def on_ecu_info(self):
        self.status_label.setText("ECU info retrieved")
        info = "TOYOTA COROLLA 2024\nVIN: JTDEPRAE8LJ123456\nECU: Denso 89661-0ZXXX"
        QMessageBox.information(self, "ECU Information", info)

    # ================================================================
    # PERFECT LOGOUT DIALOG – FIXED & GORGEOUS
    # ================================================================
    def secure_logout(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
        from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
        from PyQt6.QtGui import QColor

        dialog = QDialog(self)
        dialog.setWindowTitle(" ")
        dialog.setFixedSize(680, 420)
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

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

        shadow = QGraphicsDropShadowEffect(panel)
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(20)
        shadow.setColor(QColor(0, 255, 200, 180))
        panel.setGraphicsEffect(shadow)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(20)

        title = QLabel("Logout")
        title.setStyleSheet("color: #21F5C1; font-size: 28pt; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

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

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(25)
        no = QPushButton("Cancel")
        yes = QPushButton("Yes, Logout")
        yes.setFixedSize(160, 50)
        no.setFixedSize(160, 50)

        yes.setStyleSheet("""
            QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #21F5C1, stop:1 #2AF5D1); color: #0B2E2B; border-radius: 16px; font-weight: bold; font-size: 13pt; }
            QPushButton:hover { background: #2AF5D1; }
        """)
        no.setStyleSheet("""
            QPushButton { background: rgba(255,255,255,0.08); color: #9ED9CF; border: 2px solid #21F5C1; border-radius: 16px; font-weight: bold; font-size: 13pt; }
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

        yes.clicked.connect(lambda: [security_manager.logout() if SECURITY_MANAGER_AVAILABLE else None, self.close(), dialog.accept()])
        no.clicked.connect(dialog.reject)

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
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        app = QApplication(sys.argv)
        app.setApplicationName("AutoDiag Pro Futuristic")
        app.setApplicationVersion("3.1.2")
        style_manager.set_app(app)
        window = AutoDiagPro()
        window.show()
        sys.exit(app.exec())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AutoDiagPro()
    window.show()
    sys.exit(app.exec())