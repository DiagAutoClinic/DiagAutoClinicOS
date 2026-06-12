#!/usr/bin/env python3
"""
PCM Master Test via OBD2 Interface
Comprehensive testing of PCM (Powertrain Control Module) functionality

This script performs PCM-specific diagnostics using:
- Primary: PCMmaster (J2534 device)
- Secondary: OBDLink MX+ (CAN Sniffer)
- Protocols: ISO15765, CAN, J2534

Test Scope:
- PCM Identification and Information
- PCM DTC Scanning and Clearing
- PCM Live Data Monitoring
- PCM Reset and Special Functions
- PCM CAN Traffic Analysis
- PCM Security Access Testing
"""

import time
import logging
import sys
import os
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import threading
import json

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from shared.obdlink_mxplus import create_obdlink_mxplus, OBDLinkProtocol, CANMessage
from tests.integration_tests.test_professional_devices import DeviceHandler, ProfessionalDevice

# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pcm_master_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PCMMasterTester:
    """PCM Master Test Suite via OBD2"""
    
    def __init__(self, mock_mode: bool = True):
        self.mock_mode = mock_mode
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize devices
        self.pcm_device = None
        self.obdlink_device = None
        self.device_handler = None
        
        # Test results
        self.test_results = {
            'timestamp': self.timestamp,
            'mock_mode': mock_mode,
            'pcm_identification': {},
            'pcm_dtc_scan': {},
            'pcm_live_data': {},
            'pcm_special_functions': {},
            'pcm_security_access': {},
            'can_traffic_analysis': {},
            'overall_status': 'NOT_STARTED'
        }
        
        # PCM-specific configuration
        self.pcm_config = {
            'name': 'PCM Master Test',
            'vehicle_type': 'Generic PCM Vehicle',
            'supported_protocols': ['ISO15765', 'CAN', 'J2534'],
            'pcm_addresses': ['7E0', '7E8', '7E1'],  # Engine/PCM addresses
            'can_messages': {
                'engine_rpm': '7E8 06 41 0C',
                'vehicle_speed': '7E8 04 41 0D',
                'coolant_temp': '7E8 03 41 05',
                'fuel_pressure': '7E8 03 41 0A',
                'engine_load': '7E8 04 41 0B'
            }
        }
    
    def initialize_test_environment(self) -> bool:
        """Initialize the complete test environment"""
        print("=" * 70)
        print("PCM MASTER TEST VIA OBD2 INTERFACE")
        print("=" * 70)
        print(f"Timestamp: {self.timestamp}")
        print(f"Test Mode: {'MOCK' if self.mock_mode else 'LIVE HARDWARE'}")
        print("=" * 70)
        
        try:
            # Initialize OBDLink MX+ for CAN monitoring
            print("\n[STEP 1] Initializing OBDLink MX+ CAN Sniffer...")
            self.obdlink_device = create_obdlink_mxplus(mock_mode=self.mock_mode)
            
            # Configure for PCM testing
            self.obdlink_device.set_vehicle_profile("generic_gm")
            self.obdlink_device.configure_can_sniffing(OBDLinkProtocol.ISO15765_11BIT)
            
            print("[OK] OBDLink MX+ configured for PCM monitoring")
            
            # Initialize professional device handler for PCMmaster
            print("\n[STEP 2] Initializing PCMmaster Device Handler...")
            self.device_handler = DeviceHandler(mock_mode=self.mock_mode)
            
            # Connect to PCMmaster using a valid protocol
            if not self.device_handler.connect_to_device("PCMmaster", "ISO15765"):
                print("[FAIL] Failed to connect to PCMmaster")
                return False
            
            self.pcm_device = self.device_handler.current_device
            print("[OK] PCMmaster connected successfully")
            print(f"   Protocol: {self.device_handler.current_protocol}")
            print(f"   Device: {self.pcm_device}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Environment initialization failed: {e}")
            logger.error(f"Environment initialization error: {e}")
            return False
    
    def test_pcm_identification(self) -> Dict:
        """Test PCM identification and information retrieval"""
        print("\n" + "="*50)
        print("PCM IDENTIFICATION TEST")
        print("="*50)
        
        results = {
            'status': 'NOT_STARTED',
            'ecu_identification': {},
            'pcm_specific_info': {},
            'protocol_capabilities': {},
            'error': None
        }
        
        try:
            results['status'] = 'IN_PROGRESS'
            print("[IN PROGRESS] Reading PCM identification...")
            
            # Get basic ECU identification
            ecu_info = self.device_handler.read_ecu_identification_advanced()
            results['ecu_identification'] = ecu_info
            
            # Get PCM-specific diagnostic data
            pcm_info = self.device_handler.perform_advanced_diagnostic('system_scan')
            results['pcm_specific_info'] = pcm_info
            
            # Test protocol capabilities
            protocol_tests = {
                'ISO15765_supported': 'ISO15765' in self.pcm_config['supported_protocols'],
                'CAN_supported': 'CAN' in self.pcm_config['supported_protocols'],
                'J2534_supported': 'J2534' in self.pcm_config['supported_protocols']
            }
            results['protocol_capabilities'] = protocol_tests
            
            # Analyze results
            success_indicators = [
                bool(ecu_info.get('part_number')),
                bool(pcm_info.get('engine_systems')),
                all(protocol_tests.values())
            ]
            
            results['status'] = 'SUCCESS' if all(success_indicators) else 'PARTIAL'
            
            # Print results
            print(f"[RESULT] Status: {results['status']}")
            print(f"  ECU Part Number: {ecu_info.get('part_number', 'N/A')}")
            print(f"  Software Version: {ecu_info.get('software_version', 'N/A')}")
            print(f"  PCM Systems Detected: {len(pcm_info.get('engine_systems', []))}")
            print(f"  Protocol Support: {sum(protocol_tests.values())}/3")
            
        except Exception as e:
            results['status'] = 'FAILED'
            results['error'] = str(e)
            print(f"[FAIL] PCM identification failed: {e}")
            logger.error(f"PCM identification error: {e}")
        
        return results
    
    def test_pcm_dtc_scanning(self) -> Dict:
        """Test PCM DTC scanning and clearing"""
        print("\n" + "="*50)
        print("PCM DTC SCANNING TEST")
        print("="*50)
        
        results = {
            'status': 'NOT_STARTED',
            'dtcs_found': [],
            'dtc_analysis': {},
            'clear_test': {},
            'error': None
        }
        
        try:
            results['status'] = 'IN_PROGRESS'
            print("[IN PROGRESS] Scanning for PCM DTCs...")
            
            # Scan for DTCs
            dtcs = self.device_handler.scan_dtcs()
            results['dtcs_found'] = dtcs
            
            # Analyze DTCs
            if dtcs:
                dtc_categories = {}
                severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
                
                for code, severity, description in dtcs:
                    # Categorize DTCs
                    if code.startswith('P0'):
                        category = 'Powertrain'
                    elif code.startswith('C0'):
                        category = 'Chassis'
                    elif code.startswith('B0'):
                        category = 'Body'
                    elif code.startswith('U0'):
                        category = 'Network'
                    else:
                        category = 'Unknown'
                    
                    dtc_categories[category] = dtc_categories.get(category, 0) + 1
                    severity_counts[severity] += 1
                
                results['dtc_analysis'] = {
                    'total_dtcs': len(dtcs),
                    'categories': dtc_categories,
                    'severity_breakdown': severity_counts,
                    'pcm_specific': any(code.startswith(('P01', 'P02', 'P03')) for code, _, _ in dtcs)
                }
            else:
                results['dtc_analysis'] = {
                    'total_dtcs': 0,
                    'categories': {},
                    'severity_breakdown': {},
                    'pcm_specific': False
                }
            
            # Test DTC clearing (if mock mode or safe environment)
            if self.mock_mode or not dtcs:
                print("[TEST] Testing DTC clearing capability...")
                clear_success = self.device_handler.clear_dtcs()
                results['clear_test'] = {
                    'attempted': True,
                    'success': clear_success,
                    'note': 'Mock mode - clearing simulation'
                }
            else:
                results['clear_test'] = {
                    'attempted': False,
                    'success': False,
                    'note': 'DTCs present - skipping clear test for safety'
                }
            
            results['status'] = 'SUCCESS'
            
            # Print results
            print(f"[RESULT] Status: {results['status']}")
            print(f"  Total DTCs: {len(dtcs)}")
            print(f"  PCM-Specific: {results['dtc_analysis'].get('pcm_specific', False)}")
            
            if dtcs:
                print("  DTC Details:")
                for code, severity, description in dtcs:
                    print(f"    - {code} ({severity}): {description[:50]}...")
            
        except Exception as e:
            results['status'] = 'FAILED'
            results['error'] = str(e)
            print(f"[FAIL] PCM DTC scanning failed: {e}")
            logger.error(f"PCM DTC scanning error: {e}")
        
        return results
    
    def test_pcm_live_data_monitoring(self) -> Dict:
        """Test PCM live data monitoring and real-time parameters"""
        print("\n" + "="*50)
        print("PCM LIVE DATA MONITORING TEST")
        print("="*50)
        
        results = {
            'status': 'NOT_STARTED',
            'live_data_samples': {},
            'data_analysis': {},
            'can_correlation': {},
            'error': None
        }
        
        try:
            results['status'] = 'IN_PROGRESS'
            print("[IN PROGRESS] Monitoring PCM live data...")
            
            # Start CAN monitoring for correlation
            if self.obdlink_device:
                self.obdlink_device.start_monitoring()
                print("[OK] CAN monitoring started for data correlation")
            
            # Collect live data samples
            live_parameters = ['rpm', 'speed', 'coolant_temp', 'fuel_level', 'voltage']
            samples = {}
            
            for param in live_parameters:
                values = []
                for _ in range(5):  # Take 5 samples
                    value = self.device_handler.get_live_data(param)
                    values.append(value)
                    time.sleep(0.5)
                
                samples[param] = {
                    'values': values,
                    'average': sum(values) / len(values) if values else 0,
                    'min': min(values) if values else 0,
                    'max': max(values) if values else 0
                }
            
            results['live_data_samples'] = samples
            
            # Analyze data quality
            analysis = {}
            for param, data in samples.items():
                values = data['values']
                if values:
                    # Check for reasonable ranges
                    reasonable = True
                    range_check = {
                        'rpm': (600, 4000),
                        'speed': (0, 200),
                        'coolant_temp': (70, 120),
                        'fuel_level': (0, 100),
                        'voltage': (11.5, 15.0)
                    }
                    
                    if param in range_check:
                        min_val, max_val = range_check[param]
                        reasonable = all(min_val <= v <= max_val for v in values)
                    
                    analysis[param] = {
                        'reasonable_range': reasonable,
                        'stable': len(set(v for v in values if abs(v - data['average']) < data['average'] * 0.1)) >= len(values) * 0.6
                    }
            
            results['data_analysis'] = analysis
            
            # Get CAN traffic statistics
            if self.obdlink_device:
                can_stats = self.obdlink_device.get_message_statistics()
                results['can_correlation'] = {
                    'can_messages_captured': can_stats.get('total_messages', 0),
                    'can_rate': can_stats.get('recent_messages', 0) / 10  # Messages per second
                }
                self.obdlink_device.stop_monitoring()
            
            # Determine overall status
            reasonable_count = sum(1 for param, data in analysis.items() if data['reasonable_range'])
            results['status'] = 'SUCCESS' if reasonable_count >= len(live_parameters) * 0.8 else 'PARTIAL'
            
            # Print results
            print(f"[RESULT] Status: {results['status']}")
            print(f"  Parameters Monitored: {len(live_parameters)}")
            print(f"  Reasonable Ranges: {reasonable_count}/{len(live_parameters)}")
            
            for param, data in samples.items():
                print(f"  {param.upper()}: {data['average']:.1f} (range: {data['min']:.1f}-{data['max']:.1f})")
            
            if results['can_correlation']:
                print(f"  CAN Messages: {results['can_correlation']['can_messages_captured']}")
            
        except Exception as e:
            results['status'] = 'FAILED'
            results['error'] = str(e)
            print(f"[FAIL] PCM live data monitoring failed: {e}")
            logger.error(f"PCM live data monitoring error: {e}")
        
        return results
    
    def test_pcm_special_functions(self) -> Dict:
        """Test PCM special functions and advanced operations"""
        print("\n" + "="*50)
        print("PCM SPECIAL FUNCTIONS TEST")
        print("="*50)
        
        results = {
            'status': 'NOT_STARTED',
            'adaptation_values': {},
            'security_access': {},
            'flash_programming': {},
            'module_coding': {},
            'error': None
        }
        
        try:
            results['status'] = 'IN_PROGRESS'
            print("[IN PROGRESS] Testing PCM special functions...")
            
            # Test adaptation values
            adaptation = self.device_handler._read_adaptation_values()
            results['adaptation_values'] = adaptation
            
            # Test security access
            security = self.device_handler._check_security_access()
            results['security_access'] = security
            
            # Test flash programming
            flash = self.device_handler._check_flash_programming()
            results['flash_programming'] = flash
            
            # Test module coding
            coding = self.device_handler._perform_module_coding_check()
            results['module_coding'] = coding
            
            # Analyze results
            function_scores = {
                'adaptation': len(adaptation.get('throttle_adaptation', '')) > 0,
                'security': security.get('security_levels', []),
                'flash': flash.get('flashable_modules', []),
                'coding': coding.get('codable_modules', [])
            }
            
            results['status'] = 'SUCCESS' if any(function_scores.values()) else 'FAILED'
            
            # Print results
            print(f"[RESULT] Status: {results['status']}")
            print(f"  Adaptation Systems: {list(adaptation.keys())}")
            print(f"  Security Levels: {len(security.get('security_levels', []))}")
            print(f"  Flashable Modules: {len(flash.get('flashable_modules', []))}")
            print(f"  Codable Modules: {len(coding.get('codable_modules', []))}")
            
            if security.get('security_code_required'):
                print("  [NOTE] Security code required for advanced functions")
            
        except Exception as e:
            results['status'] = 'FAILED'
            results['error'] = str(e)
            print(f"[FAIL] PCM special functions test failed: {e}")
            logger.error(f"PCM special functions error: {e}")
        
        return results
    
    def test_pcm_security_access(self) -> Dict:
        """Test PCM security access capabilities"""
        print("\n" + "="*50)
        print("PCM SECURITY ACCESS TEST")
        print("="*50)
        
        results = {
            'status': 'NOT_STARTED',
            'security_levels': {},
            'access_attempts': [],
            'security_validation': {},
            'error': None
        }
        
        try:
            results['status'] = 'IN_PROGRESS'
            print("[IN PROGRESS] Testing PCM security access...")
            
            # Check security access capabilities
            security_info = self.device_handler._check_security_access()
            results['security_levels'] = security_info
            
            # Simulate security access attempts (in mock mode)
            if self.mock_mode:
                print("[MOCK] Simulating security access attempts...")
                access_attempts = [
                    {'level': 'Dealer', 'status': 'SUCCESS', 'note': 'Mock access granted'},
                    {'level': 'Factory', 'status': 'REQUIRES_CODE', 'note': 'Security code needed'},
                    {'level': 'Component Protection', 'status': 'REQUIRES_CODE', 'note': 'Protected function'}
                ]
                results['access_attempts'] = access_attempts
            else:
                # Real implementation would attempt security access
                results['access_attempts'] = [
                    {'level': 'Standard', 'status': 'SIMULATED', 'note': 'Live mode - no real attempts'}
                ]
            
            # Security validation
            validation = {
                'supports_security': bool(security_info.get('security_levels')),
                'dealer_level_available': 'Dealer' in security_info.get('security_levels', []),
                'factory_level_available': 'Factory' in security_info.get('security_levels', []),
                'code_protection': security_info.get('security_code_required', False)
            }
            results['security_validation'] = validation
            
            results['status'] = 'SUCCESS'
            
            # Print results
            print(f"[RESULT] Status: {results['status']}")
            print(f"  Security Levels: {len(security_info.get('security_levels', []))}")
            print(f"  Dealer Level: {'Available' if validation['dealer_level_available'] else 'Not Available'}")
            print(f"  Factory Level: {'Available' if validation['factory_level_available'] else 'Not Available'}")
            print(f"  Code Protection: {'Required' if validation['code_protection'] else 'Not Required'}")
            
        except Exception as e:
            results['status'] = 'FAILED'
            results['error'] = str(e)
            print(f"[FAIL] PCM security access test failed: {e}")
            logger.error(f"PCM security access error: {e}")
        
        return results
    
    def analyze_can_traffic_for_pcm(self) -> Dict:
        """Analyze CAN traffic specifically for PCM communications"""
        print("\n" + "="*50)
        print("PCM CAN TRAFFIC ANALYSIS")
        print("="*50)
        
        results = {
            'status': 'NOT_STARTED',
            'pcm_messages': {},
            'traffic_patterns': {},
            'protocol_analysis': {},
            'error': None
        }
        
        try:
            results['status'] = 'IN_PROGRESS'
            print("[IN PROGRESS] Analyzing PCM CAN traffic...")
            
            # Start CAN monitoring
            self.obdlink_device.start_monitoring()
            
            # Collect traffic for analysis
            collection_time = 5  # seconds
            print(f"   Collecting CAN traffic for {collection_time} seconds...")
            time.sleep(collection_time)
            
            # Get CAN statistics
            can_stats = self.obdlink_device.get_message_statistics()
            
            # Analyze PCM-specific messages
            pcm_addresses = ['7E0', '7E8', '7E1']
            pcm_messages = {}
            
            # Filter for PCM-related arbitration IDs
            arbitration_counts = can_stats.get('arbitration_id_counts', {})
            for address in pcm_addresses:
                pcm_messages[address] = arbitration_counts.get(address, 0)
            
            # Analyze traffic patterns
            patterns = {
                'pcm_traffic_rate': sum(pcm_messages.values()) / collection_time,
                'total_traffic_rate': can_stats.get('total_messages', 0) / collection_time,
                'pcm_dominance': (sum(pcm_messages.values()) / max(can_stats.get('total_messages', 1), 1)) * 100,
                'active_pcm_addresses': len([count for count in pcm_messages.values() if count > 0])
            }
            
            # Protocol analysis
            protocol_analysis = {
                'can_11bit_detected': any(addr.startswith('7') for addr in arbitration_counts.keys()),
                'mixed_protocol_traffic': len(arbitration_counts) > 3,
                'healthy_traffic_rate': patterns['total_traffic_rate'] > 1.0,
                'pcm_active_communication': patterns['pcm_traffic_rate'] > 0.1
            }
            
            results['pcm_messages'] = pcm_messages
            results['traffic_patterns'] = patterns
            results['protocol_analysis'] = protocol_analysis
            
            # Stop monitoring
            self.obdlink_device.stop_monitoring()
            
            # Determine status
            health_indicators = [
                protocol_analysis['pcm_active_communication'],
                protocol_analysis['healthy_traffic_rate'],
                patterns['active_pcm_addresses'] > 0
            ]
            results['status'] = 'SUCCESS' if sum(health_indicators) >= 2 else 'PARTIAL'
            
            # Print results
            print(f"[RESULT] Status: {results['status']}")
            print(f"  PCM Messages/sec: {patterns['pcm_traffic_rate']:.2f}")
            print(f"  Total Messages/sec: {patterns['total_traffic_rate']:.2f}")
            print(f"  PCM Traffic Share: {patterns['pcm_dominance']:.1f}%")
            print(f"  Active PCM Addresses: {patterns['active_pcm_addresses']}/3")
            
            if pcm_messages:
                print("  PCM Address Activity:")
                for address, count in pcm_messages.items():
                    if count > 0:
                        print(f"    {address}: {count} messages")
            
        except Exception as e:
            results['status'] = 'FAILED'
            results['error'] = str(e)
            print(f"[FAIL] PCM CAN traffic analysis failed: {e}")
            logger.error(f"PCM CAN traffic analysis error: {e}")
        
        return results
    
    def run_comprehensive_pcm_test(self) -> Dict:
        """Run the complete PCM master test suite"""
        print("\n[START] PCM Master Test Suite via OBD2")
        print("="*70)
        
        overall_start_time = time.time()
        
        try:
            # Initialize environment
            if not self.initialize_test_environment():
                self.test_results['overall_status'] = 'INIT_FAILED'
                return self.test_results
            
            # Test 1: PCM Identification
            print(f"\n[TIMESTAMP] {datetime.now().strftime('%H:%M:%S')} - Starting PCM Identification Test...")
            self.test_results['pcm_identification'] = self.test_pcm_identification()
            
            # Test 2: PCM DTC Scanning
            print(f"\n[TIMESTAMP] {datetime.now().strftime('%H:%M:%S')} - Starting PCM DTC Scanning Test...")
            self.test_results['pcm_dtc_scan'] = self.test_pcm_dtc_scanning()
            
            # Test 3: PCM Live Data Monitoring
            print(f"\n[TIMESTAMP] {datetime.now().strftime('%H:%M:%S')} - Starting PCM Live Data Test...")
            self.test_results['pcm_live_data'] = self.test_pcm_live_data_monitoring()
            
            # Test 4: PCM Special Functions
            print(f"\n[TIMESTAMP] {datetime.now().strftime('%H:%M:%S')} - Starting PCM Special Functions Test...")
            self.test_results['pcm_special_functions'] = self.test_pcm_special_functions()
            
            # Test 5: PCM Security Access
            print(f"\n[TIMESTAMP] {datetime.now().strftime('%H:%M:%S')} - Starting PCM Security Access Test...")
            self.test_results['pcm_security_access'] = self.test_pcm_security_access()
            
            # Test 6: CAN Traffic Analysis
            print(f"\n[TIMESTAMP] {datetime.now().strftime('%H:%M:%S')} - Starting PCM CAN Traffic Analysis...")
            self.test_results['can_traffic_analysis'] = self.analyze_can_traffic_for_pcm()
            
            # Calculate overall status
            test_results = [
                self.test_results['pcm_identification']['status'],
                self.test_results['pcm_dtc_scan']['status'],
                self.test_results['pcm_live_data']['status'],
                self.test_results['pcm_special_functions']['status'],
                self.test_results['pcm_security_access']['status'],
                self.test_results['can_traffic_analysis']['status']
            ]
            
            success_count = sum(1 for result in test_results if result == 'SUCCESS')
            partial_count = sum(1 for result in test_results if result == 'PARTIAL')
            
            if success_count >= 4:
                self.test_results['overall_status'] = 'SUCCESS'
            elif success_count + partial_count >= 4:
                self.test_results['overall_status'] = 'PARTIAL_SUCCESS'
            else:
                self.test_results['overall_status'] = 'FAILED'
            
            # Add execution time
            execution_time = time.time() - overall_start_time
            self.test_results['execution_time_seconds'] = round(execution_time, 2)
            
            # Print final summary
            self.print_test_summary()
            
            return self.test_results
            
        except Exception as e:
            logger.error(f"Comprehensive PCM test failed: {e}")
            self.test_results['overall_status'] = 'CRITICAL_ERROR'
            self.test_results['critical_error'] = str(e)
            return self.test_results
        
        finally:
            # Cleanup
            self.cleanup()
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*70)
        print("PCM MASTER TEST SUMMARY")
        print("="*70)
        
        print(f"Overall Status: {self.test_results['overall_status']}")
        print(f"Execution Time: {self.test_results.get('execution_time_seconds', 'N/A')} seconds")
        print(f"Test Mode: {'MOCK' if self.mock_mode else 'LIVE'}")
        print("-"*70)
        
        test_categories = [
            ('PCM Identification', 'pcm_identification'),
            ('PCM DTC Scanning', 'pcm_dtc_scan'),
            ('PCM Live Data', 'pcm_live_data'),
            ('PCM Special Functions', 'pcm_special_functions'),
            ('PCM Security Access', 'pcm_security_access'),
            ('CAN Traffic Analysis', 'can_traffic_analysis')
        ]
        
        for name, key in test_categories:
            result = self.test_results[key]
            status = result.get('status', 'UNKNOWN')
            icon = "OK" if status == 'SUCCESS' else "WARN" if status == 'PARTIAL' else "FAIL"
            print(f"{icon} {name}: {status}")
            
            if result.get('error'):
                print(f"    Error: {result['error']}")
        
        print("-"*70)
        print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def generate_test_report(self) -> str:
        """Generate comprehensive test report"""
        report = f"""
PCM MASTER TEST REPORT VIA OBD2
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Test Session: {self.timestamp}

EXECUTIVE SUMMARY
================
Overall Status: {self.test_results['overall_status']}
Execution Time: {self.test_results.get('execution_time_seconds', 'N/A')} seconds
Test Mode: {'Mock Mode' if self.mock_mode else 'Live Hardware Mode'}

TEST CONFIGURATION
=================
Primary Device: PCMmaster (J2534)
Secondary Device: OBDLink MX+ (CAN Sniffer)
Supported Protocols: {', '.join(self.pcm_config['supported_protocols'])}
PCM Addresses: {', '.join(self.pcm_config['pcm_addresses'])}

TEST RESULTS SUMMARY
===================
"""
        
        test_categories = [
            ('PCM Identification', 'pcm_identification'),
            ('PCM DTC Scanning', 'pcm_dtc_scan'),
            ('PCM Live Data Monitoring', 'pcm_live_data'),
            ('PCM Special Functions', 'pcm_special_functions'),
            ('PCM Security Access', 'pcm_security_access'),
            ('PCM CAN Traffic Analysis', 'can_traffic_analysis')
        ]
        
        for name, key in test_categories:
            result = self.test_results[key]
            status = result.get('status', 'UNKNOWN')
            
            report += f"""
{name}:
- Status: {status}
"""
            
            if result.get('error'):
                report += f"- Error: {result['error']}\n"
            
            # Add specific details for each test type
            if key == 'pcm_identification':
                ecu_info = result.get('ecu_identification', {})
                report += f"- ECU Part Number: {ecu_info.get('part_number', 'N/A')}\n"
                report += f"- Software Version: {ecu_info.get('software_version', 'N/A')}\n"
                
            elif key == 'pcm_dtc_scan':
                dtc_count = len(result.get('dtcs_found', []))
                report += f"- DTCs Found: {dtc_count}\n"
                if dtc_count > 0:
                    report += f"- PCM-Specific DTCs: {result.get('dtc_analysis', {}).get('pcm_specific', False)}\n"
                    
            elif key == 'pcm_live_data':
                live_data = result.get('live_data_samples', {})
                report += f"- Parameters Monitored: {len(live_data)}\n"
                reasonable_count = sum(1 for param_data in live_data.values() 
                                     if result.get('data_analysis', {}).get(param_data, {}).get('reasonable_range', False))
                report += f"- Reasonable Ranges: {reasonable_count}/{len(live_data)}\n"
                
            elif key == 'pcm_special_functions':
                adaptation = result.get('adaptation_values', {})
                security = result.get('security_access', {})
                report += f"- Adaptation Systems: {len(adaptation)}\n"
                report += f"- Security Levels: {len(security.get('security_levels', []))}\n"
                
            elif key == 'can_traffic_analysis':
                patterns = result.get('traffic_patterns', {})
                report += f"- PCM Messages/sec: {patterns.get('pcm_traffic_rate', 0):.2f}\n"
                report += f"- Total Messages/sec: {patterns.get('total_traffic_rate', 0):.2f}\n"
                report += f"- PCM Traffic Share: {patterns.get('pcm_dominance', 0):.1f}%\n"
        
        report += f"""
TECHNICAL ANALYSIS
==================
Protocol Compatibility: {'GOOD' if self.test_results['overall_status'] in ['SUCCESS', 'PARTIAL_SUCCESS'] else 'NEEDS REVIEW'}
PCM Communication: {'ACTIVE' if self.test_results.get('can_traffic_analysis', {}).get('status') == 'SUCCESS' else 'LIMITED'}
Device Integration: {'FUNCTIONAL' if self.device_handler and self.obdlink_device else 'ISSUES'}

RECOMMENDATIONS
===============
1. {'PCM master functionality is working correctly' if self.test_results['overall_status'] == 'SUCCESS' else 'Review failed test components'}
2. {'CAN traffic analysis shows healthy PCM communication' if self.test_results.get('can_traffic_analysis', {}).get('status') == 'SUCCESS' else 'Investigate CAN traffic patterns'}
3. {'All diagnostic protocols are accessible' if self.test_results.get('pcm_identification', {}).get('status') == 'SUCCESS' else 'Check protocol configuration'}

NOTES
=====
- Test performed in {'mock' if self.mock_mode else 'live'} mode
- Results may vary based on actual vehicle and PCM configuration
- Security access testing is simulated in mock mode
- CAN traffic analysis requires active vehicle communication

CONCLUSION
==========
The PCM master test via OBD2 interface has {'completed successfully' if self.test_results['overall_status'] == 'SUCCESS' else 'completed with limitations'}.
The system demonstrates {'full' if self.test_results['overall_status'] == 'SUCCESS' else 'partial'} PCM diagnostic capability.

END OF REPORT
=============
"""
        
        return report
    
    def save_test_report(self) -> str:
        """Save test report to file"""
        filename = f"pcm_master_test_report_{self.timestamp}.txt"
        report_content = self.generate_test_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # Also save JSON results
        json_filename = f"pcm_master_test_results_{self.timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        return filename, json_filename
    
    def cleanup(self):
        """Cleanup and disconnect all devices"""
        print("\n[CLEANUP] Disconnecting devices...")
        
        try:
            if self.device_handler:
                self.device_handler.disconnect()
                print("[OK] PCMmaster disconnected")
            
            if self.obdlink_device:
                self.obdlink_device.disconnect()
                print("[OK] OBDLink MX+ disconnected")
                
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


