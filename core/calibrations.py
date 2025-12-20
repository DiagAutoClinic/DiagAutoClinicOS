#!/usr/bin/env python3
"""
Calibrations Module for AutoDiag Pro
Handles calibrations and resets management and execution
"""

import logging
import sys
import os

# Add project root to Python path to enable imports from shared directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QListWidgetItem
from PyQt6.QtCore import Qt

logger = logging.getLogger(__name__)

# Import shared modules
try:
    from shared.calibrations_reset import calibrations_resets_manager, SecurityLevel
    CALIBRATIONS_AVAILABLE = True
except ImportError:
    CALIBRATIONS_AVAILABLE = False
    logger.warning("Calibrations manager not available")


class CalibrationsManager:
    """Manages calibrations and resets UI and execution"""

    def __init__(self, main_window):
        self.main_window = main_window

    def update_calibrations_list(self, brand):
        """Update calibrations list"""
        if not CALIBRATIONS_AVAILABLE:
            return

        procedures = calibrations_resets_manager.get_brand_procedures(brand)

        self.main_window.calibrations_list.clear()

        for procedure in procedures:
            item = QListWidgetItem(f"⚙️ {procedure.name}")
            item.setData(Qt.ItemDataRole.UserRole, procedure.procedure_id)
            self.main_window.calibrations_list.addItem(item)

        self.clear_calibration_details()

    def on_calibration_selected(self, item):
        """Handle calibration selection"""
        if not CALIBRATIONS_AVAILABLE:
            return

        brand = self.main_window.brand_combo.currentText()
        procedure_id = item.data(Qt.ItemDataRole.UserRole)
        procedure = calibrations_resets_manager.get_procedure(brand, procedure_id)

        if not procedure:
            return

        self.main_window.cr_name_label.setText(f"⚙️ {procedure.name}")
        self.main_window.cr_description.setText(procedure.description)
        self.main_window.cr_duration_label.setText(f"Duration: {procedure.duration}")
        self.main_window.cr_security_label.setText(f"Security: Level {procedure.security_level}")
        self.main_window.cr_type_label.setText(f"Type: {procedure.reset_type.value}")

        prereq_text = "\n".join([f"• {p}" for p in procedure.prerequisites])
        self.main_window.cr_prereq_list.setPlainText(prereq_text or "No prerequisites")

        steps_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(procedure.steps)])
        self.main_window.cr_steps_list.setPlainText(steps_text)

        has_clearance = self.main_window.security_manager.check_security_clearance(SecurityLevel(procedure.security_level))
        self.main_window.cr_execute_btn.setEnabled(has_clearance)

        if not has_clearance:
            self.main_window.cr_results.setPlainText(
                f"❌ Insufficient security clearance\n"
                f"Required: Level {procedure.security_level}")

    def clear_calibration_details(self):
        """Clear calibration details"""
        self.main_window.cr_name_label.setText("Select a procedure to view details")
        self.main_window.cr_description.clear()
        self.main_window.cr_duration_label.setText("Duration: --")
        self.main_window.cr_security_label.setText("Security Level: --")
        self.main_window.cr_type_label.setText("Type: --")
        self.main_window.cr_prereq_list.clear()
        self.main_window.cr_steps_list.clear()
        self.main_window.cr_execute_btn.setEnabled(False)
        self.main_window.cr_results.clear()

    def execute_calibration(self):
        """Execute calibration procedure"""
        if not CALIBRATIONS_AVAILABLE:
            self.main_window.cr_results.setPlainText("❌ Calibrations manager not available")
            return

        brand = self.main_window.brand_combo.currentText()
        current_item = self.main_window.calibrations_list.currentItem()

        if not current_item:
            self.main_window.cr_results.setPlainText("❌ No procedure selected")
            return

        procedure_id = current_item.data(Qt.ItemDataRole.UserRole)
        self.main_window.cr_results.setPlainText("⏳ Executing procedure...")

        result = calibrations_resets_manager.execute_procedure(brand, procedure_id)

        if result.get('success'):
            result_text = "✅ Procedure executed successfully!\n\n"
            for key, value in result.items():
                if key != 'success':
                    result_text += f"{key}: {value}\n"
        else:
            result_text = f"❌ Execution failed:\n{result.get('error', 'Unknown error')}"

        self.main_window.cr_results.setPlainText(result_text)