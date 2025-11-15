#!/usr/bin/env python3
"""
DiagAutoClinicOS - Modern Futuristic Launcher
Version: 3.2 - FIXED: Proper error handling, path resolution, dependencies
"""

import sys
import os
import subprocess
import time
import random
import logging
from PyQt6.QtCore import QLoggingCategory
QLoggingCategory.setFilterRules("qt.qss.parser.warning=false")  
from pathlib import Path
from typing import Dict, Optional                                                            
                               
                                
# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
                             

# Define project structure
PROJECT_ROOT = Path(__file__).parent.absolute()

# Import PyQt6 first (critical dependency)
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTextEdit, QMessageBox, QFrame, QGridLayout,
        QProgressDialog, QComboBox, QScrollArea
    )
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QFont
except ImportError as e:
    print("=" * 70)
    print("❌ CRITICAL ERROR: PyQt6 is not installed!")
    print("=" * 70)
    print(f"\nError: {e}\n")
    print("Please install required dependencies:")
    print("  pip install -r requirements.txt")
    print("\nOr install PyQt6 directly:")
    print("  pip install PyQt6>=6.6.1")
    print("=" * 70)
    sys.exit(1)

# Import shared modules (with proper error messages)
try:
    from shared.device_handler import DeviceHandler
    logger.info("✓ DeviceHandler imported successfully")


except ImportError as e:
    logger.error(f"❌ Failed to import DeviceHandler: {e}")
    print(f"\n❌ ERROR: Cannot import shared.device_handler")
    print(f"   Error: {e}")
    print("\nPlease ensure all shared modules are present.")
    sys.exit(1)

try:
    # Force reload to bypass cache
    import shared.style_manager as style_manager_module
    import importlib
    importlib.reload(style_manager_module)

    # Now safe to access
    from shared.style_manager import style_manager
    logger.info("StyleManager imported and instantiated successfully")

    # Apply default theme immediately
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyleSheet(style_manager.set_theme("neon_clinic"))

except Exception as e:
    logger.warning(f"StyleManager failed: {e}")
    # Keep your existing MinimalStyleManager fallback
    class MinimalStyleManager:
        def set_theme(self, theme):
            logger.info(f"Theme set to: {theme}")
            return ""
        def get_theme_names(self):
            return ["neon_clinic"]
    style_manager = MinimalStyleManager()
    # Create minimal fallback
    class MinimalStyleManager:
        def set_theme(self, theme):
            logger.info(f"Theme set to: {theme}")
        def get_theme_names(self):
            return ["default"]
    style_manager = MinimalStyleManager()

try:
    from shared.widgets.animated_bg import NeonClinicBG
    logger.info("✓ NeonClinicBG imported successfully")
except ImportError as e:
    logger.warning(f"⚠ Animated background not available: {e}")
    class NeonClinicBG(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)

try:
    from shared.circular_gauge import CircularGauge, StatCard
    logger.info("✓ Gauges imported successfully")
except ImportError as e:
    logger.warning(f"⚠ Circular gauges not available: {e}")
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
ALLOWED_APPS: Dict[str, dict] = {
    'diag': {
        'name': 'AutoDiag Pro',
        'path': PROJECT_ROOT / 'AutoDiag' / 'main.py',
        'icon': '🔍'
    },
    'ecu': {
        'name': 'AutoECU Pro', 
        'path': PROJECT_ROOT / 'AutoECU' / 'main.py',
        'icon': '⚙️'
    },
    'key': {
        'name': 'AutoKey Pro',
        'path': PROJECT_ROOT / 'AutoKey' / 'main.py',
        'icon': '🔑'
    }
}

