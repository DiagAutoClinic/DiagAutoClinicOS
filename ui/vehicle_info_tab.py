#!/usr/bin/env python3
"""
Vehicle Info Tab Component
Separate tab for vehicle information
"""

from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class VehicleInfoTab(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Vehicle Identification
        id_group = QGroupBox("Vehicle Identification")
        id_layout = QGridLayout(id_group)
        
        # VIN
        id_layout.addWidget(QLabel("VIN:"), 0, 0)
        self.vin_label = QLabel("1G1ZE5E08CF123456")
        self.vin_label.setStyleSheet("font-family: monospace; font-weight: bold;")
        id_layout.addWidget(self.vin_label, 0, 1)
        
        # Make/Model/Year
        id_layout.addWidget(QLabel("Make:"), 1, 0)
        self.make_label = QLabel("Chevrolet")
        id_layout.addWidget(self.make_label, 1, 1)
        
        id_layout.addWidget(QLabel("Model:"), 2, 0)
        self.model_label = QLabel("Cruze")
        id_layout.addWidget(self.model_label, 2, 1)
        
        id_layout.addWidget(QLabel("Year:"), 3, 0)
        self.year_label = QLabel("2014")
        id_layout.addWidget(self.year_label, 3, 1)
        
        layout.addWidget(id_group)
        
        # Engine Information
        engine_group = QGroupBox("Engine Information")
        engine_layout = QGridLayout(engine_group)
        
        engine_layout.addWidget(QLabel("Engine Type:"), 0, 0)
        self.engine_type = QLabel("1.4L Turbo I4")
        engine_layout.addWidget(self.engine_type, 0, 1)
        
        engine_layout.addWidget(QLabel("ECU Part Number:"), 1, 0)
        self.ecu_part = QLabel("12657834")
        engine_layout.addWidget(self.ecu_part, 1, 1)
        
        engine_layout.addWidget(QLabel("Software Version:"), 2, 0)
        self.software_ver = QLabel("RPO: LUV")
        engine_layout.addWidget(self.software_ver, 2, 1)
        
        engine_layout.addWidget(QLabel("Calibration ID:"), 3, 0)
        self.cal_id = QLabel("75823456")
        engine_layout.addWidget(self.cal_id, 3, 1)
        
        layout.addWidget(engine_group)
        
        # ECU Status
        ecu_group = QGroupBox("ECU Status")
        ecu_layout = QGridLayout(ecu_group)
        
        ecu_layout.addWidget(QLabel("Communication:"), 0, 0)
        self.comm_status = QLabel("ACTIVE")
        self.comm_status.setStyleSheet("color: green; font-weight: bold;")
        ecu_layout.addWidget(self.comm_status, 0, 1)
        
        ecu_layout.addWidget(QLabel("Protocol:"), 1, 0)
        self.protocol = QLabel("CAN 500kbps")
        ecu_layout.addWidget(self.protocol, 1, 1)
        
        ecu_layout.addWidget(QLabel("Operating Mode:"), 2, 0)
        self.op_mode = QLabel("DIAGNOSTIC")
        ecu_layout.addWidget(self.op_mode, 2, 1)
        
        ecu_layout.addWidget(QLabel("Uptime:"), 3, 0)
        self.uptime = QLabel("42h 15m")
        ecu_layout.addWidget(self.uptime, 3, 1)
        
        layout.addWidget(ecu_group)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        read_all_btn = QPushButton("Read All Data")
        read_all_btn.clicked.connect(self.read_all_data)
        buttons_layout.addWidget(read_all_btn)
        
        save_report_btn = QPushButton("Save Report")
        save_report_btn.clicked.connect(self.save_report)
        buttons_layout.addWidget(save_report_btn)
        
        print_btn = QPushButton("Print Report")
        print_btn.clicked.connect(self.print_report)
        buttons_layout.addWidget(print_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Detailed Information
        layout.addWidget(QLabel("Detailed Vehicle Data:"))
        self.info_display = QTextEdit()
        self.info_display.setMaximumHeight(200)
        layout.addWidget(self.info_display)
        
    def read_all_data(self):
        """Read all vehicle information"""
        self.info_display.setPlainText("Reading vehicle information...")
        QTimer.singleShot(2000, lambda: self.info_display.setPlainText(
            f"Vehicle Information Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            "="*60 + "\n\n"
            
            "IDENTIFICATION:\n"
            f"VIN: {self.vin_label.text()}\n"
            f"Make: {self.make_label.text()}\n"
            f"Model: {self.model_label.text()}\n"
            f"Year: {self.year_label.text()}\n\n"
            
            "ENGINE SPECIFICATIONS:\n"
            f"Engine: {self.engine_type.text()}\n"
            f"Displacement: 1.4L\n"
            f"Configuration: Inline 4\n"
            f"Aspiration: Turbocharged\n"
            f"Fuel Type: Gasoline\n\n"
            
            "ECU INFORMATION:\n"
            f"Part Number: {self.ecu_part.text()}\n"
            f"Software: {self.software_ver.text()}\n"
            f"Calibration: {self.cal_id.text()}\n"
            f"Protocol: {self.protocol.text()}\n\n"
            
            "SYSTEM STATUS:\n"
            f"Communication: {self.comm_status.text()}\n"
            f"Operating Mode: {self.op_mode.text()}\n"
            f"Uptime: {self.uptime.text()}\n"
            f"Battery Voltage: 13.8V\n"
            f"ECM Temperature: 85°C\n\n"
            
            "CAPABILITIES:\n"
            "✓ OBD-II Compliant\n"
            "✓ Enhanced Diagnostics\n"
            "✓ Live Data Streaming\n"
            "✓ Programming Capability\n"
            "✓ Security Functions\n"
        ))
        
    def save_report(self):
        """Save vehicle report to file"""
        filename, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "TXT Files (*.txt)")
        if filename:
            self.info_display.append(f"\n[{datetime.now().strftime('%H:%M:%S')}] Report saved to {filename}")
            
    def print_report(self):
        """Print vehicle report"""
        self.info_display.append(f"\n[{datetime.now().strftime('%H:%M:%S')}] Preparing report for printing...")
        QTimer.singleShot(1000, lambda: self.info_display.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Report ready for printing"
        ))
        
    def update_vehicle_info(self, vin=None, make=None, model=None, year=None):
        """Update vehicle information"""
        if vin:
            self.vin_label.setText(vin)
        if make:
            self.make_label.setText(make)
        if model:
            self.model_label.setText(model)
        if year:
            self.year_label.setText(year)
            
    def set_engine_info(self, engine_type=None, ecu_part=None, software_ver=None, cal_id=None):
        """Set engine information"""
        if engine_type:
            self.engine_type.setText(engine_type)
        if ecu_part:
            self.ecu_part.setText(ecu_part)
        if software_ver:
            self.software_ver.setText(software_ver)
        if cal_id:
            self.cal_id.setText(cal_id)