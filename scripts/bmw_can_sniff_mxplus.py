#!/usr/bin/env python3
"""
BMW CAN Sniffing Script using OBDLink MX+
Specifically designed for BMW E90 and other BMW vehicles
"""

import time
import logging
import sys
import os
from typing import List, Dict

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from shared.obdlink_mxplus import OBDLinkMXPlus, OBDLinkProtocol

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BMWCANSniffer:
    """BMW CAN Bus Sniffer using OBDLink MX+"""
    
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.obdlink = OBDLinkMXPlus(mock_mode=mock_mode)
        self.is_sniffing = False
        
        # BMW-specific vehicle configurations
        self.bmw_profiles = {
            'bmw_e90_2005': {
                'name': 'BMW E90 320d 2005',
                'vin': 'WBAVC36020NC55225',
                'odo': '255319km',
                'engine': '2.0L M47 Diesel',
                'protocol': OBDLinkProtocol.ISO15765_29BIT,
                'arbitration_ids': {
                    'dme_dde': ['6F1', '6F9'],          # Engine Management (DME/DDE)
                    'egs': ['6D1', '6D9'],              # Transmission Control (EGS)
                    'abs_dsc': ['6B1', '6B9'],          # Anti-lock Braking System
                    'srs': ['6A1', '6A9'],              # Safety Restraint System
                    'kombi': ['6E1', '6E9'],            # Instrument Cluster
                    'zke': ['6C1', '6C9'],              # Central Body Electronics
                    'ihka': ['6H1', '6H9'],             # Climate Control System
                    'pdc': ['6E5', '6E6'],              # Parking Distance Control
                    'doors': ['6B0', '6B1'],            # Door systems
                    'windows': ['6C0', '6C1']           # Window/roof systems
                }
            },
            'bmw_e90_320i': {
                'name': 'BMW E90 320i 2006',
                'vin': 'WBAVC76020NC12345',
                'odo': '180245km',
                'engine': '2.0L N46 Petrol',
                'protocol': OBDLinkProtocol.ISO15765_29BIT,
                'arbitration_ids': {
                    'dme': ['6F1', '6F9'],              # Engine Management (DME)
                    'egs': ['6D1', '6D9'],              # Transmission Control
                    'abs_dsc': ['6B1', '6B9'],          # Anti-lock Braking System
                    'srs': ['6A1', '6A9'],              # Safety Restraint System
                    'kombi': ['6E1', '6E9'],            # Instrument Cluster
                    'zke': ['6C1', '6C9'],              # Central Body Electronics
                    'ihka': ['6H1', '6H9'],             # Climate Control
                    'pdc': ['6E5', '6E6']               # Parking Distance Control
                }
            },
            'bmw_generic': {
                'name': 'Generic BMW',
                'protocol': OBDLinkProtocol.ISO15765_29BIT,
                'arbitration_ids': {
                    'engine': ['6F1', '6F9'],           # DME/DDE
                    'transmission': ['6D1', '6D9'],     # EGS
                    'brakes': ['6B1', '6B9'],           # ABS
                    'safety': ['6A1', '6A9'],           # Airbag/SRS
                    'instrument': ['6E1', '6E9'],       # KOMBI
                    'body': ['6C1', '6C9'],             # ZKE
                    'climate': ['6H1', '6H9']           # IHKA
                }
            }
        }
        
    def connect_mxplus(self, connection_type: str = "serial", device: str = None) -> bool:
        """Connect to OBDLink MX+"""
        logger.info("Connecting to OBDLink MX+...")
        
        if self.mock_mode:
            logger.info("[MOCK MODE] Simulating MX+ connection")
            self.obdlink.is_connected = True
            return True
        
        if connection_type.lower() == "serial":
            # Try common serial ports
            serial_ports = ["/dev/ttyUSB0", "/dev/ttyUSB1", "COM1", "COM2", "COM3"]
            if device:
                serial_ports = [device]
            
            for port in serial_ports:
                try:
                    if self.obdlink.connect_serial(port):
                        logger.info(f"Connected via serial port: {port}")
                        return True
                except Exception as e:
                    logger.debug(f"Failed to connect on {port}: {e}")
                    continue
            
            logger.error("Failed to connect via serial on any port")
            return False
            
        elif connection_type.lower() == "bluetooth":
            if not device:
                # Discover devices
                logger.info("Discovering Bluetooth devices...")
                devices = self.obdlink.discover_devices()
                if not devices:
                    logger.error("No OBDLink devices found")
                    return False
                
                # Use first found device
                device = devices[0]
                logger.info(f"Using discovered device: {device}")
            
            if self.obdlink.connect_bluetooth(device):
                logger.info(f"Connected via Bluetooth: {device}")
                return True
            else:
                logger.error("Bluetooth connection failed")
                return False
        else:
            logger.error(f"Unknown connection type: {connection_type}")
            return False
    
    def setup_bmw_vehicle(self, bmw_profile: str = 'bmw_e90_2005') -> bool:
        """Setup OBDLink MX+ for BMW CAN sniffing"""
        if bmw_profile not in self.bmw_profiles:
            logger.warning(f"Unknown BMW profile '{bmw_profile}', using generic BMW")
            bmw_profile = 'bmw_generic'
        
        bmw_config = self.bmw_profiles[bmw_profile]
        logger.info(f"Setting up BMW CAN sniffing for: {bmw_config['name']}")
        
        # Set vehicle profile
        if not self.obdlink.set_vehicle_profile(bmw_profile):
            logger.error("Failed to set BMW vehicle profile")
            return False
        
        # Configure for 29-bit CAN (BMW standard)
        if not self.obdlink.configure_can_sniffing(bmw_config['protocol']):
            logger.error("Failed to configure CAN sniffing")
            return False
        
        logger.info(f"BMW CAN sniffing configured for {bmw_config['protocol'].value}")
        logger.info(f"Arbitration IDs to monitor: {len(bmw_config['arbitration_ids'])} categories")
        
        # Print BMW-specific ID ranges
        for category, ids in bmw_config['arbitration_ids'].items():
            logger.info(f"  {category}: {ids}")
        
        return True
    
    def start_can_sniffing(self) -> bool:
        """Start BMW CAN bus sniffing"""
        logger.info("Starting BMW CAN bus monitoring...")
        
        if not self.obdlink.start_monitoring():
            logger.error("Failed to start CAN monitoring")
            return False
        
        self.is_sniffing = True
        logger.info("BMW CAN sniffing active - monitoring bus traffic...")
        return True
    
    def sniff_bmw_can(self, duration_seconds: int = 60, display_realtime: bool = True) -> List[str]:
        """Sniff BMW CAN messages for specified duration"""
        if not self.is_sniffing:
            logger.error("CAN sniffing not active")
            return []
        
        logger.info(f"BMW CAN sniffing for {duration_seconds} seconds...")
        if display_realtime:
            print("\nBMW CAN Message Stream:")
            print("=" * 60)
        
        messages = []
        start_time = time.time()
        message_count = 0
        
        try:
            while (time.time() - start_time) < duration_seconds:
                # Read available messages
                batch = self.obdlink.read_messages(count=10, timeout_ms=100)
                if batch:
                    for msg in batch:
                        messages.append(f"{msg.arbitration_id} {msg.data}")
                        message_count += 1
                        
                        if display_realtime:
                            print(f"[{message_count:04d}] {msg.arbitration_id} {msg.data}")
                
                time.sleep(0.05)  # 50ms between reads
                
        except KeyboardInterrupt:
            logger.info("BMW CAN sniffing interrupted by user")
        
        logger.info(f"BMW CAN sniffing completed: {len(messages)} messages captured")
        return messages
    
    def analyze_bmw_messages(self, messages: List[str]) -> Dict:
        """Analyze captured BMW CAN messages"""
        analysis = {
            'total_messages': len(messages),
            'arbitration_ids': set(),
            'message_rate': 0
        }
        
        # Initialize BMW category counters
        current_profile = list(self.bmw_profiles.values())[0]  # Use first profile for categories
        for category in current_profile['arbitration_ids'].keys():
            analysis[f'{category}_messages'] = 0
        analysis['unknown_messages'] = 0
        
        # Analyze each message
        for msg in messages:
            parts = msg.split()
            if len(parts) >= 1:
                arb_id = parts[0].upper()
                analysis['arbitration_ids'].add(arb_id)
                
                # Categorize BMW messages
                categorized = False
                for category, patterns in current_profile['arbitration_ids'].items():
                    if any(arb_id.startswith(pattern) for pattern in patterns):
                        analysis[f'{category}_messages'] += 1
                        categorized = True
                        break
                
                if not categorized:
                    analysis['unknown_messages'] += 1
        
        return analysis
    
    def save_bmw_results(self, messages: List[str], analysis: Dict, filename: str = None) -> str:
        """Save BMW CAN capture results to file"""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"bmw_can_capture_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("BMW CAN Bus Capture Results\n")
            f.write("=" * 50 + "\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Messages: {analysis['total_messages']}\n")
            f.write(f"Unique Arbitration IDs: {len(analysis['arbitration_ids'])}\n")
            f.write("\nMessage Categories:\n")
            
            for category, count in analysis.items():
                if category.endswith('_messages') and category != 'total_messages':
                    category_name = category.replace('_messages', '').replace('_', ' ').title()
                    f.write(f"  {category_name}: {count}\n")
            
            f.write(f"\nArbitration IDs Found: {sorted(list(analysis['arbitration_ids']))}\n")
            f.write("\n" + "=" * 50 + "\n")
            f.write("Raw CAN Messages:\n")
            
            for msg in messages:
                f.write(msg + "\n")
        
        logger.info(f"BMW results saved to: {filename}")
        return filename
    
    def disconnect(self):
        """Disconnect from OBDLink MX+"""
        self.stop_sniffing()
        self.obdlink.disconnect()
        logger.info("Disconnected from OBDLink MX+")
    
    def stop_sniffing(self):
        """Stop CAN sniffing"""
        if self.is_sniffing:
            self.obdlink.stop_monitoring()
            self.is_sniffing = False
            logger.info("BMW CAN sniffing stopped")

