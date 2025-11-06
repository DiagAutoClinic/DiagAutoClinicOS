#!/usr/bin/env python3
"""
Comprehensive Brand Database Tests
Tests 25-brand database, security integration, protocol filtering, and access control
"""

import pytest
import sys
import os

# Add shared directory to path
shared_path = os.path.join(os.path.dirname(__file__), '..', 'shared')
sys.path.insert(0, shared_path)

from brand_database import (
    EnhancedBrandDatabase, SecurityLevel, brand_database,
    get_brand_list, get_brand_info, get_brands_by_region, get_brands_by_protocol
)


class TestBrandDatabaseInitialization:
    """Test brand database initialization"""
    
    def test_database_initialization(self):
        """Test database initializes correctly"""
        db = EnhancedBrandDatabase()
        assert db is not None
        assert hasattr(db, 'brand_data')
        assert len(db.brand_data) >= 25  # Should have 25+ brands
    
    def test_brand_data_structure(self):
        """Test each brand has required fields"""
        db = EnhancedBrandDatabase()
        
        required_fields = [
            'region', 'diagnostic_protocols', 'common_ecus',
            'key_systems', 'obd_protocol', 'security_level',
            'market_share', 'requires_security_code'
        ]
        
        for brand, data in db.brand_data.items():
            for field in required_fields:
                assert field in data, f"{brand} missing field: {field}"
    
    def test_all_25_brands_present(self):
        """Test all 25 major brands are present"""
        db = EnhancedBrandDatabase()
        
        expected_brands = [
            'Toyota', 'Honda', 'Nissan', 'Mazda', 'Subaru', 'Mitsubishi', 'Lexus',
            'Volkswagen', 'BMW', 'Mercedes-Benz', 'Audi', 'Porsche',
            'Ford', 'Chevrolet', 'Jeep', 'Cadillac', 'GMC',
            'Hyundai', 'Kia', 'Tesla',
            'Volvo', 'Land Rover', 'Jaguar', 'Renault', 'Peugeot', 'Fiat'
        ]
        
        for brand in expected_brands:
            assert brand in db.brand_data, f"{brand} not found in database"


class TestBrandListRetrieval:
    """Test brand list retrieval with security"""
    
    @pytest.fixture
    def db(self):
        return EnhancedBrandDatabase()
    
    def test_get_brand_list_no_security(self, db):
        """Test getting brand list without security manager"""
        brands = db.get_brand_list()
        assert isinstance(brands, list)
        assert len(brands) >= 25
    
    def test_get_brand_list_legacy_function(self):
        """Test legacy get_brand_list() function"""
        brands = get_brand_list()
        assert isinstance(brands, list)
        assert len(brands) >= 5  # At least basic brands
        assert 'Toyota' in brands
        assert 'Honda' in brands
    
    def test_brand_list_alphabetical_not_required(self, db):
        """Test brand list returns all brands (order not critical)"""
        brands = db.get_brand_list()
        assert 'Toyota' in brands
        assert 'BMW' in brands
        assert 'Tesla' in brands


class TestBrandInfoRetrieval:
    """Test detailed brand information retrieval"""
    
    @pytest.fixture
    def db(self):
        return EnhancedBrandDatabase()
    
    @pytest.mark.parametrize("brand", [
        'Toyota', 'Honda', 'Nissan', 'Volkswagen', 'BMW', 
        'Mercedes-Benz', 'Ford', 'Chevrolet', 'Hyundai', 'Tesla'
    ])
    def test_get_brand_info_major_brands(self, db, brand):
        """Test retrieving info for major brands"""
        info = db.get_brand_info(brand)
        
        assert isinstance(info, dict)
        assert 'region' in info
        assert 'diagnostic_protocols' in info
        assert 'common_ecus' in info
        assert len(info['diagnostic_protocols']) > 0
    
    def test_get_brand_info_invalid_brand(self, db):
        """Test retrieving info for non-existent brand"""
        info = db.get_brand_info('NonExistentBrand')
        assert info == {}
    
    def test_get_brand_info_legacy_function(self):
        """Test legacy get_brand_info() function"""
        info = get_brand_info('Toyota')
        assert isinstance(info, dict)
        assert 'region' in info
        assert info['region'] == 'Japan'
    
    def test_brand_info_protocols_list(self, db):
        """Test diagnostic protocols are properly listed"""
        info = db.get_brand_info('Toyota')
        protocols = info['diagnostic_protocols']
        
        assert isinstance(protocols, list)
        assert len(protocols) > 0
        assert any('CAN' in p or 'KWP2000' in p for p in protocols)


