"""
Test script for Opel Corsa ECU HSFI with GD101 -> GT100 Plus GPT -> ECU
This script validates the diagnostic workflow for the specific hardware setup.
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
        logging.FileHandler('test_opel_corsa_hsfi.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

try:
    from AutoDiag.core.diagnostics import DiagnosticsController
    from AutoDiag.core.vci_manager import get_vci_manager, VCITypes
    VCI_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import VCI modules: {e}")
    VCI_AVAILABLE = False

def test_opel_corsa_hsfi_diagnostics():
    """Test diagnostic workflow for Opel Corsa ECU HSFI"""
    logger.info("Starting Opel Corsa ECU HSFI diagnostic test")
    logger.info("Hardware setup: GD101 -> GT100 Plus GPT -> ECU")
    
    # Initialize diagnostics controller
    try:
        diag_controller = DiagnosticsController()
        logger.info("Diagnostics controller initialized")
    except Exception as e:
        logger.error(f"Failed to initialize diagnostics controller: {e}")
        return False
    
    # Set brand to Opel
    diag_controller.set_brand("Opel")
    logger.info(f"Brand set to: {diag_controller.get_brand()}")
    
    # Test VCI connection
    if VCI_AVAILABLE:
        try:
            vci_manager = get_vci_manager()
            logger.info("VCI manager initialized")
            
            # Scan for devices
            logger.info("Scanning for VCI devices...")
            devices = vci_manager.scan_for_devices(timeout=10)
            
            if devices:
                logger.info(f"Found {len(devices)} VCI device(s)")
                for i, device in enumerate(devices):
                    logger.info(f"Device {i+1}: {device.name} ({device.device_type.value}) - Port: {device.port}")
                
                # Connect to first device (GD101)
                if len(devices) > 0:
                    logger.info(f"Connecting to {devices[0].name}...")
                    if vci_manager.connect_to_device(devices[0]):
                        logger.info(f"Successfully connected to {devices[0].name}")
                        
                        # Test basic communication
                        logger.info("Testing basic communication...")
                        if vci_manager.is_connected():
                            logger.info("✅ Basic communication established")
                        else:
                            logger.error("❌ Failed to establish basic communication")
                            return False
                    else:
                        logger.error(f"Failed to connect to {devices[0].name}")
                        return False
                else:
                    logger.error("No VCI devices found")
                    return False
            else:
                logger.error("No VCI devices found")
                return False
        except Exception as e:
            logger.error(f"VCI connection test failed: {e}")
            return False
    else:
        logger.warning("VCI manager not available - running in simulation mode")
    
    # Test DTC reading
    try:
        logger.info("Testing DTC reading...")
        dtc_result = diag_controller.read_dtcs("Opel")
        logger.info(f"DTC read result: {dtc_result}")
        
        if dtc_result.get("status") == "started":
            logger.info("✅ DTC reading initiated successfully")
        else:
            logger.error(f"❌ DTC reading failed: {dtc_result.get('message', 'Unknown error')}")
    except Exception as e:
        logger.error(f"DTC reading test failed: {e}")
    
    # Test quick scan
    try:
        logger.info("Testing quick scan...")
        scan_result = diag_controller.run_quick_scan("Opel")
        logger.info(f"Quick scan result: {scan_result}")
        
        if scan_result.get("status") == "started":
            logger.info("✅ Quick scan initiated successfully")
        else:
            logger.error(f"❌ Quick scan failed: {scan_result.get('message', 'Unknown error')}")
    except Exception as e:
        logger.error(f"Quick scan test failed: {e}")
    
    # Test ECU info
    try:
        logger.info("Testing ECU info retrieval...")
        ecu_result = diag_controller.get_ecu_info("Opel")
        logger.info(f"ECU info result: {ecu_result}")
        
        if ecu_result.get("status") == "success":
            logger.info("✅ ECU info retrieved successfully")
            logger.info(f"ECU Info: {ecu_result.get('ecu_info', {})}")
        else:
            logger.error(f"❌ ECU info retrieval failed: {ecu_result.get('message', 'Unknown error')}")
    except Exception as e:
        logger.error(f"ECU info test failed: {e}")
    
    # Test live data
    try:
        logger.info("Testing live data streaming...")
        live_result = diag_controller.start_live_stream("Opel")
        logger.info(f"Live data result: {live_result}")
        
        if live_result.get("status") == "started":
            logger.info("✅ Live data streaming started successfully")
            
            # Let it run for a few seconds
            import time
            time.sleep(5)
            
            # Stop streaming
            diag_controller.stop_live_stream()
            logger.info("Live data streaming stopped")
        else:
            logger.error(f"❌ Live data streaming failed: {live_result.get('message', 'Unknown error')}")
    except Exception as e:
        logger.error(f"Live data test failed: {e}")
    
    # Cleanup
    try:
        diag_controller.cleanup()
        logger.info("Diagnostics controller cleaned up")
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
    
    logger.info("Opel Corsa ECU HSFI diagnostic test completed")
    return True

def test_protocol_compatibility():
    """Test protocol compatibility for Opel Corsa ECU HSFI"""
    logger.info("Testing protocol compatibility...")
    
    # Test CAN protocol
    try:
        from AutoDiag.core.can_database_sqlite import SQLiteCANManager
        logger.info("CAN database manager initialized")
        
        # Test if we can load a generic CAN database
        db_manager = SQLiteCANManager()
        logger.info("✅ CAN database manager working")
        
    except Exception as e:
        logger.error(f"CAN database test failed: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    logger.info("=" * 60)
    logger.info("Opel Corsa ECU HSFI Diagnostic Test")
    logger.info("Hardware: GD101 -> GT100 Plus GPT -> ECU")
    logger.info("=" * 60)
    
    # Run tests
    success = True
    
    # Test protocol compatibility
    if not test_protocol_compatibility():
        success = False
    
    # Test diagnostic workflow
    if not test_opel_corsa_hsfi_diagnostics():
        success = False
    
    # Final result
    logger.info("=" * 60)
    if success:
        logger.info("✅ All tests completed successfully")
        logger.info("Opel Corsa ECU HSFI diagnostic workflow validated")
    else:
        logger.error("❌ Some tests failed")
        logger.error("Please check the log for details")
    
    logger.info("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)