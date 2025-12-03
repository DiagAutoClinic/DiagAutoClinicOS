#!/usr/bin/env python3
"""
AutoDiag Pro - Live Data Tab
Separate tab implementation for easier customization
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class LiveDataTab:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.live_data_table = None

    def create_tab(self):
        """Create the live data tab and return the widget"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Header
        header = QLabel("📊 Live Data Streaming")
        header.setProperty("class", "tab-title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Control Panel
        control_frame = QFrame()
        control_frame.setProperty("class", "glass-card")
        control_layout = QHBoxLayout(control_frame)

        start_btn = QPushButton("▶ Start Stream")
        start_btn.setProperty("class", "success")
        start_btn.clicked.connect(self.parent.start_live_stream)

        stop_btn = QPushButton("⏹ Stop Stream")
        stop_btn.setProperty("class", "danger")
        stop_btn.clicked.connect(self.parent.stop_live_stream)

        control_layout.addWidget(start_btn)
        control_layout.addWidget(stop_btn)
        control_layout.addStretch()

        # Live Data Table
        data_frame = QFrame()
        data_frame.setProperty("class", "glass-card")
        data_layout = QVBoxLayout(data_frame)

        data_title = QLabel("Live Parameters")
        data_title.setProperty("class", "section-title")

        self.live_data_table = QTableWidget(0, 3)
        self.live_data_table.setHorizontalHeaderLabels(["Parameter", "Value", "Unit"])
        self.live_data_table.horizontalHeader().setStretchLastSection(True)

        # Add sample data
        self.populate_sample_data()

        data_layout.addWidget(data_title)
        data_layout.addWidget(self.live_data_table)

        layout.addWidget(header)
        layout.addWidget(control_frame)
        layout.addWidget(data_frame)

        return tab, "📊 Live Data"

    def populate_sample_data(self):
        """Populate live data table with mock data"""
        # Get current mock live data
        from shared.live_data import get_mock_live_data
        live_data = get_mock_live_data()

        self.live_data_table.setRowCount(len(live_data))
        for row, (param, value, unit) in enumerate(live_data):
            self.live_data_table.setItem(row, 0, QTableWidgetItem(param))
            self.live_data_table.setItem(row, 1, QTableWidgetItem(value))
            self.live_data_table.setItem(row, 2, QTableWidgetItem(unit))