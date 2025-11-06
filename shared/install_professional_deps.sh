#!/bin/bash

# DiagAutoClinicOS Professional Hardware Support Installer
echo "Installing professional hardware dependencies for DiagAutoClinicOS..."

# Update package list
sudo apt update

# Core Python and serial dependencies
sudo apt install -y python3 python3-pip python3-serial python3-usb

# CAN utilities (SocketCAN)
sudo apt install -y can-utils

# Bluetooth support
sudo apt install -y bluetooth bluez blueman

# J2534 support
sudo apt install -y wine libj2534-dev

# USB permissions
sudo apt install -y udev

# Python packages for professional hardware
pip3 install pyusb pybluez

# Create udev rules for professional devices
echo 'Setting up udev rules for professional diagnostic devices...'
sudo tee /etc/udev/rules.d/99-professional-diag.rules > /dev/null << 'RULES'
# Godiag GT101
SUBSYSTEM=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="0666"

# ELM327 devices
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="0666"
SUBSYSTEM=="tty", ATTRS{idVendor}=="067b", ATTRS{idProduct}=="2303", MODE="0666"
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="0666"

# J2534 devices
SUBSYSTEM=="usb", ATTRS{idVendor}=="0bdc", MODE="0666"  # Mercedes
SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", MODE="0666"  # STMicroelectronics

# Generic diagnostic devices
SUBSYSTEM=="usb", ATTRS{idVendor}=="04d8", MODE="0666"  # Microchip
SUBSYSTEM=="usb", ATTRS{idVendor}=="04b4", MODE="0666"  # Cypress
RULES

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Create J2534 configuration
sudo mkdir -p /etc/j2534
sudo tee /etc/j2534/passthru.conf > /dev/null << 'CONF'
[Godiag GT101]
vendor=0403
product=6001
protocol=J2534

[ELM327]
vendor=0403  
product=6001
protocol=ELM327
CONF

echo "Professional hardware support installation complete!"
echo "Supported devices:"
echo "  - Godiag GT101 J2534"
echo "  - ELM327 (USB/Bluetooth)"
echo "  - Scanmatic 2"
echo "  - Tatrix"
echo "  - Mongoose Pro"
echo "  - PCMmaster"
echo ""
echo "Please reconnect your devices for automatic detection."
