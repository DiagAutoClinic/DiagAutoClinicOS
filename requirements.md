1. AutoDiag Requirements
AutoDiag/requirements.txt
txt
# AutoDiag - Automotive Diagnostic System
PyQt6==6.6.1
PyQt6-Qt6==6.6.2
PyQt6-sip==13.6.0
obd==0.7.1
pyserial==3.5
python-can==4.2.2
pandas==2.1.4
numpy==1.25.2
matplotlib==3.8.2
pyqtgraph==0.13.3
psutil==5.9.6
requests==2.31.0
python-dateutil==2.8.2
pycrc==0.9.2
pytest==7.4.3
2. AutoECU Requirements
AutoECU/requirements.txt
txt
# AutoECU - ECU Programming System
PyQt6==6.6.1
PyQt6-Qt6==6.6.2
PyQt6-sip==13.6.0
pyserial==3.5
python-can==4.2.2
cryptography==41.0.8
pycryptodome==3.19.0
intelhex==2.3.0
bitstring==4.1.2
pandas==2.1.4
numpy==1.25.2
psutil==5.9.6
requests==2.31.0
pyelftools==0.29
construct==2.10.68
pytest==7.4.3
3. AutoKey Requirements
AutoKey/requirements.txt
txt
# AutoKey - Key Programming System
PyQt6==6.6.1
PyQt6-Qt6==6.6.2
PyQt6-sip==13.6.0
pyserial==3.5
python-can==4.2.2
cryptography==41.0.8
pycryptodome==3.19.0
rfid==0.2.0
pyscard==2.0.7
pandas==2.1.4
numpy==1.25.2
psutil==5.9.6
requests==2.31.0
qrcode==7.4.2
Pillow==10.1.0
pytest==7.4.3
4. Shared Requirements (for ISO build)
requirements.txt (Root level - for complete suite)
txt
# DiagAutoClinicOS - Complete Automotive Diagnostic Suite
# Core GUI Framework
PyQt6==6.6.1
PyQt6-Qt6==6.6.2
PyQt6-sip==13.6.0
PyQt6-Charts==6.6.0

# Hardware Communication
pyserial==3.5
python-can==4.2.2
python-vxi11==0.9
pyusb==1.2.1
bleak==0.21.1

# Automotive Protocols
obd==0.7.1
can-isotp==1.7
j2534==0.3.0
udsoncan==1.17

# Cryptography & Security
cryptography==41.0.8
pycryptodome==3.19.0
rsa==4.9

# Data Processing & Analysis
pandas==2.1.4
numpy==1.25.2
scipy==1.11.4
matplotlib==3.8.2
pyqtgraph==0.13.3
seaborn==0.13.0

# File Formats & Data
intelhex==2.3.0
bitstring==4.1.2
pyelftools==0.29
construct==2.10.68
openpyxl==3.1.2
python-docx==1.1.0

# System & Utilities
psutil==5.9.6
requests==2.31.0
python-dateutil==2.8.2
pytz==2023.3
tzlocal==5.2

# RFID & Smart Card
pyscard==2.0.7
rfid==0.2.0

# QR Code Generation
qrcode==7.4.2
Pillow==10.1.0

# Development & Testing
pytest==7.4.3
pytest-qt==4.2.0
pytest-cov==4.1.0
black==23.11.0
flake8==6.1.0
mypy==1.7.1

# Logging & Monitoring
loguru==0.7.2
sentry-sdk==1.35.0

# Networking
zeroconf==0.131.0
websockets==12.0

# Optional Dependencies
opencv-python==4.8.1.78
pyzbar==0.1.9
5. Development Requirements
requirements-dev.txt (For contributors)
txt
# Development dependencies for DiagAutoClinicOS
-r requirements.txt

# Testing
pytest==7.4.3
pytest-qt==4.2.0
pytest-cov==4.1.0
pytest-mock==3.12.0
pytest-timeout==2.1.0

# Code Quality
black==23.11.0
flake8==6.1.0
mypy==1.7.1
isort==5.13.2
pre-commit==3.5.0

# Documentation
sphinx==7.2.6
sphinx-rtd-theme==2.0.0
sphinx-autoapi==3.0.0

# Packaging
setuptools==68.2.2
wheel==0.41.3
twine==4.0.2
pyinstaller==5.13.2

# Debugging
ipdb==0.13.13
debugpy==1.8.0

# Build Tools
cmake==3.27.7
ninja==1.11.1.1
6. Minimal Requirements (Lightweight)
requirements-minimal.txt (For systems with limited resources)
txt
# Minimal dependencies for DiagAutoClinicOS
PyQt6==6.6.1
pyserial==3.5
python-can==4.2.2
obd==0.7.1
pandas==2.1.4
numpy==1.25.2
cryptography==41.0.8
psutil==5.9.6
requests==2.31.0
Installation Script
install_dependencies.py
python
#!/usr/bin/env python3
"""
Dependency installer for DiagAutoClinicOS
"""

import subprocess
import sys
import os

def install_requirements(requirements_file):
    """Install requirements from specified file"""
    if os.path.exists(requirements_file):
        print(f"Installing dependencies from {requirements_file}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
    else:
        print(f"Requirements file not found: {requirements_file}")

def main():
    print("DiagAutoClinicOS Dependency Installer")
    print("=" * 40)
    
    # Install core dependencies
    if os.path.exists("requirements.txt"):
        install_requirements("requirements.txt")
    
    # Install application-specific dependencies
    apps = ["AutoDiag", "AutoECU", "AutoKey"]
    for app in apps:
        req_file = os.path.join(app, "requirements.txt")
        if os.path.exists(req_file):
            print(f"\nInstalling {app} dependencies...")
            install_requirements(req_file)
    
    print("\nAll dependencies installed successfully!")

if __name__ == "__main__":
    main()
Usage Instructions
For End Users (ISO):
bash
# The ISO includes all dependencies pre-installed
# No additional installation required
For Developers:
bash
# Clone the repository
git clone https://github.com/DiagAutoClinic/DiagAutoClinicOS.git
cd DiagAutoClinicOS

# Install all dependencies
pip install -r requirements.txt

# Or install specific application dependencies
pip install -r AutoDiag/requirements.txt
For Minimal Installation:
bash
# Install only essential dependencies
pip install -r requirements-minimal.txt
These requirements files ensure that all three applications have the necessary dependencies while avoiding conflicts and maintaining compatibility across different systems.

