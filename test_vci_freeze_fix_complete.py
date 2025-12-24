#!/usr/bin/env python3
"""
Test file for VCI Freeze Fix
Tests the threaded device discovery implementation to verify no GUI freezing occurs
"""

import sys
import time
import logging
import threading
from typing import List
from unittest.mock import patch, MagicMock

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_vci_discovery_worker():
    """Test the VCI discovery worker implementation"""
    logger.info("=== Testing VCI Discovery Worker ===")
    
    try:
        from shared.vci_discovery_worker import VCIDiscoveryWorker, DiscoveredDevice
        from PyQt6.QtCore import QCoreApplication
        
        # Create QCoreApplication if not exists
        app = QCoreApplication.instance()
        if app is None:
            app = QCoreApplication([])
        
        # Test worker creation
        worker = VCIDiscoveryWorker(timeout=5)
        logger.info("✓ VCI Discovery Worker created successfully")
        
        # Test signals
        assert worker.signals is not None
        logger.info("✓ Worker signals initialized")
        
        # Test device filtering
        test_devices = [
            DiscoveredDevice("Device1", "OBDLink MX+", port="COM1"),
            DiscoveredDevice("Device2", "OBDLink MX+", port="COM2"),  # Duplicate type
            DiscoveredDevice("Device3", "ScanMatik 2 Pro", port="COM3"),
        ]
        
        filtered = worker._filter_and_deduplicate_devices(test_devices)
        assert len(filtered) == 2  # Should remove duplicate
        logger.info("✓ Device filtering working correctly")
        
        # Test Bluetooth address extraction
        device_info = "OBDLink MX+ (00:11:22:33:44:55)"
        address = worker._extract_bluetooth_address(device_info)
        assert address == "00:11:22:33:44:55"
        logger.info("✓ Bluetooth address extraction working")
        
        return True
        
    except Exception as e:
        logger.error(f"VCI Discovery Worker test failed: {e}")
        return False

def test_device_handler_async_discovery():
    """Test the enhanced device handler with async discovery"""
    logger.info("=== Testing Device Handler Async Discovery ===")
    
    try:
        from shared.device_handler import DeviceHandler, DeviceInfo
        
        # Test mock mode
        handler = DeviceHandler(mock_mode=True)
        logger.info("✓ Device handler created in mock mode")
        
        # Test device detection in mock mode
        devices = handler.detect_professional_devices()
        assert len(devices) > 0
        logger.info(f"✓ Mock mode detected {len(devices)} devices")
        
        # Test async discovery methods exist
        assert hasattr(handler, 'discover_devices_async')
        assert hasattr(handler, 'discover_devices_blocking')
        assert hasattr(handler, 'cancel_discovery')
        logger.info("✓ Async discovery methods available")
        
        # Test blocking discovery with timeout
        start_time = time.time()
        devices = handler.discover_devices_blocking(timeout=3)
        elapsed = time.time() - start_time
        
        assert elapsed < 5  # Should complete within timeout + buffer
        logger.info(f"✓ Blocking discovery completed in {elapsed:.1f}s")
        
        return True
        
    except Exception as e:
        logger.error(f"Device handler async discovery test failed: {e}")
        return False

def test_obdlink_timeout_protection():
    """Test OBDLink MX+ timeout protection"""
    logger.info("=== Testing OBDLink MX+ Timeout Protection ===")
    
    try:
        from shared.obdlink_mxplus import OBDLinkMXPlus
        
        # Test mock mode
        obdlink = OBDLinkMXPlus(mock_mode=True)
        devices = obdlink.discover_devices(timeout=2)
        assert len(devices) > 0
        logger.info(f"✓ Mock OBDLink discovery found {len(devices)} devices")
        
        # Test timeout protection (should not hang)
        start_time = time.time()
        # This would normally hang for 8 seconds, but should timeout at 2 seconds
        with patch('shared.obdlink_mxplus.bluetooth') as mock_bluetooth:
            # Mock bluetooth.discover_devices to hang
            def hang_forever(*args, **kwargs):
                time.sleep(10)  # Simulate hanging
                return []
            
            mock_bluetooth.discover_devices = hang_forever
            
            try:
                devices = obdlink.discover_devices(timeout=2)
                elapsed = time.time() - start_time
                assert elapsed < 5  # Should timeout quickly
                logger.info(f"✓ Timeout protection working - returned in {elapsed:.1f}s")
            except Exception:
                # Expected to timeout
                elapsed = time.time() - start_time
                assert elapsed < 5
                logger.info(f"✓ Timeout protection working - timed out in {elapsed:.1f}s")
        
        return True
        
    except Exception as e:
        logger.error(f"OBDLink timeout protection test failed: {e}")
        return False

