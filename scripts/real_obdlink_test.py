#!/usr/bin/env python3
"""
Real OBDLink MX+ CAN Sniffing Test
Connects to physical OBDLink MX+ device in OBD-II port
"""

import time
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def test_real_obdlink_mxplus():
    """Test real OBDLink MX+ with physical connection"""
    print("Real OBDLink MX+ CAN Sniffing Test")
    print("=" * 45)
    print("*** Connected to physical OBDLink MX+ in OBD-II port ***")
    print()
    
    try:
        # Import the OBDLink MX+ module
        from shared.obdlink_mxplus import create_obdlink_mxplus, OBDLinkProtocol
        
        # Create real instance (NOT mock mode)
        print("Creating real OBDLink MX+ instance...")
        obdlink = create_obdlink_mxplus(mock_mode=False)
        print("[OK] Real OBDLink MX+ instance created")
        
        # Test 1: Check available serial ports
        print("\nChecking available serial ports...")
        try:
            import serial.tools.list_ports
            ports = list(serial.tools.list_ports.comports())
            
            if ports:
                print("Available serial ports:")
                for port, desc, hwid in sorted(ports):
                    print(f"  {port}: {desc}")
            else:
                print("[WARNING] No serial ports found")
                print("Make sure OBDLink MX+ is connected via USB")
        except ImportError:
            print("[WARNING] pyserial not available - cannot list ports")
        except Exception as e:
            print(f"[ERROR] Port check failed: {e}")
        
        # Test 2: Try common OBDLink MX+ serial ports
        print("\nTesting OBDLink MX+ connection...")
        test_ports = ['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8']
        connected = False
        
        for port in test_ports:
            try:
                print(f"  Trying {port}...")
                if obdlink.connect_serial(port, baudrate=38400):
                    print(f"  [OK] Connected successfully via {port}")
                    connected = True
                    break
                else:
                    print(f"  [FAIL] Failed to connect via {port}")
            except Exception as e:
                print(f"  [FAIL] Error with {port}: {e}")
                continue
        
        if not connected:
            print("\n[ERROR] Could not connect to OBDLink MX+ on any port")
            print("\nTroubleshooting steps:")
            print("1. Verify OBDLink MX+ is plugged into OBD-II port")
            print("2. Check if device shows up in Device Manager")
            print("3. Try different COM ports")
            print("4. Ensure proper drivers are installed")
            return False
        
        # Test 3: Initialize device
        print("\nInitializing OBDLink MX+...")
        if obdlink._initialize_device():
            print("[OK] Device initialized successfully")
        else:
            print("[WARNING] Device initialization unclear - continuing anyway")
        
        # Test 4: Set vehicle profile
        print("\nSetting vehicle profile...")
        vehicle_profiles = ['chevrolet_cruze_2014', 'ford_ranger_2014', 'generic_gm']
        
        for profile in vehicle_profiles:
            if obdlink.set_vehicle_profile(profile):
                print(f"[OK] Vehicle profile set: {profile}")
                break
        else:
            print("[WARNING] Could not set specific profile - using default")
        
        # Test 5: Configure CAN sniffing
        print("\nConfiguring CAN sniffing...")
        if obdlink.configure_can_sniffing(OBDLinkProtocol.ISO15765_11BIT):
            print("[OK] CAN sniffing configured for ISO15765-11BIT")
        else:
            print("[FAIL] Failed to configure CAN sniffing")
            return False
        
        # Test 6: Start real CAN monitoring
        print("\nStarting real CAN bus monitoring...")
        print("*** Reading actual vehicle CAN traffic...")
        
        if obdlink.start_monitoring():
            print("[OK] Real CAN monitoring started!")
            print("\nCapturing live CAN messages for 10 seconds...")
            
            # Capture real messages
            start_time = time.time()
            all_messages = []
            
            while time.time() - start_time < 10:
                messages = obdlink.read_messages(count=5, timeout_ms=100)
                if messages:
                    all_messages.extend(messages)
                    for msg in messages:
                        print(f"CAN: {msg}")
                
                time.sleep(0.1)
            
            # Stop monitoring
            obdlink.stop_monitoring()
            print(f"\n[OK] Captured {len(all_messages)} real CAN messages")
            
            # Analyze captured messages
            if all_messages:
                print("\nMessage Analysis:")
                stats = obdlink.get_message_statistics()
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                
                # Show unique arbitration IDs
                unique_ids = set()
                for msg in all_messages:
                    if hasattr(msg, 'arbitration_id') and msg.arbitration_id:
                        unique_ids.add(msg.arbitration_id)
                
                print(f"\nUnique CAN IDs detected: {sorted(unique_ids)}")
                
                # Save to file
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"real_can_capture_{timestamp}.txt"
                
                with open(filename, 'w') as f:
                    f.write(f"Real CAN Messages captured at {timestamp}\n")
                    f.write("=" * 50 + "\n")
                    for msg in all_messages:
                        f.write(f"{msg}\n")
                
                print(f"\nMessages saved to: {filename}")
            else:
                print("[WARNING] No messages captured")
                print("Possible reasons:")
                print("- Vehicle engine not running")
                print("- No CAN traffic on this vehicle")
                print("- Wrong protocol configuration")
        else:
            print("[FAIL] Could not start CAN monitoring")
            return False
        
        # Test 7: Disconnect
        print("\nDisconnecting...")
        obdlink.disconnect()
        print("[OK] Disconnected successfully")
        
        print("\n[SUCCESS] Real OBDLink MX+ CAN Sniffing Test Completed!")
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print("Check if all required modules are installed")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("*** REAL OBDLink MX+ CAN SNIFFER ***")
    print("=" * 50)
    print("This test connects to your physical OBDLink MX+ device")
    print("Make sure it's plugged into the vehicle's OBD-II port")
    print()
    
    success = test_real_obdlink_mxplus()
    
    if success:
        print("\n*** SUCCESS! Your OBDLink MX+ is capturing real CAN traffic! ***")
    else:
        print("\n*** Test failed. Check connections and try again. ***")
    
    print("\nPress any key to exit...")
    try:
        input()
    except:
        pass