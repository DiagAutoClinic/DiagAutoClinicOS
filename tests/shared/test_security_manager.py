#!/usr/bin/env python3
"""
Comprehensive Security Manager Tests
Tests authentication, authorization, session management, and security features
"""

import pytest
import time
import sys
import os
import tempfile
import json

# Add shared directory to path
shared_path = os.path.join(os.path.dirname(__file__), '..', 'shared')
sys.path.insert(0, shared_path)

from security_manager import (
    SecurityManager, EnhancedSecurityManager, SecurityLevel, UserRole, security_manager
)


@pytest.fixture
def sec_manager():
    """Create fresh security manager for each test"""
    # Use temporary config file
    temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    temp_config.close()
    
    manager = SecurityManager()
    
    yield manager
    
    # Cleanup
    manager.logout()
    try:
        os.unlink(temp_config.name)
    except:
        pass


class TestSecurityManagerInitialization:
    """Test security manager initialization"""
    
    def test_manager_initialization(self, sec_manager):
        """Test security manager initializes correctly"""
        assert sec_manager is not None
        assert sec_manager.current_user is None
        assert sec_manager.security_level == SecurityLevel.BASIC
        assert sec_manager.session_token is None
    
    def test_user_database_initialized(self, sec_manager):
        """Test user database is populated"""
        assert hasattr(sec_manager, 'user_database')
        assert len(sec_manager.user_database) >= 3
        
        # Check default users exist
        assert 'tech1' in sec_manager.user_database
        assert 'supervisor' in sec_manager.user_database
        assert 'admin' in sec_manager.user_database
    
    def test_security_config_loaded(self, sec_manager):
        """Test security configuration is loaded"""
        config = sec_manager.security_config
        
        assert 'session_timeout' in config
        assert 'max_failed_attempts' in config
        assert 'lockout_duration' in config
        assert config['session_timeout'] > 0


class TestPasswordHashing:
    """Test password hashing and security"""
    
    def test_password_hash_generation(self, sec_manager):
        """Test password hash is generated correctly"""
        password = "testpass123"
        salt = sec_manager._generate_salt()
        
        hash1 = sec_manager._hash_password(password, salt)
        hash2 = sec_manager._hash_password(password, salt)
        
        # Same password + salt = same hash
        assert hash1 == hash2
        assert len(hash1) > 0
    
    def test_different_salts_different_hashes(self, sec_manager):
        """Test different salts produce different hashes"""
        password = "testpass123"
        salt1 = sec_manager._generate_salt()
        salt2 = sec_manager._generate_salt()
        
        hash1 = sec_manager._hash_password(password, salt1)
        hash2 = sec_manager._hash_password(password, salt2)
        
        # Same password, different salts = different hashes
        assert hash1 != hash2
    
    def test_salt_generation_uniqueness(self, sec_manager):
        """Test salt generation produces unique values"""
        salts = [sec_manager._generate_salt() for _ in range(100)]
        
        # All salts should be unique
        assert len(salts) == len(set(salts))
    
    def test_salt_length(self, sec_manager):
        """Test salt has appropriate length"""
        salt = sec_manager._generate_salt()
        
        # Should be hex string of 32 bytes = 64 characters
        assert len(salt) == 64
        assert all(c in '0123456789abcdef' for c in salt)


class TestAuthentication:
    """Test user authentication"""
    
    def test_successful_authentication(self, sec_manager):
        """Test successful user authentication"""
        success, message, user_info = sec_manager.authenticate_user('tech1', 'tech123')

        assert success is True
        assert 'Welcome' in message
        assert sec_manager.current_user == 'tech1'
        assert sec_manager.session_token is not None
        assert sec_manager.security_level == SecurityLevel.STANDARD
        assert user_info['username'] == 'tech1'
    
    def test_authentication_wrong_password(self, sec_manager):
        """Test authentication with wrong password"""
        success, message, user_info = sec_manager.authenticate_user('tech1', 'wrongpass')

        assert success is False
        assert 'Invalid credentials' in message
        assert sec_manager.current_user is None
        assert user_info is None
    
    def test_authentication_nonexistent_user(self, sec_manager):
        """Test authentication with non-existent user"""
        success, message, user_info = sec_manager.authenticate_user('nonexistent', 'pass')

        assert success is False
        assert sec_manager.current_user is None
        assert user_info is None

    def test_authentication_empty_credentials(self, sec_manager):
        """Test authentication with empty credentials"""
        success1, msg1, ui1 = sec_manager.authenticate_user('', 'pass')
        success2, msg2, ui2 = sec_manager.authenticate_user('user', '')

        assert success1 is False
        assert success2 is False
        assert ui1 is None
        assert ui2 is None

    def test_authentication_case_insensitive_username(self, sec_manager):
        """Test username is case-insensitive"""
        success1, _, ui1 = sec_manager.authenticate_user('TECH1', 'tech123')
        sec_manager.logout()
        success2, _, ui2 = sec_manager.authenticate_user('Tech1', 'tech123')

        assert success1 is True
        assert success2 is True
        assert ui1 is not None
        assert ui2 is not None
    
    @pytest.mark.parametrize("username,password,expected_level", [
        ('tech1', 'tech123', SecurityLevel.STANDARD),
        ('supervisor', 'super789', SecurityLevel.ADVANCED),
        ('admin', 'admin345', SecurityLevel.FACTORY),
    ])
    def test_different_user_security_levels(self, sec_manager, username,
                                           password, expected_level):
        """Test different users have correct security levels"""
        success, _, user_info = sec_manager.authenticate_user(username, password)

        assert success is True
        assert sec_manager.security_level == expected_level
        assert user_info is not None


