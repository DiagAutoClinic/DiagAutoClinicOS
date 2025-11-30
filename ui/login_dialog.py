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

from PyQt6.QtWidgets import QApplication,QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QWidget 
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
        
        # Calculate responsive size based on screen dimensions
        self.setup_responsive_geometry()

        # Setup layout with responsive spacing
        layout = QVBoxLayout()
        # Use responsive scale for spacing
        scale = getattr(self, '_responsive_scale', 1.0)
        layout.setSpacing(int(5 * scale))
        layout.setContentsMargins(int(40 * scale), int(40 * scale), int(40 * scale), int(40 * scale))

        # Title with futuristic styling
        title = QLabel("🔒 AutoDiag Pro Login")
        title.setProperty("class", "hero-title")
        title_font = QFont("Segoe UI", max(16, int(20 * scale)), QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)

        subtitle = QLabel("Secure Access Required")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setProperty("class", "subtitle")

        # Form with glassmorphic styling
        form_widget = QWidget()
        form_widget.setProperty("class", "glass-card")
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(int(20 * scale))
        form_layout.setHorizontalSpacing(int(25 * scale))

        # Form labels with specific styling
        username_label = QLabel("Username:")
        username_label.setProperty("class", "form-label")
        password_label = QLabel("Password:")
        password_label.setProperty("class", "form-label")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setMinimumHeight(max(30, int(30 * scale)))

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(max(30, int(30 * scale)))
        self.password_input.returnPressed.connect(self.attempt_login)

        # Add rows with proper spacing
        form_layout.addRow(username_label, self.username_input)
        form_layout.addRow(password_label, self.password_input)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(int(10 * scale))

        login_btn = QPushButton("Login")
        login_btn.setProperty("class", "primary")
        login_btn.setMinimumHeight(max(30, int(50 * scale)))
        login_btn.clicked.connect(self.attempt_login)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "danger")
        cancel_btn.setMinimumHeight(max(30, int(50 * scale)))
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(login_btn)
        button_layout.addWidget(cancel_btn)

        # Status
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setProperty("class", "status-label")

        # Assemble layout
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(form_widget)
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # Apply centralized theme
        style_manager.set_app(QApplication.instance())
        style_manager.ensure_theme()

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

    def setup_responsive_geometry(self):
        """Calculate and set responsive geometry based on screen size"""
        # Get screen information
        screen = QApplication.primaryScreen()
        available_size = screen.availableSize()
        screen_size = screen.size()
        device_pixel_ratio = screen.devicePixelRatio()
        
        # Determine base screen dimensions (normalize for very large monitors)
        base_width = min(available_size.width(), 1920)
        base_height = min(available_size.height(), 1080)
        
        # Calculate responsive dimensions with better constraints
        # Use proportional sizing with safe minimums and maximums
        if base_width < 768:  # Mobile/small screens
            dialog_width = int(base_width * 0.9)
            dialog_height = int(base_height * 0.8)
        elif base_width < 1366:  # Standard laptop
            dialog_width = int(base_width * 0.5)
            dialog_height = int(base_height * 0.6)
        else:  # Large monitors
            dialog_width = int(base_width * 0.35)
            dialog_height = int(base_height * 0.5)
        
        # Apply safe constraints
        dialog_width = max(min(dialog_width, 650), 380)
        dialog_height = max(min(dialog_height, 650), 380)
        
        # Center the dialog on screen
        center_x = (screen_size.width() - dialog_width) // 2
        center_y = (screen_size.height() - dialog_height) // 2
        
        # Set geometry with responsive constraints
        self.setGeometry(center_x, center_y, dialog_width, dialog_height)
        self.setMinimumSize(350, 280)
        self.setMaximumSize(800, 700)
        
        # Apply adaptive scaling for high DPI displays
        if device_pixel_ratio > 1.5:
            scaling_factor = min(device_pixel_ratio * 0.1, 0.2)
            current_geometry = self.geometry()
            new_width = int(current_geometry.width() * (1 + scaling_factor))
            new_height = int(current_geometry.height() * (1 + scaling_factor))
            
            # Ensure we don't exceed maximum size
            new_width = min(new_width, 800)
            new_height = min(new_height, 700)
            
            self.setGeometry(center_x, center_y, new_width, new_height)
        
        # Store responsive values for layout adjustments
        self._responsive_scale = min(dialog_width / 500.0, 1.2)  # Base scale from 500px width
