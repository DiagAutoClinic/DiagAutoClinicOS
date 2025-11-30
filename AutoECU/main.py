# main.py - COMPLETE ECU PROGRAMMING IMPLEMENTATION

#!/usr/bin/env python3
"""
AutoECU - Automotive ECU Programming Tool
FUTURISTIC GLASSMORPHIC DESIGN with Teal Theme
"""

import sys
import os
import re
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QWidget, QPushButton, QLabel, QComboBox, QTabWidget,
                            QGroupBox, QTableWidget, QTableWidgetItem, QProgressBar,
                            QTextEdit, QLineEdit, QHeaderView, QFrame, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# FIXED: Enhanced import path resolution for shared modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(parent_dir)  # Go up to DiagAutoClinicOS root

# Add all possible paths
sys.path.insert(0, project_root)  # DiagAutoClinicOS root
sys.path.insert(0, parent_dir)    # AutoECU directory
sys.path.insert(0, current_dir)   # Current script directory
sys.path.insert(0, os.path.join(project_root, 'shared'))  # Shared modules

try:
    from shared.themes.dacos_theme import DACOS_THEME, DACOS_STYLESHEET, apply_dacos_theme, get_dacos_color
    from shared.brand_database import get_brand_info, get_brand_list
    from shared.circular_gauge import CircularGauge, StatCard
    from shared.mock_ecu_engine import MockECUEngine
    print("Successfully imported DACOS theme and shared modules")
except ImportError as e:
    print(f"Warning: Failed to import modules: {e}")
    # Fallback classes
    DACOS_THEME = {
        "bg_main": "#0A1A1A",
        "bg_panel": "#0D2323",
        "bg_card": "#134F4A",
        "accent": "#21F5C1",
        "glow": "#2AF5D1",
        "text_main": "#E8F4F2",
        "text_muted": "#9ED9CF",
        "error": "#FF4D4D",
        "success": "#10B981",
        "warning": "#F59E0B"
    }
    DACOS_STYLESHEET = "/* Fallback DACOS stylesheet */"

    def apply_dacos_theme(app):
        app.setStyleSheet(DACOS_STYLESHEET)
        return True

    def get_dacos_color(color_name):
        return DACOS_THEME.get(color_name, DACOS_THEME['accent'])

    def get_brand_list():
        return ["Toyota", "Honda", "Ford", "BMW", "Mercedes-Benz"]

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
            layout.addWidget(QLabel(f"{title}\n{value}"))
        def update_value(self, val): pass

    class MockECUEngine:
        def __init__(self, *args, **kwargs): pass
        def check_start_ready(self): return {"start_ready": False}
        def simulate_immo_off(self): return {"success": False}
        def simulate_egr_dpf_removal(self): return {"success": False}

class AutoECUApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_brand = "Toyota"
        self.current_window_width = 1366
        self.mock_ecu = MockECUEngine(self.selected_brand, "Generic")
        self.init_ui()
        
    def init_ui(self):
        """Initialize DACOS Unified Theme user interface"""
        self.setWindowTitle("AutoECU Pro - DACOS Unified Theme")
        self.setMinimumSize(1280, 700)
        self.resize(1366, 768)

        # Apply DACOS theme as per AI_RULES.md
        # Theme is applied in main() function

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create header
        self.create_header(main_layout)
        
        # Create main tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_ecu_scan_tab()
        self.create_programming_tab()
        self.create_parameters_tab()
        self.create_diagnostics_tab()
        self.create_coding_tab()
        
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

    def update_responsive_layouts(self):
        """Update all responsive layouts based on current window size"""
        # Update dashboard stats grid
        if hasattr(self, 'stats_grid'):
            columns = self.get_column_count()
            self.update_stats_layout(columns)

        # Update quick actions grid
        if hasattr(self, 'quick_actions_layout'):
            self.update_quick_actions_layout()

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

    def update_stats_layout(self, columns):
        """Update stats layout based on column count"""
        # Clear existing layout
        for i in reversed(range(self.stats_grid.count())):
            self.stats_grid.itemAt(i).widget().setParent(None)

        cards = [self.ecu_health_card, self.programming_card, self.modules_card]

        for i, card in enumerate(cards):
            row = i // columns
            col = i % columns
            self.stats_grid.addWidget(card, row, col)

        # Update column stretches
        for i in range(columns):
            self.stats_grid.setColumnStretch(i, 1)
        # Clear unused column stretches
        for i in range(columns, 4):
            self.stats_grid.setColumnStretch(i, 0)

    def update_quick_actions_layout(self):
        """Update quick actions layout responsively"""
        # Clear existing layout
        for i in reversed(range(self.quick_actions_layout.count())):
            self.quick_actions_layout.itemAt(i).widget().setParent(None)

        buttons = [self.scan_btn, self.ready_btn, self.immo_btn, self.egr_btn]
        columns = 4  # Force 4 columns for 4 buttons in 1 row

        for i, btn in enumerate(buttons):
            row = i // columns
            col = i % columns
            self.quick_actions_layout.addWidget(btn, row, col)

    def create_header(self, layout):
        """Create DACOS Unified Theme header"""
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_frame.setMaximumHeight(150)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setSpacing(20)
        header_layout.setContentsMargins(20, 15, 20, 15)

        # Title section
        title_section = QWidget()
        title_layout = QVBoxLayout(title_section)
        title_layout.setSpacing(5)

        title_label = QLabel("AutoECU Pro")
        title_label.setProperty("class", "hero-title")
        title_font = QFont("Segoe UI", 22, QFont.Weight.Bold)
        title_label.setFont(title_font)

        subtitle_label = QLabel("⚙️ Professional ECU Programming")
        subtitle_label.setProperty("class", "section-title")

        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)

        # Brand selector
        brand_section = QWidget()
        brand_layout = QVBoxLayout(brand_section)
        brand_layout.setSpacing(5)

        brand_label = QLabel("Vehicle Brand:")
        brand_label.setProperty("class", "section-title")

        self.brand_combo = QComboBox()
        self.brand_combo.addItems(get_brand_list())
        self.brand_combo.setCurrentText(self.selected_brand)
        self.brand_combo.currentTextChanged.connect(self.on_brand_changed)
        self.brand_combo.setMinimumWidth(180)

        brand_layout.addWidget(brand_label)
        brand_layout.addWidget(self.brand_combo)

        header_layout.addWidget(title_section)
        header_layout.addStretch()
        header_layout.addWidget(brand_section)

        layout.addWidget(header_frame)

    def create_dashboard_tab(self):
        """Create FUTURISTIC dashboard with live stats – NOW FULLY RESPONSIVE"""
        dashboard_tab = QWidget()
        layout = QVBoxLayout(dashboard_tab)
        layout.setSpacing(20)
        layout.setContentsMargins(15, 15, 15, 15)

        # === RESPONSIVE STATS OVERVIEW ===
        stats_frame = QFrame()
        stats_frame.setProperty("class", "glass-card")
        stats_frame.setMinimumHeight(280)

        # This is the grid that will be re-arranged on resize
        self.stats_grid = QGridLayout(stats_frame)
        self.stats_grid.setSpacing(20)
        self.stats_grid.setContentsMargins(25, 25, 25, 25)

        # Create the 3 stat cards (CircularGauge + label style from shared module)
        self.ecu_health_card   = StatCard("ECU Health",      96,  max_value=100, unit="")
        self.programming_card  = StatCard("Last Program",    100, max_value=100, unit="%")
        self.modules_card      = StatCard("ECU Modules",     12,  max_value=30,  unit="pc")

        # Set uniform fixed size for all stat cards
        self.ecu_health_card.setFixedSize(250, 250)
        self.programming_card.setFixedSize(250, 250)
        self.modules_card.setFixedSize(250, 250)

        # Initially add them (will be re-positioned by update_stats_layout)
        self.cards = [self.ecu_health_card, self.programming_card, self.modules_card]

        for card in self.cards:
            self.stats_grid.addWidget(card)

        # === Quick Actions Section (already responsive) ===
        actions_frame = QFrame()
        actions_frame.setProperty("class", "glass-card")
        actions_layout = QVBoxLayout(actions_frame)
        actions_layout.setSpacing(15)
        actions_layout.setContentsMargins(20, 20, 20, 20)

        actions_title = QLabel("Quick Actions")
        actions_title.setStyleSheet(f"color: {get_dacos_color('accent')}; font-size: 16pt; font-weight: bold;")
        actions_layout.addWidget(actions_title)

        self.quick_actions_layout = QGridLayout()
        self.quick_actions_layout.setSpacing(20)

        # Buttons (same as before)
        self.scan_btn = QPushButton("Scan ECUs")
        self.ready_btn = QPushButton("Check Start Ready")
        self.immo_btn = QPushButton("IMMO Off")
        self.egr_btn = QPushButton("EGR-DPF Remove")
        self.file_btn = QPushButton("Import File")
        self.dtc_btn = QPushButton("Add Start DTC")

        for btn in (self.scan_btn, self.ready_btn, self.immo_btn,
                    self.egr_btn, self.file_btn, self.dtc_btn):
            btn.setMinimumHeight(60)
            btn.setProperty("class", "primary" if btn == self.scan_btn else
                                      "success" if btn == self.ready_btn else
                                      "danger"  if btn == self.immo_btn else
                                      "warning" if btn == self.egr_btn else
                                      "info"    if btn == self.file_btn else "secondary")

        # Connect signals (unchanged)
        self.scan_btn.clicked.connect(self.scan_ecus)
        self.ready_btn.clicked.connect(self.check_start_ready)
        self.immo_btn.clicked.connect(self.perform_immo_off)
        self.egr_btn.clicked.connect(self.perform_egr_dpf_removal)
        self.file_btn.clicked.connect(self.import_start_ready_file)
        self.dtc_btn.clicked.connect(self.add_start_ready_dtc)

        actions_layout.addLayout(self.quick_actions_layout)

        # === System Information (unchanged) ===
        info_frame = QFrame()
        info_frame.setProperty("class", "glass-card")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(10)
        info_layout.setContentsMargins(20, 20, 20, 20)

        info_title = QLabel("System Information")
        info_title.setStyleSheet(f"color: {get_dacos_color('accent')}; font-size: 14pt; font-weight: bold;")
        info_layout.addWidget(info_title)

        info_grid = QGridLayout()
        info_grid.setSpacing(10)

        info_grid.addWidget(QLabel("Selected Brand:"), 0, 0)
        self.brand_info_label = QLabel(self.selected_brand)
        info_grid.addWidget(self.brand_info_label, 0, 1)

        info_grid.addWidget(QLabel("Connection Status:"), 1, 0)
        self.conn_info_label = QLabel("Disconnected")
        self.conn_info_label.setStyleSheet(f"color: {get_dacos_color('error')};")
        info_grid.addWidget(self.conn_info_label, 1, 1)

        info_grid.addWidget(QLabel("Last Operation:"), 2, 0)
        self.last_op_label = QLabel("None")
        info_grid.addWidget(self.last_op_label, 2, 1)

        for i in range(3):
            info_grid.itemAtPosition(i, 0).widget().setStyleSheet(f"color: {get_dacos_color('text_muted')}; font-weight: bold;")

        info_layout.addLayout(info_grid)

        # === Final layout with scroll area (important for small screens) ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.addWidget(stats_frame)
        content_layout.addWidget(actions_frame)
        content_layout.addWidget(info_frame)
        content_layout.addStretch()

        scroll.setWidget(content_widget)

        layout.addWidget(scroll)
        self.tab_widget.addTab(dashboard_tab, "Dashboard")

        # <<< CRITICAL >>> Force initial responsive layout
        QTimer.singleShot(100, lambda: self.update_responsive_layouts())

    def create_ecu_scan_tab(self):
        """Create FUTURISTIC ECU scan tab"""
        scan_tab = QWidget()
        layout = QVBoxLayout(scan_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        header_label = QLabel("🔍 ECU Detection & Scanning")
        header_label.setStyleSheet(f"color: {get_dacos_color('accent')}; font-size: 18pt; font-weight: bold;")
        
        scan_btn = QPushButton("🔄 Scan for ECUs")
        scan_btn.setProperty("class", "primary")
        scan_btn.setMinimumHeight(45)
        scan_btn.clicked.connect(self.scan_ecus)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(scan_btn)
        
        # Scan controls
        controls_frame = QFrame()
        controls_frame.setProperty("class", "glass-card")
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setSpacing(15)
        controls_layout.setContentsMargins(20, 20, 20, 20)
        
        # ECU table
        self.ecu_table = QTableWidget()
        self.ecu_table.setColumnCount(4)
        self.ecu_table.setHorizontalHeaderLabels(["ECU Name", "Protocol", "Status", "Address"])
        self.ecu_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        controls_layout.addWidget(self.ecu_table)
        
        # Status section
        status_frame = QFrame()
        status_frame.setProperty("class", "stat-card")
        status_frame.setMaximumHeight(80)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(15, 15, 15, 15)
        
        self.connection_status = QLabel("⚪ Disconnected")
        self.connection_status.setStyleSheet(f"color: {get_dacos_color('error')}; font-size: 12pt; font-weight: bold;")
        
        self.scan_progress = QProgressBar()
        self.scan_progress.setMinimumHeight(30)
        self.scan_progress.setVisible(False)
        
        status_layout.addWidget(QLabel("Connection:"))
        status_layout.addWidget(self.connection_status)
        status_layout.addWidget(self.scan_progress)
        status_layout.addStretch()
        
        layout.addWidget(header_frame)
        layout.addWidget(controls_frame)
        layout.addWidget(status_frame)
        
        self.tab_widget.addTab(scan_tab, "🔍 ECU Scan")
        
    def create_programming_tab(self):
        """Create FUTURISTIC ECU programming tab"""
        prog_tab = QWidget()
        layout = QVBoxLayout(prog_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        header_label = QLabel("⚙️ ECU Programming")
        header_label.setStyleSheet(f"color: {get_dacos_color('accent')}; font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(header_label)
        
        # Programming controls
        prog_frame = QFrame()
        prog_frame.setProperty("class", "glass-card")
        prog_layout = QVBoxLayout(prog_frame)
        prog_layout.setSpacing(15)
        prog_layout.setContentsMargins(20, 20, 20, 20)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        read_btn = QPushButton("📖 Read ECU Memory")
        read_btn.setProperty("class", "primary")
        read_btn.setMinimumHeight(50)
        read_btn.clicked.connect(self.read_ecu)
        
        write_btn = QPushButton("✍️ Write ECU Memory")
        write_btn.setProperty("class", "danger")
        write_btn.setMinimumHeight(50)
        write_btn.clicked.connect(self.write_ecu)
        
        verify_btn = QPushButton("✅ Verify Data")
        verify_btn.setProperty("class", "success")
        verify_btn.setMinimumHeight(50)
        verify_btn.clicked.connect(self.verify_ecu)
        
        btn_layout.addWidget(read_btn)
        btn_layout.addWidget(write_btn)
        btn_layout.addWidget(verify_btn)

        prog_layout.addLayout(btn_layout)
        
        # Hex viewer
        hex_label = QLabel("📄 ECU Memory View:")
        hex_label.setStyleSheet(f"color: {get_dacos_color('text_muted')}; font-weight: bold; margin-top: 10px;")
        
        self.hex_viewer = QTextEdit()
        self.hex_viewer.setPlaceholderText("ECU memory content will appear here...\nClick 'Read ECU Memory' to start")
        self.hex_viewer.setMinimumHeight(300)
        
        prog_layout.addWidget(hex_label)
        prog_layout.addWidget(self.hex_viewer)
        
        # Programming progress
        progress_label = QLabel("Programming Progress:")
        progress_label.setStyleSheet(f"color: {get_dacos_color('text_muted')}; font-weight: bold;")
        
        self.prog_progress = QProgressBar()
        self.prog_progress.setMinimumHeight(35)
        self.prog_progress.setTextVisible(True)
        self.prog_progress.setValue(0)
        
        prog_layout.addWidget(progress_label)
        prog_layout.addWidget(self.prog_progress)
        
        layout.addWidget(header_frame)
        layout.addWidget(prog_frame)
        
        self.tab_widget.addTab(prog_tab, "⚙️ Programming")
        
    def create_parameters_tab(self):
        """Create FUTURISTIC parameter editing tab"""
        param_tab = QWidget()
        layout = QVBoxLayout(param_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        header_label = QLabel("🎛️ ECU Parameters")
        header_label.setStyleSheet(f"color: {get_dacos_color('accent')}; font-size: 18pt; font-weight: bold;")
        
        load_btn = QPushButton("📥 Load Parameters")
        load_btn.setProperty("class", "primary")
        load_btn.setMinimumHeight(45)
        load_btn.clicked.connect(self.load_parameters)
        
        save_btn = QPushButton("💾 Save Parameters")
        save_btn.setProperty("class", "success")
        save_btn.setMinimumHeight(45)
        save_btn.clicked.connect(self.save_parameters)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(load_btn)
        header_layout.addWidget(save_btn)
        
        # Parameters table
        param_frame = QFrame()
        param_frame.setProperty("class", "glass-card")
        param_layout = QVBoxLayout(param_frame)
        param_layout.setContentsMargins(20, 20, 20, 20)
        
        table_label = QLabel("Available Parameters:")
        table_label.setStyleSheet(f"color: {get_dacos_color('text_muted')}; font-weight: bold; margin-bottom: 10px;")
        
        self.param_table = QTableWidget()
        self.param_table.setColumnCount(3)
        self.param_table.setHorizontalHeaderLabels(["Parameter", "Value", "Unit"])
        self.param_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        param_layout.addWidget(table_label)
        param_layout.addWidget(self.param_table)
        
        layout.addWidget(header_frame)
        layout.addWidget(param_frame)
        
        self.tab_widget.addTab(param_tab, "🎛️ Parameters")
        
    def create_diagnostics_tab(self):
        """Create FUTURISTIC diagnostics tab"""
        diag_tab = QWidget()
        layout = QVBoxLayout(diag_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        header_label = QLabel("🔧 ECU Diagnostics")
        header_label.setStyleSheet(f"color: {get_dacos_color('accent')}; font-size: 18pt; font-weight: bold;")
        
        scan_dtc_btn = QPushButton("🔍 Read DTCs")
        scan_dtc_btn.setProperty("class", "primary")
        scan_dtc_btn.setMinimumHeight(45)
        scan_dtc_btn.clicked.connect(self.read_dtcs)
        
        clear_dtc_btn = QPushButton("🗑️ Clear DTCs")
        clear_dtc_btn.setProperty("class", "danger")
        clear_dtc_btn.setMinimumHeight(45)
        clear_dtc_btn.clicked.connect(self.clear_dtcs)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(scan_dtc_btn)
        header_layout.addWidget(clear_dtc_btn)
        
        # DTC table
        diag_frame = QFrame()
        diag_frame.setProperty("class", "glass-card")
        diag_layout = QVBoxLayout(diag_frame)
        diag_layout.setContentsMargins(20, 20, 20, 20)
        
        table_label = QLabel("Diagnostic Trouble Codes:")
        table_label.setStyleSheet(f"color: {get_dacos_color('text_muted')}; font-weight: bold; margin-bottom: 10px;")
        
        self.dtc_table = QTableWidget()
        self.dtc_table.setColumnCount(3)
        self.dtc_table.setHorizontalHeaderLabels(["DTC Code", "Description", "Status"])
        self.dtc_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        diag_layout.addWidget(table_label)
        diag_layout.addWidget(self.dtc_table)
        
        layout.addWidget(header_frame)
        layout.addWidget(diag_frame)
        
        self.tab_widget.addTab(diag_tab, "🔧 Diagnostics")

    def create_coding_tab(self):
        """Create FUTURISTIC coding/adaptations tab"""
        coding_tab = QWidget()
        layout = QVBoxLayout(coding_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        header_label = QLabel("🔐 Module Coding & Adaptations")
        header_label.setStyleSheet(f"color: {get_dacos_color('accent')}; font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(header_label)
        
        # Content
        content_frame = QFrame()
        content_frame.setProperty("class", "glass-card")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        placeholder = QLabel("🚧 Module coding interface under development\n\n"
                            "This tab will include:\n"
                            "• Long coding editor\n"
                            "• Adaptation values\n"
                            "• Module configuration\n"
                            "• Security access")
        placeholder.setStyleSheet(f"color: {get_dacos_color('text_muted')}; font-size: 12pt; line-height: 1.8;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        content_layout.addWidget(placeholder)
        
        layout.addWidget(header_frame)
        layout.addWidget(content_frame)
        layout.addStretch()
        
        self.tab_widget.addTab(coding_tab, "🔐 Coding")
        
    def create_status_bar(self):
        """Create FUTURISTIC status bar"""
        status_frame = QFrame()
        status_frame.setProperty("class", "glass-card")
        status_frame.setMaximumHeight(40)
        
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        self.status_label = QLabel("✨ Ready to program ECUs")
        self.status_label.setStyleSheet(f"color: {get_dacos_color('success')}; font-weight: bold;")
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        status_frame.setLayout(status_layout)
        self.statusBar().addPermanentWidget(status_frame, 1)
        
    def start_live_updates(self):
        """Start live updates for dashboard gauges"""
        self.live_timer = QTimer()
        self.live_timer.timeout.connect(self.update_live_data)
        self.live_timer.start(2000)  # Update every 2 seconds
        
    def update_live_data(self):
        """Update live data for dashboard"""
        try:
            # Update ECU health with slight random variation
            current_health = random.randint(94, 98)
            self.ecu_health_card.update_value(current_health)
            
            
        except Exception as e:
            print(f"Error updating live data: {e}")
    
    
    def on_brand_changed(self, brand):
        """Handle brand change"""
        self.selected_brand = brand
        self.brand_info_label.setText(brand)
        self.status_label.setText(f"✨ Brand changed to: {brand}")

        # Update mock ECU engine with new brand
        self.mock_ecu = MockECUEngine(brand, "Generic")
        
    def identify_modules(self):
        """Identify ECU modules"""
        try:
            self.status_label.setText("🔍 Identifying ECU modules...")
            self.last_op_label.setText("Module Identification")
            self.last_op_label.setStyleSheet(f"color: {get_dacos_color('success')};")
            
            # Simulate identification process
            QTimer.singleShot(1500, self.complete_identification)
        except Exception as e:
            self.status_label.setText(f"❌ Error identifying modules: {e}")
    
    def complete_identification(self):
        """Complete module identification"""
        self.status_label.setText("✅ Module identification completed")
        self.modules_card.update_value(8)  # Update modules count
        
    def verify_ecu(self):
        """Verify ECU data"""
        try:
            self.status_label.setText("✅ Verifying ECU data...")
            self.prog_progress.setValue(0)
            
            # Simulate verification progress
            self.verify_timer = QTimer()
            self.verify_timer.timeout.connect(self.update_verify_progress)
            self.verify_timer.start(100)
        except Exception as e:
            self.status_label.setText(f"❌ Error verifying ECU: {e}")
    
    def update_verify_progress(self):
        """Update verification progress"""
        current = self.prog_progress.value()
        if current < 100:
            self.prog_progress.setValue(current + 10)
        else:
            self.verify_timer.stop()
            self.status_label.setText("✅ ECU verification successful")
            self.prog_progress.setValue(100)
                
    def scan_ecus(self):
        """Scan for ECU modules using mock engine"""
        try:
            self.connection_status.setText("🔄 Scanning...")
            self.connection_status.setStyleSheet(f"color: {get_dacos_color('warning')}; font-size: 12pt; font-weight: bold;")
            self.scan_progress.setVisible(True)
            self.scan_progress.setValue(0)

            self.status_label.setText("🔍 Scanning for ECU modules...")
            self.last_op_label.setText("ECU Scan")
            self.last_op_label.setStyleSheet(f"color: {get_dacos_color('success')};")

            # Use mock ECU engine for scanning
            self.mock_ecu.connect_to_ecu("0x7E0")

            # Simulate scan progress
            self.scan_timer = QTimer()
            self.scan_timer.timeout.connect(self.update_scan_progress)
            self.scan_timer.start(100)
        except Exception as e:
            self.status_label.setText(f"❌ Error during scan: {e}")
        
    def update_scan_progress(self):
        """Update scan progress"""
        try:
            current = self.scan_progress.value()
            if current < 100:
                self.scan_progress.setValue(current + 10)
            else:
                self.scan_timer.stop()
                self.scan_progress.setVisible(False)
                self.connection_status.setText("✅ Connected")
                self.connection_status.setStyleSheet(f"color: {get_dacos_color('success')}; font-size: 12pt; font-weight: bold;")
                self.conn_info_label.setText("Connected")
                self.conn_info_label.setStyleSheet(f"color: {get_dacos_color('success')};")
                
                # Add sample ECU data
                self.add_sample_ecu_data()
                self.status_label.setText("✅ ECU scan completed successfully")
                
                # Update modules count
                self.modules_card.update_value(4)
        except Exception as e:
            self.status_label.setText(f"❌ Error updating progress: {e}")
            
    def add_sample_ecu_data(self):
        """Add sample ECU data to table"""
        sample_data = [
            ["Engine Control Module", "CAN", "✅ Online", "0x7E0"],
            ["Transmission Control", "CAN", "✅ Online", "0x7E1"],
            ["ABS Module", "CAN", "✅ Online", "0x7E2"],
            ["Body Control Module", "LIN", "✅ Online", "0x7E3"]
        ]
        
        self.ecu_table.setRowCount(len(sample_data))
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                clean_value = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', value)
                item = QTableWidgetItem(clean_value)
                if col == 2:  # Status column
                    item.setForeground(Qt.GlobalColor.green)
                self.ecu_table.setItem(row, col, item)
                
    def read_ecu(self):
        """Read ECU memory using mock engine"""
        try:
            self.status_label.setText("📖 Reading ECU memory...")
            self.last_op_label.setText("ECU Read")
            self.last_op_label.setStyleSheet("color: #10b981;")
            self.prog_progress.setValue(0)

            # Use mock ECU engine for memory reading
            result = self.mock_ecu.read_ecu_memory(0x0000, 64)  # Read 64 bytes from address 0

            # Simulate reading progress
            self.read_timer = QTimer()
            self.read_timer.timeout.connect(self.update_read_progress)
            self.read_timer.start(50)
        except Exception as e:
            self.status_label.setText(f"❌ Error reading ECU: {e}")
    
    def update_read_progress(self):
        """Update read progress"""
        current = self.prog_progress.value()
        if current < 100:
            self.prog_progress.setValue(current + 5)
        else:
            self.read_timer.stop()
            self.status_label.setText("✅ ECU memory read successfully")
            self.hex_viewer.setText(
                "0000: 12 34 56 78 9A BC DE F0  11 22 33 44 55 66 77 88\n"
                "0010: FF EE DD CC BB AA 99 88  77 66 55 44 33 22 11 00\n"
                "0020: 01 23 45 67 89 AB CD EF  FE DC BA 98 76 54 32 10\n"
                "0030: 55 AA 33 CC 66 99 22 BB  44 DD 77 EE 00 FF 11 88\n"
                "0040: 98 76 54 32 10 FE DC BA  89 AB CD EF 01 23 45 67"
            )
            self.prog_progress.setValue(100)
        
    def write_ecu(self):
        """Write to ECU memory using mock engine"""
        try:
            self.status_label.setText("✍️ Writing to ECU...")
            self.last_op_label.setText("ECU Write")
            self.last_op_label.setStyleSheet("color: #10b981;")
            self.prog_progress.setValue(0)

            # Use mock ECU engine for flash programming
            test_data = bytes([i % 256 for i in range(64)])  # Test data
            result = self.mock_ecu.flash_ecu_memory(test_data, 0x0000)

            # Simulate writing progress
            self.write_timer = QTimer()
            self.write_timer.timeout.connect(self.update_write_progress)
            self.write_timer.start(80)
        except Exception as e:
            self.status_label.setText(f"❌ Error writing ECU: {e}")
    
    def update_write_progress(self):
        """Update write progress"""
        current = self.prog_progress.value()
        if current < 100:
            self.prog_progress.setValue(current + 8)
        else:
            self.write_timer.stop()
            self.status_label.setText("✅ ECU programming completed successfully")
            self.programming_card.update_value(100)
            self.prog_progress.setValue(100)
    
    def load_parameters(self):
        """Load sample parameters"""
        try:
            self.status_label.setText("📥 Loading ECU parameters...")
            
            sample_params = [
                ["Engine RPM Limit", "6800", "RPM"],
                ["Idle Speed", "750", "RPM"],
                ["Injection Timing", "12.5", "°BTDC"],
                ["Ignition Advance", "18.3", "°BTDC"],
                ["Fuel Pressure", "3.8", "bar"],
                ["Coolant Temp Threshold", "95", "°C"],
                ["Boost Pressure", "1.2", "bar"],
                ["Lambda Value", "0.98", "λ"]
            ]
            
            self.param_table.setRowCount(len(sample_params))
            for row, data in enumerate(sample_params):
                for col, value in enumerate(data):
                    self.param_table.setItem(row, col, QTableWidgetItem(value))
            
            self.status_label.setText("✅ Parameters loaded successfully")
            self.last_op_label.setText("Load Parameters")
            self.last_op_label.setStyleSheet("color: #10b981;")
        except Exception as e:
            self.status_label.setText(f"❌ Error loading parameters: {e}")
    
    def save_parameters(self):
        """Save parameters (simulated)"""
        try:
            self.status_label.setText("💾 Saving parameters...")
            QTimer.singleShot(1000, lambda: self.status_label.setText("✅ Parameters saved successfully"))
            self.last_op_label.setText("Save Parameters")
            self.last_op_label.setStyleSheet("color: #10b981;")
        except Exception as e:
            self.status_label.setText(f"❌ Error saving parameters: {e}")
    
    def read_dtcs(self):
        """Read diagnostic trouble codes"""
        try:
            self.status_label.setText("🔍 Reading diagnostic trouble codes...")
            
            sample_dtcs = [
                ["P0300", "Random/Multiple Cylinder Misfire Detected", "Active"],
                ["P0128", "Coolant Thermostat (Coolant Temperature Below Thermostat Regulating Temperature)", "Pending"],
                ["U0100", "Lost Communication With ECM/PCM 'A'", "Inactive"],
                ["C0034", "Left Front Wheel Speed Sensor Circuit", "Active"]
            ]
            
            self.dtc_table.setRowCount(len(sample_dtcs))
            for row, data in enumerate(sample_dtcs):
                for col, value in enumerate(data):
                    item = QTableWidgetItem(value)
                    if col == 2:  # Status column
                        if value == "Active":
                            item.setForeground(Qt.GlobalColor.red)
                        elif value == "Pending":
                            item.setForeground(Qt.GlobalColor.yellow)
                        else:
                            item.setForeground(Qt.GlobalColor.gray)
                    self.dtc_table.setItem(row, col, item)
            
            self.status_label.setText("✅ DTCs read successfully")
            self.last_op_label.setText("Read DTCs")
            self.last_op_label.setStyleSheet("color: #10b981;")
        except Exception as e:
            self.status_label.setText(f"❌ Error reading DTCs: {e}")
    
    def clear_dtcs(self):
        """Clear diagnostic trouble codes"""
        try:
            self.status_label.setText("🗑️ Clearing diagnostic trouble codes...")
            self.dtc_table.setRowCount(0)
            QTimer.singleShot(1000, lambda: self.status_label.setText("✅ DTCs cleared successfully"))
            self.last_op_label.setText("Clear DTCs")
            self.last_op_label.setStyleSheet("color: #10b981;")
        except Exception as e:
            self.status_label.setText(f"❌ Error clearing DTCs: {e}")

    def check_start_ready(self):
        """Check if ECU is start-ready"""
        try:
            self.status_label.setText("🔍 Checking start-ready status...")

            # Use mock ECU engine
            result = self.mock_ecu.check_start_ready()

            if result["start_ready"]:
                self.status_label.setText("✅ ECU is start-ready!")
                self.last_op_label.setText("Start Ready: YES")
                self.last_op_label.setStyleSheet("color: #10b981;")
            else:
                self.status_label.setText("❌ ECU not start-ready")
                self.last_op_label.setText("Start Ready: NO")
                self.last_op_label.setStyleSheet(f"color: {get_dacos_color('error')};")

            # Update system info
            self.conn_info_label.setText(f"Start Ready: {result['start_ready']}")
            self.conn_info_label.setStyleSheet("color: #10b981;" if result["start_ready"] else "color: #ef4444;")

        except Exception as e:
            self.status_label.setText(f"❌ Error checking start-ready: {e}")

    def perform_immo_off(self):
        """Perform IMMO disable operation"""
        try:
            self.status_label.setText("🔐 Performing IMMO disable...")

            result = self.mock_ecu.simulate_immo_off()

            if result["success"]:
                self.status_label.setText("✅ IMMO disabled successfully!")
                self.last_op_label.setText("IMMO: DISABLED")
                self.last_op_label.setStyleSheet("color: #10b981;")
            else:
                self.status_label.setText(f"❌ IMMO disable failed: {result.get('error', 'Unknown error')}")
                self.last_op_label.setText("IMMO: FAILED")
                self.last_op_label.setStyleSheet("color: #ef4444;")

        except Exception as e:
            self.status_label.setText(f"❌ Error performing IMMO off: {e}")

    def perform_egr_dpf_removal(self):
        """Perform EGR-DPF removal operation"""
        try:
            self.status_label.setText("🔧 Performing EGR-DPF removal...")

            result = self.mock_ecu.simulate_egr_dpf_removal()

            if result["success"]:
                self.status_label.setText("✅ EGR-DPF removal completed!")
                self.last_op_label.setText("EGR-DPF: REMOVED")
                self.last_op_label.setStyleSheet("color: #10b981;")
            else:
                self.status_label.setText(f"❌ EGR-DPF removal failed: {result.get('error', 'Unknown error')}")
                self.last_op_label.setText("EGR-DPF: FAILED")
                self.last_op_label.setStyleSheet("color: #ef4444;")

        except Exception as e:
            self.status_label.setText(f"❌ Error performing EGR-DPF removal: {e}")

    def import_start_ready_file(self):
        """Import start-ready configuration file"""
        try:
            from PyQt6.QtWidgets import QFileDialog

            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select Start-Ready File", "", "All Files (*.*)"
            )

            if file_path:
                self.status_label.setText("📥 Importing start-ready file...")

                result = self.mock_ecu.import_start_ready_file(file_path)

                if result["success"]:
                    self.status_label.setText("✅ Start-ready file imported successfully!")
                    self.last_op_label.setText("File Import: SUCCESS")
                    self.last_op_label.setStyleSheet("color: #10b981;")

                    # Update start-ready status
                    self.conn_info_label.setText("Start Ready: YES (File Imported)")
                    self.conn_info_label.setStyleSheet("color: #10b981;")
                else:
                    self.status_label.setText(f"❌ File import failed: {result.get('error', 'Unknown error')}")
                    self.last_op_label.setText("File Import: FAILED")
                    self.last_op_label.setStyleSheet("color: #ef4444;")

        except Exception as e:
            self.status_label.setText(f"❌ Error importing file: {e}")

    def add_start_ready_dtc(self):
        """Add DTC to enable start-ready mode"""
        try:
            from PyQt6.QtWidgets import QInputDialog

            dtc_code, ok = QInputDialog.getText(
                self, "Add Start-Ready DTC", "Enter DTC code (e.g., P0000):"
            )

            if ok and dtc_code:
                self.status_label.setText(f"🔧 Adding start-ready DTC: {dtc_code}")

                result = self.mock_ecu.add_start_ready_dtc(dtc_code)

                if result["success"]:
                    self.status_label.setText(f"✅ Start-ready DTC {dtc_code} added!")
                    self.last_op_label.setText(f"DTC Added: {dtc_code}")
                    self.last_op_label.setStyleSheet("color: #10b981;")

                    # Update start-ready status
                    self.conn_info_label.setText("Start Ready: YES (DTC Added)")
                    self.conn_info_label.setStyleSheet("color: #10b981;")
                else:
                    self.status_label.setText("❌ Failed to add DTC")
                    self.last_op_label.setText("DTC Add: FAILED")
                    self.last_op_label.setStyleSheet("color: #ef4444;")

        except Exception as e:
            self.status_label.setText(f"❌ Error adding DTC: {e}")

def main():
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("AutoECU Pro")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("DiagAutoClinicOS")

    try:
        # Apply DACOS theme as per AI_RULES.md
        apply_dacos_theme(app)

        # Create and show main window
        window = AutoECUApp()

        sys.exit(app.exec())
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()