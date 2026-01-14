import os
import sys
import time
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add current directory to path so we can import shared modules
sys.path.append(os.getcwd())

try:
    from shared.j2534_passthru import J2534PassThru, J2534Protocol, J2534Status
except ImportError as e:
    print(f"Error importing J2534 modules: {e}")
    sys.exit(1)

def check_godiag_driver():
    print("\n--- Checking Godiag Drivers ---")
    paths = [
        r"C:\Program Files (x86)\Godiag\J2534\Godiag_J2534.dll",
        r"C:\Program Files\Godiag\J2534\Godiag_J2534.dll",
        os.path.join(os.getcwd(), "drivers", "Godiag_J2534.dll"),
        os.path.join(os.getcwd(), "Godiag_J2534.dll"),
        os.path.join(os.getcwd(), "drivers", "GODIAG J2534 Driver", "GODIAG_PT32.dll")
    ]
    
    import platform
    print(f"Python Architecture: {platform.architecture()[0]}")
    
    found_path = None
    for p in paths:
        if os.path.exists(p):
            print(f"[OK] Found driver at: {p}")
            found_path = p
            break
        else:
            print(f"[MISSING] Driver not found at: {p}")
            
    return found_path

def test_connection(dll_path):
    print(f"\n--- Testing Connection with {dll_path} ---")
    
    try:
        j2534 = J2534PassThru(dll_path)
    except Exception as e:
        print(f"[ERROR] Failed to instantiate J2534PassThru: {e}")
        return

    # 1. Open Device
    print("Attempting to OPEN device...")
    if not j2534.open():
        print(f"[FAIL] Could not open device. Last Error: {j2534.get_last_error()}")
        return
    print("[SUCCESS] Device Opened.")

    # 2. Test Protocols
    protocols = [
        ("ISO15765 (CAN)", J2534Protocol.ISO15765),
        ("ISO9141 (K-Line)", J2534Protocol.ISO9141),
        ("ISO14230 (KWP2000)", J2534Protocol.ISO14230)
    ]

    for name, proto in protocols:
        print(f"\nTesting Protocol: {name}...")
        channel_id = j2534.connect(proto, flags=0, baudrate=500000 if "CAN" in name else 10400)
        
        if channel_id > 0:
            print(f"[SUCCESS] Connected to {name} on Channel {channel_id}")
            
            # Try a simple battery voltage check if possible (requires vendor specific or OBD)
            # Or just disconnect
            j2534.disconnect(channel_id)
            print(f"Disconnected {name}")
        else:
            print(f"[FAIL] Could not connect to {name}. Last Error: {j2534.get_last_error()}")

    # 3. Close Device
    j2534.close()
    print("\n[SUCCESS] Device Closed.")

if __name__ == "__main__":
    dll_path = check_godiag_driver()
    
    if dll_path:
        test_connection(dll_path)
    else:
        print("\n[CRITICAL] Godiag Driver NOT found. Please install the Godiag J2534 driver.")
