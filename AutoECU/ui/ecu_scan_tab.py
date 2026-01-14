#!/usr/bin/env python3
"""
AutoECU - ECU Scan Tab
Separate tab implementation for easier customization
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
                            QTableWidget, QTableWidgetItem, QProgressBar, QHeaderView, QScrollArea)
from PyQt6.QtCore import Qt

# Import color function
try:
    from shared.themes.dacos_cyber_teal import get_dacos_color
except ImportError:
    # Fallback color function
    def get_dacos_color(color_name):
        DACOS_THEME = {
            "bg_main": "#0A1A1A",
            "bg_panel": "#0D2323",
            "bg_card": "#134F4A",
            "accent": "#21F5C1",
            "glow": "#2AF5D1",
            "text_main": "#E8F4F2",
            "text_muted": "#9ED9CF",
            "error": "#FF4D4D",
            "success": "#10B981",
            "warning": "#F59E0B"
        }
        return DACOS_THEME.get(color_name, DACOS_THEME['accent'])

class ECUScanTab:
    """
    ECU Scan Tab for detecting and scanning ECU modules.
    """

    def __init__(self, parent_window):
        """
        Initialize the ECU Scan Tab.

        Args:
            parent_window: The main application window instance
        """
        self.parent = parent_window
        self.ecu_table = None
        self.connection_status = None
        self.scan_progress = None

    def create_tab(self) -> tuple[QWidget, str]:
        """
        Create the ECU scan tab and return the widget.

        Returns:
            tuple: (tab_widget, tab_title)
        """
        scan_tab = QWidget()
        layout = QVBoxLayout(scan_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)

        header_label = QLabel("🔍 ECU Detection & Scanning")
        header_label.setStyleSheet(f"color: {get_dacos_color('accent')}; font-size: 18pt; font-weight: bold;")

        scan_btn = QPushButton("🔄 Scan for ECUs")
        scan_btn.setProperty("class", "primary")
        scan_btn.setMinimumHeight(45)
        scan_btn.clicked.connect(self.parent.scan_ecus)

        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(scan_btn)

        # Scan controls
        controls_frame = QFrame()
        controls_frame.setProperty("class", "glass-card")
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setSpacing(15)
        controls_layout.setContentsMargins(20, 20, 20, 20)

        # ECU table
        self.ecu_table = QTableWidget()
        self.ecu_table.setColumnCount(4)
        self.ecu_table.setHorizontalHeaderLabels(["ECU Name", "Protocol", "Status", "Address"])
        self.ecu_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        controls_layout.addWidget(self.ecu_table)

        # Status section
        status_frame = QFrame()
        status_frame.setProperty("class", "stat-card")
        status_frame.setMaximumHeight(80)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(15, 15, 15, 15)

        self.connection_status = QLabel("⚪ Disconnected")
        self.connection_status.setStyleSheet(f"color: {get_dacos_color('error')}; font-size: 12pt; font-weight: bold;")

        self.scan_progress = QProgressBar()
        self.scan_progress.setMinimumHeight(30)
        self.scan_progress.setVisible(False)

        status_layout.addWidget(QLabel("Connection:"))
        status_layout.addWidget(self.connection_status)
        status_layout.addWidget(self.scan_progress)
        status_layout.addStretch()

        # === Final layout with scroll area (important for small screens) ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.addWidget(header_frame)
        content_layout.addWidget(controls_frame)
        content_layout.addWidget(status_frame)
        content_layout.addStretch()

        scroll.setWidget(content_widget)

        layout.addWidget(scroll)

        return scan_tab, "🔍 ECU Scan"