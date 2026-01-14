#!/usr/bin/env python3
"""
Extract manufacturer list from DACOS CAN bus data files.
This script parses the REF file names to extract unique manufacturer names.
"""

import os
import re
from collections import defaultdict

def extract_manufacturers():
    """Extract unique manufacturer names from REF file names."""
    
    # Path to the REF files directory
    ref_dir = "can_bus_data/Vehicle_CAN_Files_REF"
    
    if not os.path.exists(ref_dir):
        print(f"Error: Directory {ref_dir} not found")
        return []
    
    # Get all REF files
    ref_files = [f for f in os.listdir(ref_dir) if f.endswith('.REF')]
    
    manufacturers = set()
    manufacturer_details = defaultdict(list)
    
    for filename in ref_files:
        # Remove .REF extension
        base_name = filename.replace('.REF', '')
        
        # Split by first dash to separate manufacturer from model
        if ' - ' in base_name:
            # Handle cases like "Chrysler-300 (2005-2010)" vs "Chrysler-300 (2005-2010)"
            parts = base_name.split(' - ', 1)
        else:
            parts = base_name.split('-', 1)
        
        if len(parts) >= 1:
            manufacturer = parts[0].strip()
            model_info = parts[1] if len(parts) > 1 else ""
            
            # Filter out entries that look like they're not actual manufacturers
            # (e.g., entries that contain model years or other non-manufacturer info)
            if not re.match(r'^\d{4}-\d{4}$', manufacturer) and not re.match(r'^\d{4}-$', manufacturer):
                manufacturers.add(manufacturer)
                manufacturer_details[manufacturer].append(model_info)
    
    return sorted(list(manufacturers)), manufacturer_details

def main():
    """Main function to extract and display manufacturer data."""
    
    print("=== DACOS Manufacturer List ===\n")
    
    manufacturers, details = extract_manufacturers()
    
    print(f"Total unique manufacturers found: {len(manufacturers)}\n")
    
    print("=== Manufacturer List ===")
    for i, manufacturer in enumerate(manufacturers, 1):
        print(f"{i:3d}. {manufacturer}")
    
    print(f"\n=== Detailed Breakdown ===")
    for manufacturer in sorted(manufacturers):
        model_count = len(details[manufacturer])
        print(f"\n{manufacturer} ({model_count} models):")
        for model in sorted(details[manufacturer]):
            if model:  # Only show non-empty model info
                print(f"  - {model}")

if __name__ == "__main__":
    main()