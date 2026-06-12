#!/usr/bin/env python3
"""
Install all required dependencies
"""

import subprocess
import sys

requirements = [
    "python-can",      # CAN bus interface
    "cantools",        # CAN database tools
    "pyserial",        # Serial communication
    "pytest",          # Testing framework
    "tabulate",        # Pretty tables
    "colorama",        # Colored output
]

print("Installing CAN Bus project dependencies...")
print("="*50)

for package in requirements:
    print(f"Installing {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
    except subprocess.CalledProcessError:
        print(f"⚠️  Failed to install {package}")

print("\n" + "="*50)
print("Installation complete!")
print("\nQuick test commands:")
print("  python analyze_database.py          # Analyze parsed data")
print("  python bmw_can.py                   # Test BMW module")
print("  python quick_test.py                # Test basic parsing")