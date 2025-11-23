"""
DiagAutoClinicOS - Security Manager Module
Professional 25-Brand Diagnostic Suite
"""

import logging
import os
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security levels for the system"""
    BASIC = 1
    STANDARD = 2
    ADVANCED = 3
    PROFESSIONAL = 4
    ADMIN = 5

class UserRole(Enum):
    """User roles for the system"""
    VIEWER = "viewer"
    TECHNICIAN = "technician"
    SPECIALIST = "specialist"
    ADMIN = "admin"

class SecurityManager:
    """Security management for DiagAutoClinicOS"""
    
    def __init__(self):
        self.current_user = None
        self.session_active = False
        self.session_expiry = None
        self.security_level = SecurityLevel.BASIC
        self.user_role = UserRole.VIEWER
        
        # Demo user database
        self.users = {
            "demo": {
                "password": "demo",
                "security_level": SecurityLevel.BASIC,
                "role": UserRole.TECHNICIAN,
                "full_name": "Demo User"
            },
            "admin": {
                "password": "admin123", 
                "security_level": SecurityLevel.ADMIN,
                "role": UserRole.ADMIN,
                "full_name": "Administrator"
            },
            "technician": {
                "password": "tech123",
                "security_level": SecurityLevel.STANDARD, 
                "role": UserRole.TECHNICIAN,
                "full_name": "Technician User"
            },
            "user": {
                "password": "user123",
                "security_level": SecurityLevel.BASIC,
                "role": UserRole.VIEWER,
                "full_name": "Regular User"
            }
        }
        
        logger.info("SecurityManager initialized")
    
    def authenticate_user(self, username: str, password: str) -> tuple[bool, str]:
        """Authenticate a user with username and password"""
        try:
            if username in self.users:
                user_data = self.users[username]
                if user_data["password"] == password:
                    self.current_user = username
                    self.security_level = user_data["security_level"]
                    self.user_role = user_data["role"]
                    self.session_active = True
                    self.session_expiry = datetime.now() + timedelta(hours=8)
                    
                    logger.info(f"User {username} authenticated successfully")
                    return True, "Login successful"
                else:
                    logger.warning(f"Invalid password for user {username}")
                    return False, "Invalid password"
            else:
                logger.warning(f"Unknown user: {username}")
                return False, "Invalid username"
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False, f"Authentication error: {e}"
    
    def logout(self):
        """Logout current user"""
        if self.current_user:
            user_info = self.get_user_info()
            logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            session_duration = "Unknown"
            
            if self.session_expiry:
                # Calculate session duration
                try:
                    # We can't get login time directly, but we can estimate session duration
                    # For demo purposes, we'll use a standard 8-hour session
                    session_duration = "8 hours (standard session)"
                except:
                    session_duration = "Unknown"
            
            logger.info(f"✓ Logout successful: {user_info['full_name']} ({self.current_user}) | "
                       f"Security Level: {user_info['security_level']} | "
                       f"Session Duration: {session_duration} | "
                       f"Logout Time: {logout_time}")
        else:
            logger.info("✓ Logout completed (no active session)")
            
        self.current_user = None
        self.session_active = False
        self.session_expiry = None
        self.security_level = SecurityLevel.BASIC
        self.user_role = UserRole.VIEWER
    
    def get_security_level(self) -> SecurityLevel:
        """Get current security level"""
        return self.security_level
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        if not self.current_user or not self.session_active:
            return {
                "full_name": "Guest",
                "security_level": "NONE",
                "role": "guest",
                "session_expiry": 0
            }
        
        user_data = self.users.get(self.current_user, {})
        return {
            "full_name": user_data.get("full_name", self.current_user),
            "security_level": self.security_level.name,
            "role": self.user_role.value,
            "session_expiry": self.session_expiry.timestamp() if self.session_expiry else 0
        }
    
    def is_session_valid(self) -> bool:
        """Check if current session is still valid"""
        if not self.session_active or not self.session_expiry:
            return False
        return datetime.now() < self.session_expiry
    
    def extend_session(self, hours: int = 8):
        """Extend current session"""
        if self.session_active:
            self.session_expiry = datetime.now() + timedelta(hours=hours)
            logger.info(f"Session extended for {hours} hours")

# Global security manager instance
security_manager = SecurityManager()