# AutoDiag Suite - Advanced Password Hashing Implementation

## Critical Security Enhancement: Beyond SHA-256

**SHA-256 is too fast and well-known to crackers. We need something slower and off the radar.**

This document provides advanced password hashing alternatives that are secure, slow, and less targeted by automated attacks.

## Table of Contents

1. [Current Vulnerability Analysis](#current-vulnerability-analysis)
2. [Advanced Hashing Alternatives](#advanced-hashing-alternatives)
3. [Implementation Strategy](#implementation-strategy)
4. [Custom Hashing Algorithm](#custom-hashing-algorithm)
5. **[Security Best Practices](#security-best-practices)**
6. [Migration Strategy](#migration-strategy)

---

## Current Vulnerability Analysis

### SHA-256 Problems:
- **Too Fast**: Can compute billions of hashes per second on modern hardware
- **Well-Known**: All cracking tools optimized for SHA-256
- **No Salt**: Current implementation likely missing proper salting
- **No Iterations**: Single hash computation provides no protection

### Current Implementation Issues:
```python
# CURRENT VULNERABLE CODE (example)
def hash_password(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hash_value):
    return hash_password(password) == hash_value
```

**Vulnerabilities:**
- Rainbow table attacks
- GPU-accelerated brute force
- Dictionary attacks
- No protection against timing attacks

---

## Advanced Hashing Alternatives

### 1. **Argon2id** (Recommended)
- **Status**: Winner of Password Hashing Competition (2015)
- **Security**: Memory-hard function, resistant to GPU/ASIC attacks
- **Speed**: Configurable memory and time cost
- **Implementation**: `argon2-cffi` library

```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

class SecurePasswordManager:
    def __init__(self):
        # Memory-hard configuration to slow down attackers
        self.ph = PasswordHasher(
            memory_cost=2**16,  # 64 MB memory cost
            time_cost=3,        # 3 iterations
            parallelism=2,      # 2 parallel threads
            hash_len=32,        # 32-byte hash length
            salt_len=16         # 16-byte salt
        )
    
    def hash_password(self, password):
        """Hash password with Argon2id"""
        if not self._validate_password_strength(password):
            raise ValueError("Password does not meet security requirements")
        
        return self.ph.hash(password)
    
    def verify_password(self, password, hash_value):
        """Verify password against hash with timing attack protection"""
        try:
            return self.ph.verify(hash_value, password)
        except VerifyMismatchError:
            return False
    
    def _validate_password_strength(self, password):
        """Validate password meets security requirements"""
        if len(password) < 12:
            return False
        
        # Check for complexity
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        return has_upper and has_lower and has_digit and has_special
```

### 2. **Scrypt** (Alternative)
- **Status**: NIST approved, memory-hard function
- **Security**: Resistant to hardware attacks
- **Speed**: Configurable CPU and memory cost
- **Implementation**: `scrypt` library

```python
import scrypt
import os
import binascii

class ScryptPasswordManager:
    def __init__(self):
        self.salt_length = 32
        self.n = 2**14  # CPU cost parameter
        self.r = 8      # Block size parameter
        self.p = 1      # Parallelization parameter
    
    def hash_password(self, password):
        """Hash password with Scrypt"""
        salt = os.urandom(self.salt_length)
        key = scrypt.hash(
            password.encode('utf-8'),
            salt,
            N=self.n,
            r=self.r,
            p=self.p,
            buflen=32
        )
        return f"${self.n}${self.r}${self.p}${binascii.hexlify(salt).decode()}${binascii.hexlify(key).decode()}"
    
    def verify_password(self, password, hash_value):
        """Verify password against Scrypt hash"""
        try:
            parts = hash_value.split('$')
            if len(parts) != 6:
                return False
            
            n, r, p = int(parts[1]), int(parts[2]), int(parts[3])
            salt = binascii.unhexlify(parts[4])
            stored_key = binascii.unhexlify(parts[5])
            
            key = scrypt.hash(
                password.encode('utf-8'),
                salt,
                N=n, r=r, p=p,
                buflen=32
            )
            
            return key == stored_key
        except:
            return False
```

### 3. **Custom Multi-Stage Hashing** (Off the Radar)
- **Status**: Custom implementation, not in standard cracking tools
- **Security**: Multiple hash functions with custom transformations
- **Speed**: Very slow, custom timing
- **Implementation**: Custom algorithm

```python
import hashlib
import os
import time
import random

class CustomPasswordManager:
    def __init__(self):
        self.salt_length = 32
        self.iterations = 10000  # High iteration count
        self.hash_functions = [
            hashlib.sha3_256,
            hashlib.blake2b,
            hashlib.sha3_512,
            hashlib.sha512
        ]
    
    def hash_password(self, password):
        """Custom multi-stage password hashing"""
        # Add timing variation to prevent timing attacks
        time.sleep(random.uniform(0.001, 0.01))
        
        # Generate salt
        salt = os.urandom(self.salt_length)
        
        # Initial hash with salt
        current_hash = hashlib.sha3_256(salt + password.encode()).digest()
        
        # Multi-stage hashing with different algorithms
        for i in range(self.iterations):
            # Select hash function based on iteration
            hash_func = self.hash_functions[i % len(self.hash_functions)]
            
            # Mix in iteration number and salt
            data = current_hash + salt + str(i).encode() + password.encode()
            
            # Apply hash function
            current_hash = hash_func(data).digest()
            
            # Add computational delay
            if i % 1000 == 0:
                time.sleep(0.001)
        
        # Final transformation
        final_hash = hashlib.sha3_512(current_hash + salt).hexdigest()
        
        # Store with metadata
        return f"custom_v1${self.iterations}${binascii.hexlify(salt).decode()}${final_hash}"
    
    def verify_password(self, password, hash_value):
        """Verify password against custom hash"""
        try:
            parts = hash_value.split('$')
            if len(parts) != 4 or parts[0] != 'custom_v1':
                return False
            
            iterations = int(parts[1])
            salt = binascii.unhexlify(parts[2])
            stored_hash = parts[3]
            
            # Recompute hash
            current_hash = hashlib.sha3_256(salt + password.encode()).digest()
            
            for i in range(iterations):
                hash_func = self.hash_functions[i % len(self.hash_functions)]
                data = current_hash + salt + str(i).encode() + password.encode()
                current_hash = hash_func(data).digest()
                
                if i % 1000 == 0:
                    time.sleep(0.001)
            
            final_hash = hashlib.sha3_512(current_hash + salt).hexdigest()
            
            return final_hash == stored_hash
        except:
            return False
```

---

## Implementation Strategy

### Phase 1: Immediate Security Upgrade
```python
# Replace current auth.py with secure implementation
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

class SecureAuthManager:
    def __init__(self):
        self.ph = PasswordHasher(
            memory_cost=2**16,  # 64 MB
            time_cost=3,        # 3 iterations
            parallelism=2,      # 2 threads
            hash_len=32,
            salt_len=16
        )
    
    def create_user(self, username, password):
        """Create user with secure password hashing"""
        if not self._validate_password(password):
            raise ValueError("Password does not meet security requirements")
        
        hashed_password = self.ph.hash(password)
        
        # Store in database with additional security
        user_data = {
            'username': username,
            'password_hash': hashed_password,
            'created_at': time.time(),
            'failed_attempts': 0,
            'locked_until': None,
            'password_changed': time.time()
        }
        
        return self._save_user(user_data)
    
    def authenticate_user(self, username, password):
        """Authenticate user with rate limiting and logging"""
        # Check if account is locked
        if self._is_account_locked(username):
            raise AccountLockedError("Account temporarily locked due to failed attempts")
        
        # Get user data
        user = self._get_user(username)
        if not user:
            self._log_failed_attempt(username, "User not found")
            self._increment_failed_attempts(username)
            return False
        
        # Verify password
        try:
            if self.ph.verify(user['password_hash'], password):
                # Reset failed attempts on successful login
                self._reset_failed_attempts(username)
                self._log_successful_login(username)
                return True
            else:
                self._log_failed_attempt(username, "Invalid password")
                self._increment_failed_attempts(username)
                return False
        except VerifyMismatchError:
            self._log_failed_attempt(username, "Invalid password")
            self._increment_failed_attempts(username)
            return False
    
    def _validate_password(self, password):
        """Validate password meets security requirements"""
        # Minimum length
        if len(password) < 12:
            return False
        
        # Complexity requirements
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        return has_upper and has_lower and has_digit and has_special
    
    def _is_account_locked(self, username):
        """Check if account is locked due to failed attempts"""
        user = self._get_user(username)
        if not user:
            return False
        
        if user.get('locked_until'):
            if time.time() < user['locked_until']:
                return True
            else:
                # Unlock account after timeout
                self._unlock_account(username)
        
        return False
    
    def _increment_failed_attempts(self, username):
        """Increment failed login attempts with automatic lockout"""
        user = self._get_user(username)
        if not user:
            return
        
        failed_attempts = user.get('failed_attempts', 0) + 1
        
        # Lock account after 5 failed attempts for 15 minutes
        if failed_attempts >= 5:
            lockout_duration = 15 * 60  # 15 minutes
            user['locked_until'] = time.time() + lockout_duration
        
        user['failed_attempts'] = failed_attempts
        self._update_user(user)
    
    def _reset_failed_attempts(self, username):
        """Reset failed attempts counter on successful login"""
        user = self._get_user(username)
        if user:
            user['failed_attempts'] = 0
            user['locked_until'] = None
            self._update_user(user)
```

### Phase 2: Password Migration
```python
class PasswordMigrationManager:
    def __init__(self, old_auth_manager, new_auth_manager):
        self.old_auth = old_auth_manager
        self.new_auth = new_auth_manager
    
    def migrate_user_password(self, username, old_password):
        """Migrate user from old to new password hashing"""
        # Verify old password
        if self.old_auth.verify_password(username, old_password):
            # Hash with new algorithm
            new_hash = self.new_auth.hash_password(old_password)
            
            # Update database
            self._update_password_hash(username, new_hash, 'migrated')
            
            return True
        return False
    
    def upgrade_password_on_login(self, username, password):
        """Transparently upgrade password hash on successful login"""
        # Try old authentication first
        if self.old_auth.verify_password(username, password):
            # Upgrade to new hash
            new_hash = self.new_auth.hash_password(password)
            self._update_password_hash(username, new_hash, 'upgraded')
            return True
        
        # Try new authentication
        if self.new_auth.verify_password(username, password):
            return True
        
        return False
```

---

## Security Best Practices

### 1. **Password Policy Enforcement**
```python
class PasswordPolicy:
    def __init__(self):
        self.min_length = 12
        self.max_length = 128
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_digits = True
        self.require_special = True
        self.max_consecutive_chars = 3
        self.banned_passwords = self._load_banned_passwords()
    
    def validate_password(self, password):
        """Comprehensive password validation"""
        errors = []
        
        # Length check
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters")
        
        if len(password) > self.max_length:
            errors.append(f"Password must not exceed {self.max_length} characters")
        
        # Character requirements
        if self.require_uppercase and not any(c.isupper() for c in password):
            errors.append("Password must contain uppercase letters")
        
        if self.require_lowercase and not any(c.islower() for c in password):
            errors.append("Password must contain lowercase letters")
        
        if self.require_digits and not any(c.isdigit() for c in password):
            errors.append("Password must contain digits")
        
        if self.require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain special characters")
        
        # Consecutive character check
        if self._has_consecutive_chars(password):
            errors.append(f"Password cannot have more than {self.max_consecutive_chars} consecutive identical characters")
        
        # Banned password check
        if password.lower() in self.banned_passwords:
            errors.append("Password is too common, please choose a different one")
        
        return len(errors) == 0, errors
    
    def _has_consecutive_chars(self, password):
        """Check for consecutive identical characters"""
        consecutive_count = 1
        for i in range(1, len(password)):
            if password[i].lower() == password[i-1].lower():
                consecutive_count += 1
                if consecutive_count > self.max_consecutive_chars:
                    return True
            else:
                consecutive_count = 1
        return False
```

### 2. **Rate Limiting and Monitoring**
```python
class SecurityMonitor:
    def __init__(self):
        self.failed_attempts = {}
        self.lockout_duration = 15 * 60  # 15 minutes
        self.max_attempts = 5
    
    def log_authentication_attempt(self, username, success, ip_address):
        """Log authentication attempts for security monitoring"""
        timestamp = time.time()
        
        # Log to security database
        self._log_security_event({
            'username': username,
            'success': success,
            'ip_address': ip_address,
            'timestamp': timestamp,
            'user_agent': self._get_user_agent()
        })
        
        # Update failed attempts tracking
        if not success:
            self._update_failed_attempts(username, ip_address, timestamp)
    
    def _update_failed_attempts(self, username, ip_address, timestamp):
        """Update failed attempts with IP-based tracking"""
        key = f"{username}:{ip_address}"
        
        if key not in self.failed_attempts:
            self.failed_attempts[key] = []
        
        self.failed_attempts[key].append(timestamp)
        
        # Clean old attempts (older than 1 hour)
        cutoff_time = timestamp - 3600
        self.failed_attempts[key] = [t for t in self.failed_attempts[key] if t > cutoff_time]
    
    def is_rate_limited(self, username, ip_address):
        """Check if user/IP combination is rate limited"""
        key = f"{username}:{ip_address}"
        
        if key not in self.failed_attempts:
            return False
        
        recent_attempts = [t for t in self.failed_attempts[key] if time.time() - t < 300]  # 5 minutes
        
        return len(recent_attempts) >= self.max_attempts
```

### 3. **Session Security**
```python
class SecureSessionManager:
    def __init__(self):
        self.sessions = {}
        self.session_timeout = 30 * 60  # 30 minutes
        self.max_sessions_per_user = 3
    
    def create_session(self, user_id, ip_address, user_agent):
        """Create secure session with validation"""
        # Check maximum sessions
        user_sessions = [s for s in self.sessions.values() if s['user_id'] == user_id]
        if len(user_sessions) >= self.max_sessions_per_user:
            self._terminate_oldest_session(user_id)
        
        # Generate secure session ID
        session_id = self._generate_secure_session_id()
        
        # Create session data
        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'created_at': time.time(),
            'last_activity': time.time(),
            'csrf_token': self._generate_csrf_token()
        }
        
        self.sessions[session_id] = session_data
        
        return session_id
    
    def validate_session(self, session_id, ip_address, user_agent):
        """Validate session with IP and user agent checking"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        # Check timeout
        if time.time() - session['last_activity'] > self.session_timeout:
            self.destroy_session(session_id)
            return False
        
        # Check IP address (optional strict checking)
        if session['ip_address'] != ip_address:
            # Log potential session hijacking
            self._log_suspicious_activity(session_id, 'IP address mismatch')
            return False
        
        # Check user agent
        if session['user_agent'] != user_agent:
            # Log potential session hijacking
            self._log_suspicious_activity(session_id, 'User agent mismatch')
            return False
        
        # Update last activity
        session['last_activity'] = time.time()
        
        return True
    
    def _generate_secure_session_id(self):
        """Generate cryptographically secure session ID"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _generate_csrf_token(self):
        """Generate CSRF protection token"""
        import secrets
        return secrets.token_hex(32)
```

---

## Migration Strategy

### Step 1: Install Dependencies
```bash
pip install argon2-cffi
pip install scrypt  # Optional alternative
```

### Step 2: Update Database Schema
```sql
-- Add new password hash field
ALTER TABLE users ADD COLUMN password_hash_new VARCHAR(255);

-- Add migration tracking
ALTER TABLE users ADD COLUMN password_migrated BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN password_migrated_at TIMESTAMP NULL;
```

### Step 3: Implement Gradual Migration
```python
class HybridAuthManager:
    def __init__(self):
        self.old_auth = OldPasswordManager()  # Current SHA-256
        self.new_auth = SecurePasswordManager()  # Argon2id
    
    def authenticate_user(self, username, password):
        """Authenticate with automatic migration"""
        user = self._get_user(username)
        if not user:
            return False
        
        # Check if already migrated
        if user.get('password_migrated'):
            return self.new_auth.verify_password(password, user['password_hash_new'])
        
        # Try old authentication
        if self.old_auth.verify_password(password, user['password_hash']):
            # Migrate to new system
            new_hash = self.new_auth.hash_password(password)
            self._migrate_user_password(user['id'], new_hash)
            return True
        
        return False
    
    def _migrate_user_password(self, user_id, new_hash):
        """Migrate user to new password system"""
        # Update database
        self._update_user_password(user_id, new_hash, True, time.time())
        
        # Log migration
        self._log_password_migration(user_id)
```

### Step 4: Force Password Reset for Weak Passwords
```python
def force_password_reset_for_weak_passwords():
    """Identify and force reset for weak passwords"""
    weak_users = []
    
    # Check all users for weak passwords
    for user in get_all_users():
        if not password_policy.validate_password(user['password']):
            weak_users.append(user['username'])
            send_password_reset_request(user['email'])
    
    return weak_users
```

---

## Conclusion

**SHA-256 is indeed too fast and well-targeted by crackers.** The implementation above provides:

1. **Argon2id**: Industry-standard, memory-hard function
2. **Custom Hashing**: Off the radar, very slow implementation
3. **Comprehensive Security**: Rate limiting, session management, monitoring
4. **Gradual Migration**: Seamless transition from current system
5. **Password Policy**: Strong requirements and banned password checking

**Implementation Priority:**
1. **Week 1**: Implement Argon2id with basic security
2. **Week 2**: Add rate limiting and session security
3. **Week 3**: Implement password policy and monitoring
4. **Week 4**: Migrate existing users and test thoroughly

This approach makes password cracking **prohibitively expensive** and moves us off the standard attack vectors used by script kiddies and automated tools.