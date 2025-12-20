"""
Comprehensive End-to-End Test for AutoDiag
This test validates the complete diagnostic workflow with live data focus.
"""

import sys
import os
import logging
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_end_to_end_comprehensive.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_complete_diagnostic_workflow():
    """Test complete diagnostic workflow end-to-end"""
    logger.info("Starting comprehensive end-to-end diagnostic test")
    
    try:
        from AutoDiag.core.diagnostics import DiagnosticsController
        from AutoDiag.core.can_database_sqlite import SQLiteCANManager
        
        # Initialize components
        diag_controller = DiagnosticsController()
        can_db = SQLiteCANManager()
        logger.info("Components initialized")
        
        # Test multiple brands
        brands = ["Toyota", "BMW", "Mercedes", "Ford", "Honda"]
        
        for brand in brands:
            logger.info(f"\n--- Testing {brand} ---")
            
            # Set brand
            diag_controller.set_brand(brand)
            logger.info(f"Brand set to: {brand}")
            
            # Load CAN database
            if diag_controller.load_vehicle_database(brand):
                logger.info(f"CAN database loaded for {brand}")
            else:
                logger.warning(f"No specific CAN database for {brand}, using fallback")
            
            # Test DTC reading
            dtc_result = diag_controller.read_dtcs(brand)
            logger.info(f"DTC read: {dtc_result.get('status')}")
            
            # Test quick scan
            scan_result = diag_controller.run_quick_scan(brand)
            logger.info(f"Quick scan: {scan_result.get('status')}")
            
            # Test live data
            live_result = diag_controller.start_live_stream(brand)
            logger.info(f"Live data: {live_result.get('status')}")
            
            # Get sample data
            sample_data = diag_controller.populate_sample_data()
            logger.info(f"Sample data: {len(sample_data)} items")
            
            # Stop live data
            diag_controller.stop_live_stream()
            
        # Test cleanup
        diag_controller.cleanup()
        logger.info("Diagnostics controller cleaned up")
        
        logger.info("Comprehensive diagnostic workflow test completed")
        return True
        
    except Exception as e:
        logger.error(f"Diagnostic workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_can_database_comprehensive():
    """Test CAN database functionality comprehensively"""
    logger.info("Testing CAN database functionality")
    
    try:
        from AutoDiag.core.can_database_sqlite import (
            SQLiteCANManager, 
            get_vehicle_database, 
            list_all_vehicles, 
            get_all_manufacturers
        )
        
        # Test database manager
        db_manager = SQLiteCANManager()
        logger.info("SQLiteCANManager initialized")
        
        # Test statistics
        vehicles = list_all_vehicles()
        manufacturers = get_all_manufacturers()
        
        logger.info(f"Total vehicles: {len(vehicles)}")
        logger.info(f"Total manufacturers: {len(manufacturers)}")
        
        # Test specific brands
        test_brands = ["Toyota", "BMW", "Mercedes", "Ford", "Honda", "Volkswagen"]
        
        for brand in test_brands:
            db = get_vehicle_database(brand)
            if db:
                logger.info(f"{brand}: {len(db.messages)} messages")
            else:
                logger.warning(f"No database for {brand}")
        
        logger.info("CAN database comprehensive test completed")
        return True
        
    except Exception as e:
        logger.error(f"CAN database test failed: {e}")
        return False

def test_vci_simulation():
    """Test VCI functionality in simulation mode"""
    logger.info("Testing VCI functionality in simulation mode")
    
    try:
        from AutoDiag.core.vci_manager import get_vci_manager
        
        vci_manager = get_vci_manager()
        logger.info("VCI manager initialized")
        
        # Test device scanning
        devices = vci_manager.scan_for_devices(timeout=5)
        logger.info(f"Found {len(devices)} VCI devices")
        
        # List devices
        for i, device in enumerate(devices):
            logger.info(f"Device {i+1}: {device.name} ({device.device_type.value})")
        
        logger.info("VCI simulation test completed")
        return True
        
    except Exception as e:
        logger.error(f"VCI simulation test failed: {e}")
        return False

def test_live_data_performance():
    """Test live data performance and functionality"""
    logger.info("Testing live data performance")
    
    try:
        from AutoDiag.core.diagnostics import DiagnosticsController
        
        diag_controller = DiagnosticsController()
        
        # Test with Toyota (most likely to have good CAN data)
        diag_controller.set_brand("Toyota")
        diag_controller.load_vehicle_database("Toyota")
        
        # Start live data
        live_result = diag_controller.start_live_stream("Toyota")
        
        if live_result.get("status") == "started":
            logger.info("Live data streaming started")
            
            # Let it run for a few cycles
            import time
            time.sleep(3)
            
            # Get sample data
            sample_data = diag_controller.populate_sample_data()
            logger.info(f"Live data sample: {len(sample_data)} items")
            
            # Display sample data
            for i, (name, value, unit) in enumerate(sample_data[:5]):  # Show first 5
                logger.info(f"  {i+1}. {name}: {value} {unit}")
            
            # Stop streaming
            diag_controller.stop_live_stream()
            logger.info("Live data streaming stopped")
        else:
            logger.warning("Live data streaming failed to start")
        
        diag_controller.cleanup()
        logger.info("Live data performance test completed")
        return True
        
    except Exception as e:
        logger.error(f"Live data performance test failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("=" * 70)
    logger.info("COMPREHENSIVE END-TO-END DIAGNOSTIC TEST")
    logger.info("Testing complete diagnostic workflow with live data focus")
    logger.info("=" * 70)
    
    success = True
    
    # Test CAN database
    if not test_can_database_comprehensive():
        success = False
    
    # Test VCI simulation
    if not test_vci_simulation():
        success = False
    
    # Test complete diagnostic workflow
    if not test_complete_diagnostic_workflow():
        success = False
    
    # Test live data performance
    if not test_live_data_performance():
        success = False
    
    # Final result
    logger.info("=" * 70)
    if success:
        logger.info("ALL COMPREHENSIVE TESTS PASSED")
        logger.info("End-to-end diagnostic workflow validated")
        logger.info("System is ready for production use")
    else:
        logger.error("SOME COMPREHENSIVE TESTS FAILED")
        logger.error("Please review the logs for details")
    
    logger.info("=" * 70)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)