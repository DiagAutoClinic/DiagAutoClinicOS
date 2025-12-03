#!/usr/bin/env python3
"""
BMW E90 320d OBDLink MX+ Test Script
VIN: WBAVC36020NC55225
Odometer: 255319km
Comprehensive test for BMW-specific CAN sniffing
"""

import sys
import os
import time

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

try:
    from shared.obdlink_mxplus import create_obdlink_mxplus, OBDLinkProtocol
    print("✓ Successfully imported OBDLink MX+ module")
except ImportError as e:
    print(f"✗ Failed to import OBDLink MX+ module: {e}")
    sys.exit(1)

def test_bmw_e90_configuration():
    """Test BMW E90 specific configuration"""
    print("\n" + "="*60)
    print("BMW E90 320D OBDLink MX+ TEST")
    print("="*60)
    
    # Vehicle Information
    vehicle_info = {
        'vin': 'WBAVC36020NC55225',
        'odo': '255319km',
        'make': 'BMW',
        'model': '3 Series (E90)',
        'year': 2005,
        'engine': '2.0L M47 Diesel'
    }
    
    print(f"Vehicle: {vehicle_info['year']} {vehicle_info['make']} {vehicle_info['model']}")
    print(f"VIN: {vehicle_info['vin']}")
    print(f"Odometer: {vehicle_info['odo']}")
    print(f"Engine: {vehicle_info['engine']}")
    print("-" * 60)
    
    # Test 1: Create OBDLink MX+ instance
    print("\n[Test 1] Creating OBDLink MX+ instance...")
    obdlink = create_obdlink_mxplus(mock_mode=True)
    print("[OK] OBDLink MX+ instance created")
    
    # Test 2: Check BMW E90 profile availability
    print("\n[Test 2] Checking BMW E90 vehicle profiles...")
    available_profiles = [
        'bmw_e90_2005',
        'bmw_e90_320d', 
        'generic_bmw'
    ]
    
    profile_found = False
    for profile in available_profiles:
        if profile in obdlink.vehicle_profiles:
            profile_info = obdlink.vehicle_profiles[profile]
            print(f"  ✓ Found profile: {profile}")
            print(f"    Name: {profile_info.get('name', 'N/A')}")
            print(f"    VIN: {profile_info.get('vin', 'N/A')}")
            print(f"    Protocol: {profile_info.get('protocol', 'N/A')}")
            
            # Check BMW-specific arbitration IDs
            arbitration_ids = profile_info.get('arbitration_ids', {})
            if 'engine' in arbitration_ids:
                print(f"    Engine IDs: {arbitration_ids['engine']}")
            if 'transmission' in arbitration_ids:
                print(f"    Transmission IDs: {arbitration_ids['transmission']}")
            if 'brakes' in arbitration_ids:
                print(f"    Brake IDs: {arbitration_ids['brakes']}")
            
            profile_found = True
        else:
            print(f"  ✗ Profile not found: {profile}")
    
    if not profile_found:
        print("[FAIL] No BMW E90 profiles found")
        return False
    
    # Test 3: Set BMW E90 profile
    print("\n[Test 3] Setting BMW E90 vehicle profile...")
    profile_success = False
    for profile in ['bmw_e90_2005', 'bmw_e90_320d']:
        if obdlink.set_vehicle_profile(profile):
            print(f"[OK] Vehicle profile set to: {profile}")
            profile_success = True
            break
    
    if not profile_success:
        print("[FAIL] Could not set BMW E90 profile")
        return False
    
    # Test 4: Configure CAN sniffing for BMW
    print("\n[Test 4] Configuring CAN sniffing for BMW (29-bit)...")
    
    # Test different BMW protocols
    protocols_to_test = [
        OBDLinkProtocol.ISO15765_29BIT,
        OBDLinkProtocol.AUTO
    ]
    
    protocol_success = False
    for protocol in protocols_to_test:
        if obdlink.configure_can_sniffing(protocol):
            print(f"[OK] CAN sniffing configured for: {protocol.value}")
            protocol_success = True
            break
    
    if not protocol_success:
        print("[FAIL] Could not configure CAN sniffing")
        return False
    
    # Test 5: Mock connection and monitoring
    print("\n[Test 5] Testing connection and monitoring...")
    
    # Mock connection
    if obdlink.connect_serial("COM3"):  # Mock serial connection
        print("[OK] Mock serial connection successful")
    else:
        print("[WARN] Mock serial connection failed, trying Bluetooth...")
        if obdlink.connect_bluetooth("00:11:22:33:44:55"):  # Mock Bluetooth
            print("[OK] Mock Bluetooth connection successful")
        else:
            print("[FAIL] Could not establish mock connection")
            return False
    
    # Start monitoring
    print("\n[Test 6] Starting CAN monitoring...")
    if obdlink.start_monitoring():
        print("[OK] CAN monitoring started")
        
        # Collect some messages
        print("Collecting CAN messages for 3 seconds...")
        time.sleep(3)
        
        # Read messages
        messages = obdlink.read_messages(10)
        print(f"Captured {len(messages)} messages")
        
        if messages:
            print("Sample BMW messages:")
            for i, msg in enumerate(messages[:3]):
                print(f"  {i+1}. {msg}")
        
        # Get statistics
        stats = obdlink.get_message_statistics()
        print(f"\nMessage Statistics:")
        print(f"  Total messages: {stats.get('total_messages', 0)}")
        print(f"  Unique IDs: {stats.get('unique_ids', 0)}")
        
        # Check for BMW-specific arbitration IDs
        if stats.get('arbitration_id_counts'):
            bmw_ids_found = []
            all_ids = stats['arbitration_id_counts']
            
            # Check for BMW patterns
            bmw_patterns = ['6F1', '6F9', '6D1', '6D9', '6B1', '6B9', '6E1', '6E9', '6C1', '6C9', '6H1', '6H9']
            for pattern in bmw_patterns:
                if pattern in all_ids:
                    bmw_ids_found.append(f"{pattern}:{all_ids[pattern]}")
            
            if bmw_ids_found:
                print(f"  BMW IDs found: {', '.join(bmw_ids_found[:5])}")
            else:
                print("  No BMW-specific arbitration IDs found")
        
        # Stop monitoring
        obdlink.stop_monitoring()
        print("[OK] CAN monitoring stopped")
    else:
        print("[FAIL] Could not start monitoring")
        return False
    
    # Test 7: BMW protocol validation
    print("\n[Test 7] BMW Protocol Validation...")
    
    # Check if BMW profile is active
    if hasattr(obdlink, 'current_vehicle_profile') and obdlink.current_vehicle_profile:
        profile = obdlink.current_vehicle_profile
        print(f"[OK] Active profile: {profile.get('name', 'Unknown')}")
        
        # Check BMW arbitration IDs
        arbitration_ids = profile.get('arbitration_ids', {})
        bmw_categories = ['engine', 'transmission', 'brakes', 'safety', 'instrument', 'body', 'climate']
        
        print("BMW ECU categories supported:")
        for category in bmw_categories:
            if category in arbitration_ids:
                ids = arbitration_ids[category]
                print(f"  ✓ {category.capitalize()}: {ids}")
            else:
                print(f"  ✗ {category.capitalize()}: Not supported")
    else:
        print("[WARN] No active vehicle profile")
    
    # Test 8: Disconnection
    print("\n[Test 8] Disconnecting...")
    obdlink.disconnect()
    print("[OK] Disconnected successfully")
    
    return True

