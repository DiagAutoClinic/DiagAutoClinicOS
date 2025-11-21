#!/usr/bin/env python3
# AGENTS: DO NOT TOUCH THIS FILE - THEME IS CENTRALIZED IN shared/theme_constants.py
# ANY CHANGES HERE WILL BE REVERTED
"""
Login Dialog Module for AutoDiag Pro
"""

import sys
import os

# Add project root to Python path to enable imports from shared directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Import shared modules
try:
    from shared.security_manager import security_manager
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

from shared.style_manager import style_manager


class LoginDialog(QDialog):
    """Secure login dialog with futuristic styling"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NeonBackground")
        self.setWindowTitle("AutoDiag Pro - Secure Login")
        self.setModal(True)
        self.setFixedSize(480, 400)

        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title with futuristic styling
        title = QLabel("🔒 AutoDiag Pro Login")
        title.setProperty("class", "hero-title")
        title_font = QFont("Segoe UI", 20, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Secure Access Required")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setProperty("class", "subtitle")

        # Form with glassmorphic styling
        form_widget = QWidget()
        form_widget.setProperty("class", "glass-card")
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(20)
        form_layout.setHorizontalSpacing(15)

        # Form labels with specific styling
        username_label = QLabel("Username:")
        username_label.setProperty("class", "form-label")
        password_label = QLabel("Password:")
        password_label.setProperty("class", "form-label")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setMinimumHeight(45)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(45)
        self.password_input.returnPressed.connect(self.attempt_login)

        # Add rows with proper spacing
        form_layout.addRow(username_label, self.username_input)
        form_layout.addRow(password_label, self.password_input)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        login_btn = QPushButton("Login")
        login_btn.setProperty("class", "primary")
        login_btn.setMinimumHeight(50)
        login_btn.clicked.connect(self.attempt_login)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "danger")
        cancel_btn.setMinimumHeight(50)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(login_btn)
        button_layout.addWidget(cancel_btn)

        # Status
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setProperty("class", "status-label")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(form_widget)
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # Apply launcher theme
        launcher_stylesheet = self.get_launcher_theme()
        self.setStyleSheet(launcher_stylesheet)

    def attempt_login(self):
        """Attempt user login"""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.status_label.setText("⚠️ Username and password required")
            return

        if SECURITY_AVAILABLE:
            success, message = security_manager.authenticate_user(username, password)
        else:
            # Fallback for demo mode
            success = True
            message = "Login successful (demo mode)"

        if success:
            self.accept()
        else:
            self.status_label.setText(f"❌ {message}")

    def get_launcher_theme(self):
        from shared.theme_constants import THEME
        t = THEME
        return f"""
        QDialog {{ background-color: {t['bg_main']}; border: 2px solid {t['glow']}; border-radius: 15px; }}
        QLabel {{ color: {t['text_main']}; background: transparent; }}
        QLabel[objectName="hero-title"] {{ color: {t['glow']}; font-size: 26pt; font-weight: bold; }}
        .subtitle {{ color: {t['text_muted']}; font-size: 16px; }}
        QWidget[class="glass-card"] {{ background-color: {t['bg_card']}; border: 1px solid {t['glow']}; border-radius: 12px; }}
        QLineEdit {{ background-color: {t['bg_panel']}; border: 2px solid {t['glow']}; color: {t['text_main']}; }}
        QLineEdit:focus {{ border: 2px solid {t['accent']}; background-color: {t['bg_card']}; }}
        QPushButton[class="primary"] {{ background-color: {t['accent']}; color: #002F2C; }}
        QPushButton[class="primary"]:hover {{ background-color: #1AE5B1; }}
        """