import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTextEdit, QMessageBox, QLineEdit)
from PyQt6.QtCore import Qt

from shared.vin_decoder import VINDecoder
from shared.device_handler import DeviceHandler

class AutoKeyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoKey - DiagAutoClinicOS")
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
        self.connect_btn = QPushButton("Connect to Vehicle")
        self.connect_btn.clicked.connect(self.toggle_connection)
        connection_layout.addWidget(self.connect_btn)
        
        self.connection_status = QLabel("Status: Disconnected")
        connection_layout.addWidget(self.connection_status)
        layout.addLayout(connection_layout)
        
        # Key Programming
        key_layout = QVBoxLayout()
        key_layout.addWidget(QLabel("Key Programming:"))
        
        key_id_layout = QHBoxLayout()
        key_id_layout.addWidget(QLabel("Key ID:"))
        self.key_id_input = QLineEdit()
        key_id_layout.addWidget(self.key_id_input)
        layout.addLayout(key_id_layout)
        
        generate_btn = QPushButton("Generate Key Code")
        generate_btn.clicked.connect(self.generate_key)
        key_layout.addWidget(generate_btn)
        
        program_btn = QPushButton("Program Key")
        program_btn.clicked.connect(self.program_key)
        key_layout.addWidget(program_btn)
        
        self.key_output = QTextEdit()
        self.key_output.setPlaceholderText("Key programming results will appear here")
        key_layout.addWidget(self.key_output)
        layout.addLayout(key_layout)
        
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
            self.connect_btn.setText("Connect to Vehicle")
            self.connection_status.setText("Status: Disconnected")
        else:
            if self.device.connect():
                self.connect_btn.setText("Disconnect")
                self.connection_status.setText("Status: Connected")
            else:
                QMessageBox.warning(self, "Connection Error", "Failed to connect to vehicle")
                
    def generate_key(self):
        vin = self.vin_input.toPlainText().strip()
        key_id = self.key_id_input.text()
        
        if not vin or len(vin) != 17:
            QMessageBox.warning(self, "Invalid VIN", "Please enter a valid 17-character VIN")
            return
            
        if not key_id:
            QMessageBox.warning(self, "Missing Key ID", "Please enter a Key ID")
            return
            
        # Simple key generation algorithm based on VIN and key ID
        # In a real implementation, this would use manufacturer-specific algorithms
        key_code = f"{vin[-6:]}{key_id.zfill(4)}"
        self.key_output.setText(f"Generated Key Code: {key_code}\n\nThis is a mock implementation. A real key generation algorithm would be manufacturer-specific.")
        
    def program_key(self):
        if not self.device.is_connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to the vehicle first")
            return
            
        reply = QMessageBox.question(self, "Confirm Programming", 
                                    "Are you sure you want to program a new key? This will change your vehicle's immobilizer system.",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.key_output.append("\n\nKey programming initiated...")
            # In a real implementation, this would send the actual programming commands
            self.key_output.append("Key programming completed successfully (MOCK)")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutoKeyApp()
    window.show()
    sys.exit(app.exec())
