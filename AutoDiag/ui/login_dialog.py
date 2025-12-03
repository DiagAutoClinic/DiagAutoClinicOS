#!/usr/bin/env python3
"""
Simple Login Dialog for AutoDiag Pro
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
    """Simple login dialog with demo credentials"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AutoDiag Pro - Login")
        self.setModal(True)
        self.setMinimumSize(400, 300)
        self.resize(450, 350)
        
        # Demo credentials (for real implementation, use secure authentication)
        self.valid_username = "admin"
        self.valid_password = "password"
        
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
        self.username_input.setText("admin")  # Default for demo
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)
        
        # Password
        password_layout = QVBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setText("password")  # Default for demo
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # Demo notice
        demo_label = QLabel("Demo Mode: admin / password")
        demo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        demo_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(demo_label)
        
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
        """Check if login credentials are valid"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Simple validation for demo
        if username == self.valid_username and password == self.valid_password:
            logger.info("Login successful")
            self.accept()
        else:
            # Show error message
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Login Failed")
            msg.setText("Invalid username or password")
            msg.setInformativeText("Please check your credentials and try again.\n\nDemo: admin / password")
            msg.exec()
            
            # Clear password field
            self.password_input.clear()
            self.password_input.setFocus()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)