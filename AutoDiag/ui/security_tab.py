#!/usr/bin/env python3
"""
AutoDiag Pro - Security Tab
Separate tab implementation for easier customization
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel
from PyQt6.QtCore import Qt

class SecurityTab:
    def __init__(self, parent_window):
        self.parent = parent_window

    def create_tab(self):
        """Create the security tab and return the widget"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        header = QLabel("🔒 Security & Access")
        header.setProperty("class", "tab-title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        security_frame = QFrame()
        security_frame.setProperty("class", "glass-card")
        security_layout = QVBoxLayout(security_frame)

        user_info = QLabel("Current User: Demo Technician\n"
                          "Security Level: BASIC\n"
                          "Access: Standard Diagnostics\n"
                          "Session: Active")
        user_info.setProperty("class", "section-title")

        security_layout.addWidget(user_info)

        layout.addWidget(header)
        layout.addWidget(security_frame)
        layout.addStretch()

        return tab, "🔒 Security"