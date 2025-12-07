#!/usr/bin/env python3
"""
AutoDiag Pro - Diagnostics Tab with BIGGER FRAMES and SCROLL AREAS
Separate tab implementation for easier customization
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, 
    QPushButton, QTextEdit, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class DiagnosticsTab:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.scan_btn = None
        self.dtc_btn = None
        self.clear_btn = None
        self.results_text = None
        self.vci_status_label = None
        self.vci_connect_btn = None
        self.vci_disconnect_btn = None
        self.vci_scan_btn = None

    def create_tab(self):
        """Create the diagnostics tab with enhanced layout and scroll areas"""
        tab = QWidget()
        
        # Create scroll area for entire tab
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Content widget inside scroll area
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 12, 15, 12)

        # ----------------------------------------------------------
        # HEADER - BIGGER
        # ----------------------------------------------------------
        header = QLabel("🔧 Advanced Diagnostics")
        header.setProperty("class", "tab-title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFixedHeight(50)
        font = header.font()
        font.setPointSize(14)
        header.setFont(font)
        layout.addWidget(header)

        # ----------------------------------------------------------
        # VCI STATUS SECTION - BIGGER
        # ----------------------------------------------------------
        vci_frame = QFrame()
        vci_frame.setProperty("class", "glass-card")
        vci_frame.setMinimumHeight(250)
        vci_layout = QVBoxLayout(vci_frame)
        vci_layout.setSpacing(12)
        vci_layout.setContentsMargins(20, 15, 20, 15)

        vci_title = QLabel("🔌 VCI Interface")
        vci_title.setProperty("class", "section-title")
        vci_title.setFixedHeight(32)
        font = vci_title.font()
        font.setPointSize(12)
        font.setBold(True)
        vci_title.setFont(font)
        vci_layout.addWidget(vci_title)

        # VCI status display
        self.vci_status_label = QLabel("🔌 VCI Status: Not Connected")
        self.vci_status_label.setProperty("class", "section-label")
        self.vci_status_label.setFixedHeight(30)
        font = self.vci_status_label.font()
        font.setPointSize(11)
        self.vci_status_label.setFont(font)
        vci_layout.addWidget(self.vci_status_label)

        # VCI control buttons
        vci_buttons_layout = QHBoxLayout()
        vci_buttons_layout.setSpacing(15)

        self.vci_scan_btn = QPushButton("🔍 Scan for VCI")
        self.vci_scan_btn.setProperty("class", "primary")
        self.vci_scan_btn.setFixedHeight(45)
        self.vci_scan_btn.setMinimumWidth(150)
        self.vci_scan_btn.clicked.connect(self.scan_for_vci)
        font = self.vci_scan_btn.font()
        font.setPointSize(10)
        font.setBold(True)
        self.vci_scan_btn.setFont(font)

        self.vci_connect_btn = QPushButton("🔌 Connect VCI")
        self.vci_connect_btn.setProperty("class", "success")
        self.vci_connect_btn.setFixedHeight(45)
        self.vci_connect_btn.setMinimumWidth(150)
        self.vci_connect_btn.clicked.connect(self.connect_vci)
        self.vci_connect_btn.setEnabled(False)
        font = self.vci_connect_btn.font()
        font.setPointSize(10)
        font.setBold(True)
        self.vci_connect_btn.setFont(font)

        self.vci_disconnect_btn = QPushButton("🔌 Disconnect VCI")
        self.vci_disconnect_btn.setProperty("class", "warning")
        self.vci_disconnect_btn.setFixedHeight(45)
        self.vci_disconnect_btn.setMinimumWidth(160)
        self.vci_disconnect_btn.clicked.connect(self.disconnect_vci)
        self.vci_disconnect_btn.setEnabled(False)
        font = self.vci_disconnect_btn.font()
        font.setPointSize(10)
        font.setBold(True)
        self.vci_disconnect_btn.setFont(font)

        vci_buttons_layout.addWidget(self.vci_scan_btn)
        vci_buttons_layout.addWidget(self.vci_connect_btn)
        vci_buttons_layout.addWidget(self.vci_disconnect_btn)
        vci_buttons_layout.addStretch()

        vci_layout.addLayout(vci_buttons_layout)
        layout.addWidget(vci_frame)

        # ----------------------------------------------------------
        # CONTROL PANEL - BIGGER
        # ----------------------------------------------------------
        control_frame = QFrame()
        control_frame.setProperty("class", "glass-card")
        control_frame.setMinimumHeight(250)
        control_layout = QVBoxLayout(control_frame)
        control_layout.setSpacing(12)
        control_layout.setContentsMargins(20, 15, 20, 15)

        control_title = QLabel("⚡ Diagnostic Controls")
        control_title.setProperty("class", "section-title")
        control_title.setFixedHeight(28)
        font = control_title.font()
        font.setPointSize(11)
        font.setBold(True)
        control_title.setFont(font)
        control_layout.addWidget(control_title)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        self.scan_btn = QPushButton("🚀 Full System Scan")
        self.scan_btn.setProperty("class", "primary")
        self.scan_btn.setFixedHeight(45)
        self.scan_btn.setMinimumWidth(180)
        self.scan_btn.clicked.connect(self.parent.run_full_scan)
        font = self.scan_btn.font()
        font.setPointSize(10)
        font.setBold(True)
        self.scan_btn.setFont(font)

        self.dtc_btn = QPushButton("📋 Read DTCs")
        self.dtc_btn.setProperty("class", "success")
        self.dtc_btn.setFixedHeight(45)
        self.dtc_btn.setMinimumWidth(150)
        self.dtc_btn.clicked.connect(self.parent.read_dtcs)
        font = self.dtc_btn.font()
        font.setPointSize(10)
        font.setBold(True)
        self.dtc_btn.setFont(font)

        self.clear_btn = QPushButton("🧹 Clear DTCs")
        self.clear_btn.setProperty("class", "warning")
        self.clear_btn.setFixedHeight(45)
        self.clear_btn.setMinimumWidth(150)
        self.clear_btn.clicked.connect(self.parent.clear_dtcs)
        font = self.clear_btn.font()
        font.setPointSize(10)
        font.setBold(True)
        self.clear_btn.setFont(font)

        buttons_layout.addWidget(self.scan_btn)
        buttons_layout.addWidget(self.dtc_btn)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addStretch()

        control_layout.addLayout(buttons_layout)
        layout.addWidget(control_frame)

        # ----------------------------------------------------------
        # RESULTS AREA - BIGGER WITH SCROLL
        # ----------------------------------------------------------
        results_frame = QFrame()
        results_frame.setProperty("class", "glass-card")
        results_frame.setMinimumHeight(400)
        results_layout = QVBoxLayout(results_frame)
        results_layout.setSpacing(12)
        results_layout.setContentsMargins(20, 15, 20, 15)

        results_title = QLabel("📊 Scan Results")
        results_title.setProperty("class", "section-title")
        results_title.setFixedHeight(32)
        font = results_title.font()
        font.setPointSize(12)
        font.setBold(True)
        results_title.setFont(font)
        results_layout.addWidget(results_title)

        # Create scroll area for results text
        results_scroll = QScrollArea()
        results_scroll.setWidgetResizable(True)
        results_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        results_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        results_scroll.setFrameShape(QFrame.Shape.StyledPanel)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(320)
        self.results_text.setPlainText(
            "System ready for diagnostics.\n\n"
            "Steps to begin:\n"
            "1. Select a vehicle brand from the header\n"
            "2. Scan for VCI devices (optional)\n"
            "3. Click 'Full System Scan' to begin diagnostics\n\n"
            "Alternatively:\n"
            "• Click 'Read DTCs' to read diagnostic trouble codes\n"
            "• Click 'Clear DTCs' to clear stored codes"
        )
        font = self.results_text.font()
        font.setPointSize(10)
        self.results_text.setFont(font)

        results_scroll.setWidget(self.results_text)
        results_layout.addWidget(results_scroll)
        layout.addWidget(results_frame)

        # Set content widget to scroll area
        scroll_area.setWidget(content_widget)

        # Main tab layout
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)

        return tab, "🔧 Diagnostics"

    def scan_for_vci(self):
        """Scan for available VCI devices"""
        try:
            if hasattr(self.parent, 'diagnostics_controller') and self.parent.diagnostics_controller:
                self.results_text.setPlainText("🔍 Scanning for VCI devices...\n\nPlease wait...")
                result = self.parent.diagnostics_controller.scan_for_vci_devices()

                if result["status"] == "success":
                    devices = result.get("devices", [])
                    if devices:
                        device_list = "\n".join([
                            f"• {d['name']} ({d['type']}) on {d.get('port', 'Unknown')}" 
                            for d in devices
                        ])
                        self.results_text.setPlainText(
                            f"✅ VCI Devices Found\n\n"
                            f"Discovered {len(devices)} device(s):\n\n{device_list}\n\n"
                            f"Click 'Connect VCI' to establish connection."
                        )
                        self.vci_connect_btn.setEnabled(True)
                    else:
                        self.results_text.setPlainText(
                            "⚠️ No VCI Devices Found\n\n"
                            "No VCI devices were detected.\n\n"
                            "Troubleshooting:\n"
                            "• Ensure your VCI device is connected via USB\n"
                            "• Check that the device is powered on\n"
                            "• Verify driver installation\n"
                            "• Try a different USB port\n"
                            "• Restart the application"
                        )
                        self.vci_connect_btn.setEnabled(False)
                else:
                    self.results_text.setPlainText(
                        f"❌ VCI Scan Failed\n\n"
                        f"Error: {result.get('message', 'Unknown error')}\n\n"
                        f"Please check your VCI device connection and try again."
                    )
                    self.vci_connect_btn.setEnabled(False)
            else:
                self.results_text.setPlainText(
                    "⚠️ Diagnostics Controller Not Available\n\n"
                    "The diagnostics controller is not initialized.\n"
                    "Please restart the application."
                )
        except Exception as e:
            self.results_text.setPlainText(
                f"❌ Error Scanning for VCI\n\n"
                f"Exception: {str(e)}\n\n"
                f"Please check the application logs for more details."
            )

    def connect_vci(self):
        """Connect to the first available VCI device"""
        try:
            if hasattr(self.parent, 'diagnostics_controller') and self.parent.diagnostics_controller:
                self.results_text.setPlainText("🔌 Connecting to VCI...\n\nPlease wait...")
                result = self.parent.diagnostics_controller.connect_to_vci(device_index=0)

                if result["status"] == "success":
                    device = result.get("device", {})
                    capabilities = ', '.join(device.get('capabilities', ['Unknown']))
                    
                    self.results_text.setPlainText(
                        f"✅ Successfully Connected to VCI\n\n"
                        f"Device Information:\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"Device Name: {device.get('name', 'Unknown')}\n"
                        f"Device Type: {device.get('type', 'Unknown')}\n"
                        f"Port: {device.get('port', 'Unknown')}\n"
                        f"Capabilities: {capabilities}\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"The VCI device is ready for diagnostics.\n"
                        f"You can now perform system scans and read DTCs."
                    )
                    self.vci_connect_btn.setEnabled(False)
                    self.vci_disconnect_btn.setEnabled(True)
                else:
                    self.results_text.setPlainText(
                        f"❌ VCI Connection Failed\n\n"
                        f"Error: {result.get('message', 'Unknown error')}\n\n"
                        f"Please verify:\n"
                        f"• VCI device is properly connected\n"
                        f"• No other application is using the device\n"
                        f"• Device drivers are installed correctly"
                    )
            else:
                self.results_text.setPlainText(
                    "⚠️ Diagnostics Controller Not Available\n\n"
                    "Cannot connect to VCI device."
                )
        except Exception as e:
            self.results_text.setPlainText(
                f"❌ Error Connecting to VCI\n\n"
                f"Exception: {str(e)}"
            )

    def disconnect_vci(self):
        """Disconnect from the current VCI device"""
        try:
            if hasattr(self.parent, 'diagnostics_controller') and self.parent.diagnostics_controller:
                self.results_text.setPlainText("🔌 Disconnecting VCI...\n\nPlease wait...")
                result = self.parent.diagnostics_controller.disconnect_vci()

                if result["status"] == "success":
                    self.results_text.setPlainText(
                        "✅ VCI Disconnected Successfully\n\n"
                        "The VCI device has been safely disconnected.\n\n"
                        "You can:\n"
                        "• Scan for devices again\n"
                        "• Connect to a different VCI\n"
                        "• Close the application"
                    )
                    self.vci_connect_btn.setEnabled(True)
                    self.vci_disconnect_btn.setEnabled(False)
                else:
                    self.results_text.setPlainText(
                        f"❌ VCI Disconnect Failed\n\n"
                        f"Error: {result.get('message', 'Unknown error')}"
                    )
            else:
                self.results_text.setPlainText(
                    "⚠️ Diagnostics Controller Not Available\n\n"
                    "Cannot disconnect VCI device."
                )
        except Exception as e:
            self.results_text.setPlainText(
                f"❌ Error Disconnecting VCI\n\n"
                f"Exception: {str(e)}"
            )

    def update_vci_status_display(self, status_info):
        """Update the VCI status display"""
        try:
            if status_info["status"] == "connected":
                device = status_info.get("device", {})
                status_text = f"✅ Connected: {device.get('name', 'Unknown')} ({device.get('type', 'Unknown')})"
                self.vci_connect_btn.setEnabled(False)
                self.vci_disconnect_btn.setEnabled(True)
            elif status_info["status"] == "disconnected":
                status_text = "🔌 VCI Status: Not Connected"
                self.vci_connect_btn.setEnabled(True)
                self.vci_disconnect_btn.setEnabled(False)
            elif status_info["status"] == "not_available":
                status_text = "⚠️ VCI Status: Manager Not Available"
                self.vci_connect_btn.setEnabled(False)
                self.vci_disconnect_btn.setEnabled(False)
            else:
                status_text = f"🔌 VCI Status: {status_info['status']}"

            if self.vci_status_label:
                self.vci_status_label.setText(status_text)

        except Exception as e:
            print(f"Error updating VCI status display: {e}")