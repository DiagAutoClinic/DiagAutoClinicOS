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