class TestSessionManagement:
    """Test session management and validation"""
    
    def test_session_token_generation(self, sec_manager):
        """Test session token is generated on login"""
        sec_manager.authenticate_user('tech1', 'tech123')

        assert sec_manager.session_token is not None
        assert len(sec_manager.session_token) > 0
        assert sec_manager.session_expiry is not None
    
    def test_session_validation_valid(self, sec_manager):
        """Test valid session validation"""
        sec_manager.authenticate_user('tech1', 'tech123')

        assert sec_manager.validate_session() is True
    
    def test_session_validation_no_token(self, sec_manager):
        """Test session validation without login"""
        assert sec_manager.validate_session() is False
    
    def test_session_expiration(self, sec_manager):
        """Test session expires after timeout"""
        # Use short timeout for testing
        sec_manager.security_config['session_timeout'] = 1  # 1 second

        sec_manager.authenticate_user('tech1', 'tech123')
        assert sec_manager.validate_session() is True

        # Wait for expiration
        time.sleep(1.5)

        assert sec_manager.validate_session() is False
        assert sec_manager.current_user is None

    def test_session_sliding_expiration(self, sec_manager):
        """Test session expiration extends on validation"""
        sec_manager.security_config['session_timeout'] = 2  # 2 seconds

        sec_manager.authenticate_user('tech1', 'tech123')
        initial_expiry = sec_manager.session_expiry

        time.sleep(0.5)
        sec_manager.validate_session()  # Should extend expiration

        new_expiry = sec_manager.session_expiry
        assert new_expiry > initial_expiry


class TestSecurityClearance:
    """Test security clearance checks"""
    
    def test_check_clearance_sufficient(self, sec_manager):
        """Test clearance check with sufficient level"""
        sec_manager.authenticate_user('admin', 'admin345')  # FACTORY level
        
        assert sec_manager.check_security_clearance(SecurityLevel.BASIC) is True
        assert sec_manager.check_security_clearance(SecurityLevel.STANDARD) is True
        assert sec_manager.check_security_clearance(SecurityLevel.ADVANCED) is True
        assert sec_manager.check_security_clearance(SecurityLevel.FACTORY) is True
    
    def test_check_clearance_insufficient(self, sec_manager):
        """Test clearance check with insufficient level"""
        sec_manager.authenticate_user('tech1', 'tech123')  # STANDARD level
        
        assert sec_manager.check_security_clearance(SecurityLevel.BASIC) is True
        assert sec_manager.check_security_clearance(SecurityLevel.STANDARD) is True
        assert sec_manager.check_security_clearance(SecurityLevel.ADVANCED) is False
        assert sec_manager.check_security_clearance(SecurityLevel.FACTORY) is False
    
    def test_check_clearance_no_session(self, sec_manager):
        """Test clearance check without valid session"""
        assert sec_manager.check_security_clearance(SecurityLevel.BASIC) is False
    
    def test_get_security_level(self, sec_manager):
        """Test getting current security level"""
        # No session
        assert sec_manager.get_security_level() == SecurityLevel.BASIC
        
        # With session
        sec_manager.authenticate_user('supervisor', 'super789')
        assert sec_manager.get_security_level() == SecurityLevel.ADVANCED