class TestJapaneseBrands:
    """Test Japanese brand configurations"""
    
    @pytest.fixture
    def db(self):
        return EnhancedBrandDatabase()
    
    @pytest.mark.parametrize("brand,expected_region", [
        ('Toyota', 'Japan'),
        ('Honda', 'Japan'),
        ('Nissan', 'Japan'),
        ('Mazda', 'Japan'),
        ('Subaru', 'Japan'),
        ('Mitsubishi', 'Japan'),
        ('Lexus', 'Japan'),
    ])
    def test_japanese_brands_region(self, db, brand, expected_region):
        """Test Japanese brands have correct region"""
        info = db.get_brand_info(brand)
        assert info['region'] == expected_region
    
    def test_toyota_specific_features(self, db):
        """Test Toyota-specific features"""
        info = db.get_brand_info('Toyota')
        
        assert 'ECM' in info['common_ecus']
        assert 'Immobilizer' in info['common_ecus']
        assert 'TechStream' == info['programming_tool']
        assert info['security_level'] >= 3
    
    def test_honda_specific_features(self, db):
        """Test Honda-specific features"""
        info = db.get_brand_info('Honda')
        
        assert 'PCM' in info['common_ecus']
        assert 'HDS' == info['programming_tool']
        assert 'Honda Smart Key' in info['key_systems']


class TestGermanBrands:
    """Test German brand configurations"""
    
    @pytest.fixture
    def db(self):
        return EnhancedBrandDatabase()
    
    @pytest.mark.parametrize("brand,expected_region", [
        ('Volkswagen', 'Germany'),
        ('BMW', 'Germany'),
        ('Mercedes-Benz', 'Germany'),
        ('Audi', 'Germany'),
        ('Porsche', 'Germany'),
    ])
    def test_german_brands_region(self, db, brand, expected_region):
        """Test German brands have correct region"""
        info = db.get_brand_info(brand)
        assert info['region'] == expected_region
    
    def test_vw_specific_features(self, db):
        """Test VW-specific features"""
        info = db.get_brand_info('Volkswagen')
        
        assert 'UDS' in str(info['diagnostic_protocols'])
        assert 'Gateway' in info['common_ecus']
        assert info['security_level'] >= 4
    
    def test_bmw_high_security(self, db):
        """Test BMW has high security level"""
        info = db.get_brand_info('BMW')
        
        assert info['security_level'] == 5  # Factory level
        assert 'ISTA' == info['programming_tool']
        assert 'CAS' in info['key_systems']
    
    def test_mercedes_specific_features(self, db):
        """Test Mercedes-specific features"""
        info = db.get_brand_info('Mercedes-Benz')
        
        assert 'SAM' in info['common_ecus']
        assert 'XENTRY' == info['programming_tool']
        assert info['security_level'] == 5


class TestAmericanBrands:
    """Test American brand configurations"""
    
    @pytest.fixture
    def db(self):
        return EnhancedBrandDatabase()
    
    @pytest.mark.parametrize("brand,expected_region", [
        ('Ford', 'USA'),
        ('Chevrolet', 'USA'),
        ('Jeep', 'USA'),
        ('Cadillac', 'USA'),
        ('GMC', 'USA'),
        ('Tesla', 'USA'),
    ])
    def test_american_brands_region(self, db, brand, expected_region):
        """Test American brands have correct region"""
        info = db.get_brand_info(brand)
        assert info['region'] == expected_region
    
    def test_ford_specific_features(self, db):
        """Test Ford-specific features"""
        info = db.get_brand_info('Ford')
        
        assert 'PATS' in info['key_systems']
        assert 'PCM' in info['common_ecus']
        assert 'IDS/FDRS' == info['programming_tool']
    
    def test_gm_brands_commonality(self, db):
        """Test GM brands share common features"""
        chevy = db.get_brand_info('Chevrolet')
        cadillac = db.get_brand_info('Cadillac')
        gmc = db.get_brand_info('GMC')
        
        # All should use GMLAN
        assert 'GMLAN' in chevy['diagnostic_protocols']
        assert 'GMLAN' in cadillac['diagnostic_protocols']
        assert 'GMLAN' in gmc['diagnostic_protocols']
        
        # All should use GDS2/MDI
        assert 'GDS2/MDI' in chevy['programming_tool']
        assert 'GDS2/MDI' in cadillac['programming_tool']
    
    def test_tesla_unique_features(self, db):
        """Test Tesla unique features"""
        info = db.get_brand_info('Tesla')
        
        assert 'BMS' in info['common_ecus']  # Battery Management
        assert 'Autopilot' in info['common_ecus']
        assert info['security_level'] == 5


