#!/bin/bash

# Add this at the beginning of your build-iso.sh
echo "╔══════════════════════════════════════════════════╗"
echo "║           Building DiagAutoClinicOS 2025         ║"
echo "║      Created by Flame with DeepSeek AI           ║"
echo "║          October 2024 - Continued 2025           ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""


# DiagAutoClinicOS ISO Builder Script
# This script creates an ISO with DiagAutoClinicOS pre-installed

set -e  # Exit on any error

# Configuration
ISO_NAME="DiagAutoClinicOS"
ISO_VERSION="1.0"
ISO_DIR="/tmp/${ISO_NAME}_build"
APP_DIR="${ISO_DIR}/opt/DiagAutoClinicOS"
DESKTOP_DIR="${ISO_DIR}/usr/share/applications"
ICON_DIR="${ISO_DIR}/usr/share/icons/hicolor/256x256/apps"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== DiagAutoClinicOS ISO Builder ===${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root: sudo ./build_ISO.sh${NC}"
    exit 1
fi

# Install required packages
echo -e "${YELLOW}Installing required packages...${NC}"
apt-get update
apt-get install -y \
    genisoimage \
    python3 \
    python3-pip \
    git \
    imagemagick

# Install Python dependencies
echo "Creating Python virtual environment..."
python3 -m venv /tmp/build-venv
source /tmp/build-venv/bin/activate

echo "Installing Python dependencies in virtual environment..."
echo -e "${YELLOW}Installing Python dependencies...${NC}"
echo "Installing Python dependencies in virtual environment..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "WARNING: requirements.txt not found, installing default dependencies..."
    pip install PyQt6==6.6.0 pygame==2.5.2 requests==2.31.0 pyserial==3.5 obd==0.7.1 python-dotenv==1.0.0 Pillow==10.0.0
fi
pip install -r requirements.txt
pip3 install PyQt6 obd

# Create ISO directory structure
echo -e "${YELLOW}Creating ISO directory structure...${NC}"
rm -rf "${ISO_DIR}"
mkdir -p "${ISO_DIR}"
mkdir -p "${APP_DIR}"
mkdir -p "${DESKTOP_DIR}"
mkdir -p "${ICON_DIR}"

# Copy current DiagAutoClinicOS files
echo -e "${YELLOW}Copying application files...${NC}"
cp -r "/home/flame/DiagAutoClinicOS/"* "${APP_DIR}/"

# Remove any __pycache__ directories
find "${APP_DIR}" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Create desktop shortcuts
echo -e "${YELLOW}Creating desktop shortcuts...${NC}"

# AutoDiag shortcut
cat > "${DESKTOP_DIR}/autodiag.desktop" << EOF
[Desktop Entry]
Version=1.1
Name=AutoDiag
Comment=Vehicle Diagnostic Tool
Exec=python3 /opt/DiagAutoClinicOS/AutoDiag/main.py
Icon=/usr/share/icons/hicolor/256x256/apps/autodiag.png
Terminal=false
Type=Application
Categories=Utility;Automotive;
EOF

# AutoECU shortcut
cat > "${DESKTOP_DIR}/autoecu.desktop" << EOF
[Desktop Entry]
Version=1.1
Name=AutoECU
Comment=ECU Programming Tool
Exec=python3 /opt/DiagAutoClinicOS/AutoECU/main.py
Icon=/usr/share/icons/hicolor/256x256/apps/autoecu.png
Terminal=false
Type=Application
Categories=Utility;Automotive;
EOF

# AutoKey shortcut
cat > "${DESKTOP_DIR}/autokey.desktop" << EOF
[Desktop Entry]
Version=1.1
Name=AutoKey
Comment=Key Programming Tool
Exec=python3 /opt/DiagAutoClinicOS/AutoKey/main.py
Icon=/usr/share/icons/hicolor/256x256/apps/autokey.png
Terminal=false
Type=Application
Categories=Utility;Automotive;
EOF

# Create placeholder icons
echo -e "${YELLOW}Creating placeholder icons...${NC}"
# Create simple colored icons with text
convert -size 256x256 xc:blue -pointsize 40 -fill white -gravity center -annotate +0+0 "AD" "${ICON_DIR}/autodiag.png"
convert -size 256x256 xc:green -pointsize 40 -fill white -gravity center -annotate +0+0 "AE" "${ICON_DIR}/autoecu.png"
convert -size 256x256 xc:red -pointsize 40 -fill white -gravity center -annotate +0+0 "AK" "${ICON_DIR}/autokey.png"

# Create launcher script
echo -e "${YELLOW}Creating launcher script...${NC}"
cat > "${APP_DIR}/launch_all.sh" << EOF
#!/bin/bash
# Launcher script for DiagAutoClinicOS applications
echo "Starting DiagAutoClinicOS Applications..."
cd /opt/DiagAutoClinicOS
python3 AutoDiag/main.py &
python3 AutoECU/main.py &
python3 AutoKey/main.py &
echo "Applications started!"
EOF

chmod +x "${APP_DIR}/launch_all.sh"

# Create ISO filesystem
echo -e "${YELLOW}Creating ISO filesystem...${NC}"
cd "${ISO_DIR}"

# Create the ISO (simplified - no boot files)
genisoimage -o "/tmp/${ISO_NAME}-${ISO_VERSION}.iso" \
    -r -J \
    -V "${ISO_NAME}" \
    .

echo -e "${GREEN}=== ISO Build Complete! ===${NC}"
echo -e "ISO created at: ${YELLOW}/tmp/${ISO_NAME}-${ISO_VERSION}.iso${NC}"
echo -e "Size: $(du -h "/tmp/${ISO_NAME}-${ISO_VERSION}.iso" | cut -f1)"
