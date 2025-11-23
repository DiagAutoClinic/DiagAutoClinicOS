#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DiagAutoClinicOS - Python 3.10.11 Compatibility Checker
Verifies that all dependencies are compatible with Python 3.10.11
"""

import sys
import platform
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

def check_python_version():
    """Check if Python version is compatible"""
    print("=" * 60)
    print("PYTHON VERSION CHECK")
    print("=" * 60)
    
    version_info = sys.version_info
    version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    
    print(f"Current Python Version: {version_str}")
    print(f"Full Version Info: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()[0]}")
    
    # Check minimum requirements
    if version_info.major < 3:
        print("\n❌ ERROR: Python 3.x is required")
        return False
    
    if version_info.minor < 8:
        print("\n❌ ERROR: Python 3.8 or higher is required")
        return False
    
    if version_info.minor > 12:
        print("\n⚠️  WARNING: Python 3.13+ may have compatibility issues")
        print("   Recommended: Python 3.10-3.12")
    
    print("\n✅ Python version is compatible")
    return True

def check_installed_packages():
    """Check which required packages are installed"""
    print("\n" + "=" * 60)
    print("INSTALLED PACKAGES CHECK")
    print("=" * 60)
    
    required_packages = {
        'PyQt6': '6.6.1',
        'pyserial': '3.5',
        'python-can': '4.2.2',
        'obd': '0.7.1',
        'psutil': '5.9.6',
        'requests': '2.31.0',
        'pyinstaller': '6.10.0',
        'loguru': '0.7.2'
    }
    
    installed = []
    missing = []
    
    for package, min_version in required_packages.items():
        try:
            if package == 'python-can':
                import can
                pkg = can
                pkg_name = 'python-can'
            elif package == 'PyQt6':
                import PyQt6
                pkg = PyQt6
                pkg_name = 'PyQt6'
            elif package == 'pyserial':
                import serial
                pkg = serial
                pkg_name = 'pyserial'
            elif package == 'obd':
                import obd
                pkg = obd
                pkg_name = 'obd'
            elif package == 'psutil':
                import psutil
                pkg = psutil
                pkg_name = 'psutil'
            elif package == 'requests':
                import requests
                pkg = requests
                pkg_name = 'requests'
            elif package == 'pyinstaller':
                import PyInstaller
                pkg = PyInstaller
                pkg_name = 'pyinstaller'
            elif package == 'loguru':
                import loguru
                pkg = loguru
                pkg_name = 'loguru'
            
            version = getattr(pkg, '__version__', 'unknown')
            installed.append((pkg_name, version))
            print(f"✅ {pkg_name:20s} {version}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package:20s} NOT INSTALLED")
    
    return installed, missing

def check_optional_packages():
    """Check optional packages"""
    print("\n" + "=" * 60)
    print("OPTIONAL PACKAGES CHECK")
    print("=" * 60)
    
    optional = {
        'bluetooth': 'pybluez',
        'pyusb': 'pyusb'
    }
    
    for feature, package in optional.items():
        try:
            if package == 'pybluez':
                import bluetooth
                print(f"✅ Bluetooth support available")
            elif package == 'pyusb':
                import usb
                print(f"✅ USB support available")
        except ImportError:
            print(f"⚠️  {feature} support not available (optional)")

def check_project_structure():
    """Verify project structure"""
    print("\n" + "=" * 60)
    print("PROJECT STRUCTURE CHECK")
    print("=" * 60)
    
    from pathlib import Path
    
    required_dirs = ['AutoDiag', 'AutoECU', 'AutoKey', 'shared', 'core', 'ui']
    required_files = ['launcher.py', 'requirements.txt', 'config.py']
    
    project_root = Path(__file__).parent
    
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/ directory found")
        else:
            print(f"❌ {dir_name}/ directory missing")
    
    for file_name in required_files:
        file_path = project_root / file_name
        if file_path.exists():
            print(f"✅ {file_name} found")
        else:
            print(f"❌ {file_name} missing")

def main():
    """Main compatibility check"""
    print("\n")
    print("=" * 60)
    print(" " * 10 + "DiagAutoClinicOS Compatibility Check")
    print("=" * 60)
    print()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check installed packages
    installed, missing = check_installed_packages()
    
    # Check optional packages
    check_optional_packages()
    
    # Check project structure
    check_project_structure()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if missing:
        print(f"\n⚠️  {len(missing)} required package(s) missing:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\nTo install missing packages, run:")
        print("   pip install -r requirements.txt")
    else:
        print("\n✅ All required packages are installed!")
    
    print(f"\n✅ {len(installed)} package(s) installed successfully")
    print("\n" + "=" * 60)
    print("Compatibility check complete!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
