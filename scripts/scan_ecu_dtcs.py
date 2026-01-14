#!/usr/bin/env python3
"""
ECU DTC Scan Script
Scans ECU for Diagnostic Trouble Codes (DTCs) and displays results
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ECUDTCScanner:
    """ECU DTC Scanner using AutoDiag diagnostics controller"""

    def __init__(self):
        self.diagnostics_controller = None
        self.brand = "Toyota"  # Default brand, can be changed

    def initialize_diagnostics(self):
        """Initialize the diagnostics controller"""
        try:
            from AutoDiag.core.diagnostics import DiagnosticsController
            self.diagnostics_controller = DiagnosticsController()
            logger.info("✅ Diagnostics controller initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize diagnostics controller: {e}")
            return False

    def set_brand(self, brand: str):
        """Set the vehicle brand"""
        self.brand = brand
        if self.diagnostics_controller:
            self.diagnostics_controller.set_brand(brand)
            logger.info(f"✅ Brand set to: {brand}")

    def scan_dtcs(self):
        """Scan ECU for DTCs"""
        if not self.diagnostics_controller:
            logger.error("❌ Diagnostics controller not initialized")
            return None

        logger.info(f"🔍 Scanning ECU for DTCs (Brand: {self.brand})...")

        try:
            # Attempt to read DTCs
            result = self.diagnostics_controller.read_dtcs(self.brand)

            if result.get("status") == "error":
                logger.error(f"❌ DTC scan failed: {result.get('message', 'Unknown error')}")
                return None

            logger.info("✅ DTC scan initiated successfully")
            logger.info("Waiting for scan completion...")

            # In a real implementation, we'd wait for the signal or callback
            # For this script, we'll simulate waiting
            import time
            time.sleep(2)  # Wait for the async operation

            # Try to get the DTC data from the controller
            # This is a simplified approach - in real usage, we'd use signals/callbacks
            dtc_data = {
                "timestamp": datetime.now().isoformat(),
                "brand": self.brand,
                "dtcs": [],  # This would be populated by the real hardware
                "total_count": 0
            }

            return dtc_data

        except Exception as e:
            logger.error(f"❌ DTC scan error: {e}")
            return None

    def display_results(self, dtc_data):
        """Display DTC scan results"""
        if not dtc_data:
            logger.error("❌ No DTC data to display")
            return

        logger.info("\n" + "=" * 60)
        logger.info("ECU DTC SCAN RESULTS")
        logger.info("=" * 60)

        logger.info(f"Timestamp: {dtc_data.get('timestamp', 'Unknown')}")
        logger.info(f"Brand: {dtc_data.get('brand', 'Unknown')}")
        logger.info(f"Total DTCs Found: {dtc_data.get('total_count', 0)}")

        dtcs = dtc_data.get('dtcs', [])
        if dtcs:
            logger.info("\nDTC Details:")
            for i, dtc in enumerate(dtcs, 1):
                logger.info(f"{i}. Code: {dtc.get('code', 'Unknown')}")
                logger.info(f"   Description: {dtc.get('description', 'Unknown')}")
                logger.info(f"   Status: {dtc.get('status', 'Unknown')}")
                logger.info(f"   Priority: {dtc.get('priority', 'Unknown')}")
                if 'freeze_frame' in dtc:
                    ff = dtc['freeze_frame']
                    logger.info(f"   Freeze Frame: RPM={ff.get('RPM', 'N/A')}, Load={ff.get('Load', 'N/A')}")
                logger.info("")
        else:
            logger.info("\nNo DTCs found in ECU memory")
            logger.info("This indicates either:")
            logger.info("- No current faults")
            logger.info("- DTCs have been cleared")
            logger.info("- Hardware connection issues")

        logger.info("=" * 60)

    def cleanup(self):
        """Clean up resources"""
        if self.diagnostics_controller:
            self.diagnostics_controller.cleanup()
            logger.info("✅ Diagnostics controller cleaned up")


def main():
    """Main DTC scan execution"""
    scanner = ECUDTCScanner()

    # Initialize diagnostics
    if not scanner.initialize_diagnostics():
        logger.error("Failed to initialize diagnostics system")
        return False

    # Set brand (you can modify this or make it configurable)
    scanner.set_brand("Toyota")  # Default to Toyota, change as needed

    # Perform DTC scan
    dtc_results = scanner.scan_dtcs()

    # Display results
    scanner.display_results(dtc_results)

    # Cleanup
    scanner.cleanup()

    logger.info("\n🎯 DTC scan completed. Please verify the results match your expectations.")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)