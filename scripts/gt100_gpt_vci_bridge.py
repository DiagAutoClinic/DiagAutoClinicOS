#!/usr/bin/env python3
"""
GoDiag GT100 PLUS GPT VCI Bridge
================================

Enhanced VCI bridge implementation that works with ANY existing VCI device
to provide diagnostic enhancement features:

Key Feature: GT100 PLUS GPT acts as a diagnostic bridge that can be used
with ANY VCI device (OBDLink MX+, Scanmatik 2 Pro, etc.) to provide:

• Real-time voltage and current monitoring
• Protocol detection and LED feedback  
• 24V → 12V conversion for heavy vehicles
• All-keys-lost programming assistance
• Battery replacement power backup
• OBDII pin-level access via banana plugs

Architecture: Vehicle → GT100 PLUS GPT → VCI Device → Diagnostic Software
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Import existing VCI managers
try:
    from AutoDiag.core.vci_manager import get_vci_manager, VCITypes
    STANDARD_VCI_AVAILABLE = True
except ImportError:
    STANDARD_VCI_AVAILABLE = False

try:
    from AutoDiag.core.godiag_gt100_gpt_manager import get_gt100_gpt_manager, GT100GPTStatus
    GT100_AVAILABLE = True
except ImportError:
    GT100_AVAILABLE = False

logger = logging.getLogger(__name__)

class BridgeConnectionType(Enum):
    """Types of bridge connections possible with GT100 PLUS GPT"""
    VCI_PASSTHROUGH = "vci_passthrough"
    DIRECT_OBDII = "direct_obdii"
    BENCH_ECU = "bench_ecu"
    PROGRAMMING_TOOL = "programming_tool"

@dataclass
class VCIBridgeConfig:
    """Configuration for VCI bridge setup"""
    primary_vci_type: str  # Type of primary VCI device being used
    gt100_enhancement: bool  # Whether GT100 PLUS GPT enhancement is active
    connection_type: BridgeConnectionType
    vehicle_type: str  # "passenger", "truck", "heavy_vehicle"
    monitoring_enabled: bool  # Voltage/current monitoring active
    programming_mode: bool  # GPT programming mode active

class GT100GPTVCIBridge:
    """VCI Bridge that enhances ANY VCI device with GT100 PLUS GPT capabilities"""
    
    def __init__(self):
        self.setup_logging()
        self.bridge_config = None
        self.primary_vci_manager = None
        self.gt100_manager = None
        
        # Initialize managers
        if STANDARD_VCI_AVAILABLE:
            self.primary_vci_manager = get_vci_manager()
            print("✅ Standard VCI Manager initialized")
            
        if GT100_AVAILABLE:
            self.gt100_manager = get_gt100_gpt_manager()
            print("✅ GT100 PLUS GPT Manager initialized")
            
        print("🔗 GT100 PLUS GPT VCI Bridge ready for any VCI device enhancement")
        
    def setup_logging(self):
        """Setup logging for bridge operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def setup_bridge_configuration(self, 
                                   primary_vci_type: str,
                                   vehicle_type: str = "passenger",
                                   enable_monitoring: bool = True,
                                   enable_programming: bool = False) -> VCIBridgeConfig:
        """Setup bridge configuration for specific VCI and vehicle type"""
        
        self.bridge_config = VCIBridgeConfig(
            primary_vci_type=primary_vci_type,
            gt100_enhancement=GT100_AVAILABLE,
            connection_type=BridgeConnectionType.VCI_PASSTHROUGH,
            vehicle_type=vehicle_type,
            monitoring_enabled=enable_monitoring,
            programming_mode=enable_programming
        )
        
        logger.info(f"Bridge configured: {primary_vci_type} + GT100 PLUS GPT for {vehicle_type} vehicles")
        return self.bridge_config
        
    def connect_bridge_setup(self) -> Dict[str, Any]:
        """Connect the complete bridge setup: Vehicle → GT100 → VCI → Software"""
        connection_result = {
            'status': 'FAIL',
            'details': {},
            'bridge_connected': False
        }
        
        try:
            logger.info("🔗 Setting up GT100 PLUS GPT VCI Bridge...")
            print("Bridge Setup: Vehicle → GT100 PLUS GPT → VCI Device → Diagnostic Software")
            
            # Step 1: Connect GT100 PLUS GPT (if available)
            gt100_connected = False
            if self.gt100_manager:
                print("1. Connecting GT100 PLUS GPT to vehicle OBDII...")
                gt100_connected = self._connect_gt100_plus_gpt()
                if gt100_connected:
                    print("   ✅ GT100 PLUS GPT connected to vehicle")
                else:
                    print("   ⚠️ GT100 PLUS GPT not available, continuing with VCI only")
            else:
                print("1. GT100 PLUS GPT not available, proceeding with VCI only")
                
            # Step 2: Connect primary VCI device
            vci_connected = False
            if self.primary_vci_manager:
                print("2. Connecting primary VCI device...")
                vci_connected = self._connect_primary_vci()
                if vci_connected:
                    print("   ✅ Primary VCI device connected")
                else:
                    print("   ❌ Failed to connect primary VCI device")
            else:
                print("2. No primary VCI manager available")
                
            # Step 3: Verify bridge connectivity
            if gt100_connected and vci_connected:
                connection_result['status'] = 'PASS'
                connection_result['bridge_connected'] = True
                connection_result['details'] = {
                    'gt100_connected': gt100_connected,
                    'vci_connected': vci_connected,
                    'enhancement_active': True,
                    'voltage_monitoring': self.bridge_config.monitoring_enabled if self.bridge_config else False
                }
                print("✅ Complete bridge setup successful - Enhanced diagnostics active")
                
            elif vci_connected and not gt100_connected:
                connection_result['status'] = 'PASS'
                connection_result['bridge_connected'] = True
                connection_result['details'] = {
                    'gt100_connected': False,
                    'vci_connected': vci_connected,
                    'enhancement_active': False,
                    'voltage_monitoring': False
                }
                print("✅ VCI connection successful - Standard diagnostics active")
                
            else:
                connection_result['details']['error'] = 'Failed to establish bridge connections'
                print("❌ Bridge setup failed")
                
        except Exception as e:
            logger.error(f"Bridge connection failed: {e}")
            connection_result['details']['error'] = str(e)
            
        return connection_result
        
    def _connect_gt100_plus_gpt(self) -> bool:
        """Connect GT100 PLUS GPT to vehicle OBDII"""
        try:
            # Scan for GT100 PLUS GPT devices
            if self.gt100_manager.scan_for_devices(timeout=15):
                time.sleep(2)  # Wait for scan completion
                
                devices = self.gt100_manager.available_devices
                if devices:
                    device = devices[0]  # Connect to first found device
                    if self.gt100_manager.connect_to_device(device):
                        logger.info(f"GT100 PLUS GPT connected: {device.name}")
                        return True
                        
            logger.warning("No GT100 PLUS GPT devices found")
            return False
            
        except Exception as e:
            logger.error(f"GT100 PLUS GPT connection failed: {e}")
            return False
            
    def _connect_primary_vci(self) -> bool:
        """Connect primary VCI device"""
        try:
            # Scan for primary VCI devices
            if self.primary_vci_manager.scan_for_devices(timeout=10):
                time.sleep(1)  # Wait for scan completion
                
                devices = self.primary_vci_manager.available_devices
                if devices:
                    device = devices[0]  # Connect to first found device
                    if self.primary_vci_manager.connect_to_device(device):
                        logger.info(f"Primary VCI connected: {device.name}")
                        return True
                        
            logger.warning("No primary VCI devices found")
            return False
            
        except Exception as e:
            logger.error(f"Primary VCI connection failed: {e}")
            return False
            
    def get_enhanced_diagnostics_status(self) -> Dict[str, Any]:
        """Get enhanced diagnostics status with GT100 PLUS GPT monitoring"""
        status = {
            'bridge_active': False,
            'enhancement_level': 'none',
            'voltage_status': {'input': 0, 'output': 0, 'current': 0},
            'vci_status': {'connected': False, 'type': 'none'},
            'protocol_detection': [],
            'warnings': []
        }
        
        try:
            # Check bridge connectivity
            gt100_connected = self.gt100_manager and self.gt100_manager.is_connected()
            vci_connected = self.primary_vci_manager and self.primary_vci_manager.is_connected()
            
            status['bridge_active'] = gt100_connected or vci_connected
            
            # Determine enhancement level
            if gt100_connected and vci_connected:
                status['enhancement_level'] = 'full'  # Full GT100 + VCI enhancement
            elif gt100_connected:
                status['enhancement_level'] = 'gt100_only'  # GT100 only
            elif vci_connected:
                status['enhancement_level'] = 'vci_only'  # VCI only
            else:
                status['enhancement_level'] = 'none'  # No connections
                
            # Get GT100 PLUS GPT status
            if gt100_connected:
                voltage_status = self.gt100_manager.get_voltage_status()
                status['voltage_status'] = voltage_status
                
                # Add voltage warnings
                if voltage_status['input_voltage'] < 11.0:
                    status['warnings'].append(f"Low input voltage: {voltage_status['input_voltage']:.1f}V")
                if voltage_status['input_voltage'] > 25.0:
                    status['warnings'].append(f"High input voltage: {voltage_status['input_voltage']:.1f}V")
                    
                # Get protocol detection
                protocols = self.gt100_manager.detect_protocols()
                status['protocol_detection'] = protocols
                
            # Get primary VCI status
            if vci_connected:
                vci_info = self.primary_vci_manager.get_device_info()
                status['vci_status'] = {
                    'connected': True,
                    'type': vci_info.get('type', 'Unknown'),
                    'name': vci_info.get('name', 'Unknown')
                }
                
        except Exception as e:
            logger.error(f"Failed to get enhanced diagnostics status: {e}")
            status['error'] = str(e)
            
        return status
        
    def monitor_bridge_operations(self, duration: int = 30) -> Dict[str, Any]:
        """Monitor bridge operations for specified duration"""
        monitoring_data = {
            'duration': duration,
            'samples': [],
            'voltage_events': [],
            'connection_events': [],
            'protocol_changes': []
        }
        
        start_time = time.time()
        last_voltage = None
        last_protocols = None
        
        print(f"📊 Monitoring bridge operations for {duration} seconds...")
        print("Press Ctrl+C to stop monitoring early")
        
        try:
            while time.time() - start_time < duration:
                current_time = time.time()
                elapsed = current_time - start_time
                
                # Get current status
                status = self.get_enhanced_diagnostics_status()
                
                # Sample data
                sample = {
                    'timestamp': elapsed,
                    'voltage_input': status['voltage_status']['input_voltage'],
                    'voltage_output': status['voltage_status']['output_voltage'],
                    'current_draw': status['voltage_status']['current_draw'],
                    'enhancement_level': status['enhancement_level'],
                    'vci_connected': status['vci_status']['connected'],
                    'protocols': status['protocol_detection']
                }
                monitoring_data['samples'].append(sample)
                
                # Detect voltage events
                if last_voltage != status['voltage_status']['input_voltage']:
                    if last_voltage is not None:
                        voltage_event = {
                            'time': elapsed,
                            'from': last_voltage,
                            'to': status['voltage_status']['input_voltage'],
                            'change': status['voltage_status']['input_voltage'] - last_voltage
                        }
                        monitoring_data['voltage_events'].append(voltage_event)
                    last_voltage = status['voltage_status']['input_voltage']
                    
                # Detect protocol changes
                current_protocols = set(status['protocol_detection'])
                if last_protocols != current_protocols and last_protocols is not None:
                    protocol_event = {
                        'time': elapsed,
                        'added': list(current_protocols - last_protocols),
                        'removed': list(last_protocols - current_protocols),
                        'current': list(current_protocols)
                    }
                    monitoring_data['protocol_changes'].append(protocol_event)
                last_protocols = current_protocols
                
                # Print status update
                print(f"[{elapsed:5.1f}s] V_in:{status['voltage_status']['input_voltage']:5.1f}V "
                      f"V_out:{status['voltage_status']['output_voltage']:5.1f}V "
                      f"I:{status['voltage_status']['current_draw']:5.3f}A "
                      f"Level:{status['enhancement_level']}")
                      
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(f"\n⏹️ Monitoring stopped early at {time.time() - start_time:.1f}s")
            monitoring_data['duration'] = time.time() - start_time
            
        # Generate summary
        if monitoring_data['samples']:
            voltages = [s['voltage_input'] for s in monitoring_data['samples'] if s['voltage_input'] > 0]
            currents = [s['current_draw'] for s in monitoring_data['samples'] if s['current_draw'] > 0]
            
            monitoring_data['summary'] = {
                'total_samples': len(monitoring_data['samples']),
                'voltage_range': {
                    'min': min(voltages) if voltages else 0,
                    'max': max(voltages) if voltages else 0,
                    'avg': sum(voltages) / len(voltages) if voltages else 0
                },
                'current_range': {
                    'min': min(currents) if currents else 0,
                    'max': max(currents) if currents else 0,
                    'avg': sum(currents) / len(currents) if currents else 0
                },
                'voltage_events_count': len(monitoring_data['voltage_events']),
                'protocol_changes_count': len(monitoring_data['protocol_changes'])
            }
            
        print(f"📊 Monitoring completed: {len(monitoring_data['samples'])} samples collected")
        return monitoring_data
        
    def demonstrate_vci_enhancement(self):
        """Demonstrate how GT100 PLUS GPT enhances any VCI device"""
        print("\n" + "=" * 70)
        print("🔧 GT100 PLUS GPT VCI Bridge Demonstration")
        print("=" * 70)
        print("Showing how GT100 PLUS GPT enhances ANY VCI device")
        
        # Example VCI devices that can be enhanced
        example_vcis = [
            {
                'name': 'OBDLink MX+',
                'enhancement': 'Voltage monitoring + Protocol LEDs + Battery backup'
            },
            {
                'name': 'Scanmatik 2 Pro',
                'enhancement': 'DOIP support + 24V conversion + All-keys-lost programming'
            },
            {
                'name': 'HH OBD Advance',
                'enhancement': 'Professional voltage monitoring + GPT programming mode'
            },
            {
                'name': 'Generic J2534',
                'enhancement': 'Full GT100 feature set + Banana plug access'
            }
        ]
        
        print("\nVCI Devices Enhanced by GT100 PLUS GPT:")
        for vci in example_vcis:
            print(f"• {vci['name']}: {vci['enhancement']}")
            
        print("\nBridge Architecture:")
        print("┌─────────────┐    ┌──────────────────┐    ┌─────────────┐    ┌─────────────────┐")
        print("│   Vehicle   │────│  GT100 PLUS GPT  │────│ VCI Device  │────│ Diagnostic SW   │")
        print("│   OBDII     │    │ (Enhancement)    │    │ (Any Type)  │    │ (Manufacturer)  │")
        print("└─────────────┘    └──────────────────┘    └─────────────┘    └─────────────────┘")
        print("                         │                        │")
        print("                    ┌────▼────┐              ┌───▼───┐")
        print("                    │Voltage  │              │Protocol│")
        print("                    │Monitor  │              │Detect │")
        print("                    │24V→12V  │              │LEDs   │")
        print("                    └─────────┘              └───────┘")
        
        # Simulate enhancement scenarios
        print("\nEnhancement Scenarios:")
        
        scenarios = [
            {
                'vehicle': 'BMW F30 (2019)',
                'vci': 'OBDLink MX+',
                'enhancement': 'DOIP diagnostics via GT100 Ethernet port',
                'benefit': 'Access to BMW ISTA/D full diagnostics'
            },
            {
                'vehicle': 'Ford F-350 Super Duty (24V)',
                'vci': 'Generic OBDII Scanner',
                'enhancement': '24V → 12V conversion + Voltage monitoring',
                'benefit': 'Safe diagnostics on heavy duty trucks'
            },
            {
                'vehicle': 'VW Golf MK7 (All Keys Lost)',
                'vci': 'VAGCOM Compatible Interface',
                'enhancement': 'Pin 16→Pin 1 shorting + Power backup',
                'benefit': 'Successful key programming without data loss'
            },
            {
                'vehicle': 'Toyota Camry (ECU Replacement)',
                'vci': 'Techstream Compatible Device',
                'enhancement': 'Pin 13→Pin 4 activation + GPT mode',
                'benefit': 'Direct ECU programming on bench'
            }
        ]
        
        for scenario in scenarios:
            print(f"\n🚗 {scenario['vehicle']}:")
            print(f"   VCI: {scenario['vci']}")
            print(f"   Enhancement: {scenario['enhancement']}")
            print(f"   Benefit: {scenario['benefit']}")
            
    def disconnect_bridge(self) -> bool:
        """Disconnect the complete bridge setup"""
        success = True
        
        try:
            # Disconnect GT100 PLUS GPT
            if self.gt100_manager and self.gt100_manager.is_connected():
                if self.gt100_manager.disconnect():
                    print("✅ GT100 PLUS GPT disconnected")
                else:
                    print("⚠️ GT100 PLUS GPT disconnection failed")
                    success = False
                    
            # Disconnect primary VCI
            if self.primary_vci_manager and self.primary_vci_manager.is_connected():
                if self.primary_vci_manager.disconnect():
                    print("✅ Primary VCI disconnected")
                else:
                    print("⚠️ Primary VCI disconnection failed")
                    success = False
                    
            if success:
                print("✅ Complete bridge disconnection successful")
            else:
                print("⚠️ Partial bridge disconnection")
                
        except Exception as e:
            logger.error(f"Bridge disconnection failed: {e}")
            success = False
            
        return success