class TestSecurityElevation:
    """Test security level elevation"""
    
    def test_elevate_security_success(self, sec_manager):
        """Test successful security elevation"""
        # Login as tech
        sec_manager.authenticate_user('tech1', 'tech123')
        initial_level = sec_manager.security_level
        
        # Elevate to admin
        success, message = sec_manager.elevate_security(
            'admin', 'admin345', SecurityLevel.FACTORY
        )
        
        assert success is True
        assert sec_manager.security_level > initial_level
    
    def test_elevate_security_insufficient_privilege(self, sec_manager):
        """Test elevation with insufficient target privilege"""
        sec_manager.authenticate_user('tech1', 'tech123')  # STANDARD
        
        # Try to elevate to FACTORY (tech1 can't do this)
        success, message = sec_manager.elevate_security(
            'tech1', 'tech123', SecurityLevel.FACTORY
        )
        
        assert success is False
        assert 'Insufficient privileges' in message
    
    def test_elevate_security_invalid_credentials(self, sec_manager):
        """Test elevation with invalid credentials"""
        sec_manager.authenticate_user('tech1', 'tech123')
        
        success, message = sec_manager.elevate_security(
            'admin', 'wrongpass', SecurityLevel.FACTORY
        )
        
        assert success is False


class TestFailedAttemptHandling:
    """Test failed authentication attempt handling"""
    
    def test_failed_attempt_counter(self, sec_manager):
        """Test failed attempts are counted"""
        initial_attempts = sec_manager.failed_attempts

        sec_manager.authenticate_user('tech1', 'wrongpass')

        assert sec_manager.failed_attempts > initial_attempts

    def test_user_lockout_after_failures(self, sec_manager):
        """Test user lockout after multiple failures"""
        # Attempt failed logins
        for _ in range(3):
            sec_manager.authenticate_user('tech1', 'wrongpass')

        # User should be locked
        success, message, user_info = sec_manager.authenticate_user('tech1', 'tech123')

        assert success is False
        assert 'locked' in message.lower()
        assert user_info is None

    def test_system_lockout_after_max_failures(self, sec_manager):
        """Test system-wide lockout after max failures"""
        sec_manager.security_config['max_failed_attempts'] = 3

        # Fail 3 times
        for _ in range(3):
            sec_manager.authenticate_user('fake', 'wrongpass')

        # System should be locked
        assert sec_manager.lockout_until is not None

        # Even valid login should fail
        success, message, user_info = sec_manager.authenticate_user('tech1', 'tech123')
        assert success is False
        assert 'locked' in message.lower()
        assert user_info is None
    
    def test_failed_attempts_reset_on_success(self, sec_manager):
        """Test failed attempts reset after successful login"""
        # Make some failures
        sec_manager.authenticate_user('tech1', 'wrongpass')
        sec_manager.authenticate_user('tech1', 'wrongpass')
        
        assert sec_manager.failed_attempts > 0
        
        # Successful login should reset
        sec_manager.authenticate_user('tech1', 'tech123')
        
        assert sec_manager.failed_attempts == 0


class TestLogout:
    """Test logout functionality"""
    
    def test_logout_clears_session(self, sec_manager):
        """Test logout clears all session data"""
        sec_manager.authenticate_user('tech1', 'tech123')
        
        assert sec_manager.current_user is not None
        assert sec_manager.session_token is not None
        
        sec_manager.logout()
        
        assert sec_manager.current_user is None
        assert sec_manager.session_token is None
        assert sec_manager.session_expiry is None
        assert sec_manager.security_level == SecurityLevel.BASIC
    
    def test_logout_without_login(self, sec_manager):
        """Test logout when not logged in"""
        # Should not raise error
        sec_manager.logout()
        
        assert sec_manager.current_user is None


class TestAuditLogging:
    """Test security audit logging"""
    
    def test_successful_login_logged(self, sec_manager):
        """Test successful login is logged"""
        initial_log_size = len(sec_manager.audit_log)
        
        sec_manager.authenticate_user('tech1', 'tech123')
        
        assert len(sec_manager.audit_log) > initial_log_size
        
        # Check log entry
        last_entry = sec_manager.audit_log[-1]
        assert last_entry['event_type'] == 'login_success'
        assert last_entry['username'] == 'tech1'
    
    def test_failed_login_logged(self, sec_manager):
        """Test failed login is logged"""
        initial_log_size = len(sec_manager.audit_log)
        
        sec_manager.authenticate_user('tech1', 'wrongpass')
        
        assert len(sec_manager.audit_log) > initial_log_size
    
    def test_logout_logged(self, sec_manager):
        """Test logout is logged"""
        sec_manager.authenticate_user('tech1', 'tech123')
        initial_log_size = len(sec_manager.audit_log)
        
        sec_manager.logout()
        
        assert len(sec_manager.audit_log) > initial_log_size
        last_entry = sec_manager.audit_log[-1]
        assert last_entry['event_type'] == 'logout'
    
    def test_get_audit_log(self, sec_manager):
        """Test retrieving audit log"""
        sec_manager.authenticate_user('tech1', 'tech123')
        sec_manager.logout()
        
        log = sec_manager.get_audit_log(limit=10)
        
        assert isinstance(log, list)
        assert len(log) > 0
    
    def test_audit_log_limit(self, sec_manager):
        """Test audit log respects limit"""
        # Generate many events
        for _ in range(50):
            sec_manager.authenticate_user('fake', 'wrong')
        
        log = sec_manager.get_audit_log(limit=10)
        
        assert len(log) <= 10


