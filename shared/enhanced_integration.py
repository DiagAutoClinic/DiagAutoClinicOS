#!/usr/bin/env python3
"""
AutoDiag Pro - Professional 25-Brand Diagnostic Suite v2.0
Complete Integration with Special Functions, Calibrations, and Security
"""

import sys
import os
import logging
from typing import Dict, List

# Security: Import validation
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

# Security modules
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QPushButton, QLabel, QComboBox, QTabWidget, QFrame, QGroupBox,
    QTableWidget, QTableWidgetItem, QProgressBar, QTextEdit, QLineEdit,
    QHeaderView, QMessageBox, QSplitter, QScrollArea, QCheckBox,
    QInputDialog, QDialog, QFormLayout, QFileDialog, QListWidget,
    QListWidgetItem, QStackedWidget, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, QSettings
from PyQt6.QtGui import QFont, QPalette, QColor

# Import shared modules
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared'))
if os.path.exists(shared_path):
    sys.path.append(shared_path)

try:
    from style_manager import StyleManager
    from brand_database import get_brand_list, get_brand_info
    from dtc_database import DTCDatabase
    from vin_decoder import VINDecoder
    from device_handler import DeviceHandler
    from security_manager import security_manager, SecurityLevel, UserRole
    from special_functions import special_functions_manager, FunctionCategory, SpecialFunction
    from calibrations_reset import calibrations_resets_manager, ResetType, CalibrationProcedure
except ImportError as e:
    logging.error(f"Failed to import modules: {e}")
    sys.exit(1)

logger = logging.getLogger(__name__)

class LoginDialog(QDialog):
    """Secure login dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AutoDiag Pro - Secure Login")
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🔒 AutoDiag Pro Login")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Form
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.attempt_login)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(login_btn)
        button_layout.addWidget(cancel_btn)
        
        # Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: red;")
        
        layout.addWidget(title)
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def attempt_login(self):
        """Attempt user login"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.status_label.setText("Username and password required")
            return
        
        success, message = security_manager.authenticate_user(username, password)
        
        if success:
            self.accept()
        else:
            self.status_label.setText(message)

