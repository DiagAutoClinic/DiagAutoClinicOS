#!/usr/bin/env python3
"""
Security Module for AutoDiag Pro
Handles security management and audit functions
"""

import logging
import sys
import os

# Add project root to Python path to enable imports from shared directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QMessageBox, QInputDialog, QLineEdit

logger = logging.getLogger(__name__)

# Import shared modules
try:
    from shared.security_manager import security_manager, SecurityLevel
    SECURITY_MANAGER_AVAILABLE = True
except ImportError:
    SECURITY_MANAGER_AVAILABLE = False
    logger.warning("Security manager not available")


class SecurityManager:
    """Manages security-related UI operations"""

    def __init__(self, main_window):
        self.main_window = main_window

    def update_security_status(self):
        """Update security status display"""
        if not SECURITY_MANAGER_AVAILABLE:
            self.main_window.security_status.setPlainText("Security manager not available")
            return

        user_info = security_manager.get_user_info()
        status_text = f"""
Current User: {user_info.get('full_name', 'Unknown')}
Username: {user_info.get('username', 'Unknown')}
Security Level: {user_info.get('security_level', 'BASIC')}
Role: {user_info.get('role', 'technician')}
Session Expires: {self.format_timestamp(user_info.get('session_expiry', 0))}
        """
        self.main_window.security_status.setPlainText(status_text.strip())

    def show_audit_log(self):
        """Display security audit log"""
        if not SECURITY_MANAGER_AVAILABLE:
            QMessageBox.warning(self.main_window, "Audit Log", "Security manager not available")
            return

        audit_log = security_manager.get_audit_log(50)

        log_text = "🔒 Security Audit Log (Last 50 Events)\n\n"
        for event in audit_log:
            log_text += f"[{self.format_timestamp(event['timestamp'])}] {event['event_type']} - {event['username']}\n"
            if event['details']:
                log_text += f"    {event['details']}\n"
            log_text += "\n"

        QMessageBox.information(self.main_window, "Security Audit Log", log_text)

    def run_security_check(self):
        """Run comprehensive security check"""
        if not SECURITY_MANAGER_AVAILABLE:
            self.main_window.security_check_result.setPlainText("❌ Security manager not available")
            return

        checks = []

        if security_manager.validate_session():
            checks.append("✅ Session is valid")
        else:
            checks.append("❌ Session is invalid")

        current_level = security_manager.get_security_level()
        checks.append(f"✅ Current security level: {current_level.name}")

        brand = self.main_window.brand_combo.currentText()
        try:
            from shared.special_functions import special_functions_manager
            functions = special_functions_manager.get_brand_functions(brand)
            accessible = sum(1 for f in functions if
                            security_manager.check_security_clearance(SecurityLevel(f.security_level)))
            checks.append(f"✅ Accessible functions: {accessible}/{len(functions)}")
        except ImportError:
            checks.append("⚠️ Special functions not available for check")

        self.main_window.security_check_result.setPlainText("\n".join(checks))

    def elevate_security(self):
        """Elevate security level"""
        if not SECURITY_MANAGER_AVAILABLE:
            QMessageBox.warning(self.main_window, "Security Elevation", "Security manager not available")
            return

        username, ok = QInputDialog.getText(self.main_window, "Security Elevation", "Enter username:")
        if not ok or not username:
            return

        password, ok = QInputDialog.getText(self.main_window, "Security Elevation",
                                          "Enter password:",
                                          QLineEdit.EchoMode.Password)
        if not ok or not password:
            return

        required_level = SecurityLevel.DEALER
        success, message = security_manager.elevate_security(username, password, required_level)

        if success:
            QMessageBox.information(self.main_window, "Security Elevated", message)
            self.update_security_status()
        else:
            QMessageBox.warning(self.main_window, "Elevation Failed", message)

    def format_timestamp(self, timestamp: float) -> str:
        """Format timestamp for display"""
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")