class TestPasswordValidation:
    """Test password strength validation"""
    
    def test_password_minimum_length(self, sec_manager):
        """Test password minimum length requirement"""
        valid, message = sec_manager.validate_password_strength('short')
        
        assert valid is False
        assert 'at least' in message.lower()
    
    def test_password_sufficient_length(self, sec_manager):
        """Test password with sufficient length"""
        valid, message = sec_manager.validate_password_strength('LongPass123')
        
        assert valid is True
    
    def test_password_mixed_case_requirement(self, sec_manager):
        """Test password mixed case requirement"""
        if sec_manager.security_config['require_mixed_case']:
            # All lowercase
            valid1, msg1 = sec_manager.validate_password_strength('alllowercase123')
            assert valid1 is False
            
            # All uppercase
            valid2, msg2 = sec_manager.validate_password_strength('ALLUPPERCASE123')
            assert valid2 is False
            
            # Mixed case
            valid3, msg3 = sec_manager.validate_password_strength('MixedCase123')
            assert valid3 is True
    
    def test_password_number_requirement(self, sec_manager):
        """Test password number requirement"""
        if sec_manager.security_config['require_numbers']:
            # No numbers
            valid1, msg1 = sec_manager.validate_password_strength('NoNumbersHere')
            assert valid1 is False
            
            # With numbers
            valid2, msg2 = sec_manager.validate_password_strength('WithNum123')
            assert valid2 is True


class TestUserManagement:
    """Test user management functions"""
    
    def test_get_user_info_authenticated(self, sec_manager):
        """Test getting user info when authenticated"""
        sec_manager.authenticate_user('tech1', 'tech123')
        
        user_info = sec_manager.get_user_info()
        
        assert user_info['username'] == 'tech1'
        assert 'full_name' in user_info
        assert 'role' in user_info
        assert 'security_level' in user_info
    
    def test_get_user_info_not_authenticated(self, sec_manager):
        """Test getting user info when not authenticated"""
        user_info = sec_manager.get_user_info()
        
        assert user_info == {}
    
    def test_add_user_requires_admin(self, sec_manager):
        """Test adding user requires FACTORY privileges"""
        sec_manager.authenticate_user('tech1', 'tech123')  # STANDARD level
        
        success, message = sec_manager.add_user(
            'newuser', 'NewPass123', UserRole.TECHNICIAN,
            SecurityLevel.BASIC, 'New User'
        )
        
        assert success is False
        assert 'Insufficient privileges' in message
    
    def test_add_user_success(self, sec_manager):
        """Test successfully adding new user"""
        sec_manager.authenticate_user('admin', 'admin345')  # FACTORY level
        
        success, message = sec_manager.add_user(
            'newtech', 'NewPass123', UserRole.TECHNICIAN,
            SecurityLevel.STANDARD, 'New Technician'
        )
        
        assert success is True
        assert 'newtech' in sec_manager.user_database
        
        # Verify new user can login
        sec_manager.logout()
        success2, _, user_info2 = sec_manager.authenticate_user('newtech', 'NewPass123')
        assert success2 is True
        assert user_info2 is not None
    
    def test_add_user_duplicate_username(self, sec_manager):
        """Test adding user with existing username"""
        sec_manager.authenticate_user('admin', 'admin345')
        
        success, message = sec_manager.add_user(
            'tech1', 'Pass123', UserRole.TECHNICIAN,
            SecurityLevel.BASIC, 'Duplicate'
        )
        
        assert success is False
        assert 'already exists' in message.lower()
    
    def test_add_user_weak_password(self, sec_manager):
        """Test adding user with weak password"""
        sec_manager.authenticate_user('admin', 'admin345')
        
        success, message = sec_manager.add_user(
            'newuser', 'weak', UserRole.TECHNICIAN,
            SecurityLevel.BASIC, 'New User'
        )
        
        assert success is False


