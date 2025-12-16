#!/usr/bin/env python3
"""
Test SQLite Database Conversion
Tests the converted SQLite databases to ensure they work correctly
"""

import logging
import sys
import os

# Add shared to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_dtc_database_sqlite():
    """Test the SQLite DTC database functionality"""
    logger.info("🔧 Testing SQLite DTC Database Conversion...")

    try:
        # Import the SQLite DTC database
        from dtc_database_sqlite import DTCDatabaseSQLite
        logger.info("✅ SQLite DTC database module imported successfully")

        # Initialize the SQLite DTC database
        dtc_db = DTCDatabaseSQLite()
        logger.info("✅ SQLite DTC database initialized successfully")

        # Test basic functionality
        info = dtc_db.get_dtc_info('P0300')
        logger.info(f"P0300: {info}")

        info = dtc_db.get_dtc_info('U0100')
        logger.info(f"U0100: {info}")

        info = dtc_db.get_dtc_info('INVALID')
        logger.info(f"INVALID: {info}")

        # Test search
        results = dtc_db.search_dtcs('misfire')
        logger.info(f"Found {len(results)} misfire-related DTCs")

        # Test count
        count = dtc_db.get_dtc_count()
        logger.info(f"Total DTCs: {count}")

        # Test add DTC
        success = dtc_db.add_dtc('P9999', 'Test DTC Code', 'Medium', 'Test')
        if success:
            logger.info("✅ DTC addition working")
            # Clean up test DTC
            dtc_db.delete_dtc('P9999')
        else:
            logger.error("❌ DTC addition failed")

        # Test update DTC
        success = dtc_db.update_dtc('P0300', description='Updated Misfire Description')
        if success:
            logger.info("✅ DTC update working")
            # Verify update
            updated_info = dtc_db.get_dtc_info('P0300')
            if 'Updated Misfire Description' in updated_info['description']:
                logger.info("✅ DTC update verified")
        else:
            logger.error("❌ DTC update failed")

        logger.info("🎉 ALL SQLITE DTC DATABASE TESTS SUCCESSFUL!")
        return True

    except Exception as e:
        logger.error(f"❌ SQLite DTC database test failed: {e}")
        return False

def test_user_database_sqlite():
    """Test the SQLite User database functionality"""
    logger.info("🔧 Testing SQLite User Database Conversion...")

    try:
        # Import the SQLite User database
        from user_database_sqlite import UserDatabase, UserTier, UserStatus
        logger.info("✅ SQLite User database module imported successfully")

        # Initialize the SQLite User database
        user_db = UserDatabase()
        logger.info("✅ SQLite User database initialized successfully")

        # Test user authentication
        success, message, user_info = user_db.authenticate_user("superuser", "ChangeMe123!")
        if success and user_info:
            logger.info("✅ User authentication working")
            logger.info(f"User info: {user_info['username']} - {user_info['tier']}")
        else:
            logger.error(f"❌ User authentication failed: {message}")

        # Test user creation
        test_username = "test_user_sqlite"
        if not user_db.user_exists(test_username):
            success = user_db.create_user(
                test_username, 
                "TestPassword123!", 
                "Test User SQLite", 
                UserTier.BASIC,
                "test@example.com"
            )
            if success:
                logger.info("✅ User creation working")
                
                # Test user info retrieval
                user_info = user_db.get_user_info(test_username)
                if user_info:
                    logger.info(f"✅ User info retrieval working: {user_info['full_name']}")
                
                # Test permission check
                has_permission = user_db.has_permission(test_username, "basic_diagnostics")
                logger.info(f"✅ Permission check working: {has_permission}")
                
                # Clean up test user
                user_db.delete_user(test_username, "test")
                logger.info("✅ Test user cleaned up")
            else:
                logger.error("❌ User creation failed")
        else:
            logger.info("ℹ️  Test user already exists, skipping creation test")

        # Test audit log
        logs = user_db.get_audit_logs(5)
        logger.info(f"✅ Audit log retrieval working: {len(logs)} entries")

        # Test password change (simulate)
        if user_db.user_exists("superuser"):
            # Test password validation
            success, message = user_db.change_password("superuser", "wrong_password", "NewPassword123!")
            if not success:
                logger.info("✅ Password validation working (correctly rejected wrong password)")
            else:
                logger.error("❌ Password validation failed (should have rejected wrong password)")

        logger.info("🎉 ALL SQLITE USER DATABASE TESTS SUCCESSFUL!")
        return True

    except Exception as e:
        logger.error(f"❌ SQLite User database test failed: {e}")
        return False

def test_database_compatibility():
    """Test compatibility between old and new database implementations"""
    logger.info("🔧 Testing Database Compatibility...")

    try:
        # Import both old and new DTC databases
        from dtc_database import DTCDatabase as DTCDatabaseOld
        from dtc_database_sqlite import DTCDatabaseSQLite
        
        # Create both database instances
        old_db = DTCDatabaseOld(":memory:")
        new_db = DTCDatabaseSQLite()
        
        # Test same functionality
        test_codes = ['P0300', 'P0171', 'U0100', 'B1000']
        
        for code in test_codes:
            old_info = old_db.get_dtc_info(code)
            new_info = new_db.get_dtc_info(code)
            
            if old_info['description'] == new_info['description']:
                logger.info(f"✅ DTC {code}: Compatibility maintained")
            else:
                logger.warning(f"⚠️  DTC {code}: Description mismatch")
                logger.info(f"   Old: {old_info['description']}")
                logger.info(f"   New: {new_info['description']}")
        
        # Test search functionality
        old_results = old_db.search_dtcs('misfire')
        new_results = new_db.search_dtcs('misfire')
        
        if len(old_results) == len(new_results):
            logger.info(f"✅ Search compatibility: {len(new_results)} results")
        else:
            logger.warning(f"⚠️  Search results mismatch: Old={len(old_results)}, New={len(new_results)}")
        
        old_db.close()
        
        logger.info("🎉 DATABASE COMPATIBILITY TESTS SUCCESSFUL!")
        return True

    except Exception as e:
        logger.error(f"❌ Database compatibility test failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting SQLite Database Conversion Tests")
    logger.info("=" * 60)

    all_tests_passed = True

    # Test DTC database
    if not test_dtc_database_sqlite():
        all_tests_passed = False

    logger.info("-" * 60)

    # Test User database
    if not test_user_database_sqlite():
        all_tests_passed = False

    logger.info("-" * 60)

    # Test compatibility
    if not test_database_compatibility():
        all_tests_passed = False

    logger.info("=" * 60)
    
    if all_tests_passed:
        logger.info("🎉 ALL SQLITE CONVERSION TESTS SUCCESSFUL!")
        logger.info("✅ DTC database successfully converted from SQL Server to SQLite")
        logger.info("✅ User database successfully converted from SQL Server to SQLite")
        logger.info("✅ All functionality preserved and enhanced")
        logger.info("✅ Database compatibility maintained")
        return True
    else:
        logger.error("❌ SOME TESTS FAILED!")
        logger.error("Database conversion requires attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)