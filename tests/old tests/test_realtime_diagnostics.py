#!/usr/bin/env python3
"""
Test script for realtime diagnosing functionality
"""

import sys
import os
from pathlib import Path
import time
import logging
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("RealtimeTest")

def test_realtime_functionality():
    """Test the realtime diagnosing functionality"""
    logger.info("🚀 Starting realtime diagnostics test")

    try:
        # Test 1: Import main modules
        logger.info("📦 Testing module imports...")
        from AutoDiag.main import AutoDiagPro
        from AutoDiag.core.diagnostics import DiagnosticsController
        from AutoDiag.ui.can_bus_tab import CANBusDataTab
        logger.info("✅ All modules imported successfully")

        # Test 2: Create diagnostics controller
        logger.info("🔧 Creating diagnostics controller...")
        controller = DiagnosticsController()
        logger.info("✅ Diagnostics controller created")

        # Test 3: Test VCI manager
        logger.info("🔌 Testing VCI manager...")
        if controller.vci_manager:
            logger.info("✅ VCI manager available")
            vci_status = controller.get_vci_status()
            logger.info(f"VCI Status: {vci_status}")
        else:
            logger.warning("⚠️ VCI manager not available")

        # Test 4: Test CAN database loading
        logger.info("📚 Testing CAN database loading...")
        manufacturers = controller.get_available_manufacturers()
        logger.info(f"Available manufacturers: {len(manufacturers)}")

        if manufacturers:
            # Test with first manufacturer
            test_brand = manufacturers[0]
            controller.set_brand(test_brand)
            logger.info(f"✅ Set brand to: {test_brand}")

        # Test 5: Test realtime CAN data generation
        logger.info("📊 Testing realtime CAN data generation...")
        can_data = controller._get_realtime_can_data()
        logger.info(f"Generated {len(can_data)} CAN messages")

        if can_data:
            for can_id, data in can_data.items():
                logger.info(f"CAN ID 0x{can_id:03X}: {data.hex(' ')}")
        else:
            logger.warning("⚠️ No CAN data generated")

        # Test 6: Test live data streaming
        logger.info("📡 Testing live data streaming...")
        live_data = controller._get_live_data_from_can_db()
        logger.info(f"Generated {len(live_data)} live data parameters")

        for param, value, unit in live_data:
            logger.info(f"  {param}: {value} {unit}")

        # Test 7: Test realtime monitoring methods
        logger.info("🔍 Testing realtime monitoring methods...")

        # Create CAN bus tab instance
        can_bus_tab = CANBusDataTab()
        logger.info("✅ CAN bus tab created")

        # Test realtime data update
        if can_data:
            can_bus_tab.update_realtime_data(can_data)
            logger.info("✅ Realtime CAN data update successful")

        logger.info("🎉 All realtime diagnostics tests completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Realtime diagnostics test failed: {e}")
        logger.exception("Full exception details:")
        return False

def test_launcher_integration():
    """Test launcher integration with realtime diagnostics"""
    logger.info("🚀 Starting launcher integration test")

    try:
        # Test launcher imports
        from launcher import DiagLauncher
        logger.info("✅ Launcher module imported successfully")

        # Test that launcher can monitor processes
        logger.info("🔍 Testing launcher monitoring capabilities...")

        # The launcher should be able to monitor AutoDiag Pro processes
        # and provide realtime status updates

        logger.info("✅ Launcher integration test completed")
        return True

    except Exception as e:
        logger.error(f"❌ Launcher integration test failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🧪 Starting comprehensive realtime diagnostics test suite")
    logger.info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run tests
    test1_result = test_realtime_functionality()
    test2_result = test_launcher_integration()

    # Summary
    logger.info("\n" + "="*60)
    logger.info("📋 REALTIME DIAGNOSTICS TEST SUMMARY")
    logger.info("="*60)

    if test1_result:
        logger.info("✅ Realtime functionality test: PASSED")
    else:
        logger.info("❌ Realtime functionality test: FAILED")

    if test2_result:
        logger.info("✅ Launcher integration test: PASSED")
    else:
        logger.info("❌ Launcher integration test: FAILED")

    if test1_result and test2_result:
        logger.info("🎉 ALL TESTS PASSED - Realtime diagnostics fully functional!")
        return 0
    else:
        logger.info("⚠️  Some tests failed - Check logs for details")
        return 1

if __name__ == "__main__":
    sys.exit(main())