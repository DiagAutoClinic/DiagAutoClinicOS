#!/usr/bin/env python3
"""
DiagAutoClinicOS - Installation Validator
Checks if all required components and dependencies are present
"""

import sys
import importlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def check_python_version():
    """Verify Python version"""
    print("Checking Python version...")
    if sys.version_info < (3, 10):
        print(f"  ✗ Python {sys.version_info.major}.{sys.version_info.minor} is too old")
        print(f"  ⚠ Requires Python 3.10 or newer")
        return False
    print(f"  ✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_dependencies():
    """Check critical dependencies"""
    print("\nChecking dependencies...")
    
    required = [
        ('PyQt6', 'PyQt6'),
        ('serial', 'pyserial'),
        ('can', 'python-can'),
        ('obd', 'obd'),
        ('requests', 'requests'),
    ]
    
    optional = [
        ('bluetooth', 'pybluez'),
        ('loguru', 'loguru'),
        ('usb', 'pyusb'),
    ]
    
    all_ok = True
    
    for module, package in required:
        try:
            importlib.import_module(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (REQUIRED)")
            all_ok = False
    
    for module, package in optional:
        try:
            importlib.import_module(module)
            print(f"  ✓ {package} (optional)")
        except ImportError:
            print(f"  ⚠ {package} (optional - not installed)")
    
    return all_ok

def check_project_structure():
    """Verify project file structure"""
    print("\nChecking project structure...")
    
    required_files = [
        'launcher.py',
        'requirements.txt',
        'LICENSE',
        'README.md',
        'shared/device_handler.py',
        'shared/style_manager.py',
        'AutoDiag/main.py',
        'AutoECU/main.py',
        'AutoKey/main.py',
    ]
    
    all_ok = True
    
    for file_path in required_files:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (MISSING)")
            all_ok = False
    
    return all_ok

def main():
    """Run all validation checks"""
    print("=" * 70)
    print("DiagAutoClinicOS Installation Validator")
    print("=" * 70)
    
    results = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Project Structure': check_project_structure(),
    }
    
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {check}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✓ All checks passed! Installation is valid.")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        print("\nTo fix dependency issues, run:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())