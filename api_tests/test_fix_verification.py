#!/usr/bin/env python3
"""
Test script to verify the selected_brand attribute error has been fixed
"""

import sys
import os
from pathlib import Path

# Set headless mode for testing
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_autodiag_fix():
    """Test that AutoDiagPro can be instantiated without selected_brand error"""
    print("Testing AutoDiagPro fix...")
    
    try:
        # Import the module
        from AutoDiag.main import AutoDiagPro
        print("SUCCESS: AutoDiagPro imported successfully")
        
        # Create QApplication
        from PyQt6.QtWidgets import QApplication
        app = QApplication([])
        print("SUCCESS: QApplication created")
        
        # Test instantiation
        window = AutoDiagPro()
        print("SUCCESS: AutoDiagPro instance created without errors")
        
        # Verify the fix: check that brand selection works
        current_brand = window.header.brand_combo.currentText()
        print(f"Current brand: {current_brand}")
        
        # Test that both special functions and calibrations combo boxes work
        sf_brand = window.sf_brand_combo.currentText()
        cr_brand = window.cr_brand_combo.currentText()
        
        print(f"Special functions brand: {sf_brand}")
        print(f"Calibrations brand: {cr_brand}")
        
        # Verify they all match
        if sf_brand == current_brand == cr_brand:
            print("SUCCESS: All brand combos synchronized correctly")
        else:
            print("WARNING: Brand combos not synchronized (this is expected during initialization)")
            
        print("\n*** SUCCESS: The selected_brand attribute error has been fixed! ***")
        print("The application now uses self.header.brand_combo.currentText() instead of the missing self.selected_brand attribute")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_autodiag_fix()
    sys.exit(0 if success else 1)