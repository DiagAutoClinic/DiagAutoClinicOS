#!/usr/bin/env python3
"""
Login Dialog for DiagAutoClinicOS
Integrated with user database system
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QIcon

logger = logging.getLogger(__name__)

class LoginDialog(QDialog):
    """Login dialog with database authentication"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DiagAutoClinicOS - Login")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.resize(550, 450)

        # Security manager
        from shared.security_manager import security_manager
        self.user_db = security_manager

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
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Professional Diagnostic Suite")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont("Segoe UI", 12)
        subtitle.setFont(subtitle_font)
        layout.addWidget(subtitle)
        
        # Username
        username_layout = QVBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setMinimumHeight(35)
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #21F5C1;
                border-radius: 8px;
                background-color: #0D2323;
                color: #E8F4F2;
                font-size: 12pt;
            }
            QLineEdit:focus {
                border-color: #2AF5D1;
            }
        """)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        # Password
        password_layout = QVBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setMinimumHeight(35)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #21F5C1;
                border-radius: 8px;
                background-color: #0D2323;
                color: #E8F4F2;
                font-size: 12pt;
            }
            QLineEdit:focus {
                border-color: #2AF5D1;
            }
        """)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

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