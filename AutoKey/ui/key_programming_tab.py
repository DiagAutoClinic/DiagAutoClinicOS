#!/usr/bin/env python3
"""
AutoKey Pro - Key Programming Tab
Separate tab implementation for key programming functionality
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
                            QPushButton, QLineEdit, QScrollArea, QGridLayout, QProgressBar)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class KeyProgrammingTab:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.security_input = None
        self.key_status = None
        self.immobilizer_status = None
        self.key_progress = None

    def create_tab(self):
        """Create the key programming tab and return the widget"""
        key_tab = QWidget()
        layout = QVBoxLayout(key_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(5, 5, 5, 5)

        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)

        header_label = QLabel("🔑 Key Programming")
        header_label.setProperty("class", "tab-title")
        header_label.setWordWrap(True)
        header_layout.addWidget(header_label)

        # Vehicle information
        vehicle_frame = QFrame()
        vehicle_frame.setProperty("class", "glass-card")
        vehicle_layout = QVBoxLayout(vehicle_frame)
        vehicle_layout.setContentsMargins(15, 15, 15, 15)

        vehicle_title = QLabel("🚗 Vehicle Information")
        vehicle_title.setProperty("class", "section-title")

        make_label = QLabel("Toyota Camry 2020")
        make_label.setProperty("class", "vehicle-make")
        make_label.setWordWrap(True)

        model_label = QLabel("2.5L Hybrid - Smart Key System")
        model_label.setProperty("class", "vehicle-model")
        model_label.setWordWrap(True)

        vehicle_layout.addWidget(vehicle_title)
        vehicle_layout.addWidget(make_label)
        vehicle_layout.addWidget(model_label)

        # Key programming controls
        key_frame = QFrame()
        key_frame.setProperty("class", "glass-card")
        key_layout = QVBoxLayout(key_frame)
        key_layout.setSpacing(10)
        key_layout.setContentsMargins(15, 15, 15, 15)

        # Security code input - responsive
        security_layout = QHBoxLayout()
        security_label = QLabel("🔒 Security Code:")
        security_label.setProperty("class", "input-label")
        security_label.setMinimumWidth(120)

        self.security_input = QLineEdit()
        self.security_input.setPlaceholderText("Enter vehicle security code (4-8 alphanumeric characters)")
        self.security_input.setMaxLength(8)
        self.security_input.setMinimumHeight(40)

        security_layout.addWidget(security_label)
        security_layout.addWidget(self.security_input)
        security_layout.addStretch()

        # Programming buttons - responsive grid
        btn_layout = QGridLayout()
        btn_layout.setSpacing(10)

        buttons = [
            ("🔑 Program New Key", "primary", self.parent.program_key),
            ("📋 Clone Key", "success", self.parent.clone_key),
            ("🔄 Reset System", "danger", self.parent.reset_system),
        ]

        columns = 2 if self.parent.current_window_width < 800 else 3
        for i, (text, style, callback) in enumerate(buttons):
            btn = QPushButton(text)
            btn.setProperty("class", style)
            btn.setMinimumHeight(45)
            btn.clicked.connect(callback)
            row = i // columns
            col = i % columns
            btn_layout.addWidget(btn, row, col)

        # Key status - responsive
        status_frame = QFrame()
        status_frame.setProperty("class", "stat-card")
        status_frame.setMaximumHeight(80)
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(15, 10, 15, 10)

        self.key_status = QLabel("🔴 No Key Detected")
        self.key_status.setProperty("class", "status-error")
        self.key_status.setWordWrap(True)

        self.immobilizer_status = QLabel("🛡️ Immobilizer: Active")
        self.immobilizer_status.setProperty("class", "status-success")
        self.immobilizer_status.setWordWrap(True)

        status_layout.addWidget(QLabel("Key Status:"))
        status_layout.addWidget(self.key_status)
        status_layout.addStretch()
        status_layout.addWidget(self.immobilizer_status)

        status_frame.setLayout(status_layout)

        # Programming progress
        self.key_progress = QProgressBar()
        self.key_progress.setMinimumHeight(20)
        self.key_progress.setTextVisible(True)
        self.key_progress.setValue(0)
        self.key_progress.setVisible(False)

        key_layout.addLayout(security_layout)
        key_layout.addLayout(btn_layout)
        key_layout.addWidget(self.key_progress)

        scroll_layout.addWidget(header_frame)
        scroll_layout.addWidget(vehicle_frame)
        scroll_layout.addWidget(key_frame)
        scroll_layout.addWidget(status_frame)
        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        return key_tab, "🔑 Key Programming"