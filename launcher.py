#!/usr/bin/env python3
"""
DiagAutoClinicOS - MODERN FUTURISTIC Launcher
Version: 3.0 - Glassmorphic Design
"""

import sys
import os
import subprocess
import time
import random
from pathlib import Path
from typing import List, Dict

# Add shared directory to path
shared_path = os.path.join(os.path.dirname(__file__), 'shared')
if shared_path not in sys.path:
    sys.path.append(shared_path)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QMessageBox, QFrame, QGridLayout,
    QProgressDialog, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon

try:
    from device_handler import DeviceHandler
    from style_manager import StyleManager
    # Import circular gauge if in same directory
    try:
        from circular_gauge import CircularGauge, StatCard
    except ImportError:
        # Fallback: Create simple placeholders
        class CircularGauge(QWidget):
            def __init__(self, *args, **kwargs):
                super().__init__()
                self.setMinimumSize(150, 150)
        class StatCard(QFrame):
            def __init__(self, title, value, *args, **kwargs):
                super().__init__()
                self.setProperty("class", "stat-card")
                layout = QVBoxLayout(self)
                layout.addWidget(QLabel(f"{title}\n{value}"))
            def update_value(self, value):
                pass
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    class DeviceHandler:
        def __init__(self, mock_mode=True):
            self.mock_mode = True
            self.is_connected = False
        def detect_professional_devices(self):
            return []
    class StyleManager:
        def __init__(self):
            self.current_theme = "futuristic"
        def set_theme(self, theme):
            pass
        def get_theme_names(self):
            return ["futuristic", "dark", "security"]

ALLOWED_APPS: Dict[str, str] = {
    'diag': 'AutoDiag/main.py',
    'ecu': 'AutoECU/main.py',
    'key': 'AutoKey/main.py'
}

class ModernLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.device_handler = DeviceHandler(mock_mode=True)
        self.style_manager = StyleManager()
        self.setup_ui()
        self.start_live_updates()
        
    def setup_ui(self):
        """Initialize modern futuristic UI"""
        self.setWindowTitle("DiagAutoClinicOS - Where Mechanics Meet Future Intelligence")
        self.setGeometry(50, 50, 1600, 1000)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        
        # Apply futuristic theme
        self.style_manager.set_theme("futuristic")
        
        # Central widget with scrollable content
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Hero Section
        hero_section = self.create_hero_section()
        main_layout.addWidget(hero_section)
        
        # Stats Dashboard
        stats_section = self.create_stats_dashboard()
        main_layout.addWidget(stats_section)
        
        # Applications Grid
        apps_section = self.create_applications_grid()
        main_layout.addWidget(apps_section)
        
        # Quick Info Cards
        info_section = self.create_info_cards()
        main_layout.addWidget(info_section)
        
        # Activity Log
        log_section = self.create_activity_log()
        main_layout.addWidget(log_section)
        
    def create_hero_section(self):
        """Create modern hero section with gradient"""
        hero_frame = QFrame()
        hero_frame.setProperty("class", "glass-card")
        hero_frame.setMinimumHeight(180)
        hero_frame.setMaximumHeight(200)
        
        layout = QVBoxLayout(hero_frame)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title with glow effect
        title = QLabel("DiagAutoClinicOS")
        title.setProperty("class", "hero-title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtitle
        subtitle = QLabel("Where Mechanics Meet Future Intelligence")
        subtitle.setProperty("class", "hero-subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Theme selector
        theme_layout = QHBoxLayout()
        theme_label = QLabel("🎨 Theme:")
        theme_label.setStyleSheet("color: #5eead4; font-size: 11pt;")
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self.style_manager.get_theme_names())
        self.theme_combo.setCurrentText("futuristic")
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        self.theme_combo.setMinimumWidth(150)
        
        theme_layout.addStretch()
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(10)
        layout.addLayout(theme_layout)
        
        return hero_frame
        
    def create_stats_dashboard(self):
        """Create stats dashboard with circular gauges"""
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(20)
        
        # System Health
        self.health_card = StatCard("System Health", 97, 100, "%")
        
        # Connection Quality
        self.connection_card = StatCard("Connection Quality", 85, 100, "%")
        
        # Diagnostic Coverage
        self.coverage_card = StatCard("Diagnostic Coverage", 93, 100, "%")
        
        # Active Sessions
        self.sessions_card = StatCard("Active Sessions", 3, 10, "")
        
        stats_layout.addWidget(self.health_card)
        stats_layout.addWidget(self.connection_card)
        stats_layout.addWidget(self.coverage_card)
        stats_layout.addWidget(self.sessions_card)
        stats_layout.addStretch()
        
        return stats_frame
        
    def create_applications_grid(self):
        """Create modern application cards in bento-box layout"""
        apps_frame = QFrame()
        apps_layout = QGridLayout(apps_frame)
        apps_layout.setSpacing(20)
        
        # Section title
        title_label = QLabel("🚀 Professional Diagnostic Applications")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #14b8a6; margin: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        apps_layout.addWidget(title_label, 0, 0, 1, 3)
        
        # AutoDiag Card (Large)
        diag_card = self.create_modern_app_card(
            "🔍",
            "AutoDiag Pro",
            "Vehicle Diagnostics",
            "Professional DTC scanning, live data monitoring, and comprehensive system analysis",
            self.launch_diag,
            "#14b8a6"
        )
        apps_layout.addWidget(diag_card, 1, 0, 2, 1)
        
        # AutoECU Card (Medium)
        ecu_card = self.create_modern_app_card(
            "⚙️",
            "AutoECU Pro",
            "ECU Programming",
            "Advanced ECU reading, writing, coding, and module programming",
            self.launch_ecu,
            "#10b981"
        )
        apps_layout.addWidget(ecu_card, 1, 1, 1, 1)
        
        # AutoKey Card (Medium)
        key_card = self.create_modern_app_card(
            "🔒",
            "AutoKey Pro",
            "Security Systems",
            "Key programming, immobilizer access, and security management",
            self.launch_key,
            "#ef4444"
        )
        apps_layout.addWidget(key_card, 1, 2, 1, 1)
        
        # Hardware Status Card
        hardware_card = self.create_hardware_status_card()
        apps_layout.addWidget(hardware_card, 2, 1, 1, 2)
        
        return apps_frame
        
    def create_modern_app_card(self, emoji, title, subtitle, description, handler, accent_color):
        """Create glassmorphic application card"""
        card = QFrame()
        card.setProperty("class", "app-card")
        card.setMinimumHeight(200)
        card.setMaximumHeight(280)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        emoji_label = QLabel(emoji)
        emoji_label.setStyleSheet("font-size: 40px;")
        
        title_layout = QVBoxLayout()
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {accent_color};")
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("color: #5eead4; font-size: 11pt;")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        header_layout.addWidget(emoji_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #a0d4cc; font-size: 10pt; line-height: 1.5;")
        
        # Launch button
        launch_btn = QPushButton("Launch Application")
        launch_btn.setProperty("class", "primary")
        launch_btn.setMinimumHeight(45)
        launch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        launch_btn.clicked.connect(handler)
        
        layout.addLayout(header_layout)
        layout.addWidget(desc_label)
        layout.addStretch()
        layout.addWidget(launch_btn)
        
        return card
        
    def create_hardware_status_card(self):
        """Create hardware status card"""
        card = QFrame()
        card.setProperty("class", "glass-card")
        card.setMinimumHeight(200)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("🔌 Hardware Status")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #14b8a6;")
        
        # Connection indicator
        self.connection_indicator = QLabel("●")
        self.connection_indicator.setStyleSheet("color: #ef4444; font-size: 32px;")
        self.connection_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.connection_status = QLabel("No Hardware Connected")
        self.connection_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.connection_status.setStyleSheet("color: #a0d4cc; font-size: 11pt;")
        
        # Scan button
        scan_btn = QPushButton("🔍 Scan for Hardware")
        scan_btn.setProperty("class", "primary")
        scan_btn.clicked.connect(self.scan_hardware)
        scan_btn.setMinimumHeight(40)
        
        layout.addWidget(title)
        layout.addWidget(self.connection_indicator)
        layout.addWidget(self.connection_status)
        layout.addStretch()
        layout.addWidget(scan_btn)
        
        return card
        
    def create_info_cards(self):
        """Create quick info cards"""
        info_frame = QFrame()
        info_layout = QHBoxLayout(info_frame)
        info_layout.setSpacing(15)
        
        # Supported Brands
        brands_card = self.create_info_card(
            "🏭", "Supported Brands", "25+", "Global Coverage"
        )
        
        # Diagnostic Functions
        functions_card = self.create_info_card(
            "🔧", "Special Functions", "150+", "Brand Specific"
        )
        
        # Security Level
        security_card = self.create_info_card(
            "🔒", "Security Level", "DEALER", "Full Access"
        )
        
        info_layout.addWidget(brands_card)
        info_layout.addWidget(functions_card)
        info_layout.addWidget(security_card)
        info_layout.addStretch()
        
        return info_frame
        
    def create_info_card(self, emoji, title, value, subtitle):
        """Create small info card"""
        card = QFrame()
        card.setProperty("class", "stat-card")
        card.setMinimumSize(200, 120)
        card.setMaximumSize(300, 140)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        layout.setContentsMargins(15, 15, 15, 15)
        
        emoji_label = QLabel(emoji)
        emoji_label.setStyleSheet("font-size: 28px;")
        emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #5eead4; font-size: 10pt;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setProperty("class", "stat-value")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("color: #a0d4cc; font-size: 9pt;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(emoji_label)
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(subtitle_label)
        
        return card
        
    def create_activity_log(self):
        """Create activity log section"""
        log_frame = QFrame()
        log_frame.setProperty("class", "glass-card")
        log_frame.setMaximumHeight(150)
        
        layout = QVBoxLayout(log_frame)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("📊 Activity Log")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #14b8a6;")
        
        # Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(80)
        
        # Clear button
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self.log_output.clear)
        clear_btn.setMaximumWidth(120)
        
        layout.addWidget(title)
        layout.addWidget(self.log_output)
        layout.addWidget(clear_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.log_message("✨ Welcome to DiagAutoClinicOS - Futuristic Edition")
        self.log_message("🚀 System initialized successfully")
        
        return log_frame
        
    def scan_hardware(self):
        """Scan for professional hardware"""
        self.log_message("🔍 Scanning for professional diagnostic hardware...")
        
        progress = QProgressDialog("Scanning for hardware...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        for i in range(101):
            progress.setValue(i)
            QApplication.processEvents()
            if progress.wasCanceled():
                break
            time.sleep(0.01)
        
        progress.close()
        
        devices = self.device_handler.detect_professional_devices()
        if devices:
            self.connection_indicator.setStyleSheet("color: #10b981; font-size: 32px;")
            self.connection_status.setText(f"✅ {len(devices)} Device(s) Found")
            self.log_message(f"✅ Found {len(devices)} professional device(s)")
        else:
            self.log_message("⚠️ No hardware detected - using mock mode")
            
    def start_live_updates(self):
        """Start live data updates for gauges"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_live_data)
        self.update_timer.start(3000)  # Update every 3 seconds
        
    def update_live_data(self):
        """Update live data in gauges"""
        # Simulate live data changes
        self.health_card.update_value(random.randint(90, 99))
        self.connection_card.update_value(random.randint(80, 95))
        self.coverage_card.update_value(random.randint(88, 98))
        self.sessions_card.update_value(random.randint(1, 5))
        
    def log_message(self, message):
        """Add message to activity log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_output.append(f"[{timestamp}] {message}")
        
    def change_theme(self, theme_name):
        """Change application theme"""
        self.style_manager.set_theme(theme_name)
        self.log_message(f"🎨 Theme changed to: {theme_name}")
        
    def launch_diag(self):
        """Launch AutoDiag Pro"""
        try:
            diag_path = os.path.join(os.path.dirname(__file__), ALLOWED_APPS['diag'])
            if os.path.exists(diag_path):
                subprocess.Popen([sys.executable, diag_path], shell=False)
                self.log_message("🚀 Launched AutoDiag Pro")
            else:
                QMessageBox.warning(self, "Not Found", "AutoDiag Pro not found")
        except Exception as e:
            self.log_message(f"❌ Failed to launch: {e}")
            
    def launch_ecu(self):
        """Launch AutoECU Pro"""
        try:
            ecu_path = os.path.join(os.path.dirname(__file__), ALLOWED_APPS['ecu'])
            if os.path.exists(ecu_path):
                subprocess.Popen([sys.executable, ecu_path], shell=False)
                self.log_message("🚀 Launched AutoECU Pro")
            else:
                QMessageBox.warning(self, "Not Found", "AutoECU Pro not found")
        except Exception as e:
            self.log_message(f"❌ Failed to launch: {e}")
            
    def launch_key(self):
        """Launch AutoKey Pro"""
        try:
            key_path = os.path.join(os.path.dirname(__file__), ALLOWED_APPS['key'])
            if os.path.exists(key_path):
                subprocess.Popen([sys.executable, key_path], shell=False)
                self.log_message("🚀 Launched AutoKey Pro")
            else:
                QMessageBox.warning(self, "Not Found", "AutoKey Pro not found")
        except Exception as e:
            self.log_message(f"❌ Failed to launch: {e}")

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    app.setApplicationName("DiagAutoClinicOS Futuristic")
    app.setApplicationVersion("3.0.0")
    app.setOrganizationName("AutoClinic Pro")
    
    launcher = ModernLauncher()
    launcher.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
