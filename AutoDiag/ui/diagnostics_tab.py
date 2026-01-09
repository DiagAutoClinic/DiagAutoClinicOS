#!/usr/bin/env python3
"""
AutoDiag Pro - Diagnostics Tab FINAL WORKING VERSION
All VCI buttons now provide proper feedback
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, 
    QPushButton, QTextEdit, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)

class DiagnosticsTab:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.scan_btn = None
        self.dtc_btn = None
        self.clear_btn = None
        self.results_text = None
        self.vci_status_label = None

    def create_tab(self):
        """Create the diagnostics tab"""
        tab = QWidget()
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 12, 15, 12)

        # HEADER
        header = QLabel("Advanced Diagnostics")
        header.setProperty("class", "tab-title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFixedHeight(50)
        layout.addWidget(header)

        # VCI STATUS INDICATOR
        status_frame = QFrame()
        status_frame.setProperty("class", "glass-card")
        status_frame.setMinimumHeight(100)
        status_layout = QVBoxLayout(status_frame)
        status_layout.setSpacing(12)
        status_layout.setContentsMargins(20, 15, 20, 15)

        status_title = QLabel("VCI Connection Status")
        status_title.setProperty("class", "section-title")
        status_layout.addWidget(status_title)

        self.vci_status_label = QLabel("VCI Status: Check VCI Connection tab first")
        self.vci_status_label.setProperty("class", "section-label")
        status_layout.addWidget(self.vci_status_label)

        # Note about VCI connection
        vci_note = QLabel("💡 VCI connection must be established in the VCI Connection tab before diagnostics can be performed.")
        vci_note.setProperty("class", "info-note")
        vci_note.setWordWrap(True)
        status_layout.addWidget(vci_note)

        layout.addWidget(status_frame)

        # CONTROL PANEL
        control_frame = QFrame()
        control_frame.setProperty("class", "glass-card")
        control_frame.setMinimumHeight(180)
        control_layout = QVBoxLayout(control_frame)
        control_layout.setSpacing(12)
        control_layout.setContentsMargins(20, 15, 20, 15)

        control_title = QLabel("Diagnostic Controls")
        control_title.setProperty("class", "section-title")
        control_layout.addWidget(control_title)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        self.scan_btn = QPushButton("Full System Scan")
        self.scan_btn.setProperty("class", "primary")
        self.scan_btn.setFixedHeight(45)
        self.scan_btn.clicked.connect(self.parent.run_full_scan)

        self.dtc_btn = QPushButton("Read DTCs")
        self.dtc_btn.setProperty("class", "success")
        self.dtc_btn.setFixedHeight(45)
        self.dtc_btn.clicked.connect(self.parent.read_dtcs)

        self.clear_btn = QPushButton("Clear DTCs")
        self.clear_btn.setProperty("class", "warning")
        self.clear_btn.setFixedHeight(45)
        self.clear_btn.clicked.connect(self.parent.clear_dtcs)

        buttons_layout.addWidget(self.scan_btn)
        buttons_layout.addWidget(self.dtc_btn)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addStretch()

        control_layout.addLayout(buttons_layout)
        layout.addWidget(control_frame)

        # RESULTS AREA
        results_frame = QFrame()
        results_frame.setProperty("class", "glass-card")
        results_frame.setMinimumHeight(400)
        results_layout = QVBoxLayout(results_frame)
        results_layout.setSpacing(12)
        results_layout.setContentsMargins(20, 15, 20, 15)

        results_title = QLabel("Scan Results")
        results_title.setProperty("class", "section-title")
        results_layout.addWidget(results_title)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(350)
        self.results_text.setPlainText(
            "System ready for diagnostics.\n\n"
            "Steps to begin:\n"
            "1. Go to 'VCI Connection' tab and connect your device\n"
            "2. Return here and perform diagnostics operations\n\n"
            "Note: VCI connection is required for actual diagnostics.\n"
            "For evaluation, you can still explore the interface."
        )

        results_layout.addWidget(self.results_text)
        layout.addWidget(results_frame)

        scroll_area.setWidget(content_widget)

        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)

        return tab, "Diagnostics"

    def update_vci_status(self, status_text):
        """Update VCI status label"""
        if self.vci_status_label:
            self.vci_status_label.setText(f"VCI Status: {status_text}")
            logger.info(f"VCI Status: {status_text}")

    def update_vci_status_display(self, status_info):
        """Update VCI status display"""
        try:
            status = status_info.get("status", "unknown")
            
            if status == "connected":
                device = status_info.get("device", {})
                self.update_vci_status(f"Connected: {device.get('name', 'VCI Device')}")
            elif status == "disconnected":
                self.update_vci_status("VCI Status: Not Connected")
            else:
                self.update_vci_status(f"VCI Status: {status}")
                
        except Exception as e:
            logger.error(f"Error updating VCI status display: {e}")