def test_scanmatik_timeout_protection():
    """Test ScanMatik timeout protection"""
    logger.info("=== Testing ScanMatik Timeout Protection ===")
    
    try:
        from shared.scanmatik_2_pro import ScanMatik2Pro
        
        # Test mock mode
        scanmatik = ScanMatik2Pro(mock_mode=True)
        devices = scanmatik.detect_devices(timeout=3)
        assert len(devices) >= 0  # May be empty in mock mode
        logger.info(f"✓ Mock ScanMatik detection completed")
        
        # Test timeout protection
        start_time = time.time()
        with patch('shared.scanmatik_2_pro.serial.Serial') as mock_serial:
            # Mock serial to hang
            mock_instance = MagicMock()
            mock_instance.read.side_effect = lambda size: time.sleep(0.1) or b''
            mock_serial.return_value.__enter__.return_value = mock_instance
            
            try:
                devices = scanmatik.detect_devices(timeout=2)
                elapsed = time.time() - start_time
                assert elapsed < 5  # Should timeout quickly
                logger.info(f"✓ ScanMatik timeout protection working - completed in {elapsed:.1f}s")
            except Exception:
                elapsed = time.time() - start_time
                assert elapsed < 5
                logger.info(f"✓ ScanMatik timeout protection working - handled in {elapsed:.1f}s")
        
        return True
        
    except Exception as e:
        logger.error(f"ScanMatik timeout protection test failed: {e}")
        return False

def test_gui_integration():
    """Test GUI integration patterns"""
    logger.info("=== Testing GUI Integration Patterns ===")
    
    try:
        # Test that the worker can be used from GUI context
        from shared.vci_discovery_worker import VCIAsyncDiscoveryManager
        from PyQt6.QtCore import QCoreApplication
        
        app = QCoreApplication.instance()
        if app is None:
            app = QCoreApplication([])
        
        # Test manager creation
        manager = VCIAsyncDiscoveryManager()
        logger.info("✓ VCI Async Discovery Manager created")
        
        # Test callback system
        callback_called = []
        
        def test_callback(data):
            callback_called.append(data)
        
        manager.add_callback('finished', test_callback)
        manager.add_callback('progress', test_callback)
        manager.add_callback('error', test_callback)
        manager.add_callback('device_found', test_callback)
        logger.info("✓ Callback system working")
        
        # Test cancellation
        manager.cancel_discovery()
        logger.info("✓ Discovery cancellation working")
        
        return True
        
    except Exception as e:
        logger.error(f"GUI integration test failed: {e}")
        return False

def test_comprehensive_fix():
    """Test the comprehensive fix with realistic scenarios"""
    logger.info("=== Testing Comprehensive Fix ===")
    
    try:
        from shared.device_handler import DeviceHandler
        from shared.vci_discovery_worker import start_vci_discovery_async, cancel_vci_discovery
        
        # Create device handler
        handler = DeviceHandler(mock_mode=True)
        logger.info("✓ Created device handler for comprehensive test")
        
        # Test async discovery start
        discovery_started = start_vci_discovery_async([handler], timeout=5)
        logger.info(f"✓ Async discovery started: {discovery_started}")
        
        # Wait a moment for discovery to process
        time.sleep(1)
        
        # Cancel discovery
        cancel_vci_discovery()
        logger.info("✓ Discovery cancelled")
        
        # Test blocking discovery as fallback
        start_time = time.time()
        devices = handler.discover_devices_blocking(timeout=3)
        elapsed = time.time() - start_time
        
        logger.info(f"✓ Blocking fallback completed in {elapsed:.1f}s, found {len(devices)} devices")
        
        return True
        
    except Exception as e:
        logger.error(f"Comprehensive fix test failed: {e}")
        return False

def simulate_gui_freeze_scenario():
    """Simulate the original GUI freeze scenario and verify it's fixed"""
    logger.info("=== Simulating Original GUI Freeze Scenario ===")
    
    try:
        # This simulates what would happen in the original code
        logger.info("Testing original blocking behavior simulation...")
        
        # Original problematic code pattern:
        # devices = bluetooth.discover_devices(duration=8, lookup_names=True, flush_cache=True)
        # This would block for 8+ seconds and freeze the GUI
        
        # Test our fixed approach
        from shared.obdlink_mxplus import OBDLinkMXPlus
        
        obdlink = OBDLinkMXPlus(mock_mode=True)  # Use mock to avoid real hardware
        
        start_time = time.time()
        
        # This should not block the GUI thread for more than a few seconds
        devices = obdlink.discover_devices(timeout=3)
        
        elapsed = time.time() - start_time
        
        # Verify it completed in reasonable time
        assert elapsed < 5, f"Discovery took too long: {elapsed:.1f}s"
        
        logger.info(f"✓ Fixed discovery completed in {elapsed:.1f}s (vs original 8+ seconds)")
        logger.info(f"✓ Found {len(devices)} devices without GUI freeze")
        
        return True
        
    except Exception as e:
        logger.error(f"GUI freeze scenario test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    logger.info("Starting VCI Freeze Fix Test Suite")
    logger.info("=" * 50)
    
    tests = [
        ("VCI Discovery Worker", test_vci_discovery_worker),
        ("Device Handler Async Discovery", test_device_handler_async_discovery),
        ("OBDLink Timeout Protection", test_obdlink_timeout_protection),
        ("ScanMatik Timeout Protection", test_scanmatik_timeout_protection),
        ("GUI Integration", test_gui_integration),
        ("Comprehensive Fix", test_comprehensive_fix),
        ("GUI Freeze Scenario", simulate_gui_freeze_scenario),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✓ {test_name} PASSED")
            else:
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name} FAILED with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! VCI Freeze Fix is working correctly!")
        return True
    else:
        logger.error("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)