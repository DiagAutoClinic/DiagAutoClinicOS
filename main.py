#!/usr/bin/env python3
"""
AutoDiag Main Application - Modular Tab Architecture
Each tab is now a separate, editable component
"""

import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# Import all separate tab components
from ui.dashboard_tab import DashboardTab
from ui.diagnostics_tab import DiagnosticsTab
from ui.live_data_tab import LiveDataTab
from ui.special_functions_tab import SpecialFunctionsTab
from ui.calibrations_tab import CalibrationsTab
from ui.security_tab import SecurityTab
from ui.vehicle_info_tab import VehicleInfoTab

class AutoDiagMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoDiag Pro - Modular Edition")
        self.setGeometry(100, 100, 1400, 800)
        
        # Initialize tab instances
        self.dashboard_tab = None
        self.diagnostics_tab = None
        self.live_data_tab = None
        self.special_functions_tab = None
        self.calibrations_tab = None
        self.security_tab = None
        self.vehicle_info_tab = None
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Application header
        header = QLabel("AutoDiag Pro - Modular Diagnostic System")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: white; 
            padding: 15px; 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                       stop:0 #0078d4, stop:1 #005a9e);
            border-radius: 8px;
            margin-bottom: 10px;
        """)
        layout.addWidget(header)
        
        # Vehicle selection
        vehicle_layout = QHBoxLayout()
        vehicle_layout.addWidget(QLabel("Vehicle:"))
        self.vehicle_combo = QComboBox()
        self.vehicle_combo.addItems([
            "Chevrolet Cruze 2014",
            "Toyota Camry 2020", 
            "Honda Civic 2019",
            "Ford F-150 2018",
            "BMW 3 Series 2021",
            "VW Golf 2020"
        ])
        vehicle_layout.addWidget(self.vehicle_combo)
        
        # Connection status
        self.connection_label = QLabel("● Connected")
        self.connection_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        vehicle_layout.addWidget(QLabel("Status:"))
        vehicle_layout.addWidget(self.connection_label)
        
        vehicle_layout.addStretch()
        layout.addLayout(vehicle_layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Initialize all tabs
        self.setup_tabs()
        
        # Status bar
        self.statusBar().showMessage("Ready for diagnostics...")
        
    def setup_tabs(self):
        """Initialize all tab components"""
        
        # Dashboard Tab
        self.dashboard_tab = DashboardTab(self)
        self.tab_widget.addTab(self.dashboard_tab, "📊 Dashboard")
        
        # Diagnostics Tab
        self.diagnostics_tab = DiagnosticsTab(self)
        self.tab_widget.addTab(self.diagnostics_tab, "🔧 Diagnostics")
        
        # Live Data Tab
        self.live_data_tab = LiveDataTab(self)
        self.tab_widget.addTab(self.live_data_tab, "📈 Live Data")
        
        # Special Functions Tab
        self.special_functions_tab = SpecialFunctionsTab(self)
        self.tab_widget.addTab(self.special_functions_tab, "⚙️ Special Functions")
        
        # Calibrations Tab
        self.calibrations_tab = CalibrationsTab(self)
        self.tab_widget.addTab(self.calibrations_tab, "🎛️ Calibrations")
        
        # Security Tab
        self.security_tab = SecurityTab(self)
        self.tab_widget.addTab(self.security_tab, "🔒 Security")
        
        # Vehicle Info Tab
        self.vehicle_info_tab = VehicleInfoTab(self)
        self.tab_widget.addTab(self.vehicle_info_tab, "🚗 Vehicle Info")
        
        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
    def on_tab_changed(self, index):
        """Handle tab change events"""
        tab_names = [
            "Dashboard", "Diagnostics", "Live Data", "Special Functions",
            "Calibrations", "Security", "Vehicle Info"
        ]
        
        if 0 <= index < len(tab_names):
            self.statusBar().showMessage(f"Switched to {tab_names[index]} tab")
            
            # Update dashboard if switching to diagnostics
            if tab_names[index] == "Diagnostics" and self.dashboard_tab:
                self.dashboard_tab.update_status(connection="ACTIVE", dtcs="1")
                
    # Navigation methods for tab switching
    def switch_to_diagnostics(self):
        """Switch to diagnostics tab"""
        self.tab_widget.setCurrentIndex(1)
        
    def switch_to_live_data(self):
        """Switch to live data tab"""
        self.tab_widget.setCurrentIndex(2)
        
    def switch_to_special_functions(self):
        """Switch to special functions tab"""
        self.tab_widget.setCurrentIndex(3)
        
    def switch_to_calibrations(self):
        """Switch to calibrations tab"""
        self.tab_widget.setCurrentIndex(4)
        
    def switch_to_security(self):
        """Switch to security tab"""
        self.tab_widget.setCurrentIndex(5)
        
    def switch_to_vehicle_info(self):
        """Switch to vehicle info tab"""
        self.tab_widget.setCurrentIndex(6)
        
    def switch_to_dashboard(self):
        """Switch to dashboard tab"""
        self.tab_widget.setCurrentIndex(0)
        
    def update_connection_status(self, status, color="green"):
        """Update connection status across all tabs"""
        self.connection_label.setText(f"● {status}")
        self.connection_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        # Update dashboard if it exists
        if self.dashboard_tab:
            connection_text = "GOOD" if status == "Connected" else "DISCONNECTED"
            connection_color = "#4CAF50" if status == "Connected" else "#F44336"
            self.dashboard_tab.conn_label.setText(connection_text)
            self.dashboard_tab.conn_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {connection_color};")
            
    def closeEvent(self, event):
        """Handle application close"""
        reply = QMessageBox.question(self, 'Exit AutoDiag', 
                                   'Are you sure you want to exit?',
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Stop any live data streams
            if self.live_data_tab:
                self.live_data_tab.stop_stream()
            event.accept()
        else:
            event.ignore()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("AutoDiag Pro")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("AutoDiag Systems")
    
    # Apply global style
    app.setStyleSheet("""
        QMainWindow { 
            background-color: #2b2b2b; 
            color: white; 
        }
        QTabWidget::pane { 
            border: 1px solid #555; 
            background: #3a3a3a; 
        }
        QTabBar::tab { 
            background: #4a4a4a; 
            color: white; 
            padding: 8px 16px; 
            margin: 2px; 
            border-radius: 4px;
        }
        QTabBar::tab:selected { 
            background: #0078d4; 
        }
        QTabBar::tab:hover {
            background: #5a5a5a;
        }
        QPushButton { 
            background: #0078d4; 
            color: white; 
            border: none; 
            padding: 8px 16px; 
            border-radius: 4px; 
            font-weight: bold;
        }
        QPushButton:hover { 
            background: #106ebe; 
        }
        QPushButton:pressed {
            background: #005a9e;
        }
        QTextEdit { 
            background: #1e1e1e; 
            color: white; 
            border: 1px solid #555; 
            border-radius: 4px;
        }
        QTableWidget { 
            background: #1e1e1e; 
            color: white; 
            border: 1px solid #555; 
            border-radius: 4px;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #555;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QSpinBox, QDoubleSpinBox {
            background: #1e1e1e;
            color: white;
            border: 1px solid #555;
            border-radius: 3px;
            padding: 4px;
        }
        QLineEdit {
            background: #1e1e1e;
            color: white;
            border: 1px solid #555;
            border-radius: 3px;
            padding: 4px;
        }
    """)
    
    # Create and show main window
    window = AutoDiagMainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()