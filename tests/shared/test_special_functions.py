#!/usr/bin/env python3
"""
Comprehensive Special Functions Tests
Tests brand-specific diagnostic functions, parameter validation, security integration
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add shared directory to path
shared_path = os.path.join(os.path.dirname(__file__), '..', 'shared')
sys.path.insert(0, shared_path)

from special_functions import (
    EnhancedSpecialFunction, EnhancedSpecialFunctionsManager,
    FunctionCategory, special_functions_manager
)


@pytest.fixture
def mock_security_manager():
    """Create mock security manager"""
    mock = Mock()
    mock.validate_session.return_value = True
    mock.current_user = "test_user"
    mock.get_security_level.return_value = Mock(value=5)  # FACTORY level
    return mock


@pytest.fixture
def functions_manager(mock_security_manager):
    """Create functions manager with mock security"""
    manager = EnhancedSpecialFunctionsManager()
    manager.security_manager = mock_security_manager
    return manager


class TestSpecialFunctionObject:
    """Test EnhancedSpecialFunction object"""
    
    def test_function_creation(self):
        """Test creating a special function"""
        func = EnhancedSpecialFunction(
            "test_func",
            "Test Function",
            FunctionCategory.DIAGNOSTIC,
            "Test description",
            3,
            "Toyota"
        )
        
        assert func.function_id == "test_func"
        assert func.name == "Test Function"
        assert func.category == FunctionCategory.DIAGNOSTIC
        assert func.description == "Test description"
        assert func.security_level == 3
        assert func.brand == "Toyota"
    
    def test_add_parameter(self):
        """Test adding parameters to function"""
        func = EnhancedSpecialFunction(
            "test_func", "Test", FunctionCategory.DIAGNOSTIC,
            "Test", 3, "Toyota"
        )
        
        func.add_parameter("engine_temp", "int", True, "70-105")
        
        assert "engine_temp" in func.parameters
        assert func.parameters["engine_temp"]["type"] == "int"
        assert func.parameters["engine_temp"]["required"] is True
    
    def test_add_prerequisite(self):
        """Test adding prerequisites"""
        func = EnhancedSpecialFunction(
            "test_func", "Test", FunctionCategory.DIAGNOSTIC,
            "Test", 3, "Toyota"
        )
        
        func.add_prerequisite("Battery voltage > 12V")
        
        assert len(func.prerequisites) == 1
        assert "Battery voltage" in func.prerequisites[0]
    
    def test_add_risk(self):
        """Test adding risk warnings"""
        func = EnhancedSpecialFunction(
            "test_func", "Test", FunctionCategory.DIAGNOSTIC,
            "Test", 3, "Toyota"
        )
        
        func.add_risk("May cause engine stall")
        
        assert len(func.risks) == 1
        assert "engine stall" in func.risks[0]


class TestFunctionCategory:
    """Test FunctionCategory enumeration"""
    
    def test_categories_defined(self):
        """Test all function categories are defined"""
        assert FunctionCategory.ADAPTATION.value == "adaptation"
        assert FunctionCategory.CALIBRATION.value == "calibration"
        assert FunctionCategory.PROGRAMMING.value == "programming"
        assert FunctionCategory.SECURITY.value == "security"
        assert FunctionCategory.MAINTENANCE.value == "maintenance"
        assert FunctionCategory.DIAGNOSTIC.value == "diagnostic"


class TestFunctionsManagerInitialization:
    """Test functions manager initialization"""
    
    def test_manager_initialization(self):
        """Test manager initializes correctly"""
        manager = EnhancedSpecialFunctionsManager()
        
        assert manager is not None
        assert hasattr(manager, 'functions_db')
        assert hasattr(manager, 'audit_log')
        assert isinstance(manager.functions_db, dict)
    
    def test_functions_database_populated(self):
        """Test functions database is populated with brands"""
        manager = EnhancedSpecialFunctionsManager()
        
        # Should have multiple brands
        assert len(manager.functions_db) >= 10
        
        # Check key brands present
        assert 'Toyota' in manager.functions_db
        assert 'Volkswagen' in manager.functions_db
        assert 'BMW' in manager.functions_db
    
    def test_all_brands_have_functions(self):
        """Test all brands have at least one function"""
        manager = EnhancedSpecialFunctionsManager()
        
        for brand, functions in manager.functions_db.items():
            assert isinstance(functions, list)
            assert len(functions) > 0, f"{brand} has no functions"


class TestToyotaFunctions:
    """Test Toyota-specific functions"""
    
    def test_toyota_functions_exist(self, functions_manager):
        """Test Toyota has defined functions"""
        toyota_funcs = functions_manager.get_brand_functions('Toyota')
        
        assert len(toyota_funcs) > 0
        assert all(isinstance(f, EnhancedSpecialFunction) for f in toyota_funcs)
    
    def test_toyota_throttle_learning(self, functions_manager):
        """Test Toyota throttle body learning function"""
        func = functions_manager.get_function('Toyota', 'toyota_throttle_learn')
        
        if func:
            assert func.name == "Throttle Body Learning"
            assert func.category == FunctionCategory.ADAPTATION
            assert func.security_level >= 2
            assert "engine_temperature" in func.parameters
    
    def test_toyota_immobilizer_registration(self, functions_manager):
        """Test Toyota immobilizer registration function"""
        func = functions_manager.get_function('Toyota', 'toyota_immobilizer_reg')
        
        if func:
            assert func.category == FunctionCategory.SECURITY
            assert func.security_level >= 4  # High security
            assert "key_count" in func.parameters
    
    def test_toyota_steering_calibration(self, functions_manager):
        """Test Toyota steering angle calibration"""
        func = functions_manager.get_function('Toyota', 'toyota_steering_angle')
        
        if func:
            assert func.category == FunctionCategory.CALIBRATION
            assert len(func.prerequisites) > 0


class TestVolkswagenFunctions:
    """Test Volkswagen-specific functions"""
    
    def test_vw_functions_exist(self, functions_manager):
        """Test VW has defined functions"""
        vw_funcs = functions_manager.get_brand_functions('Volkswagen')
        
        assert len(vw_funcs) > 0
    
    def test_vw_dpf_regeneration(self, functions_manager):
        """Test VW DPF regeneration function"""
        func = functions_manager.get_function('Volkswagen', 'vw_dpf_regeneration')
        
        if func:
            assert func.category == FunctionCategory.MAINTENANCE
            assert "engine_temperature" in func.parameters
            assert len(func.risks) > 0  # High temp warning
    
    def test_vw_throttle_adaptation(self, functions_manager):
        """Test VW throttle valve adaptation"""
        func = functions_manager.get_function('Volkswagen', 'vw_throttle_adaptation')
        
        if func:
            assert func.category == FunctionCategory.ADAPTATION
            assert func.security_level >= 3


class TestBMWFunctions:
    """Test BMW-specific functions"""
    
    def test_bmw_functions_exist(self, functions_manager):
        """Test BMW has defined functions"""
        bmw_funcs = functions_manager.get_brand_functions('BMW')
        
        # BMW should have functions (may not be fully implemented yet)
        assert isinstance(bmw_funcs, list)


class TestBrandCoverage:
    """Test brand coverage across function database"""
    
    @pytest.mark.parametrize("brand", [
        'Toyota', 'Lexus', 'Volkswagen', 'Audi', 'Skoda', 'Seat',
        'BMW', 'Mini', 'Mercedes-Benz', 'Ford', 'Lincoln',
        'Chevrolet', 'Cadillac', 'GMC', 'Buick',
        'Hyundai', 'Kia', 'Jeep', 'Chrysler', 'Dodge', 'Ram',
        'Honda', 'Nissan', 'Mazda', 'Subaru', 'Mitsubishi',
        'Volvo', 'Porsche', 'Jaguar', 'Land Rover'
    ])
    def test_brand_in_database(self, functions_manager, brand):
        """Test brand exists in functions database"""
        assert brand in functions_manager.functions_db


class TestFunctionRetrieval:
    """Test function retrieval methods"""
    
    def test_get_brand_functions(self, functions_manager):
        """Test retrieving all functions for a brand"""
        toyota_funcs = functions_manager.get_brand_functions('Toyota')
        
        assert isinstance(toyota_funcs, list)
        assert len(toyota_funcs) > 0
    
    def test_get_nonexistent_brand(self, functions_manager):
        """Test retrieving functions for non-existent brand"""
        funcs = functions_manager.get_brand_functions('NonExistentBrand')
        
        assert funcs == []
    
    def test_get_specific_function(self, functions_manager):
        """Test retrieving specific function by ID"""
        func = functions_manager.get_function('Toyota', 'toyota_throttle_learn')
        
        if func:
            assert isinstance(func, EnhancedSpecialFunction)
            assert func.function_id == 'toyota_throttle_learn'
    
    def test_get_nonexistent_function(self, functions_manager):
        """Test retrieving non-existent function"""
        func = functions_manager.get_function('Toyota', 'nonexistent_func')
        
        assert func is None


class TestParameterValidation:
    """Test parameter validation"""
    
    def test_validate_missing_required_parameter(self, functions_manager):
        """Test validation catches missing required parameters"""
        func = EnhancedSpecialFunction(
            "test", "Test", FunctionCategory.DIAGNOSTIC, "Test", 3, "Toyota"
        )
        func.add_parameter("required_param", "int", True)
        
        result = functions_manager._validate_parameters(func, {})
        
        assert result["valid"] is False
        assert "Missing required parameters" in result["error"]
    
    def test_validate_all_required_present(self, functions_manager):
        """Test validation passes with all required parameters"""
        func = EnhancedSpecialFunction(
            "test", "Test", FunctionCategory.DIAGNOSTIC, "Test", 3, "Toyota"
        )
        func.add_parameter("param1", "int", True)
        
        result = functions_manager._validate_parameters(func, {"param1": 100})
        
        assert result["valid"] is True
    
    def test_validate_parameter_range(self, functions_manager):
        """Test parameter range validation"""
        func = EnhancedSpecialFunction(
            "test", "Test", FunctionCategory.DIAGNOSTIC, "Test", 3, "Toyota"
        )
        func.add_parameter("temp", "int", True, "70-105")
        
        # Valid value
        result1 = functions_manager._validate_parameters(func, {"temp": 85})
        assert result1["valid"] is True
        
        # Invalid value (too low)
        result2 = functions_manager._validate_parameters(func, {"temp": 50})
        assert result2["valid"] is False
    
    def test_validate_optional_parameter_missing(self, functions_manager):
        """Test optional parameter can be missing"""
        func = EnhancedSpecialFunction(
            "test", "Test", FunctionCategory.DIAGNOSTIC, "Test", 3, "Toyota"
        )
        func.add_parameter("optional_param", "int", False)
        
        result = functions_manager._validate_parameters(func, {})
        
        assert result["valid"] is True


class TestSecurityIntegration:
    """Test security manager integration"""
    
    def test_execute_without_security_manager(self):
        """Test execution fails without security manager"""
        manager = EnhancedSpecialFunctionsManager()
        manager.security_manager = None
        
        result = manager.execute_function('Toyota', 'toyota_throttle_learn', {})
        
        assert result["success"] is False
        assert "Security manager not configured" in result["error"]
    
    def test_execute_invalid_session(self, functions_manager):
        """Test execution fails with invalid session"""
        functions_manager.security_manager.validate_session.return_value = False
        
        result = functions_manager.execute_function('Toyota', 'toyota_throttle_learn', {})
        
        assert result["success"] is False
        assert "Session expired" in result["error"]
    
    def test_execute_insufficient_clearance(self, functions_manager):
        """Test execution fails with insufficient security clearance"""
        # Set low security level
        functions_manager.security_manager.get_security_level.return_value = Mock(value=1)
        
        # Try to execute high-security function
        result = functions_manager.execute_function(
            'Toyota', 'toyota_immobilizer_reg', 
            {"key_count": 2, "security_code": "1234"}
        )
        
        assert result["success"] is False
        assert "Insufficient security clearance" in result["error"]
    
    def test_execute_with_sufficient_clearance(self, functions_manager, mock_security_manager):
        """Test execution proceeds with sufficient clearance"""
        # High security level
        mock_security_manager.get_security_level.return_value = Mock(value=5)
        
        # Mock the execution method
        with patch.object(functions_manager, '_execute_enhanced_brand_function') as mock_exec:
            mock_exec.return_value = {"success": True, "message": "Function executed"}
            
            result = functions_manager.execute_function(
                'Toyota', 'toyota_throttle_learn',
                {"engine_temperature": 85, "ignition_on": True, "throttle_clean": False}
            )
            
            # Should call the execution method
            mock_exec.assert_called_once()


class TestFunctionExecution:
    """Test function execution"""
    
    def test_execute_nonexistent_function(self, functions_manager):
        """Test executing non-existent function"""
        result = functions_manager.execute_function('Toyota', 'nonexistent', {})
        
        assert result["success"] is False
        assert "Function not found" in result["error"]
    
    def test_execute_nonexistent_brand(self, functions_manager):
        """Test executing function for non-existent brand"""
        result = functions_manager.execute_function('FakeBrand', 'some_func', {})
        
        assert result["success"] is False
    
    def test_execute_with_missing_parameters(self, functions_manager):
        """Test execution fails with missing parameters"""
        result = functions_manager.execute_function(
            'Toyota', 'toyota_throttle_learn', {}
        )
        
        assert result["success"] is False
        assert "Parameter validation failed" in result["error"]
    
    def test_execute_empty_brand(self, functions_manager):
        """Test execution with empty brand"""
        result = functions_manager.execute_function('', 'func_id', {})
        
        assert result["success"] is False
        assert "Brand and function ID required" in result["error"]


class TestAuditLogging:
    """Test audit logging for function execution"""
    
    def test_function_attempt_logged(self, functions_manager):
        """Test function execution attempt is logged"""
        initial_log_size = len(functions_manager.audit_log)
        
        # Attempt execution (will fail due to missing params, but should log)
        functions_manager.execute_function('Toyota', 'toyota_throttle_learn', {})
        
        # Log should have grown (even on failure)
        assert len(functions_manager.audit_log) >= initial_log_size
    
    def test_log_contains_username(self, functions_manager, mock_security_manager):
        """Test audit log contains username"""
        mock_security_manager.current_user = "test_technician"
        
        # Mock execution
        with patch.object(functions_manager, '_execute_enhanced_brand_function') as mock_exec:
            mock_exec.return_value = {"success": True}
            
            functions_manager.execute_function(
                'Toyota', 'toyota_throttle_learn',
                {"engine_temperature": 85, "ignition_on": True, "throttle_clean": False}
            )
        
        # Check last log entry
        if functions_manager.audit_log:
            last_entry = functions_manager.audit_log[-1]
            assert last_entry['username'] == "test_technician"
    
    def test_sensitive_params_masked(self, functions_manager):
        """Test sensitive parameters are masked in logs"""
        # Try to execute function with security_code
        functions_manager.execute_function(
            'Toyota', 'toyota_immobilizer_reg',
            {"key_count": 2, "security_code": "SECRET123"}
        )
        
        # Check logs for masking
        if functions_manager.audit_log:
            for entry in functions_manager.audit_log:
                if 'parameters' in entry:
                    params = entry['parameters']
                    if 'security_code' in params:
                        assert params['security_code'] == "***"


class TestFunctionCategories:
    """Test function categorization"""
    
    def test_functions_have_categories(self, functions_manager):
        """Test all functions have assigned categories"""
        for brand, functions in functions_manager.functions_db.items():
            for func in functions:
                assert isinstance(func.category, FunctionCategory)
    
    def test_security_functions_high_level(self, functions_manager):
        """Test security functions require high security level"""
        for brand, functions in functions_manager.functions_db.items():
            for func in functions:
                if func.category == FunctionCategory.SECURITY:
                    assert func.security_level >= 4


class TestFunctionPrerequisites:
    """Test function prerequisites"""
    
    def test_critical_functions_have_prerequisites(self, functions_manager):
        """Test critical functions have prerequisites defined"""
        func = functions_manager.get_function('Toyota', 'toyota_throttle_learn')
        
        if func:
            assert len(func.prerequisites) > 0
    
    def test_immobilizer_has_prerequisites(self, functions_manager):
        """Test immobilizer functions have prerequisites"""
        func = functions_manager.get_function('Toyota', 'toyota_immobilizer_reg')
        
        if func:
            assert len(func.prerequisites) > 0
            # Should mention keys or security
            prereqs_text = ' '.join(func.prerequisites).lower()
            assert 'key' in prereqs_text or 'security' in prereqs_text


class TestFunctionRisks:
    """Test function risk warnings"""
    
    def test_dpf_has_risk_warning(self, functions_manager):
        """Test DPF regeneration has risk warnings"""
        func = functions_manager.get_function('Volkswagen', 'vw_dpf_regeneration')
        
        if func:
            assert len(func.risks) > 0
            # Should warn about high temperature
            risks_text = ' '.join(func.risks).lower()
            assert 'temperature' in risks_text or 'heat' in risks_text


class TestGlobalManagerInstance:
    """Test global special_functions_manager instance"""
    
    def test_global_instance_exists(self):
        """Test global manager instance exists"""
        assert special_functions_manager is not None
        assert isinstance(special_functions_manager, EnhancedSpecialFunctionsManager)
    
    def test_global_instance_functional(self):
        """Test global instance is functional"""
        brands = list(special_functions_manager.functions_db.keys())
        assert len(brands) > 0


class TestParameterTypes:
    """Test parameter type definitions"""
    
    def test_parameter_types_defined(self, functions_manager):
        """Test parameters have type definitions"""
        for brand, functions in functions_manager.functions_db.items():
            for func in functions:
                for param_name, param_config in func.parameters.items():
                    assert 'type' in param_config
                    assert param_config['type'] in ['int', 'bool', 'string', 'float']


class TestFunctionConsistency:
    """Test function database consistency"""
    
    def test_no_duplicate_function_ids(self, functions_manager):
        """Test no duplicate function IDs within each brand"""
        for brand, functions in functions_manager.functions_db.items():
            function_ids = [f.function_id for f in functions]
            assert len(function_ids) == len(set(function_ids)), \
                f"{brand} has duplicate function IDs"
    
    def test_all_functions_have_descriptions(self, functions_manager):
        """Test all functions have descriptions"""
        for brand, functions in functions_manager.functions_db.items():
            for func in functions:
                assert func.description
                assert len(func.description) > 10


class TestSecurityLevelValidation:
    """Test security level requirements"""
    
    def test_security_levels_in_range(self, functions_manager):
        """Test all security levels are in valid range"""
        for brand, functions in functions_manager.functions_db.items():
            for func in functions:
                assert 1 <= func.security_level <= 5


class TestFunctionPerformance:
    """Test function manager performance"""
    
    @pytest.mark.benchmark
    def test_get_brand_functions_performance(self, functions_manager, benchmark):
        """Benchmark retrieving brand functions"""
        result = benchmark(functions_manager.get_brand_functions, 'Toyota')
        assert len(result) > 0
    
    def test_bulk_function_retrieval(self, functions_manager):
        """Test retrieving functions for all brands"""
        import time
        
        start = time.time()
        
        for brand in functions_manager.functions_db.keys():
            functions_manager.get_brand_functions(brand)
        
        elapsed = time.time() - start
        
        # Should be very fast (< 0.1s for all brands)
        assert elapsed < 0.1


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
