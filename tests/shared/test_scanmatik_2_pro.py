#!/usr/bin/env python3
"""
Comprehensive Test Suite for ScanMatik 2 Pro
Tests all major functionality including mock and real hardware modes
"""

import unittest
import sys
import os
import logging
from unittest.mock import Mock, patch, MagicMock
import time

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from shared.scanmatik_2_pro import (
    ScanMatik2Pro, ScanMatikDeviceType, ScanMatikProtocol, 
    ScanMatikFeature, ScanMatikDeviceInfo, create_scanmatik_2_pro_handler
)


class TestScanMatikDeviceInfo(unittest.TestCase):
    """Test ScanMatikDeviceInfo dataclass"""
    
    def test_device_info_creation(self):
        """Test creating ScanMatikDeviceInfo object"""
        device_info = ScanMatikDeviceInfo(
            device_type=ScanMatikDeviceType.SCANMATIK_2_PRO,
            port="COM1",
            name="Test Device",
            description="Test Description"
        )
        
        self.assertEqual(device_info.device_type, ScanMatikDeviceType.SCANMATIK_2_PRO)
        self.assertEqual(device_info.port, "COM1")
        self.assertEqual(device_info.name, "Test Device")
        self.assertIsNotNone(device_info.protocol_support)
        self.assertIsNotNone(device_info.features)
        self.assertIsNotNone(device_info.capabilities)
    
    def test_default_protocols(self):
        """Test default protocol support"""
        device_info = ScanMatikDeviceInfo(
            device_type=ScanMatikDeviceType.SCANMATIK_2_PRO,
            port="COM1",
            name="Test Device",
            description="Test Description"
        )
        
        self.assertIn(ScanMatikProtocol.ISO15765_11BIT_CAN, device_info.protocol_support)
        self.assertIn(ScanMatikProtocol.UDS_OVER_CAN, device_info.protocol_support)
    
    def test_default_features(self):
        """Test default features"""
        device_info = ScanMatikDeviceInfo(
            device_type=ScanMatikDeviceType.SCANMATIK_2_PRO,
            port="COM1",
            name="Test Device",
            description="Test Description"
        )
        
        self.assertIn(ScanMatikFeature.BASIC_OBD, device_info.features)
        self.assertIn(ScanMatikFeature.DTC_CODES, device_info.features)
        self.assertIn(ScanMatikFeature.VIN_READING, device_info.features)


class TestScanMatik2ProMockMode(unittest.TestCase):
    """Test ScanMatik 2 Pro in mock mode"""
    
    def setUp(self):
        """Set up test environment"""
        self.handler = create_scanmatik_2_pro_handler(mock_mode=True)
    
    def test_mock_initialization(self):
        """Test handler initialization in mock mode"""
        self.assertTrue(self.handler.mock_mode)
        self.assertEqual(len(self.handler.detected_devices), 1)
        self.assertIsNone(self.handler.connected_device)
        self.assertIsNone(self.handler.serial_connection)
    
    def test_mock_device_detection(self):
        """Test mock device detection"""
        devices = self.handler.detect_devices()
        
        self.assertEqual(len(devices), 1)
        device = devices[0]
        self.assertEqual(device.device_type, ScanMatikDeviceType.SCANMATIK_2_PRO)
        self.assertFalse(device.is_real_hardware)
        self.assertIn("Mock", device.name)
    
    def test_mock_connection(self):
        """Test mock device connection"""
        success = self.handler.connect_device("ScanMatik 2 Pro (Mock)")
        
        self.assertTrue(success)
        self.assertIsNotNone(self.handler.connected_device)
        self.assertEqual(self.handler.connected_device.name, "ScanMatik 2 Pro (Mock)")
    
    def test_mock_obd_command(self):
        """Test mock OBD command execution"""
        self.handler.connect_device()
        
        result = self.handler.execute_obd_command("010C")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["command"], "010C")
        self.assertEqual(result["device"], "ScanMatik 2 Pro (Mock)")
        self.assertIn("protocol", result)
    
    def test_mock_live_data(self):
        """Test mock live data collection"""
        self.handler.connect_device()
        
        live_data = self.handler.get_live_data(['rpm', 'speed'])
        
        self.assertTrue(live_data["success"])
        self.assertIn("data", live_data)
        self.assertIn("rpm", live_data["data"])
        self.assertIn("speed", live_data["data"])
    
    def test_mock_comprehensive_diagnostics(self):
        """Test mock comprehensive diagnostics"""
        self.handler.connect_device()
        
        diagnostics = self.handler.get_comprehensive_diagnostics()
        
        self.assertTrue(diagnostics["success"])
        self.assertIn("device_info", diagnostics)
        self.assertIn("vehicle_info", diagnostics)
        self.assertIn("live_data", diagnostics)
        self.assertIn("dtc_info", diagnostics)
        self.assertIn("readiness_monitors", diagnostics)
        self.assertIn("vin_info", diagnostics)
    
    def test_mock_disconnect(self):
        """Test mock disconnection"""
        self.handler.connect_device()
        self.assertIsNotNone(self.handler.connected_device)
        
        self.handler.disconnect()
        
        self.assertIsNone(self.handler.connected_device)
    
    def test_mock_device_status(self):
        """Test mock device status"""
        status = self.handler.get_device_status()
        
        self.assertEqual(status["mock_mode"], True)
        self.assertEqual(status["detected_devices"], 1)
        self.assertIsNotNone(status["features"])


