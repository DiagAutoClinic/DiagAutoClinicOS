#!/usr/bin/env python3
"""
Chevrolet Cruze 2014 Live Testing Script
VIN: KL1JF6889EK617029
Odometer: 115315km

Comprehensive testing with GoDiag GT100 (J2534) + OBDLink MX+ (CAN Sniffer)
"""

import time
import logging
import sys
import os
from typing import List, Dict

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from AutoDiag.dual_device_engine import create_dual_device_engine, DiagnosticMode
from shared.obdlink_mxplus import create_obdlink_mxplus, OBDLinkProtocol

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CruzeTester:
    """Specialized tester for Chevrolet Cruze 2014"""
    
    def __init__(self, mock_mode: bool = True):
        self.mock_mode = mock_mode
        self.vehicle_info = {
            'make': 'Chevrolet',
            'model': 'Cruze',
            'year': '2014',
            'vin': 'KL1JF6889EK617029',
            'odo': '115315km',
            'engine': '1.6L/1.8L',
            'transmission': 'Manual/Automatic'
        }
        
        # Initialize dual-device engine
        self.engine = create_dual_device_engine(mock_mode=mock_mode)
        self.session_created = False
        
    def initialize_testing_environment(self) -> bool:
        """Initialize the complete testing environment"""
        print("=" * 60)
        print("CHEVROLET CRUZE 2014 LIVE TESTING SESSION")
        print("=" * 60)
        print(f"Vehicle: {self.vehicle_info['year']} {self.vehicle_info['make']} {self.vehicle_info['model']}")
        print(f"VIN: {self.vehicle_info['vin']}")
        print(f"Odometer: {self.vehicle_info['odo']}")
        print(f"Testing Mode: {'MOCK' if self.mock_mode else 'LIVE HARDWARE'}")
        print("=" * 60)
        
        try:
            # Create dual-device session
            print("\n1. Creating dual-device session...")
            if not self.engine.create_session(
                primary_device_name="GoDiag GT100 PLUS GPT",
                secondary_device_name="OBDLink MX+",
                mode=DiagnosticMode.SYNCHRONIZED
            ):
                print("[FAIL] Failed to create dual-device session")
                return False
            
            print("[OK] Dual-device session created")
            self.session_created = True
            
            # Connect both devices
            print("\n2. Connecting devices...")
            if not self.engine.connect_devices():
                print("[FAIL] Failed to connect devices")
                return False
            
            print("[OK] Both devices connected successfully")
            
            # Start synchronized monitoring
            print("\n3. Starting synchronized CAN monitoring...")
            if not self.engine.start_monitoring():
                print("[FAIL] Failed to start monitoring")
                return False
            
            print("[OK] CAN monitoring started")
            return True
            
        except Exception as e:
            print(f"[ERROR] Initialization failed: {e}")
            return False
    
    def run_comprehensive_diagnostics(self) -> Dict:
        """Run comprehensive diagnostic suite"""
        print("\n" + "=" * 60)
        print("COMPREHENSIVE DIAGNOSTIC SUITE")
        print("=" * 60)
        
        results = {}
        
        # Test 1: VIN Reading
        print("\n[Test 1] VIN Reading")
        vin_result = self.engine.perform_diagnostic_with_monitoring("read_vin")
        results['vin_reading'] = vin_result
        
        if vin_result.get('success'):
            captured_vin = vin_result.get('vin', '')
            expected_vin = self.vehicle_info['vin']
            
            print(f"   VIN Captured: {captured_vin}")
            print(f"   VIN Expected: {expected_vin}")
            
            if captured_vin == expected_vin:
                print("   [PASS] VIN matches expected")
            else:
                print("   [WARN] VIN mismatch (may be due to mock mode)")
        else:
            print(f"   [FAIL] VIN reading failed: {vin_result.get('error', 'Unknown error')}")
        
        print(f"   CAN Messages: {vin_result.get('can_monitoring', {}).get('messages_captured', 0)}")
        
        # Test 2: DTC Scanning
        print("\n[Test 2] DTC Scanning")
        dtc_result = self.engine.perform_diagnostic_with_monitoring("scan_dtcs")
        results['dtc_scanning'] = dtc_result
        
        if dtc_result.get('success'):
            dtcs = dtc_result.get('dtcs', [])
            print(f"   DTCs Found: {len(dtcs)}")
            for dtc in dtcs:
                print(f"   - {dtc[0]} ({dtc[1]}): {dtc[2]}")
        else:
            print(f"   [FAIL] DTC scanning failed: {dtc_result.get('error', 'Unknown error')}")
        
        print(f"   CAN Messages: {dtc_result.get('can_monitoring', {}).get('messages_captured', 0)}")
        
        # Test 3: ECU Information Reading
        print("\n[Test 3] ECU Information Reading")
        ecu_result = self.engine.perform_diagnostic_with_monitoring("read_ecu_info")
        results['ecu_info'] = ecu_result
        
        if ecu_result.get('success'):
            print("   [PASS] ECU information retrieved")
            print(f"   ECU Data: {ecu_result.get('ecu_data', 'N/A')[:50]}...")
        else:
            print(f"   [FAIL] ECU info reading failed: {ecu_result.get('error', 'Unknown error')}")
        
        print(f"   CAN Messages: {ecu_result.get('can_monitoring', {}).get('messages_captured', 0)}")
        
        return results
    
    def run_can_traffic_analysis(self, duration_seconds: int = 10) -> Dict:
        """Analyze CAN bus traffic patterns"""
        print(f"\n[CAN Analysis] Traffic Analysis ({duration_seconds}s)")
        print("-" * 40)
        
        # Clear buffer before analysis
        if self.engine.session:
            self.engine.session.can_buffer.clear()
        
        # Wait for traffic accumulation
        print("   Collecting CAN messages...")
        time.sleep(duration_seconds)
        
        # Get CAN statistics
        stats = self.engine.get_can_statistics()
        
        print(f"   Total Messages: {stats.get('total_messages', 0)}")
        print(f"   Recent Messages (10s): {stats.get('recent_messages_10s', 0)}")
        print(f"   Unique IDs: {stats.get('unique_ids', 0)}")
        print(f"   Messages/Second: {stats.get('messages_per_second', 0):.1f}")
        
        print("\n   Top Arbitration IDs:")
        top_ids = stats.get('top_arbitration_ids', {})
        for arb_id, count in list(top_ids.items())[:5]:
            print(f"   - {arb_id}: {count} messages")
        
        return stats
    
    def validate_gm_protocol_compatibility(self) -> Dict:
        """Validate GM/Chevrolet protocol compatibility"""
        print("\n[GM Protocol] Compatibility Check")
        print("-" * 40)
        
        validation_results = {}
        
        try:
            # Check OBDLink MX+ configuration
            if self.engine.session:
                secondary_device = self.engine.session.secondary_device
                
                # Check if Cruze profile is set
                profile_set = hasattr(secondary_device, 'current_vehicle_profile') and \
                             secondary_device.current_vehicle_profile is not None
                
                validation_results['profile_set'] = profile_set
                print(f"   Vehicle Profile: {'[OK]' if profile_set else '[NO]'}")
                
                # Check GM-specific arbitration IDs
                if profile_set:
                    arbitration_ids = secondary_device.current_vehicle_profile.get('arbitration_ids', {})
                    gm_categories = ['engine', 'transmission', 'brakes', 'steering', 'body', 'instrument', 'climate']
                    
                    for category in gm_categories:
                        has_ids = category in arbitration_ids and len(arbitration_ids[category]) > 0
                        validation_results[f'{category}_supported'] = has_ids
                        print(f"   {category.capitalize()}: {'[OK]' if has_ids else '[NO]'}")
                
                # Check protocol configuration
                protocol_configured = hasattr(secondary_device, 'current_protocol') and \
                                     secondary_device.current_protocol == OBDLinkProtocol.ISO15765_11BIT
                
                validation_results['protocol_configured'] = protocol_configured
                print(f"   Protocol: {'[OK]' if protocol_configured else '[NO]'}")
        
        except Exception as e:
            print(f"   [ERROR] Validation failed: {e}")
            validation_results['error'] = str(e)
        
        return validation_results
    
    def generate_test_report(self, diagnostic_results: Dict, can_stats: Dict, validation_results: Dict) -> str:
        """Generate comprehensive test report"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        report = f"""
