#!/usr/bin/env python3
"""
CAN Bus Sniffing Script for OBDLink MX+
Configured for Ford vehicles (Ranger 2014, Figo, and other models)
"""

import time
import logging
import sys
import os
from typing import List, Dict

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import the device handler
from tests.integration_tests.test_professional_devices import DeviceHandler, Protocol

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OBDLinkSniffer:
    """OBDLink MX+ CAN Bus Sniffer for Ford vehicles"""

    # Ford model configurations
    FORD_MODELS = {
        'ranger_2014': {
            'name': 'Ford Ranger 2014',
            'protocol': 'ISO15765',
            'arbitration_ids': {
                'engine': ['7E8', '7E0'],
                'transmission': ['7E1', '7E9'],
                'brakes': ['730', '735'],
                'steering': ['740', '745'],
                'body': ['720', '725'],
                'instrument': ['720', '721']
            }
        },
        'figo': {
            'name': 'Ford Figo',
            'protocol': 'ISO15765',
            'arbitration_ids': {
                'engine': ['7E8', '7E0'],
                'transmission': ['7E1', '7E9'],
                'brakes': ['730', '735'],
                'steering': ['740', '745'],
                'body': ['720', '725'],
                'instrument': ['720', '721'],
                'climate': ['730', '731']  # Figo-specific climate control
            }
        },
        'generic_ford': {
            'name': 'Generic Ford',
            'protocol': 'ISO15765',
            'arbitration_ids': {
                'engine': ['7E8', '7E0'],
                'transmission': ['7E1', '7E9'],
                'brakes': ['730', '735'],
                'steering': ['740', '745'],
                'body': ['720', '725']
            }
        }
    }

    def __init__(self, mock_mode: bool = False, vehicle_model: str = 'ranger_2014'):
        self.mock_mode = mock_mode
        self.vehicle_model = vehicle_model.lower()
        self.device_handler = DeviceHandler(mock_mode=mock_mode)
        self.is_sniffing = False

        # Load vehicle configuration
        if self.vehicle_model not in self.FORD_MODELS:
            logger.warning(f"Unknown vehicle model '{vehicle_model}', using generic Ford config")
            self.vehicle_model = 'generic_ford'

        self.vehicle_config = self.FORD_MODELS[self.vehicle_model]
        logger.info(f"Initialized for {self.vehicle_config['name']}")

    def setup_for_ford_vehicle(self) -> bool:
        """Set up OBDLink MX+ for Ford vehicle CAN sniffing"""
        vehicle_name = self.vehicle_config['name']
        logger.info(f"Setting up OBDLink MX+ for {vehicle_name}...")

        # Connect to ELM327 Bluetooth device
        if not self.device_handler.connect_to_device("ELM327 Bluetooth", self.vehicle_config['protocol']):
            logger.error("Failed to connect to OBDLink MX+")
            return False

        # Enable CAN sniffing mode
        if not self.device_handler.enable_can_sniffing(self.vehicle_config['protocol']):
            logger.error("Failed to enable CAN sniffing")
            return False

        logger.info(f"OBDLink MX+ ready for {vehicle_name} CAN sniffing")
        return True

    def setup_for_ford_ranger_2014(self) -> bool:
        """Legacy method for backward compatibility"""
        self.vehicle_model = 'ranger_2014'
        self.vehicle_config = self.FORD_MODELS[self.vehicle_model]
        return self.setup_for_ford_vehicle()

    def start_sniffing(self) -> bool:
        """Start CAN bus monitoring"""
        if not self.device_handler.start_can_monitor():
            logger.error("Failed to start CAN monitoring")
            return False

        self.is_sniffing = True
        logger.info("CAN sniffing started. Monitoring bus traffic...")
        return True

    def sniff_messages(self, duration_seconds: int = 30) -> List[str]:
        """Sniff CAN messages for specified duration"""
        if not self.is_sniffing:
            logger.error("Sniffing not started")
            return []

        logger.info(f"Sniffing CAN messages for {duration_seconds} seconds...")
        messages = []
        start_time = time.time()

        try:
            while (time.time() - start_time) < duration_seconds:
                # Read available messages
                batch = self.device_handler.read_can_messages(timeout_ms=100)
                if batch:
                    messages.extend(batch)
                    # Print messages in real-time
                    for msg in batch:
                        print(f"CAN: {msg}")

                time.sleep(0.1)  # Small delay between reads

        except KeyboardInterrupt:
            logger.info("Sniffing interrupted by user")

        self.stop_sniffing()
        return messages

    def stop_sniffing(self):
        """Stop CAN monitoring"""
        if self.is_sniffing:
            self.device_handler.stop_can_monitor()
            self.is_sniffing = False
            logger.info("CAN sniffing stopped")

    def disconnect(self):
        """Disconnect from device"""
        self.stop_sniffing()
        self.device_handler.disconnect()
        logger.info("Disconnected from OBDLink MX+")

    def analyze_ford_messages(self, messages: List[str]) -> dict:
        """Analyze captured CAN messages for Ford-specific patterns"""
        analysis = {
            'total_messages': len(messages),
            'arbitration_ids': set()
        }

        # Initialize counters for all categories in this vehicle
        for category in self.vehicle_config['arbitration_ids'].keys():
            analysis[f'{category}_messages'] = 0
        analysis['unknown_messages'] = 0

        for msg in messages:
            parts = msg.split()
            if len(parts) >= 1:
                arb_id = parts[0].upper()
                analysis['arbitration_ids'].add(arb_id)

                # Categorize by vehicle-specific message patterns
                categorized = False
                for category, patterns in self.vehicle_config['arbitration_ids'].items():
                    if any(arb_id.startswith(pattern) for pattern in patterns):
                        analysis[f'{category}_messages'] += 1
                        categorized = True
                        break

                if not categorized:
                    analysis['unknown_messages'] += 1

        return analysis