class TestPasswordChange:
    """Test password change functionality"""
    
    def test_change_password_success(self, sec_manager):
        """Test successfully changing password"""
        success, message = sec_manager.change_password(
            'tech1', 'tech123', 'NewPass123'
        )
        
        assert success is True
        
        # Verify can login with new password
        sec_manager.logout()
        success2, _, ui2 = sec_manager.authenticate_user('tech1', 'NewPass123')
        assert success2 is True
        assert ui2 is not None

        # Old password should not work
        sec_manager.logout()
        success3, _, ui3 = sec_manager.authenticate_user('tech1', 'tech123')
        assert success3 is False
        assert ui3 is None
    
    def test_change_password_wrong_old_password(self, sec_manager):
        """Test changing password with wrong old password"""
        success, message = sec_manager.change_password(
            'tech1', 'wrongold', 'NewPass123'
        )
        
        assert success is False
        assert 'incorrect' in message.lower()
    
    def test_change_password_weak_new_password(self, sec_manager):
        """Test changing to weak new password"""
        success, message = sec_manager.change_password(
            'tech1', 'tech123', 'weak'
        )
        
        assert success is False


class TestLockoutReset:
    """Test user lockout reset functionality"""
    
    def test_reset_lockout_requires_admin(self, sec_manager):
        """Test resetting lockout requires FACTORY privileges"""
        sec_manager.authenticate_user('tech1', 'tech123')
        
        success, message = sec_manager.reset_user_lockout('supervisor')
        
        assert success is False
        assert 'Insufficient privileges' in message
    
    def test_reset_lockout_success(self, sec_manager):
        """Test successfully resetting user lockout"""
        # Lock a user
        for _ in range(3):
            sec_manager.authenticate_user('supervisor', 'wrongpass')
        
        # Admin resets lockout
        sec_manager.authenticate_user('admin', 'admin345')
        success, message = sec_manager.reset_user_lockout('supervisor')
        
        assert success is True
        
        # User should be able to login now
        sec_manager.logout()
        success2, _, ui2 = sec_manager.authenticate_user('supervisor', 'super789')
        assert success2 is True
        assert ui2 is not None
    
    def test_reset_lockout_nonexistent_user(self, sec_manager):
        """Test resetting lockout for non-existent user"""
        sec_manager.authenticate_user('admin', 'admin345')
        
        success, message = sec_manager.reset_user_lockout('nonexistent')
        
        assert success is False
        assert 'not found' in message.lower()


class TestConfigurationPersistence:
    """Test configuration loading and persistence"""
    
    def test_load_default_config(self):
        """Test loading default configuration"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        temp_file.close()
        
        manager = EnhancedSecurityManager(config_path=temp_file.name)
        
        # Should have default values
        assert manager.security_config['session_timeout'] == 3600
        assert manager.security_config['max_failed_attempts'] == 5
        
        os.unlink(temp_file.name)
    
    def test_load_custom_config(self):
        """Test loading custom configuration"""
        custom_config = {
            'session_timeout': 1800,
            'max_failed_attempts': 3,
            'lockout_duration': 600
        }
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(custom_config, temp_file)
        temp_file.close()
        
        manager = EnhancedSecurityManager(config_path=temp_file.name)
        
        assert manager.security_config['session_timeout'] == 1800
        assert manager.security_config['max_failed_attempts'] == 3
        
        os.unlink(temp_file.name)


class TestSecurityEventPersistence:
    """Test security event persistence"""
    
    def test_critical_events_persisted(self, sec_manager):
        """Test critical security events are persisted to file"""
        # Perform login
        sec_manager.authenticate_user('tech1', 'tech123')
        
        # Check if security audit log file exists
        if os.path.exists('security_audit.log'):
            with open('security_audit.log', 'r') as f:
                content = f.read()
                assert 'login_success' in content


class TestGlobalSecurityManagerInstance:
    """Test global security_manager instance"""
    
    def test_global_instance_exists(self):
        """Test global security_manager instance exists"""
        assert security_manager is not None
        assert isinstance(security_manager, EnhancedSecurityManager)
    
    def test_global_instance_functional(self):
        """Test global instance is functional"""
        # Save initial state
        initial_user = security_manager.current_user

        success, _, user_info = security_manager.authenticate_user('admin', 'admin345')
        assert success is True
        assert user_info is not None

        # Clean up
        security_manager.logout()


class TestSecurityEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_multiple_logins_same_user(self, sec_manager):
        """Test logging in multiple times with same user"""
        sec_manager.authenticate_user('tech1', 'tech123')
        token1 = sec_manager.session_token
        
        # Login again
        sec_manager.authenticate_user('tech1', 'tech123')
        token2 = sec_manager.session_token
        
        # Should get new token
        assert token1 != token2
    
    def test_session_validation_after_logout(self, sec_manager):
        """Test session validation after logout"""
        sec_manager.authenticate_user('tech1', 'tech123')
        assert sec_manager.validate_session() is True
        
        sec_manager.logout()
        assert sec_manager.validate_session() is False
    
    def test_unicode_in_credentials(self, sec_manager):
        """Test handling unicode characters in credentials"""
        success, _ = sec_manager.authenticate_user('tëch1', 'pāss')
        
        # Should handle gracefully (fail validation)
        assert success is False
    
    def test_very_long_username(self, sec_manager):
        """Test handling very long username"""
        long_username = 'a' * 1000
        success, _ = sec_manager.authenticate_user(long_username, 'pass')
        
        assert success is False
    
    def test_sql_injection_attempt(self, sec_manager):
        """Test SQL injection attempts are handled safely"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
        ]
        
        for malicious in malicious_inputs:
            success, _ = sec_manager.authenticate_user(malicious, 'pass')
            assert success is False


