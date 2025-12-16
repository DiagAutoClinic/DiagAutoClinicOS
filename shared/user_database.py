"""
DiagAutoClinicOS - User Account Database (SQL Server Version)
Professional user management system with 4-tier accounts and super user
"""

import pyodbc
import logging
import hashlib
import os
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class UserTier(Enum):
    """User account tiers"""
    BASIC = 1
    STANDARD = 2
    ADVANCED = 3
    PROFESSIONAL = 4
    SUPER_USER = 5

class UserStatus(Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    PASSWORD_EXPIRED = "password_expired"

class UserDatabase:
    """SQL Server-based user account database"""

    def __init__(self, connection_string: str = None):
        """
        Initialize user database with SQL Server connection
        """
        if connection_string is None:
            # Default SQL Server connection - same as DTC database
            connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=localhost;Database=DiagAutoClinicDB;Trusted_Connection=yes;TrustServerCertificate=yes;Encrypt=no;"

        self.connection_string = connection_string
        self._init_database()

    def _init_database(self):
        """Initialize the database and create tables"""
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()

                # Create users table if it doesn't exist
                cursor.execute('''
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
                    CREATE TABLE users (
                        id INT IDENTITY(1,1) PRIMARY KEY,
                        username NVARCHAR(50) UNIQUE NOT NULL,
                        password_hash NVARCHAR(256) NOT NULL,
                        full_name NVARCHAR(100) NOT NULL,
                        email NVARCHAR(100),
                        tier INT NOT NULL,
                        status NVARCHAR(20) NOT NULL DEFAULT 'active',
                        created_at DATETIME2 DEFAULT GETDATE(),
                        last_login DATETIME2,
                        password_changed_at DATETIME2,
                        force_password_change BIT DEFAULT 1,
                        login_attempts INT DEFAULT 0,
                        locked_until DATETIME2,
                        created_by NVARCHAR(50),
                        notes NVARCHAR(500)
                    )
                ''')

                # Create user_permissions table if it doesn't exist
                cursor.execute('''
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='user_permissions' AND xtype='U')
                    CREATE TABLE user_permissions (
                        id INT IDENTITY(1,1) PRIMARY KEY,
                        username NVARCHAR(50) NOT NULL,
                        permission NVARCHAR(50) NOT NULL,
                        granted_by NVARCHAR(50),
                        granted_at DATETIME2 DEFAULT GETDATE(),
                        FOREIGN KEY (username) REFERENCES users(username)
                    )
                ''')

                # Create audit_log table if it doesn't exist
                cursor.execute('''
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='audit_log' AND xtype='U')
                    CREATE TABLE audit_log (
                        id INT IDENTITY(1,1) PRIMARY KEY,
                        timestamp DATETIME2 DEFAULT GETDATE(),
                        username NVARCHAR(50),
                        action NVARCHAR(50) NOT NULL,
                        details NVARCHAR(500),
                        ip_address NVARCHAR(45),
                        user_agent NVARCHAR(200)
                    )
                ''')

                # Create indexes for better performance
                cursor.execute('''
                    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='idx_users_username' AND object_id = OBJECT_ID('users'))
                    CREATE INDEX idx_users_username ON users(username)
                ''')

                cursor.execute('''
                    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='idx_permissions_username' AND object_id = OBJECT_ID('user_permissions'))
                    CREATE INDEX idx_permissions_username ON user_permissions(username)
                ''')

                cursor.execute('''
                    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='idx_audit_timestamp' AND object_id = OBJECT_ID('audit_log'))
                    CREATE INDEX idx_audit_timestamp ON audit_log(timestamp DESC)
                ''')

                conn.commit()

                # Create default super user if it doesn't exist
                self._create_default_super_user()

                logger.info("User database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize user database: {e}")
            raise

    def _create_default_super_user(self):
        """Create the default super user account"""
        try:
            # Check if super user exists
            if not self.user_exists("superuser"):
                # Create super user with default password that must be changed
                default_password = "ChangeMe123!"  # Will be forced to change on first login
                password_hash = self._hash_password(default_password)

                with pyodbc.connect(self.connection_string) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO users (
                            username, password_hash, full_name, email, tier, status,
                            force_password_change, created_by, notes
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        "superuser",
                        password_hash,
                        "System Administrator",
                        "admin@diagautoclinic.co.za",
                        UserTier.SUPER_USER.value,
                        UserStatus.ACTIVE.value,
                        True,  # Force password change
                        "system",
                        "Default super user account - password must be changed on first login"
                    ))

                    # Grant all permissions to super user
                    permissions = [
                        "user_management", "system_admin", "full_diagnostics",
                        "advanced_functions", "security_settings", "audit_logs"
                    ]

                    for perm in permissions:
                        cursor.execute('''
                            INSERT INTO user_permissions (username, permission, granted_by)
                            VALUES (?, ?, ?)
                        ''', ("superuser", perm, "system"))

                    conn.commit()

                logger.info("Default super user account created")

        except Exception as e:
            logger.error(f"Failed to create default super user: {e}")

    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256 with salt"""
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt.hex() + key.hex()

    def _verify_password(self, password: str, hash_str: str) -> bool:
        """Verify a password against its hash"""
        try:
            salt = bytes.fromhex(hash_str[:64])
            stored_key = bytes.fromhex(hash_str[64:])
            key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            return key == stored_key
        except Exception:
            return False

    def create_user(self, username: str, password: str, full_name: str, tier: UserTier,
                    email: str = None, created_by: str = "system") -> bool:
        """Create a new user account"""
        try:
            if self.user_exists(username):
                logger.warning(f"User {username} already exists")
                return False

            password_hash = self._hash_password(password)

            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (
                        username, password_hash, full_name, email, tier, status,
                        force_password_change, created_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    username, password_hash, full_name, email, tier.value,
                    UserStatus.ACTIVE.value, True, created_by
                ))

                # Grant default permissions based on tier
                default_permissions = self._get_default_permissions(tier)
                for perm in default_permissions:
                    cursor.execute('''
                        INSERT INTO user_permissions (username, permission, granted_by)
                        VALUES (?, ?, ?)
                    ''', (username, perm, created_by))

                conn.commit()

            self._audit_log(created_by, "user_created", f"Created user {username} with tier {tier.name}")
            logger.info(f"User {username} created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create user {username}: {e}")
            return False

    def _get_default_permissions(self, tier: UserTier) -> List[str]:
        """Get default permissions for a user tier"""
        permissions = []

        if tier == UserTier.BASIC:
            permissions = ["basic_diagnostics", "read_data"]
        elif tier == UserTier.STANDARD:
            permissions = ["basic_diagnostics", "read_data", "write_data", "standard_functions"]
        elif tier == UserTier.ADVANCED:
            permissions = ["basic_diagnostics", "read_data", "write_data", "standard_functions",
                          "advanced_diagnostics", "calibrations"]
        elif tier == UserTier.PROFESSIONAL:
            permissions = ["basic_diagnostics", "read_data", "write_data", "standard_functions",
                          "advanced_diagnostics", "calibrations", "programming", "coding"]
        elif tier == UserTier.SUPER_USER:
            permissions = ["user_management", "system_admin", "full_diagnostics",
                          "advanced_functions", "security_settings", "audit_logs"]

        return permissions

    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str, Dict]:
        """Authenticate a user and return user info"""
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT password_hash, tier, status, force_password_change, login_attempts, locked_until
                    FROM users WHERE username = ?
                ''', (username,))

                result = cursor.fetchone()
                if not result:
                    return False, "Invalid username", {}

                password_hash, tier, status, force_change, attempts, locked_until = result

                # Check if account is locked
                if status == UserStatus.LOCKED.value:
                    return False, "Account is locked", {}

                # Check if account is active
                if status != UserStatus.ACTIVE.value:
                    return False, "Account is not active", {}

                # Verify password
                if not self._verify_password(password, password_hash):
                    # Increment login attempts
                    attempts += 1
                    if attempts >= 3:  # Lock account after 3 failed attempts
                        cursor.execute('''
                            UPDATE users SET status = ?, locked_until = DATEADD(HOUR, 1, GETDATE())
                            WHERE username = ?
                        ''', (UserStatus.LOCKED.value, username))
                        conn.commit()
                        return False, "Account locked due to too many failed attempts", {}

                    cursor.execute('UPDATE users SET login_attempts = ? WHERE username = ?',
                                  (attempts, username))
                    conn.commit()
                    return False, f"Invalid password ({3-attempts} attempts remaining)", {}

                # Reset login attempts on successful login
                cursor.execute('''
                    UPDATE users SET login_attempts = 0, last_login = GETDATE()
                    WHERE username = ?
                ''', (username,))
                conn.commit()

                # Get user info
                user_info = self.get_user_info(username)
                if not user_info:
                    return False, "Failed to retrieve user information", {}

                # Check if password change is required
                if force_change:
                    user_info['force_password_change'] = True
                    return True, "Password change required", user_info

                self._audit_log(username, "login", "Successful login")
                return True, "Login successful", user_info

        except Exception as e:
            logger.error(f"Authentication error for {username}: {e}")
            return False, f"Authentication error: {e}", {}

    def change_password(self, username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Change user password"""
        try:
            # First verify old password
            success, message, _ = self.authenticate_user(username, old_password)
            if not success and "Password change required" not in message:
                return False, "Current password is incorrect"

            # Validate new password
            if len(new_password) < 12:
                return False, "Password must be at least 12 characters long"

            # Hash new password
            new_hash = self._hash_password(new_password)

            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET
                        password_hash = ?,
                        password_changed_at = GETDATE(),
                        force_password_change = 0
                    WHERE username = ?
                ''', (new_hash, username))
                conn.commit()

            self._audit_log(username, "password_changed", "Password changed successfully")
            return True, "Password changed successfully"

        except Exception as e:
            logger.error(f"Password change error for {username}: {e}")
            return False, f"Password change failed: {e}"

    def force_password_change(self, username: str, new_password: str) -> Tuple[bool, str]:
        """Force change password (for first login or admin reset)"""
        try:
            if len(new_password) < 12:
                return False, "Password must be at least 12 characters long"

            new_hash = self._hash_password(new_password)

            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET
                        password_hash = ?,
                        password_changed_at = GETDATE(),
                        force_password_change = 0,
                        status = ?
                    WHERE username = ?
                ''', (new_hash, UserStatus.ACTIVE.value, username))
                conn.commit()

            self._audit_log(username, "password_changed", "Password force-changed")
            return True, "Password changed successfully"

        except Exception as e:
            logger.error(f"Force password change error for {username}: {e}")
            return False, f"Password change failed: {e}"

    def user_exists(self, username: str) -> bool:
        """Check if a user exists"""
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM users WHERE username = ?', (username,))
                return cursor.fetchone() is not None
        except Exception:
            return False

    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get user information"""
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT username, full_name, email, tier, status, created_at,
                           last_login, force_password_change
                    FROM users WHERE username = ?
                ''', (username,))

                result = cursor.fetchone()
                if not result:
                    return None

                username, full_name, email, tier, status, created_at, last_login, force_change = result

                # Get permissions
                cursor.execute('SELECT permission FROM user_permissions WHERE username = ?',
                              (username,))
                permissions = [row[0] for row in cursor.fetchall()]

                return {
                    'username': username,
                    'full_name': full_name,
                    'email': email,
                    'tier': UserTier(tier).name,
                    'tier_value': tier,
                    'status': status,
                    'permissions': permissions,
                    'created_at': str(created_at) if created_at else None,
                    'last_login': str(last_login) if last_login else None,
                    'force_password_change': bool(force_change)
                }

        except Exception as e:
            logger.error(f"Failed to get user info for {username}: {e}")
            return None

    def get_all_users(self) -> List[Dict]:
        """Get all users (super user only)"""
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT username, full_name, email, tier, status, created_at, last_login
                    FROM users ORDER BY created_at DESC
                ''')

                users = []
                for row in cursor.fetchall():
                    username, full_name, email, tier, status, created_at, last_login = row
                    users.append({
                        'username': username,
                        'full_name': full_name,
                        'email': email,
                        'tier': UserTier(tier).name,
                        'status': status,
                        'created_at': str(created_at) if created_at else None,
                        'last_login': str(last_login) if last_login else None
                    })

                return users

        except Exception as e:
            logger.error(f"Failed to get all users: {e}")
            return []

    def update_user_status(self, username: str, status: UserStatus, updated_by: str) -> bool:
        """Update user status"""
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET status = ? WHERE username = ?',
                              (status.value, username))
                conn.commit()

            self._audit_log(updated_by, "user_status_updated",
                           f"Updated {username} status to {status.value}")
            return True

        except Exception as e:
            logger.error(f"Failed to update user status: {e}")
            return False

    def delete_user(self, username: str, deleted_by: str) -> bool:
        """Delete a user account"""
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                # Delete permissions first (foreign key constraint)
                cursor.execute('DELETE FROM user_permissions WHERE username = ?', (username,))
                cursor.execute('DELETE FROM users WHERE username = ?', (username,))
                conn.commit()

            self._audit_log(deleted_by, "user_deleted", f"Deleted user {username}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete user {username}: {e}")
            return False

    def has_permission(self, username: str, permission: str) -> bool:
        """Check if user has a specific permission"""
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 1 FROM user_permissions
                    WHERE username = ? AND permission = ?
                ''', (username, permission))
                return cursor.fetchone() is not None
        except Exception:
            return False

    def _audit_log(self, username: str, action: str, details: str = ""):
        """Log an audit event"""
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO audit_log (username, action, details)
                    VALUES (?, ?, ?)
                ''', (username, action, details))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")

    def get_audit_logs(self, limit: int = 100) -> List[Dict]:
        """Get audit logs (super user only)"""
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT timestamp, username, action, details
                    FROM audit_log
                    ORDER BY timestamp DESC
                ''')

                logs = []
                for row in cursor.fetchall():
                    timestamp, username, action, details = row
                    logs.append({
                        'timestamp': str(timestamp) if timestamp else None,
                        'username': username or 'system',
                        'action': action,
                        'details': details or ''
                    })

                return logs[:limit]  # Limit results

        except Exception as e:
            logger.error(f"Failed to get audit logs: {e}")
            return []

# Global user database instance
user_database = UserDatabase()