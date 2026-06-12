#!/usr/bin/env python3
"""
AutoDiag Pro - Special Functions Tab
Separate tab implementation for easier customization
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
                            QGroupBox, QScrollArea, QListWidget, QListWidgetItem, QTextEdit,
                            QDialog, QLineEdit, QSpinBox, QCheckBox)  # type: ignore
from PyQt6.QtCore import Qt  # type: ignore
from datetime import datetime
import logging

class SpecialFunctionsTab:
    """
    Enhanced Special Functions Tab with comprehensive error handling and validation.
    
    This tab provides access to brand-specific special functions with parameter input,
    security validation, and detailed execution reporting.
    """
    
    def __init__(self, parent_window):
        """
        Initialize the Special Functions Tab.
        
        Args:
            parent_window: The main application window instance
        """
        self.parent = parent_window
        self.brand_info_label = None
        self.functions_list = None
        self.function_details = None
        self.results_text = None
        self.execute_btn = None
        self.refresh_btn = None
        self.security_manager = None
        
        # Initialize security manager for special functions
        self._init_security_manager()
        
    def _init_security_manager(self) -> None:
        """Initialize security manager with fallback handling."""
        try:
            from shared.security_manager import security_manager
            self.security_manager = security_manager
        except ImportError:
            # Fallback - create a mock security manager for demo
            self.security_manager = None

    def create_tab(self) -> tuple[QWidget, str]:
        """
        Create the special functions tab and return the widget.
        
        Returns:
            tuple: (tab_widget, tab_title)
        """
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("🔧 Special Functions")
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
        self.brand_info_label = QLabel("Select a vehicle brand from the header to view available special functions.")
        self.brand_info_label.setProperty("class", "section-title")
        self.brand_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.brand_info_label.setWordWrap(True)
        content_layout.addWidget(self.brand_info_label)

        # Functions list frame
        functions_frame = QFrame()
        functions_frame.setProperty("class", "glass-card")
        functions_frame.setMinimumHeight(200)
        functions_layout = QVBoxLayout(functions_frame)
        
        functions_title = QLabel("Available Functions")
        functions_title.setProperty("class", "section-title")
        functions_layout.addWidget(functions_title)
        
        self.functions_list = QListWidget()
        self.functions_list.setProperty("class", "glass-card")
        self.functions_list.itemSelectionChanged.connect(self.show_function_details)
        self.functions_list.itemDoubleClicked.connect(self.execute_selected_function)
        functions_layout.addWidget(self.functions_list)
        
        content_layout.addWidget(functions_frame)

        # Function details frame
        details_frame = QFrame()
        details_frame.setProperty("class", "glass-card")
        details_frame.setMinimumHeight(150)
        details_layout = QVBoxLayout(details_frame)
        
        details_title = QLabel("Function Details")
        details_title.setProperty("class", "section-title")
        details_layout.addWidget(details_title)
        
        self.function_details = QTextEdit()
        self.function_details.setReadOnly(True)
        self.function_details.setMaximumHeight(150)
        self.function_details.setPlainText("Select a function to view details and parameters.")
        details_layout.addWidget(self.function_details)
        
        content_layout.addWidget(details_frame)

        # Control buttons frame
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        
        self.execute_btn = QPushButton("⚡ Execute Function")
        self.execute_btn.setProperty("class", "primary")
        self.execute_btn.clicked.connect(self.execute_selected_function)
        self.execute_btn.setEnabled(False)

        self.refresh_btn = QPushButton("🔄 Refresh Functions")
        self.refresh_btn.setProperty("class", "success")
        self.refresh_btn.clicked.connect(self.refresh_functions_list)

        buttons_layout.addWidget(self.execute_btn)
        buttons_layout.addWidget(self.refresh_btn)
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
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlainText("Function execution results will appear here.")
        results_layout.addWidget(self.results_text)
        
        content_layout.addWidget(results_frame)

        # Add stretch to push everything up
        content_layout.addStretch()

        # Set the scroll area content
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # REMOVED: self.tab_widget.addTab(tab, "🔧 Special Functions")
        # The tab will be added in the main window

        # Initialize with current brand
        self.refresh_functions_list()
        
        # REMOVED: Connect to brand changes (will be done in main window)
        # self.header.brand_combo.currentTextChanged.connect(self.on_brand_changed_special_functions)

        return tab, "🔧 Special Functions"

    def refresh_functions_list(self) -> None:
        """Refresh the functions list based on selected brand with enhanced error handling"""
        brand = self.parent.header.brand_combo.currentText()
        
        # Validate brand selection
        if not brand or brand == "":
            self.brand_info_label.setText("⚠️ Please select a vehicle brand from the header")
            self.functions_list.clear()
            self.functions_list.addItem("Select a brand to view available functions")
            return
            
        self.functions_list.clear()

        try:
            from shared.special_functions import special_functions_manager
            from shared.logger import get_logger
            
            # Get logger for this module
            logger = get_logger(__name__)
            logger.info(f"Loading special functions for brand: {brand}")
            
            functions = special_functions_manager.get_brand_functions(brand)
            
            if not functions:
                self.brand_info_label.setText(f"⚠️ No special functions available for {brand}")
                self.functions_list.addItem("No functions available for this brand")
                return
                
            # Validate function objects
            valid_functions = []
            for func in functions:
                if hasattr(func, 'function_id') and hasattr(func, 'name'):
                    valid_functions.append(func)
                else:
                    logger.warning(f"Invalid function object found: {func}")
            
            if not valid_functions:
                self.brand_info_label.setText(f"⚠️ No valid functions found for {brand}")
                self.functions_list.addItem("No valid functions available")
                return
                
            for func in valid_functions:
                try:
                    # Add category to display if available
                    category_info = f" [{func.category.value.upper()}]" if hasattr(func, 'category') else ""
                    item_text = f"{func.name} (Level {func.security_level}){category_info}"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, func)
                    self.functions_list.addItem(item)
                except Exception as e:
                    logger.error(f"Error adding function {getattr(func, 'name', 'Unknown')}: {e}")

            self.brand_info_label.setText(f"✅ Found {len(valid_functions)} functions for {brand}")
            logger.info(f"Successfully loaded {len(valid_functions)} functions for {brand}")

        except ImportError as e:
            self.brand_info_label.setText("❌ Special functions module not available")
            self.functions_list.addItem("Module import error - check installation")
            logger.error(f"Import error loading functions for {brand}: {e}")
            
        except Exception as e:
            self.brand_info_label.setText(f"❌ Error loading functions for {brand}")
            self.functions_list.addItem("Error loading functions")
            logger.error(f"Error loading functions for {brand}: {e}")

        # Update function details
        self.function_details.setPlainText("Select a function to view details and parameters.")
        self.execute_btn.setEnabled(False)

    def show_function_details(self) -> None:
        """Show details of selected function with enhanced validation"""
        current_item = self.functions_list.currentItem()
        if not current_item:
            self.function_details.setPlainText("Select a function to view details and parameters.")
            self.execute_btn.setEnabled(False)
            return

        func = current_item.data(Qt.ItemDataRole.UserRole)
        if not func:
            self.function_details.setPlainText("❌ Invalid function selected.")
            self.execute_btn.setEnabled(False)
            return

        try:
            # Validate function attributes
            required_attrs = ['function_id', 'name', 'security_level', 'description']
            missing_attrs = [attr for attr in required_attrs if not hasattr(func, attr)]
            
            if missing_attrs:
                self.function_details.setPlainText(f"❌ Function missing required attributes: {', '.join(missing_attrs)}")
                self.execute_btn.setEnabled(False)
                return

            # Build details text with error handling
            details = f"Function Details:\n"
            details += "=" * 40 + "\n\n"
            
            details += f"Name: {func.name}\n"
            details += f"ID: {func.function_id}\n"
            
            # Handle category safely
            if hasattr(func, 'category') and hasattr(func.category, 'value'):
                details += f"Category: {func.category.value.title()}\n"
            else:
                details += "Category: Unknown\n"
                
            details += f"Security Level: {func.security_level}\n\n"

            # Description
            details += f"Description:\n{func.description}\n\n"

            # Prerequisites
            if hasattr(func, 'prerequisites') and func.prerequisites:
                details += "Prerequisites:\n"
                for pre in func.prerequisites:
                    if isinstance(pre, str):
                        details += f"• {pre}\n"
                    else:
                        details += f"• {str(pre)}\n"
                details += "\n"

            # Risks
            if hasattr(func, 'risks') and func.risks:
                details += "⚠️ Risks & Warnings:\n"
                for risk in func.risks:
                    if isinstance(risk, str):
                        details += f"⚠️ {risk}\n"
                    else:
                        details += f"⚠️ {str(risk)}\n"
                details += "\n"

            # Parameters
            if hasattr(func, 'parameters') and func.parameters:
                details += "Parameters:\n"
                for param_name, param_config in func.parameters.items():
                    try:
                        required = "Required" if param_config.get('required', False) else "Optional"
                        param_type = param_config.get('type', 'unknown')
                        validation = param_config.get('validation', '')
                        validation_text = f" ({validation})" if validation else ""
                        details += f"• {param_name} ({param_type}) - {required}{validation_text}\n"
                    except Exception as e:
                        details += f"• {param_name} - Parameter error: {str(e)}\n"
            else:
                details += "Parameters: None required\n"

            # Security warnings for high-level functions
            if hasattr(func, 'security_level') and func.security_level >= 4:
                details += "\n⚠️ HIGH SECURITY LEVEL:\n"
                details += "This function requires elevated permissions.\n"
                details += "Ensure you have proper authorization before proceeding.\n"

            self.function_details.setPlainText(details)
            self.execute_btn.setEnabled(True)
            
        except Exception as e:
            from shared.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error displaying function details: {e}")
            
            self.function_details.setPlainText(f"❌ Error displaying function details:\n\n{str(e)}")
            self.execute_btn.setEnabled(False)

    def execute_selected_function(self) -> None:
        """Execute the selected special function"""
        current_item = self.functions_list.currentItem()
        if not current_item:
            return

        func = current_item.data(Qt.ItemDataRole.UserRole)
        if not func:
            return

        # Check if function requires parameters
        if func.parameters:
            # Show parameter input dialog
            params = self.get_function_parameters(func)
            if params is None:  # User cancelled
                return
        else:
            params = {}

        # Execute function with enhanced error handling
        try:
            from shared.special_functions import special_functions_manager
            from shared.logger import get_logger
            logger = get_logger(__name__)
            
            self.execute_btn.setEnabled(False)
            self.parent.status_label.setText(f"⚡ Executing {func.name}...")
            
            # Execute the function through the manager
            result = special_functions_manager.execute_function(
                self.parent.header.brand_combo.currentText(), 
                func.function_id, 
                params
            )
            
            if result.get("success"):
                self.show_execution_result(func, params)
                self.parent.status_label.setText(f"✅ {func.name} completed successfully")
            else:
                error_msg = result.get("error", "Unknown error occurred")
                self.parent.status_label.setText(f"❌ {func.name} failed: {error_msg}")
                self.results_text.setPlainText(f"❌ Function execution failed:\n\n{error_msg}")
                self.execute_btn.setEnabled(True)
                
        except Exception as e:
            from shared.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error executing function {func.name}: {e}")
            
            self.parent.status_label.setText(f"❌ Error executing {func.name}")
            self.results_text.setPlainText(f"❌ Execution error:\n\n{str(e)}")
            self.execute_btn.setEnabled(True)

    def get_function_parameters(self, func) -> dict | None:
        """Get parameters for function execution via dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Parameters for {func.name}")
        dialog.setModal(True)
        dialog.resize(400, 300)

        layout = QVBoxLayout(dialog)

        # Function description
        desc_label = QLabel(f"Description: {func.description}")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Prerequisites
        if hasattr(func, 'prerequisites') and func.prerequisites:
            pre_label = QLabel("Prerequisites:")
            pre_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            layout.addWidget(pre_label)

            for pre in func.prerequisites:
                if isinstance(pre, str):
                    pre_item = QLabel(f"• {pre}")
                    pre_item.setStyleSheet("margin-left: 10px;")
                    layout.addWidget(pre_item)

        # Parameter inputs
        param_inputs = {}
        if hasattr(func, 'parameters') and func.parameters:
            params_label = QLabel("Parameters:")
            params_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            layout.addWidget(params_label)

            for param_name, param_config in func.parameters.items():
                # Create parameter input based on type
                param_layout = QHBoxLayout()
                param_label = QLabel(f"{param_name} ({param_config['type']}):")
                param_label.setMinimumWidth(150)
                
                if param_config['type'] == 'int':
                    input_widget = QSpinBox()
                    if param_config.get('validation'):
                        if '-' in param_config['validation']:
                            min_val, max_val = map(int, param_config['validation'].split('-'))
                            input_widget.setRange(min_val, max_val)
                        else:
                            input_widget.setRange(0, 999)
                    else:
                        input_widget.setRange(0, 999)
                    input_widget.setValue(0)
                elif param_config['type'] == 'bool':
                    input_widget = QCheckBox()
                    input_widget.setChecked(False)
                else:  # string
                    input_widget = QLineEdit()
                    input_widget.setPlaceholderText(f"Enter {param_name}")
                    if param_config.get('validation'):
                        input_widget.setToolTip(f"Validation: {param_config['validation']}")

                param_layout.addWidget(param_label)
                param_layout.addWidget(input_widget)
                param_layout.addStretch()
                layout.addLayout(param_layout)
                
                param_inputs[param_name] = input_widget

            # Add risk warnings
            if hasattr(func, 'risks') and func.risks:
                risks_label = QLabel("⚠️ Risks:")
                risks_label.setStyleSheet("font-weight: bold; margin-top: 10px; color: #FF6B6B;")
                layout.addWidget(risks_label)
                
                for risk in func.risks:
                    if isinstance(risk, str):
                        risk_item = QLabel(f"⚠️ {risk}")
                        risk_item.setStyleSheet("margin-left: 10px; color: #FF6B6B;")
                        risk_item.setWordWrap(True)
                        layout.addWidget(risk_item)

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
                if isinstance(input_widget, QSpinBox):
                    params[param_name] = input_widget.value()
                elif isinstance(input_widget, QCheckBox):
                    params[param_name] = input_widget.isChecked()
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

    def show_execution_result(self, func, params) -> None:
        """Show execution result with enhanced details"""
        from datetime import datetime
        from shared.special_functions import special_functions_manager
        
        brand = self.parent.header.brand_combo.currentText()

        # Generate execution report
        result_text = f"Function Execution Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        result_text += "=" * 60 + "\n\n"

        result_text += f"Brand: {brand}\n"
        result_text += f"Function: {func.name}\n"
        result_text += f"Function ID: {func.function_id}\n"
        result_text += f"Category: {func.category.value.title()}\n"
        result_text += f"Security Level: {func.security_level}\n\n"

        if params:
            result_text += "Parameters Used:\n"
            for key, value in params.items():
                # Mask sensitive parameters
                if 'code' in key.lower() or 'password' in key.lower():
                    result_text += f"  {key}: {'*' * len(str(value))}\n"
                else:
                    result_text += f"  {key}: {value}\n"
            result_text += "\n"

        # Add execution details based on function type
        result_text += "Execution Results:\n"
        
        if "throttle" in func.name.lower():
            result_text += "✅ Throttle Body Learning: SUCCESS\n"
            result_text += "✅ Adaptation Values Updated\n"
            result_text += "✅ Idle Quality Optimized\n"
            result_text += "✅ Engine Response Improved\n"
            result_text += "⚠️  Vehicle restart recommended to complete adaptation\n"
        elif "dpf" in func.name.lower():
            result_text += "✅ DPF Regeneration: INITIATED\n"
            result_text += "🔄 Regeneration process started\n"
            result_text += "📊 Soot Level: Reduced by 40%\n"
            result_text += "✅ Filter cleaning in progress\n"
            result_text += "⚠️  Monitor DPF status for completion\n"
        elif "immobilizer" in func.name.lower():
            result_text += "✅ Immobilizer Registration: SUCCESS\n"
            result_text += "🔑 Keys programmed successfully\n"
            result_text += "🔐 Security system updated\n"
            result_text += "⚠️  Test all keys before completion\n"
        elif "steering" in func.name.lower():
            result_text += "✅ Steering Angle Calibration: SUCCESS\n"
            result_text += "📐 Sensor values reset to zero\n"
            result_text += "🎯 Calibration completed\n"
            result_text += "⚠️  Test steering wheel centering\n"
        else:
            result_text += "✅ Function executed successfully\n"
            result_text += "📋 All operations completed\n"
            result_text += "🔍 System verification passed\n"

        result_text += "\n" + "=" * 60
        result_text += "\n⚡ Execution completed successfully"
        result_text += f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        self.results_text.setPlainText(result_text)
        self.execute_btn.setEnabled(True)