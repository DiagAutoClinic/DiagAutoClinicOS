#!/usr/bin/env python3
"""
Verify Superuser Account Script
Checks the superuser account in the database
"""

import os
import sys
import sqlite3

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "shared", "users.db")


def verify_superuser():
    """Verify the superuser account exists and is properly configured"""
    print("=" * 50)
    print("DiagAutoClinicOS - Superuser Account Verification")
    print("=" * 50)
    
    if not os.path.exists(DATABASE_PATH):
        print(f"[X] Database not found at: {DATABASE_PATH}")
        return False
    
    # Connect to database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Check if superuser exists
    cursor.execute("SELECT username, full_name, email, tier, status, force_password_change FROM users WHERE username = ?", ("superuser",))
    user = cursor.fetchone()
    
    if not user:
        print("[X] Superuser account not found in database")
        conn.close()
        return False
    
    username, full_name, email, tier, status, force_password_change = user
    print(f"[+] Found superuser account:")
    print(f"    Username: {username}")
    print(f"    Full Name: {full_name}")
    print(f"    Email: {email}")
    print(f"    Tier: {tier}")
    print(f"    Status: {status}")
    print(f"    Force Password Change: {'Yes' if force_password_change else 'No'}")
    
    # Check permissions
    cursor.execute("SELECT permission FROM user_permissions WHERE username = ?", ("superuser",))
    permissions = cursor.fetchall()
    
    if permissions:
        print(f"\n[+] Permissions ({len(permissions)} total):")
        for perm in permissions:
            print(f"    - {perm[0]}")
    else:
        print("\n[!] No permissions found for superuser")
    
    # Check audit log
    cursor.execute("SELECT action, details FROM audit_log WHERE username = 'system' AND action = 'superuser_reset' ORDER BY timestamp DESC LIMIT 1")
    audit_entry = cursor.fetchone()
    
    if audit_entry:
        print(f"\n[+] Latest audit entry: {audit_entry[0]} - {audit_entry[1]}")
    
    conn.close()
    print("\n" + "=" * 50)
    print("VERIFICATION COMPLETE")
    print("=" * 50)
    return True


if __name__ == "__main__":
    try:
        if verify_superuser():
            print("\n[+] Superuser verification passed!")
        else:
            print("\n[X] Superuser verification failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n[X] Error verifying superuser: {e}")
        sys.exit(1)
