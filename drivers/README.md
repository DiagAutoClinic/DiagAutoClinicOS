# VCI Drivers for AutoDiag Pro Installer

This folder contains VCI (Vehicle Communication Interface) drivers that will be automatically installed with AutoDiag Pro.

## 📦 Included Drivers

### 1. J2534 PassThru Drivers
- **File**: `j2534_setup.exe`
- **Purpose**: Professional-grade diagnostic interface drivers
- **Download**: https://www.drewtech.com/support/j2534/
- **Devices**: Compatible with most professional VCI devices

### 2. ELM327 USB Drivers
- **File**: `elm327_usb_drivers.exe`
- **Purpose**: Basic OBD-II USB interface drivers
- **Download**: https://www.ftdichip.com/Drivers/CDM/CDM21228_Setup.exe
- **Devices**: ELM327 USB adapters, OBDLink, etc.

### 3. ELM327 Bluetooth Drivers
- **File**: `elm327_bt_drivers.exe`
- **Purpose**: Bluetooth OBD-II interface drivers
- **Note**: Usually uses standard Windows Bluetooth drivers
- **Devices**: Bluetooth ELM327 adapters

### 4. CAN Bus Interface Drivers
- **File**: `can_bus_drivers.msi`
- **Purpose**: CAN bus diagnostic interface drivers
- **Devices**: Peak CAN, Kvaser, etc.

## 🔧 Installation Process

During AutoDiag Pro installation:

1. User selects "Install common VCI device drivers"
2. Installer automatically runs:
   - `setup.exe` (if exists)
   - `install.exe` (if exists)
   - `driver.msi` (if exists)
3. Drivers are installed silently
4. User is prompted to restart if needed

## 📝 Adding New Drivers

To add more drivers:

1. Place the installer executable/MSI in this folder
2. Name it with common installer names:
   - `setup.exe`
   - `install.exe`
   - `driver.msi`
   - Or manufacturer-specific names

3. Update this README with driver information

## ⚠️ Important Notes

- Drivers are installed with administrator privileges
- Some drivers may require system restart
- Ensure drivers are compatible with Windows 10/11
- Test driver installation on clean systems
- Include both 32-bit and 64-bit versions if needed

## 🆘 Troubleshooting

If drivers fail to install:
- Check Windows compatibility
- Verify administrator privileges
- Consult device manufacturer documentation
- Check Device Manager for driver status