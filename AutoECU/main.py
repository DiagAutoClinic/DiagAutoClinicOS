import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt

from shared.vin_decoder import VINDecoder
from shared.device_handler import DeviceHandler

class AutoECUApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoECU - DiagAutoClinicOS")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize components
        self.vin_decoder = VINDecoder()
        self.device = DeviceHandler(mock_mode=True)
        
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
        self.connect_btn = QPushButton("Connect to ECU")
        self.connect_btn.clicked.connect(self.toggle_connection)
        connection_layout.addWidget(self.connect_btn)
        
        self.connection_status = QLabel("Status: Disconnected")
        connection_layout.addWidget(self.connection_status)
        layout.addLayout(connection_layout)
        
        # ECU Operations
        ecu_layout = QVBoxLayout()
        ecu_layout.addWidget(QLabel("ECU Operations:"))
        
        read_btn = QPushButton("Read ECU Data")
        read_btn.clicked.connect(self.read_ecu)
        ecu_layout.addWidget(read_btn)
        
        write_btn = QPushButton("Write ECU Data")
        write_btn.clicked.connect(self.write_ecu)
        ecu_layout.addWidget(write_btn)
        
        self.ecu_output = QTextEdit()
        self.ecu_output.setPlaceholderText("ECU data will appear here")
        ecu_layout.addWidget(self.ecu_output)
        layout.addLayout(ecu_layout)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
    def decode_vin(self):
        vin = self.vin_input.toPlainText().strip()
        result = self.vin_decoder.decode(vin)
        
        if result.get('error'):
            self.vin_output.setText(f"Error: {result['error']}")
        else:
            info = f"Brand: {result['brand']} | Year: {result['year']}"
            self.vin_output.setText(info)
            
    def toggle_connection(self):
        if self.device.is_connected:
            self.device.disconnect()
            self.connect_btn.setText("Connect to ECU")
            self.connection_status.setText("Status: Disconnected")
        else:
            if self.device.connect():
                self.connect_btn.setText("Disconnect")
                self.connection_status.setText("Status: Connected")
            else:
                QMessageBox.warning(self, "Connection Error", "Failed to connect to ECU")
                
    def read_ecu(self):
        if not self.device.is_connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to the ECU first")
            return
            
        # In a real implementation, you would specify address and length
        result = self.device.read_ecu_data(0x0000, 256)
        self.ecu_output.setText(result)
        
    def write_ecu(self):
        if not self.device.is_connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to the ECU first")
            return
            
        reply = QMessageBox.question(self, "Confirm Write", 
                                    "Are you sure you want to write to the ECU? This can potentially damage your vehicle if done incorrectly.",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # In a real implementation, you would specify address and data
            result = self.device.write_ecu_data(0x0000, b'\x00\x01\x02\x03')
            self.ecu_output.setText(result)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutoECUApp()
    window.show()
    sys.exit(app.exec())
