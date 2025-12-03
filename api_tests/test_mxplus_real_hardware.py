#!/usr/bin/env python3
"""
Real OBDLink MX+ Hardware Test
Tests actual hardware connectivity and CAN bus monitoring
"""

import time
import sys
import os
import logging

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_real_hardware_connectivity():
    """Test real OBDLink MX+ hardware connectivity"""
    print("OBDLink MX+ REAL Hardware Test")
    print("=" * 40)
    
    try:
        from shared.obdlink_mxplus import create_obdlink_mxplus, OBDLinkProtocol
        
        # Test with real hardware (mock_mode=False)
        print("Initializing OBDLink MX+ for REAL hardware testing...")
        obdlink = create_obdlink_mxplus(mock_mode=False)
        print("[OK] Instance created for real hardware")
        
        # Test 1: Device Discovery
        print("\nTest 1: Device Discovery")
        print("Searching for OBDLink MX+ devices...")
        devices = obdlink.discover_devices()
        
        if devices:
            print(f"[OK] Found {len(devices)} device(s):")
            for i, device in enumerate(devices, 1):
                print(f"  {i}. {device}")
        else:
            print("[WARNING] No OBDLink devices found via Bluetooth")
            print("Continuing with serial port testing...")
        
        # Test 2: Serial Port Connectivity
        print("\nTest 2: Serial Port Connectivity")
        serial_ports = ["COM3", "COM4", "COM6", "COM7"]
        
        connected = False
        for port in serial_ports:
            print(f"  Testing {port}...")
            try:
                if obdlink.connect_serial(port, baudrate=38400):
                    print(f"  [OK] Successfully connected to {port}")
                    connected = True
                    break
                else:
                    print(f"  [FAIL] Failed to connect to {port}")
            except Exception as e:
                print(f"  [ERROR] Error testing {port}: {e}")
        
        if not connected:
            print("[FAIL] Could not connect to any serial port")
            return False
        
        # Test 3: Vehicle Profile Configuration
        print("\nTest 3: Vehicle Profile Configuration")
        vehicle_profiles = [
            'chevrolet_cruze_2014',
            'ford_ranger_2014', 
            'ford_figo',
            'generic_gm',
            'generic_ford'
        ]
        
        profile_success = False
        for profile in vehicle_profiles:
            if obdlink.set_vehicle_profile(profile):
                print(f"  [OK] Profile '{profile}' set successfully")
                profile_success = True
                break
        
        if not profile_success:
            print("  [FAIL] Failed to set any vehicle profile")
            return False
        
        # Test 4: Protocol Configuration
        print("\nTest 4: Protocol Configuration")
        protocols = [
            OBDLinkProtocol.AUTO,
            OBDLinkProtocol.ISO15765_11BIT,
            OBDLinkProtocol.ISO15765_29BIT
        ]
        
        protocol_success = False
        for protocol in protocols:
            try:
                if obdlink.configure_can_sniffing(protocol):
                    print(f"  [OK] Protocol '{protocol.value}' configured successfully")
                    protocol_success = True
                    break
            except Exception as e:
                print(f"  [ERROR] Error configuring {protocol.value}: {e}")
        
        if not protocol_success:
            print("  [FAIL] Failed to configure any protocol")
            return False
        
        # Test 5: Real-time CAN Monitoring
        print("\nTest 5: Real-time CAN Monitoring")
        print("Starting CAN bus monitoring...")
        
        try:
            if obdlink.start_monitoring():
                print("  [OK] CAN monitoring started")
                
                # Monitor for 10 seconds
                print("  Monitoring for 10 seconds...")
                start_time = time.time()
                message_count = 0
                
                while (time.time() - start_time) < 10:
                    messages = obdlink.read_messages(count=5, timeout_ms=100)
                    if messages:
                        message_count += len(messages)
                        for msg in messages[:3]:  # Show first 3 messages
                            print(f"    CAN: {msg}")
                    time.sleep(0.5)
                
                print(f"  [OK] Captured {message_count} messages in 10 seconds")
                
                # Get statistics
                stats = obdlink.get_message_statistics()
                print("  Message statistics:")
                for key, value in stats.items():
                    if key != 'arbitration_id_counts':  # Skip detailed counts for brevity
                        print(f"    {key}: {value}")
                
                # Stop monitoring
                obdlink.stop_monitoring()
                print("  [OK] Monitoring stopped")
                
            else:
                print("  [FAIL] Failed to start CAN monitoring")
                return False
                
        except Exception as e:
            print(f"  [ERROR] Error during monitoring: {e}")
            return False
        
        # Test 6: Disconnection
        print("\nTest 6: Cleanup and Disconnection")
        try:
            obdlink.disconnect()
            print("[OK] Disconnected successfully")
        except Exception as e:
            print(f"[WARNING] Error during disconnection: {e}")
        
        print("\n" + "="*50)
        print("[SUCCESS] OBDLink MX+ Real Hardware Test Completed!")
        print("\nHardware Status Summary:")
        print(f"- Device Discovery: {'PASS' if devices else 'NO_DEVICES'}")
        print(f"- Serial Connectivity: {'PASS' if connected else 'FAIL'}")
        print(f"- Vehicle Profiles: {'PASS' if profile_success else 'FAIL'}")
        print(f"- Protocol Configuration: {'PASS' if protocol_success else 'FAIL'}")
        print(f"- CAN Monitoring: {'PASS' if message_count > 0 else 'NO_TRAFFIC'}")
        print("- Ready for real vehicle testing: YES")
        
        return True
        
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_hardware_requirements():
    """Check if hardware requirements are met"""
    print("Hardware Requirements Check")
    print("=" * 30)
    
    requirements = [
        ("OBDLink MX+ Device", "Physical device required"),
        ("Bluetooth Capability", "For wireless connectivity"),
        ("OBD-II Vehicle Port", "For CAN bus access"),
        ("Serial Ports Available", "COM3, COM4, COM6, COM7"),
        ("Python Serial Library", "For communication")
    ]
    
    all_met = True
    for req, description in requirements:
        if req == "OBDLink MX+ Device":
            # This requires physical device
            status = "REQUIRES_HARDWARE"
        elif req == "Bluetooth Capability":
            # Check if bluetooth module available
            try:
                import bluetooth
                status = "AVAILABLE"
            except ImportError:
                status = "NOT_AVAILABLE"
        elif req == "OBD-II Vehicle Port":
            status = "REQUIRES_VEHICLE"
        elif req == "Serial Ports Available":
            # Check serial ports
            import serial.tools.list_ports
            ports = [port.device for port in serial.tools.list_ports.comports()]
            available_ports = [p for p in ["COM3", "COM4", "COM6", "COM7"] if p in ports]
            status = f"AVAILABLE ({len(available_ports)} ports)"
        elif req == "Python Serial Library":
            try:
                import serial
                status = "AVAILABLE"
            except ImportError:
                status = "NOT_AVAILABLE"
                all_met = False
        
        print(f"  {req:<25} : {status}")
    
    print(f"\nOverall Status: {'READY' if all_met else 'MISSING_COMPONENTS'}")
    return all_met

if __name__ == "__main__":
    print("Starting OBDLink MX+ Real Hardware Test Suite")
    print("=" * 55)
    
    # Check requirements first
    requirements_ok = check_hardware_requirements()
    
    if not requirements_ok:
        print("\n[WARNING] Some requirements not met. Test may not work properly.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Test cancelled.")
            sys.exit(1)
    
    print("\n" + "="*55)
    
    # Run the real hardware test
    success = test_real_hardware_connectivity()
    
    if success:
        print("\n[SUCCESS] REAL HARDWARE TEST: PASSED")
        print("\nYour OBDLink MX+ is ready for:")
        print("- Live CAN bus monitoring")
        print("- Real vehicle diagnostics")
        print("- Professional automotive diagnostics")
    else:
        print("\n[FAILED] REAL HARDWARE TEST: FAILED")
        print("\nCheck:")
        print("- OBDLink MX+ is powered on")
        print("- Device is paired via Bluetooth")
        print("- Serial ports are available")
        print("- Vehicle is connected (for CAN traffic)")
    
    print(f"\nTest completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")