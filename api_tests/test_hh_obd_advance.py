#!/usr/bin/env python3
"""
HH OBD Advance Test Script
Tests the advanced OBD device handler functionality with comprehensive features
"""

import sys
import time
import logging
from datetime import datetime

# Add the shared module to the path
sys.path.append('shared')

from hh_obd_advance import HHOBDAdvanceHandler, OBDDeviceType, create_hh_obd_advance_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def test_hh_obd_advance_mock_mode():
    """Test HH OBD Advance functionality in mock mode"""
    print_section("HH OBD ADVANCE TEST - MOCK MODE")
    
    # Create handler in mock mode
    print("1. Creating HH OBD Advance Handler (Mock Mode)")
    handler = create_hh_obd_advance_handler(mock_mode=True)
    
    print(f"   Handler created successfully")
    print(f"   Mock mode: {handler.mock_mode}")
    print(f"   Initial detected devices: {len(handler.detected_devices)}")
    
    # Test device status
    print("\n2. Getting Device Status")
    status = handler.get_device_status()
    print(f"   Connected: {status['connected']}")
    print(f"   Device: {status['device']}")
    print(f"   Port: {status['port']}")
    print(f"   Detected devices: {status['detected_devices']}")
    print(f"   Mock mode: {status['mock_mode']}")
    
    # Test OBD device detection (simulated)
    print("\n3. Testing OBD Device Detection")
    detected_devices = handler.detect_obdii_devices()
    print(f"   Detected {len(detected_devices)} devices")
    
    for i, device in enumerate(detected_devices, 1):
        print(f"   Device {i}:")
        print(f"     Type: {device.device_type.value}")
        print(f"     Name: {device.name}")
        print(f"     Port: {device.port}")
        print(f"     Description: {device.description}")
        print(f"     Capabilities: {', '.join(device.capabilities)}")
        print(f"     Protocol Support: {', '.join(device.protocol_support)}")
    
    # Test simulated connection
    print("\n4. Testing Device Connection")
    connection_result = handler.connect_obdii_device("OBDII")
    print(f"   Connection result: {connection_result}")
    
    if connection_result:
        print(f"   Connected to: {handler.connected_device.name}")
        print(f"   Port: {handler.connected_device.port}")
    
    # Test OBD command execution
    print("\n5. Testing OBD Command Execution")
    test_commands = [
        "010C",  # Engine RPM
        "010D",  # Vehicle Speed
        "0105",  # Coolant Temperature
        "0902",  # VIN
    ]
    
    for command in test_commands:
        print(f"   Executing command: {command}")
        result = handler.execute_obd_command(command)
        print(f"     Success: {result.get('success', False)}")
        if result.get('success'):
            print(f"     Response: {result.get('response', 'N/A')}")
        else:
            print(f"     Error: {result.get('error', 'Unknown error')}")
    
    # Test advanced data retrieval
    print("\n6. Testing Advanced OBD Data Retrieval")
    advanced_data = handler.get_advanced_obd_data()
    print(f"   Advanced data retrieval successful: {advanced_data.get('success', False)}")
    
    if advanced_data.get('success'):
        device_info = advanced_data.get('device_info', {})
        print(f"   Device Info:")
        print(f"     Name: {device_info.get('name', 'N/A')}")
        print(f"     Port: {device_info.get('port', 'N/A')}")
        print(f"     Type: {device_info.get('type', 'N/A')}")
        
        data = advanced_data.get('data', {})
        print(f"   Retrieved {len(data)} data points:")
        for key, value in data.items():
            if isinstance(value, dict):
                description = value.get('description', 'Unknown')
                val = value.get('value', 'N/A')
                print(f"     {key}: {description} = {val}")
    
    # Test disconnection
    print("\n7. Testing Disconnection")
    handler.disconnect()
    print(f"   Disconnected successfully")
    
    final_status = handler.get_device_status()
    print(f"   Final connection status: {final_status['connected']}")
    
    print_section("HH OBD ADVANCE TEST COMPLETED")


def test_real_hardware_detection():
    """Test real hardware detection (without connecting)"""
    print_section("HH OBD ADVANCE - REAL HARDWARE DETECTION TEST")
    
    print("1. Creating HH OBD Advance Handler (Real Hardware Mode)")
    handler = HHOBDAdvanceHandler(mock_mode=False)
    
    print("2. Scanning for real OBD devices...")
    print("   Note: This will scan common COM ports for OBD devices")
    
    detected_devices = handler.detect_obdii_devices()
    
    print(f"\n3. Detection Results:")
    print(f"   Found {len(detected_devices)} device(s)")
    
    if detected_devices:
        for i, device in enumerate(detected_devices, 1):
            print(f"\n   Device {i}:")
            print(f"     Type: {device.device_type.value}")
            print(f"     Name: {device.name}")
            print(f"     Port: {device.port}")
            print(f"     Description: {device.description}")
            print(f"     Is Real Hardware: {device.is_real_hardware}")
            
            # Prioritize OBDII devices
            if device.device_type == OBDDeviceType.OBDII_GENERIC:
                print(f"     *** PRIORITY: This is a 'OBDII' named device ***")
    
    # Test connection to first detected device
    if detected_devices:
        print(f"\n4. Attempting connection to first detected device...")
        first_device = detected_devices[0]
        connection_result = handler.connect_obdii_device(first_device.name)
        print(f"   Connection result: {connection_result}")
        
        if connection_result:
            print(f"   Successfully connected to: {handler.connected_device.name}")
            print(f"   Connected on port: {handler.connected_device.port}")
            
            # Test basic communication
            print(f"\n5. Testing basic OBD communication...")
            test_result = handler.execute_obd_command("ATI")
            print(f"   ATI command result: {test_result.get('success', False)}")
            if test_result.get('success'):
                print(f"   Response: {test_result.get('response', 'N/A')}")
            
            # Disconnect
            handler.disconnect()
            print(f"   Disconnected successfully")
        else:
            print(f"   Failed to connect to device")
    
    print_section("REAL HARDWARE DETECTION TEST COMPLETED")


def test_device_type_enumeration():
    """Test OBD device type enumeration"""
    print_section("OBD DEVICE TYPE ENUMERATION TEST")
    
    print("Supported OBD Device Types:")
    for device_type in OBDDeviceType:
        print(f"   {device_type.name}: {device_type.value}")
    
    print_section("DEVICE TYPE ENUMERATION TEST COMPLETED")


def test_protocol_mapping():
    """Test protocol mapping functionality"""
    print_section("PROTOCOL MAPPING TEST")
    
    handler = HHOBDAdvanceHandler(mock_mode=True)
    
    print("Supported Protocol Mappings:")
    for protocol_num, protocol_name in handler.protocol_mapping.items():
        print(f"   Protocol {protocol_num}: {protocol_name}")
    
    print_section("PROTOCOL MAPPING TEST COMPLETED")


def main():
    """Main test function"""
    print(f"HH OBD Advance Test Suite")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Python Version: {sys.version}")
    
    try:
        # Test 1: Mock mode functionality
        test_hh_obd_advance_mock_mode()
        
        # Test 2: Device type enumeration
        test_device_type_enumeration()
        
        # Test 3: Protocol mapping
        test_protocol_mapping()
        
        # Test 4: Real hardware detection (commented out by default)
        # Uncomment the following line if you want to test real hardware detection
        # test_real_hardware_detection()
        
        print(f"\n[SUCCESS] All tests completed successfully!")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)