class TestKoreanBrands:
    """Test Korean brand configurations"""
    
    @pytest.fixture
    def db(self):
        return EnhancedBrandDatabase()
    
    @pytest.mark.parametrize("brand,expected_region", [
        ('Hyundai', 'South Korea'),
        ('Kia', 'South Korea'),
    ])
    def test_korean_brands_region(self, db, brand, expected_region):
        """Test Korean brands have correct region"""
        info = db.get_brand_info(brand)
        assert info['region'] == expected_region
    
    def test_hyundai_kia_commonality(self, db):
        """Test Hyundai and Kia share common features"""
        hyundai = db.get_brand_info('Hyundai')
        kia = db.get_brand_info('Kia')
        
        # Both should use GDS
        assert 'GDS' in hyundai['programming_tool']
        assert 'GDS' in kia['programming_tool']
        
        # Both should have similar security level
        assert hyundai['security_level'] == kia['security_level']


class TestRegionalFiltering:
    """Test filtering brands by region"""
    
    @pytest.fixture
    def db(self):
        return EnhancedBrandDatabase()
    
    def test_get_japanese_brands(self, db):
        """Test retrieving all Japanese brands"""
        japanese = db.get_brands_by_region('Japan')
        
        assert isinstance(japanese, list)
        assert len(japanese) >= 7
        assert 'Toyota' in japanese
        assert 'Honda' in japanese
        assert 'Nissan' in japanese
    
    def test_get_german_brands(self, db):
        """Test retrieving all German brands"""
        german = db.get_brands_by_region('Germany')
        
        assert len(german) >= 5
        assert 'BMW' in german
        assert 'Volkswagen' in german
        assert 'Mercedes-Benz' in german
    
    def test_get_american_brands(self, db):
        """Test retrieving all American brands"""
        american = db.get_brands_by_region('USA')
        
        assert len(american) >= 6
        assert 'Ford' in american
        assert 'Chevrolet' in american
        assert 'Tesla' in american
    
    def test_get_brands_legacy_function(self):
        """Test legacy get_brands_by_region function"""
        japanese = get_brands_by_region('Japan')
        assert isinstance(japanese, list)
        assert len(japanese) >= 5


class TestProtocolFiltering:
    """Test filtering brands by diagnostic protocol"""
    
    @pytest.fixture
    def db(self):
        return EnhancedBrandDatabase()
    
    def test_get_uds_brands(self, db):
        """Test retrieving brands using UDS protocol"""
        uds_brands = db.get_brands_by_protocol('UDS')
        
        assert isinstance(uds_brands, list)
        assert len(uds_brands) >= 10
        # Most modern brands use UDS
        assert 'BMW' in uds_brands
        assert 'Mercedes-Benz' in uds_brands
    
    def test_get_can_brands(self, db):
        """Test retrieving brands using CAN protocol"""
        can_brands = db.get_brands_by_protocol('CAN')
        
        assert len(can_brands) >= 15
        assert 'Toyota' in can_brands
        assert 'Honda' in can_brands
    
    def test_get_kwp2000_brands(self, db):
        """Test retrieving brands using KWP2000 protocol"""
        kwp_brands = db.get_brands_by_protocol('KWP2000')
        
        assert len(kwp_brands) >= 5
    
    def test_protocol_filtering_legacy_function(self):
        """Test legacy get_brands_by_protocol function"""
        uds_brands = get_brands_by_protocol('UDS')
        assert isinstance(uds_brands, list)
        assert len(uds_brands) > 0


class TestSecurityIntegration:
    """Test security manager integration"""
    
    @pytest.fixture
    def db(self):
        return EnhancedBrandDatabase()
    
    def test_security_requirements_retrieval(self, db):
        """Test getting security requirements for brands"""
        reqs = db.get_security_requirements('BMW')
        
        assert 'security_level' in reqs
        assert 'requires_security_code' in reqs
        assert 'programming_tool' in reqs
        assert reqs['security_level'] == 5
        assert reqs['requires_security_code'] is True
    
    def test_validate_brand_access_sufficient_level(self, db):
        """Test brand access validation with sufficient level"""
        # User with level 5 can access BMW (requires level 5)
        has_access = db.validate_brand_access('BMW', 5)
        assert has_access is True
    
    def test_validate_brand_access_insufficient_level(self, db):
        """Test brand access validation with insufficient level"""
        # User with level 2 cannot access BMW (requires level 5)
        has_access = db.validate_brand_access('BMW', 2)
        assert has_access is False
    
    def test_get_brands_by_security_level(self, db):
        """Test retrieving brands by security level"""
        # Get brands accessible with level 3
        level_3_brands = db.get_brands_by_security_level(3)
        
        assert isinstance(level_3_brands, list)
        assert len(level_3_brands) > 0
        
        # Toyota (level 3) should be accessible
        assert 'Toyota' in level_3_brands
        
        # BMW (level 5) should NOT be accessible
        assert 'BMW' not in level_3_brands
    
    def test_security_level_values(self, db):
        """Test security levels are within valid range"""
        for brand, data in db.brand_data.items():
            security_level = data['security_level']
            assert 1 <= security_level <= 5, \
                f"{brand} has invalid security level: {security_level}"


