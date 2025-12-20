#!/usr/bin/env python3
"""
Tier Acknowledgement Dialog for DACOS
User must acknowledge risks and responsibilities for higher tiers
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QMessageBox, QCheckBox, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

logger = logging.getLogger(__name__)

class TierAcknowledgementDialog(QDialog):
    """Dialog for user acknowledgement of tier risks and responsibilities"""

    def __init__(self, tier, brand_name=None, operation=None, parent=None):
        super().__init__(parent)
        self.tier = tier
        self.brand_name = brand_name
        self.operation = operation

        self.setWindowTitle(f"DACOS Tier {tier.value} Acknowledgement Required")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        self.resize(700, 600)

        # Import tier system
        try:
            from shared.tier_system import tier_system
            self.tier_system = tier_system
        except ImportError:
            self.tier_system = None

        self.init_ui()

    def init_ui(self):
        """Initialize the acknowledgement dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel(f"Tier {self.tier.value}: {self.tier_system.TIER_DEFINITIONS[self.tier]['name']}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 16, QFont.Weight.Bold)
        title.setFont(title_font)
        layout.addWidget(title)

        # Risk warning
        risk_label = QLabel("⚠️ AUTHORITY ACKNOWLEDGEMENT REQUIRED")
        risk_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        risk_label.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 14pt;")
        layout.addWidget(risk_label)

        # Context
        context_text = ""
        if self.brand_name:
            context_text += f"Brand: {self.brand_name}\n"
        if self.operation:
            context_text += f"Operation: {self.operation}\n"
        context_text += f"Tier: {self.tier.value} ({self.tier_system.TIER_DEFINITIONS[self.tier]['name']})"

        context_label = QLabel(context_text)
        context_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        context_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(context_label)

        # Scrollable acknowledgement text
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(200)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Acknowledgement text
        ack_text = self.get_acknowledgement_text()
        ack_label = QLabel(ack_text)
        ack_label.setWordWrap(True)
        ack_label.setStyleSheet("font-size: 11pt; line-height: 1.4;")
        scroll_layout.addWidget(ack_label)

        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # Checkbox for acknowledgement
        self.ack_checkbox = QCheckBox("I have read and understand the above acknowledgement")
        self.ack_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 12pt;
                font-weight: bold;
                color: #ff6b6b;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        layout.addWidget(self.ack_checkbox)

        # Additional checkboxes for Tier 5
        self.additional_checkboxes = []
        if self.tier.value >= 5:
            legal_checkbox = QCheckBox("I accept full legal responsibility for all consequences")
            legal_checkbox.setStyleSheet("font-size: 11pt; color: #ff4444;")
            layout.addWidget(legal_checkbox)
            self.additional_checkboxes.append(legal_checkbox)

            technical_checkbox = QCheckBox("I declare technical competence for this operation")
            technical_checkbox.setStyleSheet("font-size: 11pt; color: #ff4444;")
            layout.addWidget(technical_checkbox)
            self.additional_checkboxes.append(technical_checkbox)

            jurisdiction_checkbox = QCheckBox("I confirm compliance with local jurisdiction regulations")
            jurisdiction_checkbox.setStyleSheet("font-size: 11pt; color: #ff4444;")
            layout.addWidget(jurisdiction_checkbox)
            self.additional_checkboxes.append(jurisdiction_checkbox)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        cancel_btn = QPushButton("Cancel Operation")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #777;
            }
        """)
        button_layout.addWidget(cancel_btn)

        accept_btn = QPushButton("I Accept Full Responsibility")
        accept_btn.clicked.connect(self.accept_acknowledgement)
        accept_btn.setDefault(True)
        accept_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5252;
            }
        """)
        button_layout.addWidget(accept_btn)

        layout.addLayout(button_layout)

    def get_acknowledgement_text(self):
        """Get the acknowledgement text for the current tier"""
        if not self.tier_system:
            return "Tier system not available."

        tier_info = self.tier_system.TIER_DEFINITIONS[self.tier]

        base_text = f"""
AUTHORITY GRANTED: {tier_info['security_authority']}

RISK FACTOR: {tier_info['risk_factor'].value}

CAPABILITIES INCLUDE:
{chr(10).join(f"• {cap}" for cap in tier_info['capabilities'])}

"""

        if self.tier.value >= 3:
            base_text += f"""
MANDATORY ACKNOWLEDGEMENT:

{tier_info['user_acknowledgement']}

"""

        if self.tier.value >= 4:
            base_text += """
PER-SESSION RESPONSIBILITY:
Each time you access this tier's capabilities, you accept full responsibility for:
• Correct execution of all operations
• Safety-critical system integrity
• Potential vehicle damage or unsafe conditions
• Recovery costs and dealer intervention requirements

"""

        if self.tier.value >= 5:
            base_text += """
EXTREME RISK WARNING:
This tier can permanently alter or disable vehicle systems.
There is NO UNDO function.
Incorrect use may violate regulations, create unsafe vehicles, or brick ECUs.

LEGAL REQUIREMENTS:
• You must have explicit authorization to perform these operations
• You accept all financial, legal, and safety consequences
• You confirm technical competence for raw CAN operations
• You acknowledge this may void vehicle warranties

"""

        base_text += """
DACOS does not promise safety. DACOS enforces clarity.
By proceeding, you accept that you are responsible for all consequences of your actions.
"""

        return base_text.strip()

    def accept_acknowledgement(self):
        """Handle acknowledgement acceptance"""
        if not self.ack_checkbox.isChecked():
            QMessageBox.warning(self, "Acknowledgement Required",
                              "You must check the acknowledgement box to proceed.")
            return

        # Check additional checkboxes for Tier 5
        if self.tier.value >= 5:
            for checkbox in self.additional_checkboxes:
                if not checkbox.isChecked():
                    QMessageBox.warning(self, "Complete Acknowledgement Required",
                                      "All acknowledgement checkboxes must be checked for Tier 5 access.")
                    return

        logger.info(f"User acknowledged Tier {self.tier.value} responsibilities for {self.brand_name or 'general access'}")
        self.accept()

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


def show_tier_acknowledgement(tier, brand_name=None, operation=None, parent=None):
    """Convenience function to show tier acknowledgement dialog"""
    dialog = TierAcknowledgementDialog(tier, brand_name, operation, parent)
    return dialog.exec() == QDialog.DialogCode.Accepted