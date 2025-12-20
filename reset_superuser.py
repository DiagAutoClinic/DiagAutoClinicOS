#!/usr/bin/env python3
"""
Reset Superuser Account Script
Resets the superuser account to default credentials
"""

import os
import sys
import sqlite3
import hashlib

# Default superuser settings
DEFAULT_USERNAME = "superuser"
DEFAULT_PASSWORD = "DiagAutoClinicOS_Admin_123!"  # Must be changed on first login
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "diagautoclinic_users.db")


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt"""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + key.hex()


def reset_superuser():
    """Reset the superuser account to default state"""
    print("=" * 50)
    print("DiagAutoClinicOS - Superuser Account Reset")
    print("=" * 50)
    
    if not os.path.exists(DATABASE_PATH):
        print(f"\n[X] Database not found at: {DATABASE_PATH}")
        print("Creating new database with superuser account...")
        
        # Create directory if needed
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT,
                tier TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                password_changed_at TIMESTAMP,
                force_password_change INTEGER DEFAULT 1,
                login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP,
                created_by TEXT,
                notes TEXT
            )
        ''')
        
        # Create permissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                permission TEXT NOT NULL,
                granted_by TEXT,
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(username, permission)
            )
        ''')
        
        # Create audit log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("[+] Database created successfully")
    
    # Connect to database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Hash default password
    password_hash = hash_password(DEFAULT_PASSWORD)
    
    # Check if superuser exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (DEFAULT_USERNAME,))
    existing = cursor.fetchone()
    
    if existing:
        # Update existing superuser
        cursor.execute('''
            UPDATE users SET
                password_hash = ?,
                status = 'active',
                force_password_change = 1,
                login_attempts = 0,
                locked_until = NULL,
                notes = 'Account reset - password must be changed on first login'
            WHERE username = ?
        ''', (password_hash, DEFAULT_USERNAME))
        print(f"\n[+] Superuser account '{DEFAULT_USERNAME}' has been reset")
    else:
        # Create new superuser
        cursor.execute('''
            INSERT INTO users (
                username, password_hash, full_name, email, tier, status,
                force_password_change, created_by, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            DEFAULT_USERNAME,
            password_hash,
            "System Administrator",
            "admin@diagautoclinic.co.za",
            "super_user",
            "active",
            1,
            "system",
            "Default super user account - password must be changed on first login"
        ))
        
        # Add default permissions
        permissions = [
            "user_management", "system_admin", "full_diagnostics",
            "advanced_functions", "security_settings", "audit_logs"
        ]
        for perm in permissions:
            cursor.execute('''
                INSERT OR IGNORE INTO user_permissions (username, permission, granted_by)
                VALUES (?, ?, ?)
            ''', (DEFAULT_USERNAME, perm, "system"))
        
        print(f"\n[+] Superuser account '{DEFAULT_USERNAME}' has been created")
    
    # Add audit log entry
    cursor.execute('''
        INSERT INTO audit_log (username, action, details)
        VALUES (?, ?, ?)
    ''', ("system", "superuser_reset", "Superuser account reset to default"))
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 50)
    print("LOGIN CREDENTIALS:")
    print("=" * 50)
    print(f"  Username: {DEFAULT_USERNAME}")
    print(f"  Password: {DEFAULT_PASSWORD}")
    print("\n[!] You MUST change this password on first login!")
    print("=" * 50)


if __name__ == "__main__":
    try:
        reset_superuser()
        print("\n[+] Superuser reset completed successfully!")
    except Exception as e:
        print(f"\n[X] Error resetting superuser: {e}")
        sys.exit(1)
