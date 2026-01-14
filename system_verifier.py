import os
import subprocess
import winreg
import psutil
import re

def verify_drivers():
    """
    Verify installed drivers by checking for unsigned drivers using PowerShell.
    """
    try:
        # Use PowerShell to find unsigned drivers
        ps_command = "Get-WmiObject Win32_PnPSignedDriver | Where-Object { $_.IsSigned -eq $false } | Select-Object DeviceName, Manufacturer, DriverVersion | Format-Table -AutoSize"
        result = subprocess.run(['powershell', '-Command', ps_command], capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 2:  # More than just headers
                return lines[2:]  # Skip headers
            else:
                return []
        else:
            return [f"Error running PowerShell command: {result.stderr}"]
    except Exception as e:
        return [str(e)]

def check_rogue_programs():
    """
    Check for suspicious running processes.
    """
    suspicious = []
    known_bad_keywords = ['trojan', 'virus', 'malware', 'hack', 'keylogger', 'ransomware', 'spyware']
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            name = proc.info['name'].lower() if proc.info['name'] else ''
            exe = proc.info['exe'].lower() if proc.info['exe'] else ''
            if any(keyword in name or keyword in exe for keyword in known_bad_keywords):
                suspicious.append(f"PID {proc.info['pid']}: {proc.info['name']} - {proc.info['exe']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return suspicious

def scan_registry_unused():
    """
    Scan registry for unused uninstall entries (install locations that don't exist).
    """
    unused = []
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        i = 0
        while True:
            try:
                subkey = winreg.EnumKey(key, i)
                subkey_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\\" + subkey
                subkey_handle = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey_path)
                try:
                    install_location = winreg.QueryValueEx(subkey_handle, "InstallLocation")[0]
                    if install_location and not os.path.exists(install_location):
                        unused.append(f"{subkey}: {install_location}")
                except FileNotFoundError:
                    pass  # No InstallLocation value
                winreg.CloseKey(subkey_handle)
                i += 1
            except OSError:
                break
        winreg.CloseKey(key)
    except Exception as e:
        unused.append(f"Error scanning registry: {str(e)}")
    return unused

def scan_registry_unusual():
    """
    Scan registry for unusual entries with suspicious keywords.
    """
    unusual = []
    suspicious_patterns = [r'hack', r'trojan', r'virus', r'malware', r'keylog', r'rootkit', r'exploit', r'backdoor']
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE")
        def scan_subkeys(k, path):
            i = 0
            while True:
                try:
                    subkey = winreg.EnumKey(k, i)
                    full_path = path + "\\" + subkey
                    if re.search('|'.join(suspicious_patterns), subkey, re.IGNORECASE):
                        unusual.append(full_path)
                    try:
                        subk = winreg.OpenKey(k, subkey)
                        scan_subkeys(subk, full_path)
                        winreg.CloseKey(subk)
                    except:
                        pass
                    i += 1
                except OSError:
                    break
        scan_subkeys(key, "SOFTWARE")
        winreg.CloseKey(key)
    except Exception as e:
        unusual.append(f"Error scanning registry: {str(e)}")
    return unusual

def main():
    """
    Main function to run all checks.
    """
    print("System Verifier Starting...")
    print("=" * 50)

    print("\n1. Checking Drivers...")
    drivers = verify_drivers()
    if drivers:
        print("Problematic Drivers:")
        for d in drivers:
            print(f"  - {d}")
    else:
        print("All drivers appear to be running normally.")

    print("\n2. Checking for Rogue/Malicious Programs...")
    rogues = check_rogue_programs()
    if rogues:
        print("Suspicious Processes Found:")
        for r in rogues:
            print(f"  - {r}")
    else:
        print("No suspicious processes detected.")

    print("\n3. Scanning Registry for Unused Keys...")
    unused = scan_registry_unused()
    if unused:
        print("Unused Registry Keys (InstallLocation points to non-existent path):")
        for u in unused:
            print(f"  - {u}")
    else:
        print("No unused registry keys found.")

    print("\n4. Scanning Registry for Unusual Entries...")
    unusual = scan_registry_unusual()
    if unusual:
        print("Unusual Registry Entries:")
        for u in unusual:
            print(f"  - {u}")
    else:
        print("No unusual registry entries found.")

    print("\n" + "=" * 50)
    print("System verification complete.")

if __name__ == "__main__":
    main()