# === MAIN LAUNCHER ===
class ModernLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            self.device_handler = DeviceHandler(mock_mode=False)
        except Exception as e:
            logger.warning(f"DeviceHandler initialization failed, using mock mode: {e}")
            self.device_handler = DeviceHandler(mock_mode=True)

        self.running_processes = {}  # Track running subprocesses
        self.app_buttons = {}  # Track app buttons for state management

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
        try:
            style_manager.set_theme("neon_clinic")
        except Exception as e:
            logger.warning(f"Theme application failed: {e}")

        # === ANIMATED BACKGROUND ===
        try:
            self.bg = NeonClinicBG(self)
            self.bg.lower()
            self.bg.resize(self.size())
        except Exception as e:
            logger.warning(f"Animated background failed: {e}")
            self.bg = None

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

        # Theme selector
        theme_layout = QHBoxLayout()
        theme_layout.addStretch()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        try:
            themes = style_manager.get_theme_names()
            self.theme_combo.addItems(themes)
            if "neon_clinic" in themes:
                self.theme_combo.setCurrentText("neon_clinic")
        except Exception as e:
            logger.warning(f"Theme list error: {e}")
            self.theme_combo.addItem("default")
        
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

        # FIXED: Pass numbers, not strings with %
        self.health_card = StatCard("System Health", 97, 100, "%")
        self.connection_card = StatCard("Connection", 85, 100, "%")
        self.coverage_card = StatCard("Coverage", 93, 100, "%")
        self.sessions_card = StatCard("Sessions", 3, 10, "")

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

        # Application buttons with validation
        diag_btn = self.create_app_button('diag')
        ecu_btn = self.create_app_button('ecu')
        key_btn = self.create_app_button('key')
                                                  
        
                                                                    
                                               
                                    
                                                
        
                                                                  
                                              
                                    
                                                

        layout.addWidget(diag_btn, 0, 0)
        layout.addWidget(ecu_btn, 0, 1)
        layout.addWidget(key_btn, 0, 2)
        return frame

    def create_app_button(self, app_key: str) -> QPushButton:
        """Create application launch button with path validation"""
        app_info = ALLOWED_APPS[app_key]
        icon = app_info.get('icon', '📱')
        name = app_info['name']
        path = app_info['path']

        # Check if app exists
        exists = path.exists()
        status = "✓" if exists else "✗"

        btn = QPushButton(f"{icon} {name}\n{status} Available")
        btn.setMinimumHeight(80)

        if exists:
            btn.setProperty("class", "primary" if app_key == 'diag' else
                           "success" if app_key == 'ecu' else "danger")
            btn.clicked.connect(lambda: self._launch_app(app_key, name, path))
            # Store button reference for state management
            self.app_buttons[app_key] = btn
        else:
            btn.setEnabled(False)
            btn.setToolTip(f"Not found: {path}")
            logger.warning(f"Application not found: {path}")

        return btn

    def create_info_cards(self):
        frame = QFrame()
        frame.setProperty("class", "glass-card")
        layout = QHBoxLayout(frame)
        layout.setSpacing(12)

        # Hardware Card
        hardware = QFrame()
        hardware.setProperty("class", "stat-card")
        h_layout = QVBoxLayout(hardware)
        self.connection_status = QLabel("Not Scanned")
        self.connection_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.connection_status.setStyleSheet("font-weight: bold;")
        scan_btn = QPushButton("Scan Hardware")
        scan_btn.clicked.connect(self.scan_hardware)
        h_layout.addWidget(self.connection_status)
        h_layout.addWidget(scan_btn)

        # System Info Card
        info = QFrame()
        info.setProperty("class", "stat-card")
        i_layout = QVBoxLayout(info)
        info_label = QLabel("System Info")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        i_layout.addWidget(info_label)
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(100)
        info_text.setHtml(f"""
            <ul>
                <li><b>Python:</b> {sys.version.split()[0]}</li>
                <li><b>Project:</b> {PROJECT_ROOT.name}</li>
                <li><b>Mode:</b> {'Mock' if getattr(self.device_handler, 'mock_mode', True) else 'Live'}</li>
                                             
            </ul>
        """)
        i_layout.addWidget(info_text)

        layout.addWidget(hardware)
        layout.addWidget(info)
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

        self.log_message("✓ DiagAutoClinicOS initialized")
        self.log_message(f"✓ Project root: {PROJECT_ROOT}")
        self.log_message("✓ Ready for operations")
        return frame

    def scan_hardware(self):
        """Scan for connected diagnostic hardware"""
        self.log_message("🔍 Scanning for hardware...")
        progress = QProgressDialog("Scanning for diagnostic devices...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        
        try:
            for i in range(101):
                progress.setValue(i)
                QApplication.processEvents()
                time.sleep(0.01)
                if progress.wasCanceled(): 
                    self.log_message("⚠ Scan cancelled")
                    return
            
            devices = self.device_handler.detect_professional_devices()
            
            if devices:
                self.connection_status.setText(f"✓ {len(devices)} Device(s)")
                self.log_message(f"✓ Found {len(devices)} device(s)")
                for device in devices:
                    device_name = device.get('name', 'Unknown')
                    self.log_message(f"  - {device_name}")
            else:
                self.connection_status.setText("✗ No Devices")
                self.log_message("✗ No hardware detected")
                
        except Exception as e:
            logger.error(f"Hardware scan error: {e}")
            self.connection_status.setText("✗ Scan Error")
            self.log_message(f"✗ Scan error: {e}")
        finally:
            progress.close()

    def start_live_updates(self):
        """Start periodic stats updates"""
        timer = QTimer(self)
        timer.timeout.connect(self.update_live_data)
        timer.start(3000)

        # Start process monitoring
        self.process_timer = QTimer(self)
        self.process_timer.timeout.connect(self.check_running_processes)
        self.process_timer.start(1000)  # Check every second

    def update_live_data(self):
        """Update dashboard statistics"""
        try:
            self.health_card.update_value(f"{random.randint(90, 99)}%")
            self.connection_card.update_value(f"{random.randint(80, 95)}%")
            self.coverage_card.update_value(f"{random.randint(88, 98)}%")
            # Don't update sessions randomly - it should reflect actual state
        except Exception as e:
            logger.debug(f"Stats update error: {e}")

    def check_running_processes(self):
        """Check if running processes have ended and update button states"""
        for app_key, process in list(self.running_processes.items()):
            if process.poll() is not None:  # Process has ended
                del self.running_processes[app_key]
                if app_key in self.app_buttons:
                    app_info = ALLOWED_APPS[app_key]
                    icon = app_info.get('icon', '📱')
                    name = app_info['name']
                    self.app_buttons[app_key].setEnabled(True)
                    self.app_buttons[app_key].setText(f"{icon} {name}\n✓ Available")
                    self.log_message(f"✓ {name} process ended")

    def log_message(self, msg: str):
        """Add message to activity log with timestamp"""
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_output.append(f"[{ts}] {msg}")
        
        # Keep only last 50 lines
        lines = self.log_output.toPlainText().split('\n')
        if len(lines) > 50:
            self.log_output.setPlainText('\n'.join(lines[-50:]))
        
        # Auto-scroll to bottom
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
                                       
                                                                                 
                                           
                                                

    def change_theme(self, theme_name: str):
        """Change application theme"""
        try:
            style_manager.set_theme(theme_name)
            self.log_message(f"✓ Theme changed: {theme_name}")
            logger.info(f"Theme changed to: {theme_name}")
        except Exception as e:
            self.log_message(f"✗ Theme error: {e}")
            logger.error(f"Theme change failed: {e}")

    def _launch_app(self, key: str, name: str, path: Path):
        """Launch application subprocess with proper error handling"""
        # Check if app is already running
        if key in self.running_processes and self.running_processes[key].poll() is None:
            self.log_message(f"⚠ {name} is already running")
            QMessageBox.information(self, "Already Running", f"{name} is already running.")
            return

        self.log_message(f"🚀 Launching {name}...")
        logger.info(f"Launching {name} from {path}")

        if not path.exists():
            error_msg = f"Application not found: {path}"
            self.log_message(f"✗ {error_msg}")
            logger.error(error_msg)
            QMessageBox.critical(self, "Launch Error", error_msg)
            return

        try:
            # Launch as subprocess with proper PYTHONPATH
            working_dir = path.parent
            env = os.environ.copy()
            env['PYTHONPATH'] = str(PROJECT_ROOT)
            process = subprocess.Popen(
                [sys.executable, str(path)],
                cwd=str(working_dir),
                env=env
            )

            # Store process reference and disable button
            self.running_processes[key] = process
            if key in self.app_buttons:
                app_info = ALLOWED_APPS[key]
                icon = app_info.get('icon', '📱')
                self.app_buttons[key].setEnabled(False)
                self.app_buttons[key].setText(f"{icon} {name}\n✓ Running")

            self.log_message(f"✓ {name} launched (PID: {process.pid})")
            logger.info(f"{name} launched successfully with PID {process.pid}")

            # Update session count
            current = int(self.sessions_card.value_label.text())
            self.sessions_card.update_value(str(current + 1))

        except Exception as e:
            error_msg = f"Failed to launch {name}: {e}"

            self.log_message(f"✗ {error_msg}")
            logger.error(error_msg)
            QMessageBox.critical(
                self,
                "Launch Error",
                f"Failed to launch {name}:\n\n{e}\n\nPath: {path}"
            )

    def resizeEvent(self, event):
        """Handle window resize"""
        if hasattr(self, 'bg') and self.bg:
            self.bg.resize(self.size())
        super().resizeEvent(event)

# === MAIN ===
def main():
    """Application entry point"""
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("DiagAutoClinicOS")
        app.setApplicationVersion("3.2.0")
        app.setOrganizationName("DiagAutoClinic")
        app.setOrganizationDomain("diagautoclinic.co.za")
        
        logger.info("=" * 70)
        logger.info("DiagAutoClinicOS Launcher v3.2.0")
        logger.info(f"Project Root: {PROJECT_ROOT}")
        logger.info("=" * 70)
        
        launcher = ModernLauncher()
        launcher.show()
        
        sys.exit(app.exec())
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        print("\n" + "=" * 70)
        print("❌ FATAL ERROR")
        print("=" * 70)
        print(f"\n{e}\n")
        print("Please check the log for details.")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()