class TestScanMatik2ProRealMode(unittest.TestCase):
    """Test ScanMatik 2 Pro with mocked real hardware"""
    
    def setUp(self):
        """Set up test environment with mocked serial"""
        self.handler = create_scanmatik_2_pro_handler(mock_mode=False)
        
        # Mock serial module
        self.mock_serial = Mock()
        self.mock_serial.Serial.return_value = self.mock_serial
        
        # Mock responses for different commands
        self.mock_responses = {
            'ATZ': 'ELM327 v1.3\r\n',
            'ATI': 'ELM327 v1.5\r\n',
            'AT@1': 'ScanMatik 2 Pro\r\n',
            'OK': 'OK\r\n'
        }
        
        self.mock_serial.read.return_value = b'OK\r\n'
        self.mock_serial.in_waiting = 0
    
    @patch('shared.scanmatik_2_pro.serial.Serial')
    def test_real_device_detection(self, mock_serial_class):
        """Test real device detection"""
        mock_serial_class.return_value = self.mock_serial
        
        devices = self.handler.detect_devices()
        
        self.assertEqual(len(devices), 1)
        device = devices[0]
        self.assertTrue(device.is_real_hardware)
    
    @patch('shared.scanmatik_2_pro.serial.Serial')
    def test_real_connection(self, mock_serial_class):
        """Test real device connection"""
        mock_serial_class.return_value = self.mock_serial
        
        # Mock successful initialization
        self.mock_serial.read.return_value = b'OK\r\n'
        
        success = self.handler.connect_device("ScanMatik Device (COM1)")
        
        self.assertTrue(success)
        self.assertIsNotNone(self.handler.connected_device)
    
    @patch('shared.scanmatik_2_pro.serial.Serial')
    def test_real_command_execution(self, mock_serial_class):
        """Test real command execution"""
        mock_serial_class.return_value = self.mock_serial
        self.handler.connect_device()
        
        # Mock successful command response
        self.mock_serial.read.return_value = b'41 0C 1A F8\r\n'  # RPM response
        
        result = self.handler.execute_obd_command("010C")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["command"], "010C")
    
    @patch('shared.scanmatik_2_pro.serial.Serial')
    def test_connection_failure(self, mock_serial_class):
        """Test connection failure handling"""
        mock_serial_class.side_effect = Exception("Connection failed")
        
        success = self.handler.connect_device("Test Device")
        
        self.assertFalse(success)
        self.assertIsNone(self.handler.connected_device)


class TestScanMatik2ProProtocolSupport(unittest.TestCase):
    """Test protocol support and AT commands"""
    
    def setUp(self):
        """Set up test environment"""
        self.handler = create_scanmatik_2_pro_handler(mock_mode=True)
        self.handler.connect_device()
    
    def test_protocol_mappings(self):
        """Test protocol command mappings"""
        self.assertEqual(
            self.handler.protocol_commands[ScanMatikProtocol.ISO15765_11BIT_CAN],
            "ATSP6"
        )
        self.assertEqual(
            self.handler.protocol_commands[ScanMatikProtocol.UDS_OVER_CAN],
            "ATSP6"
        )
    
    def test_at_commands(self):
        """Test AT command templates"""
        self.assertEqual(self.handler.at_commands['reset'], 'ATZ')
        self.assertEqual(self.handler.at_commands['echo_off'], 'ATE0')
        self.assertEqual(self.handler.at_commands['headers_on'], 'ATH1')
    
    def test_obd_pid_templates(self):
        """Test OBD PID command templates"""
        self.assertEqual(self.handler.obd_pids['rpm'], '010C')
        self.assertEqual(self.handler.obd_pids['speed'], '010D')
        self.assertEqual(self.handler.obd_pids['vin'], '0902')
    
    def test_uds_command_execution(self):
        """Test UDS command execution"""
        result = self.handler.execute_uds_command("22", b'\xF1\x90')
        
        # Should return success in mock mode
        self.assertTrue(result["success"])
        self.assertEqual(result["service"], "22")
        self.assertEqual(result["protocol"], "UDS")


