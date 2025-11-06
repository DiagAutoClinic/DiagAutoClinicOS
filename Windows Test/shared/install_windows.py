#!/usr/bin/env python3
"""
Windows-specific installation script for DiagAutoClinicOS
"""

import subprocess
import sys
import os
import platform
import ctypes
import shutil
from pathlib import Path

def is_admin():
    """Check if running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_powershell_command(command):
    """Run PowerShell command and return result"""
    try:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"PowerShell error: {e}")
        return None

def check_windows_version():
    """Verify Windows version compatibility"""
    win_version = platform.version()
    print(f"Windows Version: {win_version}")
    
    # Check for Windows 10 or newer
    if int(platform.version().split('.')[0]) < 10:
        print("Warning: Windows 10 or newer recommended for best compatibility")
    
    return True

def install_windows_specific_deps():
    """Install Windows-specific dependencies"""
    windows_specific = [
        "pywin32==306",  # Windows API access
        "comtypes==1.1.14",  # COM support
        "wmi==1.5.1",  # Windows Management Instrumentation
    ]
    
    print("Installing Windows-specific dependencies...")
    for package in windows_specific:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")

def setup_can_backends():
    """Configure CAN backends for Windows"""
    print("Setting up CAN backends for Windows...")
    
    can_backends = [
        "python-can[vector]",
        "python-can[ixxat]",
        "python-can[neovi]",
        "python-can[pcan]",
    ]
    
    for backend in can_backends:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", backend])
            print(f"✓ Installed {backend}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {backend} (may not be available)")

def check_services():
    """Check required Windows services"""
    required_services = [
        "SCardSvr",  # Smart Card Service
        "BluetoothUserService",  # Bluetooth Support
        "DevQueryBroker",  # Device Query
    ]
    
    print("Checking required Windows services...")
    for service in required_services:
        result = run_powershell_command(f"Get-Service -Name '{service}' -ErrorAction SilentlyContinue")
        if result:
            print(f"✓ Service running: {service}")
        else:
            print(f"⚠ Service not found: {service}")

def install_drivers():
    """Provide driver installation guidance"""
    print("\n=== Driver Installation Guide ===")
    print("1. CAN Interfaces:")
    print("   - Vector: Download from vector.com")
    print("   - PEAK-System: Download from peak-system.com")
    print("   - Kvaser: Download from kvaser.com")
    
    print("\n2. J2534 Pass-Thru:")
    print("   - Install manufacturer-specific J2534 drivers")
    print("   - Ensure DLL files are in system PATH")
    
    print("\n3. USB Serial Drivers:")
    print("   - FTDI: ftdichip.com/drivers")
    print("   - Prolific: prolific.com.tw")
    print("   - CP210x: silabs.com/developers/usb-to-uart-bridge-vcp-drivers")

def setup_environment():
    """Set up Windows environment variables"""
    print("Setting up environment...")
    
    # Add current directory to PATH for DLL loading
    current_dir = os.getcwd()
    path_env = os.environ.get('PATH', '')
    if current_dir not in path_env:
        os.environ['PATH'] = current_dir + ';' + path_env
    
    # Create Windows-specific config directory
    appdata_dir = Path(os.environ.get('APPDATA', '')) / 'DiagAutoClinicOS'
    appdata_dir.mkdir(exist_ok=True)
    
    print(f"✓ Configuration directory: {appdata_dir}")

def install_requirements():
    """Install all requirements with Windows compatibility"""
    print("Installing core requirements...")
    
    requirements_files = [
        "requirements.txt",
        "AutoDiag/requirements.txt", 
        "AutoECU/requirements.txt",
        "AutoKey/requirements.txt"
    ]
    
    for req_file in requirements_files:
        if os.path.exists(req_file):
            print(f"Installing from {req_file}...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "-r", req_file
                ])
                print(f"✓ Successfully installed {req_file}")
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to install {req_file}: {e}")

def main():
    print("DiagAutoClinicOS - Windows Installation")
    print("=" * 50)
    
    if platform.system() != "Windows":
        print("This script is for Windows systems only.")
        sys.exit(1)
    
    # Check admin privileges
    if not is_admin():
        print("Warning: Not running as administrator. Some features may require admin rights.")
        print("Recommended: Run as Administrator for full hardware access.")
    
    # System checks
    check_windows_version()
    check_services()
    
    # Installation
    setup_environment()
    install_requirements()
    install_windows_specific_deps()
    setup_can_backends()
    
    # Driver guidance
    install_drivers()
    
    print("\n" + "=" * 50)
    print("Installation completed!")
    print("Run 'python test_windows_compatibility.py' to verify installation.")
    print("Note: Some hardware features may require additional driver installation.")

if __name__ == "__main__":
    main()
