
# main.py - RESPONSIVE KEY PROGRAMMING SUITE

#!/usr/bin/env python3
"""
AutoKey Pro - Automotive Key Programming Tool
RESPONSIVE GUI VERSION - FIXED IMPORTS & DACOS THEME COMPLIANCE
"""

import sys
import os
import re
import logging
import random

# FIXED: Enhanced import path resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(parent_dir)  # Go up to DiagAutoClinicOS root

# Add all possible paths
sys.path.insert(0, project_root)  # DiagAutoClinicOS root
sys.path.insert(0, parent_dir)    # AutoKey directory  
sys.path.insert(0, current_dir)   # Current script directory
sys.path.insert(0, os.path.join(project_root, 'shared'))  # Shared modules

from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QWidget, QPushButton, QLabel, QComboBox, QTabWidget,
                            QGroupBox, QTableWidget, QTableWidgetItem, QProgressBar,
                            QTextEdit, QLineEdit, QHeaderView, QRadioButton,
                            QInputDialog, QFrame, QGridLayout, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QResizeEvent

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# FIXED: Import DACOS theme ONLY from shared module as per AI_RULES.md
try:
    from shared.theme_manager import apply_theme, get_theme_dict, AVAILABLE_THEMES, save_config as save_theme_config, get_current_theme_name
    DACOS_THEME = get_theme_dict()
    logger.info("✅ Successfully imported DACOS theme manager")
except ImportError as e:
    logger.error(f"❌ Failed to import DACOS theme: {e}")
    logger.error("Using fallback theme")
    from shared.themes.dacos_cyber_teal import DACOS_THEME, apply_theme
    AVAILABLE_THEMES = {"DACOS Cyber-Teal": "shared.themes.dacos_cyber_teal"}
    def save_theme_config(name): pass
    def get_current_theme_name(): return "DACOS Cyber-Teal"

# FIXED: Import other shared modules with fallbacks
try:
    from shared.brand_database import get_brand_info, get_brand_list
    logger.info("✅ Successfully imported brand database")
except ImportError as e:
    logger.warning(f"⚠️ Failed to import brand database: {e}")
    # Minimal fallback that won't crash
    def get_brand_list():
        return ["Toyota", "Honda", "Ford", "BMW", "Mercedes-Benz", "Audi", "Volkswagen"]
    def get_brand_info(brand):
        return {"name": brand, "region": "Unknown", "security_level": 3}

try:
    from shared.circular_gauge import CircularGauge, StatCard
    logger.info("✅ Successfully imported circular gauges")
except ImportError as e:
    logger.warning(f"⚠️ Failed to import circular gauges: {e}")
    # Minimal fallback gauges
    class CircularGauge(QWidget):
        def __init__(self, value=0, max_value=100, label="", unit="%", parent=None):
            super().__init__(parent)
            self.setMinimumSize(120, 120)
        def set_value(self, val):
            self.update()
    class StatCard(QFrame):
        def __init__(self, title, value, max_value=100, unit="%"):
            super().__init__()
            layout = QVBoxLayout(self)
            self.title_label = QLabel(title)
            self.value_label = QLabel(f"{value}{unit}")
            layout.addWidget(self.title_label)
            layout.addWidget(self.value_label)
        def update_value(self, val):
            self.value_label.setText(f"{val}%")

# Import separate tab classes
try:
    from AutoKey.ui.dashboard_tab import DashboardTab
    from AutoKey.ui.key_programming_tab import KeyProgrammingTab
    from AutoKey.ui.transponder_tab import TransponderTab
    from AutoKey.ui.vehicle_info_tab import VehicleInfoTab
    from AutoKey.ui.security_tab import SecurityTab
    logger.info("✅ Successfully imported AutoKey tab classes")
except ImportError as e:
    logger.error(f"❌ Failed to import AutoKey tab classes: {e}")
    # Fallback tab classes
    class DashboardTab:
        def __init__(self, parent): pass
        def create_tab(self): return QWidget(), "Dashboard"

    class KeyProgrammingTab:
        def __init__(self, parent): pass
        def create_tab(self): return QWidget(), "Key Programming"

    class TransponderTab:
        def __init__(self, parent): pass
        def create_tab(self): return QWidget(), "Transponders"

    class VehicleInfoTab:
        def __init__(self, parent): pass
        def create_tab(self): return QWidget(), "Vehicle Info"

    class SecurityTab:
        def __init__(self, parent): pass
        def create_tab(self): return QWidget(), "Security"

