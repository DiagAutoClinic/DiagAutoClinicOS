#!/usr/bin/env python3
"""
Test script to verify CAN database integration
"""

import sys
import os

# Add the AutoDiag directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AutoDiag'))

from core.can_database_sqlite import can_db_manager, get_vehicle_database, list_all_vehicles, get_all_manufacturers

def test_can_database():
    """Test CAN database functionality"""
    print("Testing CAN database integration...")
    
    # Test database connection
    print("\n1. Testing database connection...")
    if can_db_manager.connect():
        print("[OK] Database connection successful")
    else:
        print("[ERROR] Database connection failed")
        return False
    
    # Test getting manufacturers
    print("\n2. Testing manufacturers retrieval...")
    manufacturers = get_all_manufacturers()
    if manufacturers:
        print(f"[OK] Found {len(manufacturers)} manufacturers")
        print(f"   Sample manufacturers: {', '.join(manufacturers[:5])}")
    else:
        print("[ERROR] No manufacturers found")
        return False
    
    # Test getting vehicles
    print("\n3. Testing vehicles retrieval...")
    vehicles = list_all_vehicles()
    if vehicles:
        print(f"[OK] Found {len(vehicles)} vehicles")
        print(f"   Sample vehicles: {', '.join([f'{v[0]} {v[1]}' for v in vehicles[:3]])}")
    else:
        print("[ERROR] No vehicles found")
        return False
    
    # Test getting specific vehicle database
    print("\n4. Testing specific vehicle database...")
    if manufacturers:
        test_manufacturer = manufacturers[0]
        print(f"   Testing with manufacturer: {test_manufacturer}")
        
        # Get models for this manufacturer
        models = can_db_manager.get_models_for_manufacturer(test_manufacturer)
        if models:
            test_model = models[0]
            print(f"   Testing with model: {test_model}")
            
            # Get vehicle database
            vehicle_db = get_vehicle_database(test_manufacturer, test_model)
            if vehicle_db:
                print(f"[OK] Vehicle database loaded: {vehicle_db.manufacturer} {vehicle_db.model}")
                print(f"   Messages: {len(vehicle_db.messages)}")
                
                # Test decoding a sample message
                if vehicle_db.messages:
                    sample_can_id = list(vehicle_db.messages.keys())[0]
                    sample_message = vehicle_db.messages[sample_can_id]
                    print(f"   Sample message: {sample_message.name} (CAN ID: 0x{sample_can_id:03X})")
                    print(f"   Signals: {len(sample_message.signals)}")
                    
                    # Test signal decoding
                    if sample_message.signals:
                        sample_signal = sample_message.signals[0]
                        print(f"   Sample signal: {sample_signal.name} ({sample_signal.unit})")
                        
                        # Create test data and decode
                        test_data = bytes([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08])
                        decoded_value = sample_signal.decode(test_data)
                        print(f"   Decoded value: {decoded_value}")
            else:
                print("[ERROR] Failed to load vehicle database")
                return False
        else:
            print("[ERROR] No models found for manufacturer")
            return False
    else:
        print("[ERROR] No manufacturers available")
        return False
    
    # Test database statistics
    print("\n5. Testing database statistics...")
    stats = can_db_manager.get_signal_statistics()
    if stats:
        print(f"[OK] Database statistics:")
        print(f"   Vehicles: {stats.get('vehicle_count', 0)}")
        print(f"   Messages: {stats.get('message_count', 0)}")
        print(f"   Signals: {stats.get('signal_count', 0)}")
    else:
        print("[ERROR] Failed to get database statistics")
        return False
    
    # Disconnect
    can_db_manager.disconnect()
    print("\n[OK] All CAN database tests passed!")
    return True

if __name__ == "__main__":
    success = test_can_database()
    sys.exit(0 if success else 1)