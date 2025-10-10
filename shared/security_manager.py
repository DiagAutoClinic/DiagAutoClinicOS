#!/usr/bin/env python3
"""
Security Manager Module - Comprehensive Security and Authentication
Handles user authentication, security levels, and secure operations
"""

import logging
import hashlib
import hmac
import secrets
import time
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    BASIC = 1      # Basic operations - DTC reading, live data
    STANDARD = 2   # Standard diagnostics - adaptations, resets
    ADVANCED = 3   # Advanced functions - coding, calibrations
    DEALER = 4     # Dealer-level - security access, programming
    FACTORY = 5    # Factory-level - full system access

class UserRole(Enum):
    TECHNICIAN = "technician"
    SUPERVISOR = "supervisor"
    DEALER = "dealer"
    FACTORY = "factory"
    ADMIN = "admin"

class SecurityManager:
    """Comprehensive security management for diagnostic operations"""
    
    def __init__(self):
        self.current_user = None
        self.user_roles = {}
        self.security_level = SecurityLevel.BASIC
        self.session_token = None
        self.session_expiry = None
        self.failed_attempts = 0
        self.lockout_until = None
        self.audit_log = []
        
        # Load user database (in production, use proper database)
        self._load_user_database()
        
    def _load_user_database(self):
        """Load user database with secure hashed passwords"""
        # In production, this would be from a secure database
        self.user_database = {
            "tech1": {
                "password_hash": self._hash_password("tech123"),
                "role": UserRole.TECHNICIAN,
                "security_level": SecurityLevel.STANDARD,
                "full_name": "John Technician"
            },
            "tech2": {
                "password_hash": self._hash_password("tech456"),
                "role": UserRole.TECHNICIAN,
                "security_level": SecurityLevel.STANDARD,
                "full_name": "Jane Technician"
            },
            "supervisor": {
                "password_hash": self._hash_password("super789"),
                "role": UserRole.SUPERVISOR,
                "security_level": SecurityLevel.ADVANCED,
                "full_name": "Supervisor User"
            },
            "dealer": {
                "password_hash": self._hash_password("dealer012"),
                "role": UserRole.DEALER,
                "security_level": SecurityLevel.DEALER,
                "full_name": "Dealer User"
            },
            "admin": {
                "password_hash": self._hash_password("admin345"),
                "role": UserRole.ADMIN,
                "security_level": SecurityLevel.FACTORY,
                "full_name": "Administrator"
            }
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash password with salt using secure method"""
        salt = "secure_salt_constant"  # In production, use per-user salt
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str]:
        """Authenticate user with comprehensive security checks"""
        
        # Check if system is locked out
        if self.lockout_until and time.time() < self.lockout_until:
            remaining = int(self.lockout_until - time.time())
            return False, f"System locked out. Try again in {remaining} seconds."
        
        # Validate inputs
        if not username or not password:
            self._log_security_event("empty_credentials", username)
            return False, "Username and password required"
        
        # Check user exists
        if username not in self.user_database:
            self._handle_failed_attempt()
            self._log_security_event("invalid_user", username)
            return False, "Invalid credentials"
        
        user_data = self.user_database[username]
        
        # Verify password
        password_hash = self._hash_password(password)
        if not hmac.compare_digest(password_hash, user_data['password_hash']):
            self._handle_failed_attempt()
            self._log_security_event("invalid_password", username)
            return False, "Invalid credentials"
        
        # Successful authentication
        self.current_user = username
        self.security_level = user_data['security_level']
        self.session_token = secrets.token_urlsafe(32)
        self.session_expiry = time.time() + 3600  # 1 hour session
        self.failed_attempts = 0
        self.lockout_until = None
        
        # Log successful login
        self._log_security_event("login_success", username, 
                               f"Security level: {self.security_level.name}")
        
        return True, f"Authentication successful. Welcome {user_data['full_name']}"
    
    def _handle_failed_attempt(self):
        """Handle failed authentication attempts with lockout"""
        self.failed_attempts += 1
        
        # Progressive lockout
        if self.failed_attempts >= 5:
            self.lockout_until = time.time() + 900  # 15 minutes
            self._log_security_event("account_lockout", "system", 
                                   f"Failed attempts: {self.failed_attempts}")
        elif self.failed_attempts >= 3:
            self.lockout_until = time.time() + 300  # 5 minutes
    
    def validate_session(self) -> bool:
        """Validate current session"""
        if not self.session_token or not self.session_expiry:
            return False
        
        if time.time() > self.session_expiry:
            self._log_security_event("session_expired", self.current_user)
            self.logout()
            return False
        
        # Refresh session expiry on validation
        self.session_expiry = time.time() + 3600
        return True
    
    def check_security_clearance(self, required_level: SecurityLevel) -> bool:
        """Check if current user has required security level"""
        if not self.validate_session():
            return False
        
        return self.security_level.value >= required_level.value
    
    def get_security_level(self) -> SecurityLevel:
        """Get current security level"""
        return self.security_level if self.validate_session() else SecurityLevel.BASIC
    
    def elevate_security(self, username: str, password: str, 
                        required_level: SecurityLevel) -> Tuple[bool, str]:
        """Elevate security level for specific operation"""
        
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
        """Secure logout with cleanup"""
        if self.current_user:
            self._log_security_event("logout", self.current_user)
        
        self.current_user = None
        self.security_level = SecurityLevel.BASIC
        self.session_token = None
        self.session_expiry = None
    
    def _log_security_event(self, event_type: str, username: str, 
                          details: str = ""):
        """Log security events for audit trail"""
        event = {
            'timestamp': time.time(),
            'event_type': event_type,
            'username': username,
            'details': details,
            'ip_address': 'localhost'  # In production, get real IP
        }
        
        self.audit_log.append(event)
        logger.info(f"SECURITY: {event_type} - {username} - {details}")
    
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Get security audit log"""
        return self.audit_log[-limit:]
    
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
            'session_expiry': self.session_expiry
        }

# Global security manager instance
security_manager = SecurityManager()
