#!/usr/bin/env python3
"""
Special Functions Module for AutoDiag Pro
Handles special functions management and execution
"""

import logging
import sys
import os

# Add project root to Python path to enable imports from shared directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QListWidgetItem, QCheckBox, QLineEdit, QLabel, QGridLayout, QWidget
from PyQt6.QtCore import Qt

logger = logging.getLogger(__name__)

# Import shared modules
try:
    from shared.special_functions import special_functions_manager, SecurityLevel
    SPECIAL_FUNCTIONS_AVAILABLE = True
except ImportError:
    SPECIAL_FUNCTIONS_AVAILABLE = False
    logger.warning("Special functions manager not available")


class SpecialFunctionsManager:
    """Manages special functions UI and execution"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.parameter_widgets = {}

    def update_special_functions_list(self, brand):
        """Update special functions list for current brand"""
        if not SPECIAL_FUNCTIONS_AVAILABLE:
            return

        functions = special_functions_manager.get_brand_functions(brand)

        self.main_window.special_functions_list.clear()

        for function in functions:
            item = QListWidgetItem(f"🔧 {function.name}")
            item.setData(Qt.ItemDataRole.UserRole, function.function_id)
            self.main_window.special_functions_list.addItem(item)

        self.main_window.sf_name_label.setText("Select a function to view details")
        self.main_window.sf_description.clear()
        self.main_window.sf_security_label.setText("Security Level: --")
        self.main_window.sf_execute_btn.setEnabled(False)
        self.clear_parameters()

    def on_special_function_selected(self, item):
        """Handle special function selection"""
        if not SPECIAL_FUNCTIONS_AVAILABLE:
            return

        brand = self.main_window.brand_combo.currentText()
        function_id = item.data(Qt.ItemDataRole.UserRole)
        function = special_functions_manager.get_function(brand, function_id)

        if not function:
            return

        self.main_window.sf_name_label.setText(f"🔧 {function.name}")
        self.main_window.sf_description.setText(function.description)
        self.main_window.sf_security_label.setText(f"Security Level: {function.security_level} "
                                     f"(Current: {self.main_window.security_manager.get_security_level().name})")

        self.create_parameter_inputs(function)

        has_clearance = self.main_window.security_manager.check_security_clearance(SecurityLevel(function.security_level))
        self.main_window.sf_execute_btn.setEnabled(has_clearance)

        if not has_clearance:
            self.main_window.sf_results.setPlainText(
                f"❌ Insufficient security clearance\n"
                f"Required: Level {function.security_level}\n"
                f"Current: Level {self.main_window.security_manager.get_security_level().value}")

    def create_parameter_inputs(self, function):
        """Create parameter input fields"""
        self.clear_parameters()

        if not function.parameters:
            no_params = QLabel("✅ No parameters required")
            no_params.setStyleSheet("color: #10b981;")
            self.main_window.sf_params_layout.addWidget(no_params)
            return

        param_widget = QWidget()
        param_layout = QGridLayout(param_widget)

        row = 0
        for param_name, param_config in function.parameters.items():
            label = QLabel(f"{param_name}:")
            label.setStyleSheet("color: #5eead4;")

            if param_config['type'] == 'bool':
                input_widget = QCheckBox()
            elif param_config['type'] == 'int':
                input_widget = QLineEdit()
                input_widget.setPlaceholderText("Enter number")
            else:
                input_widget = QLineEdit()
                input_widget.setPlaceholderText(f"Enter {param_config['type']}")

            param_layout.addWidget(label, row, 0)
            param_layout.addWidget(input_widget, row, 1)
            self.parameter_widgets[param_name] = input_widget
            row += 1

        self.main_window.sf_params_layout.addWidget(param_widget)

    def clear_parameters(self):
        """Clear parameter input section"""
        for i in reversed(range(self.main_window.sf_params_layout.count())):
            widget = self.main_window.sf_params_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def execute_special_function(self):
        """Execute selected special function"""
        if not SPECIAL_FUNCTIONS_AVAILABLE:
            self.main_window.sf_results.setPlainText("❌ Special functions not available")
            return

        brand = self.main_window.brand_combo.currentText()
        current_item = self.main_window.special_functions_list.currentItem()

        if not current_item:
            self.main_window.sf_results.setPlainText("❌ No function selected")
            return

        function_id = current_item.data(Qt.ItemDataRole.UserRole)

        parameters = {}
        for param_name, widget in self.parameter_widgets.items():
            if isinstance(widget, QLineEdit):
                parameters[param_name] = widget.text()
            elif isinstance(widget, QCheckBox):
                parameters[param_name] = widget.isChecked()

        self.main_window.sf_results.setPlainText("⏳ Executing function...")

        result = special_functions_manager.execute_function(brand, function_id, parameters)

        if result.get('success'):
            result_text = "✅ Function executed successfully!\n\n"
            for key, value in result.items():
                if key != 'success':
                    result_text += f"{key}: {value}\n"
        else:
            result_text = f"❌ Execution failed:\n{result.get('error', 'Unknown error')}"

        self.main_window.sf_results.setPlainText(result_text)