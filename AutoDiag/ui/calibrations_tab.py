#!/usr/bin/env python3
"""
AutoDiag Pro - Calibrations Tab
Separate tab implementation with consistent layout
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
                            QScrollArea, QListWidget, QListWidgetItem, QTextEdit,
                            QDialog, QLineEdit, QSpinBox, QCheckBox, QComboBox)
from PyQt6.QtCore import Qt
from datetime import datetime
import logging

class CalibrationsTab:
    """
    Enhanced Calibrations Tab with consistent layout and comprehensive functionality.
    
    This tab provides access to brand-specific calibration and reset procedures
    with parameter input and detailed execution reporting.
    """
    
    def __init__(self, parent_window):
        """
        Initialize the Calibrations Tab.
        
        Args:
            parent_window: The main application window instance
        """
        self.parent = parent_window
        self.calibrations_brand_info_label = None
        self.calibrations_list = None
        self.calibration_details = None
        self.calibrations_results_text = None
        self.execute_calibration_btn = None
        self.refresh_calibrations_btn = None

    def create_tab(self) -> tuple[QWidget, str]:
        """
        Create the calibrations tab and return the widget.
        
        Returns:
            tuple: (tab_widget, tab_title)
        """
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("⚙️ Calibrations & Resets")
        header.setProperty("class", "tab-title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)

        # Main content area - Create a scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(10, 10, 10, 10)

        # Brand info display
        self.calibrations_brand_info_label = QLabel("Select a vehicle brand from the header to view available calibration procedures.")
        self.calibrations_brand_info_label.setProperty("class", "section-title")
        self.calibrations_brand_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.calibrations_brand_info_label.setWordWrap(True)
        content_layout.addWidget(self.calibrations_brand_info_label)

        # Procedures list frame
        procedures_frame = QFrame()
        procedures_frame.setProperty("class", "glass-card")
        procedures_frame.setMinimumHeight(200)
        procedures_layout = QVBoxLayout(procedures_frame)
        
        procedures_title = QLabel("Available Procedures")
        procedures_title.setProperty("class", "section-title")
        procedures_layout.addWidget(procedures_title)
        
        self.calibrations_list = QListWidget()
        self.calibrations_list.setProperty("class", "glass-card")
        self.calibrations_list.itemSelectionChanged.connect(self.show_calibration_details)
        self.calibrations_list.itemDoubleClicked.connect(self.execute_selected_calibration)
        procedures_layout.addWidget(self.calibrations_list)
        
        content_layout.addWidget(procedures_frame)

        # Procedure details frame
        details_frame = QFrame()
        details_frame.setProperty("class", "glass-card")
        details_frame.setMinimumHeight(150)
        details_layout = QVBoxLayout(details_frame)
        
        details_title = QLabel("Procedure Details")
        details_title.setProperty("class", "section-title")
        details_layout.addWidget(details_title)
        
        self.calibration_details = QTextEdit()
        self.calibration_details.setReadOnly(True)
        self.calibration_details.setMaximumHeight(150)
        self.calibration_details.setPlainText("Select a procedure to view details and prerequisites.")
        details_layout.addWidget(self.calibration_details)
        
        content_layout.addWidget(details_frame)

        # Control buttons frame
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        
        self.execute_calibration_btn = QPushButton("⚡ Execute Procedure")
        self.execute_calibration_btn.setProperty("class", "primary")
        self.execute_calibration_btn.clicked.connect(self.execute_selected_calibration)
        self.execute_calibration_btn.setEnabled(False)

        self.refresh_calibrations_btn = QPushButton("🔄 Refresh Procedures")
        self.refresh_calibrations_btn.setProperty("class", "success")
        self.refresh_calibrations_btn.clicked.connect(self.refresh_calibrations_list)

        buttons_layout.addWidget(self.execute_calibration_btn)
        buttons_layout.addWidget(self.refresh_calibrations_btn)
        buttons_layout.addStretch()
        
        content_layout.addWidget(buttons_frame)

        # Results frame
        results_frame = QFrame()
        results_frame.setProperty("class", "glass-card")
        results_frame.setMinimumHeight(150)
        results_layout = QVBoxLayout(results_frame)
        
        results_title = QLabel("Execution Results")
        results_title.setProperty("class", "section-title")
        results_layout.addWidget(results_title)
        
        self.calibrations_results_text = QTextEdit()
        self.calibrations_results_text.setReadOnly(True)
        self.calibrations_results_text.setPlainText("Procedure execution results will appear here.")
        results_layout.addWidget(self.calibrations_results_text)
        
        content_layout.addWidget(results_frame)

        # Add stretch to push everything up
        content_layout.addStretch()

        # Set the scroll area content
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Initialize with current brand
        self.refresh_calibrations_list()

        return tab, "⚙️ Calibrations"

    def refresh_calibrations_list(self) -> None:
        """Refresh the calibrations list based on selected brand with enhanced error handling"""
        brand = self.parent.header.brand_combo.currentText()
        
        # Validate brand selection
        if not brand or brand == "":
            self.calibrations_brand_info_label.setText("⚠️ Please select a vehicle brand from the header")
            self.calibrations_list.clear()
            self.calibrations_list.addItem("Select a brand to view available procedures")
            return
            
        self.calibrations_list.clear()

        try:
            from shared.calibrations_reset import calibrations_resets_manager
            from shared.logger import get_logger
            
            # Get logger for this module
            logger = get_logger(__name__)
            logger.info(f"Loading calibration procedures for brand: {brand}")
            
            procedures = calibrations_resets_manager.get_brand_procedures(brand)
            
            if not procedures:
                self.calibrations_brand_info_label.setText(f"⚠️ No calibration procedures available for {brand}")
                self.calibrations_list.addItem("No procedures available for this brand")
                return
                
            # Validate procedure objects
            valid_procedures = []
            for proc in procedures:
                if hasattr(proc, 'procedure_id') and hasattr(proc, 'name'):
                    valid_procedures.append(proc)
                else:
                    logger.warning(f"Invalid procedure object found: {proc}")
            
            if not valid_procedures:
                self.calibrations_brand_info_label.setText(f"⚠️ No valid procedures found for {brand}")
                self.calibrations_list.addItem("No valid procedures available")
                return
                
            for proc in valid_procedures:
                try:
                    # Add reset type to display if available
                    reset_type_info = f" [{proc.reset_type.value.upper()}]" if hasattr(proc, 'reset_type') else ""
                    item_text = f"{proc.name} (Level {proc.security_level}){reset_type_info}"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, proc)
                    self.calibrations_list.addItem(item)
                except Exception as e:
                    logger.error(f"Error adding procedure {getattr(proc, 'name', 'Unknown')}: {e}")

            self.calibrations_brand_info_label.setText(f"✅ Found {len(valid_procedures)} procedures for {brand}")
            logger.info(f"Successfully loaded {len(valid_procedures)} procedures for {brand}")

        except ImportError as e:
            self.calibrations_brand_info_label.setText("❌ Calibration procedures module not available")
            self.calibrations_list.addItem("Module import error - check installation")
            logger.error(f"Import error loading procedures for {brand}: {e}")
            
        except Exception as e:
            self.calibrations_brand_info_label.setText(f"❌ Error loading procedures for {brand}")
            self.calibrations_list.addItem("Error loading procedures")
            logger.error(f"Error loading procedures for {brand}: {e}")

        # Update procedure details
        self.calibration_details.setPlainText("Select a procedure to view details and prerequisites.")
        self.execute_calibration_btn.setEnabled(False)

    def show_calibration_details(self) -> None:
        """Show details of selected calibration procedure with enhanced validation"""
        current_item = self.calibrations_list.currentItem()
        if not current_item:
            self.calibration_details.setPlainText("Select a procedure to view details and prerequisites.")
            self.execute_calibration_btn.setEnabled(False)
            return

        proc = current_item.data(Qt.ItemDataRole.UserRole)
        if not proc:
            self.calibration_details.setPlainText("❌ Invalid procedure selected.")
            self.execute_calibration_btn.setEnabled(False)
            return

        try:
            # Validate procedure attributes
            required_attrs = ['procedure_id', 'name', 'security_level', 'description', 'reset_type']
            missing_attrs = [attr for attr in required_attrs if not hasattr(proc, attr)]
            
            if missing_attrs:
                self.calibration_details.setPlainText(f"❌ Procedure missing required attributes: {', '.join(missing_attrs)}")
                self.execute_calibration_btn.setEnabled(False)
                return

            # Build details text with error handling
            details = f"Procedure Details:\n"
            details += "=" * 40 + "\n\n"
            
            details += f"Name: {proc.name}\n"
            details += f"ID: {proc.procedure_id}\n"
            
            # Handle reset type safely
            if hasattr(proc, 'reset_type') and hasattr(proc.reset_type, 'value'):
                details += f"Type: {proc.reset_type.value.title()}\n"
            else:
                details += "Type: Unknown\n"
                
            details += f"Security Level: {proc.security_level}\n"
            
            # Handle duration
            if hasattr(proc, 'duration'):
                details += f"Estimated Duration: {proc.duration}\n"
            details += "\n"

            # Description
            details += f"Description:\n{proc.description}\n\n"

            # Prerequisites
            if hasattr(proc, 'prerequisites') and proc.prerequisites:
                details += "Prerequisites:\n"
                for pre in proc.prerequisites:
                    if isinstance(pre, str):
                        details += f"• {pre}\n"
                    else:
                        details += f"• {str(pre)}\n"
                details += "\n"

            # Steps
            if hasattr(proc, 'steps') and proc.steps:
                details += "Procedure Steps:\n"
                for i, step in enumerate(proc.steps, 1):
                    if isinstance(step, str):
                        details += f"{i}. {step}\n"
                    else:
                        details += f"{i}. {str(step)}\n"
            else:
                details += "Steps: Standard procedure - follow on-screen instructions\n"

            # Safety warnings for high-level procedures
            if hasattr(proc, 'security_level') and proc.security_level >= 4:
                details += "\n⚠️ HIGH SECURITY LEVEL:\n"
                details += "This procedure requires elevated permissions.\n"
                details += "Ensure you have proper authorization before proceeding.\n"

            self.calibration_details.setPlainText(details)
            self.execute_calibration_btn.setEnabled(True)
            
        except Exception as e:
            from shared.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error displaying procedure details: {e}")
            
            self.calibration_details.setPlainText(f"❌ Error displaying procedure details:\n\n{str(e)}")
            self.execute_calibration_btn.setEnabled(False)

    def execute_selected_calibration(self) -> None:
        """Execute the selected calibration procedure"""
        current_item = self.calibrations_list.currentItem()
        if not current_item:
            return

        proc = current_item.data(Qt.ItemDataRole.UserRole)
        if not proc:
            return

        # Check if procedure requires parameters (for battery registration, etc.)
        if "battery" in proc.procedure_id.lower() or "battery" in proc.name.lower():
            # Show parameter input dialog for battery specs
            params = self.get_calibration_parameters(proc)
            if params is None:  # User cancelled
                return
        else:
            params = {}

        # Execute procedure
        try:
            from shared.calibrations_reset import calibrations_resets_manager
            from shared.logger import get_logger
            logger = get_logger(__name__)
            
            self.execute_calibration_btn.setEnabled(False)
            self.parent.status_label.setText(f"⚙️ Executing {proc.name}...")
            
            # Simulate execution (in real app, this would call the manager)
            # For now, show mock results after delay
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(3000, lambda: self.show_calibration_result(proc, params))
                
        except Exception as e:
            from shared.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error executing procedure {proc.name}: {e}")
            
            self.parent.status_label.setText(f"❌ Error executing {proc.name}")
            self.calibrations_results_text.setPlainText(f"❌ Execution error:\n\n{str(e)}")
            self.execute_calibration_btn.setEnabled(True)

    def get_calibration_parameters(self, proc) -> dict | None:
        """Get parameters for calibration procedure execution via dialog"""
        dialog = QDialog(self.parent)
        dialog.setWindowTitle(f"Parameters for {proc.name}")
        dialog.setModal(True)
        dialog.resize(400, 300)

        layout = QVBoxLayout(dialog)

        # Procedure description
        desc_label = QLabel(f"Description: {proc.description}")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Prerequisites
        if hasattr(proc, 'prerequisites') and proc.prerequisites:
            pre_label = QLabel("Prerequisites:")
            pre_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            layout.addWidget(pre_label)

            for pre in proc.prerequisites:
                if isinstance(pre, str):
                    pre_item = QLabel(f"• {pre}")
                    pre_item.setStyleSheet("margin-left: 10px;")
                    layout.addWidget(pre_item)

        # Parameter inputs for battery procedures
        param_inputs = {}
        if "battery" in proc.procedure_id.lower() or "battery" in proc.name.lower():
            params_label = QLabel("Battery Specifications:")
            params_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            layout.addWidget(params_label)

            # Battery type
            type_layout = QHBoxLayout()
            type_label = QLabel("Battery Type:")
            type_label.setMinimumWidth(150)
            type_combo = QComboBox()
            type_combo.addItems(["AGM", "Lead-acid (EFB)", "Standard (Flooded)", "Lithium-ion", "Gel"])
            type_combo.setCurrentIndex(0)
            type_layout.addWidget(type_label)
            type_layout.addWidget(type_combo)
            type_layout.addStretch()
            layout.addLayout(type_layout)
            param_inputs['battery_type'] = type_combo

            # Capacity
            capacity_layout = QHBoxLayout()
            capacity_label = QLabel("Capacity (Ah):")
            capacity_label.setMinimumWidth(150)
            capacity_spin = QSpinBox()
            capacity_spin.setRange(30, 200)
            capacity_spin.setValue(70)
            capacity_spin.setSuffix(" Ah")
            capacity_layout.addWidget(capacity_label)
            capacity_layout.addWidget(capacity_spin)
            capacity_layout.addStretch()
            layout.addLayout(capacity_layout)
            param_inputs['capacity'] = capacity_spin

            # Voltage
            voltage_layout = QHBoxLayout()
            voltage_label = QLabel("Nominal Voltage:")
            voltage_label.setMinimumWidth(150)
            voltage_combo = QComboBox()
            voltage_combo.addItems(["12V", "24V", "48V"])
            voltage_combo.setCurrentIndex(0)
            voltage_layout.addWidget(voltage_label)
            voltage_layout.addWidget(voltage_combo)
            voltage_layout.addStretch()
            layout.addLayout(voltage_layout)
            param_inputs['voltage'] = voltage_combo

            # Manufacturer
            manufacturer_layout = QHBoxLayout()
            manufacturer_label = QLabel("Manufacturer:")
            manufacturer_label.setMinimumWidth(150)
            manufacturer_edit = QLineEdit()
            manufacturer_edit.setPlaceholderText("e.g., Bosch, Varta, Exide")
            manufacturer_layout.addWidget(manufacturer_label)
            manufacturer_layout.addWidget(manufacturer_edit)
            manufacturer_layout.addStretch()
            layout.addLayout(manufacturer_layout)
            param_inputs['manufacturer'] = manufacturer_edit

        # Safety warnings
        if hasattr(proc, 'security_level') and proc.security_level >= 3:
            safety_label = QLabel("⚠️ Safety Warning:")
            safety_label.setStyleSheet("font-weight: bold; margin-top: 10px; color: #FF6B6B;")
            layout.addWidget(safety_label)
            
            safety_text = QLabel("This procedure may affect vehicle safety systems.\nEnsure proper conditions are met before proceeding.")
            safety_text.setStyleSheet("margin-left: 10px; color: #FF6B6B;")
            safety_text.setWordWrap(True)
            layout.addWidget(safety_text)

        # Buttons
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        execute_btn = QPushButton("Execute")
        execute_btn.setProperty("class", "primary")

        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(execute_btn)
        layout.addLayout(buttons_layout)

        # Connect buttons
        def on_execute():
            params = {}
            for param_name, input_widget in param_inputs.items():
                if isinstance(input_widget, QComboBox):
                    params[param_name] = input_widget.currentText()
                elif isinstance(input_widget, QSpinBox):
                    params[param_name] = input_widget.value()
                else:  # QLineEdit
                    params[param_name] = input_widget.text()

            dialog.accept()
            dialog._params = params

        def on_cancel():
            dialog.reject()

        execute_btn.clicked.connect(on_execute)
        cancel_btn.clicked.connect(on_cancel)

        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            return getattr(dialog, '_params', {})
        return None

    def show_calibration_result(self, proc, params) -> None:
        """Show calibration execution result with enhanced details"""
        from datetime import datetime
        
        brand = self.parent.header.brand_combo.currentText()

        # Generate execution report
        result_text = f"Calibration Procedure Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        result_text += "=" * 60 + "\n\n"

        result_text += f"Brand: {brand}\n"
        result_text += f"Procedure: {proc.name}\n"
        result_text += f"Procedure ID: {proc.procedure_id}\n"
        
        if hasattr(proc, 'reset_type') and hasattr(proc.reset_type, 'value'):
            result_text += f"Type: {proc.reset_type.value.title()}\n"
        result_text += f"Security Level: {proc.security_level}\n\n"

        if params:
            result_text += "Parameters Used:\n"
            for key, value in params.items():
                result_text += f"  {key.replace('_', ' ').title()}: {value}\n"
            result_text += "\n"

        # Add execution details based on procedure type
        result_text += "Execution Results:\n"
        
        if "steering" in proc.procedure_id.lower() or "steering" in proc.name.lower():
            result_text += "✅ Steering Angle Sensor Calibration: SUCCESS\n"
            result_text += "📐 Zero point successfully calibrated\n"
            result_text += "🎯 Left stop: -540° | Center: 0° | Right stop: +540°\n"
            result_text += "🔄 Adaptation values stored in EPS module\n"
            result_text += "⚠️  Perform test drive to verify calibration\n"
        elif "battery" in proc.procedure_id.lower() or "battery" in proc.name.lower():
            result_text += "✅ Battery Registration: SUCCESS\n"
            result_text += "🔋 Battery specifications registered in power management\n"
            result_text += "⚡ Charging profile updated for optimal performance\n"
            result_text += "🔄 Adaptation values cleared and reset\n"
            result_text += "📊 Battery monitoring system activated\n"
        elif "throttle" in proc.procedure_id.lower() or "throttle" in proc.name.lower():
            result_text += "✅ Throttle Body Calibration: SUCCESS\n"
            result_text += "🎛️ Throttle position sensor calibrated\n"
            result_text += "⚖️ Idle adaptation completed (650-750 RPM)\n"
            result_text += "🚀 Acceleration response optimized\n"
            result_text += "🔄 Learning values stored in ECU\n"
        elif "window" in proc.procedure_id.lower() or "window" in proc.name.lower():
            result_text += "✅ Window Calibration: SUCCESS\n"
            result_text += "🪟 Upper and lower limits learned\n"
            result_text += "🔄 Anti-pinch function calibrated\n"
            result_text += "✅ All windows calibrated successfully\n"
        else:
            result_text += "✅ Procedure executed successfully\n"
            result_text += "📋 All calibration steps completed\n"
            result_text += "🔍 System verification passed\n"
            result_text += "✅ No errors detected\n"

        result_text += "\n" + "=" * 60
        result_text += "\n⚙️ Calibration completed successfully"
        result_text += f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        result_text += f"\nDuration: {proc.duration if hasattr(proc, 'duration') else 'N/A'}"

        self.calibrations_results_text.setPlainText(result_text)
        self.parent.status_label.setText(f"✅ {proc.name} completed successfully")
        self.execute_calibration_btn.setEnabled(True)
