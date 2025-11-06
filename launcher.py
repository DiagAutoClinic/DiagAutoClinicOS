#!/usr/bin/env python3
"""
DiagAutoClinicOS - Modern Futuristic Launcher
Version: 3.1 - FIXED: AutoDiag button, global theme sync
"""

import sys
import os
import subprocess
import time
import random
from typing import Dict

# Add shared path
shared_path = os.path.join(os.path.dirname(__file__), 'shared')
if shared_path not in sys.path:
    sys.path.append(shared_path)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QMessageBox, QFrame, QGridLayout,
    QProgressDialog, QComboBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# === IMPORTS (FIXED) ===
try:
    from device_handler import DeviceHandler
    from style_manager import style_manager  # GLOBAL INSTANCE
    from widgets.animated_bg import NeonClinicBG
    from circular_gauge import CircularGauge, StatCard
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    # Fallbacks
    class DeviceHandler:
        def __init__(self, mock_mode=True): self.mock_mode = True
        def detect_professional_devices(self): return []

    class DummyStyleManager:
        def set_theme(self, t): print(f"Theme: {t}")
        def get_theme_names(self): return ["futuristic", "neon_clinic", "security", "dark", "light", "professional"]
    style_manager = DummyStyleManager()

    class NeonClinicBG(QWidget):
        def __init__(self, parent=None): super().__init__(parent)

    class StatCard(QFrame):
        def __init__(self, title, value):
            super().__init__()
            self.setProperty("class", "stat-card")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel(title))
            self.value_label = QLabel(str(value))
            layout.addWidget(self.value_label)
        def update_value(self, v): 
            if hasattr(self, 'value_label'):
                self.value_label.setText(str(v))

    CircularGauge = QWidget

# === CONSTANTS - FIXED PATHS ===
ALLOWED_APPS: Dict[str, str] = {
    'diag': 'AutoDiag/main.py',
    'ecu': 'AutoECU/main.py', 
    'key': 'AutoKey/main.py'
}

