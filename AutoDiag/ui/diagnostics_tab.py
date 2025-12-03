#!/usr/bin/env python3
"""
AutoDiag Pro - Diagnostics Tab
Separate tab implementation for easier customization
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class DiagnosticsTab:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.scan_btn = None
        self.dtc_btn = None
        self.clear_btn = None
        self.results_text = None

    def create_tab(self):
        """Create the diagnostics tab and return the widget"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Header
        header = QLabel("🔍 Advanced Diagnostics")
        header.setProperty("class", "tab-title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Control Panel
        control_frame = QFrame()
        control_frame.setProperty("class", "glass-card")
        control_layout = QHBoxLayout(control_frame)

        self.scan_btn = QPushButton("🚀 Full System Scan")
        self.scan_btn.setProperty("class", "primary")
        self.scan_btn.clicked.connect(self.parent.run_full_scan)

        self.dtc_btn = QPushButton("📋 Read DTCs")
        self.dtc_btn.setProperty("class", "success")
        self.dtc_btn.clicked.connect(self.parent.read_dtcs)

        self.clear_btn = QPushButton("🧹 Clear DTCs")
        self.clear_btn.setProperty("class", "warning")
        self.clear_btn.clicked.connect(self.parent.clear_dtcs)

        control_layout.addWidget(self.scan_btn)
        control_layout.addWidget(self.dtc_btn)
        control_layout.addWidget(self.clear_btn)
        control_layout.addStretch()

        # Results Area
        results_frame = QFrame()
        results_frame.setProperty("class", "glass-card")
        results_layout = QVBoxLayout(results_frame)

        results_title = QLabel("Scan Results")
        results_title.setProperty("class", "section-title")

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlainText(
            "System ready for diagnostics.\n\n"
            "Select a vehicle brand and click 'Full System Scan' to begin."
        )

        results_layout.addWidget(results_title)
        results_layout.addWidget(self.results_text)

        # Assemble
        layout.addWidget(header)
        layout.addWidget(control_frame)
        layout.addWidget(results_frame)

        return tab, "🔍 Diagnostics"