class TestConcurrentSessions:
    """Test handling of concurrent sessions"""
    
    def test_single_user_single_session(self, sec_manager):
        """Test user can only have one active session"""
        sec_manager.authenticate_user('tech1', 'tech123')
        token1 = sec_manager.session_token
        
        # Login again should replace session
        sec_manager.authenticate_user('tech1', 'tech123')
        token2 = sec_manager.session_token
        
        assert token1 != token2


class TestSecurityManagerPerformance:
    """Test security manager performance"""
    
    @pytest.mark.benchmark
    def test_authentication_performance(self, sec_manager, benchmark):
        """Benchmark authentication performance"""
        def auth():
            sec_manager.authenticate_user('tech1', 'tech123')
            sec_manager.logout()
        
        benchmark(auth)
    
    @pytest.mark.benchmark
    def test_session_validation_performance(self, sec_manager, benchmark):
        """Benchmark session validation performance"""
        sec_manager.authenticate_user('tech1', 'tech123')
        
        result = benchmark(sec_manager.validate_session)
        assert result is True
    
    def test_bulk_authentication_attempts(self, sec_manager):
        """Test performance with many authentication attempts"""
        import time
        
        start = time.time()
        
        for _ in range(100):
            sec_manager.authenticate_user('tech1', 'tech123')
            sec_manager.logout()
        
        elapsed = time.time() - start
        
        # Should complete 100 auth cycles in reasonable time
        assert elapsed < 5.0  # 5 seconds for 100 attempts


class TestUserRoles:
    """Test user roles functionality"""
    
    def test_user_role_assignment(self, sec_manager):
        """Test users have correct roles assigned"""
        tech_data = sec_manager.user_database['tech1']
        assert tech_data['role'] == UserRole.TECHNICIAN
        
        admin_data = sec_manager.user_database['admin']
        assert admin_data['role'] == UserRole.ADMIN
    
    def test_role_in_user_info(self, sec_manager):
        """Test role is included in user info"""
        sec_manager.authenticate_user('tech1', 'tech123')
        
        user_info = sec_manager.get_user_info()
        assert 'role' in user_info
        assert user_info['role'] == UserRole.TECHNICIAN.value


class TestTimingAttackProtection:
    """Test protection against timing attacks"""
    
    def test_constant_time_password_comparison(self, sec_manager):
        """Test password comparison uses constant time"""
        import time
        
        # Measure time for correct password
        start1 = time.time()
        sec_manager.authenticate_user('tech1', 'tech123')
        elapsed1 = time.time() - start1
        sec_manager.logout()
        
        # Measure time for wrong password
        start2 = time.time()
        sec_manager.authenticate_user('tech1', 'wrong123')
        elapsed2 = time.time() - start2

        # Times should be similar (within 100ms tolerance for timing variations)
        # Note: This is a basic check; true constant-time requires more rigorous testing
        assert abs(elapsed1 - elapsed2) < 0.1


class TestSecurityLevelEnum:
    """Test SecurityLevel enumeration"""
    
    def test_security_levels_defined(self):
        """Test all security levels are defined"""
        assert SecurityLevel.BASIC.value == 1
        assert SecurityLevel.STANDARD.value == 2
        assert SecurityLevel.ADVANCED.value == 3
        assert SecurityLevel.DEALER.value == 4
        assert SecurityLevel.FACTORY.value == 5
    
    def test_security_level_comparison(self):
        """Test security levels can be compared"""
        assert SecurityLevel.FACTORY.value > SecurityLevel.BASIC.value
        assert SecurityLevel.ADVANCED.value < SecurityLevel.FACTORY.value
        assert SecurityLevel.STANDARD.value == 2


class TestUserRoleEnum:
    """Test UserRole enumeration"""
    
    def test_user_roles_defined(self):
        """Test all user roles are defined"""
        assert UserRole.TECHNICIAN.value == "technician"
        assert UserRole.SUPERVISOR.value == "supervisor"
        assert UserRole.DEALER.value == "dealer"
        assert UserRole.FACTORY.value == "factory"
        assert UserRole.ADMIN.value == "admin"


