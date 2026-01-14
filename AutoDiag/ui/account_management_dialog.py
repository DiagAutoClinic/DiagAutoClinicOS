
#!/usr/bin/env python3
"""
Account Management Dialog for DiagAutoClinicOS
Super user only - manage all user accounts
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QMessageBox, QGroupBox,
    QFormLayout, QSpinBox, QTextEdit, QTabWidget, QWidget, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QIcon

# Use the JSON-based Security Manager instead of SQLite
from shared.security_manager import security_manager, SecurityLevel, UserRole

logger = logging.getLogger(__name__)

class AccountManagementDialog(QDialog):
    """Account management dialog for super user"""

    def __init__(self, current_user: str, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.setWindowTitle("DiagAutoClinicOS - Account Management")
        self.setModal(True)
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)
        
        # Apply DACOS Theme
        try:
            from shared.theme_manager import get_stylesheet, get_theme_dict
            self.setStyleSheet(get_stylesheet())
            self.theme = get_theme_dict()
        except:
            pass

        # Check if user has permission
        if not security_manager.has_permission(current_user, "user_management"):
            QMessageBox.critical(self, "Access Denied",
                               "You do not have permission to access account management.")
            self.reject()
            return

        self.user_db = security_manager
        self.init_ui()
        self.load_users()

    def init_ui(self):
        """Initialize the account management UI"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("👥 Account Management")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setProperty("class", "hero-title")
        layout.addWidget(title)

        # Tab widget for different management sections
        tab_widget = QTabWidget()
        tab_widget.setProperty("class", "tab-widget")

        # User accounts tab
        accounts_tab = self.create_accounts_tab()
        tab_widget.addTab(accounts_tab, "👤 User Accounts")

        # Audit logs tab
        audit_tab = self.create_audit_tab()
        tab_widget.addTab(audit_tab, "📋 Audit Logs")

        layout.addWidget(tab_widget)

        # Close button
        close_btn = QPushButton("❌ Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setMaximumWidth(150)
        close_btn.setProperty("class", "danger")
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def create_accounts_tab(self) -> QWidget:
        """Create the user accounts management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Users table
        users_group = QGroupBox("User Accounts")
        users_layout = QVBoxLayout(users_group)

        # Table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(7)
        self.users_table.setHorizontalHeaderLabels([
            "Username", "Full Name", "Tier", "Status", "Created", "Last Login", "Actions"
        ])
        self.users_table.horizontalHeader().setStretchLastSection(True)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        users_layout.addWidget(self.users_table)

        # Action buttons
        actions_layout = QHBoxLayout()

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_users)
        actions_layout.addWidget(refresh_btn)

        actions_layout.addStretch()

        create_btn = QPushButton("➕ Create User")
        create_btn.clicked.connect(self.show_create_user_dialog)
        create_btn.setProperty("class", "success")
        actions_layout.addWidget(create_btn)

        layout.addWidget(users_group)
        layout.addLayout(actions_layout)

        return tab

    def create_audit_tab(self) -> QWidget:
        """Create the audit logs tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Audit logs table
        audit_group = QGroupBox("Audit Logs")
        audit_layout = QVBoxLayout(audit_group)

        # Table
        self.audit_table = QTableWidget()
        self.audit_table.setColumnCount(4)
        self.audit_table.setHorizontalHeaderLabels([
            "Timestamp", "User", "Action", "Details"
        ])
        self.audit_table.horizontalHeader().setStretchLastSection(True)
        self.audit_table.setAlternatingRowColors(True)

        audit_layout.addWidget(self.audit_table)

        # Refresh button
        refresh_audit_btn = QPushButton("🔄 Refresh Logs")
        refresh_audit_btn.clicked.connect(self.load_audit_logs)
        audit_layout.addWidget(refresh_audit_btn)

        layout.addWidget(audit_group)

        # Load audit logs
        self.load_audit_logs()

        return tab

    def load_users(self):
        """Load users into the table"""
        try:
            users = self.user_db.get_all_users()

            self.users_table.setRowCount(len(users))

            for row, user in enumerate(users):
                # Username
                username_item = QTableWidgetItem(user['username'])
                username_item.setFlags(username_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.users_table.setItem(row, 0, username_item)

                # Full Name
                name_item = QTableWidgetItem(user['full_name'])
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.users_table.setItem(row, 1, name_item)

                # Tier
                tier_item = QTableWidgetItem(user['tier'])
                tier_item.setFlags(tier_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.users_table.setItem(row, 2, tier_item)

                # Status
                status_item = QTableWidgetItem(user['status'].title())
                status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.users_table.setItem(row, 3, status_item)

                # Created
                created_item = QTableWidgetItem(user['created_at'][:19])  # Truncate timestamp
                created_item.setFlags(created_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.users_table.setItem(row, 4, created_item)

                # Last Login
                last_login = user['last_login'] or "Never"
                if last_login != "Never":
                    last_login = last_login[:19]
                login_item = QTableWidgetItem(last_login)
                login_item.setFlags(login_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.users_table.setItem(row, 5, login_item)

                # Actions button
                actions_widget = self.create_actions_widget(user['username'])
                self.users_table.setCellWidget(row, 6, actions_widget)

            # Resize columns
            self.users_table.resizeColumnsToContents()

        except Exception as e:
            logger.error(f"Failed to load users: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load users: {e}")

    def create_actions_widget(self, username: str) -> QWidget:
        """Create action buttons widget for a user row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Edit button
        edit_btn = QPushButton("✏️")
        edit_btn.setToolTip("Edit User")
        edit_btn.setMaximumWidth(30)
        edit_btn.clicked.connect(lambda: self.edit_user(username))
        layout.addWidget(edit_btn)

        # Reset password button
        reset_btn = QPushButton("🔑")
        reset_btn.setToolTip("Reset Password")
        reset_btn.setMaximumWidth(30)
        reset_btn.clicked.connect(lambda: self.reset_password(username))
        layout.addWidget(reset_btn)

        # Delete button (disabled for self)
        if username != self.current_user:
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Delete User")
            delete_btn.setMaximumWidth(30)
            delete_btn.clicked.connect(lambda: self.delete_user(username))
            delete_btn.setProperty("class", "danger")
            layout.addWidget(delete_btn)

        layout.addStretch()
        return widget

    def load_audit_logs(self):
        """Load audit logs into the table"""
        try:
            logs = self.user_db.get_audit_log(200)  # Singular 'get_audit_log' in security_manager

            self.audit_table.setRowCount(len(logs))

            # Reverse logs to show newest first
            for row, log in enumerate(reversed(logs)):
                # Timestamp
                import datetime
                timestamp = datetime.datetime.fromtimestamp(log['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                timestamp_item = QTableWidgetItem(timestamp)
                timestamp_item.setFlags(timestamp_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.audit_table.setItem(row, 0, timestamp_item)

                # User
                user_item = QTableWidgetItem(str(log.get('username', 'System')))
                user_item.setFlags(user_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.audit_table.setItem(row, 1, user_item)

                # Action
                action_item = QTableWidgetItem(log['event_type'].replace('_', ' ').title())
                action_item.setFlags(action_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.audit_table.setItem(row, 2, action_item)

                # Details
                details_item = QTableWidgetItem(str(log.get('details', '')))
                details_item.setFlags(details_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.audit_table.setItem(row, 3, details_item)

            # Resize columns
            self.audit_table.resizeColumnsToContents()

        except Exception as e:
            logger.error(f"Failed to load audit logs: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load audit logs: {e}")

    def show_create_user_dialog(self):
        """Show dialog to create a new user"""
        dialog = CreateUserDialog(self.current_user, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_users()  # Refresh the table

    def edit_user(self, username: str):
        """Edit an existing user"""
        dialog = EditUserDialog(username, self.current_user, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_users()  # Refresh the table

    def reset_password(self, username: str):
        """Reset user password"""
        reply = QMessageBox.question(self, "Reset Password",
                                   f"Are you sure you want to reset the password for {username}?\n\n"
                                   "This will force them to change their password on next login.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.user_db.force_password_reset(username, self.current_user)
                
                if success:
                    QMessageBox.information(self, "Success",
                                          f"Password reset for {username}. They will be required to change it on next login.")
                    self.load_users()
                else:
                    QMessageBox.critical(self, "Error", "Failed to reset password.")

            except Exception as e:
                logger.error(f"Failed to reset password for {username}: {e}")
                QMessageBox.critical(self, "Error", f"Failed to reset password: {e}")

    def delete_user(self, username: str):
        """Delete a user account"""
        reply = QMessageBox.question(self, "Delete User",
                                   f"Are you sure you want to permanently delete the account for {username}?\n\n"
                                   "This action cannot be undone!",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.user_db.delete_user(username, self.current_user)
                if success:
                    QMessageBox.information(self, "Success", f"User {username} has been deleted.")
                    self.load_users()
                else:
                    QMessageBox.critical(self, "Error", f"Failed to delete user {username}.")

            except Exception as e:
                logger.error(f"Failed to delete user {username}: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete user: {e}")


class CreateUserDialog(QDialog):
    """Dialog for creating a new user"""

    def __init__(self, created_by: str, parent=None):
        super().__init__(parent)
        self.created_by = created_by
        self.setWindowTitle("Create New User")
        self.setModal(True)
        self.setMinimumSize(400, 500)
        self.resize(450, 550)
        
        try:
            from shared.themes.dacos_cyber_teal import DACOS_STYLESHEET
            self.setStyleSheet(DACOS_STYLESHEET)
        except:
            pass

        self.user_db = security_manager
        self.init_ui()

    def init_ui(self):
        """Initialize the create user dialog"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("➕ Create New User")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 16, QFont.Weight.Bold)
        title.setFont(title_font)
        layout.addWidget(title)

        # Form
        form_group = QGroupBox("User Information")
        form_layout = QFormLayout(form_group)

        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        form_layout.addRow("Username:", self.username_input)

        # Full Name
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("Enter full name")
        form_layout.addRow("Full Name:", self.full_name_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email (optional)")
        form_layout.addRow("Email:", self.email_input)

        # Tier
        self.tier_combo = QComboBox()
        self.tier_combo.addItems(["BASIC", "STANDARD", "ADVANCED", "PROFESSIONAL"])
        form_layout.addRow("Access Tier:", self.tier_combo)

        # Initial Password
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter initial password")
        form_layout.addRow("Initial Password:", self.password_input)

        layout.addWidget(form_group)

        # Buttons
        buttons_layout = QHBoxLayout()

        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        create_btn = QPushButton("✅ Create User")
        create_btn.clicked.connect(self.create_user)
        create_btn.setProperty("class", "success")
        buttons_layout.addWidget(create_btn)

        layout.addLayout(buttons_layout)

    def create_user(self):
        """Create the new user"""
        username = self.username_input.text().strip()
        full_name = self.full_name_input.text().strip()
        email = self.email_input.text().strip()
        tier_name = self.tier_combo.currentText()
        password = self.password_input.text()

        # Validation
        if not username or not full_name or not password:
            QMessageBox.warning(self, "Validation Error", "Please fill in all required fields.")
            return

        if len(password) < 8:
            QMessageBox.warning(self, "Validation Error", "Password must be at least 8 characters long.")
            return

        # Map Tier to Role/Security Level
        security_level = SecurityLevel.BASIC
        role = UserRole.VIEWER
        
        if tier_name == "PROFESSIONAL":
            security_level = SecurityLevel.DEALER
            role = UserRole.DEALER
        elif tier_name == "ADVANCED":
            security_level = SecurityLevel.ADVANCED
            role = UserRole.SUPERVISOR
        elif tier_name == "STANDARD":
            security_level = SecurityLevel.STANDARD
            role = UserRole.TECHNICIAN

        # Create user
        success, message = self.user_db.add_user(username, password, role, security_level, full_name)

        if success:
            # Update email if provided (since add_user doesn't take email)
            if email:
                self.user_db.update_user_details(username, full_name, email, tier_name, "ACTIVE", self.created_by)
                
            QMessageBox.information(self, "Success", f"User {username} created successfully!")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", f"Failed to create user: {message}")


class EditUserDialog(QDialog):
    """Dialog for editing an existing user"""

    def __init__(self, username: str, edited_by: str, parent=None):
        super().__init__(parent)
        self.username = username
        self.edited_by = edited_by
        self.setWindowTitle(f"Edit User - {username}")
        self.setModal(True)
        self.setMinimumSize(400, 400)
        self.resize(450, 450)
        
        try:
            from shared.themes.dacos_cyber_teal import DACOS_STYLESHEET
            self.setStyleSheet(DACOS_STYLESHEET)
        except:
            pass

        self.user_db = security_manager
        
        # Get current user info from DB
        users = self.user_db.get_all_users() # Not efficient but works
        self.user_info = next((u for u in users if u['username'] == username), None)

        if not self.user_info:
            QMessageBox.critical(self, "Error", f"Could not load information for user {username}")
            self.reject()
            return

        self.init_ui()

    def init_ui(self):
        """Initialize the edit user dialog"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel(f"✏️ Edit User: {self.username}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 16, QFont.Weight.Bold)
        title.setFont(title_font)
        layout.addWidget(title)

        # Form
        form_group = QGroupBox("User Information")
        form_layout = QFormLayout(form_group)

        # Full Name
        self.full_name_input = QLineEdit(self.user_info['full_name'])
        form_layout.addRow("Full Name:", self.full_name_input)

        # Email
        self.email_input = QLineEdit(self.user_info.get('email', ''))
        form_layout.addRow("Email:", self.email_input)

        # Tier (only if not superuser/self)
        if self.username != self.edited_by:
            self.tier_combo = QComboBox()
            self.tier_combo.addItems(["BASIC", "STANDARD", "ADVANCED", "PROFESSIONAL"])
            # Try to match current tier
            current_tier = self.user_info['tier']
            # Map back from SecurityLevel name if needed, but get_all_users returns name string
            # Just do best effort match
            index = self.tier_combo.findText(current_tier)
            if index >= 0:
                self.tier_combo.setCurrentIndex(index)
            elif current_tier == "DEALER":
                self.tier_combo.setCurrentText("PROFESSIONAL")
            elif current_tier == "FACTORY":
                self.tier_combo.addItem("FACTORY")
                self.tier_combo.setCurrentText("FACTORY")
                self.tier_combo.setEnabled(False) # Don't edit factory tiers easily
                
            form_layout.addRow("Access Tier:", self.tier_combo)
        else:
            tier_label = QLabel(f"{self.user_info['tier']} (Cannot change own tier)")
            accent = getattr(self, 'theme', {}).get('accent', '#21F5C1')
            tier_label.setStyleSheet(f"font-weight: bold; color: {accent};")
            form_layout.addRow("Access Tier:", tier_label)

        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["ACTIVE", "LOCKED"])
        current_status = self.user_info['status']
        self.status_combo.setCurrentText(current_status)
        form_layout.addRow("Status:", self.status_combo)

        layout.addWidget(form_group)

        # Buttons
        buttons_layout = QHBoxLayout()

        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        save_btn = QPushButton("💾 Save Changes")
        save_btn.clicked.connect(self.save_changes)
        save_btn.setProperty("class", "success")
        buttons_layout.addWidget(save_btn)

        layout.addLayout(buttons_layout)

    def save_changes(self):
        """Save the user changes"""
        full_name = self.full_name_input.text().strip()
        email = self.email_input.text().strip()
        tier_name = self.tier_combo.currentText() if hasattr(self, 'tier_combo') else None
        status = self.status_combo.currentText()

        # Validation
        if not full_name:
            QMessageBox.warning(self, "Validation Error", "Full name is required.")
            return

        try:
            success = self.user_db.update_user_details(
                self.username, full_name, email, tier_name, status, self.edited_by
            )

            if success:
                QMessageBox.information(self, "Success", f"User {self.username} updated successfully!")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to update user.")

        except Exception as e:
            logger.error(f"Failed to update user {self.username}: {e}")
            QMessageBox.critical(self, "Error", f"Failed to update user: {e}")
