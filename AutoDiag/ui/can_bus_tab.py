#!/usr/bin/env python3
"""
FIXED: CAN Bus Tab with BIGGER FRAMES and SCROLL AREAS for 1366x768 with DACOS styling.
Author: Generated for AutoDiag Pro
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QTextEdit,
    QSplitter, QHeaderView, QScrollArea, QSizePolicy,
    QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Try CAN REF parser
try:
    from AutoDiag.core.can_bus_ref_parser import (
        ref_parser, get_vehicle_database, list_all_vehicles,
        get_all_manufacturers, VehicleCANDatabase, CANMessage
    )
    CAN_PARSER_AVAILABLE = True
except Exception:
    CAN_PARSER_AVAILABLE = False
    logger.warning("CAN REF parser not available - hardware required for CAN data.")

# Try DACOS THEME
try:
    from shared.themes import dacos_cyber_teal
    DACOS_AVAILABLE = True
except Exception:
    DACOS_AVAILABLE = False


class CANBusDataTab:
    """CAN Bus Tab with BIGGER FRAMES + SCROLL AREAS + DACOS styling."""

    def __init__(self, parent_window=None):
        self.parent = parent_window
        self.current_database: Optional[object] = None
        self.is_streaming = False
        self.stream_timer = QTimer()
        self.stream_timer.timeout.connect(self._update_live_data)

        self.message_counters: Dict[int, int] = {}

        # UI elements
        self.manufacturer_combo = None
        self.model_combo = None
        self.can_table = None
        self.signal_table = None
        self.status_text = None
        self.stream_btn = None
        self.vehicle_info_label = None
        self.splitter = None

    # --------------------------------------------------------------
    # PUBLIC FACTORY
    # --------------------------------------------------------------
    def create_tab(self, app=None):
        if app and DACOS_AVAILABLE:
            try:
                apply_theme(app)
            except Exception as e:
                logger.warning(f"DACOS theme apply failed: {e}")

        tab = QWidget()
        tab.setObjectName("can_bus_tab")

        # Create scroll area for entire tab
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Content widget inside scroll area
        content_widget = QWidget()
        main = QVBoxLayout(content_widget)
        main.setSpacing(12)
        main.setContentsMargins(15, 12, 15, 12)

        # ----------------------------------------------------------
        # HEADER - BIGGER
        # ----------------------------------------------------------
        header = QLabel("🚗 CAN Bus Data - Vehicle Reference Files")
        header.setProperty("class", "tab-title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFixedHeight(50)
        font = header.font()
        font.setPointSize(14)
        header.setFont(font)
        main.addWidget(header)

        # ----------------------------------------------------------
        # VEHICLE SELECTION - BIGGER
        # ----------------------------------------------------------
        vehicle_frame = self._create_vehicle_selection()
        vehicle_frame.setProperty("class", "glass-card")
        vehicle_frame.setMinimumHeight(120)
        main.addWidget(vehicle_frame)

        # ----------------------------------------------------------
        # CONTROL PANEL - BIGGER
        # ----------------------------------------------------------
        control = self._create_control_panel()
        control.setProperty("class", "glass-card")
        control.setMinimumHeight(70)
        main.addWidget(control)

        # ----------------------------------------------------------
        # SPLITTER AREA - MUCH BIGGER WITH SCROLL
        # ----------------------------------------------------------
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setProperty("class", "glass-card")
        self.splitter.setHandleWidth(8)
        self.splitter.setChildrenCollapsible(False)

        left = self._create_messages_panel()
        left.setProperty("class", "glass-card")

        right = self._create_signals_panel()
        right.setProperty("class", "glass-card")

        self.splitter.addWidget(left)
        self.splitter.addWidget(right)
        self.splitter.setSizes([850, 550])
        self.splitter.setMinimumHeight(450)  # Much bigger minimum height

        main.addWidget(self.splitter)

        # ----------------------------------------------------------
        # STATUS PANEL - BIGGER
        # ----------------------------------------------------------
        status = self._create_status_panel()
        status.setProperty("class", "glass-card")
        status.setMinimumHeight(120)
        main.addWidget(status)

        # Set content widget to scroll area
        scroll_area.setWidget(content_widget)

        # Main tab layout
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)

        self._populate_manufacturers()

        return tab, "🚗 CAN Bus"

    # --------------------------------------------------------------
    # SECTIONS - ALL BIGGER
    # --------------------------------------------------------------
    def _create_vehicle_selection(self):
        f = QFrame()
        g = QGridLayout(f)
        g.setSpacing(15)
        g.setContentsMargins(20, 15, 20, 15)

        lbl_m = QLabel("Manufacturer:")
        lbl_m.setProperty("class", "section-label")
        lbl_m.setFixedHeight(28)
        font = lbl_m.font()
        font.setPointSize(11)
        lbl_m.setFont(font)

        self.manufacturer_combo = QComboBox()
        self.manufacturer_combo.setMinimumHeight(35)
        self.manufacturer_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.manufacturer_combo.currentTextChanged.connect(self._on_manufacturer_changed)
        font = self.manufacturer_combo.font()
        font.setPointSize(10)
        self.manufacturer_combo.setFont(font)

        g.addWidget(lbl_m, 0, 0)
        g.addWidget(self.manufacturer_combo, 0, 1)

        lbl_model = QLabel("Model:")
        lbl_model.setProperty("class", "section-label")
        lbl_model.setFixedHeight(28)
        font = lbl_model.font()
        font.setPointSize(11)
        lbl_model.setFont(font)

        self.model_combo = QComboBox()
        self.model_combo.setMinimumHeight(35)
        self.model_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.model_combo.currentTextChanged.connect(self._on_model_changed)
        font = self.model_combo.font()
        font.setPointSize(10)
        self.model_combo.setFont(font)

        g.addWidget(lbl_model, 0, 2)
        g.addWidget(self.model_combo, 0, 3)

        load_btn = QPushButton("📥 Load Database")
        load_btn.setProperty("class", "primary")
        load_btn.setFixedHeight(42)
        load_btn.setFixedWidth(180)
        load_btn.clicked.connect(self._load_vehicle_database)
        font = load_btn.font()
        font.setPointSize(10)
        font.setBold(True)
        load_btn.setFont(font)
        g.addWidget(load_btn, 0, 4)

        self.vehicle_info_label = QLabel("Select a vehicle to load CAN definitions")
        self.vehicle_info_label.setProperty("class", "section-title")
        self.vehicle_info_label.setWordWrap(True)
        self.vehicle_info_label.setFixedHeight(30)
        font = self.vehicle_info_label.font()
        font.setPointSize(10)
        self.vehicle_info_label.setFont(font)
        g.addWidget(self.vehicle_info_label, 1, 0, 1, 5)

        g.setColumnStretch(1, 2)
        g.setColumnStretch(3, 2)
        g.setColumnStretch(4, 0)

        return f

    def _create_control_panel(self):
        f = QFrame()
        h = QHBoxLayout(f)
        h.setSpacing(15)
        h.setContentsMargins(20, 15, 20, 15)

        self.stream_btn = QPushButton("▶ Start CAN Stream")
        self.stream_btn.setProperty("class", "success")
        self.stream_btn.setFixedHeight(45)
        self.stream_btn.setMinimumWidth(180)
        self.stream_btn.clicked.connect(self._toggle_stream)
        font = self.stream_btn.font()
        font.setPointSize(10)
        font.setBold(True)
        self.stream_btn.setFont(font)
        h.addWidget(self.stream_btn)

        clear = QPushButton("🗑️ Clear Data")
        clear.setProperty("class", "warning")
        clear.setFixedHeight(45)
        clear.setMinimumWidth(150)
        clear.clicked.connect(self._clear_data)
        font = clear.font()
        font.setPointSize(10)
        font.setBold(True)
        clear.setFont(font)
        h.addWidget(clear)

        export = QPushButton("💾 Export Log")
        export.setFixedHeight(45)
        export.setMinimumWidth(150)
        export.clicked.connect(self._export_log)
        font = export.font()
        font.setPointSize(10)
        font.setBold(True)
        export.setFont(font)
        h.addWidget(export)

        h.addStretch()

        return f

    # --------------------------------------------------------------
    # CAN MESSAGES PANEL - WITH SCROLL AREA
    # --------------------------------------------------------------
    def _create_messages_panel(self):
        f = QFrame()
        v = QVBoxLayout(f)
        v.setSpacing(10)
        v.setContentsMargins(15, 12, 15, 12)

        title = QLabel("📡 CAN Messages")
        title.setProperty("class", "section-title")
        title.setFixedHeight(35)
        font = title.font()
        font.setPointSize(12)
        font.setBold(True)
        title.setFont(font)
        v.addWidget(title)

        # Create scroll area for table
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setFrameShape(QFrame.Shape.StyledPanel)

        self.can_table = QTableWidget()
        self.can_table.setColumnCount(6)
        self.can_table.setHorizontalHeaderLabels([
            "CAN ID", "Name", "DLC", "Data (Hex)", "Count", "Last Up"
        ])

        # Set column widths
        self.can_table.setColumnWidth(0, 90)
        self.can_table.setColumnWidth(1, 180)
        self.can_table.setColumnWidth(2, 60)
        self.can_table.setColumnWidth(3, 250)
        self.can_table.setColumnWidth(4, 70)
        self.can_table.setColumnWidth(5, 140)

        header = self.can_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)

        # Bigger fonts
        font = self.can_table.font()
        font.setPointSize(9)
        self.can_table.setFont(font)
        
        header_font = header.font()
        header_font.setPointSize(10)
        header_font.setBold(True)
        header.setFont(header_font)

        self.can_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.can_table.itemSelectionChanged.connect(self._on_message_selected)
        self.can_table.setAlternatingRowColors(True)
        self.can_table.verticalHeader().setDefaultSectionSize(32)  # Bigger rows
        self.can_table.setShowGrid(True)
        self.can_table.setMinimumHeight(350)  # Much bigger

        scroll.setWidget(self.can_table)
        v.addWidget(scroll)

        return f

    # --------------------------------------------------------------
    # SIGNALS PANEL - WITH SCROLL AREA
    # --------------------------------------------------------------
    def _create_signals_panel(self):
        f = QFrame()
        v = QVBoxLayout(f)
        v.setSpacing(10)
        v.setContentsMargins(15, 12, 15, 12)

        title = QLabel("📊 Signal Values")
        title.setProperty("class", "section-title")
        title.setFixedHeight(35)
        font = title.font()
        font.setPointSize(12)
        font.setBold(True)
        title.setFont(font)
        v.addWidget(title)

        # Create scroll area for table
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setFrameShape(QFrame.Shape.StyledPanel)

        self.signal_table = QTableWidget()
        self.signal_table.setColumnCount(5)
        self.signal_table.setHorizontalHeaderLabels(["Signal", "Value", "Unit", "Min", "Max"])

        # Set column widths
        self.signal_table.setColumnWidth(0, 150)
        self.signal_table.setColumnWidth(1, 90)
        self.signal_table.setColumnWidth(2, 70)
        self.signal_table.setColumnWidth(3, 70)
        self.signal_table.setColumnWidth(4, 70)

        hdr = self.signal_table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)

        # Bigger fonts
        font = self.signal_table.font()
        font.setPointSize(9)
        self.signal_table.setFont(font)
        
        header_font = hdr.font()
        header_font.setPointSize(10)
        header_font.setBold(True)
        hdr.setFont(header_font)

        self.signal_table.setAlternatingRowColors(True)
        self.signal_table.verticalHeader().setDefaultSectionSize(32)  # Bigger rows
        self.signal_table.setShowGrid(True)
        self.signal_table.setMinimumHeight(350)  # Much bigger

        scroll.setWidget(self.signal_table)
        v.addWidget(scroll)

        return f

    # --------------------------------------------------------------
    # STATUS PANEL - BIGGER WITH SCROLL
    # --------------------------------------------------------------
    def _create_status_panel(self):
        f = QFrame()
        v = QVBoxLayout(f)
        v.setSpacing(10)
        v.setContentsMargins(20, 15, 20, 15)

        lbl = QLabel("📋 Status Log")
        lbl.setProperty("class", "section-label")
        lbl.setFixedHeight(30)
        font = lbl.font()
        font.setPointSize(11)
        font.setBold(True)
        lbl.setFont(font)
        v.addWidget(lbl)

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMinimumHeight(60)
        self.status_text.setMaximumHeight(80)
        self.status_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.status_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        font = self.status_text.font()
        font.setPointSize(9)
        self.status_text.setFont(font)
        v.addWidget(self.status_text)

        return f

    # --------------------------------------------------------------
    # MANUFACTURER / MODEL POPULATION
    # --------------------------------------------------------------
    def _populate_manufacturers(self):
        self.manufacturer_combo.clear()
        self.manufacturer_combo.addItem("-- Select Manufacturer --")

        if CAN_PARSER_AVAILABLE:
            try:
                mfrs = get_all_manufacturers()
                self.manufacturer_combo.addItems(mfrs)
                self._log(f"Loaded {len(mfrs)} manufacturers.")
            except Exception:
                self.manufacturer_combo.addItems(["BMW", "Audi", "Toyota"])
        else:
            manufacturers = ["BMW", "Mercedes", "Audi", "Toyota", "Honda", "Ford"]
            self.manufacturer_combo.addItems(manufacturers)
            self._log("CAN parser not available - limited manufacturer list.")

    def _on_manufacturer_changed(self, m):
        self.model_combo.clear()
        self.model_combo.addItem("-- Select Model --")

        if m != "-- Select Manufacturer --" and CAN_PARSER_AVAILABLE:
            try:
                models = ref_parser.get_models_for_manufacturer(m)
                self.model_combo.addItems(models)
            except Exception:
                self.model_combo.addItem("Generic")
        else:
            self.model_combo.addItem("Generic")

    def _on_model_changed(self, model):
        if model != "-- Select Model --":
            self.vehicle_info_label.setText(
                f"Selected: {self.manufacturer_combo.currentText()} {model}"
            )

    # --------------------------------------------------------------
    # LOAD DATABASE + TABLE POPULATION
    # --------------------------------------------------------------
    def _load_vehicle_database(self):
        m = self.manufacturer_combo.currentText()
        md = self.model_combo.currentText()

        if m == "-- Select Manufacturer --":
            self._log("⚠ Select manufacturer first.")
            return

        self._log(f"Loading CAN DB for {m} {md}...")
        if hasattr(self.parent, 'status_label'):
            self.parent.status_label.setText(f"Loading CAN database for {m} {md}...")

        if CAN_PARSER_AVAILABLE:
            try:
                self.current_database = get_vehicle_database(m, md)
            except Exception as e:
                logger.error(f"Failed to load CAN database: {e}")
                self.current_database = None
        else:
            # Mock DB
            from dataclasses import dataclass, field
            from typing import List, Dict

            @dataclass
            class Sig:
                name: str
                unit: str = ""
                min_value: float = 0
                max_value: float = 100

            @dataclass
            class Msg:
                can_id: int
                name: str
                dlc: int = 8
                signals: list = field(default_factory=list)

            @dataclass
            class DB:
                manufacturer: str
                model: str
                messages: Dict[int, Msg] = field(default_factory=dict)

            db = DB(m, md)
            db.messages = {
                0x7E8: Msg(0x7E8, "ECU_Response", 8, [
                    Sig("Engine_RPM", "RPM", 0, 8000),
                    Sig("Vehicle_Speed", "km/h", 0, 300),
                ]),
                0x1D0: Msg(0x1D0, "Engine_Data", 8, [
                    Sig("Throttle", "%", 0, 100),
                ]),
                0x3E8: Msg(0x3E8, "Transmission", 8, [
                    Sig("Gear_Position", "", 0, 6),
                    Sig("Oil_Temp", "°C", 0, 150),
                ]),
                0x2D0: Msg(0x2D0, "ABS_Data", 8, [
                    Sig("Wheel_Speed_FL", "km/h", 0, 300),
                    Sig("Wheel_Speed_FR", "km/h", 0, 300),
                ]),
            }
            self.current_database = db

        if not self.current_database:
            self._log("❌ Load failed.")
            if hasattr(self.parent, 'status_label'):
                self.parent.status_label.setText("Failed to load CAN database")
            return

        cnt = len(self.current_database.messages)
        self.vehicle_info_label.setText(f"Loaded {m} {md} – {cnt} messages")
        self._log(f"Loaded {cnt} messages.")
        self._populate_messages_table()

        if hasattr(self.parent, 'status_label'):
            self.parent.status_label.setText(f"Loaded CAN database: {cnt} messages")

    def _populate_messages_table(self):
        self.can_table.setRowCount(0)
        self.message_counters.clear()

        for can_id, msg in sorted(self.current_database.messages.items()):
            r = self.can_table.rowCount()
            self.can_table.insertRow(r)

            id_item = QTableWidgetItem(f"0x{can_id:03X}")
            id_item.setData(Qt.ItemDataRole.UserRole, can_id)
            self.can_table.setItem(r, 0, id_item)
            self.can_table.setItem(r, 1, QTableWidgetItem(msg.name))
            self.can_table.setItem(r, 2, QTableWidgetItem(str(msg.dlc)))
            self.can_table.setItem(r, 3, QTableWidgetItem("--"))
            self.can_table.setItem(r, 4, QTableWidgetItem("0"))
            self.can_table.setItem(r, 5, QTableWidgetItem("--"))

            self.message_counters[can_id] = 0

    def _on_message_selected(self):
        items = self.can_table.selectedItems()
        if not items:
            return
        row = items[0].row()
        canid = self.can_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        msg = self.current_database.messages.get(canid)
        if msg:
            self._populate_signals_table(msg)

    def _populate_signals_table(self, msg):
        self.signal_table.setRowCount(0)
        for s in msg.signals:
            r = self.signal_table.rowCount()
            self.signal_table.insertRow(r)
            self.signal_table.setItem(r, 0, QTableWidgetItem(s.name))
            self.signal_table.setItem(r, 1, QTableWidgetItem("--"))
            self.signal_table.setItem(r, 2, QTableWidgetItem(s.unit))
            self.signal_table.setItem(r, 3, QTableWidgetItem(str(s.min_value)))
            self.signal_table.setItem(r, 4, QTableWidgetItem(str(s.max_value)))

    # --------------------------------------------------------------
    # STREAMING / SIMULATION
    # --------------------------------------------------------------
    def _toggle_stream(self):
        if self.is_streaming:
            self._stop_stream()
        else:
            self._start_stream()

    def _start_stream(self):
        if not self.current_database:
            self._log("⚠ Load DB first.")
            return
        self.is_streaming = True
        self.stream_timer.start(100)

        self.stream_btn.setText("⏹ Stop CAN Stream")
        self.stream_btn.setProperty("class", "danger")
        self.stream_btn.style().unpolish(self.stream_btn)
        self.stream_btn.style().polish(self.stream_btn)

        self._log("▶ CAN stream started.")

    def _stop_stream(self):
        self.is_streaming = False
        self.stream_timer.stop()

        self.stream_btn.setText("▶ Start CAN Stream")
        self.stream_btn.setProperty("class", "success")
        self.stream_btn.style().unpolish(self.stream_btn)
        self.stream_btn.style().polish(self.stream_btn)

        self._log("⏹ CAN stream stopped.")

    def _update_live_data(self):
        if not self.current_database:
            return

        # Check if hardware is connected
        has_hardware = False
        if hasattr(self.parent, 'diagnostics_controller') and self.parent.diagnostics_controller:
            vci_status = self.parent.diagnostics_controller.get_vci_status()
            has_hardware = vci_status.get('status') == 'connected'

        if has_hardware:
            # Hardware connected - get real CAN data
            can_data = self.parent.diagnostics_controller._get_realtime_can_data()
            updated = 0
            for can_id, data in can_data.items():
                row = self._find_message_row(can_id)
                if row >= 0:
                    hexdata = " ".join(f"{b:02X}" for b in data)
                    self.can_table.item(row, 3).setText(hexdata)
                    self.message_counters[can_id] += 1
                    self.can_table.item(row, 4).setText(str(self.message_counters[can_id]))
                    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    self.can_table.item(row, 5).setText(ts)
                    updated += 1
        else:
            # No hardware - show hardware required
            for row in range(self.can_table.rowCount()):
                self.can_table.item(row, 3).setText("HW_REQ")
                self.can_table.item(row, 5).setText("Hardware Required")

        self._update_selected_signals()

    def _update_selected_signals(self):
        items = self.can_table.selectedItems()
        if not items:
            return
        row = items[0].row()
        canid = self.can_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        msg = self.current_database.messages.get(canid)
        if not msg:
            return

        # Check if hardware is connected
        has_hardware = False
        if hasattr(self.parent, 'diagnostics_controller') and self.parent.diagnostics_controller:
            vci_status = self.parent.diagnostics_controller.get_vci_status()
            has_hardware = vci_status.get('status') == 'connected'

        for r in range(self.signal_table.rowCount()):
            if r < len(msg.signals):
                if has_hardware:
                    # Hardware connected - get real signal values from live data
                    live_data = self.parent.diagnostics_controller.populate_sample_data()
                    # Find matching signal in live data
                    signal_name = msg.signals[r].name.replace('_', ' ').title()
                    value = "--"
                    for param, val, unit in live_data:
                        if param == signal_name:
                            value = val
                            break
                    self.signal_table.item(r, 1).setText(value)
                else:
                    # No hardware - show hardware required
                    self.signal_table.item(r, 1).setText("HW_REQ")

    # --------------------------------------------------------------
    # REALTIME MONITORING METHODS
    # --------------------------------------------------------------
    def start_realtime_monitoring(self):
        """Start realtime CAN bus monitoring with VCI integration"""
        if not self.is_streaming:
            self._start_stream()
            self._log("🔍 Realtime CAN monitoring started - Integrated with VCI device")

            if hasattr(self.parent, 'diagnostics_controller') and self.parent.diagnostics_controller:
                controller = self.parent.diagnostics_controller
                if controller.vci_manager and controller.vci_manager.is_connected():
                    self._log("✅ Connected to VCI device for realtime monitoring")
                else:
                    self._log("⚠️ No VCI device connected - Using simulated data")

    def stop_realtime_monitoring(self):
        """Stop realtime CAN bus monitoring"""
        if self.is_streaming:
            self._stop_stream()
            self._log("⏹ Realtime CAN monitoring stopped")

    def update_realtime_data(self, can_data):
        """Update CAN bus data from realtime source"""
        if not self.current_database or not self.is_streaming:
            return

        for can_id, data in can_data.items():
            if can_id in self.current_database.messages:
                row = self._find_message_row(can_id)
                if row >= 0:
                    hexdata = " ".join(f"{b:02X}" for b in data)
                    self.can_table.item(row, 3).setText(hexdata)
                    self.message_counters[can_id] += 1
                    self.can_table.item(row, 4).setText(str(self.message_counters[can_id]))
                    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    self.can_table.item(row, 5).setText(ts)

    def _find_message_row(self, can_id):
        """Find row index for a specific CAN ID"""
        for row in range(self.can_table.rowCount()):
            item = self.can_table.item(row, 0)
            if item and item.data(Qt.ItemDataRole.UserRole) == can_id:
                return row
        return -1

    # --------------------------------------------------------------
    # CLEAR / EXPORT / LOGGING
    # --------------------------------------------------------------
    def _clear_data(self):
        for r in range(self.can_table.rowCount()):
            self.can_table.item(r, 3).setText("--")
            self.can_table.item(r, 4).setText("0")
            self.can_table.item(r, 5).setText("--")
        self.signal_table.setRowCount(0)
        self.message_counters.clear()
        self._log("🗑 Data cleared.")

    def _export_log(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fn = f"can_log_{ts}.txt"
        try:
            with open(fn, "w", encoding="utf-8") as f:
                f.write("CAN Log Export\n")
                f.write(f"{datetime.now()}\n\n")
                for r in range(self.can_table.rowCount()):
                    id_ = self.can_table.item(r, 0).text()
                    name = self.can_table.item(r, 1).text()
                    data = self.can_table.item(r, 3).text()
                    count = self.can_table.item(r, 4).text()
                    f.write(f"{id_} | {name} | {data} | Count: {count}\n")
            self._log(f"💾 Exported: {fn}")
        except Exception as e:
            self._log(f"❌ Export failed: {e}")

    def _log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        if self.status_text:
            self.status_text.append(f"[{ts}] {msg}")
            sb = self.status_text.verticalScrollBar()
            sb.setValue(sb.maximum())

        if getattr(self.parent, "status_label", None):
            try:
                self.parent.status_label.setText(msg)
            except:
                pass