#!/usr/bin/env python3
"""
Diagnostic Launcher - Debug AutoDiag Pro Startup Issues
This will help identify why main.py freezes during launch
"""

import sys
import subprocess
import os
from pathlib import Path
import time
import threading

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent
AUTODIAG_DIR = PROJECT_ROOT / "AutoDiag"
MAIN_PY = AUTODIAG_DIR / "main.py"

print("=" * 60)
print("AutoDiag Pro Startup Diagnostic Tool")
print("=" * 60)

# Step 1: Check file existence
print("\n[1/5] Checking file structure...")
print(f"Project root: {PROJECT_ROOT}")
print(f"AutoDiag directory exists: {AUTODIAG_DIR.exists()}")
print(f"main.py exists: {MAIN_PY.exists()}")

if not MAIN_PY.exists():
    print("❌ ERROR: main.py not found!")
    sys.exit(1)

# Step 2: Check Python path
print("\n[2/5] Checking Python environment...")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

# Step 3: Test import of critical modules
print("\n[3/5] Testing critical imports...")
test_imports = [
    "PyQt6",
    "PyQt6.QtWidgets",
    "PyQt6.QtCore",
    "shared.themes.dacos_theme",
    "shared.user_database_sqlite",
]

for module in test_imports:
    try:
        __import__(module)
        print(f"✅ {module}")
    except ImportError as e:
        print(f"❌ {module}: {e}")

# Step 4: Launch with full diagnostics
print("\n[4/5] Launching main.py with full diagnostics...")
print("This will show ALL output including errors...\n")

env = os.environ.copy()
env["PYTHONPATH"] = str(PROJECT_ROOT)
env["QT_QPA_PLATFORM"] = "windows"
env["PYTHONUNBUFFERED"] = "1"  # Force unbuffered output

# Launch with real-time output capture
process = subprocess.Popen(
    [sys.executable, str(MAIN_PY)],
    cwd=str(AUTODIAG_DIR),
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,  # Line buffered
    universal_newlines=True
)

print(f"Process started (PID: {process.pid})")
print("-" * 60)

# Real-time output monitoring
def read_stream(stream, prefix):
    """Read and print stream in real-time"""
    try:
        for line in iter(stream.readline, ''):
            if line:
                print(f"{prefix}: {line.rstrip()}")
    except Exception as e:
        print(f"{prefix} ERROR: {e}")

# Start output readers
stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, "STDOUT"), daemon=True)
stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, "STDERR"), daemon=True)

stdout_thread.start()
stderr_thread.start()

# Monitor process with timeout
print("\n[5/5] Monitoring process (60 second timeout)...")
start_time = time.time()
timeout = 60

while True:
    return_code = process.poll()
    elapsed = time.time() - start_time
    
    if return_code is not None:
        print(f"\nProcess exited with code: {return_code}")
        break
    
    if elapsed > timeout:
        print(f"\n⚠️ TIMEOUT: Process did not exit after {timeout} seconds")
        print("This suggests the process is hanging during initialization")
        
        # Try to get more info
        print("\nAttempting to terminate process...")
        process.terminate()
        try:
            process.wait(timeout=5)
            print("Process terminated successfully")
        except subprocess.TimeoutExpired:
            print("Process did not respond to termination, killing...")
            process.kill()
        
        break
    
    # Show progress
    if int(elapsed) % 5 == 0 and elapsed > 0:
        print(f"Still running... ({int(elapsed)}s elapsed)")
    
    time.sleep(1)

# Wait for output threads to finish
stdout_thread.join(timeout=2)
stderr_thread.join(timeout=2)

print("\n" + "=" * 60)
print("Diagnostic Complete")
print("=" * 60)

print("\n📋 Summary:")
print("If you see the process hanging:")
print("1. Check STDERR output above for Python exceptions")
print("2. Look for Qt/PyQt6 errors")
print("3. Check if login dialog is trying to show but failing")
print("4. Verify all theme files are present")
print("\nIf you see errors about:")
print("- 'No module named': Missing dependencies")
print("- Qt errors: PyQt6 installation issues")
print("- Theme errors: Missing shared/themes files")
print("- Database errors: Missing user database file")