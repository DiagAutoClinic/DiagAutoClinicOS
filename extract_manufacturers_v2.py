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
    
    # Known manufacturers to help with parsing
    known_manufacturers = {
        'Acura', 'AiM', 'Alfa Romeo', 'Alsense', 'Aprilia', 'Ariel', 'Aston Martin', 'Audi',
        'BAC', 'BMW', 'Cadillac', 'Caterham', 'Chery', 'Chevrolet', 'Chrysler', 'Citroen',
        'Continental Teves', 'DTAFast', 'Dodge', 'Emerald', 'Emtron', 'Ferrari', 'Fiat', 'Ford',
        'Ginetta', 'Gumpert', 'Haltech', 'Holden', 'Honda', 'Hondata', 'Hyundai', 'Infiniti',
        'Jaguar', 'Jeep', 'KTM', 'Kawasaki', 'Kia', 'Lamborghini', 'Land Rover', 'Lexus',
        'Life Racing', 'Ligier', 'Lincoln', 'Lotus', 'MaxxECU', 'Mazda', 'McLaren', 'Mercedes',
        'Mini', 'Mitsubishi', 'Nissan', 'Noble', 'Norma', 'Peugeot', 'Porsche', 'Racelogic',
        'Radical', 'Ram', 'Renault', 'Rivian', 'Saab', 'Scion', 'Seat', 'Skoda', 'Smart',
        'SsangYong', 'Subaru', 'Suzuki', 'Tesla', 'Toyota', 'Vauxhall', 'Volkswagen', 'Volvo', 'Zenos'
    }
    
    for filename in ref_files:
        # Remove .REF extension
        base_name = filename.replace('.REF', '')
        
        # Try to find the manufacturer by looking for known manufacturers first
        found_manufacturer = None
        model_info = ""
        
        # Check if the filename starts with a known manufacturer
        for manufacturer in known_manufacturers:
            if base_name.startswith(manufacturer + ' - ') or base_name.startswith(manufacturer + '-'):
                found_manufacturer = manufacturer
                # Extract the rest as model info
                if base_name.startswith(manufacturer + ' - '):
                    model_info = base_name[len(manufacturer + ' - '):]
                else:
                    model_info = base_name[len(manufacturer + '-'):]
                break
        
        # If no known manufacturer found, try splitting by first dash
        if not found_manufacturer:
            if ' - ' in base_name:
                parts = base_name.split(' - ', 1)
            else:
                parts = base_name.split('-', 1)
            
            if len(parts) >= 1:
                found_manufacturer = parts[0].strip()
                model_info = parts[1] if len(parts) > 1 else ""
        
        if found_manufacturer:
            manufacturers.add(found_manufacturer)
            manufacturer_details[found_manufacturer].append(model_info)
    
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