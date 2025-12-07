#!/usr/bin/env python3
"""Test VCI device scanning"""
import sys
sys.path.insert(0, '.')
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_serial_ports():
    """Test serial port detection"""
    print("=" * 50)
    print("Testing serial port detection...")
    print("=" * 50)
    
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        print(f"Found {len(ports)} ports:")
        for p in ports:
            print(f"  {p.device}: {p.description}")
            print(f"    VID={p.vid}, PID={p.pid}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_vci_manager():
    """Test VCI Manager"""
    print()
    print("=" * 50)
    print("Testing VCI Manager...")
    print("=" * 50)
    
    try:
        from AutoDiag.core.vci_manager import VCIManager
        manager = VCIManager()
        print("VCI Manager created successfully")
        
        print("Scanning for devices...")
        devices = manager.scan_for_devices()
        print(f"Devices found: {len(devices)}")
        
        for d in devices:
            print(f"  - {d.name} ({d.device_type.value}) on {d.port}")
            print(f"    Capabilities: {d.capabilities}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_serial_ports()
    test_vci_manager()
    print()
    print("Test complete!")