class TestSessionTokenSecurity:
    """Test session token security features"""
    
    def test_session_token_uniqueness(self, sec_manager):
        """Test session tokens are unique"""
        tokens = set()
        
        for _ in range(10):
            sec_manager.authenticate_user('tech1', 'tech123')
            tokens.add(sec_manager.session_token)
            sec_manager.logout()
        
        # All tokens should be unique
        assert len(tokens) == 10
    
    def test_session_token_length(self, sec_manager):
        """Test session token has sufficient length"""
        sec_manager.authenticate_user('tech1', 'tech123')
        
        # Should be URL-safe base64 token of sufficient length
        assert len(sec_manager.session_token) >= 64
    
    def test_session_token_cleared_on_logout(self, sec_manager):
        """Test session token is cleared on logout"""
        sec_manager.authenticate_user('tech1', 'tech123')
        assert sec_manager.session_token is not None
        
        sec_manager.logout()
        assert sec_manager.session_token is None


class TestAuditLogStructure:
    """Test audit log entry structure"""
    
    def test_audit_log_entry_structure(self, sec_manager):
        """Test audit log entries have correct structure"""
        sec_manager.authenticate_user('tech1', 'tech123')
        
        log_entries = sec_manager.get_audit_log()
        
        for entry in log_entries:
            assert 'timestamp' in entry
            assert 'event_type' in entry
            assert 'username' in entry
            assert isinstance(entry['timestamp'], (int, float))
    
    def test_audit_log_chronological_order(self, sec_manager):
        """Test audit log entries are in chronological order"""
        # Generate multiple events
        sec_manager.authenticate_user('tech1', 'tech123')
        sec_manager.logout()
        sec_manager.authenticate_user('supervisor', 'super789')
        sec_manager.logout()
        
        log_entries = sec_manager.get_audit_log()
        
        # Check timestamps are increasing
        timestamps = [entry['timestamp'] for entry in log_entries]
        assert timestamps == sorted(timestamps)


class TestPasswordHashingSecurity:
    """Test password hashing security properties"""
    
    def test_hash_irreversibility(self, sec_manager):
        """Test password hash cannot be easily reversed"""
        password = "testpass123"
        salt = sec_manager._generate_salt()
        hash_value = sec_manager._hash_password(password, salt)
        
        # Hash should be different from password
        assert hash_value != password
        
        # Hash should not contain password substring
        assert password not in hash_value
    
    def test_different_passwords_different_hashes(self, sec_manager):
        """Test different passwords produce different hashes"""
        salt = sec_manager._generate_salt()
        
        hash1 = sec_manager._hash_password("password1", salt)
        hash2 = sec_manager._hash_password("password2", salt)
        
        assert hash1 != hash2
    
    def test_hash_deterministic(self, sec_manager):
        """Test hashing is deterministic with same inputs"""
        password = "testpass123"
        salt = sec_manager._generate_salt()
        
        hash1 = sec_manager._hash_password(password, salt)
        hash2 = sec_manager._hash_password(password, salt)
        hash3 = sec_manager._hash_password(password, salt)
        
        assert hash1 == hash2 == hash3


class TestUserDatabaseSecurity:
    """Test user database security"""
    
    def test_passwords_not_stored_plaintext(self, sec_manager):
        """Test passwords are not stored in plaintext"""
        for username, user_data in sec_manager.user_database.items():
            # Should have password_hash, not password
            assert 'password_hash' in user_data
            assert 'password' not in user_data
            
            # Hash should not be a common password
            hash_value = user_data['password_hash']
            assert hash_value not in ['password', '123456', 'admin']
    
    def test_user_database_contains_salt(self, sec_manager):
        """Test user database contains salt for each user"""
        for username, user_data in sec_manager.user_database.items():
            assert 'salt' in user_data
            assert len(user_data['salt']) > 0


class TestLockoutTimers:
    """Test lockout timer functionality"""
    
    def test_user_lockout_duration(self, sec_manager):
        """Test user lockout has time limit"""
        # Lock user
        for _ in range(3):
            sec_manager.authenticate_user('tech1', 'wrongpass')
        
        user_data = sec_manager.user_database['tech1']
        
        if 'locked_until' in user_data:
            assert user_data['locked_until'] > time.time()
    
    def test_system_lockout_duration(self, sec_manager):
        """Test system lockout has time limit"""
        sec_manager.security_config['max_failed_attempts'] = 3
        
        # Trigger system lockout
        for _ in range(3):
            sec_manager.authenticate_user('fake', 'wrong')
        
        if sec_manager.lockout_until:
            assert sec_manager.lockout_until > time.time()


