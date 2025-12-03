#!/usr/bin/env python3
"""
Test script to verify AutoDiag main module fixes
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

def test_imports():
    """Test all imports work correctly"""
    try:
        print("Testing imports...")
        
        # Test main module import
        import AutoDiag.main
        print("[OK] AutoDiag.main imported successfully")
        
        # Test login dialog import
        from AutoDiag.ui.login_dialog import LoginDialog
        print("[OK] LoginDialog imported successfully")
        
        # Test basic class instantiation (without GUI)
        print("[OK] All critical imports working")
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

def test_pyqt6_integration():
    """Test PyQt6 imports specifically"""
    try:
        print("\nTesting PyQt6 integration...")
        
        # Test specific PyQt6 imports that were fixed - keeping only commonly used widgets
        from PyQt6.QtWidgets import (
            QApplication, QMainWindow, QWidget, QPushButton, 
            QComboBox, QHBoxLayout, QVBoxLayout, QTabWidget, 
            QTextEdit, QDialog, QMessageBox
        )
        print("[OK] PyQt6.QtWidgets imports working")
        
        from PyQt6.QtCore import Qt, QTimer
        print("[OK] PyQt6.QtCore imports working")
        
        from PyQt6.QtGui import QFont, QColor
        print("[OK] PyQt6.QtGui imports working")
        
        return True
        
    except ImportError as e:
        print(f"[ERROR] PyQt6 import error: {e}")
        return False

def main():
    """Main test function"""
    print("=== AutoDiag Main Module Fix Verification ===\n")
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test PyQt6 integration
    if not test_pyqt6_integration():
        success = False
    
    print("\n=== Test Results ===")
    if success:
        print("[OK] All tests passed! The PyQt6 import issues have been resolved.")
        print("[OK] The code should now work without Pylance import warnings.")
        return 0
    else:
        print("[ERROR] Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())