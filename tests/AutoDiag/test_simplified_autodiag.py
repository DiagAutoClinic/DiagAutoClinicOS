#!/usr/bin/env python3
"""
Simplified AutoDiag Test Suite
Focus: VIN Scan, DTC Scan, DTC Clear
Real: Volkswagen (via J2534 GoDiag GD101) | Mock: All other brands
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add shared path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

# Import from simplified main
sys.path.insert(0, os.path.dirname(__file__))
from main_simplified import (
    DiagnosticSession,
    VWDiagnosticEngine,
    MockDiagnosticEngine,
    DiagnosticResults,
    AutoDiagMainWindow
)

from j2534_passthru import (
    MockJ2534PassThru, J2534Protocol, J2534Message, J2534PassThru
)


@pytest.fixture(scope='session')
def qapp():
    """Create QApplication instance for all tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    app.quit()


class TestVWDiagnosticEngine:
    """Test Volkswagen diagnostic engine (real implementation)"""
    
    def test_vw_engine_initialization(self):
        """Test VW engine initializes correctly"""
        engine = VWDiagnosticEngine()
        assert engine is not None
        assert engine.protocol.value == "UDS (ISO 14229)"
    
    def test_vw_read_vin(self):
        """Test VW VIN read"""
        engine = VWDiagnosticEngine()
        vin = engine.read_vin()
        assert vin is not None
        assert len(vin) == 17
        assert vin.startswith("WVWZZZ")  # VW prefix
    
    def test_vw_scan_dtcs(self):
        """Test VW DTC scan"""
        engine = VWDiagnosticEngine()
        dtcs = engine.scan_dtcs()
        assert isinstance(dtcs, list)
        assert len(dtcs) > 0
        # Each DTC should be (code, severity, description)
        for code, severity, description in dtcs:
            assert isinstance(code, str)
            assert severity in ['Low', 'Medium', 'High', 'Critical']
            assert isinstance(description, str)
    
    def test_vw_clear_dtcs(self):
        """Test VW DTC clear"""
        engine = VWDiagnosticEngine()
        success = engine.clear_dtcs()
        assert success is True


class TestJ2534PassThru:
    """Test J2534 PassThru interface and GoDiag GD101 integration"""
    
    def test_mock_passthru_open(self):
        """Test opening mock J2534 device"""
        device = MockJ2534PassThru()
        assert device.open() is True
        assert device.is_connected() is False
        device.close()
    
    def test_mock_passthru_connect(self):
        """Test connecting to UDS protocol"""
        device = MockJ2534PassThru()
        device.open()
        
        channel = device.connect(J2534Protocol.ISO14229_UDS)
        assert channel > 0
        assert device.is_connected() is True
        
        device.disconnect(channel)
        device.close()
    
    def test_mock_passthru_send_message(self):
        """Test sending UDS message"""
        device = MockJ2534PassThru()
        device.open()
        channel = device.connect(J2534Protocol.ISO14229_UDS)
        
        # Send UDS VIN read request (0x22 0xF1 0x90)
        msg = J2534Message(J2534Protocol.ISO14229_UDS, data=b'\x22\xF1\x90')
        assert device.send_message(channel, msg) is True
        
        device.disconnect(channel)
        device.close()
    
    def test_mock_passthru_read_message(self):
        """Test reading UDS response"""
        device = MockJ2534PassThru()
        device.open()
        channel = device.connect(J2534Protocol.ISO14229_UDS)
        
        # Send message
        msg = J2534Message(J2534Protocol.ISO14229_UDS, data=b'\x22\xF1\x90')
        device.send_message(channel, msg)
        
        # Read response (mock returns random UDS responses)
        response = device.read_message(channel, timeout_ms=1000)
        assert response is not None
        # Response can be VIN (0x62), DTC scan (0x59), or DTC clear (0x54)
        assert response.data[0] in [0x62, 0x59, 0x54]
        
        device.disconnect(channel)
        device.close()
    
    def test_vw_engine_with_j2534_mock(self):
        """Test VW engine with mock J2534 device"""
        passthru = MockJ2534PassThru("Test GoDiag GD101")
        engine = VWDiagnosticEngine(passthru_device=passthru, use_mock=False)
        
        # Should connect successfully with mock device
        assert engine.connect() is True
        assert engine.is_connected is True
        
        # Read VIN
        vin = engine.read_vin()
        assert vin is not None
        
        engine.disconnect()
    
    def test_vw_engine_j2534_vin_read_with_connection(self):
        """Test VW VIN read via J2534 with proper connection"""
        passthru = MockJ2534PassThru()
        passthru.open()
        
        engine = VWDiagnosticEngine(passthru_device=passthru, use_mock=False)
        assert engine.connect() is True
        
        vin = engine.read_vin()
        assert vin is not None
        assert len(vin) == 17
        assert vin.startswith("WVW")
        
        engine.disconnect()
    
    def test_vw_engine_j2534_dtc_scan_with_connection(self):
        """Test VW DTC scan via J2534"""
        passthru = MockJ2534PassThru()
        passthru.open()
        
        engine = VWDiagnosticEngine(passthru_device=passthru, use_mock=False)
        engine.connect()
        
        dtcs = engine.scan_dtcs()
        assert isinstance(dtcs, list)
        assert len(dtcs) > 0
        
        engine.disconnect()
    
    def test_vw_engine_j2534_dtc_clear_with_connection(self):
        """Test VW DTC clear via J2534"""
        passthru = MockJ2534PassThru()
        passthru.open()
        
        engine = VWDiagnosticEngine(passthru_device=passthru, use_mock=False)
        engine.connect()
        
        success = engine.clear_dtcs()
        assert success is True
        
        engine.disconnect()
    
    def test_vw_engine_j2534_parse_dtc_response(self):
        """Test DTC response parsing"""
        engine = VWDiagnosticEngine()
        
        # Mock DTC response data: 0x030000 (P0300) + status 0x08 (confirmed)
        dtc_data = b'\x03\x00\x00\x08'
        dtcs = engine._parse_dtc_response(dtc_data)
        
        assert len(dtcs) > 0
        assert dtcs[0][0].startswith('P')  # Should be P code
        assert dtcs[0][1] in ['Low', 'Medium', 'High', 'Critical']  # Severity
        assert len(dtcs[0][2]) > 0  # Description



