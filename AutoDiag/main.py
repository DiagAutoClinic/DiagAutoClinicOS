#!/usr/bin/env python3
"""
AutoDiag - Professional Vehicle Diagnostic System
Modern interface with brand-specific diagnostics and theme support
"""

import sys
import os
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QPushButton, QLabel, QComboBox, QTabWidget, QFrame, QGroupBox,
    QTableWidget, QTableWidgetItem, QProgressBar, QTextEdit, QLineEdit,
    QHeaderView, QMessageBox, QSplitter, QScrollArea, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, QSettings
from PyQt6.QtGui import QFont, QPalette, QColor

# Import shared modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from style_manager import StyleManager
from brand_database import get_brand_list, get_brand_info

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutoDiagApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.style_manager = StyleManager()
        self.selected_brand = "Toyota"
        self.connected = False
        self.scanning = False
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("AutoDiag - Professional Vehicle Diagnostics")
        self.setGeometry(100, 100, 1400, 900)
        
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
        self.create_dashboard_tab()
        self.create_diagnostics_tab()
        self.create_live_data_tab()
        self.create_advanced_tab()
        self.create_brand_diagnostics_tab()
        
        # Create status bar
        self.create_status_bar()
        
        # Apply theme AFTER UI is created
        self.style_manager.set_theme("dark")
        
        # Initialize brand-specific data
        self.update_brand_specific_data()
        
        # Show the window
        self.show()
        
    def create_header(self, layout):
        """Create application header with theme and brand selectors"""
        header_widget = QWidget()
        header_widget.setMaximumHeight(80)
        header_layout = QHBoxLayout(header_widget)
        
        # Title
        title_label = QLabel("AutoDiag - Professional Vehicle Diagnostics")
        title_label.setProperty("class", "title")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # Spacer
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Brand selector
        brand_layout = QHBoxLayout()
        brand_label = QLabel("Vehicle Brand:")
        self.brand_combo = QComboBox()
        
        brands = get_brand_list()
        self.brand_combo.addItems(brands)
        self.brand_combo.setCurrentText(self.selected_brand)
        self.brand_combo.currentTextChanged.connect(self.on_brand_changed)
        
        brand_layout.addWidget(brand_label)
        brand_layout.addWidget(self.brand_combo)
        
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
        
        # Connection status
        self.connection_status = QLabel("🔴 Disconnected")
        self.connection_status.setProperty("class", "status-disconnected")
        
        header_layout.addLayout(brand_layout)
        header_layout.addSpacing(20)
        header_layout.addLayout(theme_layout)
        header_layout.addSpacing(20)
        header_layout.addWidget(self.connection_status)
        
        layout.addWidget(header_widget)
    
    def create_dashboard_tab(self):
        """Create dashboard tab with overview and quick actions"""
        dashboard_tab = QWidget()
        layout = QVBoxLayout(dashboard_tab)
        
        # Quick actions frame
        quick_frame = QFrame()
        quick_frame.setProperty("class", "diagnostic_frame")
        quick_layout = QHBoxLayout(quick_frame)
        
        # Quick action buttons
        scan_btn = QPushButton("🔍 Quick Scan")
        scan_btn.setProperty("class", "primary")
        scan_btn.clicked.connect(self.quick_scan)
        
        dtc_btn = QPushButton("⚡ Read DTCs")
        dtc_btn.setProperty("class", "primary")
        dtc_btn.clicked.connect(self.read_dtcs)
        
        live_btn = QPushButton("📊 Live Data")
        live_btn.setProperty("class", "primary")
        live_btn.clicked.connect(self.show_live_data)
        
        clear_btn = QPushButton("🔄 Clear Codes")
        clear_btn.setProperty("class", "danger")
        clear_btn.clicked.connect(self.clear_dtcs)
        
        quick_layout.addWidget(scan_btn)
        quick_layout.addWidget(dtc_btn)
        quick_layout.addWidget(live_btn)
        quick_layout.addWidget(clear_btn)
        quick_layout.addStretch()
        
        # Vehicle info frame
        vehicle_frame = QFrame()
        vehicle_frame.setProperty("class", "diagnostic_frame")
        vehicle_layout = QVBoxLayout(vehicle_frame)
        
        vehicle_title = QLabel("Vehicle Information")
        vehicle_title.setProperty("class", "subtitle")
        
        # Brand info
        self.brand_info_label = QLabel()
        self.brand_info_label.setWordWrap(True)
        
        # Protocol info
        self.protocol_info_label = QLabel()
        
        vehicle_layout.addWidget(vehicle_title)
        vehicle_layout.addWidget(self.brand_info_label)
        vehicle_layout.addWidget(self.protocol_info_label)
        
        # System status frame
        status_frame = QFrame()
        status_frame.setProperty("class", "diagnostic_frame")
        status_layout = QVBoxLayout(status_frame)
        
        status_title = QLabel("System Status")
        status_title.setProperty("class", "subtitle")
        
        # Status indicators
        status_grid = QHBoxLayout()
        
        self.obd_status = QLabel("OBD: Not Connected")
        self.obd_status.setProperty("class", "status-disconnected")
        
        self.protocol_status = QLabel("Protocol: Unknown")
        self.comm_status = QLabel("Communication: Idle")
        
        status_grid.addWidget(self.obd_status)
        status_grid.addWidget(self.protocol_status)
        status_grid.addWidget(self.comm_status)
        status_grid.addStretch()
        
        status_layout.addWidget(status_title)
        status_layout.addLayout(status_grid)
        
        # Layout organization
        top_layout = QHBoxLayout()
        top_layout.addWidget(quick_frame)
        
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(vehicle_frame)
        bottom_layout.addWidget(status_frame)
        
        layout.addLayout(top_layout)
        layout.addLayout(bottom_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(dashboard_tab, "Dashboard")
    
    def create_diagnostics_tab(self):
        """Create diagnostics tab with DTC reading and clearing"""
        diag_tab = QWidget()
        layout = QVBoxLayout(diag_tab)
        
        # DTC controls frame
        controls_frame = QFrame()
        controls_frame.setProperty("class", "diagnostic_frame")
        controls_layout = QHBoxLayout(controls_frame)
        
        # DTC action buttons
        read_dtc_btn = QPushButton("Read DTCs")
        read_dtc_btn.setProperty("class", "primary")
        read_dtc_btn.clicked.connect(self.read_dtcs)
        
        clear_dtc_btn = QPushButton("Clear DTCs")
        clear_dtc_btn.setProperty("class", "danger")
        clear_dtc_btn.clicked.connect(self.clear_dtcs)
        
        freeze_btn = QPushButton("Freeze Frame")
        freeze_btn.setProperty("class", "primary")
        freeze_btn.clicked.connect(self.read_freeze_frame)
        
        controls_layout.addWidget(read_dtc_btn)
        controls_layout.addWidget(clear_dtc_btn)
        controls_layout.addWidget(freeze_btn)
        controls_layout.addStretch()
        
        # DTC table
        dtc_frame = QFrame()
        dtc_frame.setProperty("class", "diagnostic_frame")
        dtc_layout = QVBoxLayout(dtc_frame)
        
        dtc_title = QLabel("Diagnostic Trouble Codes")
        dtc_title.setProperty("class", "subtitle")
        
        self.dtc_table = QTableWidget()
        self.dtc_table.setProperty("class", "diagnostic_table")
        self.dtc_table.setColumnCount(4)
        self.dtc_table.setHorizontalHeaderLabels(["DTC Code", "Description", "Status", "Severity"])
        self.dtc_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        dtc_layout.addWidget(dtc_title)
        dtc_layout.addWidget(self.dtc_table)
        
        layout.addWidget(controls_frame)
        layout.addWidget(dtc_frame)
        
        self.tab_widget.addTab(diag_tab, "Diagnostics")
    
    def create_live_data_tab(self):
        """Create live data monitoring tab"""
        live_tab = QWidget()
        layout = QVBoxLayout(live_tab)
        
        # Live data controls
        controls_frame = QFrame()
        controls_frame.setProperty("class", "diagnostic_frame")
        controls_layout = QHBoxLayout(controls_frame)
        
        start_btn = QPushButton("Start Monitoring")
        start_btn.setProperty("class", "success")
        start_btn.clicked.connect(self.start_live_data)
        
        stop_btn = QPushButton("Stop Monitoring")
        stop_btn.setProperty("class", "danger")
        stop_btn.clicked.connect(self.stop_live_data)
        
        self.record_check = QCheckBox("Record Data")
        
        controls_layout.addWidget(start_btn)
        controls_layout.addWidget(stop_btn)
        controls_layout.addWidget(self.record_check)
        controls_layout.addStretch()
        
        # Live data table
        data_frame = QFrame()
        data_frame.setProperty("class", "diagnostic_frame")
        data_layout = QVBoxLayout(data_frame)
        
        data_title = QLabel("Live Parameter Data")
        data_title.setProperty("class", "subtitle")
        
        self.live_data_table = QTableWidget()
        self.live_data_table.setProperty("class", "diagnostic_table")
        self.live_data_table.setColumnCount(3)
        self.live_data_table.setHorizontalHeaderLabels(["Parameter", "Value", "Unit"])
        self.live_data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        data_layout.addWidget(data_title)
        data_layout.addWidget(self.live_data_table)
        
        layout.addWidget(controls_frame)
        layout.addWidget(data_frame)
        
        self.tab_widget.addTab(live_tab, "Live Data")
    
    def create_advanced_tab(self):
        """Create advanced diagnostics tab"""
        advanced_tab = QWidget()
        layout = QVBoxLayout(advanced_tab)
        
        # Advanced controls
        controls_frame = QFrame()
        controls_frame.setProperty("class", "diagnostic_frame")
        controls_layout = QHBoxLayout(controls_frame)
        
        # Advanced function buttons
        actuator_btn = QPushButton("Actuator Test")
        actuator_btn.setProperty("class", "primary")
        
        adaptation_btn = QPushButton("Adaptations")
        adaptation_btn.setProperty("class", "primary")
        
        coding_btn = QPushButton("Coding")
        coding_btn.setProperty("class", "primary")
        
        controls_layout.addWidget(actuator_btn)
        controls_layout.addWidget(adaptation_btn)
        controls_layout.addWidget(coding_btn)
        controls_layout.addStretch()
        
        # System info
        info_frame = QFrame()
        info_frame.setProperty("class", "diagnostic_frame")
        info_layout = QVBoxLayout(info_frame)
        
        info_title = QLabel("System Information")
        info_title.setProperty("class", "subtitle")
        
        self.system_info_text = QTextEdit()
        self.system_info_text.setProperty("class", "procedure_viewer")
        self.system_info_text.setMaximumHeight(200)
        
        info_layout.addWidget(info_title)
        info_layout.addWidget(self.system_info_text)
        
        layout.addWidget(controls_frame)
        layout.addWidget(info_frame)
        layout.addStretch()
        
        self.tab_widget.addTab(advanced_tab, "Advanced")
    
    def create_brand_diagnostics_tab(self):
        """Create brand-specific diagnostics tab"""
        brand_tab = QWidget()
        layout = QVBoxLayout(brand_tab)
        
        # Brand-specific modules
        modules_frame = QFrame()
        modules_frame.setProperty("class", "diagnostic_frame")
        modules_layout = QVBoxLayout(modules_frame)
        
        modules_title = QLabel("Brand-Specific Control Modules")
        modules_title.setProperty("class", "subtitle")
        
        self.modules_table = QTableWidget()
        self.modules_table.setProperty("class", "diagnostic_table")
        self.modules_table.setColumnCount(4)
        self.modules_table.setHorizontalHeaderLabels(["Module", "Address", "Protocol", "Status"])
        self.modules_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        modules_layout.addWidget(modules_title)
        modules_layout.addWidget(self.modules_table)
        
        # Brand-specific procedures
        procedures_frame = QFrame()
        procedures_frame.setProperty("class", "diagnostic_frame")
        procedures_layout = QVBoxLayout(procedures_frame)
        
        procedures_title = QLabel("Brand-Specific Procedures")
        procedures_title.setProperty("class", "subtitle")
        
        self.procedures_text = QTextEdit()
        self.procedures_text.setProperty("class", "procedure_viewer")
        self.procedures_text.setMaximumHeight(200)
        
        procedures_layout.addWidget(procedures_title)
        procedures_layout.addWidget(self.procedures_text)
        
        layout.addWidget(modules_frame)
        layout.addWidget(procedures_frame)
        
        self.tab_widget.addTab(brand_tab, "Brand Diagnostics")
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_label = QLabel("Ready to connect to vehicle")
        self.statusBar().addWidget(self.status_label)
        
        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar)
    
    def on_theme_changed(self, theme_name):
        """Handle theme change"""
        theme_info = self.style_manager.get_theme_info()
        for theme_id, info in theme_info.items():
            if info['name'] == theme_name:
                self.style_manager.set_theme(theme_id)
                break
    
    def on_brand_changed(self, brand_name):
        """Handle brand selection change"""
        self.selected_brand = brand_name
        self.update_brand_specific_data()
        
        # Show brand-specific tips
        self.show_brand_tips(brand_name)
    
    def update_brand_specific_data(self):
        """Update UI with brand-specific information"""
        brand_info = get_brand_info(self.selected_brand)
        
        # Update brand info label
        if hasattr(self, 'brand_info_label'):
            self.brand_info_label.setText(
                f"Brand: {self.selected_brand}\n"
                f"Region: {brand_info.get('region', 'N/A')}\n"
                f"Market Share: {brand_info.get('market_share', 'N/A')}"
            )
        
        # Update protocol info
        if hasattr(self, 'protocol_info_label'):
            protocols = brand_info.get('diagnostic_protocols', [])
            self.protocol_info_label.setText(
                f"Protocols: {', '.join(protocols)}\n"
                f"OBD Protocol: {brand_info.get('obd_protocol', 'N/A')}"
            )
        
        # Update brand-specific modules
        self.update_brand_modules()
        
        # Update brand procedures
        self.update_brand_procedures()
    
    def update_brand_modules(self):
        """Update modules table with brand-specific ECUs"""
        brand_info = get_brand_info(self.selected_brand)
        common_ecus = brand_info.get('common_ecus', [])
        
        self.modules_table.setRowCount(len(common_ecus))
        for row, ecu in enumerate(common_ecus):
            self.modules_table.setItem(row, 0, QTableWidgetItem(ecu))
            self.modules_table.setItem(row, 1, QTableWidgetItem(self.get_ecu_address(ecu)))
            self.modules_table.setItem(row, 2, QTableWidgetItem(self.get_ecu_protocol(ecu)))
            self.modules_table.setItem(row, 3, QTableWidgetItem("Not Scanned"))
    
    def update_brand_procedures(self):
        """Update brand-specific procedures"""
        procedures = self.get_brand_procedures(self.selected_brand)
        self.procedures_text.setText(procedures)
    
    def get_ecu_address(self, ecu_name):
        """Get typical ECU addresses for brands"""
        address_map = {
            "ECM": "0x7E0", "PCM": "0x7E0", "Engine ECU": "0x7E0", "DME": "0x7E0",
            "TCM": "0x7E1", "Transmission": "0x7E1", "EGS": "0x7E1",
            "ABS": "0x7E2", "ESP": "0x7E2", "DSC": "0x7E2",
            "SRS": "0x7E3", "Airbag": "0x7E3",
            "BCM": "0x7E4", "Body ECU": "0x7E4", "SAM": "0x7E4",
            "Instrument Cluster": "0x7E5", "IC": "0x7E5"
        }
        return address_map.get(ecu_name, "0x7XX")
    
    def get_ecu_protocol(self, ecu_name):
        """Get typical ECU protocols"""
        brand_info = get_brand_info(self.selected_brand)
        protocols = brand_info.get('diagnostic_protocols', [])
        return protocols[0] if protocols else "UDS"
    
    def get_brand_procedures(self, brand):
        """Get brand-specific diagnostic procedures"""
        procedures = {
            "Toyota": """Toyota Diagnostic Procedures:
            
1. Quick Scan:
   - Connect with ISO 15765-4 (CAN)
   - Use TechStream compatible commands
   - Access all ECUs via gateway

2. DTC Reading:
   - Standard OBD-II PIDs
   - Enhanced manufacturer codes
   - Freeze frame data available

3. Live Data:
   - Real-time parameter monitoring
   - Custom PID support
   - Graphing capabilities""",

            "Volkswagen": """VW/Audi Diagnostic Procedures:
            
1. Quick Scan:
   - Use UDS protocol (ISO 14229)
   - Access via OBD or direct CAN
   - Full module communication

2. DTC Reading:
   - Manufacturer-specific codes
   - Extended fault memory
   - Environment data recording

3. Coding/Adaptation:
   - Online coding required
   - SCN coding for some modules
   - Component protection""",

            "BMW": """BMW Diagnostic Procedures:
            
1. Quick Scan:
   - Use ISTA/D compatible protocols
   - K+CAN bus systems
   - Ethernet diagnostics for newer models

2. DTC Reading:
   - BMW-specific fault codes
   - Detailed fault descriptions
   - Service plan integration

3. Programming:
   - ISTA/P required for flash
   - ICOM interface recommended
   - Online connection needed"""
        }
        
        return procedures.get(brand, f"Standard diagnostic procedures for {brand} vehicles.")
    
    def show_brand_tips(self, brand_name):
        """Show brand-specific diagnostic tips"""
        tips = {
            "Toyota": "Tip: Use TechStream compatible protocols for full system access",
            "Volkswagen": "Tip: VCDS/ODIS protocols provide deepest module access",
            "BMW": "Tip: ISTA-D/ISTA-P required for advanced programming functions",
            "Mercedes-Benz": "Tip: XENTRY diagnostics needed for SCN coding and updates",
            "Ford": "Tip: IDS/FDRS provides complete module programming capabilities",
            "Hyundai": "Tip: GDS is the official diagnostic system for full access",
            "Nissan": "Tip: CONSULT-III+ required for NATS immobilizer programming"
        }
        
        if brand_name in tips:
            self.status_label.setText(f"Brand Tip: {tips[brand_name]}")
    
    def quick_scan(self):
        """Perform quick vehicle scan"""
        self.status_label.setText("Performing quick scan...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Simulate scan progress
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.update_scan_progress)
        self.scan_timer.start(100)
        
        # Update connection status
        self.connection_status.setText("🟡 Scanning...")
        self.connection_status.setProperty("class", "status-warning")
        self.obd_status.setText("OBD: Scanning")
    
    def update_scan_progress(self):
        """Update scan progress"""
        current = self.progress_bar.value()
        if current < 100:
            self.progress_bar.setValue(current + 10)
        else:
            self.scan_timer.stop()
            self.progress_bar.setVisible(False)
            
            # Update connection status
            self.connection_status.setText("🟢 Connected")
            self.connection_status.setProperty("class", "status-connected")
            self.obd_status.setText("OBD: Connected")
            self.connected = True
            
            # Add sample data
            self.add_sample_dtc_data()
            self.add_sample_live_data()
            
            self.status_label.setText("Quick scan completed successfully")
    
    def read_dtcs(self):
        """Read diagnostic trouble codes"""
        if not self.connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to a vehicle first")
            return
        
        self.status_label.setText("Reading diagnostic trouble codes...")
        
        # Simulate DTC reading
        QTimer.singleShot(2000, self.dtc_reading_complete)
    
    def dtc_reading_complete(self):
        """Called when DTC reading completes"""
        self.add_sample_dtc_data()
        self.status_label.setText("DTC reading completed")
    
    def clear_dtcs(self):
        """Clear diagnostic trouble codes"""
        if not self.connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to a vehicle first")
            return
        
        reply = QMessageBox.question(self, "Clear DTCs", 
                                   "Are you sure you want to clear all diagnostic trouble codes?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.dtc_table.setRowCount(0)
            self.status_label.setText("DTCs cleared successfully")
    
    def read_freeze_frame(self):
        """Read freeze frame data"""
        if not self.connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to a vehicle first")
            return
        
        self.status_label.setText("Reading freeze frame data...")
    
    def start_live_data(self):
        """Start live data monitoring"""
        if not self.connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to a vehicle first")
            return
        
        self.status_label.setText("Starting live data monitoring...")
        self.add_sample_live_data()
    
    def stop_live_data(self):
        """Stop live data monitoring"""
        self.status_label.setText("Live data monitoring stopped")
    
    def add_sample_dtc_data(self):
        """Add sample DTC data to table"""
        sample_dtcs = [
            ["P0300", "Random/Multiple Cylinder Misfire Detected", "Confirmed", "Medium"],
            ["P0171", "System Too Lean (Bank 1)", "Pending", "Low"],
            ["C1234", "ABS Wheel Speed Sensor Fault", "Confirmed", "High"],
            ["B1345", "ECU Communication Error", "Confirmed", "High"]
        ]
        
        self.dtc_table.setRowCount(len(sample_dtcs))
        for row, dtc in enumerate(sample_dtcs):
            for col, value in enumerate(dtc):
                self.dtc_table.setItem(row, col, QTableWidgetItem(value))
    
    def add_sample_live_data(self):
        """Add sample live data to table"""
        sample_data = [
            ["Engine RPM", "2,350", "RPM"],
            ["Vehicle Speed", "65", "km/h"],
            ["Coolant Temp", "92", "°C"],
            ["MAF Sensor", "4.8", "g/s"],
            ["Throttle Position", "24.5", "%"],
            ["Fuel Pressure", "350", "kPa"],
            ["O2 Sensor B1S1", "0.45", "V"],
            ["Intake Air Temp", "35", "°C"]
        ]
        
        self.live_data_table.setRowCount(len(sample_data))
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                self.live_data_table.setItem(row, col, QTableWidgetItem(value))
    
    def show_live_data(self):
        """Switch to live data tab"""
        self.tab_widget.setCurrentIndex(2)  # Live Data tab index

def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("AutoDiag")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("DiagAutoClinicOS")
    
    # Create and show main window
    window = AutoDiagApp()
    
    # Start the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()