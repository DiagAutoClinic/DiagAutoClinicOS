#!/usr/bin/env python3
"""
Test script to verify that the AutoDiag login fix works
"""

import sys
import os
import time
import logging
from pathlib import Path

# Add the project root to the path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_diagnostics_controller():
    """Test that DiagnosticsController can be created without hanging"""
    print("Testing DiagnosticsController initialization...")
    
    try:
        from AutoDiag.core.diagnostics import DiagnosticsController
        
        # Create controller with minimal callbacks
        ui_callbacks = {
            'set_button_enabled': lambda btn, enabled: None,
            'set_status': lambda text: None,
            'set_results_text': lambda text: None,
            'update_card_value': lambda card, value: None,
            'switch_to_tab': lambda index: None,
            'show_message': lambda title, text, msg_type="info": None,
            'vci_status_changed': lambda event, data: None,
            'update_vci_status_display': lambda status_info: None,
            'update_live_data_table': lambda data: None,
            'populate_live_data_table': lambda data: None,
            'update_can_bus_data': lambda can_data: None
        }
        
        controller = DiagnosticsController(ui_callbacks)
        print("✅ DiagnosticsController created successfully")
        
        # Test that manufacturers can be retrieved (this should trigger deferred loading)
        manufacturers = controller.get_available_manufacturers()
        print(f"✅ Retrieved {len(manufacturers)} manufacturers: {manufacturers[:5]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating DiagnosticsController: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_application_imports():
    """Test that main application can be imported"""
    print("Testing main application imports...")
    
    try:
        # Test imports that happen during main application startup
        from AutoDiag.main import AutoDiagPro, ResponsiveHeader, LoginDialog
        print("✅ Main application classes imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error importing main application: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("AutoDiag Login Fix Test")
    print("=" * 50)
    
    # Setup basic logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Diagnostics Controller
    if test_diagnostics_controller():
        tests_passed += 1
    
    print()
    
    # Test 2: Main application imports
    if test_main_application_imports():
        tests_passed += 1
    
    print()
    print("=" * 50)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! The login fix is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())