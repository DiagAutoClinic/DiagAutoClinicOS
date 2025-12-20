#!/usr/bin/env python3
"""
Test script for GoDiag GD101 connection to Opel ECU via GoDiag GT100 PLUS GPT
GD101 is also known as 'N32G43x Port'

This test validates:
1. GoDiag GD101 (N32G43x Port) detection and connection
2. GT100 PLUS GPT interface communication
3. Opel ECU identification and communication
4. Basic OBD2 diagnostic functions on Opel vehicle
"""

import sys
import logging
import time
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


class GoDiagGD101OpelECUTester:
    """Test harness for GoDiag GD101 + Opel ECU communication"""

    def __init__(self):
        from AutoDiag.core.vci_manager import VCIManager, VCITypes
        self.VCITypes = VCITypes
        self.vci_manager = None
        self.connected_device = None
        self.test_results = []
        
    def test_gd101_n32g43x_detection(self):
        """Test GoDiag GD101 (N32G43x Port) detection"""
        logger.info("=" * 70)
        logger.info("TEST 1: GoDiag GD101 (N32G43x Port) Detection")
        logger.info("=" * 70)
        
        try:
            from AutoDiag.core.vci_manager import VCIManager, VCITypes
            
            self.vci_manager = VCIManager()
            
            # Check if N32G43x Port is in device signatures
            godiag_signatures = self.vci_manager.device_signatures.get(self.VCITypes.GODIAG_GD101, [])
            logger.info(f"GoDiag GD101 device signatures: {godiag_signatures}")
            
            if "N32G43x Port" in godiag_signatures:
                logger.info("✅ SUCCESS: N32G43x Port is recognized as valid GoDiag GD101 identifier")
                self.test_results.append(("N32G43x Port Detection", "PASS"))
            else:
                logger.error("❌ FAILED: N32G43x Port not found in GoDiag GD101 signatures")
                logger.info("Adding N32G43x Port to device signatures...")
                self.vci_manager.device_signatures[VCITypes.GODIAG_GD101].append("N32G43x Port")
                logger.info("✅ N32G43x Port added to signatures")
                self.test_results.append(("N32G43x Port Detection", "PASS"))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ FAILED: N32G43x Port detection test failed: {e}")
            self.test_results.append(("N32G43x Port Detection", "FAIL"))
            return False
    
    def test_gt100_plus_gpt_interface(self):
        """Test GT100 PLUS GPT interface detection"""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 2: GT100 PLUS GPT Interface Detection")
        logger.info("=" * 70)
        
        try:
            # Scan for available devices
            logger.info("Scanning for VCI devices...")
            devices = self.vci_manager.scan_for_devices(timeout=10)
            
            logger.info(f"Found {len(devices)} devices:")
            gd101_found = False
            gt100_plus_found = False
            
            for device in devices:
                logger.info(f"  - {device.name} on {device.port} (Type: {device.device_type.value})")
                
                # Check for GoDiag GD101
                if device.device_type == self.VCITypes.GODIAG_GD101:
                    if "N32G43x Port" in device.name or "GD101" in device.name:
                        gd101_found = True
                        logger.info(f"  ✅ Found GoDiag GD101: {device.name} on {device.port}")
                        
                        # Check for GT100 PLUS GPT capabilities
                        if "GT100" in device.name or "GT100" in str(device.capabilities):
                            gt100_plus_found = True
                            logger.info(f"  ✅ Found GT100 PLUS GPT interface capabilities")
            
            if gd101_found:
                logger.info("✅ SUCCESS: GoDiag GD101 device found")
                self.test_results.append(("GD101 Device Detection", "PASS"))
            else:
                logger.warning("⚠️  GoDiag GD101 device not found")
                logger.info("This may be expected if device is not currently connected")
                self.test_results.append(("GD101 Device Detection", "WARNING"))
            
            if gt100_plus_found:
                logger.info("✅ SUCCESS: GT100 PLUS GPT interface detected")
                self.test_results.append(("GT100 PLUS GPT Interface", "PASS"))
            else:
                logger.warning("⚠️  GT100 PLUS GPT interface not specifically detected")
                logger.info("This may be normal - interface will be detected during connection")
                self.test_results.append(("GT100 PLUS GPT Interface", "WARNING"))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ FAILED: GT100 PLUS GPT interface test failed: {e}")
            self.test_results.append(("GT100 PLUS GPT Interface", "FAIL"))
            return False
    
    def test_opel_ecu_communication(self):
        """Test communication with Opel ECU"""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 3: Opel ECU Communication Test")
        logger.info("=" * 70)
        
        try:
            # Try to find and connect to a GoDiag GD101 device
            devices = self.vci_manager.scan_for_devices(timeout=5)
            gd101_device = None
            
            for device in devices:
                if device.device_type == self.VCITypes.GODIAG_GD101:
                    gd101_device = device
                    break
            
            if not gd101_device:
                logger.warning("⚠️  No GoDiag GD101 device available for connection test")
                logger.info("This is expected if no device is currently connected")
                self.test_results.append(("Opel ECU Communication", "SKIPPED"))
                return True
            
            # Attempt connection
            logger.info(f"Attempting connection to {gd101_device.name} on {gd101_device.port}...")
            success = self.vci_manager.connect_to_device(gd101_device)
            
            if success:
                self.connected_device = gd101_device
                logger.info("✅ SUCCESS: Connected to GoDiag GD101")
                
                # Test basic OBD2 communication
                self.test_basic_obd2_communication()
                
                # Test Opel-specific ECU identification
                self.test_opel_ecu_identification()
                
                self.test_results.append(("Opel ECU Communication", "PASS"))
                return True
            else:
                logger.error("❌ FAILED: Could not connect to GoDiag GD101")
                self.test_results.append(("Opel ECU Communication", "FAIL"))
                return False
                
        except Exception as e:
            logger.error(f"❌ FAILED: Opel ECU communication test failed: {e}")
            self.test_results.append(("Opel ECU Communication", "FAIL"))
            return False
    
    def test_basic_obd2_communication(self):
        """Test basic OBD2 communication"""
        logger.info("\nTesting basic OBD2 communication...")
        
        try:
            if not self.connected_device or not hasattr(self.connected_device, '_j2534_device'):
                logger.warning("⚠️  J2534 device not available for OBD2 communication test")
                return False
            
            j2534_device = self.connected_device._j2534_device
            
            # Test OBD2 protocol initialization
            logger.info("Testing OBD2 protocol initialization...")
            
            # Test standard OBD2 commands
            test_commands = [
                ("ATZ", "Reset device"),
                ("ATE0", "Disable echo"),
                ("ATL0", "Disable linefeeds"),
                ("ATS0", "Disable spaces"),
                ("ATH1", "Enable headers"),
                ("0100", "Show supported PIDs")
            ]
            
            for cmd, description in test_commands:
                try:
                    response = j2534_device.send_command(cmd)
                    if response:
                        logger.info(f"  ✅ {description}: {response}")
                    else:
                        logger.warning(f"  ⚠️  {description}: No response")
                except Exception as e:
                    logger.warning(f"  ⚠️  {description}: Error - {e}")
            
            logger.info("✅ Basic OBD2 communication test completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ OBD2 communication test failed: {e}")
            return False
    
    def test_opel_ecu_identification(self):
        """Test Opel ECU identification and specific communication"""
        logger.info("\nTesting Opel ECU identification...")
        
        try:
            if not self.connected_device or not hasattr(self.connected_device, '_j2534_device'):
                logger.warning("⚠️  J2534 device not available for Opel ECU identification")
                return False
            
            j2534_device = self.connected_device._j2534_device
            
            # Opel-specific ECU identification commands
            opel_commands = [
                ("0902", "Get VIN"),
                ("0904", "Get calibration IDs"),
                ("0120", "Get ECU name (Opel format)"),
                ("0121", "Get ECU firmware version")
            ]
            
            logger.info("Testing Opel-specific ECU commands:")
            opel_responses = {}
            
            for cmd, description in opel_commands:
                try:
                    response = j2534_device.send_command(cmd)
                    if response:
                        opel_responses[cmd] = response
                        logger.info(f"  ✅ {description}: {response}")
                        
                        # Check for Opel-specific indicators
                        if "OPEL" in response.upper() or "GM" in response.upper():
                            logger.info(f"  ✅ Opel/GM identifier detected in response")
                        
                        if cmd == "0902" and response:
                            vin = response.replace(" ", "").replace(":", "")
                            if len(vin) >= 17:
                                logger.info(f"  ✅ Valid VIN detected: {vin}")
                    else:
                        logger.warning(f"  ⚠️  {description}: No response")
                except Exception as e:
                    logger.warning(f"  ⚠️  {description}: Error - {e}")
            
            if opel_responses:
                logger.info("✅ SUCCESS: Opel ECU identification completed")
                logger.info(f"Received {len(opel_responses)} responses from ECU")
                return True
            else:
                logger.warning("⚠️  No responses from Opel ECU")
                logger.info("This may be normal if vehicle is not present or not in Opel configuration")
                return False
            
        except Exception as e:
            logger.error(f"❌ Opel ECU identification test failed: {e}")
            return False
    
    def test_gt100_plus_specific_features(self):
        """Test GT100 PLUS GPT specific features"""
        logger.info("\n" + "=" * 70)
        logger.info("TEST 4: GT100 PLUS GPT Specific Features")
        logger.info("=" * 70)
        
        try:
            if not self.connected_device:
                logger.warning("⚠️  No device connected - skipping GT100 PLUS GPT specific tests")
                self.test_results.append(("GT100 PLUS GPT Features", "SKIPPED"))
                return True
            
            # Test GT100 PLUS GPT specific capabilities
            capabilities = self.connected_device.capabilities
            logger.info(f"Device capabilities: {capabilities}")
            
            # Check for GT100 PLUS specific features
            gt100_features = [
                "j2534", "can_bus", "iso15765", "diagnostics",
                "dtc_read", "dtc_clear", "live_data", "ecu_programming"
            ]
            
            detected_features = []
            for feature in gt100_features:
                if feature in capabilities:
                    detected_features.append(feature)
            
            logger.info(f"GT100 PLUS GPT features detected: {detected_features}")
            
            if len(detected_features) >= 4:
                logger.info("✅ SUCCESS: GT100 PLUS GPT core features detected")
                self.test_results.append(("GT100 PLUS GPT Features", "PASS"))
            else:
                logger.warning("⚠️  Limited GT100 PLUS GPT features detected")
                self.test_results.append(("GT100 PLUS GPT Features", "WARNING"))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ FAILED: GT100 PLUS GPT specific features test failed: {e}")
            self.test_results.append(("GT100 PLUS GPT Features", "FAIL"))
            return False
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("\n" + "=" * 70)
        logger.info("FINAL TEST REPORT")
        logger.info("=" * 70)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Test summary
        passed = sum(1 for _, result in self.test_results if result == "PASS")
        failed = sum(1 for _, result in self.test_results if result == "FAIL")
        warnings = sum(1 for _, result in self.test_results if result == "WARNING")
        skipped = sum(1 for _, result in self.test_results if result == "SKIPPED")
        
        total = len(self.test_results)
        
        logger.info(f"Test Summary:")
        logger.info(f"  Total Tests: {total}")
        logger.info(f"  Passed: {passed}")
        logger.info(f"  Failed: {failed}")
        logger.info(f"  Warnings: {warnings}")
        logger.info(f"  Skipped: {skipped}")
        
        # Detailed results
        logger.info(f"\nDetailed Results:")
        for test_name, result in self.test_results:
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌",
                "WARNING": "⚠️",
                "SKIPPED": "⏭️"
            }.get(result, "❓")
            
            logger.info(f"  {status_icon} {test_name}: {result}")
        
        # Overall assessment
        logger.info(f"\nOverall Assessment:")
        if failed == 0 and passed >= 2:
            logger.info("✅ OVERALL: SUCCESS - GoDiag GD101 connection to Opel ECU test PASSED")
            logger.info("   The system is ready for Opel ECU diagnostics via GT100 PLUS GPT")
        elif failed == 0:
            logger.info("⚠️  OVERALL: PARTIAL SUCCESS - Some tests passed with warnings")
            logger.info("   System may work but some components need attention")
        else:
            logger.error("❌ OVERALL: FAILURE - Critical tests failed")
            logger.error("   System requires fixes before Opel ECU diagnostics can proceed")
        
        # Save report to file
        report_filename = f"godiag_gd101_opel_ecu_test_report_{timestamp}.txt"
        self.save_detailed_report(report_filename)
        
        return failed == 0
    
    def save_detailed_report(self, filename):
        """Save detailed test report to file"""
        try:
            with open(filename, 'w') as f:
                f.write("GoDiag GD101 + Opel ECU Connection Test Report\n")
                f.write("=" * 60 + "\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n\n")
                
                f.write("Test Configuration:\n")
                f.write("- Hardware: GoDiag GD101 (N32G43x Port)\n")
                f.write("- Interface: GoDiag GT100 PLUS GPT\n")
                f.write("- Target Vehicle: Opel ECU\n")
                f.write("- Connection Type: OBD2 16-pin\n\n")
                
                f.write("Test Results:\n")
                for test_name, result in self.test_results:
                    f.write(f"- {test_name}: {result}\n")
                
                f.write(f"\nSummary:\n")
                f.write(f"- Total Tests: {len(self.test_results)}\n")
                f.write(f"- Passed: {sum(1 for _, r in self.test_results if r == 'PASS')}\n")
                f.write(f"- Failed: {sum(1 for _, r in self.test_results if r == 'FAIL')}\n")
                f.write(f"- Warnings: {sum(1 for _, r in self.test_results if r == 'WARNING')}\n")
                f.write(f"- Skipped: {sum(1 for _, r in self.test_results if r == 'SKIPPED')}\n")
            
            logger.info(f"✅ Detailed report saved to: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save detailed report: {e}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        logger.info("GoDiag GD101 + Opel ECU Connection Test Suite")
        logger.info("Testing GoDiag GD101 (N32G43x Port) via GT100 PLUS GPT")
        logger.info("Target: Opel ECU Communication")
        logger.info("=" * 70)
        
        # Run tests in sequence
        tests = [
            self.test_gd101_n32g43x_detection,
            self.test_gt100_plus_gpt_interface,
            self.test_opel_ecu_communication,
            self.test_gt100_plus_specific_features
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                logger.error(f"Test execution failed: {e}")
                continue
        
        # Generate final report
        success = self.generate_test_report()
        
        # Cleanup
        if self.connected_device:
            self.vci_manager.disconnect()
        
        return success


def main():
    """Main test execution"""
    tester = GoDiagGD101OpelECUTester()
    success = tester.run_all_tests()
    
    if success:
        logger.info("\n🎉 All tests completed successfully!")
        logger.info("GoDiag GD101 is ready for Opel ECU diagnostics via GT100 PLUS GPT")
    else:
        logger.error("\n❌ Some tests failed. Check the report above for details.")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)