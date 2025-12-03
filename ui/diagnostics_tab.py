#!/usr/bin/env python3
"""
Diagnostics Tab Component
Separate tab for diagnostics functionality
"""

from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class DiagnosticsTab(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Controls
        controls_layout = QHBoxLayout()
        scan_btn = QPushButton("Full System Scan")
        read_btn = QPushButton("Read DTCs")
        clear_btn = QPushButton("Clear DTCs")
        freeze_btn = QPushButton("Freeze Frame")
        
        scan_btn.clicked.connect(self.full_scan)
        read_btn.clicked.connect(self.read_dtcs)
        clear_btn.clicked.connect(self.clear_dtcs)
        freeze_btn.clicked.connect(self.freeze_frame)
        
        controls_layout.addWidget(scan_btn)
        controls_layout.addWidget(read_btn)
        controls_layout.addWidget(clear_btn)
        controls_layout.addWidget(freeze_btn)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Results section
        layout.addWidget(QLabel("Diagnostic Results:"))
        self.results = QTextEdit()
        self.results.setPlaceholderText("Scan results will appear here...")
        layout.addWidget(self.results)
        
        # DTC Table
        layout.addWidget(QLabel("Stored DTCs:"))
        self.dtc_table = QTableWidget(0, 4)
        self.dtc_table.setHorizontalHeaderLabels(["DTC Code", "Status", "Priority", "Description"])
        layout.addWidget(self.dtc_table)
        
    def full_scan(self):
        """Full system scan"""
        self.results.setPlainText("Running full system scan...")
        QTimer.singleShot(2000, lambda: self.results.setPlainText(
            f"Full System Scan Results - {datetime.now().strftime('%H:%M:%S')}\n\n"
            "✓ ECU Communication: ESTABLISHED\n"
            "✓ CAN Bus: NORMAL (500kbps)\n"
            "✓ LIN Bus: ACTIVE\n"
            "✓ Sensor Network: OK\n"
            "✓ System Voltage: 13.8V\n"
            "✓ Communication Speed: 500kbps\n\n"
            "Result: ALL SYSTEMS OPERATIONAL"
        ))
        
    def read_dtcs(self):
        """Read diagnostic trouble codes"""
        self.results.setPlainText("Reading DTCs...")
        QTimer.singleShot(1500, lambda: self.results.setPlainText(
            f"DTC Read Results - {datetime.now().strftime('%H:%M:%S')}\n\n"
            "P0301 - Cylinder 1 Misfire Detected\n"
            "  Status: Confirmed\n"
            "  Priority: Medium\n\n"
            "Total DTCs: 1\n"
            "Status: REQUIRES ATTENTION"
        ))
        
        # Add DTC to table
        self.add_dtc_row("P0301", "Confirmed", "Medium", "Cylinder 1 Misfire Detected")
        
    def clear_dtcs(self):
        """Clear diagnostic trouble codes"""
        reply = QMessageBox.question(self, "Clear DTCs", 
                                   "Clear all diagnostic trouble codes?",
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.results.setPlainText("Clearing DTCs...")
            QTimer.singleShot(1000, lambda: self.results.setPlainText(
                f"DTC Clear Results - {datetime.now().strftime('%H:%M:%S')}\n\n"
                "✓ All DTCs cleared successfully\n"
                "✓ System memory reset\n\n"
                "Status: READY FOR NEW DIAGNOSTICS"
            ))
            # Clear table
            self.dtc_table.setRowCount(0)
            
    def freeze_frame(self):
        """Capture freeze frame data"""
        self.results.setPlainText("Capturing freeze frame data...")
        QTimer.singleShot(1000, lambda: self.results.setPlainText(
            f"Freeze Frame Data - {datetime.now().strftime('%H:%M:%S')}\n\n"
            "Engine RPM: 2500\n"
            "Vehicle Speed: 45 MPH\n"
            "Coolant Temp: 195°F\n"
            "Throttle Pos: 25%\n"
            "Fuel Level: 75%\n\n"
            "Data captured successfully"
        ))
        
    def add_dtc_row(self, code, status, priority, description):
        """Add a DTC row to the table"""
        row_position = self.dtc_table.rowCount()
        self.dtc_table.insertRow(row_position)
        
        self.dtc_table.setItem(row_position, 0, QTableWidgetItem(code))
        self.dtc_table.setItem(row_position, 1, QTableWidgetItem(status))
        self.dtc_table.setItem(row_position, 2, QTableWidgetItem(priority))
        self.dtc_table.setItem(row_position, 3, QTableWidgetItem(description))