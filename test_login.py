#!/usr/bin/env python3
"""
Test script to demonstrate AutoDiag login working
"""

import sys
import os

# Add AutoDiag to path
autodiag_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'AutoDiag'))
if autodiag_path not in sys.path:
    sys.path.insert(0, autodiag_path)

print("Testing AutoDiag login...")
print("This will use console login since PyQt6 is not available")

try:
    # Import and test the login
    from AutoDiag.main import AutoDiagPro

    # This should trigger the console login
    app = AutoDiagPro()
    print("Login successful! AutoDiag is now accessible.")
except ImportError as e:
    print(f"Import failed (likely missing PyQt6): {e}")
    print("AutoDiagPro requires PyQt6 to be installed.")
except SystemExit as e:
    if e.code == 1:
        print("Login failed or was cancelled.")
    else:
        print("Application exited normally.")
except Exception as e:
    print(f"Error: {e}")