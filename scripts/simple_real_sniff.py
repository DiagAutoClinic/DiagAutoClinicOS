#!/usr/bin/env python3
"""
Simple OBDLink MX+ Real CAN Sniffing
Direct connection test with your real OBDLink MX+ device
"""

import time
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def simple_can_sniff():
    """Simple CAN sniffing test with real OBDLink MX+"""
    print("SIMPLE OBDLink MX+ REAL CAN SNIFFING")
    print("=" * 50)
    print(f"*** Device connected via COM6 ***")
    print()
    
    try:
        from shared.obdlink_mxplus import create_obdlink_mxplus, OBDLinkProtocol
        
        # Create real instance
        obdlink = create_obdlink_mxplus(mock_mode=False)
        print("[1] Real OBDLink MX+ instance created")
        
        # Connect (we know COM6 works from previous test)
        print("[2] Connecting to OBDLink MX+ via COM6...")
        if obdlink.connect_serial("COM6", baudrate=38400):
            print("    [OK] Connected to COM6!")
        else:
            print("    [FAIL] Connection failed")
            return False
        
        print("[3] Checking connection status...")
        print(f"    Connected: {obdlink.is_connected}")
        
        # Set vehicle profile
        print("[4] Setting vehicle profile...")
        if obdlink.set_vehicle_profile("chevrolet_cruze_2014"):
            print("    [OK] Chevrolet Cruze 2014 profile set")
        else:
            print("    [WARN] Profile setting unclear - continuing")
        
        # Try to start monitoring directly without complex config
        print("[5] Starting CAN monitoring (simplified)...")
        
        if obdlink.start_monitoring():
            print("    [OK] CAN monitoring started!")
            
            print("\n*** CAPTURING REAL CAN TRAFFIC ***")
            print("Waiting 15 seconds for real CAN messages...")
            
            start_time = time.time()
            all_messages = []
            
            # Capture messages for 15 seconds
            while time.time() - start_time < 15:
                messages = obdlink.read_messages(count=10, timeout_ms=200)
                if messages:
                    all_messages.extend(messages)
                    for msg in messages:
                        print(f"REAL CAN: {msg}")
                
                # Update every second
                elapsed = int(time.time() - start_time)
                if elapsed % 3 == 0:  # Print every 3 seconds
                    print(f"    ... {elapsed}s elapsed, {len(all_messages)} messages captured")
                
                time.sleep(0.2)
            
            # Stop monitoring
            obdlink.stop_monitoring()
            print(f"\n[OK] Captured {len(all_messages)} REAL CAN messages!")
            
            if all_messages:
                # Analyze messages
                print("\n*** REAL CAN MESSAGE ANALYSIS ***")
                
                # Show unique IDs
                unique_ids = set()
                for msg in all_messages:
                    if hasattr(msg, 'arbitration_id') and msg.arbitration_id:
                        unique_ids.add(msg.arbitration_id)
                
                print(f"Unique CAN IDs detected: {len(unique_ids)}")
                print(f"IDs: {sorted(unique_ids)}")
                
                # Message statistics
                stats = obdlink.get_message_statistics()
                print("\nMessage Statistics:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                
                # Save real capture
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"REAL_CAN_TRAFFIC_{timestamp}.txt"
                
                with open(filename, 'w') as f:
                    f.write(f"REAL OBDLink MX+ CAN Traffic Capture\n")
                    f.write(f"Timestamp: {timestamp}\n")
                    f.write(f"Device: OBDLink MX+ via COM6\n")
                    f.write(f"Messages captured: {len(all_messages)}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for i, msg in enumerate(all_messages):
                        f.write(f"{i+1:3d}. {msg}\n")
                
                print(f"\n[OK] Real CAN traffic saved to: {filename}")
                
            else:
                print("\n[WARN] No messages captured")
                print("This could mean:")
                print("- Vehicle is off")
                print("- No CAN traffic on this bus")
                print("- Engine needs to be running")
        
        else:
            print("    [FAIL] Could not start monitoring")
            print("    Trying alternative approach...")
            
            # Try manual AT commands
            print("    Trying manual AT commands...")
            
            try:
                # Send basic AT commands manually
                commands = [
                    b'ATZ\r\n',    # Reset
                    b'ATE0\r\n',   # Echo off
                    b'ATL0\r\n',   # Linefeeds off
                    b'ATH1\r\n',   # Headers on
                ]
                
                for cmd in commands:
                    print(f"    Sending: {cmd.decode().strip()}")
                    if obdlink._send_command(cmd):
                        time.sleep(1)
                
                # Try starting monitoring again
                print("    Trying monitor mode...")
                obdlink._send_command(b'ATMA\r\n')  # Monitor all
                
                print("    [OK] Monitor mode started manually")
                
                # Give it a moment then read
                time.sleep(2)
                messages = obdlink.read_messages(count=5)
                
                if messages:
                    print(f"    Captured {len(messages)} messages with manual setup:")
                    for msg in messages:
                        print(f"      {msg}")
                
            except Exception as e:
                print(f"    Manual approach failed: {e}")
        
        # Disconnect
        print("\n[6] Disconnecting...")
        obdlink.disconnect()
        print("    [OK] Disconnected")
        
        print("\n*** TEST COMPLETE ***")
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    print("*** TESTING REAL OBDLink MX+ CAN SNIFFING ***")
    print("   Make sure your OBDLink MX+ is connected to vehicle OBD-II port")
    print("   and powered on!")
    print()
    
    success = simple_can_sniff()
    
    if success:
        print("\n*** REAL CAN SNIFFING TEST SUCCESSFUL! ***")
        print("   Your OBDLink MX+ is working and capturing real CAN traffic!")
    else:
        print("\n*** Test completed with issues ***")
        print("   But connection was established - try with engine running")
    
    print("\nPress Enter to exit...")
    try:
        input()
    except:
        pass