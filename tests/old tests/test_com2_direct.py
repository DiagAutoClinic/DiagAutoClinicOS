#!/usr/bin/env python3
"""
Direct test script to check VCI connection on COM2 for GoDiag GD101 passthru cable
"""

import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_com2_direct():
    """Test COM2 connection directly"""
    logger.info("Starting direct COM2 connection test")

    try:
        # Test 1: Check available COM ports
        logger.info("Test 1: Checking available COM ports...")

        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            available_ports = [p.device for p in ports]
            logger.info(f"Available COM ports: {available_ports}")

            com2_available = "COM2" in available_ports
            logger.info(f"COM2 available: {com2_available}")

            if not com2_available:
                logger.warning("COM2 not found in available ports")
                return False

        except ImportError:
            logger.warning("pyserial not available, cannot check COM ports")
            return False

        # Test 2: Try to open COM2 directly
        logger.info("\nTest 2: Attempting to open COM2 directly...")

        try:
            import serial
            ser = serial.Serial('COM2', baudrate=115200, timeout=1)
            logger.info("✅ SUCCESS: COM2 opened successfully")

            # Try to send a simple command
            ser.write(b'ATZ\r')  # Reset command
            ser.flush()

            # Wait for response
            import time
            time.sleep(0.5)

            response = ser.read(100)
            if response:
                logger.info(f"✅ SUCCESS: Received response from COM2: {response}")
            else:
                logger.warning("⚠️  WARNING: No response received from COM2")

            ser.close()
            logger.info("COM2 closed")

            return True

        except serial.SerialException as e:
            logger.error(f"❌ FAILED: Could not open COM2: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ ERROR: COM2 test failed: {e}")
            return False

    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_godiag_compatibility():
    """Test GoDiag GD101 compatibility"""
    logger.info("\nTest 3: Testing GoDiag GD101 compatibility...")

    try:
        # Test importing the GoDiag GD101 class
        from shared.j2534_passthru import GoDiagGD101PassThru, J2534Protocol
        logger.info("✅ SUCCESS: GoDiag GD101 classes imported successfully")

        # Create instance
        gd101 = GoDiagGD101PassThru(port="COM2", baudrate=115200)
        logger.info("✅ SUCCESS: GoDiag GD101 instance created")

        # Test opening
        if gd101.open():
            logger.info("✅ SUCCESS: GoDiag GD101 opened successfully on COM2")

            # Get OBD2 status
            obd2_status = gd101.get_obd2_status()
            logger.info(f"OBD2 Status: {obd2_status}")

            # Validate connection
            valid, errors = gd101.validate_obd2_connection()
            if valid:
                logger.info("✅ SUCCESS: OBD2 connection validation passed")
            else:
                logger.error(f"❌ FAILED: OBD2 connection validation failed: {errors}")

            # Test J2534 protocol
            channel_id = gd101.connect(J2534Protocol.ISO14229_UDS)
            if channel_id > 0:
                logger.info(f"✅ SUCCESS: Connected to J2534 protocol on channel {channel_id}")
                gd101.disconnect(channel_id)
            else:
                logger.error("❌ FAILED: Could not connect to J2534 protocol")

            gd101.close()
            return True
        else:
            logger.error("❌ FAILED: Could not open GoDiag GD101 on COM2")
            return False

    except ImportError as e:
        logger.error(f"❌ FAILED: Could not import GoDiag GD101 classes: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ ERROR: GoDiag GD101 test failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("=" * 60)
    logger.info("GoDiag GD101 VCI Connection Test on COM2")
    logger.info("=" * 60)

    # Test direct COM2 connection
    com2_success = test_com2_direct()

    # Test GoDiag compatibility
    godiag_success = test_godiag_compatibility()

    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    if com2_success and godiag_success:
        logger.info("✅ VCI Connection Test: PASSED")
        logger.info("GoDiag GD101 passthru cable is working on COM2")
    else:
        logger.error("❌ VCI Connection Test: FAILED")
        logger.error("GoDiag GD101 passthru cable is NOT working on COM2")

    logger.info("=" * 60)

    return com2_success and godiag_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)