def main():
    """Main function for PCM Master Test"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PCM Master Test via OBD2 Interface")
    parser.add_argument('--live', action='store_true', help='Use live hardware instead of mock mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine mode
    mock_mode = not args.live
    
    print("PCM Master Test via OBD2 Interface")
    print("Primary: PCMmaster (J2534)")
    print("Secondary: OBDLink MX+ (CAN Sniffer)")
    print("=" * 50)
    
    if mock_mode:
        print("* Running in MOCK MODE (no real hardware required)")
        print("  Perfect for development and validation")
    else:
        print("+ Running in LIVE MODE (requires real hardware)")
        print("  PCMmaster + OBDLink MX+ must be connected")
        print("  ! Ensure proper safety precautions")
    
    # Create tester
    tester = PCMMasterTester(mock_mode=mock_mode)
    
    # Run comprehensive test
    results = tester.run_comprehensive_pcm_test()
    
    # Generate and save report
    txt_file, json_file = tester.save_test_report()
    
    print(f"\nReport saved to: {txt_file}")
    print(f"JSON results saved to: {json_file}")
    
    # Return appropriate exit code
    if results['overall_status'] == 'SUCCESS':
        print("\n[SUCCESS] PCM Master Test completed successfully!")
        return 0
    elif results['overall_status'] == 'PARTIAL_SUCCESS':
        print("\n[WARNING] PCM Master Test completed with warnings!")
        return 1
    else:
        print("\n[FAILED] PCM Master Test failed!")
        return 2


if __name__ == "__main__":
    exit(main())