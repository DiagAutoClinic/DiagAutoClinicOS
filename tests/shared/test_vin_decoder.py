#!/usr/bin/env python3
"""
Comprehensive VIN Decoder Tests
Tests VIN validation, decoding, brand detection, year decoding, and model estimation
"""

import pytest
import sys
import os

# Add shared directory to path
shared_path = os.path.join(os.path.dirname(__file__), '..', 'shared')
sys.path.insert(0, shared_path)

from vin_decoder import VINDecoder


class TestVINDecoderInitialization:
    """Test VIN decoder initialization and setup"""
    
    def test_decoder_initialization(self):
        """Test decoder initializes correctly"""
        decoder = VINDecoder()
        assert decoder is not None
        assert hasattr(decoder, 'wmi_to_brand')
        assert hasattr(decoder, 'decode')
    
    def test_wmi_database_populated(self):
        """Test WMI database is properly populated"""
        decoder = VINDecoder()
        assert len(decoder.wmi_to_brand) > 30  # Should have 30+ brands
        
        # Check key brands present
        assert '1HG' in decoder.wmi_to_brand  # Honda
        assert 'JTE' in decoder.wmi_to_brand  # Toyota
        assert 'WVW' in decoder.wmi_to_brand  # VW
        assert 'WBA' in decoder.wmi_to_brand  # BMW


class TestVINValidation:
    """Test VIN validation rules"""
    
    @pytest.fixture
    def decoder(self):
        return VINDecoder()
    
    def test_valid_vin_length(self, decoder):
        """Test valid 17-character VIN"""
        result = decoder.decode('1HGCM82633A004352')
        assert result['error'] is None
        assert result['full_vin'] == '1HGCM82633A004352'
    
    def test_invalid_vin_too_short(self, decoder):
        """Test VIN too short"""
        result = decoder.decode('1HG82633A004')
        assert result['error'] == 'VIN must be 17 characters'
    
    def test_invalid_vin_too_long(self, decoder):
        """Test VIN too long"""
        result = decoder.decode('1HGCM82633A0043521234')
        assert result['error'] == 'VIN must be 17 characters'
    
    @pytest.mark.parametrize("invalid_char", ['I', 'O', 'Q'])
    def test_invalid_characters(self, decoder, invalid_char):
        """Test VINs with invalid characters (I, O, Q)"""
        vin = f'1HGCM82633A00435{invalid_char}'
        result = decoder.decode(vin)
        assert 'Invalid characters' in result['error']
    
    def test_vin_case_insensitive(self, decoder):
        """Test VIN decoding is case-insensitive"""
        result_upper = decoder.decode('1HGCM82633A004352')
        result_lower = decoder.decode('1hgcm82633a004352')
        
        assert result_upper['brand'] == result_lower['brand']
        assert result_upper['year'] == result_lower['year']
    
    def test_vin_whitespace_trimming(self, decoder):
        """Test VIN whitespace is properly trimmed"""
        result = decoder.decode('  1HGCM82633A004352  ')
        assert result['full_vin'] == '1HGCM82633A004352'
        assert result['error'] is None


class TestBrandDetection:
    """Test brand identification from WMI codes"""
    
    @pytest.fixture
    def decoder(self):
        return VINDecoder()
    
    @pytest.mark.parametrize("vin,expected_brand", [
        # Japanese
        ('1HGCM82633A004352', 'Honda'),
        ('JTE123456789ABCDE', 'Toyota'),
        ('1N4AA5AP0AC000000', 'Nissan'),
        ('JM1BK32F781234567', 'Mazda'),
        ('JF1SH94608G000000', 'Subaru'),
        
        # European
        ('WVWZZZ1JZ3W000000', 'Volkswagen'),
        ('WBAAA1234567890AB', 'BMW'),
        ('WDDHF8AB6AA000000', 'Mercedes'),
        ('WAUAA00000000000A', 'Audi'),
        
        # American
        ('1FAHP3F23CL000000', 'Ford'),
        ('1G1BC5SM5J7000000', 'Chevrolet'),
        ('1C4RJFAG0EC000000', 'Jeep'),
    ])
    def test_brand_detection(self, decoder, vin, expected_brand):
        """Test correct brand detection for various VINs"""
        result = decoder.decode(vin)
        assert result['brand'] == expected_brand
    
    def test_unknown_wmi_generic_brand(self, decoder):
        """Test unknown WMI returns Generic brand"""
        result = decoder.decode('XXXAAAAAA12345678')
        assert result['brand'] == 'Generic'


