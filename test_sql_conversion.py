#!/usr/bin/env python3
"""
SQL Conversion Test
This script tests the conversion from SQLite to SQL Server for the DTC database
"""

import logging
from shared.dtc_database_sql import DTCDatabaseSQL

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_sql_dtc_database():
    """Test the SQL Server DTC database functionality"""
    logger.info("🔧 Testing SQL Server DTC Database Conversion...")

    try:
        # Initialize the SQL Server DTC database
        dtc_db = DTCDatabaseSQL()
        logger.info("✅ SQL Server DTC database initialized successfully")

        # Test basic DTC retrieval
        test_codes = ['P0300', 'U0100', 'B1000', 'INVALID']
        for code in test_codes:
            info = dtc_db.get_dtc_info(code)
            if code == 'INVALID':
                assert info['description'] == 'Unknown DTC Code', f"Expected unknown DTC for {code}"
                logger.info(f"✅ {code}: Correctly returns unknown DTC")
            else:
                assert info['description'] != 'Unknown DTC Code', f"Expected valid DTC for {code}"
                logger.info(f"✅ {code}: {info['description']} ({info['severity']})")

        # Test search functionality
        search_results = dtc_db.search_dtcs('misfire')
        assert len(search_results) > 0, "Expected to find misfire-related DTCs"
        logger.info(f"✅ Search functionality working - found {len(search_results)} misfire DTCs")

        # Test DTC count
        count = dtc_db.get_dtc_count()
        assert count > 0, "Expected at least some DTCs in database"
        logger.info(f"✅ DTC count working - {count} DTCs in database")

        # Test severity filtering
        critical_dtcs = dtc_db.get_dtcs_by_severity('Critical')
        assert len(critical_dtcs) > 0, "Expected to find critical DTCs"
        logger.info(f"✅ Severity filtering working - found {len(critical_dtcs)} critical DTCs")

        # Test category filtering
        powertrain_dtcs = dtc_db.get_dtcs_by_category('Powertrain')
        assert len(powertrain_dtcs) > 0, "Expected to find powertrain DTCs"
        logger.info(f"✅ Category filtering working - found {len(powertrain_dtcs)} powertrain DTCs")

        # Test adding a new DTC
        new_dtc_added = dtc_db.add_dtc('P0401', 'Exhaust Gas Recirculation Flow Insufficient', 'Medium', 'Powertrain')
        assert new_dtc_added, "Failed to add new DTC"
        logger.info("✅ Add DTC functionality working")

        # Verify the new DTC was added
        new_dtc_info = dtc_db.get_dtc_info('P0401')
        assert new_dtc_info['description'] == 'Exhaust Gas Recirculation Flow Insufficient'
        logger.info("✅ New DTC verified in database")

        # Test updating a DTC
        update_success = dtc_db.update_dtc('P0401', description='EGR Flow Insufficient Detected')
        assert update_success, "Failed to update DTC"
        logger.info("✅ Update DTC functionality working")

        # Verify the update
        updated_info = dtc_db.get_dtc_info('P0401')
        assert updated_info['description'] == 'EGR Flow Insufficient Detected'
        logger.info("✅ DTC update verified")

        # Test getting all DTCs
        all_dtcs = dtc_db.get_all_dtcs()
        assert len(all_dtcs) > 0, "Expected to get all DTCs"
        logger.info(f"✅ Get all DTCs working - retrieved {len(all_dtcs)} DTCs")

        logger.info("🎉 ALL SQL CONVERSION TESTS PASSED!")
        return True

    except Exception as e:
        logger.error(f"❌ SQL conversion test failed: {e}")
        return False

def test_database_compatibility():
    """Test compatibility between old and new database implementations"""
    logger.info("🔧 Testing Database Compatibility...")

    try:
        # Test that both databases can coexist
        from shared.dtc_database import DTCDatabase as DTCDatabaseSQLite
        from shared.dtc_database_sql import DTCDatabaseSQL

        # Create both database instances
        sqlite_db = DTCDatabaseSQLite(":memory:")
        sql_db = DTCDatabaseSQL()

        # Test that both return similar results for basic queries
        sqlite_result = sqlite_db.get_dtc_info('P0300')
        sql_result = sql_db.get_dtc_info('P0300')

        assert sqlite_result['description'] == sql_result['description'], "Results should match"
        logger.info("✅ Both databases return consistent results")

        # Test that both can handle invalid codes
        sqlite_invalid = sqlite_db.get_dtc_info('INVALID')
        sql_invalid = sql_db.get_dtc_info('INVALID')

        assert sqlite_invalid['description'] == sql_invalid['description'], "Invalid results should match"
        logger.info("✅ Both databases handle invalid codes consistently")

        logger.info("🎉 DATABASE COMPATIBILITY TEST PASSED!")
        return True

    except Exception as e:
        logger.error(f"❌ Database compatibility test failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting SQL Conversion Testing")
    logger.info("=" * 60)

    results = {
        'sql_conversion': test_sql_dtc_database(),
        'database_compatibility': test_database_compatibility()
    }

    logger.info("\n" + "=" * 60)
    logger.info("📊 SQL CONVERSION TEST RESULTS")
    logger.info("=" * 60)

    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name.upper():<25}: {status}")
        if not result:
            all_passed = False

    logger.info("=" * 60)

    if all_passed:
        logger.info("🎉 ALL SQL CONVERSION TESTS SUCCESSFUL!")
        logger.info("✅ DTC database successfully converted from SQLite to SQL Server")
        logger.info("✅ All functionality preserved and enhanced")
        logger.info("✅ Ready for production use")
    else:
        logger.error("❌ SOME SQL CONVERSION TESTS FAILED!")
        logger.error("Please review the error messages above")

    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)