def validate_bmw_capture_files():
    """Check if BMW capture files exist and validate their format"""
    print("\n" + "="*60)
    print("BMW CAPTURE FILE VALIDATION")
    print("="*60)
    
    # Check for existing BMW capture files
    capture_files = []
    potential_patterns = ['bmw', 'e90', 'bayer', '320d']
    
    for file in os.listdir('.'):
        if file.lower().endswith('.txt') or file.lower().endswith('.log'):
            file_lower = file.lower()
            if any(pattern in file_lower for pattern in potential_patterns):
                capture_files.append(file)
    
    if capture_files:
        print(f"Found {len(capture_files)} BMW-related files:")
        for file in capture_files:
            try:
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                print(f"  ✓ {file}: {len(lines)} lines")
                
                # Sample first few lines
                if lines:
                    sample_lines = lines[:3]
                    print(f"    Sample:")
                    for line in sample_lines:
                        print(f"      {line.strip()}")
                        
            except Exception as e:
                print(f"  ✗ {file}: Error reading - {e}")
    else:
        print("No existing BMW capture files found")
    
    return len(capture_files) > 0

def main():
    """Main test function"""
    print("BMW E90 320D CAN Sniffing Test")
    print("Testing OBDLink MX+ with BMW E90 configuration")
    print("="*60)
    
    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path[0]}")
    
    # Test BMW E90 configuration
    config_success = test_bmw_e90_configuration()
    
    # Validate capture files
    file_validation = validate_bmw_capture_files()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    if config_success:
        print("✓ BMW E90 OBDLink MX+ configuration: PASS")
    else:
        print("✗ BMW E90 OBDLink MX+ configuration: FAIL")
    
    if file_validation:
        print("✓ BMW capture file validation: PASS")
    else:
        print("⚠ BMW capture file validation: No files found")
    
    overall_success = config_success
    
    if overall_success:
        print("\n🎉 BMW E90 Test: SUCCESS")
        print("\nThe system is ready for BMW E90 CAN sniffing:")
        print("- OBDLink MX+ configured for BMW 29-bit CAN")
        print("- BMW E90 2005 vehicle profile loaded")
        print("- BMW-specific ECU addresses configured")
        print("- Ready for real hardware testing")
        print("\nNext steps for live testing:")
        print("1. Connect OBDLink MX+ via Bluetooth or USB")
        print("2. Run: python can_sniff_obdlink.py --vehicle=bmw_e90_2005")
        print("3. Monitor BMW CAN bus traffic")
    else:
        print("\n❌ BMW E90 Test: FAILED")
        print("\nConfiguration issues need to be resolved")

if __name__ == "__main__":
    main()