def main():
    """Main demonstration function"""
    print("GoDiag GT100 PLUS GPT VCI Bridge")
    print("Enhanced diagnostics with ANY VCI device")
    print("=" * 50)
    
    # Create bridge instance
    bridge = GT100GPTVCIBridge()
    
    # Setup configuration
    config = bridge.setup_bridge_configuration(
        primary_vci_type="OBDLink MX+",
        vehicle_type="passenger",
        enable_monitoring=True,
        enable_programming=True
    )
    
    print(f"\nBridge Configuration:")
    print(f"• Primary VCI: {config.primary_vci_type}")
    print(f"• Vehicle Type: {config.vehicle_type}")
    print(f"• GT100 Enhancement: {config.gt100_enhancement}")
    print(f"• Voltage Monitoring: {config.monitoring_enabled}")
    print(f"• Programming Mode: {config.programming_mode}")
    
    # Demonstrate enhancement capabilities
    bridge.demonstrate_vci_enhancement()
    
    # Connect bridge
    connection_result = bridge.connect_bridge_setup()
    
    if connection_result['bridge_connected']:
        print(f"\n✅ Bridge connected successfully!")
        print(f"Enhancement Level: {connection_result['details'].get('enhancement_level', 'unknown')}")
        
        # Get status
        status = bridge.get_enhanced_diagnostics_status()
        print(f"\nEnhanced Diagnostics Status:")
        print(f"• Bridge Active: {status['bridge_active']}")
        print(f"• Enhancement Level: {status['enhancement_level']}")
        print(f"• VCI Connected: {status['vci_status']['connected']}")
        print(f"• Voltage Monitoring: {status['voltage_status']['input_voltage']:.1f}V input")
        
        if status['warnings']:
            print(f"• Warnings: {', '.join(status['warnings'])}")
            
        # Short monitoring session
        print(f"\n📊 Starting 10-second monitoring session...")
        monitoring_data = bridge.monitor_bridge_operations(duration=10)
        
        if monitoring_data.get('summary'):
            summary = monitoring_data['summary']
            print(f"\nMonitoring Summary:")
            print(f"• Samples: {summary['total_samples']}")
            print(f"• Voltage Range: {summary['voltage_range']['min']:.1f}V - {summary['voltage_range']['max']:.1f}V")
            print(f"• Current Range: {summary['current_range']['min']:.3f}A - {summary['current_range']['max']:.3f}A")
            
    else:
        print(f"\n⚠️ Bridge connection failed: {connection_result['details'].get('error', 'Unknown error')}")
        
    # Disconnect bridge
    print(f"\n🔌 Disconnecting bridge...")
    bridge.disconnect_bridge()
    
    print(f"\n🎉 GT100 PLUS GPT VCI Bridge demonstration completed!")
    print(f"\nKey Benefits Demonstrated:")
    print(f"• Works with ANY existing VCI device")
    print(f"• Provides professional diagnostic enhancement")
    print(f"• Real-time voltage and current monitoring")
    print(f"• Protocol detection and LED feedback")
    print(f"• Support for all vehicle types including 24V trucks")

if __name__ == "__main__":
    main()