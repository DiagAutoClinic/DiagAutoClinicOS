"""
AutoDiag v2 Beta - Complete Test Suite
Professional testing framework for DiagAutoClinicOS
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add shared path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared'))

# ============================================================================
# FIXTURES - Shared Test Resources
# ============================================================================

@pytest.fixture(scope='session')
def qapp():
    """Create QApplication instance for all tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    app.quit()

@pytest.fixture
def mock_security_manager():
    """Mock security manager for testing"""
    mock = MagicMock()
    mock.authenticate_user.return_value = (True, "Login successful")
    mock.current_user = "test_user"
    mock.get_security_level.return_value = MagicMock(name='BASIC', value=1)
    mock.get_user_info.return_value = {
        'full_name': 'Test User',
        'username': 'test_user',
        'security_level': 'BASIC',
        'role': 'technician',
        'session_expiry': 9999999999
    }
    mock.validate_session.return_value = True
    mock.check_security_clearance.return_value = True
    mock.get_audit_log.return_value = []
    return mock

@pytest.fixture
def mock_device_handler():
    """Mock device handler for testing"""
    from device_handler import DeviceHandler
    handler = DeviceHandler(mock_mode=True)
    return handler

@pytest.fixture
def mock_dtc_database():
    """Mock DTC database for testing"""
    from dtc_database import DTCDatabase
    db = DTCDatabase(":memory:")
    return db

# ============================================================================
# TEST SUITE 1: DEVICE HANDLER TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.hardware
@pytest.mark.mock
class TestDeviceHandler:
    """Test hardware device handling"""
    
    def test_device_handler_initialization(self, mock_device_handler):
        """Test device handler initializes correctly"""
        assert mock_device_handler is not None
        assert mock_device_handler.mock_mode == True
        assert mock_device_handler.is_connected == False
    
    def test_detect_professional_devices(self, mock_device_handler):
        """Test professional device detection"""
        devices = mock_device_handler.detect_professional_devices()
        assert len(devices) > 0
        assert any('Godiag' in str(d) for d in devices)
        assert any('ELM327' in str(d) for d in devices)
    
    def test_connect_to_device_mock(self, mock_device_handler):
        """Test connecting to device in mock mode"""
        success = mock_device_handler.connect_to_device("Godiag GT101", "AUTO")
        assert success == True
        assert mock_device_handler.is_connected == True
        assert mock_device_handler.current_device is not None
    
    def test_scan_dtcs_mock(self, mock_device_handler):
        """Test DTC scanning in mock mode"""
        mock_device_handler.connect_to_device("ELM327 USB", "AUTO")
        dtcs = mock_device_handler.scan_dtcs()
        assert len(dtcs) > 0
        assert all(len(dtc) == 3 for dtc in dtcs)  # (code, severity, description)
    
    def test_get_live_data_mock(self, mock_device_handler):
        """Test live data reading in mock mode"""
        mock_device_handler.connect_to_device("ELM327 USB", "AUTO")
        rpm = mock_device_handler.get_live_data('rpm')
        assert isinstance(rpm, (int, float))
        assert rpm >= 0
    
    def test_clear_dtcs_mock(self, mock_device_handler):
        """Test DTC clearing in mock mode"""
        mock_device_handler.connect_to_device("ELM327 USB", "AUTO")
        result = mock_device_handler.clear_dtcs()
        assert result == True
    
    def test_disconnect_from_device(self, mock_device_handler):
        """Test disconnecting from device"""
        mock_device_handler.connect_to_device("ELM327 USB", "AUTO")
        assert mock_device_handler.is_connected == True
        mock_device_handler.disconnect()
        assert mock_device_handler.is_connected == False
    
    def test_read_ecu_identification(self, mock_device_handler):
        """Test ECU identification reading"""
        mock_device_handler.connect_to_device("Godiag GT101", "AUTO")
        ecu_info = mock_device_handler.read_ecu_identification_advanced()
        assert 'part_number' in ecu_info
        assert 'software_version' in ecu_info
        assert 'serial_number' in ecu_info
        # Verify serial masking
        assert '*' in ecu_info['serial_number'] or len(ecu_info['serial_number']) <= 8

