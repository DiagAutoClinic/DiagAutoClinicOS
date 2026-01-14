#!/usr/bin/env python3
"""
AutoECU - Diagnostics Tab
Separate tab implementation for easier customization
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
                            QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea)
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

class DiagnosticsTab:
    """
    Diagnostics Tab for ECU diagnostic operations.
    """

    def __init__(self, parent_window):
        """
        Initialize the Diagnostics Tab.

        Args:
            parent_window: The main application window instance
        """
        self.parent = parent_window
        self.dtc_table = None

    def create_tab(self) -> tuple[QWidget, str]:
        """
        Create the diagnostics tab and return the widget.

        Returns:
            tuple: (tab_widget, tab_title)
        """
        diag_tab = QWidget()
        layout = QVBoxLayout(diag_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)

        header_label = QLabel("🔧 ECU Diagnostics")
        header_label.setStyleSheet(f"color: {get_dacos_color('accent')}; font-size: 18pt; font-weight: bold;")

        scan_dtc_btn = QPushButton("🔍 Read DTCs")
        scan_dtc_btn.setProperty("class", "primary")
        scan_dtc_btn.setMinimumHeight(45)
        scan_dtc_btn.clicked.connect(self.parent.read_dtcs)

        clear_dtc_btn = QPushButton("🗑️ Clear DTCs")
        clear_dtc_btn.setProperty("class", "danger")
        clear_dtc_btn.setMinimumHeight(45)
        clear_dtc_btn.clicked.connect(self.parent.clear_dtcs)

        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(scan_dtc_btn)
        header_layout.addWidget(clear_dtc_btn)

        # DTC table
        diag_frame = QFrame()
        diag_frame.setProperty("class", "glass-card")
        diag_layout = QVBoxLayout(diag_frame)
        diag_layout.setContentsMargins(20, 20, 20, 20)

        table_label = QLabel("Diagnostic Trouble Codes:")
        table_label.setStyleSheet(f"color: {get_dacos_color('text_muted')}; font-weight: bold; margin-bottom: 10px;")

        self.dtc_table = QTableWidget()
        self.dtc_table.setColumnCount(3)
        self.dtc_table.setHorizontalHeaderLabels(["DTC Code", "Description", "Status"])
        self.dtc_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        diag_layout.addWidget(table_label)
        diag_layout.addWidget(self.dtc_table)

        # === Final layout with scroll area (important for small screens) ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.addWidget(header_frame)
        content_layout.addWidget(diag_frame)
        content_layout.addStretch()

        scroll.setWidget(content_widget)

        layout.addWidget(scroll)

        return diag_tab, "🔧 Diagnostics"