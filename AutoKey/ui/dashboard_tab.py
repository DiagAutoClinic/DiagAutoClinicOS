#!/usr/bin/env python3
"""
AutoKey Pro - Dashboard Tab
Separate tab implementation for easier customization
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel,
                            QPushButton, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import random

class DashboardTab:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.success_card = None
        self.keys_today_card = None
        self.system_card = None
        self.vehicles_card = None
        self.stats_layout = None
        self.quick_actions_layout = None
        self.action_buttons = []
        self.brand_info_label = None
        self.interface_info_label = None
        self.last_op_label = None

    def create_tab(self):
        """Create the dashboard tab and return the widget"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
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
        self.stats_layout = QGridLayout(stats_container)
        self.stats_layout.setSpacing(15)
        self.stats_layout.setContentsMargins(5, 5, 5, 5)

        # Create stat cards
        try:
            from shared.circular_gauge import StatCard
            self.success_card = StatCard("Success Rate", 98, 100, "%")
            self.keys_today_card = StatCard("Keys Today", 12, 50, "")
            self.system_card = StatCard("System Status", 100, 100, "%")
            self.vehicles_card = StatCard("Active Vehicles", 8, 20, "")

            # Set size policies for responsive layout
            for card in [self.success_card, self.keys_today_card, self.system_card, self.vehicles_card]:
                card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            # Add cards to grid - layout will be updated dynamically
            self.stats_layout.addWidget(self.success_card, 0, 0)
            self.stats_layout.addWidget(self.keys_today_card, 0, 1)
            self.stats_layout.addWidget(self.system_card, 1, 0)
            self.stats_layout.addWidget(self.vehicles_card, 1, 1)
        except ImportError:
            # Fallback if shared module not available
            self.success_card = QLabel("Success Rate: 98%")
            self.keys_today_card = QLabel("Keys Today: 12")
            self.system_card = QLabel("System Status: 100%")
            self.vehicles_card = QLabel("Active Vehicles: 8")

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
            ("🔑 Program New Key", "primary", self.parent.program_key),
            ("📋 Clone Key", "success", self.parent.clone_key),
            ("🔄 Reset System", "danger", self.parent.reset_system),
            ("🔍 Diagnose Keys", "primary", self.parent.diagnose_keys),
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
        self.brand_info_label = QLabel(self.parent.selected_brand)
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

        return tab, "📊 Dashboard"

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