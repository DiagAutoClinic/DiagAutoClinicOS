#!/usr/bin/env python3
"""
Password Change Dialog for DiagAutoClinicOS
Forces password change on first login
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QIcon

logger = logging.getLogger(__name__)

class PasswordChangeDialog(QDialog):
    """Dialog for forcing password change on first login"""

    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle("DiagAutoClinicOS - Password Change Required")
        self.setModal(True)
        self.setMinimumSize(550, 450)
        self.resize(600, 500)

        self.init_ui()

    def init_ui(self):
        """Initialize the password change dialog UI"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("🔐 Password Change Required")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 20, QFont.Weight.Bold)
        title.setFont(title_font)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("You must change your password before proceeding.\n\nPassword Requirements:")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont("Segoe UI", 11)
        subtitle.setFont(subtitle_font)
        layout.addWidget(subtitle)

        # Requirements list
        requirements = QLabel(
            "• Minimum 12 characters\n"
            "• At least one uppercase letter\n"
            "• At least one lowercase letter\n"
            "• At least one number\n"
            "• At least one special character (!@#$%^&*)\n"
            "• Cannot be the same as default password"
        )
        requirements.setStyleSheet("color: #666; font-size: 10pt; margin-left: 20px;")
        layout.addWidget(requirements)

        # Username display
        username_layout = QVBoxLayout()
        username_label = QLabel(f"Username: {self.username}")
        username_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        username_label.setStyleSheet("font-weight: bold; color: #21F5C1;")
        username_layout.addWidget(username_label)
        layout.addLayout(username_layout)

        # New password
        new_password_layout = QVBoxLayout()
        new_password_label = QLabel("New Password:")
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setPlaceholderText("Enter new password")
        self.new_password_input.setMinimumHeight(35)
        self.new_password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #21F5C1;
                border-radius: 8px;
                background-color: #0D2323;
                color: #E8F4F2;
                font-size: 12pt;
            }
            QLineEdit:focus {
                border-color: #2AF5D1;
            }
        """)
        self.new_password_input.textChanged.connect(self.validate_password)
        new_password_layout.addWidget(new_password_label)
        new_password_layout.addWidget(self.new_password_input)
        layout.addLayout(new_password_layout)

        # Confirm password
        confirm_password_layout = QVBoxLayout()
        confirm_password_label = QLabel("Confirm Password:")
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("Confirm new password")
        self.confirm_password_input.setMinimumHeight(35)
        self.confirm_password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #21F5C1;
                border-radius: 8px;
                background-color: #0D2323;
                color: #E8F4F2;
                font-size: 12pt;
            }
            QLineEdit:focus {
                border-color: #2AF5D1;
            }
        """)
        self.confirm_password_input.textChanged.connect(self.validate_password)
        confirm_password_layout.addWidget(confirm_password_label)
        confirm_password_layout.addWidget(self.confirm_password_input)
        layout.addLayout(confirm_password_layout)

        # Password strength indicator
        self.strength_label = QLabel("Password Strength: Weak")
        self.strength_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.strength_label.setStyleSheet("color: #FF4D4D; font-weight: bold;")
        layout.addWidget(self.strength_label)

        # Spacer
        layout.addStretch()

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        # Change password button
        self.change_btn = QPushButton("🔄 Change Password")
        self.change_btn.clicked.connect(self.change_password)
        self.change_btn.setEnabled(False)
        button_layout.addWidget(self.change_btn)

        # Cancel button (closes application)
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setToolTip("Cancel will close the application")
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        # Connect Enter key
        self.new_password_input.returnPressed.connect(self.focus_confirm)
        self.confirm_password_input.returnPressed.connect(self.change_password)

        # Set focus
        self.new_password_input.setFocus()

    def focus_confirm(self):
        """Move focus to confirm password field"""
        self.confirm_password_input.setFocus()

    def validate_password(self):
        """Validate password strength and match"""
        new_pass = self.new_password_input.text()
        confirm_pass = self.confirm_password_input.text()

        # Check password strength
        strength_score = self._check_password_strength(new_pass)

        # Update strength indicator
        if strength_score < 2:
            self.strength_label.setText("Password Strength: Weak")
            self.strength_label.setStyleSheet("color: #FF4D4D; font-weight: bold;")
        elif strength_score < 4:
            self.strength_label.setText("Password Strength: Medium")
            self.strength_label.setStyleSheet("color: #F59E0B; font-weight: bold;")
        else:
            self.strength_label.setText("Password Strength: Strong")
            self.strength_label.setStyleSheet("color: #21F5C1; font-weight: bold;")

        # Check if passwords match and meet requirements
        passwords_match = new_pass == confirm_pass and new_pass != ""
        meets_requirements = strength_score >= 4

        # Enable/disable change button
        self.change_btn.setEnabled(passwords_match and meets_requirements)

        # Show validation messages
        if new_pass and confirm_pass and new_pass != confirm_pass:
            self.strength_label.setText("Passwords do not match")
            self.strength_label.setStyleSheet("color: #FF4D4D; font-weight: bold;")

    def _check_password_strength(self, password: str) -> int:
        """Check password strength and return score"""
        score = 0

        # Length check
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1

        # Character variety
        if any(c.isupper() for c in password):
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1

        # Check against common weak passwords
        weak_passwords = ["password", "123456", "qwerty", "admin", "changeme", "default"]
        if password.lower() not in weak_passwords:
            score += 1

        return score

    def change_password(self):
        """Change the password"""
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        # Final validation
        if not new_password or not confirm_password:
            QMessageBox.warning(self, "Error", "Please fill in both password fields.")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return

        if len(new_password) < 12:
            QMessageBox.warning(self, "Error", "Password must be at least 12 characters long.")
            return

        # Check if it's the default password
        if self.username == "superuser" and new_password == "ChangeMe123!":
            QMessageBox.warning(self, "Error", "You cannot use the default password. Please choose a different password.")
            return

        # Attempt to change password
        try:
            from shared.user_database import user_database
            success, message = user_database.force_password_change(self.username, new_password)

            if success:
                QMessageBox.information(self, "Success",
                                      "Password changed successfully!\n\nYou can now log in with your new password.")
                logger.info(f"Password changed successfully for user {self.username}")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", f"Failed to change password: {message}")
                logger.error(f"Password change failed for {self.username}: {message}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            logger.error(f"Password change error for {self.username}: {e}")

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            # Confirm before canceling
            reply = QMessageBox.question(self, "Cancel Password Change",
                                       "Are you sure you want to cancel? This will close the application.",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.reject()
        else:
            super().keyPressEvent(event)