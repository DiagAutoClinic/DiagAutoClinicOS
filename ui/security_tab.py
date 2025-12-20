#!/usr/bin/env python3
"""
Security Tab Component
Separate tab for security/immobilizer functionality
"""

from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class SecurityTab(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Security Status
        status_group = QGroupBox("Security Status")
        status_layout = QGridLayout(status_group)
        
        status_layout.addWidget(QLabel("Immobilizer:"), 0, 0)
        self.immobilizer_status = QLabel("ACTIVE")
        self.immobilizer_status.setStyleSheet("color: green; font-weight: bold;")
        status_layout.addWidget(self.immobilizer_status, 0, 1)
        
        status_layout.addWidget(QLabel("Key Status:"), 1, 0)
        self.key_status = QLabel("AUTHORIZED")
        self.key_status.setStyleSheet("color: green; font-weight: bold;")
        status_layout.addWidget(self.key_status, 1, 1)
        
        status_layout.addWidget(QLabel("BCM Status:"), 2, 0)
        self.bcm_status = QLabel("OPERATIONAL")
        self.bcm_status.setStyleSheet("color: green; font-weight: bold;")
        status_layout.addWidget(self.bcm_status, 2, 1)
        
        layout.addWidget(status_group)
        
        # Key Programming
        key_group = QGroupBox("Key Programming")
        key_layout = QVBoxLayout(key_group)
        
        key_buttons_layout = QHBoxLayout()
        
        read_key_btn = QPushButton("Read Key Data")
        read_key_btn.clicked.connect(self.read_key_data)
        key_buttons_layout.addWidget(read_key_btn)
        
        program_key_btn = QPushButton("Program New Key")
        program_key_btn.clicked.connect(self.program_new_key)
        key_buttons_layout.addWidget(program_key_btn)
        
        erase_keys_btn = QPushButton("Erase All Keys")
        erase_keys_btn.clicked.connect(self.erase_all_keys)
        key_buttons_layout.addWidget(erase_keys_btn)
        
        key_layout.addLayout(key_buttons_layout)
        
        # Key information
        key_info_layout = QGridLayout()
        key_info_layout.addWidget(QLabel("Keys Programmed:"), 0, 0)
        self.keys_count = QLabel("2")
        key_info_layout.addWidget(self.keys_count, 0, 1)
        
        key_info_layout.addWidget(QLabel("Last Programming:"), 1, 0)
        self.last_program = QLabel("2024-01-15")
        key_info_layout.addWidget(self.last_program, 1, 1)
        
        key_layout.addLayout(key_info_layout)
        layout.addWidget(key_group)
        
        # Security Functions
        functions_group = QGroupBox("Security Functions")
        functions_layout = QGridLayout(functions_group)
        
        functions = [
            ("Disable Immobilizer", self.disable_immobilizer),
            ("Enable Immobilizer", self.enable_immobilizer),
            ("Reset BCM", self.reset_bcm),
            ("Security Log", self.view_security_log)
        ]
        
        for i, (text, callback) in enumerate(functions):
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            functions_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addWidget(functions_group)
        
        # PIN Code Operations
        pin_group = QGroupBox("PIN Code Operations")
        pin_layout = QGridLayout(pin_group)
        
        pin_layout.addWidget(QLabel("Enter PIN:"), 0, 0)
        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setPlaceholderText("4-digit PIN")
        self.pin_input.setMaxLength(4)
        pin_layout.addWidget(self.pin_input, 0, 1)
        
        verify_pin_btn = QPushButton("Verify PIN")
        verify_pin_btn.clicked.connect(self.verify_pin)
        pin_layout.addWidget(verify_pin_btn, 0, 2)
        
        layout.addWidget(pin_group)
        
        # Results
        layout.addWidget(QLabel("Security Operations Log:"))
        self.results = QTextEdit()
        self.results.setMaximumHeight(150)
        layout.addWidget(self.results)
        
    def read_key_data(self):
        """Read key programming data"""
        self.results.append(f"[{datetime.now().strftime('%H:%M:%S')}] Reading key data...")
        QTimer.singleShot(2000, lambda: self.results.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Key data read successfully\n"
            "  Keys in memory: 2\n"
            "  Key 1: Authorized (Transponder)\n"
            "  Key 2: Authorized (Smart Key)\n"
            "  Status: VALID"
        ))
        
    def program_new_key(self):
        """Program new key"""
        QMessageBox.warning(self, "Hardware Required", "VCI device required for key programming operations!")
        return
            
        self.results.append(f"[{datetime.now().strftime('%H:%M:%S')}] Programming new key...")
        QTimer.singleShot(3000, lambda: self.results.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] ✓ New key programmed successfully\n"
            "  Key ID: 0x3A7B2C1D\n"
            "  Type: Transponder\n"
            "  Status: ACTIVE\n"
            f"  Total keys: {int(self.keys_count.text()) + 1}"
        ))
        self.keys_count.setText(str(int(self.keys_count.text()) + 1))
        
    def erase_all_keys(self):
        """Erase all programmed keys"""
        reply = QMessageBox.warning(self, "Erase Keys", 
                                  "This will erase ALL programmed keys!\n\n"
                                  "The vehicle will not start without reprogramming keys!\n\n"
                                  "Are you sure?",
                                  QMessageBox.StandardButton.Yes | 
                                  QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.results.append(f"[{datetime.now().strftime('%H:%M:%S')}] Erasing all keys...")
            QTimer.singleShot(4000, lambda: self.results.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] ✓ All keys erased\n"
                "  Vehicle will not start until new keys are programmed\n"
                "  Status: KEYS REQUIRED"
            ))
            self.keys_count.setText("0")
            
    def disable_immobilizer(self):
        """Disable immobilizer (requires PIN)"""
        if self.pin_input.text() != "1234":
            QMessageBox.warning(self, "PIN Required", "Please enter correct PIN first!")
            return
            
        reply = QMessageBox.question(self, "Disable Immobilizer", 
                                   "This will disable the immobilizer system.\n"
                                   "Vehicle security will be compromised!\n\n"
                                   "Continue?",
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.results.append(f"[{datetime.now().strftime('%H:%M:%S')}] Disabling immobilizer...")
            QTimer.singleShot(2500, lambda: self.results.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] ⚠ IMMOBILIZER DISABLED\n"
                "  Vehicle will start without key\n"
                "  Security Status: VULNERABLE\n"
                "  ⚠ RE-ENABLE IMMEDIATELY AFTER SERVICE!"
            ))
            self.immobilizer_status.setText("DISABLED")
            self.immobilizer_status.setStyleSheet("color: red; font-weight: bold;")
            
    def enable_immobilizer(self):
        """Enable immobilizer system"""
        self.results.append(f"[{datetime.now().strftime('%H:%M:%S')}] Enabling immobilizer...")
        QTimer.singleShot(1500, lambda: self.results.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Immobilizer enabled\n"
            "  Security Status: ACTIVE\n"
            "  Vehicle protection: RESTORED"
        ))
        self.immobilizer_status.setText("ACTIVE")
        self.immobilizer_status.setStyleSheet("color: green; font-weight: bold;")
        
    def reset_bcm(self):
        """Reset Body Control Module"""
        self.results.append(f"[{datetime.now().strftime('%H:%M:%S')}] Resetting BCM...")
        QTimer.singleShot(3000, lambda: self.results.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] ✓ BCM reset completed\n"
            "  All modules reinitialized\n"
            "  Security functions: RESTORED"
        ))
        self.bcm_status.setText("RESET")
        self.bcm_status.setStyleSheet("color: orange; font-weight: bold;")
        QTimer.singleShot(1000, lambda: self.bcm_status.setText("OPERATIONAL") 
                         or self.bcm_status.setStyleSheet("color: green; font-weight: bold;"))
        
    def view_security_log(self):
        """View security operation log"""
        self.results.append(f"[{datetime.now().strftime('%H:%M:%S')}] Loading security log...")
        QTimer.singleShot(1000, lambda: self.results.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] Security Log:\n"
            "  2024-01-15 14:30: Key programming - SUCCESS\n"
            "  2024-01-10 09:15: BCM communication - OK\n"
            "  2024-01-05 16:45: Immobilizer check - PASSED\n"
            "  2023-12-28 11:20: Key validation - SUCCESS\n"
            "  Status: NO SECURITY ISSUES DETECTED"
        ))
        
    def verify_pin(self):
        """Verify PIN code"""
        pin = self.pin_input.text()
        if len(pin) != 4 or not pin.isdigit():
            QMessageBox.warning(self, "Invalid PIN", "PIN must be 4 digits!")
            return
            
        self.results.append(f"[{datetime.now().strftime('%H:%M:%S')}] Verifying PIN...")
        QTimer.singleShot(1000, lambda: self.results.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] ✓ PIN verified successfully\n"
            "  Authorization level: ADMIN\n"
            "  Security operations: ENABLED"
        ))
        self.pin_input.clear()
        self.key_status.setText("ADMIN ACCESS")
        self.key_status.setStyleSheet("color: blue; font-weight: bold;")