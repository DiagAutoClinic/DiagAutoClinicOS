#!/usr/bin/env python3
"""
AutoKey Pro - Vehicle Info Tab
Separate tab implementation for vehicle information
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
                            QScrollArea, QGridLayout, QTableWidget, QTableWidgetItem,
                            QPushButton, QHeaderView)
from PyQt6.QtCore import Qt, QTimer

class VehicleInfoTab:
    def __init__(self, parent_window):
        self.parent = parent_window

    def create_tab(self):
        """Create the vehicle info tab and return the widget"""
        vehicle_tab = QWidget()
        layout = QVBoxLayout(vehicle_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header with responsive layout
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QHBoxLayout()
        header_frame.setLayout(header_layout)
        header_layout.setContentsMargins(15, 10, 15, 10)

        header_label = QLabel("🚗 Vehicle Information")
        header_label.setProperty("class", "tab-title")
        header_label.setWordWrap(True)

        refresh_btn = QPushButton("🔄 Refresh Data")
        refresh_btn.setProperty("class", "primary")
        refresh_btn.setMinimumHeight(40)
        refresh_btn.clicked.connect(self.parent.refresh_vehicle_data)

        if self.parent.current_window_width < 600:
            header_layout.addWidget(header_label)
            header_layout.addWidget(refresh_btn)
        else:
            header_layout.addWidget(header_label)
            header_layout.addStretch()
            header_layout.addWidget(refresh_btn)

        # Scrollable content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(5, 5, 5, 5)

        vehicle_frame = QFrame()
        vehicle_frame.setProperty("class", "glass-card")
        vehicle_layout = QVBoxLayout(vehicle_frame)
        vehicle_layout.setContentsMargins(15, 15, 15, 15)

        table_label = QLabel("Vehicle Details:")
        table_label.setProperty("class", "section-title")

        # Responsive table
        details_table = QTableWidget()
        details_table.setColumnCount(2)
        details_table.setHorizontalHeaderLabels(["Property", "Value"])

        # Adjust table based on screen size
        if self.parent.current_window_width < 600:
            details_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        else:
            details_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        # Load vehicle data
        vehicle_data = [
            ["VIN", "REDACTED_VIN_123"],
            ["Make", "Toyota"],
            ["Model", "Camry"],
            ["Year", "2020"],
            ["Key System", "Smart Key"],
            ["Transponder", "ID4C / 4D"],
            ["Keys Programmed", "2/5"],
            ["Immobilizer", "Active"],
            ["Last Service", "2024-01-15"]
        ]

        details_table.setRowCount(len(vehicle_data))
        for row, data in enumerate(vehicle_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if self.parent.current_window_width < 600:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
                details_table.setItem(row, col, item)

        vehicle_layout.addWidget(table_label)
        vehicle_layout.addWidget(details_table)

        content_layout.addWidget(header_frame)
        content_layout.addWidget(vehicle_frame)
        content_layout.addStretch()

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        return vehicle_tab, "🚗 Vehicle Info"