class TestScanMatik2ProFeatures(unittest.TestCase):
    """Test feature detection and capabilities"""
    
    def test_device_type_detection(self):
        """Test different device type detection"""
        # Mock full response for ScanMatik 2 Pro
        handler_pro = create_scanmatik_2_pro_handler(mock_mode=True)
        handler_pro.detected_devices.clear()
        
        device_info = ScanMatikDeviceInfo(
            device_type=ScanMatikDeviceType.SCANMATIK_2_PRO,
            port="COM1",
            name="ScanMatik 2 Pro",
            description="Professional diagnostic device",
            features=[
                ScanMatikFeature.BASIC_OBD,
                ScanMatikFeature.ENHANCED_OBD,
                ScanMatikFeature.DTC_CODES,
                ScanMatikFeature.LIVE_DATA,
                ScanMatikFeature.BIDIRECTIONAL,
                ScanMatikFeature.PROGRAMMING,
                ScanMatikFeature.SECURITY_ACCESS,
                ScanMatikFeature.UDS_COMMANDS
            ]
        )
        
        self.assertIn(ScanMatikFeature.PROGRAMMING, device_info.features)
        self.assertIn(ScanMatikFeature.SECURITY_ACCESS, device_info.features)
        self.assertIn(ScanMatikFeature.UDS_COMMANDS, device_info.features)
    
    def test_capabilities_mapping(self):
        """Test capabilities mapping to features"""
        handler = create_scanmatik_2_pro_handler(mock_mode=True)
        device = handler.detected_devices[0]
        
        self.assertIn('PID_READ', device.capabilities)
        self.assertIn('LIVE_DATA', device.capabilities)
        self.assertIn('DTC_SCAN', device.capabilities)
        self.assertIn('UDS_COMMANDS', device.capabilities)


class TestScanMatik2ProIntegration(unittest.TestCase):
    """Test integration with existing system"""
    
    def test_factory_function(self):
        """Test factory function for creating handler"""
        handler = create_scanmatik_2_pro_handler(mock_mode=True)
        
        self.assertIsInstance(handler, ScanMatik2Pro)
        self.assertTrue(handler.mock_mode)
    
    def test_error_handling(self):
        """Test error handling in various scenarios"""
        handler = create_scanmatik_2_pro_handler(mock_mode=False)  # Real mode, no hardware
        
        # Should handle no devices gracefully
        devices = handler.detect_devices()
        self.assertEqual(len(devices), 0)
        
        # Should handle no connection gracefully
        result = handler.execute_obd_command("010C")
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_threading_safety(self):
        """Test thread safety of connection operations"""
        handler = create_scanmatik_2_pro_handler(mock_mode=True)
        
        # Simulate multiple connection attempts
        import threading
        
        results = []
        def connect_attempt():
            success = handler.connect_device()
            results.append(success)
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=connect_attempt)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # At least one should succeed (subsequent ones should be safe)
        self.assertTrue(any(results))


class TestScanMatik2ProPerformance(unittest.TestCase):
    """Test performance characteristics"""
    
    def test_mock_performance(self):
        """Test mock mode performance"""
        handler = create_scanmatik_2_pro_handler(mock_mode=True)
        handler.connect_device()
        
        start_time = time.time()
        
        # Perform multiple operations
        for i in range(10):
            handler.execute_obd_command("010C")
            handler.get_live_data(['rpm', 'speed'])
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should be very fast in mock mode (under 1 second for 20 operations)
        self.assertLess(total_time, 1.0)
    
    def test_large_data_handling(self):
        """Test handling of large diagnostic data"""
        handler = create_scanmatik_2_pro_handler(mock_mode=True)
        handler.connect_device()
        
        # Test with many parameters
        many_params = [f"param_{i}" for i in range(50)]
        live_data = handler.get_live_data(many_params)
        
        self.assertTrue(live_data["success"])
        self.assertIn("data", live_data)


def run_scanmatik_tests():
    """Run all ScanMatik 2 Pro tests"""
    # Configure logging for tests
    logging.basicConfig(
        level=logging.WARNING,  # Reduce noise during testing
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestScanMatikDeviceInfo,
        TestScanMatik2ProMockMode,
        TestScanMatik2ProRealMode,
        TestScanMatik2ProProtocolSupport,
        TestScanMatik2ProFeatures,
        TestScanMatik2ProIntegration,
        TestScanMatik2ProPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("=" * 60)
    print("ScanMatik 2 Pro Comprehensive Test Suite")
    print("=" * 60)
    
    success = run_scanmatik_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed successfully!")
        print("ScanMatik 2 Pro is ready for live testing")
    else:
        print("❌ Some tests failed. Please review the output above.")
        sys.exit(1)
    print("=" * 60)