#!/usr/bin/env python3
"""
AutoECU - Parameters Tab
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

class ParametersTab:
    """
    Parameters Tab for ECU parameter editing.
    """

    def __init__(self, parent_window):
        """
        Initialize the Parameters Tab.

        Args:
            parent_window: The main application window instance
        """
        self.parent = parent_window
        self.param_table = None

    def create_tab(self) -> tuple[QWidget, str]:
        """
        Create the parameters tab and return the widget.

        Returns:
            tuple: (tab_widget, tab_title)
        """
        param_tab = QWidget()
        layout = QVBoxLayout(param_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)

        header_label = QLabel("🎛️ ECU Parameters")
        header_label.setStyleSheet(f"color: {get_dacos_color('accent')}; font-size: 18pt; font-weight: bold;")

        load_btn = QPushButton("📥 Load Parameters")
        load_btn.setProperty("class", "primary")
        load_btn.setMinimumHeight(45)
        load_btn.clicked.connect(self.parent.load_parameters)

        save_btn = QPushButton("💾 Save Parameters")
        save_btn.setProperty("class", "success")
        save_btn.setMinimumHeight(45)
        save_btn.clicked.connect(self.parent.save_parameters)

        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(load_btn)
        header_layout.addWidget(save_btn)

        # Parameters table
        param_frame = QFrame()
        param_frame.setProperty("class", "glass-card")
        param_layout = QVBoxLayout(param_frame)
        param_layout.setContentsMargins(20, 20, 20, 20)

        table_label = QLabel("Available Parameters:")
        table_label.setStyleSheet(f"color: {get_dacos_color('text_muted')}; font-weight: bold; margin-bottom: 10px;")

        self.param_table = QTableWidget()
        self.param_table.setColumnCount(3)
        self.param_table.setHorizontalHeaderLabels(["Parameter", "Value", "Unit"])
        self.param_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        param_layout.addWidget(table_label)
        param_layout.addWidget(self.param_table)

        # === Final layout with scroll area (important for small screens) ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.addWidget(header_frame)
        content_layout.addWidget(param_frame)
        content_layout.addStretch()

        scroll.setWidget(content_widget)

        layout.addWidget(scroll)

        return param_tab, "🎛️ Parameters"