CHEVROLET CRUZE 2014 LIVE TESTING REPORT
Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}
Test Session: {timestamp}

VEHICLE INFORMATION
==================
Make: {self.vehicle_info['make']}
Model: {self.vehicle_info['model']}
Year: {self.vehicle_info['year']}
VIN: {self.vehicle_info['vin']}
Odometer: {self.vehicle_info['odo']}
Engine: {self.vehicle_info['engine']}
Transmission: {self.vehicle_info['transmission']}

TESTING CONFIGURATION
====================
Mode: {'Mock Mode' if self.mock_mode else 'Live Hardware'}
Primary Device: GoDiag GD101 (J2534)
Secondary Device: OBDLink MX+ (CAN Sniffer)
Protocol: ISO15765-11BIT (GM/Chevrolet)

DIAGNOSTIC TEST RESULTS
=======================
"""
        
        # VIN Reading Results
        vin_result = diagnostic_results.get('vin_reading', {})
        report += f"""
VIN Reading:
- Status: {'PASS' if vin_result.get('success') else 'FAIL'}
- Captured VIN: {vin_result.get('vin', 'N/A')}
- Expected VIN: {self.vehicle_info['vin']}
- CAN Messages: {vin_result.get('can_monitoring', {}).get('messages_captured', 0)}
- Duration: {vin_result.get('can_monitoring', {}).get('duration_ms', 0)}ms
"""
        
        # DTC Scanning Results
        dtc_result = diagnostic_results.get('dtc_scanning', {})
        report += f"""
