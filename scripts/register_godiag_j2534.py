import winreg
import os
import sys

# Full path to your GODIAG_PT32.dll (update if your project moves)
DLL_PATH = r"C:\Users\DACOS\Documents\DACOS\DACOS\DiagAutoClinicOS-main\DiagAutoClinicOS\drivers\GODIAG_J2534_Driver\GODIAG_PT32.dll"

# Registry base for 32-bit J2534 devices on both 32-bit and 64-bit Windows
BASE_KEY = r"SOFTWARE\WOW6432Node\PassThruSupport.04.04"

# Device subkey name (this is what most software looks for)
DEVICE_KEY_NAME = "GODIAG GD101"

# Required registry values for a basic J2534 device entry
REG_VALUES = {
    "Name": "GODIAG GD101 J2534",
    "Vendor": "GODIAG",
    "FunctionLibrary": DLL_PATH,
    "APIVersion": "04.04",
    "CAN": 1,               # Supports CAN
    "ISO15765": 1,          # Supports ISO15765 (most common for diagnostics)
    "ISO9141": 1,
    "ISO14230": 1,
    "J1850PWM": 1,
    "J1850VPW": 1,
}

def register_godiag():
    if not os.path.exists(DLL_PATH):
        print(f"ERROR: DLL not found at:\n{DLL_PATH}")
        print("Please check the path and try again.")
        sys.exit(1)

    try:
        # Open (or create) the PassThruSupport key
        base_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, BASE_KEY)
        
        # Create or open the device subkey
        device_key = winreg.CreateKey(base_key, DEVICE_KEY_NAME)
        
        print(f"Registering GODIAG GD101 at:")
        print(f"   HKLM\\{BASE_KEY}\\{DEVICE_KEY_NAME}\n")
        
        for name, value in REG_VALUES.items():
            winreg.SetValueEx(device_key, name, 0, winreg.REG_SZ if isinstance(value, str) else winreg.REG_DWORD, value)
            print(f"   {name} = {value}")
        
        winreg.CloseKey(device_key)
        winreg.CloseKey(base_key)
        
        print("\nSUCCESS: GODIAG GD101 has been registered successfully!")
        print("You can now use it in DiagAutoClinicOS or other J2534 software.")
        print("Restart any running diagnostic apps for changes to take effect.")
        
    except PermissionError:
        print("ERROR: Permission denied. You MUST run this script as Administrator.")
        print("Right-click Command Prompt or PowerShell -> 'Run as administrator'")
    except Exception as e:
        print(f"ERROR: Failed to write registry: {e}")

if __name__ == "__main__":
    print("GODIAG GD101 J2534 Registry Registration Tool")
    print("=" * 50)
    register_godiag()