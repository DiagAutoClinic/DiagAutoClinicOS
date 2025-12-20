"""
DiagAutoClinicOS - Security Manager Module
Professional 25-Brand Diagnostic Suite
"""

import logging
import os
import hashlib
import secrets
import time
import json
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security levels for the system"""
    BASIC = 1
    STANDARD = 2
    ADVANCED = 3
    DEALER = 4
    FACTORY = 5

class UserRole(Enum):
    """User roles for the system"""
    VIEWER = "viewer"
    TECHNICIAN = "technician"
    SUPERVISOR = "supervisor"
    DEALER = "dealer"
    FACTORY = "factory"
    ADMIN = "admin"

class EnhancedSecurityManager:
    """Enhanced security management for DiagAutoClinicOS with advanced features"""

    def __init__(self, config_path: Optional[str] = None):
        self.current_user = None
        self.session_active = False
        self.session_expiry = None
        self.session_token = None
        self.security_level = SecurityLevel.BASIC
        self.user_role = UserRole.VIEWER
        self.failed_attempts = 0
        self.lockout_until = None
        self.audit_log: List[Dict[str, Any]] = []

        # Load security configuration
        self.security_config = self._load_security_config(config_path)

        # Initialize user database
        self.user_database = self._initialize_user_database()

        logger.info("EnhancedSecurityManager initialized")

    def _load_security_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load security configuration from file or use defaults"""
        default_config = {
            'session_timeout': 3600,  # 1 hour
            'max_failed_attempts': 5,
            'lockout_duration': 900,  # 15 minutes
            'password_min_length': 8,
            'require_mixed_case': True,
            'require_numbers': True,
            'require_special_chars': False,
            'audit_log_max_entries': 1000
        }

        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
                    logger.info(f"Security config loaded from {config_path}")
            except Exception as e:
                logger.warning(f"Failed to load security config: {e}")

        return default_config

    def _initialize_user_database(self) -> Dict[str, Dict[str, Any]]:
        """Initialize user database, loading from file if available, else use defaults"""
        users = self._load_users_from_file()
        if users is None:
            users = self._create_default_users()
        return users

    def _load_users_from_file(self) -> Optional[Dict[str, Dict[str, Any]]]:
        """Load user database from users.json file"""
        try:
            if not os.path.exists('users.json'):
                return None
            with open('users.json', 'r') as f:
                data = json.load(f)
            users = {}
            for username, user_data in data.items():
                users[username] = {
                    "password_hash": user_data["password_hash"],
                    "salt": user_data["salt"],
                    "security_level": SecurityLevel[user_data["security_level"]],
                    "role": UserRole(user_data["role"]),
                    "full_name": user_data["full_name"],
                    "failed_attempts": user_data.get("failed_attempts", 0),
                    "locked_until": user_data.get("locked_until"),
                    "last_login": user_data.get("last_login"),
                    "created_at": user_data.get("created_at", time.time()),
                    "force_password_change": user_data.get("force_password_change", False)
                }
            return users
        except Exception as e:
            logger.warning(f"Failed to load users from file: {e}")
            return None

    def _create_default_users(self) -> Dict[str, Dict[str, Any]]:
        """Create default users"""
        users = {}

        # Create tech1 user
        tech1_salt = self._generate_salt()
        users["tech1"] = {
            "password_hash": self._hash_password("tech123", tech1_salt),
            "salt": tech1_salt,
            "security_level": SecurityLevel.STANDARD,
            "role": UserRole.TECHNICIAN,
            "full_name": "Technician One",
            "failed_attempts": 0,
            "locked_until": None,
            "last_login": None,
            "created_at": time.time(),
            "force_password_change": False
        }

        # Create supervisor user
        super_salt = self._generate_salt()
        users["supervisor"] = {
            "password_hash": self._hash_password("super789", super_salt),
            "salt": super_salt,
            "security_level": SecurityLevel.ADVANCED,
            "role": UserRole.SUPERVISOR,
            "full_name": "System Supervisor",
            "failed_attempts": 0,
            "locked_until": None,
            "last_login": None,
            "created_at": time.time(),
            "force_password_change": False
        }

        # Create admin user
        admin_salt = self._generate_salt()
        users["admin"] = {
            "password_hash": self._hash_password("admin345", admin_salt),
            "salt": admin_salt,
            "security_level": SecurityLevel.FACTORY,
            "role": UserRole.ADMIN,
            "full_name": "System Administrator",
            "failed_attempts": 0,
            "locked_until": None,
            "last_login": None,
            "created_at": time.time(),
            "force_password_change": False
        }

        return users

    def _generate_salt(self) -> str:
        """Generate a random salt for password hashing"""
        return secrets.token_hex(32)  # 64 character hex string

    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt using SHA-256"""
        combined = f"{password}{salt}".encode('utf-8')
        return hashlib.sha256(combined).hexdigest()

    def _generate_session_token(self) -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(64)

    def _log_audit_event(self, event_type: str, username: str = None,
                        details: Dict[str, Any] = None) -> None:
        """Log an audit event"""
        entry = {
            'timestamp': time.time(),
            'event_type': event_type,
            'username': username or self.current_user,
            'details': details or {}
        }

        self.audit_log.append(entry)

        # Keep audit log size manageable
        if len(self.audit_log) > self.security_config['audit_log_max_entries']:
            self.audit_log = self.audit_log[-self.security_config['audit_log_max_entries']:]

        # Log to file if configured
        try:
            with open('security_audit.log', 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except:
            pass  # Ignore file write errors

    def authenticate_user(self, username: str, password: str) -> tuple[bool, str, Optional[Dict[str, Any]]]:
        """Authenticate a user with username and password"""
        try:
            # Normalize username to lowercase for case-insensitive lookup
            normalized_username = username.lower()

            # Check system lockout
            if self.lockout_until and time.time() < self.lockout_until:
                remaining = int(self.lockout_until - time.time())
                return False, f"System locked due to security policy. Try again in {remaining} seconds.", None

            # Check if user exists (case-insensitive)
            if normalized_username not in self.user_database:
                self._log_audit_event('login_failed_unknown_user', username)
                return False, "Invalid credentials", None

            user_data = self.user_database[normalized_username]

            # Check user lockout
            if user_data.get('locked_until') and time.time() < user_data['locked_until']:
                remaining = int(user_data['locked_until'] - time.time())
                return False, f"Account locked. Try again in {remaining} seconds.", None

            # Verify password
            expected_hash = self._hash_password(password, user_data['salt'])
            if expected_hash != user_data['password_hash']:
                user_data['failed_attempts'] = user_data.get('failed_attempts', 0) + 1
                self.failed_attempts += 1

                # Check for user lockout
                if user_data['failed_attempts'] >= 3:
                    user_data['locked_until'] = time.time() + self.security_config['lockout_duration']
                    self._log_audit_event('user_locked', username, {'reason': 'failed_attempts'})
                    return False, "Account locked due to multiple failed attempts", None

                # Check for system lockout
                if self.failed_attempts >= self.security_config['max_failed_attempts']:
                    self.lockout_until = time.time() + self.security_config['lockout_duration']
                    self._log_audit_event('system_locked', username, {'reason': 'max_failed_attempts'})
                    return False, "System locked due to security policy", None

                self._log_audit_event('login_failed_wrong_password', username)
                return False, "Invalid credentials", None

            # Successful authentication
            self.current_user = normalized_username  # Store normalized username
            self.security_level = user_data["security_level"]
            self.user_role = user_data["role"]
            self.session_active = True
            self.session_token = self._generate_session_token()
            self.session_expiry = datetime.now() + timedelta(seconds=self.security_config['session_timeout'])

            # Reset failed attempts and update last login
            user_data['failed_attempts'] = 0
            user_data['last_login'] = time.time()
            self.failed_attempts = 0

            # Get user info for return
            user_info = self.get_user_info()

            # Check if password change is required
            if user_data.get('force_password_change', False):
                self._log_audit_event('login_success_password_change_required', username)
                logger.info(f"User {username} authenticated successfully - password change required")
                return True, "Password change required", user_info

            self._log_audit_event('login_success', username)
            logger.info(f"User {username} authenticated successfully")
            return True, f"Welcome {user_data['full_name']}!", user_info

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False, f"Authentication error: {e}", None

    def logout(self) -> None:
        """Logout current user"""
        if self.current_user:
            self._log_audit_event('logout', self.current_user)
            logger.info(f"User {self.current_user} logged out")

        self.current_user = None
        self.session_active = False
        self.session_expiry = None
        self.session_token = None
        self.security_level = SecurityLevel.BASIC
        self.user_role = UserRole.VIEWER

    def validate_session(self) -> bool:
        """Validate current session (alias for is_session_valid)"""
        return self.is_session_valid()

    def is_session_valid(self) -> bool:
        """Check if current session is still valid"""
        if not self.session_active or not self.session_expiry:
            return False

        if datetime.now() >= self.session_expiry:
            self.logout()
            return False

        return True

    def extend_session(self, hours: int = 1) -> None:
        """Extend current session"""
        if self.session_active:
            self.session_expiry = datetime.now() + timedelta(hours=hours)
            self._log_audit_event('session_extended', self.current_user, {'hours': hours})
            logger.info(f"Session extended for {hours} hours")

    def check_security_clearance(self, required_level: SecurityLevel) -> bool:
        """Check if current user has sufficient security clearance"""
        if not self.is_session_valid():
            return False
        return self.security_level.value >= required_level.value

    def get_security_level(self) -> SecurityLevel:
        """Get current security level"""
        return self.security_level

    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        if not self.current_user or not self.session_active:
            return {}

        user_data = self.user_database.get(self.current_user, {})

        # Determine permissions based on role/security level
        permissions = []
        if self.security_level.value >= SecurityLevel.FACTORY.value or self.user_role == UserRole.ADMIN:
            permissions.append('user_management')

        return {
            "username": self.current_user,
            "full_name": user_data.get("full_name", self.current_user),
            "security_level": self.security_level.name,
            "tier": self.security_level.name,
            "role": self.user_role.value,
            "permissions": permissions,
            "session_expiry": self.session_expiry.timestamp() if self.session_expiry else 0,
            "last_login": user_data.get("last_login"),
            "force_password_change": user_data.get("force_password_change", False)
        }

    def get_audit_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        return self.audit_log[-limit:] if limit > 0 else self.audit_log

    def elevate_security(self, username: str, password: str, target_level: SecurityLevel) -> tuple[bool, str]:
        """Elevate security level with additional authentication"""
        try:
            # Verify credentials
            if username not in self.user_database:
                return False, "Invalid credentials"

            user_data = self.user_database[username]
            expected_hash = self._hash_password(password, user_data['salt'])
            if expected_hash != user_data['password_hash']:
                return False, "Invalid credentials"

            # Check if user has permission to elevate to target level
            user_level = user_data['security_level'].value
            if user_level < target_level.value:
                return False, "Insufficient privileges for elevation"

            # Elevate current session
            if self.current_user == username:
                old_level = self.security_level
                self.security_level = target_level
                self._log_audit_event('security_elevated', username,
                                    {'from_level': old_level.name, 'to_level': target_level.name})
                return True, f"Security elevated to {target_level.name}"

            return False, "Elevation only allowed for current session"

        except Exception as e:
            logger.error(f"Security elevation error: {e}")
            return False, f"Elevation error: {e}"

    def add_user(self, username: str, password: str, role: UserRole,
                 security_level: SecurityLevel, full_name: str) -> tuple[bool, str]:
        """Add a new user (requires FACTORY level)"""
        if not self.check_security_clearance(SecurityLevel.FACTORY):
            return False, "Insufficient privileges"

        if username in self.user_database:
            return False, "Username already exists"

        # Validate password strength
        valid, message = self.validate_password_strength(password)
        if not valid:
            return False, message

        # Create user
        salt = self._generate_salt()
        self.user_database[username] = {
            "password_hash": self._hash_password(password, salt),
            "salt": salt,
            "security_level": security_level,
            "role": role,
            "full_name": full_name,
            "failed_attempts": 0,
            "locked_until": None,
            "last_login": None,
            "created_at": time.time()
        }

        self._log_audit_event('user_created', self.current_user, {'new_user': username})
        return True, f"User {username} created successfully"

    def change_password(self, username: str, old_password: str, new_password: str) -> tuple[bool, str]:
        """Change user password"""
        if username not in self.user_database:
            return False, "User not found"

        user_data = self.user_database[username]

        # Verify old password (skip if force password change)
        if not user_data.get('force_password_change', False):
            expected_hash = self._hash_password(old_password, user_data['salt'])
            if expected_hash != user_data['password_hash']:
                return False, "Current password incorrect"

        # Validate new password strength
        valid, message = self.validate_password_strength(new_password)
        if not valid:
            return False, message

        # Update password
        salt = self._generate_salt()
        user_data['password_hash'] = self._hash_password(new_password, salt)
        user_data['salt'] = salt
        user_data['failed_attempts'] = 0  # Reset failed attempts
        user_data['force_password_change'] = False  # Reset force change flag

        self._log_audit_event('password_changed', username)
        return True, "Password changed successfully"

    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """Validate password strength according to security policy"""
        if len(password) < self.security_config['password_min_length']:
            return False, f"Password must be at least {self.security_config['password_min_length']} characters long"

        if self.security_config['require_mixed_case']:
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            if not (has_upper and has_lower):
                return False, "Password must contain both uppercase and lowercase letters"

        if self.security_config['require_numbers'] and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"

        if self.security_config['require_special_chars']:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                return False, "Password must contain at least one special character"

        return True, "Password strength acceptable"

    def reset_user_lockout(self, username: str) -> tuple[bool, str]:
        """Reset user lockout (requires FACTORY level)"""
        if not self.check_security_clearance(SecurityLevel.FACTORY):
            return False, "Insufficient privileges"

        if username not in self.user_database:
            return False, "User not found"

        user_data = self.user_database[username]
        user_data['failed_attempts'] = 0
        user_data['locked_until'] = None

        self._log_audit_event('lockout_reset', self.current_user, {'target_user': username})
        return True, f"Lockout reset for user {username}"


# Backward compatibility - keep old SecurityManager as alias
SecurityManager = EnhancedSecurityManager

# Global security manager instance
security_manager = EnhancedSecurityManager()