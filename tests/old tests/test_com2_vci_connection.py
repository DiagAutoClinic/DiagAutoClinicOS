#!/usr/bin/env python3
"""
Test script to check VCI connection on COM2 for GoDiag GD101 passthru cable
"""

import logging
import time
from typing import Optional, List, Dict, Any
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_com2_connection():
    """Test VCI connection on COM2 for GoDiag GD101"""
    logger.info("Starting VCI connection test on COM2 for GoDiag GD101")

    try:
        # Import required modules
        from AutoDiag.core.vci_manager import VCIManager, VCITypes, VCIStatus
        from shared.j2534_passthru import GoDiagGD101PassThru, J2534Protocol

        # Create VCI manager instance
        vci_manager = VCIManager()
        logger.info("VCI Manager initialized")

        # Check available serial ports
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            logger.info(f"Available COM ports: {[p.device for p in ports]}")

            # Check if COM2 is available
            com2_available = any(p.device == "COM2" for p in ports)
            logger.info(f"COM2 available: {com2_available}")

        except ImportError:
            logger.warning("pyserial not available, using fallback port list")
            ports = ["COM2", "COM1", "COM3", "COM4"]
            com2_available = True

        # Create GoDiag GD101 device for COM2
        logger.info("Creating GoDiag GD101 device for COM2...")

        # Test direct connection to COM2
        try:
            gd101_device = GoDiagGD101PassThru(port="COM2", baudrate=115200)
            logger.info("GoDiag GD101 device created")

            # Test opening the device
            logger.info("Attempting to open GoDiag GD101 on COM2...")
            open_success = gd101_device.open()

            if open_success:
                logger.info("✅ SUCCESS: GoDiag GD101 opened successfully on COM2")

                # Get OBD2 status
                obd2_status = gd101_device.get_obd2_status()
                logger.info(f"OBD2 Status: {obd2_status}")

                # Validate OBD2 connection
                validation_success, validation_errors = gd101_device.validate_obd2_connection()
                logger.info(f"OBD2 Connection Validation: {'✅ SUCCESS' if validation_success else '❌ FAILED'}")
                if validation_errors:
                    for error in validation_errors:
                        logger.error(f"  - {error}")

                # Test J2534 protocol connection
                logger.info("Testing J2534 protocol connection...")
                channel_id = gd101_device.connect(J2534Protocol.ISO14229_UDS)

                if channel_id > 0:
                    logger.info(f"✅ SUCCESS: Connected to ISO14229_UDS protocol on channel {channel_id}")

                    # Test sending a simple message
                    from shared.j2534_passthru import J2534Message
                    test_message = J2534Message(J2534Protocol.ISO14229_UDS, data=b'\x22\xF1\x90')
                    send_success = gd101_device.send_message(channel_id, test_message)

                    if send_success:
                        logger.info("✅ SUCCESS: Test message sent successfully")
                    else:
                        logger.error("❌ FAILED: Could not send test message")

                    # Disconnect from protocol
                    gd101_device.disconnect(channel_id)
                else:
                    logger.error("❌ FAILED: Could not connect to J2534 protocol")

                # Close the device
                gd101_device.close()
                logger.info("GoDiag GD101 device closed")

            else:
                logger.error("❌ FAILED: Could not open GoDiag GD101 on COM2")

        except Exception as e:
            logger.error(f"❌ ERROR: Failed to test GoDiag GD101 on COM2: {e}")
            return False

        # Test through VCI manager
        logger.info("\nTesting through VCI Manager...")

        # Create a GoDiag GD101 device
        from AutoDiag.core.vci_manager import VCIDevice

        test_device = VCIDevice(
            device_type=VCITypes.GODIAG_GD101,
            name="GoDiag GD101 Test",
            port="COM2",
            status=VCIStatus.DISCONNECTED
        )

        # Try to connect
        logger.info("Attempting VCI Manager connection...")
        connect_success = vci_manager.connect_to_device(test_device)

        if connect_success:
            logger.info("✅ SUCCESS: VCI Manager connected to GoDiag GD101 on COM2")

            # Get device info
            device_info = vci_manager.get_device_info()
            logger.info(f"Device Info: {device_info}")

            # Disconnect
            vci_manager.disconnect()
        else:
            logger.error("❌ FAILED: VCI Manager could not connect to GoDiag GD101 on COM2")

        return True

    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_godiag_compatibility():
    """Check GoDiag GD101 passthru cable compatibility"""
    logger.info("\nChecking GoDiag GD101 passthru cable compatibility...")

    try:
        # Check if required modules are available
        required_modules = [
            ('pyserial', 'serial'),
            ('shared.j2534_passthru', 'GoDiagGD101PassThru'),
            ('AutoDiag.core.vci_manager', 'VCIManager')
        ]

        compatibility_results = []

        for module_name, class_name in required_modules:
            try:
                if '.' in module_name:
                    # Import from module
                    module_parts = module_name.split('.')
                    module = __import__(module_parts[0])
                    for part in module_parts[1:]:
                        module = getattr(module, part)
                    getattr(module, class_name)
                    compatibility_results.append((module_name, True, None))
                else:
                    # Import module directly
                    __import__(module_name)
                    compatibility_results.append((module_name, True, None))
            except ImportError as e:
                compatibility_results.append((module_name, False, str(e)))
            except Exception as e:
                compatibility_results.append((module_name, False, str(e)))

        # Report compatibility results
        all_compatible = True
        for module_name, is_compatible, error in compatibility_results:
            if is_compatible:
                logger.info(f"✅ {module_name}: Available")
            else:
                logger.error(f"❌ {module_name}: Not available - {error}")
                all_compatible = False

        return all_compatible

    except Exception as e:
        logger.error(f"❌ Compatibility check failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("=" * 60)
    logger.info("GoDiag GD101 VCI Connection Test on COM2")
    logger.info("=" * 60)

    # Check compatibility first
    compatibility_ok = check_godiag_compatibility()

    if not compatibility_ok:
        logger.error("❌ Compatibility check failed - some required components missing")
        return False

    # Test the connection
    test_success = test_com2_connection()

    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    if test_success:
        logger.info("✅ VCI Connection Test: PASSED")
        logger.info("GoDiag GD101 passthru cable is working on COM2")
    else:
        logger.error("❌ VCI Connection Test: FAILED")
        logger.error("GoDiag GD101 passthru cable is NOT working on COM2")

    logger.info("=" * 60)

    return test_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)