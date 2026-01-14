
import sys
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    logger.info("Checking dependencies...")
    
    # Check PySerial
    try:
        import serial
        import serial.tools.list_ports
        logger.info(f"PySerial available: Version {serial.__version__}")
        
        # List ports
        ports = list(serial.tools.list_ports.comports())
        logger.info(f"Found {len(ports)} serial ports:")
        for p in ports:
            logger.info(f"  - {p.device}: {p.description} [{p.hwid}]")
            
    except ImportError:
        logger.error("PySerial not installed!")
        return False
        
    # Check PyBluez
    try:
        import bluetooth
        logger.info("PyBluez (bluetooth) available")
    except ImportError:
        logger.warning("PyBluez (bluetooth) not installed - Bluetooth discovery will fail")
    
    return True

def test_mxplus_connection():
    logger.info("\nTesting OBDLink MX+ Connection Logic...")
    
    try:
        sys.path.append('.')
        from shared.obdlink_mxplus import OBDLinkMXPlus
        
        mx = OBDLinkMXPlus(mock_mode=False)
        
        # Test 1: Bluetooth Discovery
        logger.info("\n[Test 1] Bluetooth Discovery (Timeout 5s)...")
        devices = mx.discover_devices(timeout=5)
        logger.info(f"Discovered {len(devices)} Bluetooth devices:")
        for dev in devices:
            logger.info(f"  - {dev}")
            
        # Test 2: Serial Scan
        logger.info("\n[Test 2] Serial Port Scan...")
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        
        found_mx = False
        for p in ports:
            # Look for common OBDLink identifiers in description/hwid
            if "OBDLink" in p.description or "STN" in p.description or "COM" in p.device:
                logger.info(f"Attempting connection on {p.device} (Auto-detect baud)...")
                if mx.connect_serial(p.device): # Auto-detect baudrate
                    logger.info(f"SUCCESS: Connected to OBDLink MX+ on {p.device}")
                    found_mx = True
                    mx.disconnect()
                    break
                else:
                    logger.info(f"Failed to connect on {p.device}")
        
        if not found_mx:
            logger.warning("Could not connect to OBDLink MX+ on any detected port.")

    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if check_dependencies():
        test_mxplus_connection()
