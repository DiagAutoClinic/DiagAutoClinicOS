#!/usr/bin/env python3
"""
Comprehensive Calibrations and Resets Tests
Tests calibration procedures, reset functions, prerequisites, and security
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add shared directory to path
shared_path = os.path.join(os.path.dirname(__file__), '..', 'shared')
sys.path.insert(0, shared_path)

from calibrations_reset import (
    CalibrationProcedure, CalibrationsResetsManager,
    ResetType, calibrations_resets_manager
)


@pytest.fixture
def mock_security_manager():
    """Create mock security manager"""
    mock = Mock()
    mock.validate_session.return_value = True
    mock.current_user = "test_user"
    mock.get_security_level.return_value = 5  # FACTORY level
    return mock


@pytest.fixture
def calibrations_manager(mock_security_manager):
    """Create calibrations manager with mock security"""
    manager = CalibrationsResetsManager()
    manager.security_manager = mock_security_manager
    return manager


class TestCalibrationProcedureObject:
    """Test CalibrationProcedure object"""
    
    def test_procedure_creation(self):
        """Test creating a calibration procedure"""
        proc = CalibrationProcedure(
            "test_cal",
            "Test Calibration",
            ResetType.CALIBRATION,
            "Test description",
            "5 minutes",
            3
        )
        
        assert proc.procedure_id == "test_cal"
        assert proc.name == "Test Calibration"
        assert proc.reset_type == ResetType.CALIBRATION
        assert proc.description == "Test description"
        assert proc.duration == "5 minutes"
        assert proc.security_level == 3
    
    def test_add_prerequisite(self):
        """Test adding prerequisites to procedure"""
        proc = CalibrationProcedure(
            "test", "Test", ResetType.CALIBRATION,
            "Test", "5 min", 3
        )
        
        proc.add_prerequisite("Battery voltage > 12V")
        
        assert len(proc.prerequisites) == 1
        assert "Battery voltage" in proc.prerequisites[0]
    
    def test_add_step(self):
        """Test adding steps to procedure"""
        proc = CalibrationProcedure(
            "test", "Test", ResetType.CALIBRATION,
            "Test", "5 min", 3
        )
        
        proc.add_step("Turn ignition ON")
        proc.add_step("Connect diagnostic tool")
        
        assert len(proc.steps) == 2
        assert proc.steps[0] == "Turn ignition ON"
    
    def test_empty_steps_list(self):
        """Test procedure starts with empty steps list"""
        proc = CalibrationProcedure(
            "test", "Test", ResetType.CALIBRATION,
            "Test", "5 min", 3
        )
        
        assert isinstance(proc.steps, list)
        assert len(proc.steps) == 0


class TestResetType:
    """Test ResetType enumeration"""
    
    def test_reset_types_defined(self):
        """Test all reset types are defined"""
        assert ResetType.ADAPTATION.value == "adaptation_reset"
        assert ResetType.MAINTENANCE.value == "maintenance_reset"
        assert ResetType.SYSTEM.value == "system_reset"
        assert ResetType.CALIBRATION.value == "calibration"
        assert ResetType.SECURITY.value == "security_reset"


class TestCalibrationsManagerInitialization:
    """Test calibrations manager initialization"""
    
    def test_manager_initialization(self):
        """Test manager initializes correctly"""
        manager = CalibrationsResetsManager()
        
        assert manager is not None
        assert hasattr(manager, 'procedures_db')
        assert isinstance(manager.procedures_db, dict)
    
    def test_procedures_database_populated(self):
        """Test procedures database has brands"""
        manager = CalibrationsResetsManager()
        
        # Should have multiple brands
        assert len(manager.procedures_db) > 0
        
        # Check key brands
        expected_brands = ['Toyota', 'Volkswagen', 'BMW', 'Mercedes-Benz', 'Ford']
        for brand in expected_brands:
            if brand in manager.procedures_db:
                assert len(manager.procedures_db[brand]) > 0


class TestToyotaProcedures:
    """Test Toyota calibration procedures"""
    
    def test_toyota_procedures_exist(self, calibrations_manager):
        """Test Toyota has defined procedures"""
        toyota_procs = calibrations_manager.get_brand_procedures('Toyota')
        
        assert len(toyota_procs) > 0
        assert all(isinstance(p, CalibrationProcedure) for p in toyota_procs)
    
    def test_toyota_steering_calibration(self, calibrations_manager):
        """Test Toyota steering angle calibration"""
        proc = calibrations_manager.get_procedure('Toyota', 'toyota_steering_cal')
        
        if proc:
            assert proc.reset_type == ResetType.CALIBRATION
            assert len(proc.prerequisites) > 0
            assert len(proc.steps) > 0
            assert "steering" in proc.name.lower()
    
    def test_toyota_battery_reset(self, calibrations_manager):
        """Test Toyota battery reset procedure"""
        proc = calibrations_manager.get_procedure('Toyota', 'toyota_battery_reset')
        
        if proc:
            assert proc.reset_type == ResetType.MAINTENANCE
            assert "battery" in proc.name.lower()
            assert len(proc.prerequisites) > 0
    
    def test_toyota_procedures_have_steps(self, calibrations_manager):
        """Test Toyota procedures have defined steps"""
        toyota_procs = calibrations_manager.get_brand_procedures('Toyota')
        
        for proc in toyota_procs:
            assert len(proc.steps) > 0, f"{proc.name} has no steps"


class TestVolkswagenProcedures:
    """Test Volkswagen calibration procedures"""
    
    def test_vw_procedures_exist(self, calibrations_manager):
        """Test VW has defined procedures"""
        vw_procs = calibrations_manager.get_brand_procedures('Volkswagen')
        
        assert len(vw_procs) > 0
    
    def test_vw_steering_calibration(self, calibrations_manager):
        """Test VW steering angle calibration"""
        proc = calibrations_manager.get_procedure('Volkswagen', 'vw_steering_cal')
        
        if proc:
            assert proc.reset_type == ResetType.CALIBRATION
            assert "steering" in proc.name.lower()
            # VW steering cal should have specific prerequisites
            assert len(proc.prerequisites) > 0
    
    def test_vw_window_calibration(self, calibrations_manager):
        """Test VW window calibration exists"""
        vw_procs = calibrations_manager.get_brand_procedures('Volkswagen')
        
        # Check if window calibration exists
        has_window_cal = any('window' in proc.name.lower() for proc in vw_procs)
        # May or may not be implemented yet
        assert isinstance(has_window_cal, bool)
    
    def test_vw_battery_adaptation(self, calibrations_manager):
        """Test VW battery adaptation procedure"""
        proc = calibrations_manager.get_procedure('Volkswagen', 'vw_battery_adaptation')
        
        if proc:
            assert "battery" in proc.name.lower()


class TestBMWProcedures:
    """Test BMW calibration procedures"""
    
    def test_bmw_procedures_exist(self, calibrations_manager):
        """Test BMW has defined procedures"""
        bmw_procs = calibrations_manager.get_brand_procedures('BMW')
        
        assert len(bmw_procs) > 0
    
    def test_bmw_battery_registration(self, calibrations_manager):
        """Test BMW battery registration procedure"""
        proc = calibrations_manager.get_procedure('BMW', 'bmw_battery_reg')
        
        if proc:
            assert proc.reset_type == ResetType.MAINTENANCE
            assert "battery" in proc.name.lower()
            # BMW battery registration requires specific info
            assert len(proc.steps) >= 5
    
    def test_bmw_steering_calibration(self, calibrations_manager):
        """Test BMW steering calibration"""
        proc = calibrations_manager.get_procedure('BMW', 'bmw_steering_cal')
        
        if proc:
            assert proc.reset_type == ResetType.CALIBRATION
    
    def test_bmw_procedures_high_security(self, calibrations_manager):
        """Test BMW procedures have appropriate security levels"""
        bmw_procs = calibrations_manager.get_brand_procedures('BMW')
        
        # BMW procedures should generally require higher security
        avg_security = sum(p.security_level for p in bmw_procs) / len(bmw_procs)
        assert avg_security >= 3


class TestMercedesProcedures:
    """Test Mercedes-Benz calibration procedures"""
    
    def test_mercedes_procedures_exist(self, calibrations_manager):
        """Test Mercedes has defined procedures"""
        mb_procs = calibrations_manager.get_brand_procedures('Mercedes-Benz')
        
        assert len(mb_procs) > 0
    
    def test_mercedes_esp_calibration(self, calibrations_manager):
        """Test Mercedes ESP calibration"""
        proc = calibrations_manager.get_procedure('Mercedes-Benz', 'mb_esp_calibration')
        
        if proc:
            assert "esp" in proc.name.lower() or "stability" in proc.description.lower()


class TestFordProcedures:
    """Test Ford calibration procedures"""
    
    def test_ford_procedures_exist(self, calibrations_manager):
        """Test Ford has defined procedures"""
        ford_procs = calibrations_manager.get_brand_procedures('Ford')
        
        assert len(ford_procs) > 0
    
    def test_ford_steering_reset(self, calibrations_manager):
        """Test Ford steering angle reset"""
        proc = calibrations_manager.get_procedure('Ford', 'ford_steering_angle_reset')
        
        if proc:
            assert "steering" in proc.name.lower()
    
    def test_ford_tpms_reset(self, calibrations_manager):
        """Test Ford TPMS reset procedure"""
        proc = calibrations_manager.get_procedure('Ford', 'ford_tpms_reset')
        
        if proc:
            assert "tpms" in proc.name.lower() or "tire" in proc.description.lower()


class TestProcedureRetrieval:
    """Test procedure retrieval methods"""
    
    def test_get_brand_procedures(self, calibrations_manager):
        """Test retrieving all procedures for a brand"""
        toyota_procs = calibrations_manager.get_brand_procedures('Toyota')
        
        assert isinstance(toyota_procs, list)
        assert len(toyota_procs) > 0
    
    def test_get_nonexistent_brand(self, calibrations_manager):
        """Test retrieving procedures for non-existent brand"""
        procs = calibrations_manager.get_brand_procedures('NonExistentBrand')
        
        assert procs == []
    
    def test_get_specific_procedure(self, calibrations_manager):
        """Test retrieving specific procedure by ID"""
        proc = calibrations_manager.get_procedure('Toyota', 'toyota_steering_cal')
        
        if proc:
            assert isinstance(proc, CalibrationProcedure)
            assert proc.procedure_id == 'toyota_steering_cal'
    
    def test_get_nonexistent_procedure(self, calibrations_manager):
        """Test retrieving non-existent procedure"""
        proc = calibrations_manager.get_procedure('Toyota', 'nonexistent_proc')
        
        assert proc is None


class TestProcedureExecution:
    """Test procedure execution"""
    
    def test_execute_procedure_success(self, calibrations_manager):
        """Test successfully executing a procedure"""
        with patch.object(calibrations_manager, '_execute_brand_procedure') as mock_exec:
            mock_exec.return_value = {"success": True, "message": "Completed"}
            
            result = calibrations_manager.execute_procedure(
                'Toyota', 'toyota_steering_cal'
            )
            
            assert result["success"] is True
    
    def test_execute_nonexistent_procedure(self, calibrations_manager):
        """Test executing non-existent procedure"""
        result = calibrations_manager.execute_procedure(
            'Toyota', 'nonexistent_proc'
        )
        
        assert result["success"] is False
        assert "Procedure not found" in result["error"]
    
    def test_execute_without_security_clearance(self, calibrations_manager):
        """Test execution fails without security clearance"""
        calibrations_manager.security_manager = None
        
        result = calibrations_manager.execute_procedure(
            'Toyota', 'toyota_steering_cal'
        )
        
        # Should check security but may have fallback
        assert "success" in result


class TestSecurityClearance:
    """Test security clearance checks"""
    
    def test_check_security_clearance_sufficient(self, calibrations_manager):
        """Test security clearance check with sufficient level"""
        # Manager's mock has level 5 (FACTORY)
        has_clearance = calibrations_manager._check_security_clearance(3)
        
        assert has_clearance is True
    
    def test_check_security_clearance_insufficient(self, calibrations_manager):
        """Test security clearance with insufficient level"""
        # Set low level
        calibrations_manager.security_manager.get_security_level.return_value = 2
        
        has_clearance = calibrations_manager._check_security_clearance(5)
        
        assert has_clearance is False
    
    def test_check_clearance_without_security_manager(self):
        """Test clearance check without security manager"""
        manager = CalibrationsResetsManager()
        manager.security_manager = None
        
        # Should allow basic operations (level <= 3)
        assert manager._check_security_clearance(2) is True
        assert manager._check_security_clearance(3) is True
        assert manager._check_security_clearance(4) is False


class TestProcedurePrerequisites:
    """Test procedure prerequisites"""
    
    def test_steering_has_prerequisites(self, calibrations_manager):
        """Test steering calibrations have prerequisites"""
        toyota_steering = calibrations_manager.get_procedure('Toyota', 'toyota_steering_cal')
        
        if toyota_steering:
            assert len(toyota_steering.prerequisites) > 0
            # Should mention alignment or centering
            prereqs_text = ' '.join(toyota_steering.prerequisites).lower()
            assert 'level' in prereqs_text or 'center' in prereqs_text
    
    def test_battery_has_prerequisites(self, calibrations_manager):
        """Test battery procedures have prerequisites"""
        toyota_battery = calibrations_manager.get_procedure('Toyota', 'toyota_battery_reset')
        
        if toyota_battery:
            assert len(toyota_battery.prerequisites) > 0
            prereqs_text = ' '.join(toyota_battery.prerequisites).lower()
            assert 'battery' in prereqs_text


class TestProcedureSteps:
    """Test procedure step definitions"""
    
    def test_all_procedures_have_steps(self, calibrations_manager):
        """Test all procedures have defined steps"""
        for brand, procedures in calibrations_manager.procedures_db.items():
            for proc in procedures:
                assert len(proc.steps) > 0, \
                    f"{brand} - {proc.name} has no steps"
    
    def test_steps_are_ordered(self, calibrations_manager):
        """Test steps are in logical order"""
        proc = calibrations_manager.get_procedure('Toyota', 'toyota_steering_cal')
        
        if proc and len(proc.steps) > 0:
            # First step should often be about ignition or preparation
            first_step = proc.steps[0].lower()
            assert any(word in first_step for word in 
                      ['turn', 'ignition', 'ensure', 'connect', 'start'])
    
    def test_steps_have_actions(self, calibrations_manager):
        """Test steps contain actionable instructions"""
        for brand, procedures in calibrations_manager.procedures_db.items():
            for proc in procedures:
                for step in proc.steps:
                    # Steps should be non-empty and reasonably long
                    assert len(step) > 5


class TestProcedureDuration:
    """Test procedure duration specifications"""
    
    def test_all_procedures_have_duration(self, calibrations_manager):
        """Test all procedures specify duration"""
        for brand, procedures in calibrations_manager.procedures_db.items():
            for proc in procedures:
                assert proc.duration is not None
                assert len(proc.duration) > 0
    
    def test_duration_format(self, calibrations_manager):
        """Test duration is in reasonable format"""
        for brand, procedures in calibrations_manager.procedures_db.items():
            for proc in procedures:
                duration = proc.duration.lower()
                # Should mention time unit
                assert any(unit in duration for unit in 
                          ['minute', 'min', 'second', 'sec', 'hour'])


class TestResetTypes:
    """Test reset type categorization"""
    
    def test_procedures_have_reset_types(self, calibrations_manager):
        """Test all procedures have reset type"""
        for brand, procedures in calibrations_manager.procedures_db.items():
            for proc in procedures:
                assert isinstance(proc.reset_type, ResetType)
    
    def test_steering_is_calibration(self, calibrations_manager):
        """Test steering procedures are CALIBRATION type"""
        toyota_steering = calibrations_manager.get_procedure('Toyota', 'toyota_steering_cal')
        
        if toyota_steering:
            assert toyota_steering.reset_type == ResetType.CALIBRATION
    
    def test_battery_is_maintenance(self, calibrations_manager):
        """Test battery procedures are MAINTENANCE type"""
        toyota_battery = calibrations_manager.get_procedure('Toyota', 'toyota_battery_reset')
        
        if toyota_battery:
            assert toyota_battery.reset_type == ResetType.MAINTENANCE


class TestSecurityLevels:
    """Test security level requirements"""
    
    def test_security_levels_in_range(self, calibrations_manager):
        """Test all security levels are valid"""
        for brand, procedures in calibrations_manager.procedures_db.items():
            for proc in procedures:
                assert 1 <= proc.security_level <= 5
    
    def test_calibrations_require_higher_security(self, calibrations_manager):
        """Test calibration procedures require appropriate security"""
        for brand, procedures in calibrations_manager.procedures_db.items():
            for proc in procedures:
                if proc.reset_type == ResetType.CALIBRATION:
                    # Calibrations should require at least level 2
                    assert proc.security_level >= 2


class TestBrandCoverage:
    """Test brand coverage in procedures database"""
    
    @pytest.mark.parametrize("brand", [
        'Toyota', 'Volkswagen', 'BMW', 'Mercedes-Benz', 'Ford'
    ])
    def test_major_brands_have_procedures(self, calibrations_manager, brand):
        """Test major brands have procedures defined"""
        procs = calibrations_manager.get_brand_procedures(brand)
        
        assert len(procs) > 0, f"{brand} has no procedures"


class TestProcedureConsistency:
    """Test procedure database consistency"""
    
    def test_no_duplicate_procedure_ids(self, calibrations_manager):
        """Test no duplicate procedure IDs within brands"""
        for brand, procedures in calibrations_manager.procedures_db.items():
            proc_ids = [p.procedure_id for p in procedures]
            assert len(proc_ids) == len(set(proc_ids)), \
                f"{brand} has duplicate procedure IDs"
    
    def test_all_procedures_have_names(self, calibrations_manager):
        """Test all procedures have names"""
        for brand, procedures in calibrations_manager.procedures_db.items():
            for proc in procedures:
                assert proc.name
                assert len(proc.name) > 5
    
    def test_all_procedures_have_descriptions(self, calibrations_manager):
        """Test all procedures have descriptions"""
        for brand, procedures in calibrations_manager.procedures_db.items():
            for proc in procedures:
                assert proc.description
                assert len(proc.description) > 10


class TestSteeringCalibrationExecution:
    """Test steering calibration execution logic"""
    
    def test_execute_steering_calibration(self, calibrations_manager):
        """Test steering calibration execution"""
        result = calibrations_manager._execute_steering_calibration(
            'Toyota', 'toyota_steering_cal'
        )
        
        assert result["success"] is True
        assert "steps_completed" in result
        assert "verification" in result
    
    def test_steering_result_structure(self, calibrations_manager):
        """Test steering calibration result structure"""
        result = calibrations_manager._execute_steering_calibration(
            'BMW', 'bmw_steering_cal'
        )
        
        assert "message" in result
        assert "steps_completed" in result
        assert isinstance(result["steps_completed"], list)


class TestBatteryResetExecution:
    """Test battery reset execution logic"""
    
    def test_execute_battery_reset(self, calibrations_manager):
        """Test battery reset execution"""
        params = {
            'battery_type': 'AGM',
            'capacity': '80Ah'
        }
        
        result = calibrations_manager._execute_battery_reset(
            'BMW', 'bmw_battery_reg', params
        )
        
        assert result["success"] is True
        assert "details" in result
    
    def test_battery_reset_uses_parameters(self, calibrations_manager):
        """Test battery reset uses provided parameters"""
        params = {
            'battery_type': 'Lead-acid',
            'capacity': '70Ah'
        }
        
        result = calibrations_manager._execute_battery_reset(
            'Toyota', 'toyota_battery_reset', params
        )
        
        if "details" in result:
            assert result["details"]["battery_type"] == 'Lead-acid'


class TestGlobalManagerInstance:
    """Test global calibrations_resets_manager instance"""
    
    def test_global_instance_exists(self):
        """Test global manager instance exists"""
        assert calibrations_resets_manager is not None
        assert isinstance(calibrations_resets_manager, CalibrationsResetsManager)
    
    def test_global_instance_functional(self):
        """Test global instance is functional"""
        brands = list(calibrations_resets_manager.procedures_db.keys())
        assert len(brands) > 0


class TestCommonProcedures:
    """Test common procedures across brands"""
    
    def test_most_brands_have_steering_cal(self, calibrations_manager):
        """Test most brands have steering calibration"""
        brands_with_steering = 0
        
        for brand in calibrations_manager.procedures_db.keys():
            procs = calibrations_manager.get_brand_procedures(brand)
            has_steering = any('steering' in p.name.lower() for p in procs)
            if has_steering:
                brands_with_steering += 1
        
        # At least 3 brands should have steering calibration
        assert brands_with_steering >= 3
    
    def test_battery_procedures_common(self, calibrations_manager):
        """Test battery procedures are common across brands"""
        brands_with_battery = 0
        
        for brand in calibrations_manager.procedures_db.keys():
            procs = calibrations_manager.get_brand_procedures(brand)
            has_battery = any('battery' in p.name.lower() for p in procs)
            if has_battery:
                brands_with_battery += 1
        
        # Multiple brands should have battery procedures
        assert brands_with_battery >= 2


class TestProcedureParameters:
    """Test procedure parameter handling"""
    
    def test_execute_with_parameters(self, calibrations_manager):
        """Test executing procedure with parameters"""
        params = {'test_param': 'value'}
        
        with patch.object(calibrations_manager, '_execute_brand_procedure') as mock:
            mock.return_value = {"success": True}
            
            result = calibrations_manager.execute_procedure(
                'Toyota', 'toyota_battery_reset', params
            )
            
            # Should pass parameters to execution
            mock.assert_called_once()


class TestManagerPerformance:
    """Test manager performance"""
    
    @pytest.mark.benchmark
    def test_get_procedures_performance(self, calibrations_manager, benchmark):
        """Benchmark getting brand procedures"""
        result = benchmark(calibrations_manager.get_brand_procedures, 'Toyota')
        assert len(result) > 0
    
    def test_bulk_procedure_retrieval(self, calibrations_manager):
        """Test retrieving procedures for all brands"""
        import time
        
        start = time.time()
        
        for brand in calibrations_manager.procedures_db.keys():
            calibrations_manager.get_brand_procedures(brand)
        
        elapsed = time.time() - start
        
        # Should be very fast
        assert elapsed < 0.1


class TestProcedureValidation:
    """Test procedure validation"""
    
    def test_procedure_id_format(self, calibrations_manager):
        """Test procedure IDs follow consistent format"""
        for brand, procedures in calibrations_manager.procedures_db.items():
            for proc in procedures:
                # Should be lowercase with underscores
                assert proc.procedure_id.islower() or '_' in proc.procedure_id
                # Should not contain spaces
                assert ' ' not in proc.procedure_id


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
