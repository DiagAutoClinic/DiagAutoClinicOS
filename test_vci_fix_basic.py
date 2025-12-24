#!/usr/bin/env python3
"""
Basic test for VCI Freeze Fix
Simple test to verify the core fixes work without GUI dependencies
"""

import sys
import time
import logging
from unittest.mock import patch, MagicMock

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_obdlink_timeout_fix():
    """Test that OBDLink discovery has timeout protection"""
    logger.info("Testing OBDLink MX+ timeout protection...")
    
    try:
        from shared.obdlink_mxplus import OBDLinkMXPlus
        
        # Test mock mode
        obdlink = OBDLinkMXPlus(mock_mode=True)
        devices = obdlink.discover_devices(timeout=2)
        assert isinstance(devices, list)
        logger.info(f"✓ Mock OBDLink discovery returned {len(devices)} devices")
        
        # Test that timeout parameter works
        start_time = time.time()
        devices = obdlink.discover_devices(timeout=1)  # Very short timeout
        elapsed = time.time() - start_time
        
        assert elapsed < 3  # Should complete quickly even with timeout
        logger.info(f"✓ Timeout protection working - completed in {elapsed:.1f}s")
        
        return True
        
    except Exception as e:
        logger.error(f"OBDLink timeout test failed: {e}")
        return False

def test_scanmatik_timeout_fix():
    """Test that ScanMatik discovery has timeout protection"""
    logger.info("Testing ScanMatik timeout protection...")
    
    try:
        from shared.scanmatik_2_pro import ScanMatik2Pro
        
        # Test mock mode
        scanmatik = ScanMatik2Pro(mock_mode=True)
        devices = scanmatik.detect_devices(timeout=2)
        assert isinstance(devices, list)
        logger.info(f"✓ Mock ScanMatik detection returned {len(devices)} devices")
        
        # Test timeout parameter
        start_time = time.time()
        devices = scanmatik.detect_devices(timeout=1)  # Very short timeout
        elapsed = time.time() - start_time
        
        assert elapsed < 3  # Should complete quickly
        logger.info(f"✓ Timeout protection working - completed in {elapsed:.1f}s")
        
        return True
        
    except Exception as e:
        logger.error(f"ScanMatik timeout test failed: {e}")
        return False

def test_device_handler_enhancements():
    """Test enhanced device handler"""
    logger.info("Testing enhanced device handler...")
    
    try:
        from shared.device_handler import DeviceHandler
        
        # Test mock mode
        handler = DeviceHandler(mock_mode=True)
        logger.info("✓ Device handler created")
        
        # Test async methods exist
        assert hasattr(handler, 'discover_devices_async')
        assert hasattr(handler, 'discover_devices_blocking')
        assert hasattr(handler, 'cancel_discovery')
        logger.info("✓ Async methods available")
        
        # Test blocking discovery
        start_time = time.time()
        devices = handler.discover_devices_blocking(timeout=2)
        elapsed = time.time() - start_time
        
        assert elapsed < 5  # Should complete quickly
        assert isinstance(devices, list)
        logger.info(f"✓ Blocking discovery working - found {len(devices)} devices in {elapsed:.1f}s")
        
        return True
        
    except Exception as e:
        logger.error(f"Device handler test failed: {e}")
        return False

def test_vci_worker_basic():
    """Test VCI discovery worker basic functionality"""
    logger.info("Testing VCI discovery worker...")
    
    try:
        from shared.vci_discovery_worker import VCIDiscoveryWorker, DiscoveredDevice
        
        # Test worker creation
        worker = VCIDiscoveryWorker(timeout=3)
        logger.info("✓ VCI Discovery Worker created")
        
        # Test device filtering
        test_devices = [
            DiscoveredDevice("Device1", "OBDLink MX+", port="COM1"),
            DiscoveredDevice("Device2", "OBDLink MX+", port="COM2"),
            DiscoveredDevice("Device3", "ScanMatik", port="COM3"),
        ]
        
        filtered = worker._filter_and_deduplicate_devices(test_devices)
        assert len(filtered) == 2  # Should remove duplicate OBDLink
        logger.info("✓ Device filtering working")
        
        # Test Bluetooth address extraction
        device_info = "OBDLink (00:11:22:33:44:55)"
        address = worker._extract_bluetooth_address(device_info)
        assert address == "00:11:22:33:44:55"
        logger.info("✓ Bluetooth address extraction working")
        
        return True
        
    except Exception as e:
        logger.error(f"VCI worker test failed: {e}")
        return False

def test_comparison_with_original_issue():
    """Test that demonstrates the fix compared to original issue"""
    logger.info("Testing fix vs original issue comparison...")
    
    try:
        from shared.obdlink_mxplus import OBDLinkMXPlus
        
        # Create mock OBDLink
        obdlink = OBDLinkMXPlus(mock_mode=True)
        
        # Original issue: bluetooth.discover_devices(duration=8, ...) would block for 8+ seconds
        # Our fix: Should complete quickly with timeout
        
        start_time = time.time()
        
        # This should not block for 8+ seconds like the original
        devices = obdlink.discover_devices(timeout=3)
        
        elapsed = time.time() - start_time
        
        # Verify it completes quickly
        assert elapsed < 5, f"Discovery took too long: {elapsed:.1f}s"
        
        logger.info(f"✓ Fixed discovery: {elapsed:.1f}s (original would be 8+ seconds)")
        logger.info(f"✓ Found {len(devices)} devices without blocking")
        
        return True
        
    except Exception as e:
        logger.error(f"Comparison test failed: {e}")
        return False

def run_basic_tests():
    """Run basic tests to verify the fix works"""
    logger.info("Starting Basic VCI Freeze Fix Tests")
    logger.info("=" * 40)
    
    tests = [
        ("OBDLink Timeout Fix", test_obdlink_timeout_fix),
        ("ScanMatik Timeout Fix", test_scanmatik_timeout_fix),
        ("Device Handler Enhancements", test_device_handler_enhancements),
        ("VCI Worker Basic", test_vci_worker_basic),
        ("Fix vs Original Issue", test_comparison_with_original_issue),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "PASS" if result else "FAIL"
            logger.info(f"{test_name}: {status}")
        except Exception as e:
            logger.error(f"{test_name}: FAIL - {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 40)
    logger.info("RESULTS SUMMARY")
    logger.info("=" * 40)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! VCI Freeze Fix is working!")
        return True
    else:
        logger.error("❌ Some tests failed.")
        return False

if __name__ == "__main__":
    success = run_basic_tests()
    sys.exit(0 if success else 1)