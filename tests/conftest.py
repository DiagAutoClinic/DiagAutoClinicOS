"""
conftest.py - Shared pytest fixtures for AutoDiag v2 Beta
This file is automatically loaded by pytest and provides fixtures for all tests
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
from PyQt6.QtWidgets import QApplication

# Add project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHARED_DIR = os.path.join(BASE_DIR, '..', 'shared')
AUTODIAG_DIR = os.path.join(BASE_DIR, '..', 'AutoDiag')

sys.path.insert(0, SHARED_DIR)
sys.path.insert(0, AUTODIAG_DIR)

# ============================================================================
# SESSION-LEVEL FIXTURES (Created once per test session)
# ============================================================================

@pytest.fixture(scope='session')
def qapp():
    """
    Create QApplication instance for all GUI tests.
    This is created once per test session.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # Cleanup after all tests
    app.quit()

# ============================================================================
# MODULE-LEVEL FIXTURES (Created once per test module)
# ============================================================================

@pytest.fixture(scope='module')
def sample_dtc_codes():
    """Sample DTC codes for testing"""
    return [
        ('P0300', 'High', 'Random/Multiple Cylinder Misfire Detected'),
        ('P0420', 'Medium', 'Catalyst System Efficiency Below Threshold'),
        ('P0171', 'Medium', 'System Too Lean (Bank 1)'),
        ('U0100', 'Critical', 'Lost Communication with ECM/PCM'),
        ('C1201', 'High', 'ABS System Malfunction'),
        ('B0001', 'Critical', 'Front Impact Sensor Circuit Malfunction'),
    ]

@pytest.fixture(scope='module')
def sample_vin_codes():
    """Sample VIN codes for testing"""
    return [
        '1HGBH41JXMN109186',  # Valid Honda VIN
        'WVWZZZ1KZ9W000001',  # Valid VW VIN
        'INVALID123456789',   # Invalid VIN
        'DAC2025LEGACY',      # Special test VIN
    ]

@pytest.fixture(scope='module')
def sample_vehicle_brands():
    """Sample vehicle brands for testing"""
    return [
        'Toyota', 'Honda', 'Ford', 'Chevrolet', 'Volkswagen',
        'BMW', 'Mercedes-Benz', 'Audi', 'Nissan', 'Hyundai',
        'Kia', 'Mazda', 'Subaru', 'Lexus', 'Porsche'
    ]

# ============================================================================
# FUNCTION-LEVEL FIXTURES (Created for each test function)
# ============================================================================

@pytest.fixture
def mock_security_manager():
    """
    Mock security manager for testing without real authentication.
    Returns a MagicMock that simulates successful authentication.
    """
    mock = MagicMock()
    
    # Mock authentication
    mock.authenticate_user.return_value = (True, "Login successful")
    mock.current_user = "test_user"
    
    # Mock security level
    mock_level = MagicMock()
    mock_level.name = 'BASIC'
    mock_level.value = 1
    mock.get_security_level.return_value = mock_level
    
    # Mock user info
    mock.get_user_info.return_value = {
        'full_name': 'Test User',
        'username': 'test_user',
        'security_level': 'BASIC',
        'role': 'technician',
        'session_expiry': 9999999999.0
    }
    
    # Mock session validation
    mock.validate_session.return_value = True
    
    # Mock security clearance
    mock.check_security_clearance.return_value = True
    
    # Mock audit log
    mock.get_audit_log.return_value = [
        {
            'timestamp': 1234567890.0,
            'event_type': 'LOGIN',
            'username': 'test_user',
            'details': 'Successful login'
        }
    ]
    
    # Mock logout
    mock.logout.return_value = True
    
    return mock

@pytest.fixture
def mock_device_handler():
    """
    Create a real DeviceHandler in mock mode for testing.
    This allows testing without physical hardware.
    """
    from device_handler import DeviceHandler
    handler = DeviceHandler(mock_mode=True)
    yield handler
    # Cleanup
    if handler.is_connected:
        handler.disconnect()

