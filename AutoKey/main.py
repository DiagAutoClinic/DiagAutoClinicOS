#!/usr/bin/env python3
"""
AutoKey - Automotive Key Programming Tool
Modern interface with theme support
"""

import sys
import os
import re
import logging
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QComboBox, QTabWidget,
                            QGroupBox, QTableWidget, QTableWidgetItem, QProgressBar,
                            QTextEdit, QLineEdit, QHeaderView, QRadioButton, QInputDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# Setup logging (no file output to avoid persistence risks)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import custom modules safely
try:
    from style_manager import StyleManager
    from brand_database import get_brand_info, get_brand_list
except ImportError as e:
    logger.error(f"Failed to import custom modules: {e}")
    sys.exit(1)

class AutoKeyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            self.style_manager = StyleManager()
        except Exception as e:
            logger.error(f"Failed to initialize StyleManager: {e}")
            sys.exit(1)
        self.selected_brand = "Toyota"
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("AutoKey - Key Programming Tool")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create header
        self.create_header(main_layout)
        
        # Create main tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_key_programming_tab()
        self.create_transponder_tab()
        self.create_vehicle_info_tab()
        
        # Create status bar
        self.create_status_bar()
        
        # Apply theme AFTER UI is created
        try:
            self.style_manager.set_theme("dark")
        except Exception as e:
            logger.warning(f"Failed to apply theme: {e}, using default")
        
        # Show the window
        self.show()
        
    def create_header(self, layout):
        """Create application header with theme selector"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        
        # Title
        title_label = QLabel("AutoKey - Professional Key Programming")
        title_label.setProperty("class", "title")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # Theme selector
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        
        try:
            theme_info = self.style_manager.get_theme_info()
            for theme_id, info in theme_info.items():
                if isinstance(info, dict) and 'name' in info:
                    self.theme_combo.addItem(info['name'], theme_id)
                else:
                    logger.warning(f"Invalid theme info for {theme_id}")
        except Exception as e:
            logger.error(f"Failed to load themes: {e}")
        
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        
        header_layout.addWidget(title_label)
        header_layout.addLayout(theme_layout)
        
        layout.addWidget(header_widget)
        
    def create_key_programming_tab(self):
        """Create key programming tab"""
        key_tab = QWidget()
        layout = QVBoxLayout(key_tab)

        # Vehicle information
        vehicle_frame = QWidget()
        vehicle_frame.setProperty("class", "vehicle_info")
        vehicle_layout = QVBoxLayout(vehicle_frame)
        
        make_label = QLabel("Toyota Camry 2020")
        make_label.setProperty("class", "vehicle_make")
        
        model_label = QLabel("2.5L Hybrid - Smart Key System")
        model_label.setProperty("class", "vehicle_model")
        
        vehicle_layout.addWidget(make_label)
        vehicle_layout.addWidget(model_label)
        
        # Key programming controls
        key_group = QGroupBox("Key Programming")
        key_group.setProperty("class", "key_frame")
        key_layout = QVBoxLayout(key_group)
        
        # Security code input
        security_layout = QHBoxLayout()
        security_label = QLabel("Security Code:")
        self.security_input = QLineEdit()
        self.security_input.setProperty("class", "security_code")
        self.security_input.setPlaceholderText("Enter vehicle security code")
        self.security_input.setMaxLength(8)
        
        security_layout.addWidget(security_label)
        security_layout.addWidget(self.security_input)
        security_layout.addStretch()
        
        # Programming buttons
        btn_layout = QHBoxLayout()
        
        program_btn = QPushButton("Program New Key")
        program_btn.setProperty("class", "key_button program_key_button")
        program_btn.clicked.connect(self.program_key)
        
        clone_btn = QPushButton("Clone Key")
        clone_btn.setProperty("class", "key_button clone_key_button")
        clone_btn.clicked.connect(self.clone_key)
        
        reset_btn = QPushButton("Reset System")
        reset_btn.setProperty("class", "key_button reset_key_button")
        reset_btn.clicked.connect(self.reset_system)
        
        btn_layout.addWidget(program_btn)
        btn_layout.addWidget(clone_btn)
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        
        # Key status
        status_layout = QHBoxLayout()
        self.key_status = QLabel("No Key Detected")
        self.key_status.setProperty("class", "key_status_unprogrammed")
        
        self.immobilizer_status = QLabel("Immobilizer: Active")
        self.immobilizer_status.setProperty("class", "immobilizer_active")
        
        status_layout.addWidget(QLabel("Key Status:"))
        status_layout.addWidget(self.key_status)
        status_layout.addWidget(self.immobilizer_status)
        status_layout.addStretch()
        
        key_layout.addLayout(security_layout)
        key_layout.addLayout(btn_layout)
        key_layout.addLayout(status_layout)
        
        layout.addWidget(vehicle_frame)
        layout.addWidget(key_group)
        layout.addStretch()
        
        self.tab_widget.addTab(key_tab, "Key Programming")
        
    def create_transponder_tab(self):
        """Create transponder management tab"""
        transponder_tab = QWidget()
        layout = QVBoxLayout(transponder_tab)
        
        # Transponder group
        transponder_group = QGroupBox("Transponder Management")
        transponder_group.setProperty("class", "transponder_group")
        transponder_layout = QVBoxLayout(transponder_group)
        
        # Transponder table
        self.transponder_table = QTableWidget()
        self.transponder_table.setProperty("class", "key_data_table")
        self.transponder_table.setColumnCount(4)
        self.transponder_table.setHorizontalHeaderLabels(["Key ID", "Type", "Status", "Vehicle"])
        self.transponder_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Add sample data
        self.add_sample_transponder_data()
        
        transponder_layout.addWidget(self.transponder_table)
        
        layout.addWidget(transponder_group)
        layout.addStretch()
        
        self.tab_widget.addTab(transponder_tab, "Transponders")
        
    def create_vehicle_info_tab(self):
        """Create vehicle information tab"""
        vehicle_tab = QWidget()
        layout = QVBoxLayout(vehicle_tab)
        
        vehicle_group = QGroupBox("Vehicle Information")
        vehicle_group.setProperty("class", "key_frame")
        vehicle_layout = QVBoxLayout(vehicle_group)
        
        # Vehicle details table
        details_table = QTableWidget()
        details_table.setProperty("class", "key_data_table")
        details_table.setColumnCount(2)
        details_table.setHorizontalHeaderLabels(["Property", "Value"])
        details_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Load vehicle data securely (mock for now)
        vehicle_data = [
            ["VIN", "REDACTED_VIN_123"],  # Avoid hardcoded VIN
            ["Make", "Toyota"],
            ["Model", "Camry"],
            ["Year", "2020"],
            ["Key System", "Smart Key"],
            ["Transponder", "ID4C / 4D"],
            ["Keys Programmed", "2/5"]
        ]
        
        details_table.setRowCount(len(vehicle_data))
        for row, data in enumerate(vehicle_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Prevent user edits
                details_table.setItem(row, col, item)
        
        vehicle_layout.addWidget(details_table)
        
        layout.addWidget(vehicle_group)
        layout.addStretch()
        
        self.tab_widget.addTab(vehicle_tab, "Vehicle Info")
        
    def create_status_bar(self):
        """Create status bar"""
        self.status_label = QLabel("Ready to program keys")
        self.statusBar().addWidget(self.status_label)
        
    def on_theme_changed(self, theme_name):
        """Handle theme change with validation"""
        try:
            theme_info = self.style_manager.get_theme_info()
            for theme_id, info in theme_info.items():
                if info.get('name') == theme_name:
                    self.style_manager.set_theme(theme_id)
                    logger.info(f"Applied theme: {theme_name}")
                    return
            logger.warning(f"Theme {theme_name} not found")
        except Exception as e:
            logger.error(f"Failed to change theme: {e}")
                
    def add_sample_transponder_data(self):
        """Add sample transponder data securely"""
        sample_data = [
            ["KEY001", "Smart Key", "Programmed", "Generic Vehicle"],  # Avoid specific vehicle data
            ["KEY002", "Smart Key", "Programmed", "Generic Vehicle"],
            ["KEY003", "Mechanical", "Unprogrammed", "N/A"],
            ["TSP001", "ID4C", "Blank", "N/A"]
        ]
        
        self.transponder_table.setRowCount(len(sample_data))
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Prevent user edits
                self.transponder_table.setItem(row, col, item)
                
    def validate_security_code(self, code: str) -> bool:
        """Validate security code (alphanumeric, 4-8 chars)"""
        if not code:
            return False
        if not (4 <= len(code) <= 8 and re.match(r'^[a-zA-Z0-9]+$', code)):
            logger.warning(f"Invalid security code format: {code}")
            return False
        return True
    
    def check_auth(self) -> bool:
        """Mock authentication check (replace with real auth in production)"""
        # For demo, use a simple PIN dialog; replace with secure auth (e.g., keyring)
        pin, ok = QInputDialog.getText(self, "Authentication", "Enter PIN:", QLineEdit.EchoMode.Password)
        if ok and pin == "1234":  # Mock PIN; use secure storage in production
            logger.info("Authentication successful")
            return True
        logger.warning("Authentication failed")
        return False

    def program_key(self):
        """Simulate key programming with validation and auth"""
        if not self.check_auth():
            self.status_label.setText("Authentication failed")
            return
            
        code = self.security_input.text().strip()
        if not self.validate_security_code(code):
            self.status_label.setText("Invalid security code (alphanumeric, 4-8 chars)")
            return
            
        logger.info("Initiating key programming")
        self.status_label.setText("Programming new key...")
        self.key_status.setText("Programming...")
        self.key_status.setProperty("class", "key_status_learning")
        
        # Simulate programming process
        QTimer.singleShot(3000, self.programming_complete)
        
    def programming_complete(self):
        """Called when programming completes"""
        logger.info("Key programming completed")
        self.status_label.setText("Key programmed successfully!")
        self.key_status.setText("Programmed")
        self.key_status.setProperty("class", "key_status_programmed")
        
    def clone_key(self):
        """Simulate key cloning with auth"""
        if not self.check_auth():
            self.status_label.setText("Authentication failed")
            return
        logger.info("Initiating key cloning")
        self.status_label.setText("Cloning key...")
        
    def reset_system(self):
        """Simulate system reset with auth"""
        if not self.check_auth():
            self.status_label.setText("Authentication failed")
            return
        logger.info("Initiating system reset")
        self.status_label.setText("Resetting key system...")
        self.security_input.clear()
        self.key_status.setText("No Key Detected")
        self.key_status.setProperty("class", "key_status_unprogrammed")
    
    def closeEvent(self, event):
        """Ensure cleanup on close"""
        logger.info("Closing AutoKeyApp")
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("AutoKey")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("DiagAutoClinicOS")
    
    try:
        window = AutoKeyApp()
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
