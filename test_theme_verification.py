#!/usr/bin/env python3
"""
Theme Verification Test - Verify dacos_unified theme is working correctly
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

def test_theme_consistency():
    """Test that dacos_unified theme is working across components"""
    
    print("Testing Theme Consistency...")
    
    # Test 1: Import and verify theme constants
    try:
        from shared.theme_constants import THEME
        print("[OK] Theme constants loaded successfully")
        print(f"   - Theme name: {THEME.get('name')}")
        print(f"   - Primary colors: {THEME.get('accent')}, {THEME.get('glow')}")
    except Exception as e:
        print(f"[FAIL] Failed to load theme constants: {e}")
        return False
    
    # Test 2: Verify style manager
    try:
        from shared.style_manager import style_manager
        print("[OK] Style manager loaded successfully")
        print(f"   - Available themes: {style_manager.get_theme_names()}")
        print(f"   - Active theme: {style_manager.active_theme}")
    except Exception as e:
        print(f"[FAIL] Failed to load style manager: {e}")
        return False
    
    # Test 3: Verify login dialog can be created with theme
    try:
        from ui.login_dialog import LoginDialog
        app = QApplication([])
        
        # Create login dialog
        login_dialog = LoginDialog()
        print("[OK] Login dialog created successfully with responsive geometry")
        print(f"   - Dialog size: {login_dialog.width()}x{login_dialog.height()}")
        print(f"   - Min size: {login_dialog.minimumWidth()}x{login_dialog.minimumHeight()}")
        
        # Test responsive geometry calculation
        geometry = login_dialog.geometry()
        print(f"   - Responsive geometry: {geometry.width()}x{geometry.height()}")
        
        # Clean up
        login_dialog.close()
        app.quit()
        
    except Exception as e:
        print(f"[FAIL] Failed to test login dialog: {e}")
        return False
    
    # Test 4: Verify configuration
    try:
        from config import DEFAULT_THEME, AVAILABLE_THEMES
        print("[OK] Configuration loaded successfully")
        print(f"   - Default theme: {DEFAULT_THEME}")
        print(f"   - Available themes: {AVAILABLE_THEMES}")
        
        if DEFAULT_THEME != "dacos_unified":
            print(f"[WARN] Warning: Expected 'dacos_unified', got '{DEFAULT_THEME}'")
            return False
            
    except Exception as e:
        print(f"[FAIL] Failed to load configuration: {e}")
        return False
    
    print("\n[SUCCESS] All theme consistency tests passed!")
    return True

def test_neural_background():
    """Test neural background compatibility"""
    try:
        from shared.neural_background import NeuralBackground
        print("[OK] Neural background loaded successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to load neural background: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("DACOS UNIFIED THEME VERIFICATION TEST")
    print("=" * 60)
    
    # Run tests
    theme_test = test_theme_consistency()
    bg_test = test_neural_background()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Theme Consistency: {'[OK] PASS' if theme_test else '[FAIL] FAIL'}")
    print(f"Neural Background: {'[OK] PASS' if bg_test else '[FAIL] FAIL'}")
    
    if theme_test and bg_test:
        print("\n[SUCCESS] ALL TESTS PASSED! Theme changes are working correctly.")
        sys.exit(0)
    else:
        print("\n[FAIL] Some tests failed. Please check the output above.")
        sys.exit(1)