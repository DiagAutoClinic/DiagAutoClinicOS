import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
                             QProgressBar, QMessageBox)
from PyQt6.QtCore import Qt

from shared.vin_decoder import VINDecoder
from shared.device_handler import DeviceHandler
from shared.dtc_database import DTCDatabase

class AutoDiagApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoDiag - DiagAutoClinicOS")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize components
        self.vin_decoder = VINDecoder()
        self.device = DeviceHandler(mock_mode=True)
        self.dtc_db = DTCDatabase()
        
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # VIN Decoder Section
        vin_layout = QVBoxLayout()
        vin_layout.addWidget(QLabel("Enter VIN:"))
        self.vin_input = QTextEdit()
        self.vin_input.setMaximumHeight(40)
        vin_layout.addWidget(self.vin_input)
        
        decode_btn = QPushButton("Decode VIN")
        decode_btn.clicked.connect(self.decode_vin)
        vin_layout.addWidget(decode_btn)
        
        self.vin_output = QLabel("VIN information will appear here")
        vin_layout.addWidget(self.vin_output)
        layout.addLayout(vin_layout)
        
        # Device Connection
        connection_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Connect to Vehicle")
        self.connect_btn.clicked.connect(self.toggle_connection)
        connection_layout.addWidget(self.connect_btn)
        
        self.connection_status = QLabel("Status: Disconnected")
        connection_layout.addWidget(self.connection_status)
        layout.addLayout(connection_layout)
        
        # DTC Operations
        dtc_layout = QVBoxLayout()
        dtc_layout.addWidget(QLabel("Diagnostic Trouble Codes:"))
        
        scan_btn = QPushButton("Scan for DTCs")
        scan_btn.clicked.connect(self.scan_dtcs)
        dtc_layout.addWidget(scan_btn)
        
        clear_btn = QPushButton("Clear DTCs")
        clear_btn.clicked.connect(self.clear_dtcs)
        dtc_layout.addWidget(clear_btn)
        
        self.dtc_table = QTableWidget()
        self.dtc_table.setColumnCount(2)
        self.dtc_table.setHorizontalHeaderLabels(["DTC Code", "Description"])
        dtc_layout.addWidget(self.dtc_table)
        layout.addLayout(dtc_layout)
        
        # Live Data
        live_data_layout = QVBoxLayout()
        live_data_layout.addWidget(QLabel("Live Data:"))
        
        self.live_data_display = QTextEdit()
        self.live_data_display.setMaximumHeight(100)
        live_data_layout.addWidget(self.live_data_display)
        
        live_data_btn = QPushButton("Get Live Data")
        live_data_btn.clicked.connect(self.get_live_data)
        live_data_layout.addWidget(live_data_btn)
        layout.addLayout(live_data_layout)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
    def decode_vin(self):
        vin = self.vin_input.toPlainText().strip()
        result = self.vin_decoder.decode(vin)
        
        if result.get('error'):
            self.vin_output.setText(f"Error: {result['error']}")
        else:
            info = f"Brand: {result['brand']} | Year: {result['year']} | VIN: {result['full_vin']}"
            self.vin_output.setText(info)
            
    def toggle_connection(self):
        if self.device.is_connected:
            self.device.disconnect()
            self.connect_btn.setText("Connect to Vehicle")
            self.connection_status.setText("Status: Disconnected")
        else:
            if self.device.connect():
                self.connect_btn.setText("Disconnect")
                self.connection_status.setText("Status: Connected")
            else:
                QMessageBox.warning(self, "Connection Error", "Failed to connect to vehicle")
                
    def scan_dtcs(self):
        if not self.device.is_connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to the vehicle first")
            return
            
        dtcs = self.device.scan_dtcs()
        self.dtc_table.setRowCount(len(dtcs))
        
        for row, (code, description) in enumerate(dtcs):
            self.dtc_table.setItem(row, 0, QTableWidgetItem(code))
            self.dtc_table.setItem(row, 1, QTableWidgetItem(description))
            
    def clear_dtcs(self):
        if not self.device.is_connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to the vehicle first")
            return
            
        if self.device.clear_dtcs():
            QMessageBox.information(self, "Success", "DTCs cleared successfully")
            self.dtc_table.setRowCount(0)
        else:
            QMessageBox.warning(self, "Error", "Failed to clear DTCs")
            
    def get_live_data(self):
        if not self.device.is_connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to the vehicle first")
            return
            
        rpm = self.device.get_live_data('rpm')
        speed = self.device.get_live_data('speed')
        temp = self.device.get_live_data('coolant_temp')
        
        self.live_data_display.setText(f"RPM: {rpm}\nSpeed: {speed} km/h\nCoolant Temp: {temp}°C")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutoDiagApp()
    window.show()
    sys.exit(app.exec())