DTC Scanning:
- Status: {'PASS' if dtc_result.get('success') else 'FAIL'}
- DTCs Found: {len(dtc_result.get('dtcs', []))}
"""
        for dtc in dtc_result.get('dtcs', []):
            report += f"  - {dtc[0]} ({dtc[1]}): {dtc[2]}\n"
        
        report += f"""
- CAN Messages: {dtc_result.get('can_monitoring', {}).get('messages_captured', 0)}
- Duration: {dtc_result.get('can_monitoring', {}).get('duration_ms', 0)}ms
"""
        
        # ECU Info Results
        ecu_result = diagnostic_results.get('ecu_info', {})
        report += f"""
ECU Information:
- Status: {'PASS' if ecu_result.get('success') else 'FAIL'}
- ECU Data Available: {'Yes' if ecu_result.get('ecu_data') else 'No'}
- CAN Messages: {ecu_result.get('can_monitoring', {}).get('messages_captured', 0)}
- Duration: {ecu_result.get('can_monitoring', {}).get('duration_ms', 0)}ms
"""
        
        # CAN Traffic Analysis
        report += f"""
CAN TRAFFIC ANALYSIS
===================
Total Messages: {can_stats.get('total_messages', 0)}
Recent Messages (10s): {can_stats.get('recent_messages_10s', 0)}
Unique Arbitration IDs: {can_stats.get('unique_ids', 0)}
Messages Per Second: {can_stats.get('messages_per_second', 0):.1f}

Top Arbitration IDs:
"""
        top_ids = can_stats.get('top_arbitration_ids', {})
        for arb_id, count in list(top_ids.items())[:10]:
            report += f"- {arb_id}: {count} messages\n"
        
        # Protocol Validation
        report += f"""
GM PROTOCOL VALIDATION
=====================
Vehicle Profile Set: {'YES' if validation_results.get('profile_set') else 'NO'}
Protocol Configured: {'YES' if validation_results.get('protocol_configured') else 'NO'}
"""
        
        gm_categories = ['engine', 'transmission', 'brakes', 'steering', 'body', 'instrument', 'climate']
        for category in gm_categories:
            supported = validation_results.get(f'{category}_supported', False)
            report += f"{category.capitalize()}: {'SUPPORTED' if supported else 'NOT SUPPORTED'}\n"
        
        report += f"""
PERFORMANCE METRICS
==================
Connection Success: {'YES' if self.session_created else 'NO'}
CAN Monitoring: {'ACTIVE' if self.engine.is_monitoring else 'INACTIVE'}
Total Diagnostic Operations: {self.engine.get_metrics().get('diagnostic_operations', 0)}
Total CAN Messages Captured: {self.engine.get_metrics().get('messages_captured', 0)}
"""
        
        report += f"""
TESTING SUMMARY
===============
Overall Status: {'SUCCESS' if all([vin_result.get('success'), dtc_result.get('success')]) else 'PARTIAL'}
Protocol Compatibility: {'GOOD' if validation_results.get('profile_set') else 'NEEDS REVIEW'}
CAN Bus Monitoring: {'FUNCTIONAL' if can_stats.get('total_messages', 0) > 0 else 'NO TRAFFIC'}

