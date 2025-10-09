#!/usr/bin/env python3
"""
DiagAutoClinicOS - Professional Launcher with Hardware Support
"""

import sys
import os
import subprocess
import time
from pathlib import Path
from typing import List, Dict

# Add shared directory to path
shared_path = os.path.join(os.path.dirname(__file__), 'shared')
if shared_path not in sys.path:
    sys.path.append(shared_path)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QTabWidget, QMessageBox,
    QGroupBox, QFrame, QComboBox, QMenu, QSystemTrayIcon,
    QInputDialog, QListWidget, QListWidgetItem, QProgressDialog,
    QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPalette, QColor, QAction

from device_handler import DeviceHandler, ProfessionalDevice
from style_manager import StyleManager

ALLOWED_APPS: Dict[str, str] = {
    'diag': 'AutoDiag/main.py',
    'ecu': 'AutoECU/main.py',
    'key': 'AutoKey/main.py'
}

class ProfessionalDiagAutoClinicLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.device_handler = DeviceHandler(mock_mode=True)
        self.style_manager = StyleManager()
        self.available_devices = []
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("DiagAutoClinicOS - Professional Vehicle Diagnostics")
        self.setGeometry(100, 100, 1400, 1000)
        # Enable maximize button and proper window management
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowMinimizeButtonHint)
        
        # Apply initial theme
        self.style_manager.set_theme(self.style_manager.current_theme)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with better spacing
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)  # More spacing between sections
        main_layout.setContentsMargins(25, 25, 25, 25)  # More margins
        
        # Header
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)
        
        # Hardware detection section
        hardware_layout = self.create_hardware_section()
        main_layout.addLayout(hardware_layout)
        
        # Status bar
        status_layout = self.create_status_bar()
        main_layout.addLayout(status_layout)
        
        # Applications section
        apps_layout = self.create_applications_section()
        main_layout.addLayout(apps_layout)
        
        # Quick actions
        quick_actions_layout = self.create_quick_actions()
        main_layout.addLayout(quick_actions_layout)
        
        # Log output
        log_layout = self.create_log_section()
        main_layout.addLayout(log_layout)
        
        # Initialize hardware detection
        self.detect_hardware()
        
    def create_hardware_section(self):
        """Create professional hardware detection section with better layout"""
        layout = QVBoxLayout()
        
        # Section title
        hw_label = QLabel("Professional Hardware Detection")
        hw_label.setProperty("class", "subtitle")
        hw_font = QFont()
        hw_font.setPointSize(16)
        hw_font.setBold(True)
        hw_label.setFont(hw_font)
        hw_label.setStyleSheet("margin-bottom: 10px;")
        layout.addWidget(hw_label)
        
        # Hardware controls - use a grid layout for better button arrangement
        hw_controls = QHBoxLayout()
        
        # Detect button
        detect_btn = QPushButton("Scan for Hardware")
        detect_btn.setProperty("class", "primary")
        detect_btn.setMinimumHeight(30)
        detect_btn.clicked.connect(self.detect_hardware)
        
        # Connection controls
        connect_btn = QPushButton("Connect to Selected")
        connect_btn.setProperty("class", "success")
        connect_btn.setMinimumHeight(30)
        connect_btn.clicked.connect(self.connect_to_selected_device)
        
        disconnect_btn = QPushButton("Disconnect")
        disconnect_btn.setProperty("class", "danger")
        disconnect_btn.setMinimumHeight(30)
        disconnect_btn.clicked.connect(self.disconnect_device)
        
        hw_controls.addWidget(detect_btn)
        hw_controls.addWidget(connect_btn)
        hw_controls.addWidget(disconnect_btn)
        hw_controls.addStretch()
        
        layout.addLayout(hw_controls)
        
        # Device list with better sizing
        devices_label = QLabel("Detected Professional Devices:")
        devices_label.setStyleSheet("font-weight: bold; margin-top: 10px; margin-bottom: 5px;")
        layout.addWidget(devices_label)
        
        self.device_list = QListWidget()
        self.device_list.setMinimumHeight(75)  # More space for device list
        self.device_list.setMaximumHeight(200)
        self.device_list.itemClicked.connect(self.on_device_selected)
        self.device_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #2a2f34;
                border-radius: 4px;
                background-color: #1a1f24;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #2a2f34;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        layout.addWidget(self.device_list)
        
        return layout
        
    def create_header(self):
        """Create the application header with theme selector"""
        layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("DiagAutoClinicOS - Professional Edition")
        title_label.setProperty("class", "title")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # Theme selector
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self.style_manager.get_theme_names())
        self.theme_combo.setCurrentText(self.style_manager.current_theme)
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addLayout(theme_layout)
        
        return layout
        
    def create_status_bar(self):
        """Create enhanced status information bar"""
        layout = QHBoxLayout()
        
        # Connection status
        connection_group = QGroupBox("Professional Connection Status")
        connection_layout = QHBoxLayout()
        
        self.connection_indicator = QLabel("●")
        self.connection_indicator.setStyleSheet("color: #ff4444; font-size: 24px; font-weight: bold;")
        self.connection_label = QLabel("No Hardware Connected")
        self.connection_label.setProperty("class", "status-disconnected")
        
        self.device_info_label = QLabel("Device: None")
        self.protocol_info_label = QLabel("Protocol: None")
        
        connection_layout.addWidget(self.connection_indicator)
        connection_layout.addWidget(self.connection_label)
        connection_layout.addWidget(self.device_info_label)
        connection_layout.addWidget(self.protocol_info_label)
        connection_layout.addStretch()
        
        connection_group.setLayout(connection_layout)
        
        # System status
        system_group = QGroupBox("System Status")
        system_layout = QVBoxLayout()
        
        self.mock_mode_label = QLabel("Mock Mode: Active")
        self.hardware_status_label = QLabel("Hardware: Not Detected")
        
        system_layout.addWidget(self.mock_mode_label)
        system_layout.addWidget(self.hardware_status_label)
        system_group.setLayout(system_layout)
        
        layout.addWidget(connection_group, 3)
        layout.addWidget(system_group, 1)
        
        return layout

    def create_applications_section(self):
        """Create the main applications launcher section with flexible layout"""
        layout = QVBoxLayout()
        
        # Section title
        apps_label = QLabel("Professional Diagnostic Applications")
        apps_label.setProperty("class", "subtitle")
        apps_font = QFont()
        apps_font.setPointSize(16)  # Larger title
        apps_font.setBold(True)
        apps_label.setFont(apps_font)
        apps_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        apps_label.setStyleSheet("margin-bottom: 20px;")
        
        layout.addWidget(apps_label)
        
        # Use a simple horizontal layout instead of scroll area for now
        apps_container = QWidget()
        apps_container_layout = QHBoxLayout(apps_container)
        apps_container_layout.setSpacing(25)  # More spacing between cards
        apps_container_layout.setContentsMargins(10, 10, 10, 10)
        
        # AutoDiag Card
        diag_card = self.create_app_card(
            "🔍", 
            "AutoDiag Pro", 
            "Vehicle Diagnostics", 
            "Professional DTC scanning, live data monitoring, and comprehensive system analysis with real hardware support",
            self.launch_diag,
            "primary"
        )
        
        # AutoECU Card
        ecu_card = self.create_app_card(
            "⚙", 
            "AutoECU Pro", 
            "ECU Programming", 
            "Advanced ECU reading/writing, module coding, adaptations, and professional programming tools",
            self.launch_ecu,
            "success"
        )
        
        # AutoKey Card
        key_card = self.create_app_card(
            "🔒", 
            "AutoKey Pro", 
            "Security Systems", 
            "Key programming, immobilizer access, security code calculation, and advanced security systems",
            self.launch_key,
            "danger"
        )
        
        apps_container_layout.addWidget(diag_card)
        apps_container_layout.addWidget(ecu_card)
        apps_container_layout.addWidget(key_card)
        
        layout.addWidget(apps_container)
        
        return layout

    def create_app_card(self, emoji, title, subtitle, description, handler, button_class):
        """Create an application launch card with improved layout"""
        card = QFrame()
        card.setMinimumHeight(380) # Increased height for better text display
        card.setMinimumWidth(350)   # Minimum width to prevent squeezing
        card.setFrameStyle(QFrame.Shape.Box)
        card.setStyleSheet("QFrame { margin: 5px; }")
        
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)  # Add padding
        
        # Header with emoji and title
        header_layout = QHBoxLayout()
        emoji_label = QLabel(emoji)
        emoji_label.setStyleSheet("font-size: 36px; margin-right: 10px;")
        emoji_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        title_layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setProperty("class", "title")
        title_font = QFont()
        title_font.setPointSize(16)  # Slightly larger title
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)  # Allow title to wrap
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setProperty("class", "subtitle")
        subtitle_label.setWordWrap(True)  # Allow subtitle to wrap
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.addStretch()
        
        header_layout.addWidget(emoji_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Description with better formatting
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            color: #888888; 
            font-size: 12px; 
            line-height: 1.6;
            margin-top: 10px;
            margin-bottom: 15px;
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Launch button with fixed height
        launch_btn = QPushButton("Launch Professional Edition")
        launch_btn.setProperty("class", button_class)
        launch_btn.setMinimumHeight(40)  # Fixed button height
        launch_btn.clicked.connect(handler)
        
        layout.addLayout(header_layout)
        layout.addWidget(desc_label)
        layout.addStretch()
        layout.addWidget(launch_btn)
        
        return card

    def detect_hardware(self):
        """Scan for professional diagnostic hardware"""
        self.log_message("Scanning for professional diagnostic hardware...")
        
        # Show progress dialog
        progress = QProgressDialog("Scanning for hardware...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        def scan_progress():
            """Simulate hardware scanning progress with timeout protection"""
            for i in range(101):
                progress.setValue(i)
                QApplication.processEvents()
                if progress.wasCanceled():
                    break
                time.sleep(0.01)
            
            progress.close()
            
            # Perform actual hardware detection with try-except for safety
            try:
                self.available_devices = self.device_handler.detect_professional_devices()
                self.update_device_list()
                
                if self.available_devices:
                    self.log_message(f"Found {len(self.available_devices)} professional device(s)")
                    self.hardware_status_label.setText(f"Hardware: {len(self.available_devices)} devices found")
                else:
                    self.log_message("No professional hardware detected - using mock mode")
                    self.hardware_status_label.setText("Hardware: None (Mock Mode)")
            except Exception as e:
                self.log_message(f"Hardware detection failed: {str(e)} (timeout or error)")
                QMessageBox.warning(self, "Detection Error", "Hardware scan failed safely.")
        
        # Start scanning in background
        QTimer.singleShot(100, scan_progress)

    def update_device_list(self):
        """Update the device list widget"""
        self.device_list.clear()
        for device in self.available_devices:
            item = QListWidgetItem(str(device))
            item.setData(Qt.ItemDataRole.UserRole, device)
            self.device_list.addItem(item)

    def on_device_selected(self, item):
        """Handle device selection with sanitization"""
        device = item.data(Qt.ItemDataRole.UserRole)
        device_name = str(device.name).replace('\n', '').replace('\r', '').strip()
        self.log_message(f"Selected device: {device_name}")

    def connect_to_selected_device(self):
        """Connect to the selected professional device"""
        selected_items = self.device_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Device Selected", "Please select a device from the list")
            return
            
        device_item = selected_items[0]
        device = device_item.data(Qt.ItemDataRole.UserRole)
        device_name = str(device.name).replace('\n', '').replace('\r', '').strip()
        
        self.log_message(f"Connecting to {device_name}...")
        
        if self.device_handler.connect_to_device(device_name):
            self.connection_indicator.setStyleSheet("color: #00ff00; font-size: 24px; font-weight: bold;")
            self.connection_label.setText(f"Connected to {device_name}")
            self.connection_label.setProperty("class", "status-connected")
            self.device_info_label.setText(f"Device: {device_name}")
            self.protocol_info_label.setText(f"Protocol: {self.device_handler.current_protocol.value}")
            self.mock_mode_label.setText("Mock Mode: Inactive")
            self.log_message(f"Successfully connected to {device_name}")
            
            # Test advanced features without logging sensitive details
            ecu_info = self.device_handler.read_ecu_identification_advanced()
            self.log_message("ECU Identification read successfully (details in dialog)")
        else:
            self.log_message(f"Failed to connect to {device_name}")
            QMessageBox.warning(self, "Connection Failed", f"Could not connect to {device_name}")

    def disconnect_device(self):
        """Disconnect from current device"""
        if self.device_handler.is_connected:
            self.device_handler.disconnect()
            self.connection_indicator.setStyleSheet("color: #ff4444; font-size: 24px; font-weight: bold;")
            self.connection_label.setText("Disconnected")
            self.connection_label.setProperty("class", "status-disconnected")
            self.device_info_label.setText("Device: None")
            self.protocol_info_label.setText("Protocol: None")
            self.mock_mode_label.setText("Mock Mode: Active")
            self.log_message("Disconnected from professional device")

    def create_quick_actions(self):
        """Create professional quick action buttons"""
        layout = QVBoxLayout()
        
        actions_label = QLabel("Professional Quick Actions")
        actions_label.setProperty("class", "subtitle")
        actions_font = QFont()
        actions_font.setPointSize(14)
        actions_font.setBold(True)
        actions_label.setFont(actions_font)
        
        layout.addWidget(actions_label)
        
        actions_layout = QHBoxLayout()
        
        quick_scan_btn = QPushButton("🔍 Professional DTC Scan")
        quick_scan_btn.setProperty("class", "primary")
        quick_scan_btn.clicked.connect(self.professional_dtc_scan)
        
        ecu_id_btn = QPushButton("📋 ECU Identification")
        ecu_id_btn.setProperty("class", "success")
        ecu_id_btn.clicked.connect(self.professional_ecu_identification)
        
        system_scan_btn = QPushButton("📊 System Analysis")
        system_scan_btn.setProperty("class", "primary")
        system_scan_btn.clicked.connect(self.professional_system_scan)
        
        coding_btn = QPushButton("⚙ Module Coding")
        coding_btn.setProperty("class", "danger")
        coding_btn.clicked.connect(self.professional_module_coding)
        
        actions_layout.addWidget(quick_scan_btn)
        actions_layout.addWidget(ecu_id_btn)
        actions_layout.addWidget(system_scan_btn)
        actions_layout.addWidget(coding_btn)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        return layout

    def professional_dtc_scan(self):
        """Perform professional DTC scan"""
        if not self.device_handler.is_connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to a professional device first")
            return
            
        self.log_message("Performing professional DTC scan...")
        dtcs = self.device_handler.scan_dtcs()
        if dtcs:
            self.log_message(f"Found {len(dtcs)} DTC(s):")
            for code, severity, description in dtcs:
                self.log_message(f"  {code}: {description} ({severity})")
        else:
            self.log_message("No DTCs found - system clean")

    def professional_ecu_identification(self):
        """Perform professional ECU identification"""
        if not self.device_handler.is_connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to a professional device first")
            return
            
        self.log_message("Reading advanced ECU identification...")
        ecu_info = self.device_handler.read_ecu_identification_advanced()
        
        info_text = f"""
Advanced ECU Identification:
Part Number: {ecu_info.get('part_number', 'N/A')}
Software: {ecu_info.get('software_version', 'N/A')}
Hardware: {ecu_info.get('hardware_version', 'N/A')}
Serial: {ecu_info.get('serial_number', 'N/A')}
Supplier: {ecu_info.get('supplier', 'N/A')}
        """
        QMessageBox.information(self, "ECU Identification", info_text.strip())

    def professional_system_scan(self):
        """Perform professional system scan"""
        if not self.device_handler.is_connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to a professional device first")
            return
            
        self.log_message("Performing professional system analysis...")
        system_info = self.device_handler.perform_advanced_diagnostic('system_scan')
        self.log_message("System analysis completed")

    def professional_module_coding(self):
        """Check module coding capabilities"""
        if not self.device_handler.is_connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to a professional device first")
            return
            
        self.log_message("Checking module coding capabilities...")
        coding_info = self.device_handler.perform_advanced_diagnostic('module_coding')
        self.log_message(f"Coding status: {coding_info.get('coding_status', 'N/A')}")

    def log_message(self, message):
        """Add message to log with timestamp"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_output.append(f"[{timestamp}] {message}")

    def change_theme(self, theme_name):
        """Change application theme"""
        self.style_manager.set_theme(theme_name)
        self.log_message(f"Theme changed to: {theme_name}")

    def create_log_section(self):
        """Create log output section"""
        layout = QVBoxLayout()
        
        log_label = QLabel("Professional Activity Log")
        log_label.setProperty("class", "subtitle")
        
        self.log_output = QTextEdit()
        self.log_output.setMaximumHeight(150)
        self.log_output.setReadOnly(True)
        
        log_controls = QHBoxLayout()
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.log_output.clear)
        
        export_log_btn = QPushButton("Export Professional Log")
        export_log_btn.clicked.connect(self.export_log)
        
        log_controls.addWidget(clear_log_btn)
        log_controls.addWidget(export_log_btn)
        log_controls.addStretch()
        
        layout.addWidget(log_label)
        layout.addWidget(self.log_output)
        layout.addLayout(log_controls)
        
        return layout

    def export_log(self):
        """Export log to safe user home directory"""
        from datetime import datetime
        filename = os.path.expanduser(f"~/diagautoclinic_pro_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        try:
            with open(filename, 'w') as f:
                f.write(self.log_output.toPlainText())
            self.log_message(f"Professional log exported to: {filename}")
            QMessageBox.information(self, "Export Successful", f"Professional log exported to:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export log: {e}")

    def launch_diag(self):
        """Launch AutoDiag Pro with security checks"""
        try:
            rel_path = ALLOWED_APPS['diag']
            if rel_path not in ALLOWED_APPS.values():
                raise ValueError("Invalid application")
            diag_path = os.path.join(os.path.dirname(__file__), rel_path)
            if not os.path.abspath(diag_path).startswith(os.path.abspath(os.path.dirname(__file__))):
                raise ValueError("Path traversal detected")
            if os.path.exists(diag_path):
                subprocess.Popen([sys.executable, diag_path], shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.log_message("Launched AutoDiag Pro - Professional Vehicle Diagnostics")
            else:
                QMessageBox.warning(self, "Application Not Found", "AutoDiag Pro application not found")
        except Exception as e:
            self.log_message(f"Failed to launch securely: {str(e)}")
            QMessageBox.critical(self, "Launch Error", f"Failed to launch AutoDiag Pro: {e}")

    def launch_ecu(self):
        """Launch AutoECU Pro with security checks"""
        try:
            rel_path = ALLOWED_APPS['ecu']
            if rel_path not in ALLOWED_APPS.values():
                raise ValueError("Invalid application")
            ecu_path = os.path.join(os.path.dirname(__file__), rel_path)
            if not os.path.abspath(ecu_path).startswith(os.path.abspath(os.path.dirname(__file__))):
                raise ValueError("Path traversal detected")
            if os.path.exists(ecu_path):
                subprocess.Popen([sys.executable, ecu_path], shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.log_message("Launched AutoECU Pro - Professional ECU Programming")
            else:
                QMessageBox.warning(self, "Application Not Found", "AutoECU Pro application not found")
        except Exception as e:
            self.log_message(f"Failed to launch securely: {str(e)}")
            QMessageBox.critical(self, "Launch Error", f"Failed to launch AutoECU Pro: {e}")

    def launch_key(self):
        """Launch AutoKey Pro with security checks"""
        try:
            rel_path = ALLOWED_APPS['key']
            if rel_path not in ALLOWED_APPS.values():
                raise ValueError("Invalid application")
            key_path = os.path.join(os.path.dirname(__file__), rel_path)
            if not os.path.abspath(key_path).startswith(os.path.abspath(os.path.dirname(__file__))):
                raise ValueError("Path traversal detected")
            if os.path.exists(key_path):
                subprocess.Popen([sys.executable, key_path], shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.log_message("Launched AutoKey Pro - Professional Key Programming")
            else:
                QMessageBox.warning(self, "Application Not Found", "AutoKey Pro application not found")
        except Exception as e:
            self.log_message(f"Failed to launch securely: {str(e)}")
            QMessageBox.critical(self, "Launch Error", f"Failed to launch AutoKey Pro: {e}")

    def resizeEvent(self, event):
        """Handle window resize for better responsive layout"""
        super().resizeEvent(event)
        # You can add dynamic layout adjustments here if needed
        pass

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("DiagAutoClinicOS Professional")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("AutoClinic Pro")
    
    # Create and show main window
    launcher = ProfessionalDiagAutoClinicLauncher()
    launcher.show()
    
    # Start application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()        
    def setup_ui(self):
        self.setWindowTitle("DiagAutoClinicOS - Professional Vehicle Diagnostics")
        self.setGeometry(100, 100, 1400, 1000)
        # Enable maximize button and proper window management
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowMinimizeButtonHint)
        
        # Apply initial theme
        self.style_manager.set_theme(self.style_manager.current_theme)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with better spacing
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)  # More spacing between sections
        main_layout.setContentsMargins(25, 25, 25, 25)  # More margins
        
        # Header
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)
        
        # Hardware detection section
        hardware_layout = self.create_hardware_section()
        main_layout.addLayout(hardware_layout)
        
        # Status bar
        status_layout = self.create_status_bar()
        main_layout.addLayout(status_layout)
        
        # Applications section
        apps_layout = self.create_applications_section()
        main_layout.addLayout(apps_layout)
        
        # Quick actions
        quick_actions_layout = self.create_quick_actions()
        main_layout.addLayout(quick_actions_layout)
        
        # Log output
        log_layout = self.create_log_section()
        main_layout.addLayout(log_layout)
        
        # Initialize hardware detection
        self.detect_hardware()
        
    def create_hardware_section(self):
        """Create professional hardware detection section with better layout"""
        layout = QVBoxLayout()
        
        # Section title
        hw_label = QLabel("Professional Hardware Detection")
        hw_label.setProperty("class", "subtitle")
        hw_font = QFont()
        hw_font.setPointSize(16)
        hw_font.setBold(True)
        hw_label.setFont(hw_font)
        hw_label.setStyleSheet("margin-bottom: 10px;")
        layout.addWidget(hw_label)
        
        # Hardware controls - use a grid layout for better button arrangement
        hw_controls = QHBoxLayout()
        
        # Detect button
        detect_btn = QPushButton("Scan for Hardware")
        detect_btn.setProperty("class", "primary")
        detect_btn.setMinimumHeight(30)
        detect_btn.clicked.connect(self.detect_hardware)
        
        # Connection controls
        connect_btn = QPushButton("Connect to Selected")
        connect_btn.setProperty("class", "success")
        connect_btn.setMinimumHeight(30)
        connect_btn.clicked.connect(self.connect_to_selected_device)
        
        disconnect_btn = QPushButton("Disconnect")
        disconnect_btn.setProperty("class", "danger")
        disconnect_btn.setMinimumHeight(30)
        disconnect_btn.clicked.connect(self.disconnect_device)
        
        hw_controls.addWidget(detect_btn)
        hw_controls.addWidget(connect_btn)
        hw_controls.addWidget(disconnect_btn)
        hw_controls.addStretch()
        
        layout.addLayout(hw_controls)
        
        # Device list with better sizing
        devices_label = QLabel("Detected Professional Devices:")
        devices_label.setStyleSheet("font-weight: bold; margin-top: 10px; margin-bottom: 5px;")
        layout.addWidget(devices_label)
        
        self.device_list = QListWidget()
        self.device_list.setMinimumHeight(75)  # More space for device list
        self.device_list.setMaximumHeight(200)
        self.device_list.itemClicked.connect(self.on_device_selected)
        self.device_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #2a2f34;
                border-radius: 4px;
                background-color: #1a1f24;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #2a2f34;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        layout.addWidget(self.device_list)
        
        return layout
        
    def create_header(self):
        """Create the application header with theme selector"""
        layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("DiagAutoClinicOS - Professional Edition")
        title_label.setProperty("class", "title")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # Theme selector
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self.style_manager.get_theme_names())
        self.theme_combo.setCurrentText(self.style_manager.current_theme)
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addLayout(theme_layout)
        
        return layout
        
    def create_status_bar(self):
        """Create enhanced status information bar"""
        layout = QHBoxLayout()
        
        # Connection status
        connection_group = QGroupBox("Professional Connection Status")
        connection_layout = QHBoxLayout()
        
        self.connection_indicator = QLabel("●")
        self.connection_indicator.setStyleSheet("color: #ff4444; font-size: 24px; font-weight: bold;")
        self.connection_label = QLabel("No Hardware Connected")
        self.connection_label.setProperty("class", "status-disconnected")
        
        self.device_info_label = QLabel("Device: None")
        self.protocol_info_label = QLabel("Protocol: None")
        
        connection_layout.addWidget(self.connection_indicator)
        connection_layout.addWidget(self.connection_label)
        connection_layout.addWidget(self.device_info_label)
        connection_layout.addWidget(self.protocol_info_label)
        connection_layout.addStretch()
        
        connection_group.setLayout(connection_layout)
        
        # System status
        system_group = QGroupBox("System Status")
        system_layout = QVBoxLayout()
        
        self.mock_mode_label = QLabel("Mock Mode: Active")
        self.hardware_status_label = QLabel("Hardware: Not Detected")
        
        system_layout.addWidget(self.mock_mode_label)
        system_layout.addWidget(self.hardware_status_label)
        system_group.setLayout(system_layout)
        
        layout.addWidget(connection_group, 3)
        layout.addWidget(system_group, 1)
        
        return layout

    def create_applications_section(self):
        """Create the main applications launcher section with flexible layout"""
        layout = QVBoxLayout()
        
        # Section title
        apps_label = QLabel("Professional Diagnostic Applications")
        apps_label.setProperty("class", "subtitle")
        apps_font = QFont()
        apps_font.setPointSize(16)  # Larger title
        apps_font.setBold(True)
        apps_label.setFont(apps_font)
        apps_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        apps_label.setStyleSheet("margin-bottom: 20px;")
        
        layout.addWidget(apps_label)
        
        # Use a simple horizontal layout instead of scroll area for now
        apps_container = QWidget()
        apps_container_layout = QHBoxLayout(apps_container)
        apps_container_layout.setSpacing(25)  # More spacing between cards
        apps_container_layout.setContentsMargins(10, 10, 10, 10)
        
        # AutoDiag Card
        diag_card = self.create_app_card(
            "🔍", 
            "AutoDiag Pro", 
            "Vehicle Diagnostics", 
            "Professional DTC scanning, live data monitoring, and comprehensive system analysis with real hardware support",
            self.launch_diag,
            "primary"
        )
        
        # AutoECU Card
        ecu_card = self.create_app_card(
            "⚙", 
            "AutoECU Pro", 
            "ECU Programming", 
            "Advanced ECU reading/writing, module coding, adaptations, and professional programming tools",
            self.launch_ecu,
            "success"
        )
        
        # AutoKey Card
        key_card = self.create_app_card(
            "🔒", 
            "AutoKey Pro", 
            "Security Systems", 
            "Key programming, immobilizer access, security code calculation, and advanced security systems",
            self.launch_key,
            "danger"
        )
        
        apps_container_layout.addWidget(diag_card)
        apps_container_layout.addWidget(ecu_card)
        apps_container_layout.addWidget(key_card)
        
        layout.addWidget(apps_container)
        
        return layout

    def create_app_card(self, emoji, title, subtitle, description, handler, button_class):
        """Create an application launch card with improved layout"""
        card = QFrame()
        card.setMinimumHeight(380) # Increased height for better text display
        card.setMinimumWidth(350)   # Minimum width to prevent squeezing
        card.setFrameStyle(QFrame.Shape.Box)
        card.setStyleSheet("QFrame { margin: 5px; }")
        
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)  # Add padding
        
        # Header with emoji and title
        header_layout = QHBoxLayout()
        emoji_label = QLabel(emoji)
        emoji_label.setStyleSheet("font-size: 36px; margin-right: 10px;")
        emoji_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        title_layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setProperty("class", "title")
        title_font = QFont()
        title_font.setPointSize(16)  # Slightly larger title
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)  # Allow title to wrap
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setProperty("class", "subtitle")
        subtitle_label.setWordWrap(True)  # Allow subtitle to wrap
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.addStretch()
        
        header_layout.addWidget(emoji_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Description with better formatting
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            color: #888888; 
            font-size: 12px; 
            line-height: 1.6;
            margin-top: 10px;
            margin-bottom: 15px;
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Launch button with fixed height
        launch_btn = QPushButton("Launch Professional Edition")
        launch_btn.setProperty("class", button_class)
        launch_btn.setMinimumHeight(40)  # Fixed button height
        launch_btn.clicked.connect(handler)
        
        layout.addLayout(header_layout)
        layout.addWidget(desc_label)
        layout.addStretch()
        layout.addWidget(launch_btn)
        
        return card

    def detect_hardware(self):
        """Scan for professional diagnostic hardware"""
        self.log_message("Scanning for professional diagnostic hardware...")
        
        # Show progress dialog
        progress = QProgressDialog("Scanning for hardware...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        def scan_progress():
            """Simulate hardware scanning progress"""
            for i in range(101):
                progress.setValue(i)
                QApplication.processEvents()
                if progress.wasCanceled():
                    break
                time.sleep(0.01)
            
            progress.close()
            
            # Perform actual hardware detection
            self.available_devices = self.device_handler.detect_professional_devices()
            self.update_device_list()
            
            if self.available_devices:
                self.log_message(f"Found {len(self.available_devices)} professional device(s)")
                self.hardware_status_label.setText(f"Hardware: {len(self.available_devices)} devices found")
            else:
                self.log_message("No professional hardware detected - using mock mode")
                self.hardware_status_label.setText("Hardware: None (Mock Mode)")
        
        # Start scanning in background
        QTimer.singleShot(100, scan_progress)

    def update_device_list(self):
        """Update the device list widget"""
        self.device_list.clear()
        for device in self.available_devices:
            item = QListWidgetItem(str(device))
            item.setData(Qt.ItemDataRole.UserRole, device)
            self.device_list.addItem(item)

    def on_device_selected(self, item):
        """Handle device selection"""
        device = item.data(Qt.ItemDataRole.UserRole)
        self.log_message(f"Selected device: {device.name}")

    def connect_to_selected_device(self):
        """Connect to the selected professional device"""
        selected_items = self.device_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Device Selected", "Please select a device from the list")
            return
            
        device_item = selected_items[0]
        device = device_item.data(Qt.ItemDataRole.UserRole)
        
        self.log_message(f"Connecting to {device.name}...")
        
        if self.device_handler.connect_to_device(device.name):
            self.connection_indicator.setStyleSheet("color: #00ff00; font-size: 24px; font-weight: bold;")
            self.connection_label.setText(f"Connected to {device.name}")
            self.connection_label.setProperty("class", "status-connected")
            self.device_info_label.setText(f"Device: {device.name}")
            self.protocol_info_label.setText(f"Protocol: {self.device_handler.current_protocol.value}")
            self.mock_mode_label.setText("Mock Mode: Inactive")
            self.log_message(f"Successfully connected to {device.name}")
            
            # Test advanced features
            ecu_info = self.device_handler.read_ecu_identification_advanced()
            self.log_message(f"ECU Identification: {ecu_info.get('part_number', 'N/A')}")
        else:
            self.log_message(f"Failed to connect to {device.name}")
            QMessageBox.warning(self, "Connection Failed", f"Could not connect to {device.name}")

    def disconnect_device(self):
        """Disconnect from current device"""
        if self.device_handler.is_connected:
            self.device_handler.disconnect()
            self.connection_indicator.setStyleSheet("color: #ff4444; font-size: 24px; font-weight: bold;")
            self.connection_label.setText("Disconnected")
            self.connection_label.setProperty("class", "status-disconnected")
            self.device_info_label.setText("Device: None")
            self.protocol_info_label.setText("Protocol: None")
            self.mock_mode_label.setText("Mock Mode: Active")
            self.log_message("Disconnected from professional device")

    def create_quick_actions(self):
        """Create professional quick action buttons"""
        layout = QVBoxLayout()
        
        actions_label = QLabel("Professional Quick Actions")
        actions_label.setProperty("class", "subtitle")
        actions_font = QFont()
        actions_font.setPointSize(14)
        actions_font.setBold(True)
        actions_label.setFont(actions_font)
        
        layout.addWidget(actions_label)
        
        actions_layout = QHBoxLayout()
        
        quick_scan_btn = QPushButton("🔍 Professional DTC Scan")
        quick_scan_btn.setProperty("class", "primary")
        quick_scan_btn.clicked.connect(self.professional_dtc_scan)
        
        ecu_id_btn = QPushButton("📋 ECU Identification")
        ecu_id_btn.setProperty("class", "success")
        ecu_id_btn.clicked.connect(self.professional_ecu_identification)
        
        system_scan_btn = QPushButton("📊 System Analysis")
        system_scan_btn.setProperty("class", "primary")
        system_scan_btn.clicked.connect(self.professional_system_scan)
        
        coding_btn = QPushButton("⚙ Module Coding")
        coding_btn.setProperty("class", "danger")
        coding_btn.clicked.connect(self.professional_module_coding)
        
        actions_layout.addWidget(quick_scan_btn)
        actions_layout.addWidget(ecu_id_btn)
        actions_layout.addWidget(system_scan_btn)
        actions_layout.addWidget(coding_btn)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        return layout

    def professional_dtc_scan(self):
        """Perform professional DTC scan"""
        if not self.device_handler.is_connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to a professional device first")
            return
            
        self.log_message("Performing professional DTC scan...")
        dtcs = self.device_handler.scan_dtcs()
        if dtcs:
            self.log_message(f"Found {len(dtcs)} DTC(s):")
            for code, severity, description in dtcs:
                self.log_message(f"  {code}: {description} ({severity})")
        else:
            self.log_message("No DTCs found - system clean")

    def professional_ecu_identification(self):
        """Perform professional ECU identification"""
        if not self.device_handler.is_connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to a professional device first")
            return
            
        self.log_message("Reading advanced ECU identification...")
        ecu_info = self.device_handler.read_ecu_identification_advanced()
        
        info_text = f"""
Advanced ECU Identification:
Part Number: {ecu_info.get('part_number', 'N/A')}
Software: {ecu_info.get('software_version', 'N/A')}
Hardware: {ecu_info.get('hardware_version', 'N/A')}
Serial: {ecu_info.get('serial_number', 'N/A')}
Supplier: {ecu_info.get('supplier', 'N/A')}
        """
        QMessageBox.information(self, "ECU Identification", info_text.strip())

    def professional_system_scan(self):
        """Perform professional system scan"""
        if not self.device_handler.is_connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to a professional device first")
            return
            
        self.log_message("Performing professional system analysis...")
        system_info = self.device_handler.perform_advanced_diagnostic('system_scan')
        self.log_message("System analysis completed")

    def professional_module_coding(self):
        """Check module coding capabilities"""
        if not self.device_handler.is_connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to a professional device first")
            return
            
        self.log_message("Checking module coding capabilities...")
        coding_info = self.device_handler.perform_advanced_diagnostic('module_coding')
        self.log_message(f"Coding status: {coding_info.get('coding_status', 'N/A')}")

    def log_message(self, message):
        """Add message to log with timestamp"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_output.append(f"[{timestamp}] {message}")

    def change_theme(self, theme_name):
        """Change application theme"""
        self.style_manager.set_theme(theme_name)
        self.log_message(f"Theme changed to: {theme_name}")

    def create_log_section(self):
        """Create log output section"""
        layout = QVBoxLayout()
        
        log_label = QLabel("Professional Activity Log")
        log_label.setProperty("class", "subtitle")
        
        self.log_output = QTextEdit()
        self.log_output.setMaximumHeight(150)
        self.log_output.setReadOnly(True)
        
        log_controls = QHBoxLayout()
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.log_output.clear)
        
        export_log_btn = QPushButton("Export Professional Log")
        export_log_btn.clicked.connect(self.export_log)
        
        log_controls.addWidget(clear_log_btn)
        log_controls.addWidget(export_log_btn)
        log_controls.addStretch()
        
        layout.addWidget(log_label)
        layout.addWidget(self.log_output)
        layout.addLayout(log_controls)
        
        return layout

    def export_log(self):
        """Export log to file"""
        from datetime import datetime
        filename = f"diagautoclinic_pro_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write(self.log_output.toPlainText())
            self.log_message(f"Professional log exported to: {filename}")
            QMessageBox.information(self, "Export Successful", f"Professional log exported to:\\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export log: {e}")

    def launch_diag(self):
        """Launch AutoDiag Pro"""
        try:
            diag_path = os.path.join(os.path.dirname(__file__), 'AutoDiag', 'main.py')
            if os.path.exists(diag_path):
                subprocess.Popen([sys.executable, diag_path])
                self.log_message("Launched AutoDiag Pro - Professional Vehicle Diagnostics")
            else:
                QMessageBox.warning(self, "Application Not Found", "AutoDiag Pro application not found")
        except Exception as e:
            QMessageBox.critical(self, "Launch Error", f"Failed to launch AutoDiag Pro: {e}")

    def launch_ecu(self):
        """Launch AutoECU Pro"""
        try:
            ecu_path = os.path.join(os.path.dirname(__file__), 'AutoECU', 'main.py')
            if os.path.exists(ecu_path):
                subprocess.Popen([sys.executable, ecu_path])
                self.log_message("Launched AutoECU Pro - Professional ECU Programming")
            else:
                QMessageBox.warning(self, "Application Not Found", "AutoECU Pro application not found")
        except Exception as e:
            QMessageBox.critical(self, "Launch Error", f"Failed to launch AutoECU Pro: {e}")

    def launch_key(self):
        """Launch AutoKey Pro"""
        try:
            key_path = os.path.join(os.path.dirname(__file__), 'AutoKey', 'main.py')
            if os.path.exists(key_path):
                subprocess.Popen([sys.executable, key_path])
                self.log_message("Launched AutoKey Pro - Professional Key Programming")
            else:
                QMessageBox.warning(self, "Application Not Found", "AutoKey Pro application not found")
        except Exception as e:
            QMessageBox.critical(self, "Launch Error", f"Failed to launch AutoKey Pro: {e}")

    def resizeEvent(self, event):
        """Handle window resize for better responsive layout"""
        super().resizeEvent(event)
        # You can add dynamic layout adjustments here if needed
        pass

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("DiagAutoClinicOS Professional")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("AutoClinic Pro")
    
    # Create and show main window
    launcher = ProfessionalDiagAutoClinicLauncher()
    launcher.show()
    
    # Start application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
