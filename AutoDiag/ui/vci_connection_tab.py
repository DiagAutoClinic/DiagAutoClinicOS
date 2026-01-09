# VCI Connection Tab - Dedicated tab for VCI device management

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QPushButton, QTextEdit, QScrollArea, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)

class VCIConnectionTab:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.scan_btn = None
        self.connect_btn = None
        self.disconnect_btn = None
        self.results_text = None
        self.status_label = None
        self.progress_bar = None

        # VCI scan state tracking
        self._scan_in_progress = False
        self._scan_timeout_timer = None
        self._last_scan_results = []

        # Connect to VCI manager signals if available
        self._connect_vci_signals()

    def create_tab(self):
        """Create the VCI connection tab"""
        tab = QWidget()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 12, 15, 12)

        # HEADER
        header = QLabel("VCI Device Connection")
        header.setProperty("class", "tab-title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFixedHeight(50)
        layout.addWidget(header)

        # STATUS SECTION
        status_frame = QFrame()
        status_frame.setProperty("class", "glass-card")
        status_frame.setMinimumHeight(120)
        status_layout = QVBoxLayout(status_frame)
        status_layout.setSpacing(12)
        status_layout.setContentsMargins(20, 15, 20, 15)

        status_title = QLabel("Connection Status")
        status_title.setProperty("class", "section-title")
        status_layout.addWidget(status_title)

        self.status_label = QLabel("VCI Status: Not Connected")
        self.status_label.setProperty("class", "section-label")
        status_layout.addWidget(self.status_label)

        layout.addWidget(status_frame)

        # CONTROL PANEL
        control_frame = QFrame()
        control_frame.setProperty("class", "glass-card")
        control_frame.setMinimumHeight(200)
        control_layout = QVBoxLayout(control_frame)
        control_layout.setSpacing(12)
        control_layout.setContentsMargins(20, 15, 20, 15)

        control_title = QLabel("Device Controls")
        control_title.setProperty("class", "section-title")
        control_layout.addWidget(control_title)

        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        control_layout.addWidget(self.progress_bar)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        self.scan_btn = QPushButton("🔍 Scan for VCI Devices")
        self.scan_btn.setProperty("class", "primary")
        self.scan_btn.setFixedHeight(45)
        self.scan_btn.setMinimumWidth(180)
        self.scan_btn.clicked.connect(self.start_vci_scan)

        self.connect_btn = QPushButton("🔗 Connect VCI")
        self.connect_btn.setProperty("class", "success")
        self.connect_btn.setFixedHeight(45)
        self.connect_btn.setMinimumWidth(150)
        self.connect_btn.clicked.connect(self.connect_vci)
        self.connect_btn.setEnabled(False)

        self.disconnect_btn = QPushButton("🔌 Disconnect VCI")
        self.disconnect_btn.setProperty("class", "warning")
        self.disconnect_btn.setFixedHeight(45)
        self.disconnect_btn.setMinimumWidth(160)
        self.disconnect_btn.clicked.connect(self.disconnect_vci)
        self.disconnect_btn.setEnabled(False)

        buttons_layout.addWidget(self.scan_btn)
        buttons_layout.addWidget(self.connect_btn)
        buttons_layout.addWidget(self.disconnect_btn)
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

        results_title = QLabel("Connection Results")
        results_title.setProperty("class", "section-title")
        results_layout.addWidget(results_title)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(350)
        self.results_text.setPlainText(
            "VCI Connection Manager\n"
            "=====================\n\n"
            "This tab manages VCI (Vehicle Communication Interface) device connections.\n\n"
            "Steps to connect:\n"
            "1. Click 'Scan for VCI Devices' to find available devices\n"
            "2. Click 'Connect VCI' to establish connection\n"
            "3. Once connected, you can perform diagnostics in other tabs\n\n"
            "Note: If no VCI hardware is connected, the scan will complete\n"
            "but find no devices. This is normal for evaluation purposes."
        )

        results_layout.addWidget(self.results_text)
        layout.addWidget(results_frame)

        scroll_area.setWidget(content_widget)

        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)

        return tab, "🔗 VCI Connection"

    def update_status(self, status_text):
        """Update status label"""
        if self.status_label:
            self.status_label.setText(status_text)
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
            # Show progress bar
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Scanning...")
            
            # Start a visual progress timer (just for UX, actual scan is in thread)
            self._scan_progress_value = 0
            self._scan_progress_timer = QTimer()
            self._scan_progress_timer.timeout.connect(self._update_scan_progress)
            self._scan_progress_timer.start(500)  # Update every 500ms

            # Immediate UI feedback
            self.results_text.setPlainText(
                "🔍 VCI Device Scan Started\n"
                "==========================\n\n"
                "Searching for VCI devices...\n"
                "This may take 10-30 seconds.\n\n"
                "Status: Initializing scan..."
            )
            self.update_status("🔍 Scanning for VCI devices...")
            self.scan_btn.setEnabled(False)

            # Verify controller exists
            if not hasattr(self.parent, 'diagnostics_controller'):
                raise Exception("No diagnostics_controller attribute")

            # Get manager
            controller = self.parent.diagnostics_controller
            if not hasattr(controller, 'vci_manager') or not controller.vci_manager:
                raise Exception("No VCI manager available")

            # Start SCAN (This is now non-blocking)
            started = controller.vci_manager.scan_for_devices(timeout=20)
            
            if not started:
                self.update_status("Scan already in progress")
                self.results_text.append("\n⚠️ Scan already in progress...")

        except Exception as e:
            logger.error(f"Scan start failed: {e}")
            self.results_text.append(f"\n❌ ERROR: Failed to start scan: {e}")
            self.scan_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
            if hasattr(self, '_scan_progress_timer'):
                self._scan_progress_timer.stop()

    def _update_scan_progress(self):
        """Update the visual progress bar"""
        if self._scan_progress_value < 90:
            self._scan_progress_value += 5
            self.progress_bar.setValue(self._scan_progress_value)
        else:
            # Keep it at 90% until done
            self.progress_bar.setFormat("Finalizing scan...")

    def _on_vci_devices_found(self, devices):
        """Handle devices found signal"""
        logger.info(f"UI received {len(devices)} devices")
        
        # Stop progress timer
        if hasattr(self, '_scan_progress_timer'):
            self._scan_progress_timer.stop()
        self.progress_bar.setValue(100)
        self.progress_bar.setFormat("Scan Complete")
        
        # Reset button state
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("🔍 Rescan Devices")
        
        # Update results text
        if not devices:
            self.results_text.setPlainText(
                "❌ No VCI Devices Found\n"
                "=======================\n\n"
                "Troubleshooting:\n"
                "1. Check USB connection\n"
                "2. Ensure drivers are installed\n"
                "3. Verify device power (LEDs on?)\n"
                "4. Try a different USB port\n"
            )
            self.update_status("No devices found")
            return

        # List devices
        result_text = "✅ Scan Complete - Devices Found:\n"
        result_text += "================================\n\n"
        
        for i, dev in enumerate(devices):
            result_text += f"{i+1}. {dev.name} ({dev.device_type.value})\n"
            result_text += f"   Port: {dev.port}\n"
            if dev.serial_number:
                result_text += f"   SN: {dev.serial_number}\n"
            result_text += "\n"
        
        result_text += "Select a device to connect."
        self.results_text.setPlainText(result_text)
        self.update_status(f"Found {len(devices)} devices")
        
        # Enable connect button if devices found
        self.connect_btn.setEnabled(True)
        self._last_scan_results = devices

        # AUTO CONNECT: If devices are found, automatically connect to the first one
        if devices:
            logger.info("Auto-connecting to first found device...")
            self.results_text.append("\n🔄 Auto-connecting to first device...")
            # Use a single-shot timer to allow UI to update before connecting
            QTimer.singleShot(500, self.connect_vci)


    def _on_vci_status_changed(self, status, data):
        """Handle VCI status updates"""
        logger.info(f"VCI status changed: {status} - {data}")

        if status == "progress":
            message = data.get("message", "") if isinstance(data, dict) else str(data)
            if message:
                self.results_text.append(f"Status: {message}")
                # Update progress bar if it's a percentage
                if "progress" in data and isinstance(data["progress"], (int, float)):
                    self.progress_bar.setValue(int(data["progress"]))

    def _on_scan_timeout(self):
        """Handle scan timeout"""
        logger.warning("VCI scan timed out")

        self._scan_in_progress = False
        self.scan_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        self.results_text.setPlainText(
            "⏰ VCI Scan Timeout\n"
            "==================\n\n"
            "The scan took longer than 30 seconds.\n\n"
            "This may indicate:\n"
            "- Hardware communication issues\n"
            "- Driver problems\n"
            "- System resource constraints\n\n"
            "Please try again or check your hardware."
        )
        self.update_status("⏰ VCI Scan timed out")

    def connect_vci(self):
        """Connect to first available VCI device"""
        logger.info("Connect VCI button clicked")

        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Connecting...")

            self.results_text.setPlainText("🔗 Connecting to VCI device...\n\nPlease wait...")
            self.update_status("🔗 Connecting...")

            result = self.parent.diagnostics_controller.connect_to_vci(device_index=0)

            if result.get("status") == "success":
                device = result.get("device", {})

                self.results_text.setPlainText(
                    f"✅ VCI Connected Successfully!\n"
                    f"===============================\n\n"
                    f"Device: {device.get('name', 'Unknown')}\n"
                    f"Type: {device.get('type', 'Unknown')}\n"
                    f"Port: {device.get('port', 'Unknown')}\n"
                    f"Capabilities: {', '.join(device.get('capabilities', ['Unknown']))}\n\n"
                    f"The VCI device is ready for diagnostics.\n"
                    f"You can now use the Diagnostics and other tabs."
                )
                self.update_status(f"✅ Connected: {device.get('name', 'VCI Device')}")
                self.connect_btn.setEnabled(False)
                self.disconnect_btn.setEnabled(True)
                self.progress_bar.setVisible(False)
            else:
                self.results_text.setPlainText(
                    f"❌ Connection Failed\n"
                    f"===================\n\n"
                    f"Error: {result.get('message', 'Unknown error')}\n\n"
                    f"Please check:\n"
                    f"- VCI device is properly connected\n"
                    f"- Device drivers are installed\n"
                    f"- No other application is using the device"
                )
                self.update_status("❌ Connection failed")
                self.progress_bar.setVisible(False)

        except Exception as e:
            logger.error(f"VCI connect error: {e}")
            self.results_text.setPlainText(f"❌ Connection Error\n\n{str(e)}")
            self.update_status("❌ Connection error")
            self.progress_bar.setVisible(False)

    def disconnect_vci(self):
        """Disconnect from VCI device"""
        logger.info("Disconnect VCI button clicked")

        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Disconnecting...")

            result = self.parent.diagnostics_controller.disconnect_vci()

            if result.get("status") == "success":
                self.results_text.setPlainText(
                    "🔌 VCI Disconnected Successfully\n"
                    "=================================\n\n"
                    "The VCI device has been disconnected.\n"
                    "You can scan for devices again if needed.\n\n"
                    "Note: Other tabs may show limited functionality\n"
                    "until a device is connected again."
                )
                self.update_status("🔌 VCI disconnected")
                self.connect_btn.setEnabled(True)
                self.disconnect_btn.setEnabled(False)
                self.progress_bar.setVisible(False)
            else:
                self.results_text.setPlainText(
                    f"❌ Disconnect Failed\n"
                    f"===================\n\n"
                    f"Error: {result.get('message', 'Unknown error')}"
                )
                self.progress_bar.setVisible(False)

        except Exception as e:
            logger.error(f"VCI disconnect error: {e}")
            self.results_text.setPlainText(f"❌ Disconnect Error\n\n{str(e)}")
            self.progress_bar.setVisible(False)

    def update_vci_status_display(self, status_info):
        """Update VCI status display"""
        try:
            status = status_info.get("status", "unknown")

            if status == "connected":
                device = status_info.get("device", {})
                self.update_status(f"✅ Connected: {device.get('name', 'VCI Device')}")
                self.connect_btn.setEnabled(False)
                self.disconnect_btn.setEnabled(True)
            elif status == "disconnected":
                self.update_status("🔌 VCI Status: Not Connected")
                self.connect_btn.setEnabled(True)
                self.disconnect_btn.setEnabled(False)
            else:
                self.update_status(f"VCI Status: {status}")

        except Exception as e:
            logger.error(f"Error updating VCI status display: {e}")