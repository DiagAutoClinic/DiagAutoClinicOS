#!/usr/bin/env python3
"""
GT100 Plus GPT VCI Connection Test Script
==========================================

Comprehensive test for establishing VCI connections using:
- GT100 Plus GPT (12V/24V power + passthru interface)
- GPT passthru device for J2534 communication
- Working ECU for protocol testing

Previous Issues Addressed:
- GT100 interface connection failures
- Power specification compliance
- N32G42x port detection problems
- ECU communication readiness
"""

import time
import logging
import serial
import usb.core
import usb.util
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json

class GT100GPTVCITester:
    def __init__(self):
        self.setup_logging()
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'hardware': {
                'gt100_plus_gpt': 'GoDiag GT100 Plus GPT',
                'passthru_device': 'GPT J2534 Passthru',
                'power_specs': '12V/24V adjustable'
            },
            'tests': []
        }
        
    def setup_logging(self):
        """Configure logging for the test session"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'gt100_gpt_vci_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def test_usb_connection(self) -> Dict:
        """Test connection to VCI device (USB/Bluetooth/ENET)"""
        test_result = {
            'test_name': 'VCI Device Connection Test',
            'status': 'FAIL',
            'details': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Check connection based on VCI type
            vci_type = self.detect_vci_type()
            
            if vci_type == 'USB':
                # Check for GoDiag USB device
                devices = usb.core.find(find_all=True)
                godiag_device = None
                
                for device in devices:
                    if device.idVendor == 0x1eab and device.idProduct == 0x9001:  # GoDiag VID/PID
                        godiag_device = device
                        break
                        
                if godiag_device:
                    test_result['status'] = 'PASS'
                    test_result['details'] = {
                        'vci_type': 'USB',
                        'vendor_id': hex(godiag_device.idVendor),
                        'product_id': hex(godiag_device.idProduct),
                        'manufacturer': usb.util.get_string(godiag_device, godiag_device.iManufacturer),
                        'product': usb.util.get_string(godiag_device, godiag_device.iProduct),
                        'serial_number': usb.util.get_string(godiag_device, godiag_device.iSerialNumber)
                    }
                    self.logger.info("GoDiag USB VCI device found and connected")
                else:
                    test_result['details']['error'] = 'GoDiag USB VCI device not found'
                    self.logger.warning("GoDiag USB VCI device not detected")
                    
            elif vci_type == 'BLUETOOTH':
                # Check Bluetooth connection
                if self.test_bluetooth_connection():
                    test_result['status'] = 'PASS'
                    test_result['details'] = {
                        'vci_type': 'BLUETOOTH',
                        'connection_status': 'Connected',
                        'device_name': self.get_bluetooth_device_name()
                    }
                    self.logger.info("Bluetooth VCI device connected")
                else:
                    test_result['details']['error'] = 'Bluetooth VCI device not connected'
                    
            elif vci_type == 'ENET':
                # Check ENET connection
                if self.test_enet_connection():
                    test_result['status'] = 'PASS'
                    test_result['details'] = {
                        'vci_type': 'ENET',
                        'connection_status': 'Connected',
                        'ip_address': self.get_enet_ip_address()
                    }
                    self.logger.info("ENET VCI device connected")
                else:
                    test_result['details']['error'] = 'ENET VCI device not connected'
                    
        except Exception as e:
            test_result['details']['error'] = str(e)
            self.logger.error(f"VCI connection test failed: {e}")
            
        self.test_results['tests'].append(test_result)
        return test_result
        
    def test_gt100_power_supply(self) -> Dict:
        """Test GT100 power supply functionality"""
        test_result = {
            'test_name': 'GT100 Power Supply Test',
            'status': 'FAIL',
            'details': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Test 12V power output
            voltage_target = 12.5
            current_target = 0.1
            
            # Simulated measurement (replace with actual ADC reading)
            measured_voltage = self.measure_output_voltage()
            measured_current = self.measure_output_current()
            
            voltage_ok = abs(measured_voltage - voltage_target) < 0.5
            current_ok = abs(measured_current - current_target) < 0.05
            
            test_result['status'] = 'PASS' if voltage_ok and current_ok else 'FAIL'
            test_result['details'] = {
                'target_voltage': voltage_target,
                'measured_voltage': measured_voltage,
                'voltage_status': 'OK' if voltage_ok else 'OUT_OF_RANGE',
                'target_current': current_target,
                'measured_current': measured_current,
                'current_status': 'OK' if current_ok else 'OUT_OF_RANGE'
            }
            
            self.logger.info(f"Power test: {measured_voltage}V @ {measured_current}A (Target: {voltage_target}V @ {current_target}A)")
            
        except Exception as e:
            test_result['details']['error'] = str(e)
            self.logger.error(f"Power supply test failed: {e}")
            
        self.test_results['tests'].append(test_result)
        return test_result
        
    def test_obd2_connection(self) -> Dict:
        """Test OBD2 16-pin connection and pin status"""
        test_result = {
            'test_name': 'OBD2 Connection Test',
            'status': 'FAIL',
            'details': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Check OBD2 pin status
            pin_status = self.check_obd2_pins()
            
            # Essential pins for communication
            essential_pins = {
                4: 'Ground',
                16: '+12V Power',
                6: 'CAN High',
                14: 'CAN Low'
            }
            
            critical_pins_ok = all(pin_status.get(pin) == 'OK' for pin in essential_pins.keys())
            
            test_result['status'] = 'PASS' if critical_pins_ok else 'FAIL'
            test_result['details'] = {
                'pin_status': pin_status,
                'essential_pins': essential_pins,
                'all_pins_ok': critical_pins_ok
            }
            
            self.logger.info(f"OBD2 pins status: {pin_status}")
            
        except Exception as e:
            test_result['details']['error'] = str(e)
            self.logger.error(f"OBD2 connection test failed: {e}")
            
        self.test_results['tests'].append(test_result)
        return test_result
        
    def test_j2534_passthru(self) -> Dict:
        """Test J2534 passthru functionality"""
        test_result = {
            'test_name': 'J2534 Passthru Test',
            'status': 'FAIL',
            'details': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Initialize J2534 passthru
            device_id = self.initialize_j2534_device()
            
            if device_id is not None:
                test_result['status'] = 'PASS'
                test_result['details'] = {
                    'device_id': device_id,
                    'protocols_supported': self.get_supported_protocols(),
                    'status': 'J2534 device initialized successfully'
                }
                self.logger.info(f"J2534 device initialized with ID: {device_id}")
            else:
                test_result['details']['error'] = 'Failed to initialize J2534 device'
                self.logger.error("J2534 initialization failed")
                
        except Exception as e:
            test_result['details']['error'] = str(e)
            self.logger.error(f"J2534 passthru test failed: {e}")
            
        self.test_results['tests'].append(test_result)
        return test_result
        
    def test_ecu_protocol_detection(self, ecu_type: str = "Generic") -> Dict:
        """Test ECU protocol detection and communication"""
        test_result = {
            'test_name': f'ECU Protocol Detection Test ({ecu_type})',
            'status': 'FAIL',
            'details': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Protocol detection sequence
            protocols_to_test = [
                'ISO 15765-4 CAN 11-bit 500kbps',
                'ISO 15765-4 CAN 29-bit 500kbps', 
                'ISO 14230-4 KWP2000',
                'ISO 9141-2',
                'J1850 PWM',
                'J1850 VPW'
            ]
            
            detected_protocols = []
            
            for protocol in protocols_to_test:
                if self.test_protocol_communication(protocol):
                    detected_protocols.append(protocol)
                    
            if detected_protocols:
                test_result['status'] = 'PASS'
                test_result['details'] = {
                    'ecu_type': ecu_type,
                    'detected_protocols': detected_protocols,
                    'primary_protocol': detected_protocols[0] if detected_protocols else None
                }
                self.logger.info(f"Protocols detected: {detected_protocols}")
            else:
                test_result['details']['error'] = 'No protocols detected'
                self.logger.warning("No ECU protocols detected")
                
        except Exception as e:
            test_result['details']['error'] = str(e)
            self.logger.error(f"Protocol detection test failed: {e}")
            
        self.test_results['tests'].append(test_result)
        return test_result
        
    def test_diagnostic_session(self) -> Dict:
        """Test establishing diagnostic session"""
        test_result = {
            'test_name': 'Diagnostic Session Test',
            'status': 'FAIL',
            'details': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Try to establish diagnostic session
            session_established = self.establish_diagnostic_session()
            
            if session_established:
                # Test basic diagnostic services
                supported_pids = self.get_supported_pids()
                ecu_info = self.get_ecu_information()
                
                test_result['status'] = 'PASS'
                test_result['details'] = {
                    'session_established': True,
                    'supported_pids_count': len(supported_pids),
                    'ecu_info': ecu_info
                }
                self.logger.info(f"Diagnostic session established. ECU info: {ecu_info}")
            else:
                test_result['details']['error'] = 'Failed to establish diagnostic session'
                self.logger.error("Diagnostic session establishment failed")
                
        except Exception as e:
            test_result['details']['error'] = str(e)
            self.logger.error(f"Diagnostic session test failed: {e}")
            
        self.test_results['tests'].append(test_result)
        return test_result
        
    def run_comprehensive_test(self, ecu_type: str = "Generic") -> Dict:
        """Run all VCI connection tests"""
        self.logger.info("Starting GT100 Plus GPT VCI Connection Test Suite")
        self.logger.info(f"Test ECU Type: {ecu_type}")
        
        # Test sequence
        tests = [
            self.test_usb_connection,
            self.test_gt100_power_supply,
            self.test_obd2_connection,
            self.test_j2534_passthru,
            lambda: self.test_ecu_protocol_detection(ecu_type),
            self.test_diagnostic_session
        ]
        
        for test_func in tests:
            try:
                result = test_func()
                self.logger.info(f"Test completed: {result['test_name']} - {result['status']}")
            except Exception as e:
                self.logger.error(f"Test failed with exception: {test_func.__name__} - {e}")
                
        # Generate summary
        self.generate_test_summary()
        
        return self.test_results
        
    def generate_test_summary(self):
        """Generate test summary and save report"""
        passed = sum(1 for test in self.test_results['tests'] if test['status'] == 'PASS')
        failed = sum(1 for test in self.test_results['tests'] if test['status'] == 'FAIL')
        total = len(self.test_results['tests'])
        
        self.test_results['summary'] = {
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'success_rate': f"{(passed/total*100):.1f}%" if total > 0 else "0%"
        }
        
        # Save detailed report
        report_file = f"gt100_gpt_vci_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
            
        self.logger.info(f"Test Summary: {passed}/{total} tests passed ({self.test_results['summary']['success_rate']})")
        self.logger.info(f"Detailed report saved to: {report_file}")
        
    # Mock methods - replace with actual hardware interface
    def detect_vci_type(self) -> str:
        """Detect VCI type connected to GT100"""
        # Check USB devices first
        try:
            devices = usb.core.find(find_all=True)
            for device in devices:
                if device.idVendor == 0x1eab and device.idProduct == 0x9001:
                    return 'USB'
        except:
            pass
            
        # Check for Bluetooth devices
        try:
            if self.test_bluetooth_connection():
                return 'BLUETOOTH'
        except:
            pass
            
        # Check for ENET devices
        try:
            if self.test_enet_connection():
                return 'ENET'
        except:
            pass
            
        return 'UNKNOWN'
        
    def test_bluetooth_connection(self) -> bool:
        """Mock method - replace with actual Bluetooth testing"""
        return True  # Simulated connection
        
    def get_bluetooth_device_name(self) -> str:
        """Mock method - replace with actual device name retrieval"""
        return "GoDiag GD101 Bluetooth"
        
    def test_enet_connection(self) -> bool:
        """Mock method - replace with actual ENET testing"""
        return True  # Simulated connection
        
    def get_enet_ip_address(self) -> str:
        """Mock method - replace with actual IP retrieval"""
        return "192.168.1.100"
        
    def measure_output_voltage(self) -> float:
        """Mock method - replace with actual voltage measurement"""
        return 12.4  # Simulated voltage
        
    def measure_output_current(self) -> float:
        """Mock method - replace with actual current measurement"""
        return 0.095  # Simulated current
        
    def check_obd2_pins(self) -> Dict[int, str]:
        """Mock method - replace with actual pin status checking"""
        return {
            1: 'Reserved',
            2: 'SAE J1850 Bus+',
            3: 'Chassis Ground',
            4: 'Engine Ground',
            5: 'Signal Ground',
            6: 'CAN High',
            7: 'ISO 9141-2 K Line',
            10: 'SAE J1850 Bus-',
            14: 'CAN Low',
            15: 'ISO 9141-2 L Line',
            16: '+12V Power'
        }
        
    def initialize_j2534_device(self) -> Optional[int]:
        """Mock method - replace with actual J2534 initialization"""
        return 1  # Mock device ID
        
    def get_supported_protocols(self) -> List[str]:
        """Mock method - replace with actual protocol detection"""
        return [
            'ISO 15765-4 CAN 11-bit 500kbps',
            'ISO 14230-4 KWP2000',
            'ISO 9141-2'
        ]
        
    def test_protocol_communication(self, protocol: str) -> bool:
        """Mock method - replace with actual protocol testing"""
        # Simulate successful protocol detection for some protocols
        return protocol in ['ISO 15765-4 CAN 11-bit 500kbps', 'ISO 14230-4 KWP2000']
        
    def establish_diagnostic_session(self) -> bool:
        """Mock method - replace with actual diagnostic session establishment"""
        return True  # Simulated success
        
    def get_supported_pids(self) -> List[int]:
        """Mock method - replace with actual PID query"""
        return [0x01, 0x02, 0x03, 0x04, 0x05, 0x0C, 0x0D, 0x0F, 0x11]
        
    def get_ecu_information(self) -> Dict:
        """Mock method - replace with actual ECU info retrieval"""
        return {
            'ecu_name': 'Engine Control Unit',
            'protocol': 'ISO 15765-4 CAN',
            'address': '0x7E0'
        }

def main():
    """Main test execution"""
    print("GT100 Plus GPT VCI Connection Test")
    print("=" * 50)
    
    # Initialize tester
    tester = GT100GPTVCITester()
    
    # Get VCI type from user
    print("\nSelect VCI Type connected to GT100:")
    print("1. USB VCI (GoDiag GD101, etc.)")
    print("2. Bluetooth VCI (OBDLink MX+, etc.)")
    print("3. ENET VCI (Direct Ethernet)")
    print("4. Auto-detect")
    
    vci_choice = input("\nEnter choice (1-4): ").strip()
    
    if vci_choice == '1':
        print("\nUsing USB VCI - connect to OBDII female connector on GT100")
    elif vci_choice == '2':
        print("\nUsing Bluetooth VCI - pair device first, then connect to GT100")
    elif vci_choice == '3':
        print("\nUsing ENET VCI - ensure IP connectivity to device")
    else:
        print("\nAuto-detecting VCI type...")
    
    # Get ECU type from user
    ecu_type = input("\nEnter ECU type (or press Enter for Generic): ").strip()
    if not ecu_type:
        ecu_type = "Generic"
    
    print(f"\nStarting test with VCI type and ECU type: {ecu_type}")
    print("Test sequence: VCI Connection -> Power -> OBD2 -> Protocol -> Diagnostics")
    print("\nEnsure your setup is correct:")
    print("- PC -> VCI Device (USB/Bluetooth/ENET)")
    print("- VCI Device -> GT100 (OBDII female connector)")
    print("- ECU -> GT100 (25-pin port or ethernet to male OBDII)")
    print("- GT100 -> 12V Power Supply")
    
    # Run comprehensive test
    results = tester.run_comprehensive_test(ecu_type)
    
    # Display summary
    summary = results['summary']
    print(f"\nTest Summary:")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success Rate: {summary['success_rate']}")
    
    if summary['failed'] == 0:
        print("\n✅ All tests passed! VCI connection established successfully.")
        print("\nNext steps:")
        print("- ECU communication is ready")
        print("- You can now run diagnostic functions")
        print("- Test with specific ECU protocols as needed")
    else:
        print(f"\n⚠️  {summary['failed']} test(s) failed. Check the log file for details.")
        print("\nTroubleshooting:")
        print("- Verify VCI device is properly connected to GT100")
        print("- Check GT100 power supply (12V/24V)")
        print("- Ensure ECU connections are secure")
        print("- Try different VCI type if auto-detection failed")

if __name__ == "__main__":
    main()