class AutoDiagPro(QMainWindow):
    """Enhanced AutoDiag Professional with complete feature set"""
    
    def __init__(self):
        super().__init__()
        
        # Security first - require login
        if not self.secure_login():
            sys.exit(1)  # Exit if login failed
        
        # Initialize managers
        self.dtc_database = DTCDatabase()
        self.vin_decoder = VINDecoder()
        self.special_functions_manager = special_functions_manager
        self.calibrations_resets_manager = calibrations_resets_manager
        
        # Connect security managers
        self.special_functions_manager.security_manager = security_manager
        self.calibrations_resets_manager.security_manager = security_manager
        
        # UI State
        self.selected_brand = "Toyota"
        self.connected = False
        
        # Initialize UI
        self.init_ui()
        
        # Apply security theme
        try:
            self.style_manager.set_theme("security")
        except Exception as e:
            logger.warning(f"Theme application failed: {e}")
    
    def secure_login(self) -> bool:
        """Handle secure user login"""
        login_dialog = LoginDialog()
        result = login_dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            logger.info(f"User logged in: {security_manager.current_user}")
            return True
        else:
            logger.warning("Login cancelled or failed")
            return False
    
    def init_ui(self):
        """Initialize complete user interface"""
        self.setWindowTitle("AutoDiag Pro - Secure Professional Diagnostics")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create header with user info
        self.create_user_header(main_layout)
        
        # Create main tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create all tabs
        self.create_dashboard_tab()
        self.create_diagnostics_tab()
        self.create_live_data_tab()
        self.create_special_functions_tab()
        self.create_calibrations_resets_tab()
        self.create_advanced_tab()
        self.create_security_tab()
        
        # Create status bar
        self.create_status_bar()
        
        self.show()
    
    def create_user_header(self, layout):
        """Create header with user information and security status"""
        header_widget = QWidget()
        header_widget.setMaximumHeight(80)
        header_layout = QHBoxLayout(header_widget)
        
        # User info
        user_info = security_manager.get_user_info()
        user_label = QLabel(f"👤 {user_info.get('full_name', 'Unknown')} "
                          f"| 🔐 {user_info.get('security_level', 'BASIC')}")
        user_label.setProperty("class", "user-info")
        
        # Title
        title_label = QLabel("AutoDiag Pro - Secure Diagnostics")
        title_label.setProperty("class", "title")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # Brand selector
        brand_layout = QHBoxLayout()
        brand_label = QLabel("Vehicle Brand:")
        self.brand_combo = QComboBox()
        
        try:
            brands = get_brand_list()
            self.brand_combo.addItems(brands)
            self.brand_combo.setCurrentText(self.selected_brand)
            self.brand_combo.currentTextChanged.connect(self.on_brand_changed)
        except Exception as e:
            logger.error(f"Failed to load brands: {e}")
        
        brand_layout.addWidget(brand_label)
        brand_layout.addWidget(self.brand_combo)
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setProperty("class", "danger")
        logout_btn.clicked.connect(self.secure_logout)
        
        header_layout.addWidget(user_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addLayout(brand_layout)
        header_layout.addWidget(logout_btn)
        
        layout.addWidget(header_widget)
    
    def create_special_functions_tab(self):
        """Create comprehensive special functions tab"""
        functions_tab = QWidget()
        layout = QVBoxLayout(functions_tab)
        
        # Header
        header_label = QLabel("🔧 Special Functions - Brand Specific")
        header_label.setProperty("class", "tab-header")
        
        # Brand selection
        brand_layout = QHBoxLayout()
        brand_layout.addWidget(QLabel("Select Brand:"))
        self.sf_brand_combo = QComboBox()
        self.sf_brand_combo.addItems(get_brand_list())
        self.sf_brand_combo.setCurrentText(self.selected_brand)
        self.sf_brand_combo.currentTextChanged.connect(self.update_special_functions_list)
        brand_layout.addWidget(self.sf_brand_combo)
        brand_layout.addStretch()
        
        # Main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Functions list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(QLabel("Available Special Functions:"))
        self.special_functions_list = QListWidget()
        self.special_functions_list.itemClicked.connect(self.on_special_function_selected)
        left_layout.addWidget(self.special_functions_list)
        
        # Right panel - Function details and execution
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Function details
        self.sf_details_group = QGroupBox("Function Details")
        sf_details_layout = QVBoxLayout(self.sf_details_group)
        
        self.sf_name_label = QLabel("Select a function to view details")
        self.sf_name_label.setProperty("class", "function-name")
        
        self.sf_description = QTextEdit()
        self.sf_description.setReadOnly(True)
        self.sf_description.setMaximumHeight(100)
        
        self.sf_security_label = QLabel("Security Level: --")
        self.sf_security_label.setProperty("class", "security-info")
        
        sf_details_layout.addWidget(self.sf_name_label)
        sf_details_layout.addWidget(self.sf_description)
        sf_details_layout.addWidget(self.sf_security_label)
        
        # Parameters section
        self.sf_params_group = QGroupBox("Function Parameters")
        self.sf_params_layout = QVBoxLayout(self.sf_params_group)
        self.sf_params_widget = QWidget()
        self.sf_params_layout.addWidget(self.sf_params_widget)
        
        # Execute section
        execute_layout = QHBoxLayout()
        self.sf_execute_btn = QPushButton("Execute Special Function")
        self.sf_execute_btn.setProperty("class", "primary")
        self.sf_execute_btn.clicked.connect(self.execute_special_function)
        self.sf_execute_btn.setEnabled(False)
        
        execute_layout.addWidget(self.sf_execute_btn)
        execute_layout.addStretch()
        
        # Results
        self.sf_results = QTextEdit()
        self.sf_results.setReadOnly(True)
        self.sf_results.setPlaceholderText("Execution results will appear here...")
        
        right_layout.addWidget(self.sf_details_group)
        right_layout.addWidget(self.sf_params_group)
        right_layout.addLayout(execute_layout)
        right_layout.addWidget(QLabel("Execution Results:"))
        right_layout.addWidget(self.sf_results)
        
        content_splitter.addWidget(left_panel)
        content_splitter.addWidget(right_panel)
        content_splitter.setSizes([300, 700])
        
        layout.addWidget(header_label)
        layout.addLayout(brand_layout)
        layout.addWidget(content_splitter)
        
        self.tab_widget.addTab(functions_tab, "🔧 Special Functions")
        
        # Initial update
        self.update_special_functions_list()
    
    def create_calibrations_resets_tab(self):
        """Create comprehensive calibrations and resets tab"""
        calib_tab = QWidget()
        layout = QVBoxLayout(calib_tab)
        
        # Header
        header_label = QLabel("⚙ Calibrations & Resets - Professional Procedures")
        header_label.setProperty("class", "tab-header")
        
        # Brand selection
        brand_layout = QHBoxLayout()
        brand_layout.addWidget(QLabel("Select Brand:"))
        self.cr_brand_combo = QComboBox()
        self.cr_brand_combo.addItems(get_brand_list())
        self.cr_brand_combo.setCurrentText(self.selected_brand)
        self.cr_brand_combo.currentTextChanged.connect(self.update_calibrations_list)
        brand_layout.addWidget(self.cr_brand_combo)
        brand_layout.addStretch()
        
        # Main content
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Procedures list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(QLabel("Available Procedures:"))
        self.calibrations_list = QListWidget()
        self.calibrations_list.itemClicked.connect(self.on_calibration_selected)
        left_layout.addWidget(self.calibrations_list)
        
        # Right panel - Procedure details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Procedure details
        self.cr_details_group = QGroupBox("Procedure Details")
        cr_details_layout = QVBoxLayout(self.cr_details_group)
        
        self.cr_name_label = QLabel("Select a procedure to view details")
        self.cr_name_label.setProperty("class", "procedure-name")
        
        self.cr_description = QTextEdit()
        self.cr_description.setReadOnly(True)
        self.cr_description.setMaximumHeight(80)
        
        info_layout = QHBoxLayout()
        self.cr_duration_label = QLabel("Duration: --")
        self.cr_security_label = QLabel("Security Level: --")
        self.cr_type_label = QLabel("Type: --")
        
        info_layout.addWidget(self.cr_duration_label)
        info_layout.addWidget(self.cr_security_label)
        info_layout.addWidget(self.cr_type_label)
        info_layout.addStretch()
        
        cr_details_layout.addWidget(self.cr_name_label)
        cr_details_layout.addWidget(self.cr_description)
        cr_details_layout.addLayout(info_layout)
        
        # Prerequisites
        self.cr_prereq_group = QGroupBox("Prerequisites")
        self.cr_prereq_list = QTextEdit()
        self.cr_prereq_list.setReadOnly(True)
        self.cr_prereq_list.setMaximumHeight(100)
        cr_prereq_layout = QVBoxLayout(self.cr_prereq_group)
        cr_prereq_layout.addWidget(self.cr_prereq_list)
        
        # Steps
        self.cr_steps_group = QGroupBox("Procedure Steps")
        self.cr_steps_list = QTextEdit()
        self.cr_steps_list.setReadOnly(True)
        cr_steps_layout = QVBoxLayout(self.cr_steps_group)
        cr_steps_layout.addWidget(self.cr_steps_list)
        
        # Execute
        execute_layout = QHBoxLayout()
        self.cr_execute_btn = QPushButton("Execute Procedure")
        self.cr_execute_btn.setProperty("class", "primary")
        self.cr_execute_btn.clicked.connect(self.execute_calibration)
        self.cr_execute_btn.setEnabled(False)
        
        execute_layout.addWidget(self.cr_execute_btn)
        execute_layout.addStretch()
        
        # Results
        self.cr_results = QTextEdit()
        self.cr_results.setReadOnly(True)
        self.cr_results.setPlaceholderText("Procedure results will appear here...")
        
        right_layout.addWidget(self.cr_details_group)
        right_layout.addWidget(self.cr_prereq_group)
        right_layout.addWidget(self.cr_steps_group)
        right_layout.addLayout(execute_layout)
        right_layout.addWidget(QLabel("Execution Results:"))
        right_layout.addWidget(self.cr_results)
        
        content_splitter.addWidget(left_panel)
        content_splitter.addWidget(right_panel)
        content_splitter.setSizes([300, 700])
        
        layout.addWidget(header_label)
        layout.addLayout(brand_layout)
        layout.addWidget(content_splitter)
        
        self.tab_widget.addTab(calib_tab, "⚙ Calibrations & Resets")
        
        # Initial update
        self.update_calibrations_list()
    
    def create_security_tab(self):
        """Create security management and audit tab"""
        security_tab = QWidget()
        layout = QVBoxLayout(security_tab)
        
        # Header
        header_label = QLabel("🔒 Security & Audit")
        header_label.setProperty("class", "tab-header")
        
        # Security status
        status_group = QGroupBox("Security Status")
        status_layout = QVBoxLayout(status_group)
        
        user_info = security_manager.get_user_info()
        status_text = f"""
        Current User: {user_info.get('full_name', 'Unknown')}
        Username: {user_info.get('username', 'Unknown')}
        Security Level: {user_info.get('security_level', 'BASIC')}
        Role: {user_info.get('role', 'technician')}
        Session Expires: {self.format_timestamp(user_info.get('session_expiry', 0))}
        """
        
        self.security_status = QTextEdit()
        self.security_status.setPlainText(status_text.strip())
        self.security_status.setReadOnly(True)
        
        status_layout.addWidget(self.security_status)
        
        # Security controls
        controls_group = QGroupBox("Security Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        refresh_btn = QPushButton("Refresh Security Status")
        refresh_btn.clicked.connect(self.update_security_status)
        
        audit_btn = QPushButton("View Audit Log")
        audit_btn.clicked.connect(self.show_audit_log)
        
        elevate_btn = QPushButton("Elevate Security")
        elevate_btn.clicked.connect(self.elevate_security)
        
        controls_layout.addWidget(refresh_btn)
        controls_layout.addWidget(audit_btn)
        controls_layout.addWidget(elevate_btn)
        controls_layout.addStretch()
        
        # Quick security check
        check_group = QGroupBox("Quick Security Check")
        check_layout = QVBoxLayout(check_group)
        
        self.security_check_result = QTextEdit()
        self.security_check_result.setReadOnly(True)
        
        check_btn = QPushButton("Run Security Check")
        check_btn.clicked.connect(self.run_security_check)
        
        check_layout.addWidget(self.security_check_result)
        check_layout.addWidget(check_btn)
        
        layout.addWidget(header_label)
        layout.addWidget(status_group)
        layout.addWidget(controls_group)
        layout.addWidget(check_group)
        layout.addStretch()
        
        self.tab_widget.addTab(security_tab, "🔒 Security")
    
    def update_special_functions_list(self):
        """Update special functions list for current brand"""
        brand = self.sf_brand_combo.currentText()
        functions = self.special_functions_manager.get_brand_functions(brand)
        
        self.special_functions_list.clear()
        
        for function in functions:
            item = QListWidgetItem(f"🔧 {function.name}")
            item.setData(Qt.ItemDataRole.UserRole, function.function_id)
            self.special_functions_list.addItem(item)
        
        # Clear details
        self.sf_name_label.setText("Select a function to view details")
        self.sf_description.clear()
        self.sf_security_label.setText("Security Level: --")
        self.sf_execute_btn.setEnabled(False)
        
        # Clear parameters
        self.clear_parameters()
    
    def on_special_function_selected(self, item):
        """Handle special function selection"""
        brand = self.sf_brand_combo.currentText()
        function_id = item.data(Qt.ItemDataRole.UserRole)
        function = self.special_functions_manager.get_function(brand, function_id)
        
        if not function:
            return
        
        # Update details
        self.sf_name_label.setText(f"🔧 {function.name}")
        self.sf_description.setText(function.description)
        self.sf_security_label.setText(f"Security Level: {function.security_level} "
                                     f"(Current: {security_manager.get_security_level().name})")
        
        # Create parameter inputs
        self.create_parameter_inputs(function)
        
        # Check security and enable button
        has_clearance = security_manager.check_security_clearance(
            SecurityLevel(function.security_level))
        self.sf_execute_btn.setEnabled(has_clearance)
        
        if not has_clearance:
            self.sf_results.setPlainText(
                f"❌ Insufficient security clearance for this function.\n"
                f"Required: Level {function.security_level}\n"
                f"Current: Level {security_manager.get_security_level().value}")
    
    def create_parameter_inputs(self, function: SpecialFunction):
        """Create parameter input fields for function"""
        # Clear existing parameters
        self.clear_parameters()
        
        if not function.parameters:
            no_params_label = QLabel("No parameters required for this function.")
            self.sf_params_layout.addWidget(no_params_label)
            return
        
        # Create input fields for each parameter
        self.parameter_widgets = {}
        param_widget = QWidget()
        param_layout = QGridLayout(param_widget)
        
        row = 0
        for param_name, param_config in function.parameters.items():
            label = QLabel(f"{param_name}:")
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
        
        self.sf_params_layout.addWidget(param_widget)
    
    def clear_parameters(self):
        """Clear parameter input section"""
        # Remove existing parameter widgets
        for i in reversed(range(self.sf_params_layout.count())):
            widget = self.sf_params_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
    
    def execute_special_function(self):
        """Execute selected special function"""
        brand = self.sf_brand_combo.currentText()
        current_item = self.special_functions_list.currentItem()
        
        if not current_item:
            self.sf_results.setPlainText("❌ No function selected")
            return
        
        function_id = current_item.data(Qt.ItemDataRole.UserRole)
        
        # Collect parameters
        parameters = {}
        for param_name, widget in self.parameter_widgets.items():
            if isinstance(widget, QLineEdit):
                parameters[param_name] = widget.text()
            elif isinstance(widget, QCheckBox):
                parameters[param_name] = widget.isChecked()
        
        # Execute function
        self.sf_results.setPlainText("🔄 Executing function...")
        
        result = self.special_functions_manager.execute_function(
            brand, function_id, parameters)
        
        # Display results
        if result.get('success'):
            result_text = "✅ Function executed successfully!\n\n"
            for key, value in result.items():
                if key != 'success':
                    result_text += f"{key}: {value}\n"
        else:
            result_text = f"❌ Function execution failed:\n{result.get('error', 'Unknown error')}"
        
        self.sf_results.setPlainText(result_text)
    
    def update_calibrations_list(self):
        """Update calibrations list for current brand"""
        brand = self.cr_brand_combo.currentText()
        procedures = self.calibrations_resets_manager.get_brand_procedures(brand)
        
        self.calibrations_list.clear()
        
        for procedure in procedures:
            item = QListWidgetItem(f"⚙ {procedure.name}")
            item.setData(Qt.ItemDataRole.UserRole, procedure.procedure_id)
            self.calibrations_list.addItem(item)
        
        # Clear details
        self.clear_calibration_details()
    
    def on_calibration_selected(self, item):
        """Handle calibration procedure selection"""
        brand = self.cr_brand_combo.currentText()
        procedure_id = item.data(Qt.ItemDataRole.UserRole)
        procedure = self.calibrations_resets_manager.get_procedure(brand, procedure_id)
        
        if not procedure:
            return
        
        # Update details
        self.cr_name_label.setText(f"⚙ {procedure.name}")
        self.cr_description.setText(procedure.description)
        self.cr_duration_label.setText(f"Duration: {procedure.duration}")
        self.cr_security_label.setText(
            f"Security Level: {procedure.security_level} "
            f"(Current: {security_manager.get_security_level().name})")
        self.cr_type_label.setText(f"Type: {procedure.reset_type.value}")
        
        # Update prerequisites
        prereq_text = "\n".join([f"• {prereq}" for prereq in procedure.prerequisites])
        self.cr_prereq_list.setPlainText(prereq_text or "No prerequisites")
        
        # Update steps
        steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(procedure.steps)])
        self.cr_steps_list.setPlainText(steps_text)
        
        # Check security and enable button
        has_clearance = security_manager.check_security_clearance(
            SecurityLevel(procedure.security_level))
        self.cr_execute_btn.setEnabled(has_clearance)
        
        if not has_clearance:
            self.cr_results.setPlainText(
                f"❌ Insufficient security clearance for this procedure.\n"
                f"Required: Level {procedure.security_level}\n"
                f"Current: Level {security_manager.get_security_level().value}")
    
    def clear_calibration_details(self):
        """Clear calibration procedure details"""
        self.cr_name_label.setText("Select a procedure to view details")
        self.cr_description.clear()
        self.cr_duration_label.setText("Duration: --")
        self.cr_security_label.setText("Security Level: --")
        self.cr_type_label.setText("Type: --")
        self.cr_prereq_list.clear()
        self.cr_steps_list.clear()
        self.cr_execute_btn.setEnabled(False)
        self.cr_results.clear()
    
    def execute_calibration(self):
        """Execute selected calibration procedure"""
        brand = self.cr_brand_combo.currentText()
        current_item = self.calibrations_list.currentItem()
        
        if not current_item:
            self.cr_results.setPlainText("❌ No procedure selected")
            return
        
        procedure_id = current_item.data(Qt.ItemDataRole.UserRole)
        
        self.cr_results.setPlainText("🔄 Executing procedure...")
        
        result = self.calibrations_resets_manager.execute_procedure(brand, procedure_id)
        
        # Display results
        if result.get('success'):
            result_text = "✅ Procedure executed successfully!\n\n"
            for key, value in result.items():
                if key != 'success':
                    if isinstance(value, list):
                        result_text += f"{key}:\n"
                        for item in value:
                            result_text += f"  • {item}\n"
                    elif isinstance(value, dict):
                        result_text += f"{key}:\n"
                        for k, v in value.items():
                            result_text += f"  {k}: {v}\n"
                    else:
                        result_text += f"{key}: {value}\n"
        else:
            result_text = f"❌ Procedure execution failed:\n{result.get('error', 'Unknown error')}"
        
        self.cr_results.setPlainText(result_text)
    
    def update_security_status(self):
        """Update security status display"""
        user_info = security_manager.get_user_info()
        status_text = f"""
        Current User: {user_info.get('full_name', 'Unknown')}
        Username: {user_info.get('username', 'Unknown')}
        Security Level: {user_info.get('security_level', 'BASIC')}
        Role: {user_info.get('role', 'technician')}
        Session Expires: {self.format_timestamp(user_info.get('session_expiry', 0))}
        """
        self.security_status.setPlainText(status_text.strip())
    
    def show_audit_log(self):
        """Display security audit log"""
        audit_log = security_manager.get_audit_log(50)
        
        log_text = "🔒 Security Audit Log (Last 50 Events)\n\n"
        for event in audit_log:
            log_text += f"[{self.format_timestamp(event['timestamp'])}] {event['event_type']} - {event['username']}\n"
            if event['details']:
                log_text += f"    Details: {event['details']}\n"
            log_text += "\n"
        
        QMessageBox.information(self, "Security Audit Log", log_text)
    
    def run_security_check(self):
        """Run comprehensive security check"""
        checks = []
        
        # Check session validity
        if security_manager.validate_session():
            checks.append("✅ Session is valid")
        else:
            checks.append("❌ Session is invalid or expired")
        
        # Check security level
        current_level = security_manager.get_security_level()
        checks.append(f"✅ Current security level: {current_level.name}")
        
        # Check special functions access
        brand = self.sf_brand_combo.currentText()
        functions = self.special_functions_manager.get_brand_functions(brand)
        accessible = sum(1 for f in functions if 
                        security_manager.check_security_clearance(SecurityLevel(f.security_level)))
        checks.append(f"✅ Accessible special functions: {accessible}/{len(functions)}")
        
        self.security_check_result.setPlainText("\n".join(checks))
    
    def elevate_security(self):
        """Elevate security level"""
        username, ok = QInputDialog.getText(self, "Security Elevation", 
                                          "Enter username:")
        if not ok or not username:
            return
        
        password, ok = QInputDialog.getText(self, "Security Elevation",
                                          "Enter password:", 
                                          QLineEdit.EchoMode.Password)
        if not ok or not password:
            return
        
        required_level = SecurityLevel.DEALER  # Example required level
        success, message = security_manager.elevate_security(
            username, password, required_level)
        
        if success:
            QMessageBox.information(self, "Security Elevated", message)
            self.update_security_status()
        else:
            QMessageBox.warning(self, "Security Elevation Failed", message)
    
    def secure_logout(self):
        """Handle secure logout"""
        reply = QMessageBox.question(self, "Logout", 
                                   "Are you sure you want to logout?",
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            security_manager.logout()
            self.close()
    
    def format_timestamp(self, timestamp: float) -> str:
        """Format timestamp for display"""
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    
    def on_brand_changed(self, brand):
        """Handle brand selection change"""
        self.selected_brand = brand
        # Update any brand-specific displays
    
    # Add other existing methods (create_dashboard_tab, create_diagnostics_tab, etc.)
    # These would be similar to your existing implementation but integrated with security
    
    def closeEvent(self, event):
        """Secure cleanup on close"""
        security_manager.logout()
        logger.info("AutoDiag Pro closed securely")
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("AutoDiag Pro Secure")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("SecureAutoClinic")
    
    try:
        window = AutoDiagPro()
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"Application crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
