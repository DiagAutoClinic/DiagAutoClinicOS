#!/usr/bin/env python3
"""
AutoDiag - Professional Vehicle Diagnostic System
Modern interface with brand-specific diagnostics and theme support
"""

import sys
import os
import logging
import re
import serial
from typing import List, Tuple
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QPushButton, QLabel, QComboBox, QTabWidget, QFrame, QGroupBox,
    QTableWidget, QTableWidgetItem, QProgressBar, QTextEdit, QLineEdit,
    QHeaderView, QMessageBox, QSplitter, QScrollArea, QCheckBox,
    QInputDialog, QDialog, QFormLayout
)
from PyQt6.QtCore import Qt, QTimer, QSettings
from PyQt6.QtGui import QFont, QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Import shared modules
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared'))
sys.path.append(shared_path)
try:
    from style_manager import StyleManager
    from brand_database import get_brand_list, get_brand_info
except ImportError as e:
    logging.error(f"Failed to import shared modules: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeviceManager:
    """Handle ELM327/J2534 device communication"""
    def __init__(self):
        self.serial = None
        self.port = None
        self.baudrate = 38400
        self.protocol = "AUTO"

    def validate_port(self, port: str) -> bool:
        """Validate serial port format"""
        pattern = r'^/(dev/)?(ttyUSB|ttyACM|ttyS)[0-9]+$|^COM[1-9][0-9]*$'
        return bool(re.match(pattern, port, re.IGNORECASE))

    def connect(self, port: str, baudrate: int, protocol: str) -> bool:
        """Connect to ELM327 device"""
        try:
            if not self.validate_port(port):
                raise ValueError(f"Invalid port: {port}")
            self.port = port
            self.baudrate = baudrate
            self.protocol = protocol
            self.serial = serial.Serial(port, baudrate, timeout=2)
            self.serial.write(b'ATZ\r')  # Reset ELM327
            response = self.serial.read(1000).decode('ascii', errors='ignore').strip()
            if 'ELM327' not in response:
                raise ValueError("Device not recognized as ELM327")
            self.serial.write(f'ATSP {protocol}\r'.encode('ascii'))  # Set protocol
            response = self.serial.read(1000).decode('ascii', errors='ignore').strip()
            logger.info(f"Connected to {port}, response: {response}")
            return True
        except Exception as e:
            logger.error(f"Device connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from device"""
        if self.serial and self.serial.is_open:
            self.serial.close()
            logger.info("Device disconnected")
        self.serial = None

    def send_command(self, cmd: str) -> str:
        """Send OBD-II command and get response"""
        if not self.serial or not self.serial.is_open:
            raise ValueError("Device not connected")
        if not re.match(r'^[0-9A-F\s]+$', cmd):
            raise ValueError(f"Invalid OBD command: {cmd}")
        try:
            self.serial.write(f'{cmd}\r'.encode('ascii'))
            response = self.serial.read(1000).decode('ascii', errors='ignore').strip()
            return response
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return ""

    def read_dtcs(self) -> List[Tuple[str, str, str, str]]:
        """Read DTCs from vehicle"""
        try:
            response = self.send_command("03")  # OBD-II mode 03: Read DTCs
            if not response or "NO DATA" in response:
                return []
            # Parse response (simplified, assumes standard OBD-II format)
            dtcs = []
            codes = response.split()
            for code in codes:
                if code.startswith(('P', 'C', 'B', 'U')) and len(code) >= 4:
                    dtcs.append([code, "Unknown DTC", "Confirmed", "Medium"])
            return dtcs
        except Exception as e:
            logger.error(f"DTC read failed: {e}")
            return []

    def read_pid(self, mode: str, pid: str) -> str:
        """Read OBD-II PID (e.g., 010C for RPM)"""
        try:
            response = self.send_command(f"{mode}{pid}")
            return response
        except Exception as e:
            logger.error(f"PID read failed: {e}")
            return ""

class AutoDiagApp(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            self.style_manager = StyleManager()
        except Exception as e:
            logger.error(f"Failed to initialize StyleManager: {e}")
            sys.exit(1)
        self.device_manager = DeviceManager()
        self.selected_brand = "Toyota"
        self.connected = False
        self.scanning = False
        self.live_data_timer = None
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
        try:
            self.style_manager.set_theme("dark")
        except Exception as e:
            logger.warning(f"Failed to apply theme: {e}")
        
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
        
        try:
            brands = get_brand_list()
            self.brand_combo.addItems(brands)
            self.brand_combo.setCurrentText(self.selected_brand)
            self.brand_combo.currentTextChanged.connect(self.on_brand_changed)
        except Exception as e:
            logger.error(f"Failed to load brands: {e}")
        
        brand_layout.addWidget(brand_label)
        brand_layout.addWidget(self.brand_combo)
        
        # Theme selector
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        
        try:
            theme_info = self.style_manager.get_theme_info()
            for theme_id, info in theme_info.items():
                if isinstance(info, dict) and 'name' in info:
                    self.theme_combo.addItem(info['name'], theme_id)
        except Exception as e:
            logger.error(f"Failed to load themes: {e}")
        
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        
        # Connection settings button
        connect_btn = QPushButton("🔌 Connection Settings")
        connect_btn.setProperty("class", "primary")
        connect_btn.clicked.connect(self.show_connection_settings)
        
        # Connection status
        self.connection_status = QLabel("🔴 Disconnected")
        self.connection_status.setProperty("class", "status-disconnected")
        
        header_layout.addLayout(brand_layout)
        header_layout.addSpacing(20)
        header_layout.addLayout(theme_layout)
        header_layout.addSpacing(20)
        header_layout.addWidget(connect_btn)
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
        
        export_btn = QPushButton("Export DTCs")
        export_btn.setProperty("class", "primary")
        export_btn.clicked.connect(self.export_dtcs)
        
        controls_layout.addWidget(read_dtc_btn)
        controls_layout.addWidget(clear_dtc_btn)
        controls_layout.addWidget(freeze_btn)
        controls_layout.addWidget(export_btn)
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
        self.dtc_table.itemClicked.connect(self.show_dtc_details)
        
        dtc_layout.addWidget(dtc_title)
        dtc_layout.addWidget(self.dtc_table)
        
        layout.addWidget(controls_frame)
        layout.addWidget(dtc_frame)
        
        self.tab_widget.addTab(diag_tab, "Diagnostics")
    
    def create_live_data_tab(self):
        """Create live data monitoring tab with graph"""
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
        
        # Splitter for table and graph
        splitter = QSplitter(Qt.Orientation.Vertical)
        
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
        
        # Graph widget
        graph_frame = QFrame()
        graph_frame.setProperty("class", "diagnostic_frame")
        graph_layout = QVBoxLayout(graph_frame)
        
        graph_title = QLabel("Live Data Graph")
        graph_title.setProperty("class", "subtitle")
        
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.live_data_values = []
        
        graph_layout.addWidget(graph_title)
        graph_layout.addWidget(self.canvas)
        
        splitter.addWidget(data_frame)
        splitter.addWidget(graph_frame)
        
        layout.addWidget(controls_frame)
        layout.addWidget(splitter)
        
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
        actuator_btn.clicked.connect(self.run_actuator_test)
        
        adaptation_btn = QPushButton("Adaptations")
        adaptation_btn.setProperty("class", "primary")
        adaptation_btn.clicked.connect(self.run_adaptations)
        
        coding_btn = QPushButton("Coding")
        coding_btn.setProperty("class", "primary")
        coding_btn.clicked.connect(self.run_coding)
        
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
    
    def show_connection_settings(self):
        """Show dialog for connection settings"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Connection Settings")
        layout = QFormLayout(dialog)
        
        port_input = QLineEdit(self.device_manager.port or "/dev/ttyUSB0")
        baudrate_input = QLineEdit(str(self.device_manager.baudrate))
        protocol_combo = QComboBox()
        protocol_combo.addItems(["AUTO", "ISO9141-2", "KWP2000", "CAN"])
        
        layout.addRow("Serial Port:", port_input)
        layout.addRow("Baudrate:", baudrate_input)
        layout.addRow("Protocol:", protocol_combo)
        
        buttons = QHBoxLayout()
        connect_btn = QPushButton("Connect")
        cancel_btn = QPushButton("Cancel")
        
        connect_btn.clicked.connect(lambda: self.connect_device(
            port_input.text(), baudrate_input.text(), protocol_combo.currentText(), dialog
        ))
        cancel_btn.clicked.connect(dialog.reject)
        
        buttons.addWidget(connect_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)
        
        dialog.exec()
    
    def connect_device(self, port: str, baudrate: str, protocol: str, dialog: QDialog):
        """Connect to device with settings"""
        try:
            baudrate = int(baudrate)
            if not (9600 <= baudrate <= 115200):
                raise ValueError("Baudrate must be between 9600 and 115200")
            if self.device_manager.connect(port, baudrate, protocol):
                self.connected = True
                self.connection_status.setText("🟢 Connected")
                self.connection_status.setProperty("class", "status-connected")
                self.obd_status.setText("OBD: Connected")
                self.protocol_status.setText(f"Protocol: {protocol}")
                self.status_label.setText("Connected to vehicle")
                dialog.accept()
            else:
                QMessageBox.critical(self, "Connection Failed", "Failed to connect to device")
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            QMessageBox.critical(self, "Connection Failed", f"Error: {e}")
    
    def on_theme_changed(self, theme_name):
        """Handle theme change"""
        try:
            theme_info = self.style_manager.get_theme_info()
            for theme_id, info in theme_info.items():
                if info.get('name') == theme_name:
                    self.style_manager.set_theme(theme_id)
                    logger.info(f"Applied theme: {theme_name}")
                    break
            else:
                logger.warning(f"Theme {theme_name} not found")
        except Exception as e:
            logger.error(f"Theme change failed: {e}")
            self.status_label.setText("Error changing theme")
    
    def on_brand_changed(self, brand_name):
        """Handle brand selection change"""
        try:
            self.selected_brand = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', brand_name)  # Sanitize
            self.update_brand_specific_data()
            self.show_brand_tips(self.selected_brand)
        except Exception as e:
            logger.error(f"Brand change failed: {e}")
            self.status_label.setText("Error changing brand")
    
    def update_brand_specific_data(self):
        """Update UI with brand-specific information"""
        try:
            brand_info = get_brand_info(self.selected_brand)
            region = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', str(brand_info.get('region', 'N/A')))
            market_share = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', str(brand_info.get('market_share', 'N/A')))
            protocols = [re.sub(r'[\x00-\x1F\x7F-\x9F]', '', p) for p in brand_info.get('diagnostic_protocols', [])]
            obd_protocol = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', str(brand_info.get('obd_protocol', 'N/A')))
            
            self.brand_info_label.setText(
                f"Brand: {self.selected_brand}\n"
                f"Region: {region}\n"
                f"Market Share: {market_share}"
            )
            self.protocol_info_label.setText(
                f"Protocols: {', '.join(protocols)}\n"
                f"OBD Protocol: {obd_protocol}"
            )
            self.update_brand_modules()
            self.update_brand_procedures()
        except Exception as e:
            logger.error(f"Brand data update failed: {e}")
            self.status_label.setText("Error updating brand data")
    
    def update_brand_modules(self):
        """Update modules table with brand-specific ECUs"""
        try:
            brand_info = get_brand_info(self.selected_brand)
            common_ecus = brand_info.get('common_ecus', [])
            self.modules_table.setRowCount(len(common_ecus))
            for row, ecu in enumerate(common_ecus):
                clean_ecu = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', ecu)
                item = QTableWidgetItem(clean_ecu)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.modules_table.setItem(row, 0, item)
                self.modules_table.setItem(row, 1, QTableWidgetItem(self.get_ecu_address(clean_ecu)))
                self.modules_table.setItem(row, 2, QTableWidgetItem(self.get_ecu_protocol(clean_ecu)))
                self.modules_table.setItem(row, 3, QTableWidgetItem("Not Scanned"))
        except Exception as e:
            logger.error(f"Modules update failed: {e}")
    
    def update_brand_procedures(self):
        """Update brand-specific procedures"""
        try:
            procedures = self.get_brand_procedures(self.selected_brand)
            clean_procedures = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', procedures)
            self.procedures_text.setText(clean_procedures)
        except Exception as e:
            logger.error(f"Procedures update failed: {e}")
    
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
1. Quick Scan: Connect with ISO 15765-4 (CAN), use TechStream commands
2. DTC Reading: Standard OBD-II PIDs, enhanced manufacturer codes
3. Live Data: Real-time PIDs, graphing supported""",
            "Volkswagen": """VW/Audi Diagnostic Procedures:
1. Quick Scan: UDS protocol (ISO 14229), full module access
2. DTC Reading: Manufacturer-specific codes, extended fault memory
3. Coding/Adaptation: Online coding required for some modules""",
            "BMW": """BMW Diagnostic Procedures:
1. Quick Scan: ISTA/D protocols, K+CAN or Ethernet
2. DTC Reading: BMW-specific codes, detailed descriptions
3. Programming: ISTA/P for flash, ICOM recommended"""
        }
        return procedures.get(brand, f"Standard diagnostic procedures for {brand} vehicles.")
    
    def show_brand_tips(self, brand_name):
        """Show brand-specific diagnostic tips"""
        tips = {
            "Toyota": "Tip: Use TechStream compatible protocols for full system access",
            "Volkswagen": "Tip: VCDS/ODIS protocols provide deepest module access",
            "BMW": "Tip: ISTA-D/ISTA-P required for advanced programming functions"
        }
        clean_tip = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', tips.get(brand_name, "No specific tips available"))
        self.status_label.setText(f"Brand Tip: {clean_tip}")
    
    def check_auth(self) -> bool:
        """Mock authentication check (replace with real auth in production)"""
        pin, ok = QInputDialog.getText(self, "Authentication", "Enter PIN:", QLineEdit.EchoMode.Password)
        if ok and pin == "1234":  # Mock PIN
            logger.info("Authentication successful")
            return True
        logger.warning("Authentication failed")
        return False

    def quick_scan(self):
        """Perform quick vehicle scan"""
        if not self.connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to a vehicle first")
            return
        try:
            self.scanning = True
            self.status_label.setText("Performing quick scan...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.connection_status.setText("🟡 Scanning...")
            self.connection_status.setProperty("class", "status-warning")
            self.obd_status.setText("OBD: Scanning")
            self.scan_timer = QTimer()
            self.scan_timer.timeout.connect(self.update_scan_progress)
            self.scan_timer.start(100)
        except Exception as e:
            logger.error(f"Quick scan failed: {e}")
            self.status_label.setText("Error during quick scan")
    
    def update_scan_progress(self):
        """Update scan progress"""
        try:
            current = self.progress_bar.value()
            if current < 100:
                self.progress_bar.setValue(current + 10)
            else:
                self.scan_timer.stop()
                self.progress_bar.setVisible(False)
                self.scanning = False
                self.connection_status.setText("🟢 Connected")
                self.connection_status.setProperty("class", "status-connected")
                self.obd_status.setText("OBD: Connected")
                dtcs = self.device_manager.read_dtcs()
                self.add_dtc_data(dtcs or self.get_sample_dtc_data())
                self.add_sample_live_data()
                self.status_label.setText("Quick scan completed successfully")
        except Exception as e:
            logger.error(f"Scan progress update failed: {e}")
            self.status_label.setText("Error during scan progress")
    
    def read_dtcs(self):
        """Read diagnostic trouble codes"""
        if not self.connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to a vehicle first")
            return
        try:
            self.status_label.setText("Reading diagnostic trouble codes...")
            dtcs = self.device_manager.read_dtcs()
            QTimer.singleShot(2000, lambda: self.dtc_reading_complete(dtcs or self.get_sample_dtc_data()))
        except Exception as e:
            logger.error(f"DTC read failed: {e}")
            self.status_label.setText("Error reading DTCs")
    
    def dtc_reading_complete(self, dtcs):
        """Called when DTC reading completes"""
        try:
            self.add_dtc_data(dtcs)
            self.status_label.setText("DTC reading completed")
        except Exception as e:
            logger.error(f"DTC complete failed: {e}")
            self.status_label.setText("Error completing DTC read")
    
    def clear_dtcs(self):
        """Clear diagnostic trouble codes"""
        if not self.connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to a vehicle first")
            return
        if not self.check_auth():
            self.status_label.setText("Authentication failed")
            return
        reply = QMessageBox.question(self, "Clear DTCs", 
                                   "Are you sure you want to clear all diagnostic trouble codes?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.device_manager.send_command("04")  # OBD-II mode 04: Clear DTCs
                self.dtc_table.setRowCount(0)
                self.status_label.setText("DTCs cleared successfully")
                logger.info("DTCs cleared")
            except Exception as e:
                logger.error(f"DTC clear failed: {e}")
                self.status_label.setText("Error clearing DTCs")
    
    def read_freeze_frame(self):
        """Read freeze frame data"""
        if not self.connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to a vehicle first")
            return
        try:
            self.status_label.setText("Reading freeze frame data...")
            response = self.device_manager.send_command("02")  # OBD-II mode 02
            self.system_info_text.setText(f"Freeze Frame Data:\n{response}")
            self.status_label.setText("Freeze frame data retrieved")
        except Exception as e:
            logger.error(f"Freeze frame read failed: {e}")
            self.status_label.setText("Error reading freeze frame")
    
    def start_live_data(self):
        """Start live data monitoring"""
        if not self.connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to a vehicle first")
            return
        try:
            self.status_label.setText("Starting live data monitoring...")
            self.live_data_timer = QTimer()
            self.live_data_timer.timeout.connect(self.update_live_data)
            self.live_data_timer.start(1000)  # Update every second
            if self.record_check.isChecked():
                logger.info("Recording live data")
        except Exception as e:
            logger.error(f"Live data start failed: {e}")
            self.status_label.setText("Error starting live data")
    
    def stop_live_data(self):
        """Stop live data monitoring"""
        if self.live_data_timer:
            self.live_data_timer.stop()
            self.live_data_timer = None
        self.status_label.setText("Live data monitoring stopped")
        logger.info("Live data monitoring stopped")
    
    def update_live_data(self):
        """Update live data table and graph"""
        try:
            # Define PIDs to monitor
            pids = [
                ("010C", "Engine RPM", "RPM"),
                ("010D", "Vehicle Speed", "km/h"),
                ("0105", "Coolant Temp", "°C"),
                ("0110", "MAF Sensor", "g/s")
            ]
            data = []
            for mode_pid, name, unit in pids:
                response = self.device_manager.read_pid("01", mode_pid[2:])
                value = response or "N/A"  # Simplified parsing
                data.append([name, value, unit])
            self.add_dtc_data(data)
            # Update graph (example: RPM)
            if data[0][1] != "N/A":
                self.live_data_values.append(float(data[0][1].replace(',', '')))
                self.live_data_values = self.live_data_values[-50:]  # Last 50 points
                self.ax.clear()
                self.ax.plot(self.live_data_values, label="Engine RPM")
                self.ax.set_xlabel("Time (s)")
                self.ax.set_ylabel("RPM")
                self.ax.legend()
                self.canvas.draw()
        except Exception as e:
            logger.error(f"Live data update failed: {e}")
            self.status_label.setText("Error updating live data")
    
    def add_dtc_data(self, dtcs):
        """Add DTC data to table"""
        try:
            self.dtc_table.setRowCount(len(dtcs))
            for row, dtc in enumerate(dtcs):
                for col, value in enumerate(dtc):
                    clean_value = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', str(value))
                    item = QTableWidgetItem(clean_value)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.dtc_table.setItem(row, col, item)
        except Exception as e:
            logger.error(f"Add DTC data failed: {e}")
    
    def add_sample_dtc_data(self):
        """Add sample DTC data for testing"""
        return [
            ["P0300", "Random/Multiple Cylinder Misfire Detected", "Confirmed", "Medium"],
            ["P0171", "System Too Lean (Bank 1)", "Pending", "Low"],
            ["C1234", "ABS Wheel Speed Sensor Fault", "Confirmed", "High"],
            ["B1345", "ECU Communication Error", "Confirmed", "High"]
        ]
    
    def add_sample_live_data(self):
        """Add sample live data for testing"""
        sample_data = [
            ["Engine RPM", "2,350", "RPM"],
            ["Vehicle Speed", "65", "km/h"],
            ["Coolant Temp", "92", "°C"],
            ["MAF Sensor", "4.8", "g/s"]
        ]
        self.add_dtc_data(sample_data)
    
    def show_dtc_details(self, item):
        """Show details for clicked DTC"""
        row = item.row()
        code = self.dtc_table.item(row, 0).text()
        desc = self.dtc_table.item(row, 1).text()
        QMessageBox.information(self, "DTC Details", f"Code: {code}\nDescription: {desc}")
    
    def export_dtcs(self):
        """Export DTCs to a text file"""
        try:
            with open("dtcs_export.txt", "w") as f:
                for row in range(self.dtc_table.rowCount()):
                    row_data = [self.dtc_table.item(row, col).text() for col in range(self.dtc_table.columnCount())]
                    f.write(",".join(row_data) + "\n")
            self.status_label.setText("DTCs exported to dtcs_export.txt")
            logger.info("DTCs exported")
        except Exception as e:
            logger.error(f"DTC export failed: {e}")
            self.status_label.setText("Error exporting DTCs")
    
    def run_actuator_test(self):
        """Run actuator test (stub)"""
        if not self.connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to a vehicle first")
            return
        self.status_label.setText("Running actuator test...")
        logger.info("Actuator test started")
    
    def run_adaptations(self):
        """Run adaptations (stub)"""
        if not self.connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to a vehicle first")
            return
        self.status_label.setText("Running adaptations...")
        logger.info("Adaptations started")
    
    def run_coding(self):
        """Run coding (stub)"""
        if not self.connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to a vehicle first")
            return
        self.status_label.setText("Running coding...")
        logger.info("Coding started")
    
    def closeEvent(self, event):
        """Ensure cleanup on close"""
        self.device_manager.disconnect()
        if self.live_data_timer:
            self.live_data_timer.stop()
        logger.info("Closing AutoDiagApp")
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("AutoDiag")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("DiagAutoClinicOS")
    
    try:
        window = AutoDiagApp()
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"Application crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
