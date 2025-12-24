#!/usr/bin/env python3
"""
Test script to verify VCI scan freeze fixes
Tests timeout mechanisms and error handling for VCI operations
"""

import logging
import time
import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_vci_manager_timeouts():
    """Test VCI manager timeout mechanisms"""
    logger.info("=== Testing VCI Manager Timeout Mechanisms ===")
    
    try:
        from AutoDiag.core.vci_manager import VCIManager, VCITypes
        
        vci_manager = VCIManager()
        
        # Test 1: Serial port scanning with timeout
        logger.info("Test 1: Serial port scanning with timeout")
        start_time = time.time()
        devices = vci_manager.scan_for_devices(timeout=5)  # 5 second timeout
        elapsed = time.time() - start_time
        
        logger.info(f"Serial scan completed in {elapsed:.1f}s, found {len(devices)} devices")
        assert elapsed <= 6.0, f"Serial scan took too long: {elapsed:.1f}s"
        
        # Test 2: Individual component timeouts
        logger.info("Test 2: Individual component timeouts")
        
        # Test serial port scanning directly
        start_time = time.time()
        vci_manager._scan_serial_ports()
        serial_elapsed = time.time() - start_time
        logger.info(f"Serial port scan completed in {serial_elapsed:.1f}s")
        assert serial_elapsed <= 11.0, f"Serial port scan took too long: {serial_elapsed:.1f}s"
        
        # Test J2534 registry scanning
        start_time = time.time()
        vci_manager._scan_j2534_devices()
        j2534_elapsed = time.time() - start_time
        logger.info(f"J2534 registry scan completed in {j2534_elapsed:.1f}s")
        assert j2534_elapsed <= 6.0, f"J2534 scan took too long: {j2534_elapsed:.1f}s"
        
        logger.info("✅ VCI Manager timeout tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ VCI Manager timeout test failed: {e}")
        return False

def test_j2534_timeout_protection():
    """Test J2534 passthru timeout protection"""
    logger.info("=== Testing J2534 Timeout Protection ===")
    
    try:
        from shared.j2534_passthru import get_passthru_device, J2534Protocol
        
        # Test with mock mode first (safe)
        logger.info("Test 1: Mock J2534 device operations")
        mock_device = get_passthru_device(mock_mode=True)
        
        start_time = time.time()
        success = mock_device.open()
        elapsed = time.time() - start_time
        
        logger.info(f"Mock device open completed in {elapsed:.3f}s")
        assert success, "Mock device should open successfully"
        assert elapsed <= 1.0, f"Mock device open took too long: {elapsed:.3f}s"
        
        # Test connection
        channel = mock_device.connect(J2534Protocol.ISO15765, baudrate=500000)
        logger.info(f"Mock device connected on channel {channel}")
        assert channel > 0, "Mock device should connect successfully"
        
        mock_device.disconnect(channel)
        mock_device.close()
        
        logger.info("✅ J2534 timeout protection tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ J2534 timeout protection test failed: {e}")
        return False

def test_diagnostics_controller_timeouts():
    """Test diagnostics controller timeout mechanisms"""
    logger.info("=== Testing Diagnostics Controller Timeout Mechanisms ===")
    
    try:
        from AutoDiag.core.diagnostics import DiagnosticsController
        
        controller = DiagnosticsController()
        
        # Test VCI scan with timeout
        logger.info("Test 1: VCI scan with timeout")
        start_time = time.time()
        result = controller.scan_for_vci_devices()
        elapsed = time.time() - start_time
        
        logger.info(f"VCI scan completed in {elapsed:.1f}s")
        assert elapsed <= 16.0, f"VCI scan took too long: {elapsed:.1f}s"
        
        # Check result structure
        assert "status" in result, "Result should contain status"
        assert result["status"] in ["success", "error"], "Status should be success or error"
        
        logger.info("✅ Diagnostics controller timeout tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Diagnostics controller timeout test failed: {e}")
        return False

def test_freeze_resistance():
    """Test that the system doesn't freeze under various conditions"""
    logger.info("=== Testing Freeze Resistance ===")
    
    try:
        from AutoDiag.core.vci_manager import VCIManager
        
        vci_manager = VCIManager()
        
        # Test multiple rapid scans
        logger.info("Test 1: Multiple rapid scans")
        for i in range(3):
            start_time = time.time()
            devices = vci_manager.scan_for_devices(timeout=3)
            elapsed = time.time() - start_time
            logger.info(f"Scan {i+1} completed in {elapsed:.1f}s")
            assert elapsed <= 4.0, f"Scan {i+1} took too long: {elapsed:.1f}s"
            time.sleep(0.5)  # Brief pause between scans
        
        # Test with very short timeout
        logger.info("Test 2: Very short timeout (1 second)")
        start_time = time.time()
        devices = vci_manager.scan_for_devices(timeout=1)
        elapsed = time.time() - start_time
        logger.info(f"Short timeout scan completed in {elapsed:.1f}s")
        assert elapsed <= 2.0, f"Short timeout scan took too long: {elapsed:.1f}s"
        
        logger.info("✅ Freeze resistance tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Freeze resistance test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting VCI Freeze Fix Tests")
    
    tests = [
        test_vci_manager_timeouts,
        test_j2534_timeout_protection,
        test_diagnostics_controller_timeouts,
        test_freeze_resistance
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                logger.error(f"❌ Test {test.__name__} failed")
        except Exception as e:
            logger.error(f"❌ Test {test.__name__} crashed: {e}")
    
    logger.info(f"=== Test Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        logger.info("🎉 All VCI freeze fix tests passed!")
        logger.info("The VCI scan freeze issue should now be resolved.")
        return True
    else:
        logger.error(f"❌ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)