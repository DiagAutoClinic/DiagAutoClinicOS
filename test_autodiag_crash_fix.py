#!/usr/bin/env python3
"""
Test script to isolate AutoDiag crash issue
"""

import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_imports():
    """Test importing all the modules that main.py imports"""
    print("Testing imports...")

    try:
        # Test shared modules
        print("Testing shared modules...")
        from shared.themes.dacos_theme import DACOS_THEME, apply_dacos_theme
        print("[OK] dacos_theme imported")

        from shared.circular_gauge import CircularGauge, StatCard
        print("[OK] circular_gauge imported")

        from shared.style_manager import style_manager
        print("[OK] style_manager imported")

        from shared.special_functions import special_functions_manager
        print("[OK] special_functions imported")

        from shared.calibrations_reset import calibrations_resets_manager
        print("[OK] calibrations_reset imported")

        from shared.live_data import live_data_generator, start_live_stream, stop_live_stream, get_live_data
        print("[OK] live_data imported")

        from shared.advance import get_advanced_functions, simulate_function_execution, get_mock_advanced_data
        print("[OK] advance imported")

        from shared.user_database import user_database
        print("[OK] user_database imported")

        # Test AutoDiag modules
        print("Testing AutoDiag modules...")
        from AutoDiag.ui.login_dialog import LoginDialog
        print("[OK] login_dialog imported")

        from AutoDiag.core.diagnostics import DiagnosticsController
        print("[OK] diagnostics imported")

        from AutoDiag.core.can_bus_ref_parser import can_bus_ref_parser
        print("[OK] can_bus_ref_parser imported")

        from AutoDiag.core.vci_manager import vci_manager
        print("[OK] vci_manager imported")

        print("All imports successful!")
        return True

    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_qt_app():
    """Test Qt application creation"""
    print("Testing Qt application...")

    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt

        app = QApplication(sys.argv)
        app.setApplicationName("Test AutoDiag")
        print("[OK] QApplication created")

        # Test theme application
        from shared.themes.dacos_theme import apply_dacos_theme
        success = apply_dacos_theme(app)
        if success:
            print("[OK] DACOS theme applied")
        else:
            print("[WARN] DACOS theme application failed")

        # Test login dialog creation
        from AutoDiag.ui.login_dialog import LoginDialog
        login_dialog = LoginDialog()
        print("[OK] LoginDialog created")

        # Test login dialog execution (this might be where the crash happens)
        print("Testing login dialog execution...")
        # For testing, we'll simulate login by setting user_info directly
        # since we can't interact with the dialog in a headless environment
        login_dialog.user_info = {'username': 'test', 'full_name': 'Test User', 'tier': 'BASIC', 'permissions': []}
        print("[OK] Login dialog user_info set (simulated)")

        # Note: We can't actually call login_dialog.exec() in a headless test
        # as it would require user interaction and a display

        # Test main window creation
        from AutoDiag.main import AutoDiagPro
        user_info = login_dialog.user_info
        main_window = AutoDiagPro(user_info)
        print("[OK] AutoDiagPro main window created")

        # Test showing the window
        main_window.show()
        print("[OK] Main window shown")

        # Test starting the event loop briefly (this might cause the crash)
        print("Testing Qt event loop...")
        # Use a timer to quit after a short time
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, app.quit)  # Quit after 100ms
        exit_code = app.exec()
        print(f"[OK] Qt event loop completed with exit code: {exit_code}")

        print("[OK] All Qt components created and event loop tested successfully")
        return True

    except Exception as e:
        print(f"[FAIL] Qt application test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("AutoDiag Crash Fix Test")
    print("=" * 50)

    # Test imports first
    if not test_imports():
        print("Import test failed - exiting")
        sys.exit(1)

    print()

    # Test Qt application
    if not test_qt_app():
        print("Qt application test failed - exiting")
        sys.exit(1)

    print()
    print("[SUCCESS] All tests passed! The issue might be elsewhere.")