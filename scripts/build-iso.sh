#!/bin/bash
# build-iso.sh: Builds DiagAutoClinicOS ISO using Cubic
# Usage: ./build-iso.sh (run on Ubuntu 24.04 host)
# Output: DiagAutoClinicOS-v0.1-alpha.iso in current dir

set -e  # Exit on error

UBUNTU_VERSION="24.04"
ISO_URL="https://releases.ubuntu.com/${UBUNTU_VERSION}/ubuntu-${UBUNTU_VERSION}-desktop-amd64.iso"
ISO_FILE="ubuntu-${UBUNTU_VERSION}-desktop-amd64.iso"
WORK_DIR="$HOME/diagauto-build"
CHROOT_DIR="${WORK_DIR}/chroot"

# Download base ISO
if [ ! -f "$ISO_FILE" ]; then
    wget "$ISO_URL" -O "$ISO_FILE"
fi

# Launch Cubic (manual: Load ISO, then run chroot commands below)
echo "Launch Cubic GUI: Create project in $WORK_DIR, load $ISO_FILE."
echo "In Cubic's chroot terminal, paste these commands:"

cat << 'EOF'
# Inside Cubic chroot:

# Update
apt update && apt upgrade -y

# Core tools
apt install -y git build-essential rustc cargo python3-pip libusb-1.0-0-dev xfce4

# Clone/build OpenJ2534
git clone https://github.com/jakka351/OpenJ2534.git
cd OpenJ2534 && make && make install && cd ..

# Clone/build OpenVehicleDiag
git clone https://github.com/jwharrin/openvehiclediag.git
cd openvehiclediag && cargo build --release && cp target/release/ovd /usr/local/bin/ && cd ..

# Install Python libs for AutoKey/AutoDiag
pip3 install python-uds python-obd

# udev rules for J2534 (e.g., Tactrix)
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="cc4c", MODE="0666"' | tee /etc/udev/rules.d/99-j2534.rules

# Desktop shortcuts (e.g., AutoDiag)
mkdir -p /usr/share/applications
cat > /usr/share/applications/autodiag.desktop << DESK
[Desktop Entry]
Name=AutoDiag
Exec=ovd --device j2534
Icon=system-search
Type=Application
Categories=Utility;
DESK

# Clean up
apt autoremove -y && apt clean
EOF

echo "After chroot in Cubic, generate ISO: DiagAutoClinicOS-v0.1-alpha.iso"
echo "Test: qemu-system-x86_64 -cdrom DiagAutoClinicOS-v0.1-alpha.iso -m 2G"
