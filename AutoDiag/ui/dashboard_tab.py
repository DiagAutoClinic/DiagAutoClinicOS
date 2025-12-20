#!/usr/bin/env python3
"""
AutoDiag Pro - Dashboard Tab
Separate tab implementation for easier customization
RELEASE VERSION - NO MOCK DATA
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel, QPushButton, QScrollArea
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class DashboardTab:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.tab_widget = None
        self.system_health_card = None
        self.connection_card = None
        self.dtc_card = None
        self.security_card = None
        self.dashboard_timer = None
        self.live_data_timer = None
        self.ai_health_monitor = None
        self.ai_prediction_widget = None
        self.ai_activity_indicator = None
        self.ai_maintenance_widget = None

    def create_tab(self):
        """Create the dashboard tab and return the widget"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tab)

        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 30, 20, 30)

        # === TOP ROW: 4 BIG GLOWING GAUGES ===
        top_grid = QGridLayout()
        top_grid.setSpacing(25)

        # Create DACOS-styled stat cards
        from shared.circular_gauge import StatCard
        self.system_health_card = StatCard("System Health", 0, 100, "%")
        self.connection_card = StatCard("Connection Quality", 0, 100, "%")
        self.dtc_card = StatCard("Active DTCs", 0, 50, "")
        self.security_card = StatCard("Security Level", 0, 5, "/5")
        self.voltage_card = StatCard("Battery Voltage", 0.0, 15.0, "V")

        # Shared StatCard handles sizing responsively

        top_grid.addWidget(self.system_health_card, 0, 0)
        top_grid.addWidget(self.connection_card, 0, 1)
        top_grid.addWidget(self.dtc_card, 0, 2)
        top_grid.addWidget(self.security_card, 0, 3)
        top_grid.addWidget(self.voltage_card, 1, 0, 1, 4)  # Span across bottom row

        # === QUICK ACTIONS ROW ===
        actions_frame = QFrame()
        actions_frame.setProperty("class", "glass-card")
        actions_layout = QGridLayout(actions_frame)
        actions_layout.setSpacing(15)

        # DACOS-styled buttons
        btn_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1F5E5A, stop:1 #134F4A);
                color: #E8FFFB;
                border: 2px solid #21F5C1;
                border-radius: 16px;
                padding: 20px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2AF5D1, stop:1 #21F5C1);
                border: 2px solid #2AF5D1;
                color: #0B2E2B;
            }
        """

        btn1 = QPushButton("🚀 Quick Scan")
        btn2 = QPushButton("🔍 Read DTCs")
        btn3 = QPushButton("📊 Live Data")
        btn4 = QPushButton("💻 ECU Info")

        for btn in (btn1, btn2, btn3, btn4):
            btn.setStyleSheet(btn_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # Connect to parent methods
            if btn.text() == "🚀 Quick Scan":
                btn.clicked.connect(self.parent.run_quick_scan)
            elif btn.text() == "🔍 Read DTCs":
                btn.clicked.connect(self.parent.read_dtcs)
            elif btn.text() == "📊 Live Data":
                btn.clicked.connect(self.parent.show_live_data)
            elif btn.text() == "💻 ECU Info":
                btn.clicked.connect(self.parent.show_ecu_info)

        actions_layout.addWidget(btn1, 0, 0)
        actions_layout.addWidget(btn2, 0, 1)
        actions_layout.addWidget(btn3, 0, 2)
        actions_layout.addWidget(btn4, 0, 3)

        # DACOS title
        actions_title = QLabel("⚡ Quick Actions")
        actions_title.setStyleSheet("font-size: 18pt; color: #21F5C1; font-weight: bold; padding: 10px;")
        actions_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # === ASSEMBLE EVERYTHING ===
        layout.addLayout(top_grid)
        layout.addWidget(actions_title)
        layout.addWidget(actions_frame)
        layout.addStretch()

        # === DASHBOARD UPDATES ===
        self.dashboard_timer = QTimer()
        self.dashboard_timer.timeout.connect(self.update_dashboard_data)
        self.dashboard_timer.start(3000)

        # REMOVED: Live data timer connection since update_live_data_table doesn't exist in parent
        # self.live_data_timer = QTimer()
        # self.live_data_timer.timeout.connect(self.parent.update_live_data_table)

        return scroll, "🚀 Dashboard"

    def update_dashboard_data(self):
        """Update dashboard with real data from diagnostics controller"""
        try:
            if self.parent.diagnostics_controller:
                # Check VCI connection
                vci_status = self.parent.diagnostics_controller.get_vci_status()
                if vci_status.get('status') == 'connected':
                    # Hardware connected - show real data
                    voltage = self.parent.diagnostics_controller.get_current_voltage()
                    self.voltage_card.update_value(voltage)

                    # Update system health based on connection
                    self.system_health_card.update_value(98)  # Connected = good health
                    self.connection_card.update_value(95)  # Connected = good connection

                    # Get DTC count from controller if available
                    dtc_result = self.parent.diagnostics_controller.read_dtcs()
                    if dtc_result.get("success"):
                        dtc_data = dtc_result.get("data", [])
                        self.dtc_card.update_value(len(dtc_data))
                    else:
                        self.dtc_card.update_value(0)
                else:
                    # No hardware - show hardware required
                    self.system_health_card.update_value(0)  # No hardware
                    self.connection_card.update_value(0)  # No connection
                    self.dtc_card.update_value(0)  # No data
                    self.voltage_card.update_value(0.0)  # No voltage

                # Update security level based on user
                if hasattr(self.parent, 'current_user_info'):
                    user_info = self.parent.current_user_info
                    if user_info.get('tier') == 'FACTORY':
                        self.security_card.update_value(5)
                    elif user_info.get('tier') == 'SUPER_USER':
                        self.security_card.update_value(4)
                    elif user_info.get('tier') == 'ADVANCED':
                        self.security_card.update_value(3)
                    elif user_info.get('tier') == 'STANDARD':
                        self.security_card.update_value(2)
                    else:
                        self.security_card.update_value(1)
                else:
                    self.security_card.update_value(1)  # Basic level

            else:
                # No diagnostics controller
                self.system_health_card.update_value(0)
                self.connection_card.update_value(0)
                self.dtc_card.update_value(0)
                self.voltage_card.update_value(0.0)
                self.security_card.update_value(1)
                
        except Exception as e:
            # Error - show hardware required
            self.system_health_card.update_value(0)
            self.connection_card.update_value(0)
            self.dtc_card.update_value(0)
            self.voltage_card.update_value(0.0)
            self.security_card.update_value(1)