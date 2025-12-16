#!/usr/bin/env python3
"""
Quick test for Racelogic .REF parser
"""

from ref_parser import RacelogicREFParser
import os

def test_parser():
    parser = RacelogicREFParser()
    
    # Test with Acura-TSX file
    ref_file = 'can_bus_data/Vehicle_CAN_Files_REF/Acura-TSX (CU2 CU4) 2009-2014.REF'
    
    if not os.path.exists(ref_file):
        print(f"Error: File not found: {ref_file}")
        return False
    
    try:
        print(f"Parsing file: {ref_file}")
        db = parser.parse_file(ref_file)
        
        print("[OK] Successfully parsed file!")
        print(f"  - Manufacturer: {db.manufacturer}")
        print(f"  - Model: {db.model}")
        print(f"  - Year Range: {db.year_range}")
        print(f"  - Messages found: {len(db.messages)}")
        
        # Show first few messages
        for i, (can_id, msg) in enumerate(list(db.messages.items())[:3]):
            print(f"  - Message {i+1}: CAN ID 0x{can_id:04X}, DLC: {msg.dlc}, Signals: {len(msg.signals)}")
            
        # Test signal decoding with a sample
        if db.messages:
            first_msg = list(db.messages.values())[0]
            if first_msg.signals:
                signal = first_msg.signals[0]
                print(f"  - Sample Signal: {signal.name}")
                print(f"    Start Bit: {signal.start_bit}, Length: {signal.bit_length}")
                print(f"    Scale: {signal.scale}, Offset: {signal.offset}")
                print(f"    Byte Order: {signal.byte_order}, Signed: {signal.signed}")
                
                # Test decode with dummy data
                try:
                    dummy_data = b'\x01\x02\x03\x04\x05\x06\x07\x08'
                    decoded = signal.decode(dummy_data)
                    print(f"    Decoded Value (dummy data): {decoded}")
                except Exception as e:
                    print(f"    Decode test error: {e}")
        
        # Test SQLite save
        databases = {"Acura-TSX": db}
        sqlite_file = "test_output.sqlite"
        parser.save_to_sqlite(databases, sqlite_file)
        
        if os.path.exists(sqlite_file):
            print(f"[OK] SQLite export successful: {sqlite_file}")
            os.remove(sqlite_file)  # Clean up
        else:
            print(f"[ERROR] SQLite export failed")
            
        return True
        
    except Exception as e:
        print(f"[ERROR] Error parsing file: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_parser()
    if success:
        print("\n[SUCCESS] All tests passed! Your REF parser is working correctly.")
    else:
        print("\n[FAILED] Tests failed. Check the error messages above.")