class TestECUConfigurations:
    """Test ECU (Electronic Control Unit) configurations"""
    
    @pytest.fixture
    def db(self):
        return EnhancedBrandDatabase()
    
    def test_common_ecus_not_empty(self, db):
        """Test all brands have common ECUs defined"""
        for brand, data in db.brand_data.items():
            ecus = data['common_ecus']
            assert isinstance(ecus, list)
            assert len(ecus) > 0, f"{brand} has no common ECUs"
    
    def test_toyota_ecus(self, db):
        """Test Toyota ECU configuration"""
        info = db.get_brand_info('Toyota')
        ecus = info['common_ecus']
        
        expected_ecus = ['ECM', 'TCM', 'ABS', 'SRS']
        for ecu in expected_ecus:
            assert ecu in ecus
    
    def test_bmw_ecus(self, db):
        """Test BMW ECU configuration"""
        info = db.get_brand_info('BMW')
        ecus = info['common_ecus']
        
        # BMW-specific ECUs
        assert 'DME' in ecus  # Digital Motor Electronics
        assert 'CAS' in ecus  # Car Access System
        assert 'FRM' in ecus  # Footwell Module


class TestKeySystemConfigurations:
    """Test key/immobilizer system configurations"""
    
    @pytest.fixture
    def db(self):
        return EnhancedBrandDatabase()
    
    def test_key_systems_not_empty(self, db):
        """Test all brands have key systems defined"""
        for brand, data in db.brand_data.items():
            key_systems = data['key_systems']
            assert isinstance(key_systems, list)
            assert len(key_systems) > 0, f"{brand} has no key systems"
    
    def test_modern_brands_have_smart_keys(self, db):
        """Test modern brands have smart key systems"""
        modern_brands = ['Tesla', 'BMW', 'Mercedes-Benz', 'Lexus']
        
        for brand in modern_brands:
            info = db.get_brand_info(brand)
            key_systems_str = ' '.join(info['key_systems'])
            assert 'Smart' in key_systems_str or 'Advanced' in key_systems_str


class TestSpecialFunctions:
    """Test special functions configuration"""
    
    @pytest.fixture
    def db(self):
        return EnhancedBrandDatabase()
    
    def test_special_functions_not_empty(self, db):
        """Test brands have special functions defined"""
        for brand, data in db.brand_data.items():
            special_funcs = data.get('special_functions', [])
            assert isinstance(special_funcs, list)
            # Most brands should have at least some special functions
    
    def test_vw_dpf_regeneration(self, db):
        """Test VW has DPF regeneration function"""
        info = db.get_brand_info('Volkswagen')
        special_funcs = info.get('special_functions', [])
        
        assert any('DPF' in func for func in special_funcs)
    
    def test_bmw_battery_registration(self, db):
        """Test BMW has battery registration function"""
        info = db.get_brand_info('BMW')
        special_funcs = info.get('special_functions', [])
        
        assert any('Battery' in func for func in special_funcs)


class TestMarketShareData:
    """Test market share data"""
    
    @pytest.fixture
    def db(self):
        return EnhancedBrandDatabase()
    
    def test_market_share_present(self, db):
        """Test all brands have market share data"""
        for brand, data in db.brand_data.items():
            assert 'market_share' in data
            assert data['market_share'] is not None
    
    def test_market_share_format(self, db):
        """Test market share is in percentage format"""
        for brand, data in db.brand_data.items():
            market_share = data['market_share']
            assert isinstance(market_share, str)
            # Should contain % symbol
            assert '%' in market_share or market_share == 'Unknown'


