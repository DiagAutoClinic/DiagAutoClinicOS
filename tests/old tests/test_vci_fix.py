#!/usr/bin/env python3
"""
Test script to verify the VCI manager fix for the infinite loop issue
"""

import sys
import time
import threading
from AutoDiag.core.vci_manager import VCIManager, get_vci_manager

def test_vci_scan_timeout():
    """Test that VCI scanning doesn't hang indefinitely"""
    print("Testing VCI manager scan timeout fix...")

    # Create a new VCI manager instance
    vci_manager = VCIManager()

    # Test with a short timeout
    start_time = time.time()
    devices = vci_manager.scan_for_devices(timeout=5)

    elapsed = time.time() - start_time
    print(f"VCI scan completed in {elapsed:.2f} seconds")
    print(f"Found {len(devices)} devices")

    # Verify the scan didn't take longer than timeout + reasonable margin
    if elapsed > 15:  # Allow some margin for system variations
        print("❌ FAILED: Scan took too long, potential infinite loop still exists")
        return False
    else:
        print("✅ PASSED: Scan completed within reasonable time")
        return True

def test_vci_scan_threaded():
    """Test VCI scanning in a separate thread to ensure it doesn't block"""
    print("\nTesting VCI manager scan in separate thread...")

    vci_manager = VCIManager()
    result = {"success": False, "devices": 0, "elapsed": 0}

    def scan_thread():
        start_time = time.time()
        devices = vci_manager.scan_for_devices(timeout=3)
        result["elapsed"] = time.time() - start_time
        result["devices"] = len(devices)
        result["success"] = True

    # Start scan in separate thread
    scan_thread_obj = threading.Thread(target=scan_thread)
    scan_thread_obj.start()

    # Wait for thread to complete with timeout
    scan_thread_obj.join(timeout=10)

    if scan_thread_obj.is_alive():
        print("❌ FAILED: Scan thread is still running after timeout")
        return False

    if result["success"]:
        print(f"✅ PASSED: Threaded scan completed in {result['elapsed']:.2f} seconds")
        print(f"Found {result['devices']} devices")
        return True
    else:
        print("❌ FAILED: Scan thread did not complete successfully")
        return False

def test_j2534_scan_safety():
    """Test J2534 scanning specifically for the infinite loop fix"""
    print("\nTesting J2534 scan safety...")

    vci_manager = VCIManager()

    # Test the J2534 scan method directly
    start_time = time.time()

    try:
        # This should not hang even if no J2534 devices are present
        vci_manager._scan_j2534_devices()
        elapsed = time.time() - start_time

        if elapsed > 5:  # Should be very fast if no devices
            print(f"❌ FAILED: J2534 scan took {elapsed:.2f} seconds - potential hang")
            return False
        else:
            print(f"✅ PASSED: J2534 scan completed in {elapsed:.2f} seconds")
            return True

    except Exception as e:
        print(f"❌ FAILED: J2534 scan raised exception: {e}")
        return False

def main():
    """Run all tests"""
    print("VCI Manager Fix Verification Tests")
    print("=" * 50)

    tests = [
        test_vci_scan_timeout,
        test_vci_scan_threaded,
        test_j2534_scan_safety
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The VCI manager fix is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. The fix may need additional work.")
        return 1

if __name__ == "__main__":
    sys.exit(main())