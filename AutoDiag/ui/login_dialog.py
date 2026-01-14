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
    QPushButton, QMessageBox, QFrame, QWidget, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon
import json
import os

try:
    from shared.theme_manager import get_theme_dict, get_stylesheet
    DACOS_THEME = get_theme_dict()
    DACOS_STYLESHEET = get_stylesheet()
except ImportError:
    # Fallback if theme not found
    DACOS_THEME = {
        "bg_main": "#ccfef4",      # Light Mint/Teal
        "bg_panel": "#b2dfdb",     # Slightly darker Teal
        "bg_card": "#FFFFFF",      # White cards
        "accent": "#00796B",       # Dark Teal (High Contrast)
        "text_main": "#000000",    # Pure Black
        "error": "#D32F2F",        # Red
        "glow": "#004D40"          # Dark Teal
    }
    DACOS_STYLESHEET = ""

logger = logging.getLogger(__name__)

class LoginDialog(QDialog):
    """Login dialog with database authentication"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DiagAutoClinicOS - Login")
        self.setModal(True)
        self.setMinimumSize(550, 550)
        self.resize(650, 650)

        # Set icon
        icon_path = os.path.join(parent_dir, 'assets', 'app_icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Security manager
        try:
            from shared.security_manager import security_manager
            self.user_db = security_manager
        except ImportError:
            logger.critical("Security manager not found. System integrity compromised.")
            # Fail loud - do not allow application to continue without security
            self.user_db = None
            # We can't show message box easily here if init fails, but we can try
            # or we rely on the check_login to fail. 
            # Better: Raise exception to crash early
            raise ImportError("Critical Security Subsystem Missing: shared.security_manager")

        self.auto_logged_in = False
        self.session_file = os.path.join(os.path.expanduser("~"), ".dacos", "session.json")
        self.init_ui()
        
        # Check for saved session after UI init
        QTimer.singleShot(100, self._check_saved_session)
    
    def init_ui(self):
        """Initialize the login dialog UI"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Explicit White Background for Dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                border: 2px solid #000000;
            }
        """)
        
        # Logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_paths = [
            os.path.join(parent_dir, 'assets', 'grok_dacos_logo_new2.jpg'),
            os.path.join(parent_dir, 'assets', 'logo_v2.png'),
            os.path.join(parent_dir, 'assets', 'dacos_logo.png')
        ]
        
        for path in logo_paths:
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    logo_label.setPixmap(scaled)
                    layout.addWidget(logo_label)
                    break

        # Title
        title = QLabel("AutoDiag Pro")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #000000;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Professional Diagnostic Suite")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont("Segoe UI", 12)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #000000;")
        layout.addWidget(subtitle)
        
        # Container for inputs
        input_container = QFrame()
        input_container.setObjectName("inputContainer")
        
        # Explicit White Background and Black Border for Login Container
        # Removed padding from stylesheet to let layout handle margins
        input_container.setStyleSheet("""
            QFrame#inputContainer {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 2px solid #000000;
            }
        """)
        input_layout = QVBoxLayout(input_container)
        input_layout.setSpacing(15)
        input_layout.setContentsMargins(30, 30, 30, 30)

        # Username
        username_label = QLabel("Username:")
        username_label.setStyleSheet(f"color: #000000; font-weight: bold;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setMinimumHeight(45)
        self.username_input.setStyleSheet(f"""
            QLineEdit {{
                padding-left: 10px;
                padding-right: 10px;
                border: 2px solid #000000;
                border-radius: 8px;
                background-color: #FFFFFF;
                color: #000000;
                font-size: 11pt;
            }}
            QLineEdit:focus {{
                border: 2px solid {DACOS_THEME['accent']};
                background-color: #FAFAFA;
            }}
        """)
        input_layout.addWidget(username_label)
        input_layout.addWidget(self.username_input)

        # Password
        password_label = QLabel("Password:")
        password_label.setStyleSheet(f"color: #000000; font-weight: bold;")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setMinimumHeight(45)
        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                padding-left: 10px;
                padding-right: 10px;
                border: 2px solid #000000;
                border-radius: 8px;
                background-color: #FFFFFF;
                color: #000000;
                font-size: 11pt;
            }}
            QLineEdit:focus {{
                border: 2px solid {DACOS_THEME['accent']};
                background-color: #FAFAFA;
            }}
        """)
        input_layout.addWidget(password_label)
        input_layout.addWidget(self.password_input)
        
        # Remember Me Checkbox
        self.remember_me = QCheckBox("Remember Me (Silent Login)")
        self.remember_me.setStyleSheet(f"color: #000000; font-weight: bold;")
        input_layout.addWidget(self.remember_me)
        
        layout.addWidget(input_container)

        # Info notice
        info_label = QLabel("Please log in to continue")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet(f"color: #000000; font-size: 10pt; font-weight: bold;")
        layout.addWidget(info_label)
        
        # Spacer
        layout.addStretch()
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        # Ensure consistent button styling if stylesheet is missing
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                color: #000000;
                border: 2px solid #000000;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #E0E0E0;
            }}
        """)
        button_layout.addWidget(cancel_btn)
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.check_login)
        login_btn.setDefault(True)
        login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #000000;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #333333;
            }}
        """)
        button_layout.addWidget(login_btn)
        
        layout.addLayout(button_layout)
        
        # Connect Enter key to login
        self.username_input.returnPressed.connect(self.check_login)
        self.password_input.returnPressed.connect(self.check_login)
        
        # Set focus to username
        self.username_input.setFocus()
    
    def _check_saved_session(self):
        """Check for saved session token"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    session = json.load(f)
                
                username = session.get('username')
                # In a real app, we'd use a secure token, not just the username.
                # For this Alpha, we'll verify the user exists in DB.
                if username and self.user_db:
                    user_info = self.user_db.get_user_info(username)
                    if user_info:
                        self.user_info = user_info
                        self.auto_logged_in = True
                        logger.info(f"Silent login successful for {username}")
                        self.accept()
        except Exception as e:
            logger.error(f"Error checking saved session: {e}")

    def check_login(self):
        """Check if login credentials are valid using database"""
        if not self.user_db:
             QMessageBox.critical(self, "System Error", "Security Manager not initialized. Cannot log in.")
             return

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
                        self._handle_successful_login(username)
                        logger.info(f"Login successful for user {username} after password change")
                        self.accept()
                    else:
                        QMessageBox.critical(self, "Login Failed", "Failed to retrieve user information after password change")
                # If password change was cancelled, don't proceed
            else:
                self.user_info = user_info
                self._handle_successful_login(username)
                logger.info(f"Login successful for user {username}")
                self.accept()
        else:
            # Show error message
            QMessageBox.warning(self, "Login Failed", message)

            # Clear password field
            self.password_input.clear()
            self.password_input.setFocus()

    def _handle_successful_login(self, username):
        """Handle post-login actions like saving session"""
        if self.remember_me.isChecked():
            try:
                os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
                with open(self.session_file, 'w') as f:
                    json.dump({'username': username}, f)
            except Exception as e:
                logger.error(f"Failed to save session: {e}")
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)