@pytest.fixture
def mock_dtc_database():
    """
    Create an in-memory DTC database for testing.
    This provides real database functionality without persistence.
    """
    from dtc_database import DTCDatabase
    db = DTCDatabase(":memory:")
    yield db
    # Cleanup
    db.close()

@pytest.fixture
def mock_brand_database():
    """Mock brand database with sample brands"""
    mock = MagicMock()
    mock.get_brand_list.return_value = [
        'Toyota', 'Honda', 'Ford', 'Chevrolet', 'Volkswagen',
        'BMW', 'Mercedes-Benz', 'Audi', 'Nissan', 'Hyundai'
    ]
    mock.get_brand_info.return_value = {
        'name': 'Toyota',
        'protocols': ['ISO15765', 'KWP2000'],
        'special_functions': ['Oil Reset', 'DPF Regen'],
    }
    return mock

@pytest.fixture
def mock_vin_decoder():
    """Mock VIN decoder for testing"""
    mock = MagicMock()
    mock.decode.return_value = {
        'manufacturer': 'Toyota',
        'year': 2020,
        'model': 'Corolla',
        'valid': True
    }
    return mock

@pytest.fixture
def mock_special_functions_manager():
    """Mock special functions manager"""
    mock = MagicMock()
    
    # Mock function object
    mock_function = MagicMock()
    mock_function.name = "Oil Service Reset"
    mock_function.description = "Reset oil service indicator"
    mock_function.security_level = 1
    mock_function.function_id = "oil_reset"
    mock_function.parameters = {}
    
    mock.get_brand_functions.return_value = [mock_function]
    mock.get_function.return_value = mock_function
    mock.execute_function.return_value = {
        'success': True,
        'message': 'Function executed successfully'
    }
    
    return mock

@pytest.fixture
def mock_calibrations_resets_manager():
    """Mock calibrations and resets manager"""
    mock = MagicMock()
    
    # Mock procedure object
    mock_procedure = MagicMock()
    mock_procedure.name = "Throttle Body Calibration"
    mock_procedure.description = "Calibrate throttle body position"
    mock_procedure.security_level = 2
    mock_procedure.procedure_id = "throttle_cal"
    mock_procedure.duration = "5 minutes"
    mock_procedure.reset_type = MagicMock(value="calibration")
    mock_procedure.prerequisites = ["Engine off", "Ignition on"]
    mock_procedure.steps = [
        "Turn ignition on",
        "Wait 10 seconds",
        "Turn ignition off"
    ]
    
    mock.get_brand_procedures.return_value = [mock_procedure]
    mock.get_procedure.return_value = mock_procedure
    mock.execute_procedure.return_value = {
        'success': True,
        'message': 'Procedure completed successfully'
    }
    
    return mock

# ============================================================================
# PARAMETRIZED FIXTURES (For testing multiple scenarios)
# ============================================================================

@pytest.fixture(params=['ELM327 USB', 'ELM327 Bluetooth', 'Godiag GT101'])
def device_name(request):
    """Parametrized fixture for testing different devices"""
    return request.param

@pytest.fixture(params=['AUTO', 'CAN_11BIT_500K', 'ISO15765', 'KWP2000'])
def protocol_name(request):
    """Parametrized fixture for testing different protocols"""
    return request.param

@pytest.fixture(params=['P0300', 'P0420', 'U0100', 'C1201'])
def dtc_code(request):
    """Parametrized fixture for testing different DTC codes"""
    return request.param

# ============================================================================
# AUTO-USE FIXTURES (Automatically applied to all tests)
# ============================================================================

@pytest.fixture(autouse=True)
def reset_environment():
    """
    Reset environment before each test.
    This fixture runs automatically for every test.
    """
    # Setup: Run before each test
    os.environ['AUTODIAG_TEST_MODE'] = '1'
    
    yield  # Test runs here
    
    # Teardown: Run after each test
    if 'AUTODIAG_TEST_MODE' in os.environ:
        del os.environ['AUTODIAG_TEST_MODE']

# ============================================================================
# HELPER FUNCTIONS (Available in all tests)
# ============================================================================