NOTES
=====
- Test performed in {'mock' if self.mock_mode else 'live'} mode
- VIN matching may differ in mock mode
- Real hardware testing recommended for final validation
- CAN traffic analysis shows {'healthy' if can_stats.get('messages_per_second', 0) > 1 else 'low'} message rate

END OF REPORT
=============
"""
        
        return report
    
    def save_test_report(self, report_content: str) -> str:
        """Save test report to file"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"cruze_2014_test_report_{timestamp}.txt"
        
        filepath = filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return filepath
    
    def cleanup(self):
        """Cleanup and disconnect all devices"""
        print("\n[Cleanup] Disconnecting devices...")
        
        try:
            if self.engine:
                self.engine.stop_monitoring()
                self.engine.disconnect()
                print("[OK] All devices disconnected")
        except Exception as e:
            print(f"[ERROR] Cleanup failed: {e}")
    
    def run_full_test_suite(self) -> Dict:
        """Run the complete test suite"""
        results = {
            'initialization': False,
            'diagnostics': {},
            'can_analysis': {},
            'protocol_validation': {},
            'report_generated': False
        }
        
        try:
            # Initialize environment
            results['initialization'] = self.initialize_testing_environment()
            if not results['initialization']:
                return results
            
            # Run diagnostics
            results['diagnostics'] = self.run_comprehensive_diagnostics()
            
            # Analyze CAN traffic
            results['can_analysis'] = self.run_can_traffic_analysis()
            
            # Validate protocol compatibility
            results['protocol_validation'] = self.validate_gm_protocol_compatibility()
            
            # Generate and save report
            report_content = self.generate_test_report(
                results['diagnostics'], 
                results['can_analysis'], 
                results['protocol_validation']
            )
            
            report_file = self.save_test_report(report_content)
            results['report_file'] = report_file
            results['report_generated'] = True
            
            print(f"\n📄 Test report saved to: {report_file}")
            
            return results
            
        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            results['error'] = str(e)
            return results
        
        finally:
            self.cleanup()


def main():
    """Main function for Cruze testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Chevrolet Cruze 2014 Live Testing")
    parser.add_argument('--live', action='store_true', help='Use live hardware instead of mock mode')
    parser.add_argument('--duration', type=int, default=10, help='CAN traffic analysis duration in seconds')
    
    args = parser.parse_args()
    
    # Determine mode
    mock_mode = not args.live
    
    print("Chevrolet Cruze 2014 Live Testing")
    print("VIN: KL1JF6889EK617029 | Odometer: 115315km")
    print("=" * 50)
    
    if mock_mode:
        print("* Running in MOCK MODE (no real hardware required)")
        print("   Perfect for development and testing")
    else:
        print("+ Running in LIVE MODE (requires real hardware)")
        print("   GoDiag GD101 + OBDLink MX+ must be connected")
        print("   ! Ensure proper safety precautions")
    
    # Create tester
    tester = CruzeTester(mock_mode=mock_mode)
    
    # Run full test suite
    results = tester.run_full_test_suite()
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if results['initialization']:
        print("[OK] Environment initialized")
    else:
        print("[FAIL] Environment initialization failed")
    
    if results['diagnostics']:
        vin_success = results['diagnostics'].get('vin_reading', {}).get('success', False)
        dtc_success = results['diagnostics'].get('dtc_scanning', {}).get('success', False)
        
        print(f"{'[OK]' if vin_success else '[FAIL]'} VIN reading: {'PASS' if vin_success else 'FAIL'}")
        print(f"{'[OK]' if dtc_success else '[FAIL]'} DTC scanning: {'PASS' if dtc_success else 'FAIL'}")
    
    if results['can_analysis']:
        msg_count = results['can_analysis'].get('total_messages', 0)
        print(f"[OK] CAN traffic captured: {msg_count} messages")
    
    if results['protocol_validation']:
        profile_set = results['protocol_validation'].get('profile_set', False)
        print(f"{'[OK]' if profile_set else '[FAIL]'} GM protocol validation: {'PASS' if profile_set else 'FAIL'}")
    
    if results['report_generated']:
        print(f"[OK] Test report generated: {results['report_file']}")
    
    print("\nTesting completed successfully!")


if __name__ == "__main__":
    main()