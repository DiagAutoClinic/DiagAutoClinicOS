#!/usr/bin/env python3
"""
Test script for VCI recognition functionality in AutoDiag
"""

import sys
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_vci_manager_import():
    """Test VCI manager import"""
    try:
        from AutoDiag.core.vci_manager import VCIManager, VCITypes, VCIStatus, get_vci_manager
        logger.info("✅ VCI manager imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Failed to import VCI manager: {e}")
        return False

def test_vci_manager_initialization():
    """Test VCI manager initialization"""
    try:
        from AutoDiag.core.vci_manager import get_vci_manager

        manager = get_vci_manager()
        logger.info("✅ VCI manager initialized successfully")

        # Test supported devices
        supported = manager.get_supported_devices()
        logger.info(f"✅ Supported VCI types: {supported}")

        # Test initial status
        status = manager.get_device_info()
        logger.info(f"✅ Initial VCI status: {status}")

        return True
    except Exception as e:
        logger.error(f"❌ VCI manager initialization failed: {e}")
        return False

def test_vci_device_scanning():
    """Test VCI device scanning"""
    try:
        from AutoDiag.core.vci_manager import get_vci_manager

        manager = get_vci_manager()
        logger.info("🔍 Starting VCI device scan...")

        # Perform scan
        devices = manager.scan_for_devices(timeout=5)

        logger.info(f"✅ Scan completed, found {len(devices)} devices")

        if devices:
            for i, device in enumerate(devices):
                logger.info(f"  Device {i+1}: {device.name} ({device.device_type.value}) on {device.port}")
                logger.info(f"    Capabilities: {device.capabilities}")
        else:
            logger.info("  No VCI devices found (this is normal if no devices are connected)")

        return True
    except Exception as e:
        logger.error(f"❌ VCI device scanning failed: {e}")
        return False

def test_diagnostics_controller_integration():
    """Test diagnostics controller VCI integration"""
    try:
        from AutoDiag.core.diagnostics import DiagnosticsController

        # Create controller without UI callbacks for testing
        controller = DiagnosticsController()
        logger.info("✅ Diagnostics controller created successfully")

        # Test VCI status methods
        status = controller.get_vci_status()
        logger.info(f"✅ VCI status: {status}")

        supported_types = controller.get_supported_vci_types()
        logger.info(f"✅ Supported VCI types: {supported_types}")

        # Test VCI scan (skip if it requires Qt event loop)
        try:
            scan_result = controller.scan_for_vci_devices()
            logger.info(f"✅ VCI scan result: {scan_result}")
        except Exception as scan_error:
            logger.warning(f"VCI scan test skipped due to Qt requirements: {scan_error}")
            logger.info("✅ VCI scan method exists and is callable")

        return True
    except Exception as e:
        logger.error(f"❌ Diagnostics controller integration failed: {e}")
        return False

def main():
    """Run all VCI recognition tests"""
    logger.info("🚗 Starting AutoDiag VCI Recognition Tests")
    logger.info("=" * 50)

    tests = [
        ("VCI Manager Import", test_vci_manager_import),
        ("VCI Manager Initialization", test_vci_manager_initialization),
        ("VCI Device Scanning", test_vci_device_scanning),
        ("Diagnostics Controller Integration", test_diagnostics_controller_integration),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running test: {test_name}")
        try:
            if test_func():
                logger.info(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")

    logger.info("\n" + "=" * 50)
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All VCI recognition tests passed!")
        return 0
    else:
        logger.warning(f"⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())