def main():
    """Main BMW CAN sniffing function"""
    # Parse command line arguments
    mock_mode = "--mock" in sys.argv
    duration = 60
    bmw_profile = "bmw_e90_2005"
    connection = "serial"
    device = None
    
    # Parse arguments
    for arg in sys.argv:
        if arg.startswith('--duration='):
            try:
                duration = int(arg.split('=')[1])
            except ValueError:
                logger.warning(f"Invalid duration: {arg}")
        elif arg.startswith('--profile='):
            bmw_profile = arg.split('=')[1]
        elif arg.startswith('--connection='):
            connection = arg.split('=')[1]
        elif arg.startswith('--device='):
            device = arg.split('=')[1]
        elif arg == "--bluetooth":
            connection = "bluetooth"
        elif arg in ["--e90", "--bmw-e90", "--bmw"]:
            bmw_profile = "bmw_e90_2005"
        elif arg in ["--320i", "--bmw-320i"]:
            bmw_profile = "bmw_e90_320i"
        elif arg == "--generic":
            bmw_profile = "bmw_generic"
    
    # Get BMW configuration
    sniffer = BMWCANSniffer(mock_mode=mock_mode)
    
    print("BMW CAN Sniffer using OBDLink MX+")
    print("=" * 50)
    
    if mock_mode:
        print("Running in MOCK MODE (no real hardware required)")
    else:
        print("Running with REAL hardware")
        print("Ensure OBDLink MX+ is connected via USB or Bluetooth")
    
    print(f"BMW Profile: {bmw_profile}")
    print(f"Connection: {connection}")
    print(f"Duration: {duration} seconds")
    print()
    
    try:
        # Connect to MX+
        if not sniffer.connect_mxplus(connection_type=connection, device=device):
            print("Failed to connect to OBDLink MX+. Exiting.")
            return
        
        # Setup for BMW
        if not sniffer.setup_bmw_vehicle(bmw_profile):
            print("Failed to setup BMW configuration. Exiting.")
            return
        
        # Start CAN sniffing
        if not sniffer.start_can_sniffing():
            print("Failed to start CAN sniffing. Exiting.")
            return
        
        # Sniff BMW CAN messages
        messages = sniffer.sniff_bmw_can(duration_seconds=duration)
        
        # Analyze and display results
        if messages:
            print(f"\nAnalysis Results:")
            print("-" * 30)
            analysis = sniffer.analyze_bmw_messages(messages)
            print(f"Total Messages: {analysis['total_messages']}")
            print(f"Unique Arbitration IDs: {len(analysis['arbitration_ids'])}")
            
            # Display BMW-specific categories
            for category, count in analysis.items():
                if category.endswith('_messages') and category != 'total_messages':
                    category_name = category.replace('_messages', '').replace('_', ' ').title()
                    print(f"{category_name}: {count}")
            
            # Save results
            filename = sniffer.save_bmw_results(messages, analysis)
            print(f"\nResults saved to: {filename}")
        else:
            print("No BMW CAN messages captured")
    
    except Exception as e:
        logger.error(f"Error during BMW CAN sniffing: {e}")
        print(f"Error: {e}")
    
    finally:
        # Cleanup
        sniffer.disconnect()
        print("\nBMW CAN sniffing session completed.")

if __name__ == "__main__":
    main()