class ResponsiveGridLayout(QGridLayout):
    """Responsive grid layout that adapts to screen size"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSpacing(15)
        self.setContentsMargins(10, 10, 10, 10)
        
    def update_columns(self, width):
        """Update number of columns based on available width"""
        if width > 1200:
            columns = 4
        elif width > 800:
            columns = 3
        elif width > 500:
            columns = 2
        else:
            columns = 1
        return columns

class ResponsiveTabWidget(QTabWidget):
    """Responsive tab widget that adjusts tab bar for mobile"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDocumentMode(True)
        self.setElideMode(Qt.TextElideMode.ElideRight)
        
    def resizeEvent(self, event: QResizeEvent):
        """Handle resize events for responsive tab bar"""
        if event.size().width() < 600:
            self.setStyleSheet("QTabBar::tab { min-width: 80px; max-width: 120px; }")
        else:
            self.setStyleSheet("QTabBar::tab { min-width: 120px; }")
        super().resizeEvent(event)

class AutoKeyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_brand = "Toyota"
        self.current_window_width = 1366
        self.init_ui()
        
    def init_ui(self):
        """Initialize RESPONSIVE user interface"""
        self.setWindowTitle("AutoKey Pro - Futuristic Key Programming")
        self.setMinimumSize(800, 600)  # More reasonable minimum size
        self.resize(1366, 768)

        # Create central widget and main layout
        central_widget = QWidget()
        central_widget.setObjectName("NeonBackground")
        self.setCentralWidget(central_widget)
        
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(15, 15, 15, 15)

        # Create header
        self.create_header(self.main_layout)
        
        # Create main tab widget
        self.tab_widget = ResponsiveTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create tabs using separated classes
        self.create_separated_tabs()
        
        # Create status bar
        self.create_status_bar()
        
        # Show the window
        self.show()
        
        # Start live updates
        self.start_live_updates()
        
    def resizeEvent(self, event):
        """Handle window resize for responsive layouts"""
        self.current_window_width = event.size().width()
        self.update_responsive_layouts()
        super().resizeEvent(event)
        
    def create_separated_tabs(self):
        """Create tabs using separated tab classes"""
        # Initialize tab classes
        self.dashboard_tab = DashboardTab(self)
        self.key_programming_tab = KeyProgrammingTab(self)
        self.transponder_tab = TransponderTab(self)
        self.vehicle_info_tab = VehicleInfoTab(self)
        self.security_tab = SecurityTab(self)

        # Create tabs
        dashboard_widget, dashboard_title = self.dashboard_tab.create_tab()
        self.tab_widget.addTab(dashboard_widget, dashboard_title)

        key_programming_widget, key_programming_title = self.key_programming_tab.create_tab()
        self.tab_widget.addTab(key_programming_widget, key_programming_title)

        transponder_widget, transponder_title = self.transponder_tab.create_tab()
        self.tab_widget.addTab(transponder_widget, transponder_title)

        vehicle_info_widget, vehicle_info_title = self.vehicle_info_tab.create_tab()
        self.tab_widget.addTab(vehicle_info_widget, vehicle_info_title)

        security_widget, security_title = self.security_tab.create_tab()
        self.tab_widget.addTab(security_widget, security_title)

    def update_responsive_layouts(self):
        """Update all responsive layouts based on current window size"""
        # Update dashboard stats grid
        if hasattr(self, 'dashboard_tab') and hasattr(self.dashboard_tab, 'stats_layout'):
            columns = self.get_column_count()
            self.dashboard_tab.update_stats_layout(columns)

        # Update quick actions grid
        if hasattr(self, 'dashboard_tab') and hasattr(self.dashboard_tab, 'quick_actions_layout'):
            self.dashboard_tab.update_quick_actions_layout()
        
    def get_column_count(self):
        """Get appropriate column count based on window width"""
        if self.current_window_width > 1200:
            return 4
        elif self.current_window_width > 800:
            return 3
        elif self.current_window_width > 500:
            return 2
        else:
            return 1
            
    def create_header(self, layout):
        """Create RESPONSIVE header with theme selector"""
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_frame.setMaximumHeight(150)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setSpacing(15)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        # Title section
        title_section = QWidget()
        title_layout = QVBoxLayout(title_section)
        title_layout.setSpacing(5)
        
        title_label = QLabel("AutoKey Pro")
        title_label.setProperty("class", "hero-title")
        title_label.setWordWrap(True)
        
        subtitle_label = QLabel("🔑 Professional Key Programming")
        subtitle_label.setProperty("class", "subtitle")
        subtitle_label.setWordWrap(True)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        # Controls section - will wrap on small screens
        controls_widget = QWidget()
        self.controls_layout = QHBoxLayout(controls_widget)
        self.controls_layout.setSpacing(10)
        
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
        self.brand_combo.setMinimumWidth(150)
        self.brand_combo.setMaximumWidth(200)
        
        brand_layout.addWidget(brand_label)
        brand_layout.addWidget(self.brand_combo)
        
        # Theme selector
        theme_section = QWidget()
        theme_layout = QVBoxLayout(theme_section)
        theme_layout.setSpacing(5)
        
        theme_label = QLabel("Theme:")
        theme_label.setProperty("class", "section-label")
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(AVAILABLE_THEMES.keys()))
        
        try:
            current = get_current_theme_name()
            index = self.theme_combo.findText(current)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)
        except: pass
            
        self.theme_combo.setEnabled(True)
        self.theme_combo.setMinimumWidth(150)
        self.theme_combo.setMaximumWidth(200)
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        
        self.controls_layout.addWidget(brand_section)
        self.controls_layout.addWidget(theme_section)
        self.controls_layout.addStretch()
        
        header_layout.addWidget(title_section)
        header_layout.addWidget(controls_widget)
        
        layout.addWidget(header_frame)

    def create_dashboard_tab(self):
        """Create RESPONSIVE dashboard with key programming stats"""
        dashboard_tab = QWidget()
        layout = QVBoxLayout(dashboard_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create scroll area for mobile
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        scroll_layout.setContentsMargins(5, 5, 5, 5)
        
        # Stats Overview Section - Responsive grid
        stats_container = QWidget()
        self.stats_layout = ResponsiveGridLayout(stats_container)
        
        # Key Programming Success
        self.success_card = StatCard("Success Rate", 98, 100, "%")
        self.success_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Keys Programmed Today
        self.keys_today_card = StatCard("Keys Today", 12, 50, "")
        self.keys_today_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # System Status
        self.system_card = StatCard("System Status", 100, 100, "%")
        self.system_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Active Vehicles
        self.vehicles_card = StatCard("Active Vehicles", 8, 20, "")
        self.vehicles_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Add cards to grid - layout will be updated dynamically
        self.stats_layout.addWidget(self.success_card, 0, 0)
        self.stats_layout.addWidget(self.keys_today_card, 0, 1)
        self.stats_layout.addWidget(self.system_card, 1, 0)
        self.stats_layout.addWidget(self.vehicles_card, 1, 1)
        
        # Quick Actions Section
        actions_frame = QFrame()
        actions_frame.setProperty("class", "glass-card")
        actions_layout = QVBoxLayout(actions_frame)
        actions_layout.setSpacing(15)
        actions_layout.setContentsMargins(15, 15, 15, 15)
        
        actions_title = QLabel("⚡ Quick Actions")
        actions_title.setProperty("class", "section-title")
        
        # Responsive quick action buttons
        self.quick_actions_layout = QGridLayout()
        self.quick_actions_layout.setSpacing(10)
        self.quick_actions_layout.setContentsMargins(5, 5, 5, 5)
        
        buttons = [
            ("🔑 Program New Key", "primary", self.program_key),
            ("📋 Clone Key", "success", self.clone_key),
            ("🔄 Reset System", "danger", self.reset_system),
            ("🔍 Diagnose Keys", "primary", self.diagnose_keys),
        ]
        
        self.action_buttons = []
        for i, (text, style, callback) in enumerate(buttons):
            btn = QPushButton(text)
            btn.setProperty("class", style)
            btn.setMinimumHeight(45)
            btn.clicked.connect(callback)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.action_buttons.append(btn)
            
        # Initial layout - will be updated dynamically
        self.update_quick_actions_layout()
        
        actions_layout.addWidget(actions_title)
        actions_layout.addLayout(self.quick_actions_layout)
        
        # System Info - Responsive
        info_frame = QFrame()
        info_frame.setProperty("class", "glass-card")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(10)
        info_layout.setContentsMargins(15, 15, 15, 15)
        
        info_title = QLabel("📋 System Information")
        info_title.setProperty("class", "section-title")
        
        info_grid = QGridLayout()
        info_grid.setSpacing(8)
        info_grid.setColumnStretch(1, 1)  # Make value column expandable
        
        info_grid.addWidget(QLabel("Selected Brand:"), 0, 0)
        self.brand_info_label = QLabel(self.selected_brand)
        self.brand_info_label.setWordWrap(True)
        info_grid.addWidget(self.brand_info_label, 0, 1)
        
        info_grid.addWidget(QLabel("Interface Status:"), 1, 0)
        self.interface_info_label = QLabel("🔌 Connected")
        self.interface_info_label.setProperty("class", "status-connected")
        self.interface_info_label.setWordWrap(True)
        info_grid.addWidget(self.interface_info_label, 1, 1)
        
        info_grid.addWidget(QLabel("Last Operation:"), 2, 0)
        self.last_op_label = QLabel("None")
        self.last_op_label.setWordWrap(True)
        info_grid.addWidget(self.last_op_label, 2, 1)
        
        # Style the labels
        for i in range(3):
            label = info_grid.itemAtPosition(i, 0).widget()
            label.setProperty("class", "info-label")
            label.setMinimumWidth(100)  # Ensure consistent label width
        
        info_layout.addWidget(info_title)
        info_layout.addLayout(info_grid)
        
        scroll_layout.addWidget(stats_container)
        scroll_layout.addWidget(actions_frame)
        scroll_layout.addWidget(info_frame)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(dashboard_tab, "📊 Dashboard")
        
    def update_stats_layout(self, columns):
        """Update stats layout based on column count"""
        # Clear existing layout
        for i in reversed(range(self.stats_layout.count())):
            self.stats_layout.itemAt(i).widget().setParent(None)
            
        cards = [self.success_card, self.keys_today_card, self.system_card, self.vehicles_card]
        
        for i, card in enumerate(cards):
            row = i // columns
            col = i % columns
            self.stats_layout.addWidget(card, row, col)
            
    def update_quick_actions_layout(self):
        """Update quick actions layout to 1 row 4 buttons"""
        # Clear existing layout
        for i in reversed(range(self.quick_actions_layout.count())):
            self.quick_actions_layout.itemAt(i).widget().setParent(None)

        columns = 4

        for i, btn in enumerate(self.action_buttons):
            row = i // columns
            col = i % columns
            self.quick_actions_layout.addWidget(btn, row, col)

    def create_key_programming_tab(self):
        """Create RESPONSIVE key programming tab"""
        key_tab = QWidget()
        layout = QVBoxLayout(key_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(5, 5, 5, 5)

        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        header_label = QLabel("🔑 Key Programming")
        header_label.setProperty("class", "tab-title")
        header_label.setWordWrap(True)
        header_layout.addWidget(header_label)

        # Vehicle information
        vehicle_frame = QFrame()
        vehicle_frame.setProperty("class", "glass-card")
        vehicle_layout = QVBoxLayout(vehicle_frame)
        vehicle_layout.setContentsMargins(15, 15, 15, 15)
        
        vehicle_title = QLabel("🚗 Vehicle Information")
        vehicle_title.setProperty("class", "section-title")
        
        make_label = QLabel("Toyota Camry 2020")
        make_label.setProperty("class", "vehicle-make")
        make_label.setWordWrap(True)
        
        model_label = QLabel("2.5L Hybrid - Smart Key System")
        model_label.setProperty("class", "vehicle-model")
        model_label.setWordWrap(True)
        
        vehicle_layout.addWidget(vehicle_title)
        vehicle_layout.addWidget(make_label)
        vehicle_layout.addWidget(model_label)
        
        # Key programming controls
        key_frame = QFrame()
        key_frame.setProperty("class", "glass-card")
        key_layout = QVBoxLayout(key_frame)
        key_layout.setSpacing(10)
        key_layout.setContentsMargins(15, 15, 15, 15)
        
        # Security code input - responsive
        security_layout = QVBoxLayout() if self.current_window_width < 600 else QHBoxLayout()
        security_label = QLabel("🔒 Security Code:")
        security_label.setProperty("class", "input-label")
        security_label.setMinimumWidth(120)
        
        self.security_input = QLineEdit()
        self.security_input.setPlaceholderText("Enter vehicle security code (4-8 alphanumeric characters)")
        self.security_input.setMaxLength(8)
        self.security_input.setMinimumHeight(40)
        
        if self.current_window_width < 600:
            security_layout.addWidget(security_label)
            security_layout.addWidget(self.security_input)
        else:
            security_layout.addWidget(security_label)
            security_layout.addWidget(self.security_input)
            security_layout.addStretch()
        
        # Programming buttons - responsive grid
        btn_layout = QGridLayout()
        btn_layout.setSpacing(10)
        
        buttons = [
            ("🔑 Program New Key", "primary", self.program_key),
            ("📋 Clone Key", "success", self.clone_key),
            ("🔄 Reset System", "danger", self.reset_system),
        ]
        
        columns = 2 if self.current_window_width < 800 else 3
        for i, (text, style, callback) in enumerate(buttons):
            btn = QPushButton(text)
            btn.setProperty("class", style)
            btn.setMinimumHeight(45)
            btn.clicked.connect(callback)
            row = i // columns
            col = i % columns
            btn_layout.addWidget(btn, row, col)
        
        # Key status - responsive
        status_frame = QFrame()
        status_frame.setProperty("class", "stat-card")
        status_frame.setMaximumHeight(80)
        status_layout = QVBoxLayout() if self.current_window_width < 500 else QHBoxLayout()
        status_layout.setContentsMargins(15, 10, 15, 10)
        
        self.key_status = QLabel("🔴 No Key Detected")
        self.key_status.setProperty("class", "status-error")
        self.key_status.setWordWrap(True)
        
        self.immobilizer_status = QLabel("🛡️ Immobilizer: Active")
        self.immobilizer_status.setProperty("class", "status-success")
        self.immobilizer_status.setWordWrap(True)
        
        if self.current_window_width < 500:
            status_layout.addWidget(QLabel("Key Status:"))
            status_layout.addWidget(self.key_status)
            status_layout.addWidget(self.immobilizer_status)
        else:
            status_layout.addWidget(QLabel("Key Status:"))
            status_layout.addWidget(self.key_status)
            status_layout.addStretch()
            status_layout.addWidget(self.immobilizer_status)
        
        status_frame.setLayout(status_layout)
        
        # Programming progress
        self.key_progress = QProgressBar()
        self.key_progress.setMinimumHeight(20)
        self.key_progress.setTextVisible(True)
        self.key_progress.setValue(0)
        self.key_progress.setVisible(False)
        
        key_layout.addLayout(security_layout)
        key_layout.addLayout(btn_layout)
        key_layout.addWidget(self.key_progress)
        
        scroll_layout.addWidget(header_frame)
        scroll_layout.addWidget(vehicle_frame)
        scroll_layout.addWidget(key_frame)
        scroll_layout.addWidget(status_frame)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(key_tab, "🔑 Key Programming")

    def create_transponder_tab(self):
        """Create RESPONSIVE transponder management tab"""
        transponder_tab = QWidget()
        layout = QVBoxLayout(transponder_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header with responsive button
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QVBoxLayout() if self.current_window_width < 600 else QHBoxLayout()
        header_frame.setLayout(header_layout)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        header_label = QLabel("📡 Transponder Management")
        header_label.setProperty("class", "tab-title")
        header_label.setWordWrap(True)
        
        scan_btn = QPushButton("🔍 Scan Transponders")
        scan_btn.setProperty("class", "primary")
        scan_btn.setMinimumHeight(40)
        scan_btn.clicked.connect(self.scan_transponders)
        
        if self.current_window_width < 600:
            header_layout.addWidget(header_label)
            header_layout.addWidget(scan_btn)
        else:
            header_layout.addWidget(header_label)
            header_layout.addStretch()
            header_layout.addWidget(scan_btn)
        
        # Transponder table in scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(5, 5, 5, 5)
        
        transponder_frame = QFrame()
        transponder_frame.setProperty("class", "glass-card")
        transponder_layout = QVBoxLayout(transponder_frame)
        transponder_layout.setContentsMargins(15, 15, 15, 15)
        
        table_label = QLabel("Available Transponders:")
        table_label.setProperty("class", "section-title")
        
        # Responsive table
        self.transponder_table = QTableWidget()
        self.transponder_table.setColumnCount(4)
        self.transponder_table.setHorizontalHeaderLabels(["Key ID", "Type", "Status", "Vehicle"])
        
        # Make table responsive
        header = self.transponder_table.horizontalHeader()
        if self.current_window_width < 800:
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        else:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            
        self.transponder_table.verticalHeader().setVisible(False)
        
        # Add sample data
        self.add_sample_transponder_data()
        
        transponder_layout.addWidget(table_label)
        transponder_layout.addWidget(self.transponder_table)
        
        content_layout.addWidget(header_frame)
        content_layout.addWidget(transponder_frame)
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(transponder_tab, "📡 Transponders")

    def create_vehicle_info_tab(self):
        """Create RESPONSIVE vehicle information tab"""
        vehicle_tab = QWidget()
        layout = QVBoxLayout(vehicle_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header with responsive layout
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QVBoxLayout() if self.current_window_width < 600 else QHBoxLayout()
        header_frame.setLayout(header_layout)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        header_label = QLabel("🚗 Vehicle Information")
        header_label.setProperty("class", "tab-title")
        header_label.setWordWrap(True)
        
        refresh_btn = QPushButton("🔄 Refresh Data")
        refresh_btn.setProperty("class", "primary")
        refresh_btn.setMinimumHeight(40)
        refresh_btn.clicked.connect(self.refresh_vehicle_data)
        
        if self.current_window_width < 600:
            header_layout.addWidget(header_label)
            header_layout.addWidget(refresh_btn)
        else:
            header_layout.addWidget(header_label)
            header_layout.addStretch()
            header_layout.addWidget(refresh_btn)
        
        # Scrollable content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(5, 5, 5, 5)
        
        vehicle_frame = QFrame()
        vehicle_frame.setProperty("class", "glass-card")
        vehicle_layout = QVBoxLayout(vehicle_frame)
        vehicle_layout.setContentsMargins(15, 15, 15, 15)
        
        table_label = QLabel("Vehicle Details:")
        table_label.setProperty("class", "section-title")
        
        # Responsive table
        details_table = QTableWidget()
        details_table.setColumnCount(2)
        details_table.setHorizontalHeaderLabels(["Property", "Value"])
        
        # Adjust table based on screen size
        if self.current_window_width < 600:
            details_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        else:
            details_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        # Load vehicle data
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
                if self.current_window_width < 600:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
                details_table.setItem(row, col, item)
        
        vehicle_layout.addWidget(table_label)
        vehicle_layout.addWidget(details_table)
        
        content_layout.addWidget(header_frame)
        content_layout.addWidget(vehicle_frame)
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(vehicle_tab, "🚗 Vehicle Info")

    def create_security_tab(self):
        """Create RESPONSIVE security and diagnostics tab"""
        security_tab = QWidget()
        layout = QVBoxLayout(security_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Scroll area for mobile
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        header_label = QLabel("🔐 Security & Diagnostics")
        header_label.setProperty("class", "tab-title")
        header_label.setWordWrap(True)
        header_layout.addWidget(header_label)
        
        # Content
        content_frame = QFrame()
        content_frame.setProperty("class", "glass-card")
        content_layout_inner = QVBoxLayout(content_frame)
        content_layout_inner.setContentsMargins(20, 20, 20, 20)
        
        placeholder = QLabel("🚧 Advanced security features under development\n\n"
                            "This tab will include:\n"
                            "• Security access levels\n"
                            "• PIN code management\n"
                            "• Diagnostic logging\n"
                            "• System audit trails\n"
                            "• Backup and restore functions")
        placeholder.setProperty("class", "placeholder-text")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setWordWrap(True)
        
        content_layout_inner.addWidget(placeholder)
        
        content_layout.addWidget(header_frame)
        content_layout.addWidget(content_frame)
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(security_tab, "🔐 Security")
        
    def create_status_bar(self):
        """Create RESPONSIVE status bar"""
        status_frame = QFrame()
        status_frame.setProperty("class", "glass-card")
        status_frame.setMaximumHeight(50)
        
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        self.status_label = QLabel("✨ Ready to program keys")
        self.status_label.setProperty("class", "status-ready")
        self.status_label.setWordWrap(True)
        self.status_label.setMinimumWidth(200)
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        # Add responsive system info
        system_info = QLabel(f"Screen: {self.current_window_width}px")
        system_info.setProperty("class", "system-info")
        status_layout.addWidget(system_info)
        
        status_frame.setLayout(status_layout)
        self.statusBar().addPermanentWidget(status_frame, 1)
        
    def start_live_updates(self):
        """Start live updates for dashboard gauges"""
        self.live_timer = QTimer()
        self.live_timer.timeout.connect(self.update_live_data)
        self.live_timer.start(2000)

    def change_theme(self, theme_name):
        """Handle theme change"""
        if theme_name == get_current_theme_name():
            return
            
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Change Theme", 
                                   f"Apply '{theme_name}'?\nApplication restart required.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if save_theme_config(theme_name):
                QMessageBox.information(self, "Restart Required", 
                                      "Theme preference saved.\n\nPlease restart the application to apply changes.")
            else:
                QMessageBox.warning(self, "Error", "Failed to save theme configuration.")
        else:
             # Revert combo box
            index = self.theme_combo.findText(get_current_theme_name())
            if index >= 0:
                self.theme_combo.blockSignals(True)
                self.theme_combo.setCurrentIndex(index)
                self.theme_combo.blockSignals(False)
        
    def update_live_data(self):
        """Update live data for dashboard"""
        try:
            if hasattr(self, 'dashboard_tab'):
                current_success = random.randint(96, 99)
                self.dashboard_tab.success_card.update_value(current_success)

                keys_today = random.randint(10, 15)
                self.dashboard_tab.keys_today_card.update_value(keys_today)

        except Exception as e:
            logger.error(f"Error updating live data: {e}")

    def on_brand_changed(self, brand):
        """Handle brand change"""
        self.selected_brand = brand
        if hasattr(self, 'dashboard_tab') and hasattr(self.dashboard_tab, 'brand_info_label'):
            self.dashboard_tab.brand_info_label.setText(brand)
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
        if hasattr(self, 'transponder_tab'):
            self.transponder_tab.add_sample_transponder_data()
        
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

        if hasattr(self, 'key_programming_tab'):
            code = self.key_programming_tab.security_input.text().strip()
            if not self.validate_security_code(code):
                self.status_label.setText("❌ Invalid security code (alphanumeric, 4-8 chars)")
                return

            logger.info("Initiating key programming")
            self.status_label.setText("🔑 Programming new key...")
            self.key_programming_tab.key_status.setText("🟡 Programming...")
            self.key_programming_tab.key_status.setProperty("class", "status-warning")
            self.key_programming_tab.key_progress.setVisible(True)
            self.key_programming_tab.key_progress.setValue(0)

            self.program_timer = QTimer()
            self.program_timer.timeout.connect(self.update_program_progress)
            self.program_timer.start(100)
        
    def update_program_progress(self):
        """Update programming progress"""
        if hasattr(self, 'key_programming_tab'):
            current = self.key_programming_tab.key_progress.value()
            if current < 100:
                self.key_programming_tab.key_progress.setValue(current + 10)
            else:
                self.program_timer.stop()
                self.programming_complete()
        
    def programming_complete(self):
        """Called when programming completes"""
        logger.info("Key programming completed")
        self.status_label.setText("✅ Key programmed successfully!")
        if hasattr(self, 'key_programming_tab'):
            self.key_programming_tab.key_status.setText("🟢 Programmed")
            self.key_programming_tab.key_status.setProperty("class", "status-success")
            self.key_programming_tab.key_progress.setVisible(False)
        self.last_op_label.setText("Key Programming")
        self.last_op_label.setProperty("class", "status-success")

        if hasattr(self, 'dashboard_tab'):
            self.dashboard_tab.keys_today_card.update_value(13)
        
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
        if hasattr(self, 'key_programming_tab'):
            self.key_programming_tab.security_input.clear()
            self.key_programming_tab.key_status.setText("🔴 No Key Detected")
            self.key_programming_tab.key_status.setProperty("class", "status-error")
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
        # FIXED: Apply DACOS theme properly as per AI_RULES.md
        apply_theme(app)

        window = AutoKeyApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
