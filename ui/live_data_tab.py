#!/usr/bin/env python3
"""
Live Data Tab Component
Separate tab for live data functionality
"""

import random
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
        """Update live data values"""
        values = [
            str(random.randint(2000, 3000)),  # RPM
            str(random.randint(30, 65)),      # Speed
            str(random.randint(190, 210)),    # Coolant
            str(random.randint(20, 35)),      # Throttle
            str(random.randint(70, 80)),      # Fuel
            f"{random.uniform(13.5, 14.0):.1f}",  # Voltage
            f"{random.uniform(0.3, 0.6):.2f}",     # O2
            f"{random.uniform(10.0, 15.0):.1f}",   # MAF
            str(random.randint(85, 95)),      # Intake Temp
            str(random.randint(55, 65)),      # Fuel Pressure
            str(random.randint(12, 18)),      # Spark Advance
            str(random.randint(30, 40))       # Engine Load
        ]
        
        for i, value in enumerate(values):
            if i < self.data_table.rowCount():
                self.data_table.setItem(i, 1, QTableWidgetItem(value))
                # Update status based on value
                if i == 1:  # Speed - flag if too high
                    if int(value) > 60:
                        self.data_table.setItem(i, 3, QTableWidgetItem("HIGH"))
                        self.data_table.item(i, 3).setBackground(QColor(255, 100, 100))
                    else:
                        self.data_table.setItem(i, 3, QTableWidgetItem("OK"))
                        self.data_table.item(i, 3).setBackground(QColor(100, 255, 100))
                elif i == 2:  # Coolant temp
                    if int(value) > 205:
                        self.data_table.setItem(i, 3, QTableWidgetItem("HOT"))
                        self.data_table.item(i, 3).setBackground(QColor(255, 100, 100))
                    else:
                        self.data_table.setItem(i, 3, QTableWidgetItem("OK"))
                        self.data_table.item(i, 3).setBackground(QColor(100, 255, 100))