@pytest.fixture
def assert_dtc_format():
    """Helper to assert DTC format is correct"""
    def _assert(dtc_tuple):
        assert len(dtc_tuple) == 3, "DTC must be (code, severity, description)"
        code, severity, description = dtc_tuple
        assert isinstance(code, str), "DTC code must be string"
        assert code.startswith(('P', 'C', 'B', 'U')), "Invalid DTC prefix"
        assert severity in ['Low', 'Medium', 'High', 'Critical'], "Invalid severity"
        assert isinstance(description, str), "Description must be string"
        assert len(description) > 0, "Description cannot be empty"
    return _assert

@pytest.fixture
def assert_device_connected():
    """Helper to assert device is properly connected"""
    def _assert(device_handler):
        assert device_handler.is_connected, "Device not connected"
        assert device_handler.current_device is not None, "No current device"
        assert device_handler.current_protocol is not None, "No protocol selected"
    return _assert

# ============================================================================
# MOCK DATA GENERATORS
# ============================================================================

@pytest.fixture
def generate_mock_live_data():
    """Generate realistic mock live data"""
    def _generate():
        import random
        return {
            'rpm': random.randint(650, 3500),
            'speed': random.randint(0, 120),
            'coolant_temp': random.randint(80, 105),
            'fuel_level': random.randint(10, 95),
            'voltage': round(random.uniform(12.5, 14.5), 1),
            'throttle_position': random.randint(0, 100),
            'engine_load': random.randint(10, 90),
            'intake_temp': random.randint(20, 60),
        }
    return _generate

@pytest.fixture
def generate_mock_ecu_info():
    """Generate realistic mock ECU information"""
    def _generate():
        return {
            'part_number': f'ECU-{random.randint(10000, 99999)}',
            'software_version': f'V{random.randint(1, 9)}.{random.randint(0, 9)}.{random.randint(0, 9)}',
            'hardware_version': f'HW-Rev-{chr(65 + random.randint(0, 4))}',
            'serial_number': f'SN{random.randint(100000, 999999)}',
            'coding_data': f'Coding: {random.randint(1000000, 9999999)}',
            'diagnostic_address': '0x7E0',
            'supplier': 'Test Automotive Systems'
        }
    return _generate

# ============================================================================
# PYTEST HOOKS (Custom behavior)
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom settings"""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for workflows"
    )
    config.addinivalue_line(
        "markers", "security: Security-related tests"
    )
    config.addinivalue_line(
        "markers", "hardware: Tests requiring hardware"
    )
    config.addinivalue_line(
        "markers", "slow: Tests taking longer than 1 second"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Auto-mark slow tests
        if 'slow' in item.nodeid.lower():
            item.add_marker(pytest.mark.slow)
        
        # Auto-mark security tests
        if 'security' in item.nodeid.lower():
            item.add_marker(pytest.mark.security)
        
        # Auto-mark hardware tests
        if 'hardware' in item.nodeid.lower() or 'device' in item.nodeid.lower():
            item.add_marker(pytest.mark.hardware)

# ============================================================================
# TEMPORARY DIRECTORY FIXTURES
# ============================================================================

@pytest.fixture
def temp_config_dir(tmp_path):
    """Create temporary config directory for tests"""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir

@pytest.fixture
def temp_log_dir(tmp_path):
    """Create temporary log directory for tests"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir

@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary data directory for tests"""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir

# ============================================================================
# PERFORMANCE MONITORING FIXTURES
# ============================================================================

@pytest.fixture
def performance_monitor():
    """Monitor test performance"""
    import time
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        def duration(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return 0
        
        def assert_faster_than(self, max_seconds):
            duration = self.duration()
            assert duration < max_seconds, f"Test took {duration}s, expected < {max_seconds}s"
    
    return PerformanceMonitor()

# ============================================================================
# CAPLOG CONFIGURATION (For testing logging)
# ============================================================================

@pytest.fixture
def captured_logs(caplog):
    """Capture log messages during tests"""
    import logging
    caplog.set_level(logging.DEBUG)
    return caplog