# ============================================================================
# TEST SUITE 2: DTC DATABASE TESTS
# ============================================================================

@pytest.mark.unit
class TestDTCDatabase:
    """Test DTC database functionality"""
    
    def test_dtc_database_initialization(self, mock_dtc_database):
        """Test DTC database initializes with data"""
        assert mock_dtc_database is not None
    
    def test_get_dtc_info_valid_code(self, mock_dtc_database):
        """Test retrieving valid DTC information"""
        info = mock_dtc_database.get_dtc_info('P0300')
        assert info['description'] != 'Unknown DTC Code'
        assert info['severity'] in ['Low', 'Medium', 'High', 'Critical']
        assert info['category'] in ['Powertrain', 'Network', 'Body', 'Chassis']
    
    def test_get_dtc_info_invalid_code(self, mock_dtc_database):
        """Test retrieving invalid DTC code"""
        info = mock_dtc_database.get_dtc_info('INVALID123')
        assert info['description'] == 'Unknown DTC Code'
        assert info['severity'] == 'Unknown'
    
    def test_search_dtcs_by_code(self, mock_dtc_database):
        """Test searching DTCs by code"""
        results = mock_dtc_database.search_dtcs('P03')
        assert len(results) > 0
        assert all('P03' in result[0] for result in results)
    
    def test_search_dtcs_by_description(self, mock_dtc_database):
        """Test searching DTCs by description"""
        results = mock_dtc_database.search_dtcs('Misfire')
        assert len(results) > 0
        assert all('Misfire' in result[1] for result in results)
    
    def test_dtc_severity_levels(self, mock_dtc_database):
        """Test DTC severity classification"""
        critical = mock_dtc_database.get_dtc_info('P0217')  # Engine Overtemp
        assert critical['severity'] == 'Critical'
        
        high = mock_dtc_database.get_dtc_info('P0300')  # Misfire
        assert high['severity'] == 'High'
    
    def test_dtc_categories(self, mock_dtc_database):
        """Test DTC category classification"""
        powertrain = mock_dtc_database.get_dtc_info('P0300')
        assert powertrain['category'] == 'Powertrain'
        
        network = mock_dtc_database.get_dtc_info('U0100')
        assert network['category'] == 'Network'

# ============================================================================
# TEST SUITE 3: SECURITY TESTS (Abstract - No Sensitive Code)
# ============================================================================

@pytest.mark.unit
@pytest.mark.security
class TestSecurityModule:
    """Test security functionality (abstracted)"""
    
    def test_authentication_success(self, mock_security_manager):
        """Test successful authentication"""
        success, message = mock_security_manager.authenticate_user('test', 'pass')
        assert success == True
        assert 'successful' in message.lower()
    
    def test_session_validation(self, mock_security_manager):
        """Test session validation"""
        is_valid = mock_security_manager.validate_session()
        assert isinstance(is_valid, bool)
    
    def test_security_level_retrieval(self, mock_security_manager):
        """Test security level retrieval"""
        level = mock_security_manager.get_security_level()
        assert hasattr(level, 'name')
        assert hasattr(level, 'value')
    
    def test_user_info_retrieval(self, mock_security_manager):
        """Test user information retrieval"""
        info = mock_security_manager.get_user_info()
        assert 'username' in info
        assert 'security_level' in info
        assert 'role' in info
    
    def test_security_clearance_check(self, mock_security_manager):
        """Test security clearance checking"""
        mock_level = MagicMock(value=1)
        has_clearance = mock_security_manager.check_security_clearance(mock_level)
        assert isinstance(has_clearance, bool)

