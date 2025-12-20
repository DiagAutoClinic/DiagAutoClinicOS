"""
Test script for COM2 hardware connection (GD101)
This script tests the actual hardware connection on COM2.
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
        logging.FileHandler('test_com2_hardware.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_com2_connection():
    """Test direct COM2 connection for GD101"""
    logger.info("Testing COM2 hardware connection for GD101")
    
    try:
        from AutoDiag.core.vci_manager import get_vci_manager
        
        # Initialize VCI manager
        vci_manager = get_vci_manager()
        logger.info("VCI manager initialized")
        
        # Scan for devices
        logger.info("Scanning for VCI devices...")
        devices = vci_manager.scan_for_devices(timeout=10)
        
        if not devices:
            logger.error("No VCI devices found")
            return False
        
        logger.info(f"Found {len(devices)} VCI device(s)")
        
        # Find GD101 on COM2 (including N32G42x Port)
        gd101_device = None
        for device in devices:
            if ("GD101" in device.name or "N32G42x Port" in device.name) and device.port == "COM2":
                gd101_device = device
                break
        
        if not gd101_device:
            logger.error("GD101 device not found on COM2")
            return False
        
        logger.info(f"Found GD101 on COM2: {gd101_device.name}")
        
        # Connect to GD101 on COM2
        logger.info("Connecting to GD101 on COM2...")
        if vci_manager.connect_to_device(gd101_device):
            logger.info("Successfully connected to GD101 on COM2")
            
            # Test connection status
            if vci_manager.is_connected():
                logger.info("Connection status: CONNECTED")
                
                # Get device info
                device_info = vci_manager.get_device_info()
                logger.info(f"Device info: {device_info}")
                
                # Test basic communication
                logger.info("Testing basic communication...")
                
                # Disconnect
                vci_manager.disconnect()
                logger.info("Disconnected from GD101")
                
                return True
            else:
                logger.error("Connection failed - device not connected")
                return False
        else:
            logger.error("Failed to connect to GD101 on COM2")
            return False
        
    except Exception as e:
        logger.error(f"COM2 connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_serial_connection():
    """Test direct serial connection to COM2"""
    logger.info("Testing direct serial connection to COM2")
    
    try:
        import serial
        
        # Test if we can access serial module
        logger.info("Serial module imported successfully")
        
        # Test COM2 availability
        logger.info("Testing COM2 availability...")
        
        # Try to open COM2
        try:
            with serial.Serial('COM2', baudrate=115200, timeout=1) as ser:
                logger.info("Successfully opened COM2")
                logger.info(f"Serial port settings: {ser.get_settings()}")
                return True
        except serial.SerialException as e:
            logger.error(f"Failed to open COM2: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error with COM2: {e}")
            return False
            
    except ImportError:
        logger.error("Serial module not available")
        return False
    except Exception as e:
        logger.error(f"Direct serial test failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("=" * 60)
    logger.info("COM2 Hardware Connection Test")
    logger.info("Testing GD101 on COM2")
    logger.info("=" * 60)
    
    success = True
    
    # Test direct serial connection
    if not test_direct_serial_connection():
        logger.warning("Direct serial connection test failed")
        success = False
    
    # Test VCI connection
    if not test_com2_connection():
        logger.warning("VCI connection test failed")
        success = False
    
    # Final result
    logger.info("=" * 60)
    if success:
        logger.info("ALL COM2 HARDWARE TESTS PASSED")
        logger.info("GD101 on COM2 is working correctly")
    else:
        logger.error("SOME COM2 HARDWARE TESTS FAILED")
        logger.error("Please check the hardware connection")
    
    logger.info("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)