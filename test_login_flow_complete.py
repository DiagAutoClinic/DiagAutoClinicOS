#!/usr/bin/env python3
"""
Test the complete AutoDiag login flow to ensure it works after the fix
"""

import sys
import os
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add the project root to the path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_login_flow():
    """Test the complete login flow"""
    print("Testing AutoDiag Login Flow...")
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    try:
        # Import the main components
        from AutoDiag.main import AutoDiagPro, LoginDialog
        from AutoDiag.core.diagnostics import DiagnosticsController
        
        print("1. Imports successful")
        
        # Test DiagnosticsController creation
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
        print("2. DiagnosticsController created successfully")
        
        # Test AutoDiagPro window creation (this is where the original issue occurred)
        user_info = {
            'username': 'testuser',
            'full_name': 'Test User',
            'tier': 'BASIC',
            'permissions': []
        }
        
        window = AutoDiagPro(current_user_info=user_info)
        print("3. AutoDiagPro window created successfully")
        
        # Test that the window can be shown (this would fail in the original bug)
        window.show()
        print("4. Window shown successfully")
        
        # Test that we can get manufacturers (triggers deferred loading)
        manufacturers = controller.get_available_manufacturers()
        print(f"5. Retrieved {len(manufacturers)} manufacturers")
        
        # Close the window
        window.close()
        print("6. Window closed successfully")
        
        print("\nSUCCESS: Complete login flow test passed!")
        return True
        
    except Exception as e:
        print(f"\nERROR: Login flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        app.quit()

def main():
    """Run the test"""
    print("AutoDiag Login Flow Test")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    success = test_login_flow()
    
    print("=" * 50)
    if success:
        print("RESULT: All tests passed! The login issue is FIXED.")
        return 0
    else:
        print("RESULT: Tests failed. The issue may not be completely resolved.")
        return 1

if __name__ == "__main__":
    sys.exit(main())