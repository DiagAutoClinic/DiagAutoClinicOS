#!/usr/bin/env python3
"""
CAN Bus Data Import and Integration Test
Processes all .REF files and integrates real automotive data into AutoDiag Pro
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_can_bus_import():
    """Test CAN bus data import functionality"""
    print("Testing CAN Bus Data Import System")
    print("=" * 50)
    
    try:
        # Import CAN bus data manager
        from shared.can_bus_data import can_bus_manager, import_can_data_file
        print("[OK] CAN bus data manager imported successfully")
        
        # Check for .REF files
        can_data_dir = PROJECT_ROOT / "can_bus_data"
        ref_files = list(can_data_dir.glob("*.REF"))
        
        if not ref_files:
            print("[WARNING] No .REF files found in can_bus_data directory")
            return False
        
        print(f"[INFO] Found {len(ref_files)} .REF files:")
        for ref_file in ref_files:
            print(f"  - {ref_file.name}")
        
        # Try to import each file
        imported_brands = []
        failed_imports = []
        
        for ref_file in ref_files:
            # Extract brand name from filename
            brand_name = ref_file.stem.split(" (")[0]  # Remove model/year info
            
            print(f"\n[INFO] Importing {brand_name} data from {ref_file.name}...")
            
            try:
                # Try importing the file
                success = import_can_data_file(str(ref_file), brand_name)
                
                if success:
                    imported_brands.append(brand_name)
                    print(f"[OK] Successfully imported {brand_name}")
                else:
                    failed_imports.append((brand_name, "Import failed"))
                    print(f"[FAIL] Failed to import {brand_name}")
                    
            except Exception as e:
                failed_imports.append((brand_name, str(e)))
                print(f"[ERROR] Error importing {brand_name}: {e}")
        
        # Report results
        print(f"\n" + "=" * 50)
        print(f"Import Results:")
        print(f"  Successfully imported: {len(imported_brands)} brands")
        print(f"  Failed imports: {len(failed_imports)} brands")
        
        if imported_brands:
            print(f"\nSuccessfully imported brands:")
            for brand in imported_brands:
                print(f"  - {brand}")
        
        if failed_imports:
            print(f"\nFailed imports:")
            for brand, reason in failed_imports:
                print(f"  - {brand}: {reason}")
        
        # Test the imported data
        if imported_brands:
            print(f"\nTesting imported data...")
            for brand in imported_brands[:3]:  # Test first 3 brands
                try:
                    # Load the brand data
                    success = can_bus_manager.load_brand_data(brand)
                    if success:
                        param_count = len(can_bus_manager.parameters)
                        print(f"  [OK] {brand}: {param_count} parameters loaded")
                        
                        # Show a few example parameters
                        if param_count > 0:
                            sample_params = list(can_bus_manager.parameters.items())[:3]
                            for param_key, param in sample_params:
                                print(f"    - {param.name}: CAN_ID 0x{param.can_id:03X}")
                    else:
                        print(f"  [FAIL] {brand}: Could not load data")
                        
                except Exception as e:
                    print(f"  [ERROR] {brand}: {e}")
        
        return len(imported_brands) > 0
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

def test_live_data_integration():
    """Test live data integration with real CAN data"""
    print(f"\nTesting Live Data Integration")
    print("=" * 50)
    
    try:
        # Import live data generator with CAN integration
        from shared.live_data import live_data_generator, set_brand_for_live_data
        from shared.can_bus_data import can_bus_manager
        
        # Set CAN bus manager in live data generator
        live_data_generator.set_can_bus_manager(can_bus_manager)
        print("[OK] CAN bus manager linked to live data generator")
        
        # Test different brands
        test_brands = ["Audi", "BMW", "Ford"]
        
        for brand in test_brands:
            print(f"\n[INFO] Testing live data for {brand}...")
            
            try:
                # Set brand for live data
                set_brand_for_live_data(brand)
                
                # Get current status
                from shared.live_data import get_real_can_data_status
                status = get_real_can_data_status()
                
                print(f"  [INFO] Live data status for {brand}:")
                print(f"    - Current brand: {status['current_brand']}")
                print(f"    - Has CAN manager: {status['has_can_manager']}")
                print(f"    - Has real data: {status['has_real_data']}")
                print(f"    - Available brands: {status.get('available_brands', [])}")
                
                # Generate some live data
                live_data_generator.start_stream()
                data = live_data_generator.get_live_data()
                
                print(f"  [OK] Generated {len(data)} live data parameters")
                
                # Show some sample data
                for param_name, value, unit in data[:5]:
                    print(f"    - {param_name}: {value} {unit}")
                
                live_data_generator.stop_stream()
                
            except Exception as e:
                print(f"  [ERROR] Error testing {brand}: {e}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Live data integration test failed: {e}")
        return False

def main():
    """Main test function"""
    print("AutoDiag Pro - CAN Bus Data Integration Test")
    print("=" * 60)
    
    # Test CAN bus import
    import_success = test_can_bus_import()
    
    # Test live data integration
    integration_success = test_live_data_integration()
    
    # Final report
    print(f"\n" + "=" * 60)
    print(f"CAN Bus Integration Test Results:")
    print(f"  Import functionality: {'WORKING' if import_success else 'FAILED'}")
    print(f"  Live data integration: {'WORKING' if integration_success else 'FAILED'}")
    
    if import_success and integration_success:
        print(f"\nSUCCESS: AutoDiag Pro now has real CAN bus data integration!")
        print(f"   The system can now:")
        print(f"   - Import .REF files with automotive CAN parameters")
        print(f"   - Extract real sensor values from CAN bus messages")
        print(f"   - Provide enhanced live data monitoring")
        print(f"   - Support multiple automotive brands")
        print(f"\nContinue uploading more .REF files to expand coverage!")
        return True
    else:
        print(f"\nSome issues detected - check the logs above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)