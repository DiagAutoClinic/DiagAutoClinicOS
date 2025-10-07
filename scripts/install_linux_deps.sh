#!/bin/bash

# DiagAutoClinicOS Linux Dependency Installer
echo "Installing dependencies for DiagAutoClinicOS on Linux..."

# Update package list
sudo apt update

# Install Python and serial dependencies
sudo apt install -y python3 python3-pip python3-serial

# Install CAN utilities (SocketCAN)
sudo apt install -y can-utils

# Install Wine for potential J2534 Windows DLL support
sudo apt install -y wine

# Install Python packages
pip3 install pyserial PyQt6

# Create udev rules for ELM327 devices
echo 'Creating udev rules for automotive devices...'
sudo tee /etc/udev/rules.d/99-elm327.rules > /dev/null << EOF
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="0666"
SUBSYSTEM=="tty", ATTRS{idVendor}=="067b", ATTRS{idProduct}=="2303", MODE="0666"
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="0666"
EOF

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

echo "Installation complete! Please reconnect your ELM327 device if connected."