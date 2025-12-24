#!/usr/bin/env python3
"""
Test script to verify AutoDiag fixes
Tests basic import and initialization functionality
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(PROJECT_ROOT))

def test_imports():
    """Test that all required imports work correctly"""
    print("[TEST] Testing imports...")
    
    try:
        # Test shared module imports
        from shared.themes.dacos_theme import DACOS_THEME, apply_dacos_theme
        print("[PASS] DACOS theme imports successful")
        
        from shared.circular_gauge import CircularGauge, StatCard
        print("[PASS] Circular gauge imports successful")
        
        from shared.style_manager import style_manager
        print("[PASS] Style manager imports successful")
        
        from shared.user_database_sqlite import user_database
        print("[PASS] User database imports successful")
        
        # Test AutoDiag core imports
        from AutoDiag.core.diagnostics import DiagnosticsController
        print("[PASS] Diagnostics controller imports successful")
        
        # Test AutoDiag UI imports
        from AutoDiag.ui.diagnostics_tab import DiagnosticsTab
        print("[PASS] Diagnostics tab imports successful")
        
        return True
        
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error during imports: {e}")
        return False

def test_diagnostics_controller():
    """Test DiagnosticsController initialization"""
    print("\n[TEST] Testing DiagnosticsController...")
    
    try:
        from AutoDiag.core.diagnostics import DiagnosticsController
        
        # Test basic initialization
        controller = DiagnosticsController()
        print("[PASS] DiagnosticsController initialized successfully")
        
        # Test some basic methods
        manufacturers = controller.get_available_manufacturers()
        print(f"[PASS] Available manufacturers: {len(manufacturers)} found")
        
        vci_status = controller.get_vci_status()
        print(f"[PASS] VCI status: {vci_status.get('status', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] DiagnosticsController test failed: {e}")
        return False

def test_main_module_syntax():
    """Test that main.py has no syntax errors"""
    print("\n[TEST] Testing main.py syntax...")
    
    try:
        import py_compile
        py_compile.compile('AutoDiag/main.py', doraise=True)
        print("[PASS] main.py syntax is valid")
        return True
    except py_compile.PyCompileError as e:
        print(f"[FAIL] main.py syntax error: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error testing main.py: {e}")
        return False

def test_diagnostics_tab_syntax():
    """Test that diagnostics_tab.py has no syntax errors"""
    print("\n[TEST] Testing diagnostics_tab.py syntax...")
    
    try:
        import py_compile
        py_compile.compile('AutoDiag/ui/diagnostics_tab.py', doraise=True)
        print("[PASS] diagnostics_tab.py syntax is valid")
        return True
    except py_compile.PyCompileError as e:
        print(f"[FAIL] diagnostics_tab.py syntax error: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error testing diagnostics_tab.py: {e}")
        return False

def main():
    """Run all tests"""
    print("[TEST] AutoDiag Fix Verification Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_diagnostics_controller,
        test_main_module_syntax,
        test_diagnostics_tab_syntax
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[FAIL] Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"[RESULT] Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("[SUCCESS] All tests passed! AutoDiag fixes are working correctly.")
        return 0
    else:
        print("[WARNING] Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())