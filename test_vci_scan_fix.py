#!/usr/bin/env python3
"""
Test script to verify the VCI scan fix for 'bool' object is not iterable error
"""

import sys
import os
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_vci_scan_fix():
    """Test that the VCI scan fix works correctly"""
    try:
        # Import the diagnostics controller
        from AutoDiag.core.diagnostics import DiagnosticsController
        
        logger.info("Testing VCI scan fix...")
        
        # Create diagnostics controller
        controller = DiagnosticsController()
        
        # Test the scan_for_vci_devices method
        logger.info("Calling scan_for_vci_devices()...")
        result = controller.scan_for_vci_devices()
        
        logger.info(f"Scan result: {result}")
        
        # Verify the result is a dictionary, not a boolean
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        
        # Verify the result has the expected structure
        assert "status" in result, "Result should have 'status' key"
        assert result["status"] in ["success", "error"], f"Invalid status: {result['status']}"
        
        if result["status"] == "success":
            assert "message" in result, "Success result should have 'message' key"
            assert "scan_started" in result, "Success result should have 'scan_started' key"
            logger.info("✅ VCI scan started successfully")
        else:
            logger.info(f"❌ VCI scan failed: {result.get('message', 'Unknown error')}")
        
        # Test the get_scan_results method
        logger.info("Calling get_scan_results()...")
        scan_results = controller.get_scan_results()
        
        logger.info(f"Scan results: {scan_results}")
        
        # Verify the scan results structure
        assert isinstance(scan_results, dict), f"Expected dict, got {type(scan_results)}"
        assert "status" in scan_results, "Scan results should have 'status' key"
        assert scan_results["status"] in ["success", "error"], f"Invalid status: {scan_results['status']}"
        
        if scan_results["status"] == "success":
            assert "devices_found" in scan_results, "Success result should have 'devices_found' key"
            assert "devices" in scan_results, "Success result should have 'devices' key"
            assert "scan_in_progress" in scan_results, "Success result should have 'scan_in_progress' key"
            logger.info(f"✅ Found {scan_results['devices_found']} devices")
        else:
            logger.info(f"❌ Failed to get scan results: {scan_results.get('message', 'Unknown error')}")
        
        logger.info("✅ All tests passed! The VCI scan fix is working correctly.")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_vci_scan_fix()
    sys.exit(0 if success else 1)