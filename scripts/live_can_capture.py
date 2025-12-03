#!/usr/bin/env python3
"""
LIVE OBDLink MX+ CAN Sniffer
Captures real CAN messages from your OBDLink MX+ device
"""

import time
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def live_can_capture():
    """Live CAN message capture with real OBDLink MX+"""
    print("LIVE OBDLink MX+ CAN CAPTURE")
    print("=" * 40)
    print("*** CONNECTING TO YOUR REAL OBDLink MX+ ***")
    print()
    
    try:
        from shared.obdlink_mxplus import create_obdlink_mxplus
        
        # Create real OBDLink MX+ instance
        obdlink = create_obdlink_mxplus(mock_mode=False)
        
        # Connect to the working COM6 port
        print("[1] Connecting to OBDLink MX+ via COM6...")
        success = obdlink.connect_serial("COM6", baudrate=38400)
        
        if not success:
            print("    [ERROR] Could not connect to COM6")
            return False
        
        print("    [OK] Connected to COM6!")
        print(f"    Connection status: {obdlink.is_connected}")
        
        # Set vehicle profile
        print("\n[2] Configuring for Chevrolet Cruze 2014...")
        obdlink.set_vehicle_profile("chevrolet_cruze_2014")
        
        # Manual AT command sequence for reliable connection
        print("\n[3] Sending AT commands to prepare device...")
        commands = [
            (b'ATZ\r\n', "Reset device"),
            (b'ATE0\r\n', "Disable echo"),
            (b'ATL0\r\n', "Linefeeds off"), 
            (b'ATH1\r\n', "Headers on"),
            (b'ATSP6\r\n', "ISO15765-11BIT CAN protocol"),
            (b'ATCAF0\r\n', "CAN auto formatting off"),
        ]
        
        for cmd, desc in commands:
            print(f"    {desc}...")
            obdlink._send_command(cmd)
            time.sleep(0.5)
        
        print("\n[4] Starting CAN monitoring mode...")
        
        # Start monitoring
        obdlink._send_command(b'ATMA\r\n')  # Monitor all
        time.sleep(1)
        
        print("    [OK] Monitor mode activated!")
        print("\n" + "="*50)
        print("*** CAPTURING REAL CAN TRAFFIC ***")
        print("="*50)
        print("Waiting for CAN messages...")
        print("(Make sure vehicle engine is RUNNING for traffic)")
        print()
        
        # Capture messages for 60 seconds
        start_time = time.time()
        all_messages = []
        message_count = 0
        
        try:
            while time.time() - start_time < 60:
                # Read available messages
                messages = obdlink.read_messages(count=20, timeout_ms=500)
                
                if messages:
                    for msg in messages:
                        message_count += 1
                        all_messages.append(msg)
                        
                        # Display real-time
                        print(f"[{message_count:3d}] {msg}")
                
                # Progress indicator
                elapsed = int(time.time() - start_time)
                if elapsed % 10 == 0 and elapsed > 0:
                    print(f"\n--- {elapsed}s elapsed, {len(all_messages)} messages captured ---")
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n[INTERRUPTED] Stopping capture...")
        
        # Stop monitoring
        print("\n[5] Stopping CAN monitoring...")
        obdlink._send_command(b'\r\n')  # Stop command
        time.sleep(1)
        
        # Disconnect
        print("[6] Disconnecting...")
        obdlink.disconnect()
        
        # Report results
        print("\n" + "="*50)
        print("*** CAPTURE COMPLETE ***")
        print("="*50)
        
        if all_messages:
            print(f"SUCCESS! Captured {len(all_messages)} REAL CAN messages!")
            
            # Analyze messages
            print(f"\nMessage Analysis:")
            
            # Count by arbitration ID
            id_counts = {}
            for msg in all_messages:
                if hasattr(msg, 'arbitration_id') and msg.arbitration_id:
                    id_counts[msg.arbitration_id] = id_counts.get(msg.arbitration_id, 0) + 1
            
            print(f"Unique CAN IDs: {len(id_counts)}")
            print(f"Most active IDs:")
            for msg_id, count in sorted(id_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {msg_id}: {count} messages")
            
            # Save to file
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"LIVE_CAN_CAPTURE_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write(f"LIVE OBDLink MX+ CAN Traffic Capture\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Vehicle: Chevrolet Cruze 2014\n")
                f.write(f"Total messages: {len(all_messages)}\n")
                f.write(f"Duration: {int(time.time() - start_time)} seconds\n")
                f.write("=" * 50 + "\n\n")
                
                for i, msg in enumerate(all_messages):
                    f.write(f"{i+1:4d}. {msg}\n")
            
            print(f"\nSaved to: {filename}")
            
            # Show sample of different message types
            print(f"\nSample CAN Messages:")
            sample_ids = list(id_counts.keys())[:5]
            for msg_id in sample_ids:
                sample_msg = next((m for m in all_messages if hasattr(m, 'arbitration_id') and m.arbitration_id == msg_id), None)
                if sample_msg:
                    print(f"  {msg_id}: {sample_msg}")
            
        else:
            print("No messages captured.")
            print("Possible reasons:")
            print("- Vehicle engine not running")
            print("- Vehicle not transmitting CAN traffic")
            print("- Wrong protocol or configuration")
            print("- OBDLink MX+ needs to be reset")
        
        print(f"\nCapture session ended.")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("STARTING LIVE CAN SNIFFING WITH YOUR OBDLink MX+")
    print("=" * 55)
    print("Make sure:")
    print("1. OBDLink MX+ is plugged into vehicle OBD-II port")
    print("2. Vehicle engine is RUNNING")
    print("3. Vehicle is Chevrolet Cruze 2014 (or similar)")
    print()
    
    success = live_can_capture()
    
    if success:
        print("\n*** LIVE CAN CAPTURE COMPLETED ***")
        print("Check the output file for your real CAN traffic!")
    else:
        print("\n*** CAPTURE FAILED ***")
        print("Check connections and try again.")
    
    print("\nPress Enter to exit...")
    try:
        input()
    except:
        pass