# === MAIN LAUNCHER ===
class ModernLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.device_handler = DeviceHandler(mock_mode=True)
        self.setup_ui()
        self.start_live_updates()

    def setup_ui(self):
        """Initialize UI with maximized window and animated background"""
        self.setWindowTitle("DiagAutoClinicOS - Where Mechanics Meet Future Intelligence")
        self.setWindowFlags(
            self.windowFlags()
            | Qt.WindowType.WindowMaximizeButtonHint
            | Qt.WindowType.WindowMinimizeButtonHint
        )
        
        # === FORCE MAXIMIZED ===
        self.showMaximized()

        # === APPLY INITIAL THEME ===
        style_manager.set_theme("neon_clinic")

        # === ANIMATED BACKGROUND ===
        self.bg = NeonClinicBG(self)
        self.bg.lower()
        self.bg.resize(self.size())

        # === SCROLL AREA ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        central = QWidget()
        scroll.setWidget(central)
        self.setCentralWidget(scroll)

        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # === SECTIONS ===
        layout.addWidget(self.create_hero_section())
        layout.addWidget(self.create_stats_dashboard())
        layout.addWidget(self.create_applications_grid())
        layout.addWidget(self.create_info_cards())
        layout.addWidget(self.create_activity_log())

    def create_hero_section(self):
        frame = QFrame()
        frame.setProperty("class", "glass-card")
        layout = QVBoxLayout(frame)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)

        title = QLabel("DiagAutoClinicOS")
        title.setProperty("class", "hero-title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))

        subtitle = QLabel("Where Mechanics Meet Future Intelligence")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 11))

        # Theme selector with ALL themes
        theme_layout = QHBoxLayout()
        theme_layout.addStretch()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(style_manager.get_theme_names())
        self.theme_combo.setCurrentText("neon_clinic")
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        self.theme_combo.setMinimumWidth(180)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(theme_layout)
        return frame

    def create_stats_dashboard(self):
        frame = QFrame()
        frame.setProperty("class", "glass-card")
        layout = QHBoxLayout(frame)
        layout.setSpacing(12)

        self.health_card = StatCard("System Health", "97%")
        self.connection_card = StatCard("Connection", "85%")
        self.coverage_card = StatCard("Coverage", "93%")
        self.sessions_card = StatCard("Sessions", "3")

        layout.addWidget(self.health_card)
        layout.addWidget(self.connection_card)
        layout.addWidget(self.coverage_card)
        layout.addWidget(self.sessions_card)
        layout.addStretch()
        return frame

    def create_applications_grid(self):
        frame = QFrame()
        frame.setProperty("class", "glass-card")
        layout = QGridLayout(frame)
        layout.setSpacing(15)

        # FIXED: Better button styling and clear labels
        diag_btn = QPushButton("🔍 AutoDiag Pro\nFull Diagnostics")
        diag_btn.setProperty("class", "primary")
        diag_btn.setMinimumHeight(80)
        diag_btn.clicked.connect(self.launch_diag)
        
        ecu_btn = QPushButton("⚙️ AutoECU Pro\nECU Programming")
        ecu_btn.setProperty("class", "success")
        ecu_btn.setMinimumHeight(80)
        ecu_btn.clicked.connect(self.launch_ecu)
        
        key_btn = QPushButton("🔑 AutoKey Pro\nKey Programming")
        key_btn.setProperty("class", "danger")
        key_btn.setMinimumHeight(80)
        key_btn.clicked.connect(self.launch_key)

        layout.addWidget(diag_btn, 0, 0)
        layout.addWidget(ecu_btn, 0, 1)
        layout.addWidget(key_btn, 0, 2)
        return frame

    def create_info_cards(self):
        frame = QFrame()
        frame.setProperty("class", "glass-card")
        layout = QHBoxLayout(frame)
        layout.setSpacing(12)

        # Hardware Card
        hardware = QFrame()
        hardware.setProperty("class", "stat-card")
        h_layout = QVBoxLayout(hardware)
        self.connection_status = QLabel("Connecting...")
        self.connection_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.connection_status.setStyleSheet("font-weight: bold;")
        scan_btn = QPushButton("Scan Hardware")
        scan_btn.clicked.connect(self.scan_hardware)
        h_layout.addWidget(self.connection_status)
        h_layout.addWidget(scan_btn)

        # Tips Card
        tips = QFrame()
        tips.setProperty("class", "stat-card")
        t_layout = QVBoxLayout(tips)
        tips_label = QLabel("Quick Tips")
        tips_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t_layout.addWidget(tips_label)
        tips_text = QTextEdit()
        tips_text.setReadOnly(True)
        tips_text.setMaximumHeight(100)
        tips_text.setHtml("""
            <ul>
                <li>Connect J2534 first</li>
                <li>Use AutoDiag for scan</li>
                <li>AutoECU for programming</li>
                <li>AutoKey for security</li>
            </ul>
        """)
        t_layout.addWidget(tips_text)

        layout.addWidget(hardware)
        layout.addWidget(tips)
        layout.addStretch()
        return frame

    def create_activity_log(self):
        frame = QFrame()
        frame.setProperty("class", "glass-card")
        layout = QVBoxLayout(frame)
        layout.setSpacing(8)

        log_label = QLabel("Activity Log")
        log_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(log_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(150)
        layout.addWidget(self.log_output)

        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self.log_output.clear)
        clear_btn.setMaximumWidth(120)
        layout.addWidget(clear_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.log_message("Welcome to DiagAutoClinicOS")
        self.log_message("System initialized")
        self.log_message("Ready for operations")
        return frame

    def scan_hardware(self):
        self.log_message("Scanning hardware...")
        progress = QProgressDialog("Scanning...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        for i in range(101):
            progress.setValue(i)
            QApplication.processEvents()
            time.sleep(0.01)
            if progress.wasCanceled(): break
        progress.close()

        devices = self.device_handler.detect_professional_devices()
        if devices:
            self.connection_status.setText(f"{len(devices)} Device(s)")
            self.log_message(f"Found {len(devices)} device(s)")
        else:
            self.connection_status.setText("No Devices")
            self.log_message("No hardware found")

    def start_live_updates(self):
        timer = QTimer(self)
        timer.timeout.connect(self.update_live_data)
        timer.start(3000)

    def update_live_data(self):
        try:
            self.health_card.update_value(f"{random.randint(90, 99)}%")
            self.connection_card.update_value(f"{random.randint(80, 95)}%")
            self.coverage_card.update_value(f"{random.randint(88, 98)}%")
            self.sessions_card.update_value(str(random.randint(1, 5)))
        except Exception as e:
            print(f"Update error: {e}")

    def log_message(self, msg):
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_output.append(f"[{ts}] {msg}")
        lines = self.log_output.toPlainText().split('\n')
        if len(lines) > 20:
            self.log_output.setPlainText('\n'.join(lines[-20:]))
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

    def change_theme(self, theme_name):
        """Change theme globally - affects launcher and will affect child apps"""
        style_manager.set_theme(theme_name)
        self.log_message(f"Theme: {theme_name}")

    def launch_diag(self): self._launch_app('diag', "AutoDiag Pro")
    def launch_ecu(self): self._launch_app('ecu', "AutoECU Pro")
    def launch_key(self): self._launch_app('key', "AutoKey Pro")

    def _launch_app(self, key, name):
        """FIXED: Proper path resolution and error handling"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        app_path = os.path.join(base_dir, ALLOWED_APPS[key])
        
        self.log_message(f"Attempting to launch {name}...")
        self.log_message(f"Path: {app_path}")
        
        if os.path.exists(app_path):
            try:
                # Launch with proper Python interpreter
                subprocess.Popen([sys.executable, app_path], cwd=os.path.dirname(app_path))
                self.log_message(f"✅ Launched {name}")
            except Exception as e:
                self.log_message(f"❌ Launch failed: {e}")
                QMessageBox.critical(self, "Launch Error", f"Failed to launch {name}:\n{e}")
        else:
            # Try alternative path structure
            alt_path = os.path.join(base_dir, '..', ALLOWED_APPS[key])
            if os.path.exists(alt_path):
                try:
                    subprocess.Popen([sys.executable, alt_path], cwd=os.path.dirname(alt_path))
                    self.log_message(f"✅ Launched {name} (alt path)")
                except Exception as e:
                    self.log_message(f"❌ Launch failed (alt): {e}")
            else:
                self.log_message(f"❌ {name} not found at {app_path} or {alt_path}")
                QMessageBox.warning(self, "Error", 
                    f"{name} not found.\n\nExpected locations:\n{app_path}\n{alt_path}\n\n"
                    f"Please verify the application is installed in the correct directory.")


    def resizeEvent(self, event):
        if hasattr(self, 'bg'):
            self.bg.resize(self.size())
        super().resizeEvent(event)

# === MAIN ===
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DiagAutoClinicOS")
    app.setApplicationVersion("3.1.0")
    launcher = ModernLauncher()
    launcher.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
