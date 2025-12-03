#!/usr/bin/env python3
"""
AutoKey Pro - Transponder Tab
Separate tab implementation for transponder management
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
                            QPushButton, QScrollArea, QGridLayout, QTableWidget,
                            QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, QTimer

class TransponderTab:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.transponder_table = None

    def create_tab(self):
        """Create the transponder tab and return the widget"""
        transponder_tab = QWidget()
        layout = QVBoxLayout(transponder_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header with responsive button
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QHBoxLayout()
        header_frame.setLayout(header_layout)
        header_layout.setContentsMargins(15, 10, 15, 10)

        header_label = QLabel("📡 Transponder Management")
        header_label.setProperty("class", "tab-title")
        header_label.setWordWrap(True)

        scan_btn = QPushButton("🔍 Scan Transponders")
        scan_btn.setProperty("class", "primary")
        scan_btn.setMinimumHeight(40)
        scan_btn.clicked.connect(self.parent.scan_transponders)

        if self.parent.current_window_width < 600:
            header_layout.addWidget(header_label)
            header_layout.addWidget(scan_btn)
        else:
            header_layout.addWidget(header_label)
            header_layout.addStretch()
            header_layout.addWidget(scan_btn)

        # Transponder table in scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(5, 5, 5, 5)

        transponder_frame = QFrame()
        transponder_frame.setProperty("class", "glass-card")
        transponder_layout = QVBoxLayout(transponder_frame)
        transponder_layout.setContentsMargins(15, 15, 15, 15)

        table_label = QLabel("Available Transponders:")
        table_label.setProperty("class", "section-title")

        # Responsive table
        self.transponder_table = QTableWidget()
        self.transponder_table.setColumnCount(4)
        self.transponder_table.setHorizontalHeaderLabels(["Key ID", "Type", "Status", "Vehicle"])

        # Make table responsive
        header = self.transponder_table.horizontalHeader()
        if self.parent.current_window_width < 800:
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        else:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.transponder_table.verticalHeader().setVisible(False)

        # Add sample data
        self.add_sample_transponder_data()

        transponder_layout.addWidget(table_label)
        transponder_layout.addWidget(self.transponder_table)

        content_layout.addWidget(header_frame)
        content_layout.addWidget(transponder_frame)
        content_layout.addStretch()

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        return transponder_tab, "📡 Transponders"

    def add_sample_transponder_data(self):
        """Add sample transponder data securely"""
        sample_data = [
            ["KEY001", "Smart Key", "✅ Programmed", "Toyota Camry"],
            ["KEY002", "Smart Key", "✅ Programmed", "Toyota Camry"],
            ["KEY003", "Mechanical", "⚠️ Unprogrammed", "N/A"],
            ["TSP001", "ID4C", "🔴 Blank", "N/A"],
            ["TSP002", "4D", "🟡 Learning", "Honda Civic"],
            ["TSP003", "ID46", "✅ Ready", "N/A"]
        ]

        self.transponder_table.setRowCount(len(sample_data))
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                if col == 2:  # Status column
                    if "Programmed" in value or "Ready" in value:
                        item.setForeground(Qt.GlobalColor.green)
                    elif "Unprogrammed" in value or "Learning" in value:
                        item.setForeground(Qt.GlobalColor.yellow)
                    elif "Blank" in value:
                        item.setForeground(Qt.GlobalColor.red)

                self.transponder_table.setItem(row, col, item)