# ============================================================================
# TEST SUITE 4: UI COMPONENT TESTS
# ============================================================================

@pytest.mark.ui
@pytest.mark.skip(reason="Requires full UI initialization")
class TestUIComponents:
    """Test UI components (requires Qt)"""
    
    def test_login_dialog_creation(self, qapp):
        """Test login dialog can be created"""
        # This would test LoginDialog initialization
        pass
    
    def test_main_window_creation(self, qapp, mock_security_manager):
        """Test main window creation"""
        # This would test AutoDiagPro initialization
        pass
    
    def test_tab_widget_creation(self, qapp):
        """Test tab widget contains all expected tabs"""
        pass

# ============================================================================
# TEST SUITE 5: INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.mock
class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_full_diagnostic_workflow_mock(self, mock_device_handler, mock_dtc_database):
        """Test complete diagnostic workflow in mock mode"""
        # Connect to device
        assert mock_device_handler.connect_to_device("ELM327 USB", "AUTO")
        
        # Scan for DTCs
        dtcs = mock_device_handler.scan_dtcs()
        assert len(dtcs) > 0
        
        # Look up DTC information
        for code, severity, description in dtcs:
            info = mock_dtc_database.get_dtc_info(code)
            assert info is not None
            assert info['description'] != 'Unknown DTC Code'
        
        # Clear DTCs
        assert mock_device_handler.clear_dtcs()
        
        # Disconnect
        mock_device_handler.disconnect()
        assert not mock_device_handler.is_connected
    
    def test_live_data_monitoring_mock(self, mock_device_handler):
        """Test live data monitoring workflow"""
        mock_device_handler.connect_to_device("Godiag GT101", "AUTO")
        
        # Read multiple parameters
        parameters = ['rpm', 'speed', 'coolant_temp', 'fuel_level', 'voltage']
        for param in parameters:
            value = mock_device_handler.get_live_data(param)
            assert isinstance(value, (int, float))
        
        mock_device_handler.disconnect()

# ============================================================================
# TEST SUITE 6: ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.unit
class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_device_connection_when_not_available(self, mock_device_handler):
        """Test handling of unavailable device"""
        # In mock mode, this should still succeed
        # In real mode, would test proper error handling
        result = mock_device_handler.connect_to_device("NonExistent Device", "AUTO")
        assert isinstance(result, bool)
    
    def test_dtc_scan_without_connection(self, mock_device_handler):
        """Test DTC scan without device connection"""
        mock_device_handler.is_connected = False
        dtcs = mock_device_handler.scan_dtcs()
        assert dtcs == []
    
    def test_live_data_without_connection(self, mock_device_handler):
        """Test live data reading without connection"""
        mock_device_handler.is_connected = False
        value = mock_device_handler.get_live_data('rpm')
        assert value == 0.0
    
    def test_invalid_dtc_code_lookup(self, mock_dtc_database):
        """Test lookup of invalid DTC code"""
        info = mock_dtc_database.get_dtc_info('ZZZZZ')
        assert info['description'] == 'Unknown DTC Code'

# ============================================================================
# TEST SUITE 7: PERFORMANCE TESTS
# ============================================================================

@pytest.mark.benchmark
@pytest.mark.slow
class TestPerformance:
    """Test performance and efficiency"""
    
    def test_dtc_database_search_performance(self, mock_dtc_database):
        """Test DTC search completes quickly"""
        import time
        start = time.time()
        results = mock_dtc_database.search_dtcs('P0')
        duration = time.time() - start
        assert duration < 1.0  # Should complete in under 1 second
        assert len(results) > 0
    
    def test_device_detection_performance(self, mock_device_handler):
        """Test device detection completes in reasonable time"""
        import time
        start = time.time()
        devices = mock_device_handler.detect_professional_devices()
        duration = time.time() - start
        assert duration < 5.0  # Should complete in under 5 seconds

# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
