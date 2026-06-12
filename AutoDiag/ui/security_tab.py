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

        _ui = getattr(self.parent, 'current_user_info', {}) or {}
        _name     = _ui.get('full_name') or _ui.get('username', 'Unknown')
        _tier     = _ui.get('security_level') or _ui.get('tier', 'BASIC')
        _username = _ui.get('username', 'unknown')
        _perms    = _ui.get('permissions', [])
        _access   = 'Full System Access' if 'user_management' in _perms else \
                    'Advanced Diagnostics' if 'full_diagnostics' in _perms else \
                    'Standard Diagnostics'

        user_info = QLabel(
            f"Current User: {_name}\n"
            f"Security Level: {_tier}\n"
            f"Access: {_access}\n"
            f"Session: Active | {_username}"
        )
        user_info.setProperty("class", "section-title")

        security_layout.addWidget(user_info)

        layout.addWidget(header)
        layout.addWidget(security_frame)
        layout.addStretch()

        return tab, "🔒 Security"