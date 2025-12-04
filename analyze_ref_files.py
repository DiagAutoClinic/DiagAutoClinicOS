#!/usr/bin/env python3
"""
Analyze .REF file format to understand the structure
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

def analyze_ref_files():
    """Analyze the structure of .REF files"""
    print("Analyzing .REF file structure...")
    print("=" * 60)
    
    can_data_dir = PROJECT_ROOT / "can_bus_data"
    ref_files = list(can_data_dir.glob("*.REF"))
    
    for ref_file in ref_files[:3]:  # Analyze first 3 files
        print(f"\nAnalyzing: {ref_file.name}")
        print("-" * 40)
        
        try:
            with open(ref_file, 'rb') as f:
                # Read first 500 bytes
                data = f.read(500)
                
                print(f"File size: {os.path.getsize(ref_file)} bytes")
                print(f"First 100 bytes (hex):")
                print(data[:100].hex())
                
                # Look for text patterns
                print(f"\nFirst 200 bytes (ascii interpretation):")
                ascii_data = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data[:200])
                print(ascii_data)
                
                # Look for specific patterns that might indicate format
                print(f"\nSearching for patterns...")
                
                # Check for common patterns
                if b'CAN' in data or b'ID' in data:
                    print("  - Contains CAN/ID references")
                
                # Check for numeric patterns
                for i in range(0, min(200, len(data) - 4), 4):
                    value = int.from_bytes(data[i:i+4], 'little', signed=True)
                    if 0x100 <= value <= 0x7FF:  # Typical CAN ID range
                        print(f"  - Possible CAN ID: 0x{value:03X} at offset {i}")
                    
                    value2 = int.from_bytes(data[i:i+4], 'big', signed=True)
                    if 0x100 <= value2 <= 0x7FF:
                        print(f"  - Possible CAN ID (big-endian): 0x{value2:03X} at offset {i}")
                
                # Check for zero-terminated strings
                print(f"\nLooking for strings...")
                current_string = ""
                for b in data:
                    if 32 <= b <= 126:  # Printable ASCII
                        current_string += chr(b)
                    elif b == 0 and len(current_string) > 2:
                        if len(current_string) > 3:
                            print(f"  - String: '{current_string}'")
                        current_string = ""
                    else:
                        current_string = ""
                
        except Exception as e:
            print(f"Error analyzing {ref_file.name}: {e}")

def try_binary_parsing():
    """Try different binary parsing approaches"""
    print(f"\n" + "=" * 60)
    print("Trying binary parsing approaches...")
    
    ref_file = PROJECT_ROOT / "can_bus_data" / "Audi-A4 (B8) 2007 - 2015.REF"
    
    try:
        with open(ref_file, 'rb') as f:
            data = f.read()
            
        print(f"Total file size: {len(data)} bytes")
        
        # Try to find structure based on known patterns
        # Many automotive formats use specific header patterns
        
        # Look for repeating patterns
        print("Looking for repeating patterns...")
        for pattern_size in [8, 16, 32]:
            patterns = {}
            for i in range(0, len(data) - pattern_size, 4):
                pattern = data[i:i + pattern_size]
                if pattern in patterns:
                    patterns[pattern] += 1
                else:
                    patterns[pattern] = 1
            
            # Show repeating patterns
            for pattern, count in patterns.items():
                if count > 5:  # Repeats more than 5 times
                    hex_pattern = pattern.hex()
                    print(f"  Pattern {hex_pattern} repeats {count} times")
        
        # Try to interpret as struct-like format
        print(f"\nTrying to interpret as structured data...")
        
        # Check if file size suggests specific structure
        if len(data) % 16 == 0:
            print(f"  - File size divisible by 16 (possible structure)")
        
        # Try common automotive data patterns
        print(f"Analyzing for automotive patterns...")
        
        # Look for voltage/temperature patterns (common automotive values)
        for i in range(0, len(data) - 2, 2):
            value = int.from_bytes(data[i:i+2], 'little')
            if 800 <= value <= 2000:  # Possible temperature in 0.1°C
                print(f"  - Possible temperature: {value/10:.1f}°C at offset {i}")
            
            value2 = int.from_bytes(data[i:i+2], 'big')
            if 800 <= value2 <= 2000:
                print(f"  - Possible temperature (big-endian): {value2/10:.1f}°C at offset {i}")
        
    except Exception as e:
        print(f"Error in binary parsing: {e}")

def main():
    """Main analysis function"""
    print("REF File Format Analysis")
    print("=" * 60)
    
    analyze_ref_files()
    try_binary_parsing()
    
    print(f"\n" + "=" * 60)
    print("Analysis complete!")
    print("Based on this analysis, we can determine the proper parsing method.")

if __name__ == "__main__":
    main()