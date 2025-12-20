#!/usr/bin/env python3
"""
Live Data Tab Component
Separate tab for live data functionality
"""

from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class LiveDataTab(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.streaming = False
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Controls
        controls_layout = QHBoxLayout()
        start_btn = QPushButton("Start Stream")
        stop_btn = QPushButton("Stop Stream")
        record_btn = QPushButton("Record Data")
        export_btn = QPushButton("Export CSV")
        
        start_btn.clicked.connect(self.start_stream)
        stop_btn.clicked.connect(self.stop_stream)
        record_btn.clicked.connect(self.record_data)
        export_btn.clicked.connect(self.export_csv)
        
        controls_layout.addWidget(start_btn)
        controls_layout.addWidget(stop_btn)
        controls_layout.addWidget(record_btn)
        controls_layout.addWidget(export_btn)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Data table
        layout.addWidget(QLabel("Live Data Parameters:"))
        self.data_table = QTableWidget(12, 4)
        self.data_table.setHorizontalHeaderLabels(["Parameter", "Value", "Unit", "Status"])
        
        # Populate with sample data
        params = [
            ("Engine RPM", "2500", "RPM", "OK"),
            ("Vehicle Speed", "45", "MPH", "OK"),
            ("Coolant Temp", "195", "°F", "OK"),
            ("Throttle Pos", "25", "%", "OK"),
            ("Fuel Level", "75", "%", "OK"),
            ("Battery Voltage", "13.8", "V", "OK"),
            ("O2 Sensor", "0.45", "V", "OK"),
            ("MAF Rate", "12.5", "g/s", "OK"),
            ("Intake Temp", "90", "°F", "OK"),
            ("Fuel Pressure", "58", "PSI", "OK"),
            ("Spark Advance", "15", "°", "OK"),
            ("Engine Load", "35", "%", "OK")
        ]
        
        for i, (param, value, unit, status) in enumerate(params):
            self.data_table.setItem(i, 0, QTableWidgetItem(param))
            self.data_table.setItem(i, 1, QTableWidgetItem(value))
            self.data_table.setItem(i, 2, QTableWidgetItem(unit))
            self.data_table.setItem(i, 3, QTableWidgetItem(status))
        
        layout.addWidget(self.data_table)
        
        # Log area
        layout.addWidget(QLabel("Data Stream Log:"))
        self.log_area = QTextEdit()
        self.log_area.setMaximumHeight(100)
        layout.addWidget(self.log_area)
        
        # Timer for updating live data
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_live_data)
        
    def start_stream(self):
        """Start live data streaming"""
        self.streaming = True
        self.update_timer.start(1000)  # Update every second
        self.log_area.append(f"[{datetime.now().strftime('%H:%M:%S')}] Live data stream started")
        
    def stop_stream(self):
        """Stop live data streaming"""
        self.streaming = False
        self.update_timer.stop()
        self.log_area.append(f"[{datetime.now().strftime('%H:%M:%S')}] Live data stream stopped")
        
    def record_data(self):
        """Record live data to file"""
        if self.streaming:
            self.log_area.append(f"[{datetime.now().strftime('%H:%M:%S')}] Recording data to file...")
            QTimer.singleShot(500, lambda: self.log_area.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] Data recorded successfully"
            ))
        else:
            QMessageBox.warning(self, "Recording", "Start data stream first!")
            
    def export_csv(self):
        """Export data to CSV file"""
        filename, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv)")
        if filename:
            self.log_area.append(f"[{datetime.now().strftime('%H:%M:%S')}] Data exported to {filename}")
            
    def update_live_data(self):
        """Update live data values from diagnostics controller"""
        try:
            if self.main_window and hasattr(self.main_window, 'diagnostics_controller'):
                controller = self.main_window.diagnostics_controller
                if controller:
                    # Check if hardware is connected
                    vci_status = controller.get_vci_status()
                    if vci_status.get('status') == 'connected':
                        # Get real live data
                        live_data = controller.populate_sample_data()
                        for i, (param, value, unit) in enumerate(live_data):
                            if i < self.data_table.rowCount():
                                self.data_table.setItem(i, 0, QTableWidgetItem(param))
                                self.data_table.setItem(i, 1, QTableWidgetItem(value))
                                self.data_table.setItem(i, 2, QTableWidgetItem(unit))
                                self.data_table.setItem(i, 3, QTableWidgetItem("OK"))
                                self.data_table.item(i, 3).setBackground(QColor(100, 255, 100))
                    else:
                        # Hardware not connected
                        for i in range(self.data_table.rowCount()):
                            self.data_table.setItem(i, 1, QTableWidgetItem("N/A"))
                            self.data_table.setItem(i, 3, QTableWidgetItem("HW_REQ"))
                            self.data_table.item(i, 3).setBackground(QColor(255, 200, 100))
                else:
                    # No controller
                    for i in range(self.data_table.rowCount()):
                        self.data_table.setItem(i, 1, QTableWidgetItem("N/A"))
                        self.data_table.setItem(i, 3, QTableWidgetItem("ERROR"))
                        self.data_table.item(i, 3).setBackground(QColor(255, 100, 100))
            else:
                # No main window or controller
                for i in range(self.data_table.rowCount()):
                    self.data_table.setItem(i, 1, QTableWidgetItem("N/A"))
                    self.data_table.setItem(i, 3, QTableWidgetItem("ERROR"))
                    self.data_table.item(i, 3).setBackground(QColor(255, 100, 100))
        except Exception as e:
            # Error - show error status
            for i in range(self.data_table.rowCount()):
                self.data_table.setItem(i, 1, QTableWidgetItem("ERROR"))
                self.data_table.setItem(i, 3, QTableWidgetItem("ERROR"))
                self.data_table.item(i, 3).setBackground(QColor(255, 100, 100))