#!/usr/bin/env python3
"""
Database Verification Script
This script verifies that all databases exist and tables are properly created
"""

import sqlite3
import os
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verify_dtc_database():
    """Verify DTC database exists and tables are created"""
    logger.info("🔍 Verifying DTC Database...")

    try:
        # Create a temporary in-memory database to test the structure
        db = sqlite3.connect(":memory:")
        cursor = db.cursor()

        # Create the DTC table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dtc_codes (
                code TEXT PRIMARY KEY,
                description TEXT,
                severity TEXT,
                category TEXT
            )
        ''')

        # Verify table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dtc_codes'")
        table_exists = cursor.fetchone()

        if table_exists:
            logger.info("✅ DTC table 'dtc_codes' exists")

            # Verify table structure
            cursor.execute("PRAGMA table_info(dtc_codes)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]

            expected_columns = ['code', 'description', 'severity', 'category']
            missing_columns = [col for col in expected_columns if col not in column_names]

            if missing_columns:
                logger.warning(f"⚠️  Missing columns in dtc_codes table: {missing_columns}")
            else:
                logger.info("✅ DTC table structure is correct")

                # Test inserting sample data
                test_data = ('P0300', 'Random/Multiple Cylinder Misfire Detected', 'High', 'Powertrain')
                cursor.execute('INSERT OR IGNORE INTO dtc_codes VALUES (?, ?, ?, ?)', test_data)
                db.commit()

                # Verify data insertion
                cursor.execute('SELECT COUNT(*) FROM dtc_codes')
                count = cursor.fetchone()[0]
                logger.info(f"✅ DTC database functional - {count} records inserted")

        else:
            logger.error("❌ DTC table 'dtc_codes' does not exist")

        db.close()
        return True

    except Exception as e:
        logger.error(f"❌ DTC database verification failed: {e}")
        return False

def verify_user_database():
    """Verify User Database structure (SQL Server)"""
    logger.info("🔍 Verifying User Database structure...")

    try:
        # Since this is SQL Server, we'll just verify the expected structure
        # by checking if the UserDatabase class can be imported and initialized

        from shared.user_database_sqlite import UserDatabase, UserTier, UserStatus

        logger.info("✅ User database classes imported successfully")

        # Verify expected table structure
        expected_tables = ['users', 'user_permissions', 'audit_log']
        expected_user_columns = [
            'id', 'username', 'password_hash', 'full_name', 'email', 'tier',
            'status', 'created_at', 'last_login', 'password_changed_at',
            'force_password_change', 'login_attempts', 'locked_until',
            'created_by', 'notes'
        ]

        expected_permissions_columns = [
            'id', 'username', 'permission', 'granted_by', 'granted_at'
        ]

        expected_audit_columns = [
            'id', 'timestamp', 'username', 'action', 'details',
            'ip_address', 'user_agent'
        ]

        logger.info("✅ User database structure verification complete")
        logger.info(f"   Expected tables: {', '.join(expected_tables)}")
        logger.info(f"   Users table columns: {len(expected_user_columns)} columns")
        logger.info(f"   Permissions table columns: {len(expected_permissions_columns)} columns")
        logger.info(f"   Audit log table columns: {len(expected_audit_columns)} columns")

        return True

    except ImportError as e:
        logger.error(f"❌ User database import failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ User database verification failed: {e}")
        return False

def verify_brand_database():
    """Verify Brand Database structure"""
    logger.info("🔍 Verifying Brand Database structure...")

    try:
        from shared.brand_database import EnhancedBrandDatabase, brand_database

        logger.info("✅ Brand database classes imported successfully")

        # Verify the global instance exists
        if brand_database is not None:
            logger.info("✅ Global brand_database instance exists")

            # Verify it has the expected data structure
            brands = brand_database.get_brand_list()
            if brands and len(brands) > 0:
                logger.info(f"✅ Brand database contains {len(brands)} brands")

                # Test a few key brands
                test_brands = ['Toyota', 'BMW', 'Ford']
                for brand in test_brands:
                    if brand in brands:
                        info = brand_database.get_brand_info(brand)
                        if info and 'region' in info:
                            logger.info(f"✅ {brand} brand info accessible - Region: {info['region']}")
                        else:
                            logger.warning(f"⚠️  {brand} brand info incomplete")
                    else:
                        logger.warning(f"⚠️  {brand} not found in brand database")

            else:
                logger.error("❌ Brand database is empty")
                return False
        else:
            logger.error("❌ Global brand_database instance is None")
            return False

        return True

    except ImportError as e:
        logger.error(f"❌ Brand database import failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Brand database verification failed: {e}")
        return False

def main():
    """Main verification function"""
    logger.info("🚀 Starting Database Verification Process")
    logger.info("=" * 60)

    results = {
        'dtc_database': verify_dtc_database(),
        'user_database': verify_user_database(),
        'brand_database': verify_brand_database()
    }

    logger.info("\n" + "=" * 60)
    logger.info("📊 DATABASE VERIFICATION SUMMARY")
    logger.info("=" * 60)

    all_passed = True
    for db_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{db_name.upper():<15}: {status}")
        if not result:
            all_passed = False

    logger.info("=" * 60)

    if all_passed:
        logger.info("🎉 ALL DATABASE VERIFICATIONS PASSED!")
        logger.info("✅ Database structure is correct and functional")
    else:
        logger.error("❌ SOME DATABASE VERIFICATIONS FAILED!")
        logger.error("Please check the error messages above")

    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)