#!/usr/bin/env python3
"""
Complete Enhanced Security Manager - All Features Fixed
Version: 2.0.1 - Production Ready
"""

import hashlib
import hmac
import secrets
import time
import json
import os
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    BASIC = 1
    STANDARD = 2
    ADVANCED = 3
    DEALER = 4
    FACTORY = 5

class UserRole(Enum):
    TECHNICIAN = "technician"
    SUPERVISOR = "supervisor"
    DEALER = "dealer"
    FACTORY = "factory"
    ADMIN = "admin"

class EnhancedSecurityManager:
    """Complete fixed security manager with all features"""
    
    def __init__(self, config_path: str = "security_config.json"):
        self.current_user = None
        self.security_level = SecurityLevel.BASIC
        self.session_token = None
        self.session_expiry = None
        self.failed_attempts = 0
        self.lockout_until = None
        self.audit_log = []
        self.config_path = config_path
        
        # Security configuration
        self.security_config = self._load_security_config()
        self._initialize_user_database()
        
        logger.info("Security Manager initialized successfully")
    
    def _load_security_config(self) -> Dict:
        """Load security configuration with defaults"""
        default_config = {
            "session_timeout": 3600,  # 1 hour
            "max_failed_attempts": 5,
            "lockout_duration": 900,  # 15 minutes
            "password_min_length": 8,
            "require_mixed_case": True,
            "require_numbers": True,
            "require_special_chars": False  # Set to False for easier testing
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
                logger.info("Security configuration loaded from file")
        except Exception as e:
            logger.warning(f"Could not load security config: {e}, using defaults")
        
        return default_config
    
    def _generate_salt(self) -> str:
        """Generate cryptographically secure salt"""
        return secrets.token_hex(32)
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with provided salt using PBKDF2 - FIXED"""
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        ).hex()
    
    def _create_user_entry(self, password: str, role: UserRole, 
                          security_level: SecurityLevel, full_name: str) -> Dict:
        """Create properly initialized user entry with correct hash"""
        salt = self._generate_salt()
        password_hash = self._hash_password(password, salt)
        
        return {
            "password_hash": password_hash,
            "salt": salt,
            "role": role,
            "security_level": security_level,
            "full_name": full_name,
            "failed_attempts": 0,
            "last_login": None,
            "created_at": time.time()
        }
    
    def _initialize_user_database(self):
        """Initialize user database with proper password storage - FIXED"""
        self.user_database = {
            "tech1": self._create_user_entry(
                "tech123",
                UserRole.TECHNICIAN,
                SecurityLevel.STANDARD,
                "John Technician"
            ),
            "supervisor": self._create_user_entry(
                "super789",
                UserRole.SUPERVISOR,
                SecurityLevel.ADVANCED,
                "Supervisor User"
            ),
            "admin": self._create_user_entry(
                "admin345",
                UserRole.ADMIN,
                SecurityLevel.FACTORY,
                "Administrator"
            ),
            # Additional test user with basic access
            "test": self._create_user_entry(
                "test123",
                UserRole.TECHNICIAN,
                SecurityLevel.BASIC,
                "Test User"
            )
        }
        logger.info(f"User database initialized with {len(self.user_database)} users")
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """Validate password meets security requirements"""
        if len(password) < self.security_config["password_min_length"]:
            return False, f"Password must be at least {self.security_config['password_min_length']} characters"
        
        if self.security_config["require_mixed_case"]:
            if not any(c.islower() for c in password) or not any(c.isupper() for c in password):
                return False, "Password must contain both uppercase and lowercase letters"
        
        if self.security_config["require_numbers"]:
            if not any(c.isdigit() for c in password):
                return False, "Password must contain at least one number"
        
        if self.security_config["require_special_chars"]:
            if not any(not c.isalnum() for c in password):
                return False, "Password must contain at least one special character"
        
        return True, "Password meets security requirements"
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Enhanced authentication with comprehensive security checks - FIXED"""
        
        # System lockout check
        if self.lockout_until and time.time() < self.lockout_until:
            remaining = int(self.lockout_until - time.time())
            return False, f"System locked. Try again in {remaining} seconds."
        
        # Input validation
        if not username or not password:
            self._log_security_event("empty_credentials", username or "unknown")
            return False, "Username and password required"
        
        # Sanitize username
        username = username.strip().lower()
        
        # Check user exists
        if username not in self.user_database:
            self._handle_failed_attempt()
            self._log_security_event("invalid_user", username)
            return False, "Invalid credentials"
        
        user_data = self.user_database[username]
        
        # Check individual user lockout
        if user_data.get('locked_until') and time.time() < user_data['locked_until']:
            remaining = int(user_data['locked_until'] - time.time())
            return False, f"Account locked. Try again in {remaining} seconds."
        
        # Verify password with correct salt - FIXED
        salt = user_data['salt']
        password_hash = self._hash_password(password, salt)
        
        # Use constant-time comparison to prevent timing attacks
        if not hmac.compare_digest(password_hash, user_data['password_hash']):
            self._handle_failed_attempt(username)
            self._log_security_event("invalid_password", username)
            return False, "Invalid credentials"
        
        # Successful authentication
        self.current_user = username
        self.security_level = user_data['security_level']
        self.session_token = secrets.token_urlsafe(64)
        self.session_expiry = time.time() + self.security_config["session_timeout"]
        self.failed_attempts = 0
        self.lockout_until = None
        
        # Update user data
        user_data['failed_attempts'] = 0
        user_data['last_login'] = time.time()
        user_data.pop('locked_until', None)
        
        self._log_security_event("login_success", username, 
                               f"Security level: {self.security_level.name}")
        
        return True, f"Welcome {user_data['full_name']}"
    
    def _handle_failed_attempt(self, username: str = None):
        """Handle failed authentication with progressive lockout"""
        self.failed_attempts += 1
        
        if username and username in self.user_database:
            user_data = self.user_database[username]
            user_data['failed_attempts'] = user_data.get('failed_attempts', 0) + 1
            
            # User-specific lockout after 3 failed attempts
            if user_data['failed_attempts'] >= 3:
                user_data['locked_until'] = time.time() + 300  # 5 minutes
                logger.warning(f"User {username} locked for 5 minutes")
        
        # System-wide lockout after max failed attempts
        if self.failed_attempts >= self.security_config["max_failed_attempts"]:
            self.lockout_until = time.time() + self.security_config["lockout_duration"]
            self._log_security_event("system_lockout", "system", 
                                   f"Failed attempts: {self.failed_attempts}")
            logger.warning(f"System locked for {self.security_config['lockout_duration']} seconds")
    
    def validate_session(self) -> bool:
        """Enhanced session validation with sliding expiration"""
        if not self.session_token or not self.session_expiry:
            return False
        
        if time.time() > self.session_expiry:
            self._log_security_event("session_expired", self.current_user or "unknown")
            self.logout()
            return False
        
        # Auto-extend session on validation (sliding expiration)
        self.session_expiry = time.time() + self.security_config["session_timeout"]
        return True
    
    def check_security_clearance(self, required_level: SecurityLevel) -> bool:
        """Enhanced security clearance check"""
        if not self.validate_session():
            logger.debug("Security clearance check failed: Invalid session")
            return False
        
        has_clearance = self.security_level.value >= required_level.value
        
        if not has_clearance:
            logger.warning(f"Insufficient clearance: Required {required_level.name}, "
                         f"Current {self.security_level.name}")
        
        return has_clearance
    
    def get_security_level(self) -> SecurityLevel:
        """Get current security level"""
        return self.security_level if self.validate_session() else SecurityLevel.BASIC
    
    def elevate_security(self, username: str, password: str, 
                        required_level: SecurityLevel) -> Tuple[bool, str]:
        """Enhanced security elevation with re-authentication"""
        
        if not self.validate_session():
            return False, "Session expired. Please log in again."
        
        # Re-authenticate for elevation
        success, message = self.authenticate_user(username, password)
        if not success:
            return False, message
        
        # Check if new level meets requirement
        if self.security_level.value >= required_level.value:
            self._log_security_event("security_elevated", username,
                                   f"Elevated to: {required_level.name}")
            return True, f"Security elevated to {required_level.name}"
        else:
            return False, f"Insufficient privileges for {required_level.name}"
    
    def logout(self):
        """Secure logout with comprehensive cleanup"""
        if self.current_user:
            self._log_security_event("logout", self.current_user)
            logger.info(f"User {self.current_user} logged out")
        
        # Clear all session data
        self.current_user = None
        self.security_level = SecurityLevel.BASIC
        self.session_token = None
        self.session_expiry = None
    
    def _log_security_event(self, event_type: str, username: str, 
                          details: str = ""):
        """Enhanced security event logging"""
        event = {
            'timestamp': time.time(),
            'event_type': event_type,
            'username': username,
            'details': details,
            'session_token': self.session_token[:16] if self.session_token else None
        }
        
        self.audit_log.append(event)
        
        # Log to file for critical events
        if event_type in ['login_success', 'login_failed', 'security_elevated', 
                         'logout', 'system_lockout']:
            logger.info(f"SECURITY EVENT: {event_type} - {username} - {details}")
            self._persist_security_event(event)
    
    def _persist_security_event(self, event: Dict):
        """Persist critical security events to file"""
        try:
            log_file = "security_audit.log"
            with open(log_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            logger.error(f"Failed to persist security event: {e}")
    
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Get security audit log with limit"""
        return self.audit_log[-limit:] if self.audit_log else []
    
    def get_user_info(self) -> Dict:
        """Get current user information"""
        if not self.current_user or not self.validate_session():
            return {}
        
        user_data = self.user_database.get(self.current_user, {})
        return {
            'username': self.current_user,
            'full_name': user_data.get('full_name', ''),
            'role': user_data.get('role', UserRole.TECHNICIAN).value,
            'security_level': self.security_level.name,
            'session_expiry': self.session_expiry,
            'last_login': user_data.get('last_login')
        }
    
    def add_user(self, username: str, password: str, role: UserRole,
                security_level: SecurityLevel, full_name: str) -> Tuple[bool, str]:
        """Add new user to database (requires ADMIN privileges)"""
        if not self.check_security_clearance(SecurityLevel.FACTORY):
            return False, "Insufficient privileges to add users"
        
        if username.lower() in self.user_database:
            return False, "Username already exists"
        
        # Validate password
        valid, message = self.validate_password_strength(password)
        if not valid:
            return False, message
        
        # Create user
        self.user_database[username.lower()] = self._create_user_entry(
            password, role, security_level, full_name
        )
        
        self._log_security_event("user_added", username, 
                               f"By: {self.current_user}")
        
        return True, f"User {username} created successfully"
    
    def change_password(self, username: str, old_password: str, 
                       new_password: str) -> Tuple[bool, str]:
        """Change user password"""
        # Verify current credentials
        success, message = self.authenticate_user(username, old_password)
        if not success:
            return False, "Current password incorrect"
        
        # Validate new password
        valid, message = self.validate_password_strength(new_password)
        if not valid:
            return False, message
        
        # Update password
        user_data = self.user_database[username.lower()]
        salt = self._generate_salt()
        user_data['salt'] = salt
        user_data['password_hash'] = self._hash_password(new_password, salt)
        
        self._log_security_event("password_changed", username)
        
        return True, "Password changed successfully"
    
    def reset_user_lockout(self, username: str) -> Tuple[bool, str]:
        """Reset user lockout (requires ADMIN privileges)"""
        if not self.check_security_clearance(SecurityLevel.FACTORY):
            return False, "Insufficient privileges"
        
        if username.lower() not in self.user_database:
            return False, "User not found"
        
        user_data = self.user_database[username.lower()]
        user_data['failed_attempts'] = 0
        user_data.pop('locked_until', None)
        
        self._log_security_event("lockout_reset", username,
                               f"By: {self.current_user}")
        
        return True, f"Lockout reset for {username}"

# Global security manager instance
security_manager = EnhancedSecurityManager()
