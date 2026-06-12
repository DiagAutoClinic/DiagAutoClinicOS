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
try:
    from .build_info import BuildVerifier
except ImportError:
    # Fallback if build_info is missing (should not happen in prod)
    class BuildVerifier:
        @staticmethod
        def verify_integrity() -> bool: return True
        @staticmethod
        def get_build_id() -> str: return "UNKNOWN"

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security levels for the system"""
    BASIC = 1
    STANDARD = 2
    ADVANCED = 3
    DEALER = 4
    FACTORY = 5
    SUPER = 6  # DAC root — unrestricted access

class UserRole(Enum):
    """User roles for the system"""
    VIEWER = "viewer"
    TECHNICIAN = "technician"
    SUPERVISOR = "supervisor"
    DEALER = "dealer"
    FACTORY = "factory"
    ADMIN = "admin"
    SUPER_USER = "super_user"  # DAC root

class EnhancedSecurityManager:
    """Enhanced security management for DiagAutoClinicOS with advanced features"""

    # Canonical mapping: TierSystem name → (SecurityLevel, UserRole)
    _TIER_MAP = {
        "FREE":         (SecurityLevel.BASIC,   UserRole.VIEWER),
        "BASIC":        (SecurityLevel.STANDARD, UserRole.TECHNICIAN),
        "INTERMEDIATE": (SecurityLevel.ADVANCED, UserRole.SUPERVISOR),
        "PROFESSIONAL": (SecurityLevel.DEALER,   UserRole.DEALER),
        "ADVANCED":     (SecurityLevel.FACTORY,  UserRole.FACTORY),
    }
    _LEVEL_TO_TIER = {
        SecurityLevel.BASIC:    "FREE",
        SecurityLevel.STANDARD: "BASIC",
        SecurityLevel.ADVANCED: "INTERMEDIATE",
        SecurityLevel.DEALER:   "PROFESSIONAL",
        SecurityLevel.FACTORY:  "ADVANCED",
        SecurityLevel.SUPER:    "SUPERUSER",
    }

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
        self.is_restricted_mode = False  # Feature degradation flag

        # Load security configuration
        self.security_config = self._load_security_config(config_path)

        # Initialize user database — use %AppData%\DACOS\ (user-writable, not Program Files)
        try:
            from config import APP_DATA_DIR  # type: ignore
            _data_dir = APP_DATA_DIR
        except ImportError:
            if os.name == 'nt':
                _appdata_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
                _data_dir = os.path.join(_appdata_dir, 'DACOS')
            else:
                _data_dir = os.path.join(os.path.expanduser('~'), '.dacos')
        os.makedirs(_data_dir, exist_ok=True)
        self.user_db_path = os.path.join(_data_dir, 'users.json')
        self.user_database = self._initialize_user_database()

        logger.info(f"EnhancedSecurityManager initialized using DB at {self.user_db_path}")

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
            # Save defaults immediately
            self.user_database = users
            self._save_users_to_file()
        return users

    def _save_users_to_file(self) -> None:
        """Save user database to users.json file"""
        try:
            # Convert enums to strings for JSON serialization
            serializable_users = {}
            for username, data in self.user_database.items():
                user_copy = data.copy()
                if isinstance(data['security_level'], SecurityLevel):
                    user_copy['security_level'] = data['security_level'].name
                if isinstance(data['role'], UserRole):
                    user_copy['role'] = data['role'].value
                # Keep email and created_by as-is (already strings)
                serializable_users[username] = user_copy
            
            with open(self.user_db_path, 'w') as f:
                json.dump(serializable_users, f, indent=4)
            logger.debug(f"User database saved to {self.user_db_path}")
        except Exception as e:
            logger.error(f"Failed to save users to file: {e}")

    def _load_users_from_file(self) -> Optional[Dict[str, Dict[str, Any]]]:
        """Load user database from users.json file"""
        try:
            if not os.path.exists(self.user_db_path):
                return None
            with open(self.user_db_path, 'r') as f:
                data = json.load(f)
            users = {}
            for username, user_data in data.items():
                users[username] = {
                    "password_hash": user_data["password_hash"],
                    "salt": user_data["salt"],
                    "hash_version": user_data.get("hash_version", "v1"),
                    "security_level": SecurityLevel[user_data["security_level"]],
                    "role": UserRole(user_data["role"]),
                    "full_name": user_data["full_name"],
                    "email": user_data.get("email", ""),
                    "created_by": user_data.get("created_by", "system"),
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
        """Create default users on first run — includes tech1, testuser, and dacos superuser."""
        users = {}

        # --- DACOS Superuser (level 6 — root) ---
        dacos_salt = self._generate_salt()
        users["supernova"] = {
            "password_hash": self._hash_password("Charaun@8576", dacos_salt, "v3"),
            "salt": dacos_salt,
            "hash_version": "v3",
            "security_level": SecurityLevel.SUPER,
            "role": UserRole.SUPER_USER,
            "full_name": "DACOS Superuser",
            "email": "superuser@diagautoclinic.co.za",
            "created_by": "system",
            "failed_attempts": 0,
            "locked_until": None,
            "last_login": None,
            "created_at": time.time(),
            "force_password_change": True  # Change on first login
        }

        # --- Alpha Test User (level 4 — DEALER) ---
        testuser_salt = self._generate_salt()
        users["testuser"] = {
            "password_hash": self._hash_password("TestUserAlpha2026!", testuser_salt, "v3"),
            "salt": testuser_salt,
            "hash_version": "v3",
            "security_level": SecurityLevel.DEALER,
            "role": UserRole.DEALER,
            "full_name": "Alpha Test User",
            "email": "testuser@diagautoclinic.co.za",
            "created_by": "system",
            "failed_attempts": 0,
            "locked_until": None,
            "last_login": None,
            "created_at": time.time(),
            "force_password_change": False
        }

        # --- Technician (level 2) ---
        tech1_salt = self._generate_salt()
        users["tech1"] = {
            "password_hash": self._hash_password("tech123", tech1_salt, "v3"),
            "salt": tech1_salt,
            "hash_version": "v3",
            "security_level": SecurityLevel.STANDARD,
            "role": UserRole.TECHNICIAN,
            "full_name": "Technician One",
            "email": "",
            "created_by": "system",
            "failed_attempts": 0,
            "locked_until": None,
            "last_login": None,
            "created_at": time.time(),
            "force_password_change": False
        }

        # --- Supervisor (level 3) ---
        super_salt = self._generate_salt()
        users["supervisor"] = {
            "password_hash": self._hash_password("super789", super_salt, "v3"),
            "salt": super_salt,
            "hash_version": "v3",
            "security_level": SecurityLevel.ADVANCED,
            "role": UserRole.SUPERVISOR,
            "full_name": "System Supervisor",
            "email": "",
            "created_by": "system",
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

    def _hash_password(self, password: str, salt: str, version: str = 'v3') -> str:
        """Hash password with salt using specified version"""
        if version == 'v1':
            # Legacy SHA-256
            combined = f"{password}{salt}".encode('utf-8')
            return hashlib.sha256(combined).hexdigest()
        elif version == 'v2':
            # V2: PBKDF2-HMAC-SHA256 (100,000 iterations)
            return hashlib.pbkdf2_hmac(
                'sha256', 
                password.encode('utf-8'), 
                salt.encode('utf-8'), 
                100000
            ).hex()
        else:
            # V3: Scrypt (High Security)
            try:
                salt_bytes = bytes.fromhex(salt)
            except ValueError:
                salt_bytes = salt.encode('utf-8')
                
            key = hashlib.scrypt(
                password.encode('utf-8'), 
                salt=salt_bytes, 
                n=16384, 
                r=8, 
                p=1, 
                dklen=64
            )
            return key.hex()

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
            hash_version = user_data.get('hash_version', 'v1')
            expected_hash = self._hash_password(password, user_data['salt'], hash_version)
            
            if expected_hash != user_data['password_hash']:
                user_data['failed_attempts'] = user_data.get('failed_attempts', 0) + 1
                self.failed_attempts += 1

                # Check for user lockout
                if user_data['failed_attempts'] >= 3:
                    user_data['locked_until'] = time.time() + self.security_config['lockout_duration']
                    self._log_audit_event('user_locked', username, {'reason': 'failed_attempts'})
                    self._save_users_to_file()
                    return False, "Account locked due to multiple failed attempts", None

                # Check for system lockout
                if self.failed_attempts >= self.security_config['max_failed_attempts']:
                    self.lockout_until = time.time() + self.security_config['lockout_duration']
                    self._log_audit_event('system_locked', username, {'reason': 'max_failed_attempts'})
                    return False, "System locked due to security policy", None

                self._log_audit_event('login_failed_wrong_password', username)
                # Save failed attempt count
                self._save_users_to_file()
                return False, "Invalid credentials", None

            # Successful authentication
            
            # MIGRATION: Upgrade legacy hashes to v3
            if hash_version in ('v1', 'v2'):
                logger.info(f"Migrating user {username} from {hash_version} to v3 password hash")
                user_data['password_hash'] = self._hash_password(password, user_data['salt'], 'v3')
                user_data['hash_version'] = 'v3'
                self._save_users_to_file()

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
            
            # Save login timestamp
            self._save_users_to_file()

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

        # SUPER session never expires
        if self.security_level == SecurityLevel.SUPER:
            return True

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

    def get_user_info(self, username: Optional[str] = None) -> Dict[str, Any]:
        """Get user information for the given username, or current user if omitted."""
        lookup = username or self.current_user
        if not lookup:
            return {}

        user_data = self.user_database.get(lookup, {})
        if not user_data:
            return {}

        # Determine permissions based on security level
        permissions = []
        if isinstance(user_data.get('security_level'), SecurityLevel):
            level_value = user_data['security_level'].value
        else:
            level_value = 0

        if level_value >= SecurityLevel.SUPER.value:
            permissions.append('user_management')
            permissions.append('all_suites')
            permissions.append('full_diagnostics')
            permissions.append('all_brands')
        elif level_value >= SecurityLevel.FACTORY.value:
            permissions.append('full_diagnostics')
            permissions.append('all_brands')
        elif level_value >= SecurityLevel.ADVANCED.value:
            permissions.append('full_diagnostics')

        return {
            "username": lookup,
            "full_name": user_data.get("full_name", lookup),
            "security_level": user_data['security_level'].name if isinstance(user_data.get('security_level'), SecurityLevel) else user_data.get('security_level', 'BASIC'),
            "tier": user_data['security_level'].name if isinstance(user_data.get('security_level'), SecurityLevel) else user_data.get('security_level', 'BASIC'),
            "role": user_data['role'].value if isinstance(user_data.get('role'), UserRole) else user_data.get('role', 'viewer'),
            "email": user_data.get('email', ''),
            "permissions": permissions,
            "is_restricted": self.is_restricted_mode,
            "session_expiry": self.session_expiry.timestamp() if self.session_expiry else 0,
            "last_login": user_data.get("last_login"),
            "force_password_change": user_data.get("force_password_change", False)
        }

    def user_exists(self, username: str) -> bool:
        """Check if a username exists in the database (case-insensitive)."""
        return username.lower() in self.user_database

    @property
    def is_super_user(self) -> bool:
        """Return True if the currently authenticated user is SUPER level."""
        return self.session_active and self.security_level == SecurityLevel.SUPER

    def create_user(self, username: str, password: str, full_name: str,
                    tier: int, email: str = "", created_by: str = "",
                    force_password_change: bool = True) -> tuple[bool, str]:
        """Convenience alias for add_user using tier integer instead of enums.
        Tier mapping: 1=FREE, 2=BASIC, 3=INTERMEDIATE, 4=PROFESSIONAL, 5=ADVANCED, 6=SUPER.
        Only the SUPER user can create users."""
        tier_map = {
            1: SecurityLevel.BASIC,
            2: SecurityLevel.STANDARD,
            3: SecurityLevel.ADVANCED,
            4: SecurityLevel.DEALER,
            5: SecurityLevel.FACTORY,
            6: SecurityLevel.SUPER,
        }
        role_map = {
            1: UserRole.VIEWER,
            2: UserRole.TECHNICIAN,
            3: UserRole.SUPERVISOR,
            4: UserRole.DEALER,
            5: UserRole.FACTORY,
            6: UserRole.SUPER_USER,
        }
        level = tier_map.get(tier, SecurityLevel.BASIC)
        role = role_map.get(tier, UserRole.VIEWER)
        return self.add_user(username, password, role, level, full_name, email, created_by, force_password_change)

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
            hash_version = user_data.get('hash_version', 'v3')
            expected_hash = self._hash_password(password, user_data['salt'], hash_version)
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
                 security_level: SecurityLevel, full_name: str,
                 email: str = "", created_by: str = "",
                 force_password_change: bool = True) -> tuple[bool, str]:
        """Add a new user (requires SUPER level — DAC root only)."""
        if not self.check_security_clearance(SecurityLevel.SUPER):
            return False, "Insufficient privileges — only the DAC superuser can create users"

        if security_level == SecurityLevel.SUPER:
            return False, "Cannot create additional SUPER accounts — root is unique"

        normalized = username.strip().lower()
        if not normalized:
            return False, "Username cannot be empty"
        if normalized in self.user_database:
            return False, "Username already exists"

        # SUPER bypasses password strength rules — no holdbacks for root
        if not self.is_super_user:
            valid, message = self.validate_password_strength(password)
            if not valid:
                return False, message

        salt = self._generate_salt()
        self.user_database[normalized] = {
            "password_hash": self._hash_password(password, salt, "v3"),
            "salt": salt,
            "hash_version": "v3",
            "security_level": security_level,
            "role": role,
            "full_name": full_name,
            "email": email,
            "created_by": created_by or self.current_user,
            "failed_attempts": 0,
            "locked_until": None,
            "last_login": None,
            "created_at": time.time(),
            "force_password_change": force_password_change,
        }

        self._save_users_to_file()
        self._log_audit_event('user_created', self.current_user, {'new_user': normalized})
        return True, f"User {username} created successfully"

    def change_password(self, username: str, old_password: str, new_password: str) -> tuple[bool, str]:
        """Change user password. Username lookup is case-insensitive."""
        # Normalize to lowercase — matches authenticate_user() behavior
        normalized = username.lower()
        if normalized not in self.user_database:
            return False, "User not found"

        user_data = self.user_database[normalized]

        # Verify old password (skip if force password change)
        if not user_data.get('force_password_change', False):
            hash_version = user_data.get('hash_version', 'v1')
            expected_hash = self._hash_password(old_password, user_data['salt'], hash_version)
            if expected_hash != user_data['password_hash']:
                return False, "Current password incorrect"

        # Validate new password strength
        valid, message = self.validate_password_strength(new_password)
        if not valid:
            return False, message

        # Update password
        salt = self._generate_salt()
        user_data['password_hash'] = self._hash_password(new_password, salt, "v3")
        user_data['salt'] = salt
        user_data['hash_version'] = "v3"
        user_data['failed_attempts'] = 0  # Reset failed attempts
        user_data['force_password_change'] = False  # Reset force change flag

        self._save_users_to_file()

        self._log_audit_event('password_changed', normalized)
        logger.info(f"Password changed for user '{normalized}'")
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
        """Reset user lockout (requires SUPER level — DAC root only)."""
        if not self.check_security_clearance(SecurityLevel.SUPER):
            return False, "Insufficient privileges — only the DAC superuser can reset lockouts"

        if username not in self.user_database:
            return False, "User not found"

        user_data = self.user_database[username]
        user_data['failed_attempts'] = 0
        user_data['locked_until'] = None
        
        self._save_users_to_file()

        self._log_audit_event('lockout_reset', self.current_user, {'target_user': username})
        return True, f"Lockout reset for user {username}"

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users for management display"""
        users_list = []
        for username, data in self.user_database.items():
            sec_level = data.get('security_level', SecurityLevel.BASIC)
            users_list.append({
                'username': username,
                'full_name': data.get('full_name', ''),
                'tier': self._LEVEL_TO_TIER.get(sec_level, 'BASIC') if isinstance(sec_level, SecurityLevel) else 'BASIC',
                'status': 'LOCKED' if data.get('locked_until') and time.time() < data.get('locked_until') else 'ACTIVE',
                'created_at': datetime.fromtimestamp(data.get('created_at', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                'last_login': datetime.fromtimestamp(data.get('last_login')).strftime('%Y-%m-%d %H:%M:%S') if data.get('last_login') else "Never",
                'email': data.get('email', '')
            })
        return users_list

    def delete_user(self, username: str, requestor: str) -> bool:
        """Delete a user (requires SUPER level — DAC root only)."""
        if not self.check_security_clearance(SecurityLevel.SUPER):
            return False

        if username not in self.user_database:
            return False

        if username == 'supernova':
            return False  # Root is permanent

        if username == requestor:
            return False  # Cannot delete yourself

        del self.user_database[username]
        self._save_users_to_file()
        self._log_audit_event('user_deleted', requestor, {'deleted_user': username})
        return True

    def update_user_details(self, username: str, full_name: str, email: str, tier_name: str, status: str, requestor: str) -> bool:
        """Update user details (requires SUPER level — DAC root only)."""
        if not self.check_security_clearance(SecurityLevel.SUPER):
            return False

        if username not in self.user_database:
            return False

        user_data = self.user_database[username]
        user_data['full_name'] = full_name
        user_data['email'] = email

        # Update tier/security level using canonical map
        if tier_name and tier_name in self._TIER_MAP:
            user_data['security_level'], user_data['role'] = self._TIER_MAP[tier_name]

        # Update status (Lock/Unlock)
        if status == "LOCKED":
             user_data['locked_until'] = time.time() + 31536000 # Lock for a year
        elif status == "ACTIVE":
             user_data['locked_until'] = None
             user_data['failed_attempts'] = 0

        self._save_users_to_file()
        self._log_audit_event('user_updated', requestor, {'updated_user': username})
        return True

    def force_password_reset(self, username: str, requestor: str) -> bool:
        """Force a user to reset their password on next login"""
        if not self.check_security_clearance(SecurityLevel.SUPER):
            return False

        if username not in self.user_database:
            return False
            
        self.user_database[username]['force_password_change'] = True
        self._save_users_to_file()
        self._log_audit_event('password_reset_forced', requestor, {'target_user': username})
        return True

    def has_permission(self, username: str, permission: str) -> bool:
        """Check if user has specific permission"""
        user_info = self.get_user_info() # Gets info for current_user
        if user_info.get('username') != username:
             # If asking for another user, we'd need to load them temporarily or check static roles
             # For now, assume we are checking current user's permission
             return False
        
        return permission in user_info.get('permissions', [])



# Backward compatibility - keep old SecurityManager as alias
SecurityManager = EnhancedSecurityManager

# Global security manager instance
security_manager = EnhancedSecurityManager()