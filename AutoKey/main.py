#!/usr/bin/env python3
"""
AutoKey Pro - Automotive Key Programming Tool
FUTURISTIC GLASSMORPHIC DESIGN with Global Theme Support
"""

import sys
import os
import re
import logging
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QWidget, QPushButton, QLabel, QComboBox, QTabWidget,
                            QGroupBox, QTableWidget, QTableWidgetItem, QProgressBar,
                            QTextEdit, QLineEdit, QHeaderView, QRadioButton,
                            QInputDialog, QFrame, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import custom modules safely
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared'))
if shared_path not in sys.path:
    sys.path.append(shared_path)
try:
    from shared.style_manager import style_manager  # Use global instance
    from shared.brand_database import get_brand_info, get_brand_list
    from shared.circular_gauge import CircularGauge, StatCard
except ImportError as e:
    logger.error(f"Failed to import custom modules: {e}")
    # Fallback classes
    class style_manager:
        def set_theme(self, theme): pass
        def get_theme_names(self): return ["futuristic", "neon_clinic", "security", "dark", "light", "professional"]
    style_manager = style_manager()
    
    def get_brand_list():
        return ["Toyota", "Honda", "Ford", "BMW", "Mercedes-Benz", "Audi", "Volkswagen"]
    
    def get_brand_info(brand):
        return {"name": brand}
    
    class CircularGauge(QWidget):
        def __init__(self, *args, **kwargs):
            super().__init__()
            self.setMinimumSize(120, 120)
        def set_value(self, val): pass
    
    class StatCard(QFrame):
        def __init__(self, title, value, *args, **kwargs):
            super().__init__()
            layout = QVBoxLayout(self)
            self.title_label = QLabel(title)
            self.value_label = QLabel(str(value))
            layout.addWidget(self.title_label)
            layout.addWidget(self.value_label)
        def update_value(self, val): 
            if hasattr(self, 'value_label'):
                self.value_label.setText(str(val))

class AutoKeyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_brand = "Toyota"
        self.init_ui()
        
    def init_ui(self):
        """Initialize FUTURISTIC user interface"""
        self.setWindowTitle("AutoKey Pro - Futuristic Key Programming")
        self.setGeometry(50, 50, 1366, 768)
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Add scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setWidget(central_widget)
        self.setCentralWidget(scroll)
        
        # Create header
        self.create_header(main_layout)
        
        # Create main tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_key_programming_tab()
        self.create_transponder_tab()
        self.create_vehicle_info_tab()
        self.create_security_tab()
        
        # Create status bar
        self.create_status_bar()
        
        # Show the window
        self.show()
        
        # Start live updates
        self.start_live_updates()
        
    def create_header(self, layout):
        """Create FUTURISTIC header with theme selector"""
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_frame.setMaximumHeight(100)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setSpacing(20)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # Title section
        title_section = QWidget()
        title_layout = QVBoxLayout(title_section)
        title_layout.setSpacing(5)
        
        title_label = QLabel("AutoKey Pro")
        title_label.setProperty("class", "hero-title")
        
        subtitle_label = QLabel("🔑 Professional Key Programming")
        subtitle_label.setProperty("class", "subtitle")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        # Brand selector
        brand_section = QWidget()
        brand_layout = QVBoxLayout(brand_section)
        brand_layout.setSpacing(5)
        
        brand_label = QLabel("Vehicle Brand:")
        brand_label.setProperty("class", "section-label")
        
        self.brand_combo = QComboBox()
        self.brand_combo.addItems(get_brand_list())
        self.brand_combo.setCurrentText(self.selected_brand)
        self.brand_combo.currentTextChanged.connect(self.on_brand_changed)
        self.brand_combo.setMinimumWidth(180)
        
        brand_layout.addWidget(brand_label)
        brand_layout.addWidget(self.brand_combo)
        
        # Theme selector
        theme_section = QWidget()
        theme_layout = QVBoxLayout(theme_section)
        theme_layout.setSpacing(5)
        
        theme_label = QLabel("Theme:")
        theme_label.setProperty("class", "section-label")
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(style_manager.get_theme_names())
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        self.theme_combo.setMinimumWidth(150)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        
        header_layout.addWidget(title_section)
        header_layout.addStretch()
        header_layout.addWidget(brand_section)
        header_layout.addWidget(theme_section)
        
        layout.addWidget(header_frame)

    def create_dashboard_tab(self):
        """Create FUTURISTIC dashboard with key programming stats"""
        dashboard_tab = QWidget()
        layout = QVBoxLayout(dashboard_tab)
        layout.setSpacing(20)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Stats Overview Section
        stats_section = QFrame()
        stats_layout = QHBoxLayout(stats_section)
        stats_layout.setSpacing(20)
        
        # Key Programming Success
        self.success_card = StatCard("Success Rate", 98, 100, "%")
        
        # Keys Programmed Today
        self.keys_today_card = StatCard("Keys Today", 12, 50, "")
        
        # System Status
        self.system_card = StatCard("System Status", 100, 100, "%")
        
        # Active Vehicles
        self.vehicles_card = StatCard("Active Vehicles", 8, 20, "")
        
        stats_layout.addWidget(self.success_card)
        stats_layout.addWidget(self.keys_today_card)
        stats_layout.addWidget(self.system_card)
        stats_layout.addWidget(self.vehicles_card)
        
        # Quick Actions Section
        actions_frame = QFrame()
        actions_frame.setProperty("class", "glass-card")
        actions_layout = QVBoxLayout(actions_frame)
        actions_layout.setSpacing(15)
        actions_layout.setContentsMargins(20, 20, 20, 20)
        
        actions_title = QLabel("⚡ Quick Actions")
        actions_title.setProperty("class", "section-title")
        
        # Quick action buttons in grid
        btn_layout = QGridLayout()
        btn_layout.setSpacing(15)
        
        program_btn = QPushButton("🔑 Program New Key")
        program_btn.setProperty("class", "primary")
        program_btn.setMinimumHeight(50)
        program_btn.clicked.connect(self.program_key)
        
        clone_btn = QPushButton("📋 Clone Key")
        clone_btn.setProperty("class", "success")
        clone_btn.setMinimumHeight(50)
        clone_btn.clicked.connect(self.clone_key)
        
        reset_btn = QPushButton("🔄 Reset System")
        reset_btn.setProperty("class", "danger")
        reset_btn.setMinimumHeight(50)
        reset_btn.clicked.connect(self.reset_system)
        
        diagnose_btn = QPushButton("🔍 Diagnose Keys")
        diagnose_btn.setProperty("class", "primary")
        diagnose_btn.setMinimumHeight(50)
        diagnose_btn.clicked.connect(self.diagnose_keys)
        
        btn_layout.addWidget(program_btn, 0, 0)
        btn_layout.addWidget(clone_btn, 0, 1)
        btn_layout.addWidget(reset_btn, 1, 0)
        btn_layout.addWidget(diagnose_btn, 1, 1)
        
        actions_layout.addWidget(actions_title)
        actions_layout.addLayout(btn_layout)
        
        # System Info
        info_frame = QFrame()
        info_frame.setProperty("class", "glass-card")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(10)
        info_layout.setContentsMargins(20, 20, 20, 20)
        
        info_title = QLabel("📋 System Information")
        info_title.setProperty("class", "section-title")
        
        info_grid = QGridLayout()
        info_grid.setSpacing(10)
        
        info_grid.addWidget(QLabel("Selected Brand:"), 0, 0)
        self.brand_info_label = QLabel(self.selected_brand)
        info_grid.addWidget(self.brand_info_label, 0, 1)
        
        info_grid.addWidget(QLabel("Interface Status:"), 1, 0)
        self.interface_info_label = QLabel("🔌 Connected")
        self.interface_info_label.setProperty("class", "status-connected")
        info_grid.addWidget(self.interface_info_label, 1, 1)
        
        info_grid.addWidget(QLabel("Last Operation:"), 2, 0)
        self.last_op_label = QLabel("None")
        info_grid.addWidget(self.last_op_label, 2, 1)
        
        # Style the labels
        for i in range(3):
            label = info_grid.itemAtPosition(i, 0).widget()
            label.setProperty("class", "info-label")
        
        info_layout.addWidget(info_title)
        info_layout.addLayout(info_grid)
        
        layout.addWidget(stats_section)
        layout.addWidget(actions_frame)
        layout.addWidget(info_frame)
        layout.addStretch()
        
        self.tab_widget.addTab(dashboard_tab, "📊 Dashboard")
        
    def create_key_programming_tab(self):
        """Create FUTURISTIC key programming tab"""
        key_tab = QWidget()
        layout = QVBoxLayout(key_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        header_label = QLabel("🔑 Key Programming")
        header_label.setProperty("class", "tab-title")
        header_layout.addWidget(header_label)

        # Vehicle information
        vehicle_frame = QFrame()
        vehicle_frame.setProperty("class", "glass-card")
        vehicle_layout = QVBoxLayout(vehicle_frame)
        vehicle_layout.setContentsMargins(20, 20, 20, 20)
        
        vehicle_title = QLabel("🚗 Vehicle Information")
        vehicle_title.setProperty("class", "section-title")
        
        make_label = QLabel("Toyota Camry 2020")
        make_label.setProperty("class", "vehicle-make")
        
        model_label = QLabel("2.5L Hybrid - Smart Key System")
        model_label.setProperty("class", "vehicle-model")
        
        vehicle_layout.addWidget(vehicle_title)
        vehicle_layout.addWidget(make_label)
        vehicle_layout.addWidget(model_label)
        
        # Key programming controls
        key_frame = QFrame()
        key_frame.setProperty("class", "glass-card")
        key_layout = QVBoxLayout(key_frame)
        key_layout.setSpacing(15)
        key_layout.setContentsMargins(20, 20, 20, 20)
        
        # Security code input
        security_layout = QHBoxLayout()
        security_label = QLabel("🔒 Security Code:")
        security_label.setProperty("class", "input-label")
        
        self.security_input = QLineEdit()
        self.security_input.setPlaceholderText("Enter vehicle security code (4-8 alphanumeric characters)")
        self.security_input.setMaxLength(8)
        self.security_input.setMinimumHeight(40)
        
        security_layout.addWidget(security_label)
        security_layout.addWidget(self.security_input)
        security_layout.addStretch()
        
        # Programming buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        program_btn = QPushButton("🔑 Program New Key")
        program_btn.setProperty("class", "primary")
        program_btn.setMinimumHeight(50)
        program_btn.clicked.connect(self.program_key)
        
        clone_btn = QPushButton("📋 Clone Key")
        clone_btn.setProperty("class", "success")
        clone_btn.setMinimumHeight(50)
        clone_btn.clicked.connect(self.clone_key)
        
        reset_btn = QPushButton("🔄 Reset System")
        reset_btn.setProperty("class", "danger")
        reset_btn.setMinimumHeight(50)
        reset_btn.clicked.connect(self.reset_system)
        
        btn_layout.addWidget(program_btn)
        btn_layout.addWidget(clone_btn)
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        
        # Key status
        status_frame = QFrame()
        status_frame.setProperty("class", "stat-card")
        status_frame.setMaximumHeight(80)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(20, 15, 20, 15)
        
        self.key_status = QLabel("🔴 No Key Detected")
        self.key_status.setProperty("class", "status-error")
        
        self.immobilizer_status = QLabel("🛡️ Immobilizer: Active")
        self.immobilizer_status.setProperty("class", "status-success")
        
        status_layout.addWidget(QLabel("Key Status:"))
        status_layout.addWidget(self.key_status)
        status_layout.addStretch()
        status_layout.addWidget(self.immobilizer_status)
        
        # Programming progress
        self.key_progress = QProgressBar()
        self.key_progress.setMinimumHeight(25)
        self.key_progress.setTextVisible(True)
        self.key_progress.setValue(0)
        self.key_progress.setVisible(False)
        
        key_layout.addLayout(security_layout)
        key_layout.addLayout(btn_layout)
        key_layout.addWidget(self.key_progress)
        
        layout.addWidget(header_frame)
        layout.addWidget(vehicle_frame)
        layout.addWidget(key_frame)
        layout.addWidget(status_frame)
        
        self.tab_widget.addTab(key_tab, "🔑 Key Programming")
        
    def create_transponder_tab(self):
        """Create FUTURISTIC transponder management tab"""
        transponder_tab = QWidget()
        layout = QVBoxLayout(transponder_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        header_label = QLabel("📡 Transponder Management")
        header_label.setProperty("class", "tab-title")
        
        scan_btn = QPushButton("🔍 Scan Transponders")
        scan_btn.setProperty("class", "primary")
        scan_btn.setMinimumHeight(45)
        scan_btn.clicked.connect(self.scan_transponders)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(scan_btn)
        
        # Transponder group
        transponder_frame = QFrame()
        transponder_frame.setProperty("class", "glass-card")
        transponder_layout = QVBoxLayout(transponder_frame)
        transponder_layout.setContentsMargins(20, 20, 20, 20)
        
        table_label = QLabel("Available Transponders:")
        table_label.setProperty("class", "section-title")
        
        # Transponder table
        self.transponder_table = QTableWidget()
        self.transponder_table.setColumnCount(4)
        self.transponder_table.setHorizontalHeaderLabels(["Key ID", "Type", "Status", "Vehicle"])
        self.transponder_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Add sample data
        self.add_sample_transponder_data()
        
        transponder_layout.addWidget(table_label)
        transponder_layout.addWidget(self.transponder_table)
        
        layout.addWidget(header_frame)
        layout.addWidget(transponder_frame)
        
        self.tab_widget.addTab(transponder_tab, "📡 Transponders")
        
    def create_vehicle_info_tab(self):
        """Create FUTURISTIC vehicle information tab"""
        vehicle_tab = QWidget()
        layout = QVBoxLayout(vehicle_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        header_label = QLabel("🚗 Vehicle Information")
        header_label.setProperty("class", "tab-title")
        
        refresh_btn = QPushButton("🔄 Refresh Data")
        refresh_btn.setProperty("class", "primary")
        refresh_btn.setMinimumHeight(45)
        refresh_btn.clicked.connect(self.refresh_vehicle_data)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        
        vehicle_frame = QFrame()
        vehicle_frame.setProperty("class", "glass-card")
        vehicle_layout = QVBoxLayout(vehicle_frame)
        vehicle_layout.setContentsMargins(20, 20, 20, 20)
        
        table_label = QLabel("Vehicle Details:")
        table_label.setProperty("class", "section-title")
        
        # Vehicle details table
        details_table = QTableWidget()
        details_table.setColumnCount(2)
        details_table.setHorizontalHeaderLabels(["Property", "Value"])
        details_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Load vehicle data securely (mock for now)
        vehicle_data = [
            ["VIN", "REDACTED_VIN_123"],
            ["Make", "Toyota"],
            ["Model", "Camry"],
            ["Year", "2020"],
            ["Key System", "Smart Key"],
            ["Transponder", "ID4C / 4D"],
            ["Keys Programmed", "2/5"],
            ["Immobilizer", "Active"],
            ["Last Service", "2024-01-15"]
        ]
        
        details_table.setRowCount(len(vehicle_data))
        for row, data in enumerate(vehicle_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                details_table.setItem(row, col, item)
        
        vehicle_layout.addWidget(table_label)
        vehicle_layout.addWidget(details_table)
        
        layout.addWidget(header_frame)
        layout.addWidget(vehicle_frame)
        
        self.tab_widget.addTab(vehicle_tab, "🚗 Vehicle Info")

    def create_security_tab(self):
        """Create FUTURISTIC security and diagnostics tab"""
        security_tab = QWidget()
        layout = QVBoxLayout(security_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        header_label = QLabel("🔐 Security & Diagnostics")
        header_label.setProperty("class", "tab-title")
        header_layout.addWidget(header_label)
        
        # Content
        content_frame = QFrame()
        content_frame.setProperty("class", "glass-card")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        placeholder = QLabel("🚧 Advanced security features under development\n\n"
                            "This tab will include:\n"
                            "• Security access levels\n"
                            "• PIN code management\n"
                            "• Diagnostic logging\n"
                            "• System audit trails\n"
                            "• Backup and restore functions")
        placeholder.setProperty("class", "placeholder-text")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        content_layout.addWidget(placeholder)
        
        layout.addWidget(header_frame)
        layout.addWidget(content_frame)
        layout.addStretch()
        
        self.tab_widget.addTab(security_tab, "🔐 Security")
        
    def create_status_bar(self):
        """Create FUTURISTIC status bar"""
        status_frame = QFrame()
        status_frame.setProperty("class", "glass-card")
        status_frame.setMaximumHeight(40)
        
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        self.status_label = QLabel("✨ Ready to program keys")
        self.status_label.setProperty("class", "status-ready")
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        status_frame.setLayout(status_layout)
        self.statusBar().addPermanentWidget(status_frame, 1)
        
    def start_live_updates(self):
        """Start live updates for dashboard gauges"""
        self.live_timer = QTimer()
        self.live_timer.timeout.connect(self.update_live_data)
        self.live_timer.start(2000)
        
    def update_live_data(self):
        """Update live data for dashboard"""
        try:
            current_success = random.randint(96, 99)
            self.success_card.update_value(current_success)
            
            keys_today = random.randint(10, 15)
            self.keys_today_card.update_value(keys_today)
            
        except Exception as e:
            logger.error(f"Error updating live data: {e}")
    
    def on_theme_changed(self, theme_name):
        """Handle theme change using global style_manager"""
        try:
            style_manager.set_theme(theme_name)
            self.status_label.setText(f"✨ Theme changed to: {theme_name}")
        except Exception as e:
            logger.error(f"Failed to change theme: {e}")
            self.status_label.setText(f"⚠️ Error changing theme: {e}")
    
    def on_brand_changed(self, brand):
        """Handle brand change"""
        self.selected_brand = brand
        self.brand_info_label.setText(brand)
        self.status_label.setText(f"✨ Brand changed to: {brand}")
        
    def scan_transponders(self):
        """Scan for available transponders"""
        try:
            self.status_label.setText("🔍 Scanning for transponders...")
            self.last_op_label.setText("Transponder Scan")
            self.last_op_label.setProperty("class", "status-success")
            
            QTimer.singleShot(2000, self.complete_transponder_scan)
        except Exception as e:
            self.status_label.setText(f"❌ Error scanning transponders: {e}")
    
    def complete_transponder_scan(self):
        """Complete transponder scanning"""
        self.status_label.setText("✅ Transponder scan completed")
        self.add_sample_transponder_data()
        
    def refresh_vehicle_data(self):
        """Refresh vehicle data"""
        try:
            self.status_label.setText("🔄 Refreshing vehicle data...")
            QTimer.singleShot(1000, lambda: self.status_label.setText("✅ Vehicle data refreshed"))
            self.last_op_label.setText("Refresh Data")
            self.last_op_label.setProperty("class", "status-success")
        except Exception as e:
            self.status_label.setText(f"❌ Error refreshing data: {e}")
    
    def diagnose_keys(self):
        """Diagnose key system"""
        try:
            self.status_label.setText("🔍 Diagnosing key system...")
            self.last_op_label.setText("System Diagnosis")
            self.last_op_label.setProperty("class", "status-success")
            
            QTimer.singleShot(1500, lambda: self.status_label.setText("✅ System diagnosis completed - No issues found"))
        except Exception as e:
            self.status_label.setText(f"❌ Error during diagnosis: {e}")
                
    def add_sample_transponder_data(self):
        """Add sample transponder data securely"""
        sample_data = [
            ["KEY001", "Smart Key", "✅ Programmed", "Toyota Camry"],
            ["KEY002", "Smart Key", "✅ Programmed", "Toyota Camry"],
            ["KEY003", "Mechanical", "⚠️ Unprogrammed", "N/A"],
            ["TSP001", "ID4C", "🔴 Blank", "N/A"],
            ["TSP002", "4D", "🟡 Learning", "Honda Civic"],
            ["TSP003", "ID46", "✅ Ready", "N/A"]
        ]
        
        self.transponder_table.setRowCount(len(sample_data))
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                
                if col == 2:
                    if "Programmed" in value or "Ready" in value:
                        item.setForeground(Qt.GlobalColor.green)
                    elif "Unprogrammed" in value or "Learning" in value:
                        item.setForeground(Qt.GlobalColor.yellow)
                    elif "Blank" in value:
                        item.setForeground(Qt.GlobalColor.red)
                        
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
        """Mock authentication check"""
        pin, ok = QInputDialog.getText(self, "Authentication", "Enter PIN:", QLineEdit.EchoMode.Password)
        if ok and pin == "1234":
            logger.info("Authentication successful")
            return True
        logger.warning("Authentication failed")
        return False

    def program_key(self):
        """Simulate key programming with validation and auth"""
        if not self.check_auth():
            self.status_label.setText("❌ Authentication failed")
            return
            
        code = self.security_input.text().strip()
        if not self.validate_security_code(code):
            self.status_label.setText("❌ Invalid security code (alphanumeric, 4-8 chars)")
            return
            
        logger.info("Initiating key programming")
        self.status_label.setText("🔑 Programming new key...")
        self.key_status.setText("🟡 Programming...")
        self.key_status.setProperty("class", "status-warning")
        self.key_progress.setVisible(True)
        self.key_progress.setValue(0)
        
        self.program_timer = QTimer()
        self.program_timer.timeout.connect(self.update_program_progress)
        self.program_timer.start(100)
        
    def update_program_progress(self):
        """Update programming progress"""
        current = self.key_progress.value()
        if current < 100:
            self.key_progress.setValue(current + 10)
        else:
            self.program_timer.stop()
            self.programming_complete()
        
    def programming_complete(self):
        """Called when programming completes"""
        logger.info("Key programming completed")
        self.status_label.setText("✅ Key programmed successfully!")
        self.key_status.setText("🟢 Programmed")
        self.key_status.setProperty("class", "status-success")
        self.key_progress.setVisible(False)
        self.last_op_label.setText("Key Programming")
        self.last_op_label.setProperty("class", "status-success")
        
        self.keys_today_card.update_value(13)
        
    def clone_key(self):
        """Simulate key cloning with auth"""
        if not self.check_auth():
            self.status_label.setText("❌ Authentication failed")
            return
            
        logger.info("Initiating key cloning")
        self.status_label.setText("📋 Cloning key...")
        self.last_op_label.setText("Key Cloning")
        self.last_op_label.setProperty("class", "status-success")
        
        QTimer.singleShot(2000, lambda: self.status_label.setText("✅ Key cloned successfully!"))
        
    def reset_system(self):
        """Simulate system reset with auth"""
        if not self.check_auth():
            self.status_label.setText("❌ Authentication failed")
            return
            
        logger.info("Initiating system reset")
        self.status_label.setText("🔄 Resetting key system...")
        self.security_input.clear()
        self.key_status.setText("🔴 No Key Detected")
        self.key_status.setProperty("class", "status-error")
        self.last_op_label.setText("System Reset")
        self.last_op_label.setProperty("class", "status-success")
        
        QTimer.singleShot(1500, lambda: self.status_label.setText("✅ System reset completed"))
    
    def closeEvent(self, event):
        """Ensure cleanup on close"""
        logger.info("Closing AutoKeyApp")
        try:
            if hasattr(self, 'live_timer'):
                self.live_timer.stop()
            if hasattr(self, 'program_timer'):
                self.program_timer.stop()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    app.setApplicationName("AutoKey Pro")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("DiagAutoClinicOS")
    
    try:
        window = AutoKeyApp()
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()