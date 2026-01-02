#!/usr/bin/env python3
"""
Login Dialog for DiagAutoClinicOS
Integrated with user database system
"""

import logging
import sys
import os

# Ensure shared modules can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QIcon

try:
    from shared.themes.dacos_theme import DACOS_THEME, DACOS_STYLESHEET
except ImportError:
    # Fallback if theme not found
    DACOS_THEME = {
        "bg_main": "#0A1A1A",
        "bg_panel": "#0D2323",
        "accent": "#21F5C1",
        "text_main": "#E8F4F2",
        "error": "#FF4D4D"
    }
    DACOS_STYLESHEET = ""

logger = logging.getLogger(__name__)

class LoginDialog(QDialog):
    """Login dialog with database authentication"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DiagAutoClinicOS - Login")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.resize(550, 450)
        
        # Apply DACOS Theme
        self.setStyleSheet(DACOS_STYLESHEET)

        # Security manager
        try:
            from shared.security_manager import security_manager
            self.user_db = security_manager
        except ImportError:
            logger.warning("Security manager not found, using dummy auth")
            self.user_db = None

        self.init_ui()
    
    def init_ui(self):
        """Initialize the login dialog UI"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("AutoDiag Pro")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {DACOS_THEME['accent']};")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Professional Diagnostic Suite")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont("Segoe UI", 12)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet(f"color: {DACOS_THEME['text_main']};")
        layout.addWidget(subtitle)
        
        # Container for inputs
        input_container = QFrame()
        input_container.setObjectName("inputContainer")
        input_container.setStyleSheet(f"""
            QFrame#inputContainer {{
                background-color: {DACOS_THEME['bg_panel']};
                border-radius: 12px;
                padding: 20px;
                border: 1px solid rgba(33, 245, 193, 0.2);
            }}
        """)
        input_layout = QVBoxLayout(input_container)
        input_layout.setSpacing(15)

        # Username
        username_label = QLabel("Username:")
        username_label.setStyleSheet(f"color: {DACOS_THEME['text_main']}; font-weight: bold;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setMinimumHeight(40)
        self.username_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {DACOS_THEME['accent']};
                border-radius: 8px;
                background-color: {DACOS_THEME['bg_main']};
                color: {DACOS_THEME['text_main']};
                font-size: 11pt;
            }}
            QLineEdit:focus {{
                border-color: {DACOS_THEME['glow']};
                background-color: {DACOS_THEME['bg_panel']};
            }}
        """)
        input_layout.addWidget(username_label)
        input_layout.addWidget(self.username_input)

        # Password
        password_label = QLabel("Password:")
        password_label.setStyleSheet(f"color: {DACOS_THEME['text_main']}; font-weight: bold;")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setMinimumHeight(40)
        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 2px solid {DACOS_THEME['accent']};
                border-radius: 8px;
                background-color: {DACOS_THEME['bg_main']};
                color: {DACOS_THEME['text_main']};
                font-size: 11pt;
            }}
            QLineEdit:focus {{
                border-color: {DACOS_THEME['glow']};
                background-color: {DACOS_THEME['bg_panel']};
            }}
        """)
        input_layout.addWidget(password_label)
        input_layout.addWidget(self.password_input)
        
        layout.addWidget(input_container)

        # Info notice
        info_label = QLabel("Super User: superuser\nDefault password must be changed on first login")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #21F5C1; font-size: 10pt; font-weight: bold;")
        layout.addWidget(info_label)
        
        # Spacer
        layout.addStretch()
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.check_login)
        login_btn.setDefault(True)
        button_layout.addWidget(login_btn)
        
        layout.addLayout(button_layout)
        
        # Connect Enter key to login
        self.username_input.returnPressed.connect(self.check_login)
        self.password_input.returnPressed.connect(self.check_login)
        
        # Set focus to username
        self.username_input.setFocus()
    
    def check_login(self):
        """Check if login credentials are valid using database"""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
            return

        # Authenticate user
        success, message, user_info = self.user_db.authenticate_user(username, password)

        if success:
            if "Password change required" in message:
                # Show password change dialog
                from AutoDiag.ui.password_change_dialog import PasswordChangeDialog
                password_dialog = PasswordChangeDialog(username, self)
                if password_dialog.exec() == QDialog.DialogCode.Accepted:
                    # Password changed successfully, get updated user info
                    user_info = self.user_db.get_user_info(username)
                    if user_info:
                        self.user_info = user_info
                        logger.info(f"Login successful for user {username} after password change")
                        self.accept()
                    else:
                        QMessageBox.critical(self, "Login Failed", "Failed to retrieve user information after password change")
                # If password change was cancelled, don't proceed
            else:
                self.user_info = user_info
                logger.info(f"Login successful for user {username}")
                self.accept()
        else:
            # Show error message
            QMessageBox.warning(self, "Login Failed", message)

            # Clear password field
            self.password_input.clear()
            self.password_input.setFocus()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)