#!/usr/bin/env python3
"""
AutoECU - Automotive ECU Programming Tool
Modern interface with theme support
"""

import sys
import os
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QComboBox, QTabWidget,
                            QGroupBox, QTableWidget, QTableWidgetItem, QProgressBar,
                            QTextEdit, QLineEdit, QHeaderView)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# Import the style manager
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared'))
sys.path.append(shared_path)
from style_manager import StyleManager
from brand_database import get_brand_info, get_brand_list

class AutoECUApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.style_manager = StyleManager()
        self.selected_brand = "Toyota"
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("AutoECU - ECU Programming Tool")
        self.setGeometry(100, 100, 1200, 800)
        
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
        self.create_ecu_scan_tab()
        self.create_programming_tab()
        self.create_parameters_tab()
        self.create_diagnostics_tab()
        
        # Create status bar
        self.create_status_bar()
        
        # Apply theme AFTER UI is created
        self.style_manager.set_theme("dark")
        
        # Show the window
        self.show()
        
    def create_header(self, layout):
        """Create application header with theme selector"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        
        # Title
        title_label = QLabel("AutoECU - Professional ECU Programming")
        title_label.setProperty("class", "title")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # Theme selector
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        
        theme_info = self.style_manager.get_theme_info()
        for theme_id, info in theme_info.items():
            self.theme_combo.addItem(info['name'], theme_id)
        
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        
        header_layout.addWidget(title_label)
        header_layout.addLayout(theme_layout)
        
        layout.addWidget(header_widget)

    def create_ecu_scan_tab(self):
        """Create ECU scan and detection tab"""
        scan_tab = QWidget()
        layout = QVBoxLayout(scan_tab)
        
        # Scan controls
        scan_group = QGroupBox("ECU Detection")
        scan_group.setProperty("class", "ecu_frame")
        scan_layout = QVBoxLayout(scan_group)
        
        # Scan button
        scan_btn = QPushButton("Scan for ECUs")
        scan_btn.setProperty("class", "program_button")
        scan_btn.clicked.connect(self.scan_ecus)
        
        # ECU table
        self.ecu_table = QTableWidget()
        self.ecu_table.setProperty("class", "ecu_data_table")
        self.ecu_table.setColumnCount(4)
        self.ecu_table.setHorizontalHeaderLabels(["ECU Name", "Protocol", "Status", "Address"])
        self.ecu_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        scan_layout.addWidget(scan_btn)
        scan_layout.addWidget(self.ecu_table)
        
        # Status frame
        status_frame = QWidget()
        status_frame.setProperty("class", "ecu_frame")
        status_layout = QHBoxLayout(status_frame)
        
        self.connection_status = QLabel("Disconnected")
        self.connection_status.setProperty("class", "ecu_status_disconnected")
        
        self.scan_progress = QProgressBar()
        self.scan_progress.setProperty("class", "ecu_progress")
        self.scan_progress.setVisible(False)
        
        status_layout.addWidget(QLabel("Status:"))
        status_layout.addWidget(self.connection_status)
        status_layout.addWidget(self.scan_progress)
        status_layout.addStretch()
        
        layout.addWidget(scan_group)
        layout.addWidget(status_frame)
        layout.addStretch()
        
        self.tab_widget.addTab(scan_tab, "ECU Scan")
        
    def create_programming_tab(self):
        """Create ECU programming tab"""
        prog_tab = QWidget()
        layout = QVBoxLayout(prog_tab)
        
        # Programming controls
        prog_group = QGroupBox("ECU Programming")
        prog_group.setProperty("class", "ecu_frame")
        prog_layout = QVBoxLayout(prog_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        read_btn = QPushButton("Read ECU")
        read_btn.setProperty("class", "program_button read_button")
        read_btn.clicked.connect(self.read_ecu)
        
        write_btn = QPushButton("Write ECU")
        write_btn.setProperty("class", "program_button write_button")
        write_btn.clicked.connect(self.write_ecu)
        
        btn_layout.addWidget(read_btn)
        btn_layout.addWidget(write_btn)
        btn_layout.addStretch()

        # Hex viewer
        hex_label = QLabel("ECU Memory View:")
        self.hex_viewer = QTextEdit()
        self.hex_viewer.setProperty("class", "hex_viewer")
        self.hex_viewer.setPlaceholderText("ECU memory content will appear here...")
        
        prog_layout.addLayout(btn_layout)
        prog_layout.addWidget(hex_label)
        prog_layout.addWidget(self.hex_viewer)
        
        layout.addWidget(prog_group)
        layout.addStretch()
        
        self.tab_widget.addTab(prog_tab, "Programming")
        
    def create_parameters_tab(self):
        """Create parameter editing tab"""
        param_tab = QWidget()
        layout = QVBoxLayout(param_tab)
        
        param_group = QGroupBox("ECU Parameters")
        param_group.setProperty("class", "ecu_frame")
        param_layout = QVBoxLayout(param_group)
        
        # Parameter table
        self.param_table = QTableWidget()
        self.param_table.setProperty("class", "ecu_data_table")
        self.param_table.setColumnCount(3)
        self.param_table.setHorizontalHeaderLabels(["Parameter", "Value", "Unit"])
        self.param_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        param_layout.addWidget(self.param_table)
        
        layout.addWidget(param_group)
        layout.addStretch()
        
        self.tab_widget.addTab(param_tab, "Parameters")
        
    def create_diagnostics_tab(self):
        """Create diagnostics tab"""
        diag_tab = QWidget()
        layout = QVBoxLayout(diag_tab)
        
        diag_group = QGroupBox("ECU Diagnostics")
        diag_group.setProperty("class", "ecu_frame")
        diag_layout = QVBoxLayout(diag_group)
        
        # DTC table
        self.dtc_table = QTableWidget()
        self.dtc_table.setProperty("class", "ecu_data_table")
        self.dtc_table.setColumnCount(3)
        self.dtc_table.setHorizontalHeaderLabels(["DTC Code", "Description", "Status"])
        self.dtc_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        diag_layout.addWidget(self.dtc_table)
        
        layout.addWidget(diag_group)
        layout.addStretch()
        
        self.tab_widget.addTab(diag_tab, "Diagnostics")
        
    def create_status_bar(self):
        """Create status bar"""
        self.status_label = QLabel("Ready")
        self.statusBar().addWidget(self.status_label)
        
    def on_theme_changed(self, theme_name):
        """Handle theme change"""
        try:
            theme_info = self.style_manager.get_theme_info()
            for theme_id, info in theme_info.items():
                if info['name'] == theme_name:
                    self.style_manager.set_theme(theme_id)
                    break
        except Exception as e:
            self.status_label.setText("Error changing theme")
                
    def scan_ecus(self):
        """Simulate ECU scanning"""
        try:
            self.connection_status.setText("Scanning...")
            self.connection_status.setProperty("class", "ecu_status_reading")
            self.scan_progress.setVisible(True)
            self.scan_progress.setValue(0)
            
            # Simulate scan progress
            self.scan_timer = QTimer()
            self.scan_timer.timeout.connect(self.update_scan_progress)
            self.scan_timer.start(100)
        except Exception as e:
            self.status_label.setText("Error during ECU scan")
        
    def update_scan_progress(self):
        """Update scan progress"""
        try:
            current = self.scan_progress.value()
            if current < 100:
                self.scan_progress.setValue(current + 10)
            else:
                self.scan_timer.stop()
                self.scan_progress.setVisible(False)
                self.connection_status.setText("Connected")
                self.connection_status.setProperty("class", "ecu_status_connected")
                
                # Add sample ECU data
                self.add_sample_ecu_data()
        except Exception as e:
            self.status_label.setText("Error during scan progress")
            
    def add_sample_ecu_data(self):
        """Add sample ECU data to table"""
        sample_data = [
            ["Engine Control Module", "CAN", "Online", "0x7E0"],
            ["Transmission Control", "CAN", "Online", "0x7E1"],
            ["ABS Module", "CAN", "Online", "0x7E2"],
            ["Body Control Module", "LIN", "Online", "0x7E3"]
        ]
        
        self.ecu_table.setRowCount(len(sample_data))
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                clean_value = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', value)
                self.ecu_table.setItem(row, col, QTableWidgetItem(clean_value))
                
    def read_ecu(self):
        """Simulate ECU reading"""
        try:
            self.status_label.setText("Reading ECU memory...")
            self.hex_viewer.setText("0000: 12 34 56 78 9A BC DE F0  11 22 33 44 55 66 77 88\n"
                                   "0010: FF EE DD CC BB AA 99 88  77 66 55 44 33 22 11 00\n"
                                   "0020: 01 23 45 67 89 AB CD EF  FE DC BA 98 76 54 32 10")
        except Exception as e:
            self.status_label.setText("Error reading ECU")
        
    def write_ecu(self):
        """Simulate ECU writing"""
        try:
            self.status_label.setText("Writing to ECU...")
        except Exception as e:
            self.status_label.setText("Error writing ECU")

def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("AutoECU")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("DiagAutoClinicOS")
    
    try:
        window = AutoECUApp()
        sys.exit(app.exec())
    except Exception as e:
        sys.exit(1)

if __name__ == "__main__":
    main()
