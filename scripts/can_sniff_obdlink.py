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

    # Vehicle configurations for multiple manufacturers
    VEHICLE_MODELS = {
        'chevrolet_cruze_2014': {
            'name': 'Chevrolet Cruze 2014',
            'vin': 'KL1JF6889EK617029',
            'odo': '115315km',
            'manufacturer': 'GM/Chevrolet',
            'protocol': 'ISO15765',
            'arbitration_ids': {
                'engine': ['7E8', '7E0', '7E1'],      # ECM primary/secondary
                'transmission': ['7E2', '7EA'],        # TCM
                'brakes': ['7B0', '7B1'],              # ABS/EBCM
                'steering': ['7B2', '7B3'],            # Power Steering
                'body': ['7A0', '7A1'],                # BCM
                'instrument': ['7C0', '7C1'],          # IPC
                'climate': ['7D0', '7D1'],             # HVAC
                'safety': ['7E0', '7E1']               # Airbag/SDM
            }
        },
        'bmw_e90_2005': {
            'name': 'BMW E90 320d 2005',
            'vin': 'WBAVC36020NC55225',
            'odo': '255319km',
            'manufacturer': 'BMW',
            'protocol': 'CAN_29BIT_500K',
            'arbitration_ids': {
                'engine': ['6F1', '6F9'],              # DDE/DME (Diesel Engine Management)
                'transmission': ['6D1', '6D9'],        # EGS (Transmission Control)
                'brakes': ['6B1', '6B9'],              # ABS (Anti-lock Braking System)
                'safety': ['6A1', '6A9'],              # Airbag/SRS (Safety Restraint System)
                'instrument': ['6E1', '6E9'],          # KOMBI (Instrument Cluster)
                'body': ['6C1', '6C9'],                # ZKE (Central Body Electronics)
                'climate': ['6H1', '6H9'],             # IHKA (Climate Control System)
                'parking': ['6E5', '6E6']              # PDC (Parking Distance Control)
            }
        },
        'bmw_e90_320d': {
            'name': 'BMW E90 320d 2005 (Diesel)',
            'vin': 'WBAVC36020NC55225',
            'odo': '255319km',
            'manufacturer': 'BMW',
            'engine': '2.0L M47 Diesel',
            'protocol': 'CAN_29BIT_500K',
            'arbitration_ids': {
                'engine': ['6F1', '6F9'],              # DDE (Diesel Engine Management)
                'transmission': ['6D1', '6D9'],        # EGS (Automatic Transmission)
                'brakes': ['6B1', '6B9'],              # ABS/DSC
                'safety': ['6A1', '6A9'],              # Airbag/SRS
                'instrument': ['6E1', '6E9'],          # KOMBI (Cluster)
                'body': ['6C1', '6C9'],                # ZKE (Central Body)
                'climate': ['6H1', '6H9'],             # IHKA (Climate)
                'parking': ['6E5', '6E6'],             # PDC
                'doors': ['6B0', '6B1'],               # Door systems
                'windows': ['6C0', '6C1']              # Window/roof systems
            }
        },
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
        },
        'generic_bmw': {
            'name': 'Generic BMW',
            'protocol': 'ISO15765_29BIT',
            'arbitration_ids': {
                'engine': ['6F1', '6F9'],              # DME/DDE
                'transmission': ['6D1', '6D9'],        # EGS
                'brakes': ['6B1', '6B9'],              # ABS
                'safety': ['6A1', '6A9'],              # Airbag
                'instrument': ['6E1', '6E9'],          # KOMBI
                'body': ['6C1', '6C9'],                # ZKE
                'climate': ['6H1', '6H9']              # IHKA
            }
        }
    }

    def __init__(self, mock_mode: bool = False, vehicle_model: str = 'chevrolet_cruze_2014'):
        self.mock_mode = mock_mode
        self.vehicle_model = vehicle_model.lower()
        self.device_handler = DeviceHandler(mock_mode=mock_mode)
        self.is_sniffing = False

        # Load vehicle configuration
        if self.vehicle_model not in self.VEHICLE_MODELS:
            logger.warning(f"Unknown vehicle model '{vehicle_model}', using Chevrolet Cruze 2014 config")
            self.vehicle_model = 'chevrolet_cruze_2014'

        self.vehicle_config = self.VEHICLE_MODELS[self.vehicle_model]
        logger.info(f"Initialized for {self.vehicle_config['name']}")
        if 'vin' in self.vehicle_config:
            logger.info(f"VIN: {self.vehicle_config['vin']}")
            logger.info(f"Odometer: {self.vehicle_config.get('odo', 'Unknown')}")
            logger.info(f"Manufacturer: {self.vehicle_config.get('manufacturer', 'Unknown')}")

    def setup_for_ford_vehicle(self) -> bool:
        """Set up OBDLink MX+ for Ford vehicle CAN sniffing"""
        vehicle_name = self.vehicle_config['name']
        logger.info(f"Setting up OBDLink MX+ for {vehicle_name}...")

        # Connect to OBDLink MX+ device
        if not self.device_handler.connect_to_device("OBDLink MX+", self.vehicle_config['protocol']):
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

def main():
    """Main function for CAN sniffing demonstration"""
    # Parse command line arguments
    mock_mode = "--mock" in sys.argv
    vehicle_model = 'chevrolet_cruze_2014'  # default

    # Check for vehicle model argument
    for arg in sys.argv:
        if arg.startswith('--vehicle='):
            vehicle_model = arg.split('=')[1]
        elif arg in ['--cruze', '--cruze2014', '--chevrolet']:
            vehicle_model = 'chevrolet_cruze_2014'
        elif arg in ['--ranger', '--ranger2014']:
            vehicle_model = 'ranger_2014'
        elif arg in ['--figo']:
            vehicle_model = 'figo'
        elif arg in ['--bmw', '--bmwe90', '--e90']:
            vehicle_model = 'bmw_e90_2005'

    # Get vehicle config for display
    vehicle_config = OBDLinkSniffer.VEHICLE_MODELS.get(vehicle_model.lower(),
                                                   OBDLinkSniffer.VEHICLE_MODELS['chevrolet_cruze_2014'])

    print(f"OBDLink MX+ CAN Sniffer for {vehicle_config['name']}")
    print("=" * 50)

    if mock_mode:
        print("Running in MOCK MODE (no real hardware required)")
    else:
        print("Running with REAL hardware")
        print("Make sure OBDLink MX+ is paired via Bluetooth")

    print(f"Vehicle Model: {vehicle_config['name']}")
    if 'vin' in vehicle_config:
        print(f"VIN: {vehicle_config['vin']}")
        print(f"Odometer: {vehicle_config.get('odo', 'Unknown')}")
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
            if 'cruze' in vehicle_model:
                vehicle_short = 'cruze_2014'
                filename = f"chevrolet_{vehicle_short}_can_capture_{timestamp}.txt"
            elif 'bmw' in vehicle_model:
                vehicle_short = 'e90_2005'
                filename = f"bmw_{vehicle_short}_can_capture_{timestamp}.txt"
            else:
                vehicle_short = vehicle_model.replace('_', '').replace('2014', '')
                filename = f"ford_{vehicle_short}_can_capture_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write(f"CAN Messages captured from {vehicle_config['name']}\n")
                if 'vin' in vehicle_config:
                    f.write(f"VIN: {vehicle_config['vin']}\n")
                    f.write(f"Odometer: {vehicle_config.get('odo', 'Unknown')}\n")
                f.write(f"Protocol: {vehicle_config['protocol']}\n")
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