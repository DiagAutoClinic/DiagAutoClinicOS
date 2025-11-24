#!/usr/bin/env python3
"""
AutoDiag Pro - Professional Diagnostic Suite v3.1.2
Fixed & Optimized for 1366x768 + Launcher Integration
"""

import sys
import os
import logging
import traceback
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from shared.theme_constants import THEME

# ==============================
# Theme Colors
# ==============================
BG_MAIN   = THEME["bg_main"]
ACCENT    = THEME["accent"]
GLOW      = THEME["glow"]
TEXT_MAIN = THEME["text_main"]

# ==============================
# PyQt6 Imports (Fixed & Clean)
# ==============================
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QTabWidget, QComboBox, QDialog,
    QMessageBox, QTextBrowser, QGraphicsDropShadowEffect, QGridLayout
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor

# ==============================
# Custom Copyable MessageBox
# ==============================
class CopyableMessageBox(QDialog):
    def __init__(self, parent=None, title="Message", message="", icon=QMessageBox.Icon.Information):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(560, 360)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        text = QTextBrowser()
        text.setPlainText(message)
        text.setStyleSheet("""
            QTextBrowser {
                background: #0B2E2B;
                border: 2px solid #21F5C1;
                border-radius: 12px;
                padding: 14px;
                color: #E8FFFB;
                font-family: Consolas, monospace;
                font-size: 11pt;
            }
        """)
        text.setReadOnly(True)
        layout.addWidget(text)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        copy_btn = QPushButton("Copy Text")
        copy_btn.setStyleSheet("""
            QPushButton { background: #21F5C1; color: #002F2C; border-radius: 8px; padding: 8px 16px; font-weight: bold; }
            QPushButton:hover { background: #2AF5D1; }
        """)
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(message))
        btn_layout.addWidget(copy_btn)

        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("""
            QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #21F5C1,stop:1 #2AF5D1);
                          color: #002F2C; border-radius: 8px; padding: 8px 24px; font-weight: bold; }
            QPushButton:hover { background: #2AF5D1; }
        """)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)


# ==============================
# Try to import shared modules (non-critical)
# ==============================
try:
    from shared.style_manager import style_manager
    from shared.circular_gauge import CircularGauge
    from ui.login_dialog import LoginDialog
    STYLE_MANAGER_OK = True
except Exception as e:
    logging.warning(f"Shared modules not fully available: {e}")
    STYLE_MANAGER_OK = False
    style_manager = type("Dummy", (), {"set_app": lambda x: None, "set_theme": lambda x: None, "apply_theme": lambda: None})()

# ==============================
# Global Exception Handler
# ==============================
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    error = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logging.error("Uncaught exception:\n" + error)
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        dlg = CopyableMessageBox(None, "Critical Error", error, QMessageBox.Icon.Critical)
        dlg.exec()
    except:
        print(error)

sys.excepthook = handle_exception


# ==============================
# Main Window - Fixed for 1366x768
# ==============================
class AutoDiagPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoDiag Pro - Futuristic Diagnostics")
        self.setGeometry(50, 50, 1366, 768)  # Perfect match for launcher
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        # Center on screen
        screen = QApplication.primaryScreen()
        self.move(screen.availableGeometry().center() - self.rect().center())

        # Login
        if not self.secure_login():
            sys.exit(0)

        self.init_ui()

    def secure_login(self):
        try:
            dialog = LoginDialog(self)
            return dialog.exec() == QDialog.DialogCode.Accepted
        except:
            # Bypass login if module missing (demo mode)
            return True

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setFixedHeight(90)
        header.setStyleSheet(f"background: {BG_MAIN}; border-bottom: 3px solid {GLOW};")
        hbox = QHBoxLayout(header)
        hbox.setContentsMargins(24, 12, 24, 12)

        title = QLabel("AutoDiag Pro")
        title.setStyleSheet("color: #21F5C1; font-size: 32pt; font-weight: bold;")
        hbox.addWidget(title)
        hbox.addStretch()

        logout = QPushButton("Logout")
        logout.setStyleSheet("""
            background: #21F5C1; color: #002F2C; padding: 12px 28px;
            border-radius: 16px; font-weight: bold; font-size: 12pt;
        """)
        logout.clicked.connect(self.close)
        hbox.addWidget(logout)

        main_layout.addWidget(header)

        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: transparent; }
            QTabBar::tab { padding: 14px 32px; font-size: 13pt; border-radius: 12px; margin: 4px; }
            QTabBar::tab:selected { background: #21F5C1; color: #002F2C; }
        """)
        main_layout.addWidget(tabs)

        # Dashboard Tab
        dash = QWidget()
        dash_layout = QVBoxLayout(dash)
        dash_layout.setContentsMargins(30, 30, 30, 30)
        dash_layout.setSpacing(30)

        title_dash = QLabel("Welcome to AutoDiag Pro")
        title_dash.setStyleSheet("color: #21F5C1; font-size: 28pt; font-weight: bold;")
        title_dash.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dash_layout.addWidget(title_dash)

        subtitle = QLabel("Professional Multi-Brand Diagnostic Suite")
        subtitle.setStyleSheet("color: #9ED9CF; font-size: 16pt;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dash_layout.addWidget(subtitle)
        dash_layout.addStretch()

        # Quick Actions Grid
        grid = QGridLayout()
        grid.setSpacing(20)
        actions = [
            ("Quick Scan", lambda: self.show_info("Quick Scan", "Full vehicle health check initiated...")),
            ("Read DTCs", lambda: self.show_info("Fault Codes", "P0300 - Misfire Detected\nP0420 - Catalyst Below Threshold")),
            ("Live Data", lambda: self.show_info("Live Data", "Engine RPM: 750\nCoolant Temp: 92°C\nVehicle Speed: 0 km/h")),
            ("ECU Info", lambda: self.show_info("ECU Information", "Toyota Corolla 2024\nVIN: JTDEPRAE8LJ123456\nECU: Denso 89661-0ZXXX")),
        ]

        style_btn = """
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #21F5C1,stop:1 #2AF5D1);
                color: #002F2C; border-radius: 20px; font-weight: bold; font-size: 15pt;
                min-height: 80px; padding: 12px;
            }
            QPushButton:hover { background: #2AF5D1; }
            QPushButton:pressed { background: #134F4A; color: #21F5C1; }
        """

        for i, (text, func) in enumerate(actions):
            btn = QPushButton(text)
            btn.setStyleSheet(style_btn)
            btn.clicked.connect(func)
            grid.addWidget(btn, i // 2, i % 2)

        dash_layout.addLayout(grid)
        dash_layout.addStretch()
        tabs.addTab(dash, "Dashboard")

        # Status Bar
        status = QLabel("System Ready • Demo Mode Active")
        status.setStyleSheet("background: #0F3D3A; color: #21F5C1; padding: 12px; font-size: 11pt;")
        main_layout.addWidget(status)

        # Apply theme
        if STYLE_MANAGER_OK:
            style_manager.set_app(QApplication.instance())
            style_manager.set_theme("dacos_unified")
            style_manager.apply_theme()

    def show_info(self, title, content):
        CopyableMessageBox(self, title, content).exec()


# ==============================
# Main Entry Point - FIXED
# ==============================
if __name__ == "__main__":
    app = QApplication(sys.argv)  # Properly pass sys.argv
    app.setApplicationName("AutoDiag Pro")
    app.setApplicationVersion("3.1.2")
    app.setOrganizationName("DACOS")

    logging.basicConfig(level=logging.INFO)

    window = AutoDiagPro()
    window.show()
    sys.exit(app.exec())