def print_help():
    """Print usage help"""
    print("OBDLink MX+ CAN Sniffer for Ford Vehicles")
    print("=" * 50)
    print("Usage: python can_sniff_obdlink.py [options]")
    print()
    print("Options:")
    print("  --mock              Run in mock mode (no hardware required)")
    print("  --vehicle=MODEL     Specify Ford vehicle model")
    print("  --ranger            Ford Ranger 2014 (default)")
    print("  --figo              Ford Figo")
    print("  --help              Show this help message")
    print()
    print("Examples:")
    print("  python can_sniff_obdlink.py --mock")
    print("  python can_sniff_obdlink.py --figo")
    print("  python can_sniff_obdlink.py --vehicle=ranger_2014")
    print()
    print("Supported vehicles:")
    for model, config in OBDLinkSniffer.FORD_MODELS.items():
        print(f"  {model}: {config['name']}")

def main():
    """Main function for CAN sniffing demonstration"""
    # Check for help
    if "--help" in sys.argv or "-h" in sys.argv:
        print_help()
        return

    # Parse command line arguments
    mock_mode = "--mock" in sys.argv
    vehicle_model = 'ranger_2014'  # default

    # Check for vehicle model argument
    for arg in sys.argv:
        if arg.startswith('--vehicle='):
            vehicle_model = arg.split('=')[1]
        elif arg in ['--ranger', '--ranger2014']:
            vehicle_model = 'ranger_2014'
        elif arg in ['--figo']:
            vehicle_model = 'figo'

    # Get vehicle config for display
    vehicle_config = OBDLinkSniffer.FORD_MODELS.get(vehicle_model.lower(),
                                                   OBDLinkSniffer.FORD_MODELS['generic_ford'])

    print(f"OBDLink MX+ CAN Sniffer for {vehicle_config['name']}")
    print("=" * 50)

    if mock_mode:
        print("Running in MOCK MODE (no real hardware required)")
    else:
        print("Running with REAL hardware")
        print("Make sure OBDLink MX+ is paired via Bluetooth")

    print(f"Vehicle Model: {vehicle_config['name']}")
    print(f"Protocol: {vehicle_config['protocol']}")
    print()

    # Initialize sniffer
    sniffer = OBDLinkSniffer(mock_mode=mock_mode, vehicle_model=vehicle_model)

    try:
        # Setup for selected Ford vehicle
        if not sniffer.setup_for_ford_vehicle():
            print("Setup failed. Exiting.")
            return

        # Start sniffing
        if not sniffer.start_sniffing():
            print("Failed to start sniffing. Exiting.")
            return

        # Sniff for 30 seconds
        messages = sniffer.sniff_messages(duration_seconds=30)

        # Analyze results
        if messages:
            print(f"\nCaptured {len(messages)} CAN messages")
            analysis = sniffer.analyze_ford_messages(messages)
            print("\nAnalysis:")

            # Display analysis for all categories
            for category in sorted(sniffer.vehicle_config['arbitration_ids'].keys()):
                count = analysis.get(f'{category}_messages', 0)
                print(f"  {category.capitalize()} messages: {count}")

            print(f"  Unknown messages: {analysis['unknown_messages']}")
            print(f"  Unique arbitration IDs: {len(analysis['arbitration_ids'])}")
            print(f"  IDs: {sorted(list(analysis['arbitration_ids']))}")

            # Save to file
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            vehicle_short = vehicle_model.replace('_', '').replace('2014', '')
            filename = f"ford_{vehicle_short}_can_capture_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(f"CAN Messages captured from {vehicle_config['name']}\n")
                f.write("=" * 50 + "\n")
                for msg in messages:
                    f.write(msg + "\n")
            print(f"\nMessages saved to: {filename}")
        else:
            print("No messages captured")

    except Exception as e:
        logger.error(f"Error during sniffing: {e}")

    finally:
        # Cleanup
        sniffer.disconnect()
        print("\nSniffing session completed.")

if __name__ == "__main__":
    main()