class TestYearDecoding:
    """Test model year decoding from position 10"""
    
    @pytest.fixture
    def decoder(self):
        return VINDecoder()
    
    @pytest.mark.parametrize("year_char,expected_year", [
        # Pre-2010 codes
        ('A', 1980),
        ('B', 1981),
        ('Y', 2000),
        ('1', 2001),
        ('5', 2005),
        ('9', 2009),
        
        # Post-2010 codes (overlapping letters)
        ('A', 1980),  # Could also be 2010, heuristic-based
        ('C', 1982),  # Could also be 2012
        ('L', 1990),  # Could also be 2020
        ('M', 1991),  # Could also be 2021
        ('N', 1992),  # Could also be 2022
    ])
    def test_year_decoding(self, decoder, year_char, expected_year):
        """Test year character decoding"""
        vin = f'1HGCM8263{year_char}A004352'
        result = decoder.decode(vin)
        
        # For overlapping codes, check it's one of valid years
        if year_char in 'ABCDEFGHJKLMNPRSTVWXY':
            assert result['year'] in [expected_year, expected_year + 30] or \
                   result['year'] == expected_year
        else:
            assert result['year'] == expected_year
    
    def test_numeric_year_codes(self, decoder):
        """Test numeric year codes (2001-2009)"""
        for year_digit in range(1, 10):
            vin = f'1HGCM8263{year_digit}A004352'
            result = decoder.decode(vin)
            assert result['year'] == 2000 + year_digit
    
    def test_invalid_year_char(self, decoder):
        """Test invalid year character"""
        vin = '1HGCM82630A004352'  # '0' is not valid
        result = decoder.decode(vin)
        # Should still decode but year might be Unknown
        assert result['error'] is None


class TestVINSections:
    """Test VIN section parsing (WMI, VDS, VIS)"""
    
    @pytest.fixture
    def decoder(self):
        return VINDecoder()
    
    def test_wmi_extraction(self, decoder):
        """Test World Manufacturer Identifier extraction"""
        result = decoder.decode('1HGCM82633A004352')
        assert result['wmi'] == '1HG'
    
    def test_vds_extraction(self, decoder):
        """Test Vehicle Descriptor Section extraction"""
        result = decoder.decode('1HGCM82633A004352')
        assert result['vds'] == 'CM826'
        assert len(result['vds']) == 5
    
    def test_vis_extraction(self, decoder):
        """Test Vehicle Identifier Section extraction"""
        result = decoder.decode('1HGCM82633A004352')
        assert result['vis'] == '33A004352'
        assert len(result['vis']) == 9
    
    def test_plant_code(self, decoder):
        """Test plant code extraction (position 11)"""
        result = decoder.decode('1HGCM82633A004352')
        assert result['plant'] == 'A'
    
    def test_serial_number(self, decoder):
        """Test serial number extraction (positions 12-17)"""
        result = decoder.decode('1HGCM82633A004352')
        assert result['serial'] == '004352'
        assert len(result['serial']) == 6


class TestModelEstimation:
    """Test model estimation from VDS patterns"""
    
    @pytest.fixture
    def decoder(self):
        return VINDecoder()
    
    def test_honda_model_patterns(self, decoder):
        """Test Honda model estimation"""
        result = decoder.decode('1HGCM82633A004352')  # CM pattern
        assert 'Honda' in result['model'] or result['model'] == 'Accord'
    
    def test_toyota_model_patterns(self, decoder):
        """Test Toyota model estimation"""
        result = decoder.decode('JTEBU5JR9A5000000')  # BU pattern
        assert 'Toyota' in result['model'] or '4Runner' in result['model']
    
    def test_generic_model_fallback(self, decoder):
        """Test generic model fallback for unknown patterns"""
        result = decoder.decode('WVWZZZ1JZ3W000000')
        assert 'Generic' in result['model'] or 'Volkswagen' in result['model']


class TestVINDecoderEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.fixture
    def decoder(self):
        return VINDecoder()
    
    def test_empty_vin(self, decoder):
        """Test empty VIN handling"""
        result = decoder.decode('')
        assert result['error'] == 'VIN must be 17 characters'
    
    def test_whitespace_only_vin(self, decoder):
        """Test whitespace-only VIN"""
        result = decoder.decode('                 ')
        assert result['error'] == 'VIN must be 17 characters'
    
    def test_special_characters(self, decoder):
        """Test VIN with special characters"""
        result = decoder.decode('1HG-CM826-33A-0043')
        assert 'Invalid characters' in result['error']
    
    def test_unicode_characters(self, decoder):
        """Test VIN with unicode characters"""
        result = decoder.decode('1HGCM82633Ä004352')
        assert result['error'] is not None
    
    def test_all_sections_present(self, decoder):
        """Test all VIN sections are present in result"""
        result = decoder.decode('1HGCM82633A004352')
        
        required_keys = ['full_vin', 'wmi', 'vds', 'vis', 'brand', 
                        'model', 'year', 'plant', 'serial', 'error']
        
        for key in required_keys:
            assert key in result


class TestRealWorldVINs:
    """Test real-world VIN examples"""
    
    @pytest.fixture
    def decoder(self):
        return VINDecoder()
    
    @pytest.mark.parametrize("vin,expected_data", [
        # Honda Accord 2003
        ('1HGCM82633A004352', {
            'brand': 'Honda',
            'year': 2003,
            'wmi': '1HG'
        }),
        
        # Toyota Camry 2018
        ('4T1BF1FK5JU000000', {
            'brand': 'Toyota',
            'year': 2018,
            'wmi': '4T1'
        }),
        
        # VW Golf 2020
        ('WVWZZZ1JZ3W000000', {
            'brand': 'Volkswagen',
            'year': 2003,
            'wmi': 'WVW'
        }),
    ])
    def test_real_world_vins(self, decoder, vin, expected_data):
        """Test decoding of real-world VINs"""
        result = decoder.decode(vin)
        
        assert result['error'] is None
        for key, value in expected_data.items():
            assert result[key] == value


class TestVINDecoderPerformance:
    """Test VIN decoder performance"""
    
    @pytest.fixture
    def decoder(self):
        return VINDecoder()
    
    @pytest.mark.benchmark
    def test_decode_performance(self, decoder, benchmark):
        """Benchmark VIN decoding performance"""
        vin = '1HGCM82633A004352'
        result = benchmark(decoder.decode, vin)
        assert result['error'] is None
    
    def test_bulk_decode_performance(self, decoder):
        """Test decoding multiple VINs efficiently"""
        vins = [
            '1HGCM82633A004352',
            'JTE123456789ABCDE',
            'WVWZZZ1JZ3W000000',
        ] * 100  # 300 VINs
        
        import time
        start = time.time()
        
        for vin in vins:
            decoder.decode(vin)
        
        elapsed = time.time() - start
        
        # Should decode 300 VINs in less than 1 second
        assert elapsed < 1.0


# Parametrized test for comprehensive brand coverage
@pytest.mark.parametrize("wmi,expected_brand", [
    ('1HG', 'Honda'), ('5FN', 'Honda'), ('JH2', 'Honda'),
    ('JTE', 'Toyota'), ('4T1', 'Toyota'), ('JTH', 'Lexus'),
    ('1FA', 'Ford'), ('1FM', 'Ford'), ('5L1', 'Lincoln'),
    ('1G1', 'Chevrolet'), ('1GC', 'GMC'), ('1G6', 'Cadillac'),
    ('1N4', 'Nissan'), ('JN1', 'Nissan'), ('JN3', 'Infiniti'),
    ('WVW', 'Volkswagen'), ('WBA', 'BMW'), ('WDD', 'Mercedes'),
    ('WAU', 'Audi'), ('KNA', 'Kia'), ('KMH', 'Hyundai'),
    ('JF1', 'Subaru'), ('JM1', 'Mazda'), ('WP0', 'Porsche'),
])
def test_comprehensive_wmi_mapping(wmi, expected_brand):
    """Test comprehensive WMI to brand mapping"""
    decoder = VINDecoder()
    assert decoder.wmi_to_brand[wmi] == expected_brand


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
