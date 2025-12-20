# AutoDiag/ui/main_window.py
# AutoDiag Pro - Main Window Implementation
# Date: December 20, 2025

#!/usr/bin/env python3

import logging
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout, QWidget, QFrame,
    QLabel, QComboBox, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# Local imports
from AutoDiag.ui.dashboard_tab import DashboardTab
from AutoDiag.ui.diagnostics_tab import DiagnosticsTab
from AutoDiag.ui.live_data_tab import LiveDataTab
from AutoDiag.ui.special_functions_tab import SpecialFunctionsTab
from AutoDiag.ui.calibrations_tab import CalibrationsTab
from AutoDiag.ui.advanced_tab import AdvancedTab
from AutoDiag.ui.security_tab import SecurityTab
from AutoDiag.ui.can_bus_tab import CANBusDataTab

logger = logging.getLogger(__name__)

class ResponsiveHeader(QFrame):
    """Responsive header with brand selector and user info"""
    def __init__(self, parent=None, user_info=None):
        super().__init__(parent)
        self.setProperty("class", "glass-card")
        self.setMinimumHeight(120)
        self.setMaximumHeight(140)

        self.user_info = user_info or {
            'username': 'guest',
            'full_name': 'Guest User',
            'tier': 'BASIC',
            'permissions': []
        }

        layout = QHBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 15)
        layout.setSpacing(20)

        # Logo / Title
        title = QLabel("AutoDiag Pro")
        title.setProperty("class", "header-title")
        title_font = QFont("Segoe UI", 20, QFont.Weight.Bold)
        title.setFont(title_font)
        layout.addWidget(title)

        # User info
        user_label = QLabel(f"👤 {self.user_info['full_name']} ({self.user_info['tier']})")
        user_label.setProperty("class", "header-text")
        layout.addWidget(user_label, alignment=Qt.AlignmentFlag.AlignRight)

        # Brand selector
        brand_label = QLabel("Vehicle Brand:")
        brand_label.setProperty("class", "header-text")
        layout.addWidget(brand_label)

        self.brand_combo = QComboBox()
        self.brand_combo.setProperty("class", "combo-glass")
        self.brand_combo.setMinimumWidth(200)
        brands = ["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Volkswagen", "Nissan", "Hyundai", "GM/Chevrolet", "Subaru"]
        self.brand_combo.addItems(brands)
        self.brand_combo.currentTextChanged.connect(parent.update_brand if parent else lambda x: None)
        layout.addWidget(self.brand_combo)

        layout.addStretch()

class AutoDiagPro(QMainWindow):
    """Main application window"""
    def __init__(self, user_info=None, parent=None):
        super().__init__(parent)
        self.user_info = user_info or {}
        self.current_brand = "Toyota"

        self.setWindowTitle("AutoDiag Pro - Professional Diagnostic Suite v3.1.2")
        self.setMinimumSize(1200, 800)
        self.showMaximized()

        self.setup_ui()
        self.setup_tabs()
        self.start_timers()

        logger.info(f"Main window initialized for user: {self.user_info.get('username', 'unknown')}")

    def setup_ui(self):
        """Setup main layout and header"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        self.header = ResponsiveHeader(parent=self, user_info=self.user_info)
        main_layout.addWidget(self.header)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setProperty("class", "tab-widget")
        main_layout.addWidget(self.tab_widget)

        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setProperty("class", "status-text")
        self.statusBar().addWidget(self.status_label)

    def setup_tabs(self):
        """Initialize and add all tabs"""
        self.tabs = {}

        # Dashboard
        dashboard_tab = DashboardTab(self)
        tab_widget, title = dashboard_tab.create_tab()
        self.tab_widget.addTab(tab_widget, title)
        self.tabs['dashboard'] = dashboard_tab

        # Diagnostics
        diagnostics_tab = DiagnosticsTab(self)
        tab_widget = diagnostics_tab.create_tab()
        self.tab_widget.addTab(tab_widget, "🔧 Diagnostics")
        self.tabs['diagnostics'] = diagnostics_tab

        # Live Data
        live_data_tab = LiveDataTab(self)
        tab_widget, title = live_data_tab.create_tab()
        self.tab_widget.addTab(tab_widget, title)
        self.tabs['live_data'] = live_data_tab

        # Special Functions
        special_tab = SpecialFunctionsTab(self)
        tab_widget, title = special_tab.create_tab()
        self.tab_widget.addTab(tab_widget, title)
        self.tabs['special'] = special_tab

        # Calibrations & Resets
        cal_tab = CalibrationsTab(self)
        tab_widget, title = cal_tab.create_tab()
        self.tab_widget.addTab(tab_widget, title)
        self.tabs['calibrations'] = cal_tab

        # Advanced
        advanced_tab = AdvancedTab(self)
        tab_widget, title = advanced_tab.create_tab()
        self.tab_widget.addTab(tab_widget, title)
        self.tabs['advanced'] = advanced_tab

        # CAN Bus
        can_tab = CANBusDataTab(self)
        tab_widget, title = can_tab.create_tab(app=self)
        self.tab_widget.addTab(tab_widget, title)
        self.tabs['can_bus'] = can_tab

        # Security
        security_tab = SecurityTab(self)
        tab_widget, title = security_tab.create_tab()
        self.tab_widget.addTab(tab_widget, title)
        self.tabs['security'] = security_tab

    def start_timers(self):
        """Start any periodic updates"""
        # Example: periodic status update
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Every 5 seconds

    def update_status(self):
        """Update status bar periodically"""
        current_tab = self.tab_widget.tabText(self.tab_widget.currentIndex())
        self.status_label.setText(f"Ready | Brand: {self.current_brand} | Tab: {current_tab}")

    def update_brand(self, brand: str):
        """Called when brand is changed in header"""
        if brand:
            self.current_brand = brand
            self.status_label.setText(f"Brand changed to: {brand}")
            logger.info(f"Vehicle brand selected: {brand}")

            # Notify tabs that might need brand update
            for tab in self.tabs.values():
                if hasattr(tab, 'update_brand'):
                    try:
                        tab.update_brand(brand)
                    except:
                        pass

    # Quick action proxies (connected from dashboard)
    def run_quick_scan(self):
        self.tab_widget.setCurrentIndex(1)  # Diagnostics tab
        if 'diagnostics' in self.tabs:
            self.tabs['diagnostics'].quick_scan()

    def read_dtcs(self):
        self.tab_widget.setCurrentIndex(1)
        if 'diagnostics' in self.tabs:
            self.tabs['diagnostics'].read_dtcs()

    def show_live_data(self):
        self.tab_widget.setCurrentIndex(2)  # Live Data tab index

    def show_ecu_info(self):
        QMessageBox.information(self, "ECU Info", "ECU Information feature coming soon.")

    # Live stream proxies
    def start_live_stream(self):
        from shared.live_data import start_live_stream
        start_live_stream()

    def stop_live_stream(self):
        from shared.live_data import stop_live_stream
        stop_live_stream()

    def closeEvent(self, event):
        """Handle window close"""
        reply = QMessageBox.question(
            self, "Exit", "Are you sure you want to exit AutoDiag Pro?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            logger.info("Application closing - goodbye!")
            event.accept()
        else:
            event.ignore()