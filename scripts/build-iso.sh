#!/bin/bash

# DiagAutoClinicOS ISO Builder Script
# This script creates a bootable ISO with DiagAutoClinicOS pre-installed

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
    syslinux \
    isolinux \
    squashfs-tools \
    python3 \
    python3-pip \
    python3-pyqt6 \
    obd \
    git

# Create ISO directory structure
echo -e "${YELLOW}Creating ISO directory structure...${NC}"
rm -rf "${ISO_DIR}"
mkdir -p "${ISO_DIR}"
mkdir -p "${APP_DIR}"
mkdir -p "${DESKTOP_DIR}"
mkdir -p "${ICON_DIR}"
mkdir -p "${ISO_DIR}/boot"
mkdir -p "${ISO_DIR}/live"

# Copy current DiagAutoClinicOS files
echo -e "${YELLOW}Copying application files...${NC}"
cp -r ~/DiagAutoClinicOS/* "${APP_DIR}/"

# Create desktop shortcuts
echo -e "${YELLOW}Creating desktop shortcuts...${NC}"

# AutoDiag shortcut
cat > "${DESKTOP_DIR}/autodiag.desktop" << EOF
[Desktop Entry]
Version=1.0
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
Version=1.0
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
Version=1.0
Name=AutoKey
Comment=Key Programming Tool
Exec=python3 /opt/DiagAutoClinicOS/AutoKey/main.py
Icon=/usr/share/icons/hicolor/256x256/apps/autokey.png
Terminal=false
Type=Application
Categories=Utility;Automotive;
EOF

# Create icons (placeholder icons - you can replace these later)
echo -e "${YELLOW}Creating placeholder icons...${NC}"
# Create simple placeholder icons
convert -size 256x256 xc:blue -pointsize 20 -fill white -gravity center -annotate +0+0 "AD" "${ICON_DIR}/autodiag.png"
convert -size 256x256 xc:green -pointsize 20 -fill white -gravity center -annotate +0+0 "AE" "${ICON_DIR}/autoecu.png"
convert -size 256x256 xc:red -pointsize 20 -fill white -gravity center -annotate +0+0 "AK" "${ICON_DIR}/autokey.png"

# Install ImageMagick if not present for icon creation
if ! command -v convert &> /dev/null; then
    apt-get install -y imagemagick
fi

# Create launcher script
echo -e "${YELLOW}Creating launcher script...${NC}"
cat > "${APP_DIR}/launch_all.sh" << EOF
#!/bin/bash
# Launcher script for DiagAutoClinicOS applications
echo "Starting DiagAutoClinicOS Applications..."
python3 /opt/DiagAutoClinicOS/AutoDiag/main.py &
python3 /opt/DiagAutoClinicOS/AutoECU/main.py &
python3 /opt/DiagAutoClinicOS/AutoKey/main.py &
echo "Applications started!"
EOF

chmod +x "${APP_DIR}/launch_all.sh"

# Create boot files (simplified)
echo -e "${YELLOW}Creating boot files...${NC}"
cat > "${ISO_DIR}/boot/grub.cfg" << EOF
set default=0
set timeout=10

menuentry "DiagAutoClinicOS Live" {
    linux /live/vmlinuz boot=live quiet
    initrd /live/initrd.img
}
EOF

# Create ISO filesystem
echo -e "${YELLOW}Creating ISO filesystem...${NC}"
cd "${ISO_DIR}"

# Create the ISO
genisoimage -o "/tmp/${ISO_NAME}-${ISO_VERSION}.iso" \
    -r -J -no-emul-boot \
    -boot-load-size 4 -boot-info-table \
    -b boot/grub.cfg \
    -V "${ISO_NAME}" \
    .

echo -e "${GREEN}=== ISO Build Complete! ===${NC}"
echo -e "ISO created at: ${YELLOW}/tmp/${ISO_NAME}-${ISO_VERSION}.iso${NC}"
echo -e "Size: $(du -h "/tmp/${ISO_NAME}-${ISO_VERSION}.iso" | cut -f1)"

# Make script executable
chmod +x ~/DiagAutoClinicOS/build_ISO.sh
