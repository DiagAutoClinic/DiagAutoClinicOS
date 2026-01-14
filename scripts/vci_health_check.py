import os
import sys
import subprocess
import winreg
import ctypes
import re
from typing import List, Dict

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def list_j2534_devices():
    print("\n--- J2534 Device Registry Scan ---")
    devices = []
    try:
        # Open the J2534 registry key
        key_path = r"Software\PassThruSupport.04.04"
        try:
            hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        except FileNotFoundError:
            print("❌ J2534 Registry Key not found (Software\\PassThruSupport.04.04)")
            return []

        # Iterate through subkeys (devices)
        i = 0
        while True:
            try:
                device_name = winreg.EnumKey(hkey, i)
                device_key = winreg.OpenKey(hkey, device_name)
                
                try:
                    name = winreg.QueryValueEx(device_key, "Name")[0]
                    vendor = winreg.QueryValueEx(device_key, "Vendor")[0]
                    function_lib = winreg.QueryValueEx(device_key, "FunctionLibrary")[0]
                    
                    print(f"✅ Found: {name}")
                    print(f"   Vendor: {vendor}")
                    print(f"   Driver: {function_lib}")
                    
                    if not os.path.exists(function_lib):
                         print(f"   ⚠️ WARNING: Driver file missing at {function_lib}")
                    
                    devices.append({"name": name, "lib": function_lib})
                except FileNotFoundError:
                    pass
                finally:
                    winreg.CloseKey(device_key)
                i += 1
            except OSError:
                break
        winreg.CloseKey(hkey)
        
    except Exception as e:
        print(f"❌ Error scanning registry: {e}")
        
    if not devices:
        print("❌ No J2534 devices found in registry.")
    
    return devices

def check_zombie_processes():
    print("\n--- Checking for Zombie Bridge Processes ---")
    
    # Use wmic to get command line arguments of python processes
    try:
        # wmic process where "name='python.exe'" get processid,commandline
        cmd = 'wmic process where "name=\'python.exe\'" get processid,commandline'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        lines = result.stdout.strip().split('\n')
        zombies = []
        current_pid = str(os.getpid())
        
        for line in lines:
            if "j2534_bridge.py" in line:
                # Parse PID (last token)
                parts = line.strip().split()
                if not parts: continue
                
                pid = parts[-1]
                if pid == current_pid:
                    continue
                    
                cmd_line = " ".join(parts[:-1])
                print(f"⚠️ FOUND ZOMBIE BRIDGE: PID {pid}")
                print(f"   Command: {cmd_line}")
                zombies.append(pid)
                
        if zombies:
            print(f"\nFound {len(zombies)} zombie bridge processes.")
            choice = input("Do you want to KILL them? (y/n): ").strip().lower()
            if choice == 'y':
                for pid in zombies:
                    try:
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True)
                        print(f"Killed PID {pid}")
                    except Exception as e:
                        print(f"Failed to kill {pid}: {e}")
        else:
            print("✅ No zombie bridge processes found.")
            
    except Exception as e:
        print(f"Error checking processes: {e}")

def main():
    print("========================================")
    print("      DACOS VCI Health Check Tool       ")
    print("========================================")
    
    if not is_admin():
        print("⚠️ WARNING: Not running as Admin. Registry scan might be incomplete.")
    
    list_j2534_devices()
    check_zombie_processes()
    
    print("\n--- Troubleshooting Tips for Scanmatik ---")
    print("1. If 'Scanmatik' is missing above, REINSTALL the Scanmatik drivers.")
    print("2. If it appears above but fails to connect, check 'Device Manager'.")
    print("3. Look for 'Show Hidden Devices' in Device Manager.")
    print("4. Try a different USB cable and port.")
    print("\nDone.")

if __name__ == "__main__":
    main()
