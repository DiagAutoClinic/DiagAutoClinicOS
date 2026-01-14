import winreg
import os
import sys
import ctypes
import datetime

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_registry_entries(access_flag, view_name):
    entries = []
    key_path = r"Software\PassThruSupport.04.04"
    
    try:
        hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ | access_flag)
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error accessing {view_name} registry: {e}")
        return []

    i = 0
    while True:
        try:
            device_name = winreg.EnumKey(hkey, i)
            device_key_path = f"{key_path}\\{device_name}"
            
            try:
                sub_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, device_key_path, 0, winreg.KEY_READ | access_flag)
                
                try:
                    name = winreg.QueryValueEx(sub_key, "Name")[0]
                except:
                    name = "(Unknown Name)"
                    
                try:
                    vendor = winreg.QueryValueEx(sub_key, "Vendor")[0]
                except:
                    vendor = "(Unknown Vendor)"
                    
                try:
                    function_lib = winreg.QueryValueEx(sub_key, "FunctionLibrary")[0]
                except:
                    function_lib = ""

                winreg.CloseKey(sub_key)
                
                status = "OK"
                if not function_lib:
                    status = "MISSING_DLL_PATH"
                elif not os.path.exists(function_lib):
                    status = "DLL_NOT_FOUND"
                
                entries.append({
                    "key_name": device_name,
                    "full_key_path": device_key_path,
                    "name": name,
                    "vendor": vendor,
                    "dll": function_lib,
                    "status": status,
                    "view": view_name,
                    "access_flag": access_flag
                })
                
            except Exception as e:
                print(f"Error reading key {device_name}: {e}")
                
            i += 1
        except OSError:
            break
            
    winreg.CloseKey(hkey)
    return entries

def delete_registry_key(entry):
    print(f"\nDeleting: {entry['full_key_path']} ({entry['view']})")
    
    try:
        # Open parent key with write access
        parent_path = r"Software\PassThruSupport.04.04"
        hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, parent_path, 0, winreg.KEY_WRITE | entry['access_flag'])
        
        winreg.DeleteKey(hkey, entry['key_name'])
        winreg.CloseKey(hkey)
        print("✅ Successfully deleted.")
        return True
    except Exception as e:
        print(f"❌ Failed to delete: {e}")
        return False

def backup_registry_key(entry):
    # Python's winreg doesn't support 'export', so we use reg.exe
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{entry['key_name']}_{timestamp}.reg"
    filename = "".join(x for x in filename if x.isalnum() or x in "._-") # sanitize
    
    # Handle WOW6432Node path explicitly for export if needed
    # But reg.exe handles architecture automatically if we point to the right path
    # If it's a 32-bit key on 64-bit system, it's under WOW6432Node in reality
    
    real_path = r"HKLM\Software\PassThruSupport.04.04" + "\\" + entry['key_name']
    if entry['view'] == "32-bit" and ctypes.sizeof(ctypes.c_void_p) == 8:
        real_path = r"HKLM\Software\WOW6432Node\PassThruSupport.04.04" + "\\" + entry['key_name']

    cmd = f'reg export "{real_path}" "{filename}" /y'
    
    print(f"Backing up to {filename}...")
    result = os.system(cmd)
    if result == 0:
        print("✅ Backup successful.")
        return True
    else:
        print("❌ Backup failed.")
        return False

def main():
    print("========================================")
    print("      DACOS J2534 Registry Cleaner      ")
    print("========================================")
    print("This tool removes Broken or Stale J2534 Drivers.")
    print("Use with caution.\n")
    
    if not is_admin():
        print("❌ ERROR: You must run this script as Administrator.")
        print("   Right-click your terminal/IDE and select 'Run as Administrator'.")
        input("Press Enter to exit...")
        return

    # Scan both 32-bit and 64-bit views
    entries_64 = []
    entries_32 = []
    
    if ctypes.sizeof(ctypes.c_void_p) == 8: # Running on 64-bit Python
        entries_64 = get_registry_entries(winreg.KEY_WOW64_64KEY, "64-bit")
        entries_32 = get_registry_entries(winreg.KEY_WOW64_32KEY, "32-bit")
    else: # Running on 32-bit Python
        entries_32 = get_registry_entries(0, "32-bit")
        # Can't easily access 64-bit registry from 32-bit process without special flags, 
        # but usually we only care about 32-bit drivers anyway.
        try:
             entries_64 = get_registry_entries(winreg.KEY_WOW64_64KEY, "64-bit")
        except:
             pass

    all_entries = entries_64 + entries_32
    
    if not all_entries:
        print("No J2534 drivers found.")
        return

    print(f"{'#':<3} {'STATUS':<15} {'NAME':<20} {'VENDOR':<20} {'VIEW'}")
    print("-" * 70)
    
    for idx, entry in enumerate(all_entries):
        status_icon = "✅" if entry['status'] == "OK" else "❌"
        print(f"{idx+1:<3} {status_icon} {entry['status']:<12} {entry['name'][:20]:<20} {entry['vendor'][:20]:<20} {entry['view']}")
        if entry['status'] != "OK":
            print(f"    ↳ Path: {entry['dll']}")

    print("-" * 70)
    print("Enter the number of the entry to DELETE (or 'q' to quit).")
    choice = input("> ").strip().lower()
    
    if choice == 'q':
        return
        
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(all_entries):
            target = all_entries[idx]
            print(f"\nYou selected: {target['name']}")
            print(f"Path: {target['dll']}")
            
            confirm = input("Are you sure? (y/n): ").lower()
            if confirm == 'y':
                backup_registry_key(target)
                delete_registry_key(target)
            else:
                print("Operation cancelled.")
        else:
            print("Invalid number.")
    except ValueError:
        print("Invalid input.")

if __name__ == "__main__":
    main()