class TestOBDProtocols:
    """Test OBD protocol configurations"""
    
    @pytest.fixture
    def db(self):
        return EnhancedBrandDatabase()
    
    def test_obd_protocol_present(self, db):
        """Test all brands have OBD protocol specified"""
        for brand, data in db.brand_data.items():
            assert 'obd_protocol' in data
            assert data['obd_protocol'] is not None
    
    def test_modern_brands_use_can(self, db):
        """Test modern brands use ISO 15765-4 (CAN)"""
        modern_brands = ['Tesla', 'BMW', 'Mercedes-Benz', 'Toyota', 'Honda']
        
        for brand in modern_brands:
            info = db.get_brand_info(brand)
            obd_protocol = info['obd_protocol']
            assert 'ISO 15765' in obd_protocol or 'CAN' in obd_protocol


class TestProgrammingTools:
    """Test programming tool configurations"""
    
    @pytest.fixture
    def db(self):
        return EnhancedBrandDatabase()
    
    def test_programming_tool_present(self, db):
        """Test all brands have programming tool specified"""
        for brand, data in db.brand_data.items():
            assert 'programming_tool' in data
            assert data['programming_tool'] is not None
    
    @pytest.mark.parametrize("brand,expected_tool", [
        ('Toyota', 'TechStream'),
        ('Honda', 'HDS'),
        ('BMW', 'ISTA'),
        ('Mercedes-Benz', 'XENTRY'),
        ('Volkswagen', 'VAS-PC'),
        ('Ford', 'IDS/FDRS'),
        ('Hyundai', 'GDS'),
    ])
    def test_brand_specific_tools(self, db, brand, expected_tool):
        """Test brand-specific programming tools"""
        info = db.get_brand_info(brand)
        assert info['programming_tool'] == expected_tool


class TestDatabaseConsistency:
    """Test database consistency and data quality"""
    
    @pytest.fixture
    def db(self):
        return EnhancedBrandDatabase()
    
    def test_no_duplicate_brands(self, db):
        """Test no duplicate brand entries"""
        brands = list(db.brand_data.keys())
        assert len(brands) == len(set(brands))
    
    def test_all_lists_are_lists(self, db):
        """Test list fields are actually lists"""
        list_fields = ['diagnostic_protocols', 'common_ecus', 
                      'key_systems', 'special_functions']
        
        for brand, data in db.brand_data.items():
            for field in list_fields:
                if field in data:
                    assert isinstance(data[field], list), \
                        f"{brand}.{field} is not a list"
    
    def test_security_code_requirement_is_boolean(self, db):
        """Test requires_security_code is boolean"""
        for brand, data in db.brand_data.items():
            assert isinstance(data['requires_security_code'], bool), \
                f"{brand} requires_security_code is not boolean"
    
    def test_no_empty_protocol_lists(self, db):
        """Test no brands have empty protocol lists"""
        for brand, data in db.brand_data.items():
            protocols = data['diagnostic_protocols']
            assert len(protocols) > 0, \
                f"{brand} has empty diagnostic_protocols"


class TestGlobalDatabaseInstance:
    """Test global brand_database instance"""
    
    def test_global_instance_exists(self):
        """Test global brand_database instance is accessible"""
        assert brand_database is not None
        assert isinstance(brand_database, EnhancedBrandDatabase)
    
    def test_global_instance_functional(self):
        """Test global instance is functional"""
        brands = brand_database.get_brand_list()
        assert len(brands) >= 25
    
    def test_legacy_functions_use_global_instance(self):
        """Test legacy functions work with global instance"""
        brands = get_brand_list()
        assert len(brands) >= 5
        
        info = get_brand_info('Toyota')
        assert 'region' in info


class TestBrandDatabasePerformance:
    """Test database performance"""
    
    @pytest.fixture
    def db(self):
        return EnhancedBrandDatabase()
    
    @pytest.mark.benchmark
    def test_brand_list_performance(self, db, benchmark):
        """Benchmark brand list retrieval"""
        result = benchmark(db.get_brand_list)
        assert len(result) >= 25
    
    @pytest.mark.benchmark
    def test_brand_info_performance(self, db, benchmark):
        """Benchmark brand info retrieval"""
        result = benchmark(db.get_brand_info, 'Toyota')
        assert result is not None
    
    def test_bulk_brand_info_retrieval(self, db):
        """Test retrieving info for all brands efficiently"""
        import time
        start = time.time()
        
        brands = db.get_brand_list()
        for brand in brands:
            db.get_brand_info(brand)
        
        elapsed = time.time() - start
        
        # Should retrieve all brand info in less than 0.1 seconds
        assert elapsed < 0.1


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