class TestFailedAttemptReset:
    """Test failed attempt counter reset"""
    
    def test_user_failed_attempts_reset_on_success(self, sec_manager):
        """Test user failed attempts reset after successful login"""
        # Make some failures
        sec_manager.authenticate_user('tech1', 'wrong1')
        sec_manager.authenticate_user('tech1', 'wrong2')
        
        user_data = sec_manager.user_database['tech1']
        assert user_data.get('failed_attempts', 0) > 0
        
        # Successful login
        sec_manager.authenticate_user('tech1', 'tech123')
        
        user_data = sec_manager.user_database['tech1']
        assert user_data.get('failed_attempts', 0) == 0


class TestLastLoginTracking:
    """Test last login timestamp tracking"""
    
    def test_last_login_updated(self, sec_manager):
        """Test last login timestamp is updated"""
        sec_manager.authenticate_user('tech1', 'tech123')
        
        user_data = sec_manager.user_database['tech1']
        
        assert 'last_login' in user_data
        assert user_data['last_login'] is not None
        # Should be recent (within last few seconds)
        assert time.time() - user_data['last_login'] < 5


class TestUserCreationTimestamp:
    """Test user creation timestamp"""
    
    def test_users_have_creation_timestamp(self, sec_manager):
        """Test all users have creation timestamp"""
        for username, user_data in sec_manager.user_database.items():
            assert 'created_at' in user_data
            assert isinstance(user_data['created_at'], (int, float))


class TestSecurityConfigValidation:
    """Test security configuration validation"""
    
    def test_timeout_positive(self, sec_manager):
        """Test session timeout is positive"""
        assert sec_manager.security_config['session_timeout'] > 0
    
    def test_max_attempts_positive(self, sec_manager):
        """Test max failed attempts is positive"""
        assert sec_manager.security_config['max_failed_attempts'] > 0
    
    def test_lockout_duration_positive(self, sec_manager):
        """Test lockout duration is positive"""
        assert sec_manager.security_config['lockout_duration'] > 0
    
    def test_password_min_length_reasonable(self, sec_manager):
        """Test password minimum length is reasonable"""
        min_length = sec_manager.security_config['password_min_length']
        assert 6 <= min_length <= 20


class TestMultipleFailedUsers:
    """Test handling of multiple users with failed attempts"""
    
    def test_different_users_independent_lockout(self, sec_manager):
        """Test different users have independent lockout counters"""
        # Fail tech1
        sec_manager.authenticate_user('tech1', 'wrong')
        
        # Fail supervisor  
        sec_manager.authenticate_user('supervisor', 'wrong')
        
        tech_data = sec_manager.user_database['tech1']
        super_data = sec_manager.user_database['supervisor']
        
        # Each should have their own counter
        assert tech_data.get('failed_attempts', 0) >= 1
        assert super_data.get('failed_attempts', 0) >= 1


class TestCleanupOnLogout:
    """Test proper cleanup on logout"""
    
    def test_all_session_data_cleared(self, sec_manager):
        """Test all session-related data is cleared on logout"""
        sec_manager.authenticate_user('tech1', 'tech123')
        
        # Verify session data exists
        assert sec_manager.current_user is not None
        assert sec_manager.session_token is not None
        assert sec_manager.session_expiry is not None
        
        sec_manager.logout()
        
        # Verify all cleared
        assert sec_manager.current_user is None
        assert sec_manager.session_token is None
        assert sec_manager.session_expiry is None
        assert sec_manager.security_level == SecurityLevel.BASIC


class TestAuthenticationReturnValues:
    """Test authentication return value consistency"""
    
    def test_authenticate_returns_tuple(self, sec_manager):
        """Test authenticate_user returns (bool, str, dict) tuple"""
        result = sec_manager.authenticate_user('tech1', 'tech123')

        assert isinstance(result, tuple)
        assert len(result) == 3
        assert isinstance(result[0], bool)
        assert isinstance(result[1], str)
        assert isinstance(result[2], (dict, type(None)))
    
    def test_all_auth_methods_return_tuples(self, sec_manager):
        """Test all authentication-related methods return tuples"""
        sec_manager.authenticate_user('admin', 'admin345')
        
        # Test various methods
        result1 = sec_manager.add_user('test', 'Test123', UserRole.TECHNICIAN,
                                       SecurityLevel.BASIC, 'Test')
        result2 = sec_manager.change_password('admin', 'admin345', 'NewPass123')
        result3 = sec_manager.elevate_security('admin', 'admin345', SecurityLevel.FACTORY)
        
        for result in [result1, result2, result3]:
            assert isinstance(result, tuple)
            assert len(result) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
