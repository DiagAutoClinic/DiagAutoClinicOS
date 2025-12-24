#!/usr/bin/env python3
"""
AutoDiag Pro - Diagnostics Tab FINAL WORKING VERSION
All VCI buttons now provide proper feedback
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, 
    QPushButton, QTextEdit, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)

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
        
        # VCI scan state tracking
        self._scan_in_progress = False
        self._scan_timeout_timer = None
        self._last_scan_results = []
        
        # Connect to VCI manager signals if available
        self._connect_vci_signals()

    def create_tab(self):
        """Create the diagnostics tab"""
        tab = QWidget()
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 12, 15, 12)

        # HEADER
        header = QLabel("Advanced Diagnostics")
        header.setProperty("class", "tab-title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFixedHeight(50)
        layout.addWidget(header)

        # VCI STATUS SECTION
        vci_frame = QFrame()
        vci_frame.setProperty("class", "glass-card")
        vci_frame.setMinimumHeight(200)
        vci_layout = QVBoxLayout(vci_frame)
        vci_layout.setSpacing(12)
        vci_layout.setContentsMargins(20, 15, 20, 15)

        vci_title = QLabel("VCI Interface")
        vci_title.setProperty("class", "section-title")
        vci_layout.addWidget(vci_title)

        self.vci_status_label = QLabel("VCI Status: Not Connected")
        self.vci_status_label.setProperty("class", "section-label")
        vci_layout.addWidget(self.vci_status_label)

        # VCI control buttons
        vci_buttons = QHBoxLayout()
        vci_buttons.setSpacing(15)

        self.vci_scan_btn = QPushButton("Scan for VCI")
        self.vci_scan_btn.setProperty("class", "primary")
        self.vci_scan_btn.setFixedHeight(45)
        self.vci_scan_btn.setMinimumWidth(150)
        self.vci_scan_btn.clicked.connect(self.start_vci_scan)

        self.vci_connect_btn = QPushButton("Connect VCI")
        self.vci_connect_btn.setProperty("class", "success")
        self.vci_connect_btn.setFixedHeight(45)
        self.vci_connect_btn.setMinimumWidth(150)
        self.vci_connect_btn.clicked.connect(self.connect_vci)
        self.vci_connect_btn.setEnabled(False)

        self.vci_disconnect_btn = QPushButton("Disconnect VCI")
        self.vci_disconnect_btn.setProperty("class", "warning")
        self.vci_disconnect_btn.setFixedHeight(45)
        self.vci_disconnect_btn.setMinimumWidth(160)
        self.vci_disconnect_btn.clicked.connect(self.disconnect_vci)
        self.vci_disconnect_btn.setEnabled(False)

        vci_buttons.addWidget(self.vci_scan_btn)
        vci_buttons.addWidget(self.vci_connect_btn)
        vci_buttons.addWidget(self.vci_disconnect_btn)
        vci_buttons.addStretch()

        vci_layout.addLayout(vci_buttons)
        layout.addWidget(vci_frame)

        # CONTROL PANEL
        control_frame = QFrame()
        control_frame.setProperty("class", "glass-card")
        control_frame.setMinimumHeight(180)
        control_layout = QVBoxLayout(control_frame)
        control_layout.setSpacing(12)
        control_layout.setContentsMargins(20, 15, 20, 15)

        control_title = QLabel("Diagnostic Controls")
        control_title.setProperty("class", "section-title")
        control_layout.addWidget(control_title)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        self.scan_btn = QPushButton("Full System Scan")
        self.scan_btn.setProperty("class", "primary")
        self.scan_btn.setFixedHeight(45)
        self.scan_btn.clicked.connect(self.parent.run_full_scan)

        self.dtc_btn = QPushButton("Read DTCs")
        self.dtc_btn.setProperty("class", "success")
        self.dtc_btn.setFixedHeight(45)
        self.dtc_btn.clicked.connect(self.parent.read_dtcs)

        self.clear_btn = QPushButton("Clear DTCs")
        self.clear_btn.setProperty("class", "warning")
        self.clear_btn.setFixedHeight(45)
        self.clear_btn.clicked.connect(self.parent.clear_dtcs)

        buttons_layout.addWidget(self.scan_btn)
        buttons_layout.addWidget(self.dtc_btn)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addStretch()

        control_layout.addLayout(buttons_layout)
        layout.addWidget(control_frame)

        # RESULTS AREA
        results_frame = QFrame()
        results_frame.setProperty("class", "glass-card")
        results_frame.setMinimumHeight(400)
        results_layout = QVBoxLayout(results_frame)
        results_layout.setSpacing(12)
        results_layout.setContentsMargins(20, 15, 20, 15)

        results_title = QLabel("Scan Results")
        results_title.setProperty("class", "section-title")
        results_layout.addWidget(results_title)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(350)
        self.results_text.setPlainText(
            "System ready for diagnostics.\n\n"
            "Steps to begin:\n"
            "1. Click 'Scan for VCI' to find devices\n"
            "2. Click 'Connect VCI' after devices are found\n"
            "3. Perform diagnostics operations\n\n"
            "Note: If no VCI hardware is connected,\n"
            "the scan will complete but find no devices."
        )

        results_layout.addWidget(self.results_text)
        layout.addWidget(results_frame)

        scroll_area.setWidget(content_widget)

        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)

        return tab, "Diagnostics"

    def update_vci_status(self, status_text):
        """Update VCI status label"""
        if self.vci_status_label:
            self.vci_status_label.setText(status_text)
            logger.info(f"VCI Status: {status_text}")

    def _connect_vci_signals(self):
        """Connect to VCI manager signals"""
        try:
            if (hasattr(self.parent, 'diagnostics_controller') and 
                self.parent.diagnostics_controller and
                hasattr(self.parent.diagnostics_controller, 'vci_manager') and
                self.parent.diagnostics_controller.vci_manager):
                
                vci_mgr = self.parent.diagnostics_controller.vci_manager
                vci_mgr.devices_found.connect(self._on_vci_devices_found)
                vci_mgr.status_changed.connect(self._on_vci_status_changed)
                logger.info("VCI manager signals connected")
        except Exception as e:
            logger.error(f"Failed to connect VCI signals: {e}")
    
    def start_vci_scan(self):
        """Start VCI scan with immediate feedback"""
        logger.info("=== VCI SCAN BUTTON CLICKED ===")
        
        try:
            # Immediate UI feedback
            self.results_text.setPlainText(
                "VCI Scan Started\n"
                "================\n\n"
                "Checking for VCI devices...\n"
                "This may take 10-30 seconds.\n\n"
                "Status: Initializing scan..."
            )
            self.update_vci_status("Scanning for VCI devices...")
            self.vci_scan_btn.setEnabled(False)
            
            # Verify controller exists
            if not hasattr(self.parent, 'diagnostics_controller'):
                raise Exception("No diagnostics_controller attribute")
            
            if not self.parent.diagnostics_controller:
                raise Exception("diagnostics_controller is None")
            
            # Verify scan method exists
            if not hasattr(self.parent.diagnostics_controller, 'scan_for_vci_devices'):
                raise Exception("scan_for_vci_devices method not found")
            
            logger.info("Calling scan_for_vci_devices()...")
            
            # Call the scan method
            result = self.parent.diagnostics_controller.scan_for_vci_devices()
            
            logger.info(f"scan_for_vci_devices() returned: {result}")
            
            # Update UI based on result
            if isinstance(result, dict):
                status = result.get('status', 'unknown')
                message = result.get('message', 'No message')

                # DEBUG: Check self.results_text
                logger.info(f"DEBUG: self.results_text type: {type(self.results_text)}")
                logger.info(f"DEBUG: hasattr appendPlainText: {hasattr(self.results_text, 'appendPlainText')}")
                if hasattr(self.results_text, 'appendPlainText'):
                    self.results_text.appendPlainText(f"\n\nScan method called successfully!")
                    self.results_text.appendPlainText(f"Status: {status}")
                    self.results_text.appendPlainText(f"Message: {message}")
                else:
                    logger.error(f"DEBUG: appendPlainText not available, using setPlainText")
                    current_text = self.results_text.toPlainText() if hasattr(self.results_text, 'toPlainText') else ""
                    self.results_text.setPlainText(current_text + f"\n\nScan method called successfully!\nStatus: {status}\nMessage: {message}")
                
                if status == 'success':
                    self.results_text.appendPlainText(
                        "\n\nWaiting for scan to complete..."
                        "\nThis will take 10-30 seconds."
                        "\nResults will appear when ready."
                    )
                    
                    # Set up timeout
                    self._scan_in_progress = True
                    self._scan_timeout_timer = QTimer()
                    self._scan_timeout_timer.setSingleShot(True)
                    self._scan_timeout_timer.timeout.connect(self._on_scan_timeout)
                    self._scan_timeout_timer.start(30000)
                    
                else:
                    self.results_text.appendPlainText(f"\n\nERROR: Scan failed to start")
                    self.vci_scan_btn.setEnabled(True)
                    self.update_vci_status("VCI Scan failed")
            else:
                self.results_text.appendPlainText(
                    f"\n\nUnexpected return type: {type(result)}"
                )
                self.vci_scan_btn.setEnabled(True)
                
        except Exception as e:
            logger.error(f"VCI Scan error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            self.results_text.setPlainText(
                f"VCI Scan Error\n"
                f"==============\n\n"
                f"Error: {str(e)}\n\n"
                f"Type: {type(e).__name__}\n\n"
                f"This is likely a configuration issue.\n"
                f"Please check the application logs."
            )
            self.update_vci_status("VCI Scan error")
            self.vci_scan_btn.setEnabled(True)
    
    def _on_vci_devices_found(self, devices):
        """Handle VCI scan completion"""
        logger.info(f"VCI devices found signal received: {len(devices)} devices")
        
        # Clear timeout
        if self._scan_timeout_timer:
            self._scan_timeout_timer.stop()
            self._scan_timeout_timer = None
        
        self._scan_in_progress = False
        self.vci_scan_btn.setEnabled(True)
        self._last_scan_results = devices
        
        if devices:
            device_list = "\n".join([
                f"  {i+1}. {d.name} ({d.device_type.value}) on {d.port or 'Unknown'}" 
                for i, d in enumerate(devices)
            ])
            
            self.results_text.setPlainText(
                f"VCI Scan Complete!\n"
                f"==================\n\n"
                f"Found {len(devices)} device(s):\n\n"
                f"{device_list}\n\n"
                f"Click 'Connect VCI' to connect to the first device."
            )
            self.update_vci_status(f"Found {len(devices)} VCI device(s)")
            self.vci_connect_btn.setEnabled(True)
        else:
            self.results_text.setPlainText(
                "VCI Scan Complete\n"
                "=================\n\n"
                "No VCI devices found.\n\n"
                "This is normal if:\n"
                "- No VCI hardware is connected\n"
                "- Device drivers are not installed\n"
                "- Device is in use by another application\n\n"
                "Troubleshooting:\n"
                "1. Connect your VCI device via USB\n"
                "2. Install required drivers\n"
                "3. Close other diagnostic software\n"
                "4. Try scanning again"
            )
            self.update_vci_status("No VCI devices found")
            self.vci_connect_btn.setEnabled(False)
    
    def _on_vci_status_changed(self, status, data):
        """Handle VCI status updates"""
        logger.info(f"VCI status changed: {status} - {data}")
        
        if status == "progress":
            message = data.get("message", "") if isinstance(data, dict) else str(data)
            if message:
                self.results_text.appendPlainText(f"Status: {message}")
    
    def _on_scan_timeout(self):
        """Handle scan timeout"""
        logger.warning("VCI scan timed out")
        
        self._scan_in_progress = False
        self.vci_scan_btn.setEnabled(True)
        
        self.results_text.setPlainText(
            "VCI Scan Timeout\n"
            "================\n\n"
            "The scan took longer than 30 seconds.\n\n"
            "This may indicate:\n"
            "- Hardware communication issues\n"
            "- Driver problems\n"
            "- System resource constraints\n\n"
            "Please try again or check your hardware."
        )
        self.update_vci_status("VCI Scan timed out")
    
    def connect_vci(self):
        """Connect to first available VCI device"""
        logger.info("Connect VCI button clicked")
        
        try:
            self.results_text.setPlainText("Connecting to VCI device...\n\nPlease wait...")
            self.update_vci_status("Connecting...")
            
            result = self.parent.diagnostics_controller.connect_to_vci(device_index=0)
            
            if result.get("status") == "success":
                device = result.get("device", {})
                
                self.results_text.setPlainText(
                    f"VCI Connected!\n"
                    f"==============\n\n"
                    f"Device: {device.get('name', 'Unknown')}\n"
                    f"Type: {device.get('type', 'Unknown')}\n"
                    f"Port: {device.get('port', 'Unknown')}\n\n"
                    f"The VCI device is ready for diagnostics."
                )
                self.update_vci_status(f"Connected: {device.get('name', 'VCI Device')}")
                self.vci_connect_btn.setEnabled(False)
                self.vci_disconnect_btn.setEnabled(True)
            else:
                self.results_text.setPlainText(
                    f"Connection Failed\n"
                    f"=================\n\n"
                    f"Error: {result.get('message', 'Unknown error')}"
                )
                self.update_vci_status("Connection failed")
                
        except Exception as e:
            logger.error(f"VCI connect error: {e}")
            self.results_text.setPlainText(f"Connection Error\n\n{str(e)}")
            self.update_vci_status("Connection error")

    def disconnect_vci(self):
        """Disconnect from VCI device"""
        logger.info("Disconnect VCI button clicked")
        
        try:
            result = self.parent.diagnostics_controller.disconnect_vci()
            
            if result.get("status") == "success":
                self.results_text.setPlainText(
                    "VCI Disconnected\n"
                    "================\n\n"
                    "The VCI device has been disconnected.\n"
                    "You can scan for devices again if needed."
                )
                self.update_vci_status("VCI disconnected")
                self.vci_connect_btn.setEnabled(True)
                self.vci_disconnect_btn.setEnabled(False)
            else:
                self.results_text.setPlainText(
                    f"Disconnect Failed\n"
                    f"=================\n\n"
                    f"Error: {result.get('message', 'Unknown error')}"
                )
                
        except Exception as e:
            logger.error(f"VCI disconnect error: {e}")
            self.results_text.setPlainText(f"Disconnect Error\n\n{str(e)}")

    def update_vci_status_display(self, status_info):
        """Update VCI status display"""
        try:
            status = status_info.get("status", "unknown")
            
            if status == "connected":
                device = status_info.get("device", {})
                self.update_vci_status(f"Connected: {device.get('name', 'VCI Device')}")
                self.vci_connect_btn.setEnabled(False)
                self.vci_disconnect_btn.setEnabled(True)
            elif status == "disconnected":
                self.update_vci_status("VCI Status: Not Connected")
                self.vci_connect_btn.setEnabled(True)
                self.vci_disconnect_btn.setEnabled(False)
            else:
                self.update_vci_status(f"VCI Status: {status}")
                
        except Exception as e:
            logger.error(f"Error updating VCI status display: {e}")