class TestMockDiagnosticEngine:
    """Test mock engine for other brands"""
    
    @pytest.mark.parametrize("brand", ["Toyota", "Honda", "Ford", "Chevrolet", "Hyundai"])
    def test_mock_engine_initialization(self, brand):
        """Test mock engine initializes for each brand"""
        engine = MockDiagnosticEngine(brand)
        assert engine is not None
        assert engine.brand == brand
    
    @pytest.mark.parametrize("brand", ["Toyota", "Honda", "Ford"])
    def test_mock_read_vin(self, brand):
        """Test mock VIN read"""
        engine = MockDiagnosticEngine(brand)
        vin = engine.read_vin()
        assert vin is not None
        assert len(vin) == 17
    
    @pytest.mark.parametrize("brand", ["Toyota", "Honda", "Ford"])
    def test_mock_scan_dtcs(self, brand):
        """Test mock DTC scan"""
        engine = MockDiagnosticEngine(brand)
        dtcs = engine.scan_dtcs()
        assert isinstance(dtcs, list)
        assert len(dtcs) > 0
    
    @pytest.mark.parametrize("brand", ["Toyota", "Honda", "Ford"])
    def test_mock_clear_dtcs(self, brand):
        """Test mock DTC clear"""
        engine = MockDiagnosticEngine(brand)
        success = engine.clear_dtcs()
        assert success is True


class TestDiagnosticSession:
    """Test diagnostic session manager"""
    
    def test_vw_session_creation(self):
        """Test creating a VW diagnostic session"""
        session = DiagnosticSession("Volkswagen", use_j2534=True)
        assert session is not None
        assert session.brand == "Volkswagen"
        assert session.results.is_mock is False
        assert isinstance(session.engine, VWDiagnosticEngine)
    
    def test_vw_session_with_mock_j2534(self):
        """Test VW session with mock J2534 device"""
        passthru = MockJ2534PassThru()
        session = DiagnosticSession("Volkswagen", use_j2534=True, passthru_device=passthru)
        
        assert session.connect() is True
        assert session.engine.is_connected is True
        
        session.disconnect()
    
    def test_mock_session_creation(self):
        """Test creating a mock diagnostic session"""
        session = DiagnosticSession("Toyota")
        assert session is not None
        assert session.brand == "Toyota"
        assert session.results.is_mock is True
        assert isinstance(session.engine, MockDiagnosticEngine)
    
    def test_session_read_vin(self):
        """Test reading VIN from session"""
        session = DiagnosticSession("Volkswagen")
        vin = session.read_vin()
        assert vin is not None
        assert len(vin) == 17
        assert session.results.vin == vin
    
    def test_session_scan_dtcs(self):
        """Test scanning DTCs from session"""
        session = DiagnosticSession("Volkswagen")
        dtcs = session.scan_dtcs()
        assert isinstance(dtcs, list)
        assert len(dtcs) > 0
        assert session.results.dtcs == dtcs
    
    def test_session_clear_dtcs(self):
        """Test clearing DTCs from session"""
        session = DiagnosticSession("Volkswagen")
        # Scan first
        session.scan_dtcs()
        assert len(session.results.dtcs) > 0
        # Then clear
        success = session.clear_dtcs()
        assert success is True
        assert len(session.results.dtcs) == 0
    
    @pytest.mark.parametrize("brand", ["Toyota", "Honda", "Ford", "Hyundai", "Kia"])
    def test_session_all_brands_mock(self, brand):
        """Test all brands except VW use mock engine"""
        session = DiagnosticSession(brand)
        assert session.results.is_mock is True
        # Should still be able to read VIN and DTCs
        vin = session.read_vin()
        assert vin is not None
        dtcs = session.scan_dtcs()
        assert isinstance(dtcs, list)


