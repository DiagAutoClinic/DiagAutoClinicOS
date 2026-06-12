# VCI Drivers Repository

Place your J2534 PassThru driver DLLs and configuration files in this directory.

## Structure
You can place DLLs directly here or in subdirectories named after the device.

Example:
- `drivers/OpenPort/op20pt32.dll`
- `drivers/Mongoose/mongoose_iso.dll`
- `drivers/MyCustomVCI/vci_driver.dll`

## Note for Scanmatik Users
For Scanmatik 2 Pro, you typically need `sm2j2534.dll`.
If you only have the `.sys` and `.inf` files (USB drivers), please install the Scanmatik software or copy `sm2j2534.dll` to this folder.

## Usage
The `shared/j2534_passthru.py` module scans this directory for valid J2534 DLLs.
It also checks the Windows Registry (`HKLM\SOFTWARE\PassThruSupport.04.04`) for installed drivers.
