#!/usr/bin/env python3
"""
AutoECU - Dashboard Tab
Separate tab implementation for easier customization
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
                            QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# Import color function
try:
    from shared.themes.dacos_theme import get_dacos_color
except ImportError:
    # Fallback color function
    def get_dacos_color(color_name):
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
        return DACOS_THEME.get(color_name, DACOS_THEME['accent'])

class DashboardTab:
    """
    Dashboard Tab with comprehensive ECU statistics and quick actions.
    """

    def __init__(self, parent_window):
        """
        Initialize the Dashboard Tab.

        Args:
            parent_window: The main application window instance
        """
        self.parent = parent_window
        self.stats_grid = None
        self.ecu_health_card = None
        self.programming_card = None
        self.modules_card = None
        self.quick_actions_layout = None
        self.scan_btn = None
        self.ready_btn = None
        self.immo_btn = None
        self.egr_btn = None
        self.file_btn = None
        self.dtc_btn = None
        self.brand_info_label = None
        self.conn_info_label = None
        self.last_op_label = None

    def create_tab(self) -> tuple[QWidget, str]:
        """
        Create the dashboard tab and return the widget.

        Returns:
            tuple: (tab_widget, tab_title)
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
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
        try:
            from shared.circular_gauge import StatCard
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
        except ImportError:
            # Fallback if shared module not available
            self.ecu_health_card = QLabel("ECU Health: 96%")
            self.programming_card = QLabel("Last Program: 100%")
            self.modules_card = QLabel("ECU Modules: 12")
            self.stats_grid.addWidget(self.ecu_health_card)
            self.stats_grid.addWidget(self.programming_card)
            self.stats_grid.addWidget(self.modules_card)

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

        # Connect signals
        self.scan_btn.clicked.connect(self.parent.scan_ecus)
        self.ready_btn.clicked.connect(self.parent.check_start_ready)
        self.immo_btn.clicked.connect(self.parent.perform_immo_off)
        self.egr_btn.clicked.connect(self.parent.perform_egr_dpf_removal)
        self.file_btn.clicked.connect(self.parent.import_start_ready_file)
        self.dtc_btn.clicked.connect(self.parent.add_start_ready_dtc)

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
        self.brand_info_label = QLabel(self.parent.selected_brand)
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

        return tab, "Dashboard"

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