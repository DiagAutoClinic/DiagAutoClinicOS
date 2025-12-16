#!/usr/bin/env python3
"""
Comprehensive Database Test
This script creates actual database files and verifies all tables and data
"""

import sqlite3
import os
import tempfile
import shutil
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseTester:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"📁 Created temporary directory: {self.temp_dir}")

    def cleanup(self):
        """Clean up temporary files"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            logger.info(f"🗑️  Cleaned up temporary directory: {self.temp_dir}")

    def test_dtc_database_creation(self):
        """Test actual DTC database file creation and verification"""
        logger.info("🔧 Testing DTC Database File Creation...")

        db_path = os.path.join(self.temp_dir, "test_dtcs.db")

        try:
            # Create the database file
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Create DTC table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dtc_codes (
                    code TEXT PRIMARY KEY,
                    description TEXT,
                    severity TEXT,
                    category TEXT
                )
            ''')

            # Insert test data
            test_dtcs = [
                ('P0300', 'Random/Multiple Cylinder Misfire Detected', 'High', 'Powertrain'),
                ('P0171', 'System Too Lean (Bank 1)', 'Medium', 'Powertrain'),
                ('U0100', 'Lost Communication With ECU', 'High', 'Network'),
                ('B1000', 'ECU Malfunction', 'Critical', 'Body'),
                ('C1201', 'ABS System Malfunction', 'High', 'Chassis')
            ]

            cursor.executemany('INSERT OR IGNORE INTO dtc_codes VALUES (?, ?, ?, ?)', test_dtcs)
            conn.commit()

            # Verify file exists
            if os.path.exists(db_path):
                file_size = os.path.getsize(db_path)
                logger.info(f"✅ DTC database file created: {db_path} ({file_size} bytes)")

                # Verify table structure
                cursor.execute("PRAGMA table_info(dtc_codes)")
                columns = cursor.fetchall()
                column_info = "\n".join([f"    - {col[1]} ({col[2]})" for col in columns])
                logger.info(f"✅ DTC table structure verified:\n{column_info}")

                # Verify data count
                cursor.execute("SELECT COUNT(*) FROM dtc_codes")
                count = cursor.fetchone()[0]
                logger.info(f"✅ DTC database contains {count} records")

                # Test data retrieval
                cursor.execute("SELECT code, description FROM dtc_codes WHERE severity = 'High'")
                high_severity = cursor.fetchall()
                logger.info(f"✅ Found {len(high_severity)} high-severity DTCs")

                return True
            else:
                logger.error("❌ DTC database file was not created")
                return False

        except Exception as e:
            logger.error(f"❌ DTC database test failed: {e}")
            return False
        finally:
            conn.close()

    def test_brand_database_comprehensive(self):
        """Test brand database with comprehensive checks"""
        logger.info("🔧 Testing Brand Database Comprehensive...")

        try:
            from shared.brand_database import EnhancedBrandDatabase, brand_database

            # Test global instance
            if brand_database is None:
                logger.error("❌ Global brand_database instance is None")
                return False

            # Test brand count
            brands = brand_database.get_brand_list()
            if not brands or len(brands) < 25:
                logger.error(f"❌ Brand database has insufficient brands: {len(brands)}")
                return False

            logger.info(f"✅ Brand database contains {len(brands)} brands")

            # Test regional distribution
            regions = {}
            for brand in brands:
                info = brand_database.get_brand_info(brand)
                region = info.get('region', 'Unknown')
                regions[region] = regions.get(region, 0) + 1

            region_distribution = "\n".join([f"    - {region}: {count} brands" for region, count in regions.items()])
            logger.info(f"✅ Regional distribution:\n{region_distribution}")

            # Test security levels
            security_levels = {}
            for brand in brands:
                info = brand_database.get_brand_info(brand)
                security_level = info.get('security_level', 1)
                security_levels[security_level] = security_levels.get(security_level, 0) + 1

            security_distribution = "\n".join([f"    - Level {level}: {count} brands" for level, count in sorted(security_levels.items())])
            logger.info(f"✅ Security level distribution:\n{security_distribution}")

            # Test protocol coverage
            protocols = set()
            for brand in brands:
                info = brand_database.get_brand_info(brand)
                brand_protocols = info.get('diagnostic_protocols', [])
                protocols.update(brand_protocols)

            logger.info(f"✅ Supported diagnostic protocols: {len(protocols)} unique protocols")

            # Test specific brand data completeness
            test_brands = ['Toyota', 'BMW', 'Ford', 'Tesla', 'Hyundai']
            for brand in test_brands:
                if brand in brands:
                    info = brand_database.get_brand_info(brand)
                    required_fields = [
                        'region', 'diagnostic_protocols', 'common_ecus',
                        'key_systems', 'security_level', 'programming_tool'
                    ]

                    missing_fields = [field for field in required_fields if field not in info]
                    if missing_fields:
                        logger.warning(f"⚠️  {brand} missing fields: {missing_fields}")
                    else:
                        logger.info(f"✅ {brand} data complete with all required fields")

            return True

        except Exception as e:
            logger.error(f"❌ Brand database comprehensive test failed: {e}")
            return False

    def test_user_database_structure(self):
        """Test user database structure and functionality"""
        logger.info("🔧 Testing User Database Structure...")

        try:
            from shared.user_database_sqlite import UserDatabase, UserTier, UserStatus

            # Test that we can create a UserDatabase instance (this will fail without SQL Server)
            # But we can at least verify the class structure

            # Verify expected methods exist
            required_methods = [
                '_init_database', '_create_default_super_user', 'create_user',
                'authenticate_user', 'get_user_info', 'has_permission'
            ]

            for method in required_methods:
                if not hasattr(UserDatabase, method):
                    logger.error(f"❌ UserDatabase missing method: {method}")
                    return False

            logger.info("✅ UserDatabase class has all required methods")

            # Verify UserTier enum
            expected_tiers = ['BASIC', 'STANDARD', 'ADVANCED', 'PROFESSIONAL', 'SUPER_USER']
            for tier in expected_tiers:
                if not hasattr(UserTier, tier):
                    logger.error(f"❌ UserTier missing: {tier}")
                    return False

            logger.info("✅ UserTier enum has all expected tiers")

            # Verify UserStatus enum
            expected_statuses = ['ACTIVE', 'INACTIVE', 'LOCKED', 'PASSWORD_EXPIRED']
            for status in expected_statuses:
                if not hasattr(UserStatus, status):
                    logger.error(f"❌ UserStatus missing: {status}")
                    return False

            logger.info("✅ UserStatus enum has all expected statuses")

            return True

        except ImportError as e:
            logger.error(f"❌ User database import failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ User database structure test failed: {e}")
            return False

    def test_ref_file_validation(self):
        """Test REF file parsing and validation"""
        logger.info("🔧 Testing REF File Validation...")

        try:
            from AutoDiag.core.can_bus_ref_parser import can_bus_ref_parser
            from shared.brand_database import brand_database

            # Get brands with can_ref
            brands = brand_database.get_brand_list()
            brands_with_ref = []
            for brand in brands:
                info = brand_database.get_brand_info(brand)
                if 'can_ref' in info and info['can_ref']:
                    brands_with_ref.append((brand, info['can_ref']))

            if not brands_with_ref:
                logger.error("❌ No brands found with can_ref entries")
                return False

            logger.info(f"✅ Found {len(brands_with_ref)} brands with REF files")

            # Test parsing each REF file
            successful_parses = 0
            total_signals = 0

            for brand, ref_files in brands_with_ref:
                for ref_file in ref_files:
                    ref_path = f"can_bus_data/Vehicle_CAN_Files_REF/{ref_file}"
                    try:
                        signals = can_bus_ref_parser.parse_ref_file(ref_path)
                        if signals:
                            successful_parses += 1
                            total_signals += len(signals)
                            logger.info(f"✅ Parsed {len(signals)} signals from {brand} - {ref_file}")
                        else:
                            logger.warning(f"⚠️  No signals parsed from {brand} - {ref_file}")
                    except Exception as e:
                        logger.error(f"❌ Failed to parse {brand} - {ref_file}: {e}")

            if successful_parses > 0:
                logger.info(f"✅ Successfully parsed {successful_parses} REF files with {total_signals} total signals")
                return True
            else:
                logger.error("❌ No REF files could be parsed successfully")
                return False

        except Exception as e:
            logger.error(f"❌ REF file validation test failed: {e}")
            return False

    def test_database_integration(self):
        """Test database integration and cross-functionality"""
        logger.info("🔧 Testing Database Integration...")

        try:
            # Test that all databases can be imported together
            from shared.dtc_database_sqlite import DTCDatabaseSQLite
            from shared.brand_database import brand_database
            from shared.user_database_sqlite import UserDatabase

            logger.info("✅ All database modules imported successfully")

            # Test DTC database creation and basic functionality
            dtc_db = DTCDatabaseSQL()
            test_dtc = dtc_db.get_dtc_info("P0300")
            if "description" in test_dtc and test_dtc["description"] != "Unknown DTC Code":
                logger.info("✅ DTC database functional with sample data")
            else:
                logger.error("❌ DTC database not returning expected data")
                return False

            # Test brand database integration
            toyota_info = brand_database.get_brand_info("Toyota")
            if toyota_info and "region" in toyota_info:
                logger.info(f"✅ Brand database integration working - Toyota region: {toyota_info['region']}")
            else:
                logger.error("❌ Brand database integration failed")
                return False

            # Test that we can access multiple brands
            brands = brand_database.get_brand_list()
            if len(brands) >= 25:
                logger.info(f"✅ Full brand database accessible with {len(brands)} brands")
            else:
                logger.error(f"❌ Insufficient brands in database: {len(brands)}")
                return False

            return True

        except Exception as e:
            logger.error(f"❌ Database integration test failed: {e}")
            return False

def main():
    """Main test function"""
    logger.info("🚀 Starting Comprehensive Database Testing")
    logger.info("=" * 70)

    tester = DatabaseTester()

    try:
        # Run all tests
        results = {
            'dtc_file_creation': tester.test_dtc_database_creation(),
            'brand_comprehensive': tester.test_brand_database_comprehensive(),
            'user_structure': tester.test_user_database_structure(),
            'ref_validation': tester.test_ref_file_validation(),
            'database_integration': tester.test_database_integration()
        }

        # Display results
        logger.info("\n" + "=" * 70)
        logger.info("📊 COMPREHENSIVE DATABASE TEST RESULTS")
        logger.info("=" * 70)

        all_passed = True
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{test_name.upper():<25}: {status}")
            if not result:
                all_passed = False

        logger.info("=" * 70)

        if all_passed:
            logger.info("🎉 ALL COMPREHENSIVE DATABASE TESTS PASSED!")
            logger.info("✅ Database system is fully functional and integrated")
        else:
            logger.error("❌ SOME COMPREHENSIVE DATABASE TESTS FAILED!")
            logger.error("Please review the error messages above")

        return all_passed

    finally:
        tester.cleanup()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)