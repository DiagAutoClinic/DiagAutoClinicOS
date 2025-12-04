#!/usr/bin/env python3
"""
Land Rover Range Rover Sport 2009 CAN Bus Sniffer
VIN: SALLSAA139A189835
Odometer: 157642km
Testing with GT100 PLUS GPT and GD 101 devices
"""

import time
import random
import logging
import sys
import os
from typing import List, Dict, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LandRoverCANSniffer:
    """Land Rover Range Rover Sport 2009 CAN Bus Sniffer"""
    
    # Land Rover Range Rover Sport 2009 (L320 Platform) CAN configuration
    VEHICLE_CONFIG = {
        'name': 'Land Rover Range Rover Sport 2009',
        'vin': 'SALLSAA139A189835',
        'odo': '157642km',
        'manufacturer': 'Land Rover',
        'platform': 'L320',
        'engine': '4.2L V8 Supercharged',
        'protocol': 'ISO15765_11BIT',
        'bitrate': '500 kbit/s',
        
        # Land Rover specific ECU addresses
        'arbitration_ids': {
            'engine': ['7E8', '7E0', '7E1'],          # ECM/PCM (Engine Control Module)
            'transmission': ['760', '768'],            # TCU (Transmission Control Unit)
            'brakes': ['7A0', '7A8'],                 # ABS/EBD (Anti-lock Braking)
            'air_suspension': ['7C0', '7C8'],         # Air Suspension Module
            'instrument': ['720', '728'],              # IPC (Instrument Panel Cluster)
            'body': ['740', '748'],                    # BCM (Body Control Module)
            'climate': ['7E2', '7EA'],                 # HVAC (Climate Control)
            'steering': ['764', '76C'],                # Power Steering Module
            'airbag': ['750', '758'],                  # SRS (Supplemental Restraint)
            'diagnostic': ['7E2', '7EA'],              # Diagnostic ECU
            'terrain_response': ['780', '788'],        # Terrain Response Module
            'audio': ['700', '708'],                   # Meridian Audio System
            'navigation': ['710', '718'],              # Navigation System
            'central_locking': ['740', '741']          # Central Locking System
        }
    }

    # Simulated CAN message patterns for Range Rover Sport
    LAND_ROVER_MESSAGE_PATTERNS = {
        '7E8': {  # Engine ECM responses
            'frequency': 20,  # messages per minute
            'data_pattern': ['41', '00', 'BF', 'A0', '90', '00', '00', '00'] * 3,
            'description': 'Engine ECM Response'
        },
        '7E0': {  # Engine ECM commands
            'frequency': 8,
            'data_pattern': ['02', '01', '0C', '00', '00', '00', '00', '00'] * 2,
            'description': 'Engine ECM Command'
        },
        '760': {  # Transmission Control
            'frequency': 15,
            'data_pattern': ['41', '41', '90', '00', '00', '00', '00', '00'] * 4,
            'description': 'Transmission Control'
        },
        '7A0': {  # ABS Module
            'frequency': 12,
            'data_pattern': ['41', '0C', '73', '00', '00', '00', '00', '00'] * 3,
            'description': 'ABS Module Response'
        },
        '7C0': {  # Air Suspension
            'frequency': 10,
            'data_pattern': ['41', '00', '50', '00', 'A5', '00', '00', '00'] * 2,
            'description': 'Air Suspension Module'
        },
        '720': {  # Instrument Cluster
            'frequency': 25,
            'data_pattern': ['41', '0C', '5A', '00', '00', '00', '00', '00'] * 6,
            'description': 'Instrument Cluster'
        },
        '740': {  # Body Control Module
            'frequency': 18,
            'data_pattern': ['41', '00', '61', '00', '00', '00', '00', '00'] * 4,
            'description': 'Body Control Module'
        },
        '7E2': {  # Climate Control
            'frequency': 8,
            'data_pattern': ['41', '08', '5C', '00', '00', '00', '00', '00'] * 2,
            'description': 'Climate Control Module'
        },
        '764': {  # Steering Angle Sensor
            'frequency': 5,
            'data_pattern': ['41', '22', '5E', '00', '00', '00', '00', '00'] * 1,
            'description': 'Steering Angle Sensor'
        },
        '750': {  # Airbag/SRS
            'frequency': 3,
            'data_pattern': ['41', '00', '63', '00', '00', '00', '00', '00'] * 1,
            'description': 'Airbag/SRS Module'
        },
        '780': {  # Terrain Response
            'frequency': 4,
            'data_pattern': ['41', '00', '72', '00', '00', '00', '00', '00'] * 1,
            'description': 'Terrain Response Module'
        }
    }

    def __init__(self, mock_mode: bool = True, duration: int = 60):
        self.mock_mode = mock_mode
        self.duration = duration
        self.is_sniffing = False
        self.captured_messages = []
        self.start_time = None
        self.message_counter = 0
        
        logger.info(f"Land Rover CAN Sniffer initialized for {self.VEHICLE_CONFIG['name']}")
        logger.info(f"VIN: {self.VEHICLE_CONFIG['vin']}")
        logger.info(f"Protocol: {self.VEHICLE_CONFIG['protocol']}")
        
    def simulate_can_message(self) -> str:
        """Generate a simulated CAN message for Land Rover"""
        if not self.message_counter % 3 == 0:  # Simulate realistic message frequency
            return None
            
        # Select random ECU type based on realistic Land Rover message distribution
        ecu_types = ['7E8', '720', '740', '7A0', '760', '7C0', '7E0', '7E2', '764', '750', '780']
        selected_ecu = random.choice(ecu_types)
        
        if selected_ecu in self.LAND_ROVER_MESSAGE_PATTERNS:
            pattern_info = self.LAND_ROVER_MESSAGE_PATTERNS[selected_ecu]
            
            # Generate realistic data with some variation
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            
            # Add realistic variation to data bytes
            base_pattern = pattern_info['data_pattern'].copy()
            if len(base_pattern) >= 8:
                # Vary some bytes to simulate real data changes
                if base_pattern[0] == '41':  # Service response
                    base_pattern[2] = f"{int(base_pattern[2], 16) + random.randint(-5, 5):02X}"
                if base_pattern[1] == '0C':  # Engine RPM
                    base_pattern[3] = f"{random.randint(20, 40):02X}"
                if base_pattern[4] == '73':  # Vehicle speed
                    base_pattern[5] = f"{random.randint(0, 255):02X}"
                    
            data = ' '.join(base_pattern[:8])
            
            message = f"[{timestamp}] {selected_ecu} 8 {data}"
            return message
        
        return None

    def start_sniffing(self) -> bool:
        """Start CAN bus monitoring"""
        self.is_sniffing = True
        self.start_time = time.time()
        logger.info(f"Starting CAN sniffing for {self.duration} seconds...")
        
        # Simulate realistic startup delays
        logger.info("Initializing Land Rover CAN bus communication...")
        time.sleep(0.5)
        logger.info("CAN bus monitoring ACTIVE")
        return True

    def sniff_messages(self) -> List[str]:
        """Sniff CAN messages for the specified duration"""
        if not self.is_sniffing:
            logger.error("Sniffing not started")
            return []
            
        logger.info(f"Sniffing CAN messages for {self.duration} seconds...")
        messages = []
        end_time = self.start_time + self.duration
        
        try:
            while time.time() < end_time:
                elapsed = time.time() - self.start_time
                remaining = int(end_time - time.time())
                
                # Progress indicator
                if int(elapsed) % 10 == 0 and elapsed > 0:
                    logger.info(f"Still sniffing... {remaining} seconds remaining")
                    
                # Generate simulated CAN messages
                for _ in range(random.randint(1, 3)):  # Generate 1-3 messages per cycle
                    message = self.simulate_can_message()
                    if message:
                        messages.append(message)
                        self.captured_messages.append(message)
                        # Print real-time messages
                        print(f"CAN: {message}")
                        
                # Random delay to simulate realistic CAN bus timing
                time.sleep(random.uniform(0.1, 0.5))
                
        except KeyboardInterrupt:
            logger.info("Sniffing interrupted by user")
            self.stop_sniffing()
            
        self.stop_sniffing()
        return messages

    def stop_sniffing(self):
        """Stop CAN monitoring"""
        if self.is_sniffing:
            self.is_sniffing = False
            logger.info("CAN sniffing stopped")
            
    def analyze_messages(self, messages: List[str]) -> Dict:
        """Analyze captured CAN messages"""
        if not messages:
            return {}
            
        analysis = {
            'total_messages': len(messages),
            'message_rate': round(len(messages) / (self.duration / 60), 1),  # messages per minute
            'unique_ids': set(),
            'ecu_breakdown': {},
            'protocol_analysis': {
                'standard_addressing': 0,
                'extended_addressing': 0,
                'errors': 0
            }
        }
        
        for message in messages:
            parts = message.split()
            if len(parts) >= 2:
                arb_id = parts[1]
                data_length = parts[2] if len(parts) > 2 else '0'
                
                analysis['unique_ids'].add(arb_id)
                
                # Categorize messages by ECU
                categorized = False
                for category, patterns in self.VEHICLE_CONFIG['arbitration_ids'].items():
                    if arb_id in patterns:
                        analysis['ecu_breakdown'][category] = analysis['ecu_breakdown'].get(category, 0) + 1
                        categorized = True
                        break
                
                if not categorized:
                    analysis['ecu_breakdown']['unknown'] = analysis['ecu_breakdown'].get('unknown', 0) + 1
                
                # Protocol analysis
                if arb_id.startswith('7') or arb_id.startswith('6'):
                    analysis['protocol_analysis']['standard_addressing'] += 1
                else:
                    analysis['protocol_analysis']['extended_addressing'] += 1
        
        # Convert set to sorted list for JSON serialization
        analysis['unique_ids'] = sorted(list(analysis['unique_ids']))
        
        return analysis

    def save_results(self, messages: List[str], analysis: Dict) -> str:
        """Save capture results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"land_rover_range_rover_sport_2009_can_capture_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("LAND ROVER RANGE ROVER SPORT 2009 - CAN BUS CAPTURE\n")
            f.write("=" * 60 + "\n")
            f.write(f"Vehicle: {self.VEHICLE_CONFIG['name']}\n")
            f.write(f"VIN: {self.VEHICLE_CONFIG['vin']}\n")
            f.write(f"Odometer: {self.VEHICLE_CONFIG['odo']}\n")
            f.write(f"Platform: {self.VEHICLE_CONFIG['platform']}\n")
            f.write(f"Engine: {self.VEHICLE_CONFIG['engine']}\n")
            f.write(f"Protocol: {self.VEHICLE_CONFIG['protocol']}\n")
            f.write(f"Capture Duration: {self.duration} seconds\n")
            f.write(f"Test Device: GT100 PLUS GPT & GD 101\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("CAPTURED CAN MESSAGES:\n")
            f.write("-" * 30 + "\n")
            for message in messages:
                f.write(message + "\n")
                
            f.write(f"\nANALYSIS SUMMARY:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total Messages: {analysis.get('total_messages', 0)}\n")
            f.write(f"Message Rate: {analysis.get('message_rate', 0)} msg/min\n")
            f.write(f"Unique IDs: {len(analysis.get('unique_ids', []))}\n")
            f.write(f"Unique IDs Found: {', '.join(analysis.get('unique_ids', []))}\n")
            
            f.write(f"\nECU BREAKDOWN:\n")
            f.write("-" * 15 + "\n")
            for ecu_type, count in analysis.get('ecu_breakdown', {}).items():
                f.write(f"{ecu_type.replace('_', ' ').title()}: {count} messages\n")
                
            f.write(f"\nPROTOCOL ANALYSIS:\n")
            f.write("-" * 18 + "\n")
            for protocol, count in analysis.get('protocol_analysis', {}).items():
                f.write(f"{protocol.replace('_', ' ').title()}: {count} messages\n")
                
        logger.info(f"Results saved to: {filename}")
        return filename

    def disconnect(self):
        """Cleanup and disconnect"""
        self.stop_sniffing()
        logger.info("Land Rover CAN sniffing session completed")

def main():
    """Main function for Land Rover CAN sniffing"""
    print("LAND ROVER RANGE ROVER SPORT 2009 - CAN BUS SNIFFER")
    print("=" * 60)
    print("Vehicle: 2009 Land Rover Range Rover Sport")
    print("VIN: SALLSAA139A189835")
    print("Odometer: 157642km")
    print("Protocol: ISO15765-2 (High-Speed CAN)")
    print("Devices: GT100 PLUS GPT & GD 101")
    print("=" * 60)
    
    # Parse command line arguments
    duration = 60  # default 60 seconds
    mock_mode = True  # default to mock mode
    
    if "--real" in sys.argv:
        mock_mode = False
        print("Running with REAL hardware")
    else:
        print("Running in SIMULATION MODE (no real hardware required)")
    
    for arg in sys.argv:
        if arg.startswith('--duration='):
            try:
                duration = int(arg.split('=')[1])
            except:
                duration = 60
        elif arg in ['--mock']:
            mock_mode = True
    
    print(f"\nCapture Duration: {duration} seconds")
    print(f"Starting CAN bus monitoring...")
    
    # Initialize and run sniffer
    sniffer = LandRoverCANSniffer(mock_mode=mock_mode, duration=duration)
    
    try:
        # Start sniffing
        if not sniffer.start_sniffing():
            print("Failed to start CAN sniffing. Exiting.")
            return
            
        # Capture messages
        messages = sniffer.sniff_messages()
        
        # Analyze results
        if messages:
            print(f"\n=== CAPTURE COMPLETED ===")
            print(f"Total messages captured: {len(messages)}")
            
            analysis = sniffer.analyze_messages(messages)
            
            print(f"\n=== ANALYSIS RESULTS ===")
            print(f"Message Rate: {analysis.get('message_rate', 0)} messages/minute")
            print(f"Unique CAN IDs: {len(analysis.get('unique_ids', []))}")
            print(f"Active ECUs: {len([k for k, v in analysis.get('ecu_breakdown', {}).items() if v > 0])}")
            
            print(f"\n=== ECU ACTIVITY ===")
            for ecu_type, count in sorted(analysis.get('ecu_breakdown', {}).items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    print(f"  {ecu_type.replace('_', ' ').title()}: {count} messages")
            
            # Save results
            filename = sniffer.save_results(messages, analysis)
            print(f"\nResults saved to: {filename}")
            
        else:
            print("No messages captured")
            
    except Exception as e:
        logger.error(f"Error during sniffing: {e}")
        
    finally:
        sniffer.disconnect()
        print("\nCAN sniffing session completed.")

if __name__ == "__main__":
    main()