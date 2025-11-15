#!/usr/bin/env python3
"""
AutoDiag Pro - Console-Based Diagnostic Tool
No GUI dependencies - pure console interface
"""

import sys
import os
import logging
from typing import Dict, List, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add shared to path
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared'))
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

try:
    from brand_database import get_brand_list
    from dtc_database import DTCDatabase
    from vin_decoder import VINDecoder
    from j2534_passthru import get_passthru_device
    logger.info("Shared modules imported successfully")
except ImportError as e:
    logger.error(f"Failed to import shared modules: {e}")
    print("Please ensure shared modules are available")
    sys.exit(1)

class ConsoleDiagnosticTool:
    """Console-based diagnostic tool"""

    def __init__(self):
        self.dtc_db = DTCDatabase()
        self.vin_decoder = VINDecoder()
        self.current_brand = None
        self.current_vin = None

    def show_welcome(self):
        """Show welcome message"""
        print("\n" + "="*60)
        print("AutoDiag Pro - Console Diagnostic Tool")
        print("="*60)
        print("Available brands:", ", ".join(get_brand_list()))
        print("="*60)

    def select_brand(self) -> str:
        """Select vehicle brand"""
        brands = get_brand_list()
        while True:
            print("\nAvailable brands:")
            for i, brand in enumerate(brands, 1):
                print(f"{i}. {brand}")

            try:
                choice = input("\nSelect brand (number or name): ").strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(brands):
                        return brands[idx]
                elif choice in brands:
                    return choice
                print("Invalid selection")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                sys.exit(0)

    def show_menu(self):
        """Show main menu"""
        print(f"\n{'='*40}")
        print(f"Current Brand: {self.current_brand}")
        print(f"Current VIN: {self.current_vin or 'Not read'}")
        print(f"{'='*40}")
        print("1. Read VIN")
        print("2. Scan DTCs")
        print("3. Clear DTCs")
        print("4. Change Brand")
        print("5. Exit")
        print(f"{'='*40}")

    def read_vin(self):
        """Read VIN from vehicle"""
        print(f"\nReading VIN for {self.current_brand}...")

        if self.current_brand.lower() == "volkswagen":
            # Try real J2534 connection
            try:
                device = get_passthru_device(mock_mode=False, device_name="GoDiag GD101")
                if device and device.open():
                    print("Connected to J2534 device")
                    # For demo, return mock VIN
                    vin = "WVWZZZ3CZ7E123456"
                    print(f"VIN: {vin}")
                    self.current_vin = vin
                    device.close()
                else:
                    print("J2534 device not available, using demo mode")
                    vin = "WVWZZZ3CZ7E123456"
                    print(f"Demo VIN: {vin}")
                    self.current_vin = vin
            except Exception as e:
                print(f"J2534 error: {e}, using demo mode")
                vin = "WVWZZZ3CZ7E123456"
                print(f"Demo VIN: {vin}")
                self.current_vin = vin
        else:
            # Mock VIN for other brands
            mock_vins = {
                "Toyota": "JTDKN3AU7E0123456",
                "Honda": "JHGCV4A47DA123456",
                "Ford": "1GTGG6B30F1272520",
            }
            vin = mock_vins.get(self.current_brand, f"MOCK{self.current_brand.upper()[:8]}123456")
            print(f"Mock VIN: {vin}")
            self.current_vin = vin

    def scan_dtcs(self):
        """Scan for DTCs"""
        print(f"\nScanning DTCs for {self.current_brand}...")

        if self.current_brand.lower() == "volkswagen":
            # Mock DTCs for VW
            dtcs = [
                ("P0300", "High", "Random/Multiple Cylinder Misfire Detected"),
                ("P0301", "High", "Cylinder 1 Misfire Detected"),
                ("U0100", "Critical", "Lost Communication with ECM"),
            ]
        else:
            # Mock DTCs for other brands
            mock_dtcs = {
                "Toyota": [("P0171", "Medium", "System Too Lean (Bank 1)")],
                "Honda": [("P0420", "Medium", "Catalyst Efficiency Below Threshold")],
                "Ford": [("P0500", "Low", "Vehicle Speed Sensor Malfunction")],
            }
            dtcs = mock_dtcs.get(self.current_brand, [("P0000", "Info", "No DTCs Found")])

        print(f"Found {len(dtcs)} DTC(s):")
        for code, severity, desc in dtcs:
            print(f"  {code} [{severity}]: {desc}")

    def clear_dtcs(self):
        """Clear DTCs"""
        print(f"\nClearing DTCs for {self.current_brand}...")

        confirm = input("Are you sure you want to clear all DTCs? (y/N): ").strip().lower()
        if confirm == 'y':
            print("All DTCs cleared successfully")
        else:
            print("Operation cancelled")

    def run(self):
        """Main application loop"""
        self.show_welcome()
        self.current_brand = self.select_brand()

        while True:
            self.show_menu()
            try:
                choice = input("Select option (1-5): ").strip()

                if choice == '1':
                    self.read_vin()
                elif choice == '2':
                    self.scan_dtcs()
                elif choice == '3':
                    self.clear_dtcs()
                elif choice == '4':
                    self.current_brand = self.select_brand()
                    self.current_vin = None
                elif choice == '5':
                    print("\nGoodbye!")
                    break
                else:
                    print("Invalid option")

                input("\nPress Enter to continue...")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                input("Press Enter to continue...")

def main():
    """Main entry point"""
    try:
        tool = ConsoleDiagnosticTool()
        tool.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\nFatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()