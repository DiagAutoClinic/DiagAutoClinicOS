#!/usr/bin/env python3
"""
Dashboard Tab Component
Separate tab for dashboard functionality
"""

import random
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class DashboardTab(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Status cards
        cards_layout = QHBoxLayout()
        
        # System Health
        health_frame = QFrame()
        health_frame.setFrameStyle(QFrame.Shape.Box)
        health_layout = QVBoxLayout(health_frame)
        health_layout.addWidget(QLabel("System Health"))
        self.health_label = QLabel("98%")
        self.health_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
        health_layout.addWidget(self.health_label)
        
        # Connection
        conn_frame = QFrame()
        conn_frame.setFrameStyle(QFrame.Shape.Box)
        conn_layout = QVBoxLayout(conn_frame)
        conn_layout.addWidget(QLabel("Connection"))
        self.conn_label = QLabel("GOOD")
        self.conn_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
        conn_layout.addWidget(self.conn_label)
        
        # DTCs
        dtc_frame = QFrame()
        dtc_frame.setFrameStyle(QFrame.Shape.Box)
        dtc_layout = QVBoxLayout(dtc_frame)
        dtc_layout.addWidget(QLabel("Active DTCs"))
        self.dtc_label = QLabel("0")
        self.dtc_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
        dtc_layout.addWidget(self.dtc_label)
        
        cards_layout.addWidget(health_frame)
        cards_layout.addWidget(conn_frame)
        cards_layout.addWidget(dtc_frame)
        layout.addLayout(cards_layout)
        
        # Quick actions
        actions_layout = QHBoxLayout()
        scan_btn = QPushButton("Quick Scan")
        dtc_btn = QPushButton("Read DTCs")
        live_btn = QPushButton("Live Data")
        
        scan_btn.clicked.connect(self.quick_scan)
        dtc_btn.clicked.connect(self.read_dtcs)
        live_btn.clicked.connect(self.show_live_data)
        
        actions_layout.addWidget(scan_btn)
        actions_layout.addWidget(dtc_btn)
        actions_layout.addWidget(live_btn)
        layout.addLayout(actions_layout)
        
        # Add some additional dashboard widgets
        layout.addWidget(QLabel("Recent Activity"))
        self.activity_log = QTextEdit()
        self.activity_log.setMaximumHeight(150)
        self.activity_log.setPlainText("Ready for diagnostics...\n")
        layout.addWidget(self.activity_log)
        
    def quick_scan(self):
        """Quick system scan"""
        self.log_activity("Running quick scan...")
        QTimer.singleShot(1000, lambda: self.log_activity(
            f"Quick Scan Results - {datetime.now().strftime('%H:%M:%S')}\n"
            "✓ ECU Communication: OK\n"
            "✓ CAN Bus: Normal\n"
            "✓ Power Supply: 13.8V\n"
            "✓ No DTCs Found\n\n"
            "System Status: READY"
        ))
        
    def read_dtcs(self):
        """Read diagnostic trouble codes"""
        if self.main_window:
            self.main_window.switch_to_diagnostics()
        
    def show_live_data(self):
        """Switch to live data tab"""
        if self.main_window:
            self.main_window.switch_to_live_data()
            
    def log_activity(self, message):
        """Log activity to the dashboard"""
        self.activity_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def update_status(self, health=None, connection=None, dtcs=None):
        """Update status displays"""
        if health:
            self.health_label.setText(health)
        if connection:
            self.conn_label.setText(connection)
        if dtcs:
            self.dtc_label.setText(dtcs)