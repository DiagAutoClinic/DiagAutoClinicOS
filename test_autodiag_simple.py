#!/usr/bin/env python3
"""
Simple AutoDiag Functionality Test
Tests core functionality without unicode issues
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_imports():
    """Test all imports work correctly"""
    print("Testing imports...")
    
    try:
        # Core PyQt6 imports
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        print("  [OK] PyQt6 imports successful")
        
        # Shared modules
        from shared.theme_constants import THEME
        from shared.style_manager import style_manager
        from shared.brand_database import get_brand_list, get_brand_info
        from shared.dtc_database import DTCDatabase
        from shared.vin_decoder import VINDecoder
        from shared.security_manager import security_manager, SecurityLevel
        from shared.circular_gauge import CircularGauge, StatCard
        from shared.calibrations_reset import calibrations_resets_manager
        from shared.special_functions import special_functions_manager
        print("  [OK] All shared modules imported successfully")
        
        # UI modules
        from ui.login_dialog import LoginDialog
        print("  [OK] UI modules imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"  [ERROR] Import failed: {e}")
        return False

def test_theme_system():
    """Test theme and styling system"""
    print("\nTesting theme system...")
    
    try:
        from shared.theme_constants import THEME
        from shared.style_manager import style_manager
        
        # Test theme values
        assert "bg_main" in THEME
        assert "accent" in THEME
        assert THEME["accent"] == "#21F5C1"
        print("  [OK] Theme constants loaded correctly")
        
        # Test style manager
        themes = style_manager.get_theme_names()
        assert "dacos_unified" in themes
        print("  [OK] Style manager functional")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Theme system error: {e}")
        return False

def test_database_systems():
    """Test all database components"""
    print("\nTesting database systems...")
    
    try:
        # Brand database
        from shared.brand_database import get_brand_list, get_brand_info
        brands = get_brand_list()
        assert len(brands) > 20  # Should have 25+ brands
        print(f"  [OK] Brand database: {len(brands)} brands loaded")
        
        # Test specific brand
        toyota_info = get_brand_info("Toyota")
        assert "region" in toyota_info
        assert toyota_info["region"] == "Japan"
        print("  [OK] Brand info retrieval working")
        
        # DTC database
        from shared.dtc_database import DTCDatabase
        dtc_db = DTCDatabase()
        p0300_info = dtc_db.get_dtc_info("P0300")
        assert "description" in p0300_info
        print("  [OK] DTC database functional")
        
        # VIN decoder
        from shared.vin_decoder import VINDecoder
        vin_decoder = VINDecoder()
        vin_result = vin_decoder.decode("1HGCM82633A004352")
        assert vin_result["brand"] == "Honda"
        print("  [OK] VIN decoder working")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Database system error: {e}")
        return False

def test_security_system():
    """Test security and authentication"""
    print("\nTesting security system...")
    
    try:
        from shared.security_manager import security_manager, SecurityLevel
        
        # Test authentication
        success, message = security_manager.authenticate_user("admin", "admin123")
        assert success == True
        print("  [OK] Admin authentication successful")
        
        # Test user info
        user_info = security_manager.get_user_info()
        assert user_info["full_name"] == "Administrator"
        print("  [OK] User info retrieval working")
        
        # Test security levels
        level = security_manager.get_security_level()
        assert level == SecurityLevel.ADMIN
        print("  [OK] Security level system working")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Security system error: {e}")
        return False

def test_calibration_system():
    """Test calibration and reset procedures"""
    print("\nTesting calibration system...")
    
    try:
        from shared.calibrations_reset import calibrations_resets_manager
        
        # Test procedures availability
        toyota_procedures = calibrations_resets_manager.get_brand_procedures("Toyota")
        assert len(toyota_procedures) > 0
        print(f"  [OK] Toyota procedures: {len(toyota_procedures)} available")
        
        # Test specific procedure
        procedure = calibrations_resets_manager.get_procedure("Toyota", "toyota_steering_cal")
        assert procedure is not None
        assert "Steering Angle" in procedure.name
        print("  [OK] Procedure retrieval working")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] Calibration system error: {e}")
        return False

def test_gui_components():
    """Test GUI components (without displaying them)"""
    print("\nTesting GUI components...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from shared.circular_gauge import CircularGauge, StatCard
        
        # Create minimal QApplication for testing
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Test circular gauge creation
        gauge = CircularGauge(75, 100, "Test Gauge", "%")
        assert gauge is not None
        print("  [OK] CircularGauge creation successful")
        
        # Test stat card creation
        stat_card = StatCard("Health", "95%", 100, "%")
        assert stat_card is not None
        print("  [OK] StatCard creation successful")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] GUI component error: {e}")
        return False

def main():
    """Run all validation tests"""
    print("AutoDiag Functionality Validation Test")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Theme System", test_theme_system),
        ("Database Systems", test_database_systems),
        ("Security System", test_security_system),
        ("Calibration System", test_calibration_system),
        ("GUI Components", test_gui_components),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"[FAIL] {test_name} failed")
        except Exception as e:
            print(f"[CRASH] {test_name} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("[SUCCESS] ALL TESTS PASSED - AutoDiag is fully functional!")
        print("\nThe system is ready for use.")
    else:
        print(f"[FAIL] {total - passed} tests failed - there may be issues")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)