class TestDiagnosticWorkflow:
    """Test complete diagnostic workflows"""
    
    def test_vw_complete_workflow(self):
        """Test complete VW diagnostic workflow"""
        session = DiagnosticSession("Volkswagen", use_j2534=True)
        
        # Connect
        session.connect()
        
        # Step 1: Read VIN
        vin = session.read_vin()
        assert vin is not None
        
        # Step 2: Scan DTCs
        dtcs = session.scan_dtcs()
        assert len(dtcs) > 0
        
        # Step 3: Verify DTC structure
        for code, severity, description in dtcs:
            assert code.startswith('P') or code.startswith('U') or code.startswith('C') or code.startswith('B')
            assert severity in ['Low', 'Medium', 'High', 'Critical']
            assert len(description) > 0
        
        # Step 4: Clear DTCs
        success = session.clear_dtcs()
        assert success is True
        assert len(session.results.dtcs) == 0
        
        # Disconnect
        session.disconnect()
    
    def test_mock_complete_workflow(self):
        """Test complete mock diagnostic workflow"""
        session = DiagnosticSession("Toyota")
        
        # Step 1: Read VIN
        vin = session.read_vin()
        assert vin is not None
        
        # Step 2: Scan DTCs
        dtcs = session.scan_dtcs()
        assert len(dtcs) > 0
        
        # Step 3: Clear DTCs
        success = session.clear_dtcs()
        assert success is True
    
    def test_multiple_sessions(self):
        """Test managing multiple diagnostic sessions"""
        vw_session = DiagnosticSession("Volkswagen")
        toyota_session = DiagnosticSession("Toyota")
        
        # Both should work independently
        vw_vin = vw_session.read_vin()
        toyota_vin = toyota_session.read_vin()
        
        assert vw_vin != toyota_vin
        assert not vw_session.results.is_mock
        assert toyota_session.results.is_mock


class TestDiagnosticResults:
    """Test diagnostic results container"""
    
    def test_results_initialization(self):
        """Test DiagnosticResults initializes correctly"""
        results = DiagnosticResults()
        assert results.vin is None
        assert results.brand is None
        assert results.dtcs == []
        assert results.is_mock is False
        assert results.status_message == ""
    
    def test_results_populated(self):
        """Test populating DiagnosticResults"""
        results = DiagnosticResults()
        results.brand = "Volkswagen"
        results.vin = "WVWZZZ3CZ7E123456"
        results.dtcs = [('P0300', 'High', 'Misfire')]
        results.is_mock = False
        results.status_message = "Success"
        
        assert results.brand == "Volkswagen"
        assert results.vin == "WVWZZZ3CZ7E123456"
        assert len(results.dtcs) == 1
        assert results.status_message == "Success"


class TestAutoDialMainWindow:
    """Test AutoDiag main window"""
    
    def test_window_creation(self, qapp):
        """Test creating main window"""
        window = AutoDiagMainWindow()
        assert window is not None
        assert window.session is None
    
    def test_window_ui_elements(self, qapp):
        """Test main window has required UI elements"""
        window = AutoDiagMainWindow()
        assert hasattr(window, 'brand_combo')
        assert hasattr(window, 'connect_btn')
        assert hasattr(window, 'read_vin_btn')
        assert hasattr(window, 'scan_dtc_btn')
        assert hasattr(window, 'clear_dtc_btn')
        assert hasattr(window, 'dtc_table')
        assert hasattr(window, 'vin_display')
    
    def test_window_button_states(self, qapp):
        """Test window button enable/disable states"""
        window = AutoDiagMainWindow()
        
        # Initially disabled
        assert not window.read_vin_btn.isEnabled()
        assert not window.scan_dtc_btn.isEnabled()
        assert not window.clear_dtc_btn.isEnabled()
        
        # Connect
        window._on_connect()
        
        # Should be enabled after connect
        assert window.read_vin_btn.isEnabled()
        assert window.scan_dtc_btn.isEnabled()
        assert window.clear_dtc_btn.isEnabled()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
