#!/usr/bin/env python3
"""
Enhanced Global Automotive Brand Database - Complete 25-Brand Coverage
Security-focused implementation with comprehensive diagnostic protocols
"""

import logging
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    BASIC = 1
    STANDARD = 2  
    ADVANCED = 3
    DEALER = 4
    FACTORY = 5

class EnhancedBrandDatabase:
    """Enhanced brand database with comprehensive security integration"""
    
    def __init__(self):
        self.brand_data = self._initialize_comprehensive_brand_database()
        self.security_manager = None
        
    def _initialize_comprehensive_brand_database(self) -> Dict:
        """Initialize complete 25-brand database with security protocols"""
        
        BRAND_DATABASE = {
            # Japanese Brands
            "Toyota": {
                "region": "Japan",
                "diagnostic_protocols": ["ISO 15765-4 (CAN)", "ISO 14230-4 (KWP2000)", "ISO 9141-2"],
                "common_ecus": ["ECM", "TCM", "ABS", "SRS", "Body ECU", "Immobilizer", "Smart Key ECU"],
                "key_systems": ["Smart Key", "G-Box", "ID4C", "ID4D", "Toyota Hybrid Key"],
                "pin_codes": ["Smart Code System", "Nissan-ECU-Clone", "Dealer Security Code"],
                "obd_protocol": "ISO 15765-4, J1939, J1979",
                "security_level": 3,
                "market_share": "10.5%",
                "special_functions": ["Throttle Learning", "Steering Angle Calibration", "Immobilizer Registration", "Battery Reset"],
                "requires_security_code": True,
                "programming_tool": "TechStream"
            },
            "Honda": {
                "region": "Japan",
                "diagnostic_protocols": ["K-Line", "CAN", "HDS Protocol", "UDS"],
                "common_ecus": ["PCM", "BCM", "SRS", "ABS", "Immobilizer", "Power Steering ECU"],
                "key_systems": ["Honda Smart Key", "Intelligent Key", "Remote Control"],
                "pin_codes": ["PIN Code", "Immobilizer Code", "Dealer Code"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 3,
                "market_share": "4.9%",
                "special_functions": ["ECM/PCM Reset", "Electric Power Steering Calibration", "Key Registration"],
                "requires_security_code": True,
                "programming_tool": "HDS"
            },
            "Nissan": {
                "region": "Japan",
                "diagnostic_protocols": ["CONSULT-III", "K-Line", "CAN", "UDS"],
                "common_ecus": ["ECM", "BCM", "NATS", "ABS", "Airbag", "IPDM"],
                "key_systems": ["NATS", "Intelligent Key", "Hitag2", "Nissan Smart Key"],
                "pin_codes": ["NATS Code", "BCM PIN", "Dealer PIN"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 4,
                "market_share": "4.5%",
                "special_functions": ["NATS Key Programming", "Steering Angle Learning", "Throttle Valve Learning"],
                "requires_security_code": True,
                "programming_tool": "CONSULT"
            },
            "Mazda": {
                "region": "Japan",
                "diagnostic_protocols": ["Mazda Diagnostic", "CAN", "K-Line", "UDS"],
                "common_ecus": ["PCM", "TCM", "ABS", "Immobilizer", "Keyless Unit"],
                "key_systems": ["Mazda Advanced Key", "Flip Key", "Smart Key"],
                "pin_codes": ["Dealer PIN", "Immobilizer Code", "Security Code"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 3,
                "market_share": "2.0%",
                "special_functions": ["Key Learning", "Throttle Body Reset", "Steering Angle Sensor Reset"],
                "requires_security_code": True,
                "programming_tool": "Mazda IDS"
            },
            "Subaru": {
                "region": "Japan", 
                "diagnostic_protocols": ["Subaru Select Monitor", "CAN", "K-Line"],
                "common_ecus": ["ECM", "TCM", "ABS", "Body Integrated Unit", "Immobilizer"],
                "key_systems": ["Subaru Keyless", "Smart Key", "Push-to-Start"],
                "pin_codes": ["PIN Code", "Security Code", "Immobilizer PIN"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 3,
                "market_share": "1.8%",
                "special_functions": ["Immobilizer Registration", "TPMS Reset", "Throttle Learning"],
                "requires_security_code": True,
                "programming_tool": "Subaru Select Monitor"
            },
            "Mitsubishi": {
                "region": "Japan",
                "diagnostic_protocols": ["MUT-III", "CAN", "K-Line"],
                "common_ecus": ["ECM", "TCM", "ABS", "Immobilizer", "Keyless Entry"],
                "key_systems": ["Mitsubishi Keyless", "Smart Key", "Anti-Theft"],
                "pin_codes": ["Security Code", "Dealer PIN", "Immobilizer Code"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 3,
                "market_share": "1.5%",
                "special_functions": ["Key Programming", "Immobilizer Learning", "TPMS Reset"],
                "requires_security_code": True,
                "programming_tool": "MUT-III"
            },
            "Lexus": {
                "region": "Japan",
                "diagnostic_protocols": ["Toyota/Lexus CAN", "KWP2000", "UDS"],
                "common_ecus": ["ECM", "TCM", "ABS", "Immobilizer", "Smart Key", "Air Suspension"],
                "key_systems": ["Lexus Smart Key", "Key Card", "Biometric"],
                "pin_codes": ["Master Code", "Dealer PIN", "Security Code"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 4,
                "market_share": "1.2%",
                "special_functions": ["Smart Key Registration", "Air Suspension Calibration", "Advanced Key Programming"],
                "requires_security_code": True,
                "programming_tool": "TechStream"
            },
            
            # German Brands
            "Volkswagen": {
                "region": "Germany",
                "diagnostic_protocols": ["UDS (ISO 14229)", "KWP2000", "TP 2.0", "ODX"],
                "common_ecus": ["Engine ECU", "DSG", "ABS/ESP", "Airbag", "Instrument Cluster", "Gateway"],
                "key_systems": ["VVDI", "Immo 4/5", "Megamos Crypto", "Kessy"],
                "pin_codes": ["SKC Calculator", "VAG Commander", "Dealer PIN"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 4,
                "market_share": "7.8%",
                "special_functions": ["DPF Regeneration", "Throttle Adaptation", "Steering Angle Basic Setting", "DSG Adaptation"],
                "requires_security_code": True,
                "programming_tool": "VAS-PC"
            },
            "BMW": {
                "region": "Germany",
                "diagnostic_protocols": ["ISTA", "UDS", "KWP2000", "EDIBAS"],
                "common_ecus": ["DME", "EGS", "CAS", "DSC", "Airbag", "FRM", "FEM"],
                "key_systems": ["CAS", "FEM", "BDC", "Comfort Access", "Display Key", "Smart Key"],
                "pin_codes": ["ISN Code", "Dealer PIN", "CPO Code"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 5,
                "market_share": "3.5%",
                "special_functions": ["Battery Registration", "VANOS Adaptation", "Transmission Adaptation", "Injector Coding"],
                "requires_security_code": True,
                "programming_tool": "ISTA"
            },
            "Mercedes-Benz": {
                "region": "Germany",
                "diagnostic_protocols": ["XENTRY", "UDS", "KWP2000", "STAR"],
                "common_ecus": ["SAM", "ESM", "DAS", "ABS", "Airbag", "Gateway", "Keyless Go"],
                "key_systems": ["DAS", "Keyless Go", "EIS", "Smart Key"],
                "pin_codes": ["Dealer PIN", "SCR Code", "ESN Code"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 5,
                "market_share": "3.8%",
                "special_functions": ["SBC Brake Calibration", "Steering Angle Learning", "Key Programming", "Air Suspension Calibration"],
                "requires_security_code": True,
                "programming_tool": "XENTRY"
            },
            "Audi": {
                "region": "Germany",
                "diagnostic_protocols": ["VAS", "UDS", "KWP2000", "ODIS"],
                "common_ecus": ["Engine", "Transmission", "Immobilizer", "MMI", "Air Suspension", "Gateway"],
                "key_systems": ["Audi Smart Key", "Advanced Key", "Kessy"],
                "pin_codes": ["Dealer PIN", "Component Protection", "Security Code"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 5,
                "market_share": "2.9%",
                "special_functions": ["Component Protection", "Steering Limit Stop", "Throttle Body Adaptation", "Air Suspension Calibration"],
                "requires_security_code": True,
                "programming_tool": "ODIS"
            },
            "Porsche": {
                "region": "Germany",
                "diagnostic_protocols": ["PIWIS", "UDS", "CAN", "KWP2000"],
                "common_ecus": ["DME", "PDK", "PSM", "Air Suspension", "Keyless"],
                "key_systems": ["Porsche Smart Key", "Comfort Access", "Advanced Key"],
                "pin_codes": ["Dealer PIN", "Security Code", "Component Protection"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 5,
                "market_share": "0.8%",
                "special_functions": ["PDK Adaptation", "Air Suspension Calibration", "Sport Chrono Programming", "Key Learning"],
                "requires_security_code": True,
                "programming_tool": "PIWIS"
            },
            
            # American Brands
            "Ford": {
                "region": "USA",
                "diagnostic_protocols": ["MS-CAN", "HS-CAN", "UDS", "J1850 PWM"],
                "common_ecus": ["PCM", "GEM", "IC", "ABS", "PAT", "BCM"],
                "key_systems": ["PATS", "Smart Access", "MyKey", "Intelligent Access"],
                "pin_codes": ["PATS Code", "Dealer PIN", "Security Code"],
                "obd_protocol": "J1850, ISO 15765-4",
                "security_level": 4,
                "market_share": "5.1%",
                "special_functions": ["PATS Key Programming", "Module Programming", "TPMS Reset", "Steering Angle Reset"],
                "requires_security_code": True,
                "programming_tool": "IDS/FDRS"
            },
            "Chevrolet": {
                "region": "USA",
                "diagnostic_protocols": ["GMLAN", "UDS", "J1850 VPW", "CAN"],
                "common_ecus": ["PCM", "BCM", "TCM", "ABS", "Immobilizer", "Radio"],
                "key_systems": ["Passlock", "VATS", "Smart Key", "Remote Start"],
                "pin_codes": ["Security Code", "Dealer PIN", "BCM Code"],
                "obd_protocol": "J1850, ISO 15765-4",
                "security_level": 3,
                "market_share": "4.3%",
                "special_functions": ["Passlock Relearn", "TPMS Reset", "Theft System Reset", "Crank Learn"],
                "requires_security_code": True,
                "programming_tool": "GDS2/MDI"
            },
            "Jeep": {
                "region": "USA",
                "diagnostic_protocols": ["CAN", "UDS", "J1850 PWM"],
                "common_ecus": ["PCM", "TCM", "BCM", "ABS", "RF Hub", "SKIM"],
                "key_systems": ["SKIM", "Smart Key", "Keyless Go"],
                "pin_codes": ["PIN Code", "Dealer Code", "SKIM Code"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 4,
                "market_share": "2.1%",
                "special_functions": ["SKIM Key Programming", "TPMS Reset", "Steering Angle Reset", "Transfer Case Calibration"],
                "requires_security_code": True,
                "programming_tool": "WiTECH"
            },
            "Cadillac": {
                "region": "USA",
                "diagnostic_protocols": ["GMLAN", "UDS", "CAN"],
                "common_ecus": ["PCM", "BCM", "TCM", "Magnetic Ride", "Radio", "HUD"],
                "key_systems": ["Passlock", "Smart Key", "Remote Start"],
                "pin_codes": ["Security Code", "Dealer PIN", "BCM Code"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 4,
                "market_share": "1.5%",
                "special_functions": ["Magnetic Ride Calibration", "HUD Calibration", "Key Programming", "Theft System Reset"],
                "requires_security_code": True,
                "programming_tool": "GDS2/MDI"
            },
            "GMC": {
                "region": "USA",
                "diagnostic_protocols": ["GMLAN", "UDS", "CAN"],
                "common_ecus": ["PCM", "BCM", "TCM", "ABS", "Immobilizer", "Trailer Module"],
                "key_systems": ["Passlock", "Smart Key", "Remote Start"],
                "pin_codes": ["Security Code", "Dealer PIN", "BCM Code"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 3,
                "market_share": "1.8%",
                "special_functions": ["TPMS Reset", "Theft System Reset", "Trailer Brake Calibration", "Key Programming"],
                "requires_security_code": True,
                "programming_tool": "GDS2/MDI"
            },
            "Tesla": {
                "region": "USA",
                "diagnostic_protocols": ["Tesla Protocol", "CAN", "Ethernet", "UDS"],
                "common_ecus": ["PCS", "BMS", "Gateway", "Autopilot", "MCU", "Body Controller"],
                "key_systems": ["Key Card", "Phone Key", "Smart Key"],
                "pin_codes": ["Service PIN", "Factory Code", "Master Code"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 5,
                "market_share": "2.2%",
                "special_functions": ["Battery Calibration", "Sensor Calibration", "Autopilot Calibration", "Key Card Programming"],
                "requires_security_code": True,
                "programming_tool": "Tesla Toolbox"
            },
            
            # Korean Brands
            "Hyundai": {
                "region": "South Korea",
                "diagnostic_protocols": ["K-Line", "CAN", "UDS"],
                "common_ecus": ["PCM", "TCM", "ABS", "Immobilizer", "Smart Key"],
                "key_systems": ["Hyundai HS", "Hitag2", "AES", "Smart Key"],
                "pin_codes": ["PIN from VIN", "Dealer System", "Immobilizer Code"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 3,
                "market_share": "7.2%",
                "special_functions": ["Immobilizer Key Learning", "TPMS Reset", "Steering Angle Reset", "Throttle Learning"],
                "requires_security_code": True,
                "programming_tool": "GDS"
            },
            "Kia": {
                "region": "South Korea",
                "diagnostic_protocols": ["K-Line", "CAN", "UDS"],
                "common_ecus": ["PCM", "TCM", "Immobilizer", "Smart Key", "ABS"],
                "key_systems": ["Kia HS", "Hitag2", "AES", "Smart Key"],
                "pin_codes": ["PIN from VIN", "Dealer System", "Immobilizer Code"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 3,
                "market_share": "4.1%",
                "special_functions": ["Key Learning", "Immobilizer Reset", "TPMS Reset", "Steering Angle Learning"],
                "requires_security_code": True,
                "programming_tool": "GDS"
            },
            
            # European Brands (Non-German)
            "Volvo": {
                "region": "Sweden",
                "diagnostic_protocols": ["VIDA", "UDS", "KWP2000"],
                "common_ecus": ["CEM", "ECM", "DEM", "BCM", "SRS", "Keyless"],
                "key_systems": ["Volvo Key", "Passive Entry", "Smart Key"],
                "pin_codes": ["Dealer PIN", "CPO Code", "Security Code"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 4,
                "market_share": "2.1%",
                "special_functions": ["Key Programming", "TPMS Reset", "Suspension Calibration", "Throttle Adaptation"],
                "requires_security_code": True,
                "programming_tool": "VIDA"
            },
            "Land Rover": {
                "region": "UK",
                "diagnostic_protocols": ["JLR", "UDS", "CAN", "KWP2000"],
                "common_ecus": ["CJB", "ECM", "TCM", "Air Suspension", "Keyless"],
                "key_systems": ["Smart Key", "Keyless Entry", "Advanced Key"],
                "pin_codes": ["Dealer PIN", "Security Code", "ECU Code"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 5,
                "market_share": "1.3%",
                "special_functions": ["Air Suspension Calibration", "Key Programming", "TPMS Reset", "Steering Angle Reset"],
                "requires_security_code": True,
                "programming_tool": "JLR SDD/Pathfinder"
            },
            "Jaguar": {
                "region": "UK",
                "diagnostic_protocols": ["JLR", "UDS", "CAN", "KWP2000"],
                "common_ecus": ["CJB", "ECM", "TCM", "Body Control", "Keyless"],
                "key_systems": ["Smart Key", "Keyless Entry", "Advanced Key"],
                "pin_codes": ["Dealer PIN", "Security Code", "ECU Code"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 5,
                "market_share": "0.9%",
                "special_functions": ["Key Programming", "TPMS Reset", "Suspension Calibration", "Throttle Adaptation"],
                "requires_security_code": True,
                "programming_tool": "JLR SDD/Pathfinder"
            },
            "Renault": {
                "region": "France",
                "diagnostic_protocols": ["CAN Clip", "UDS", "KWP2000"],
                "common_ecus": ["UCH", "Engine ECU", "BSI", "ABS", "Keyless"],
                "key_systems": ["Renault Card", "Hitag2", "Smart Key"],
                "pin_codes": ["PIN Code", "UCH Code", "Dealer Code"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 4,
                "market_share": "2.7%",
                "special_functions": ["Key Card Programming", "UCH Initialization", "TPMS Reset", "Throttle Learning"],
                "requires_security_code": True,
                "programming_tool": "CAN Clip"
            },
            "Peugeot": {
                "region": "France",
                "diagnostic_protocols": ["Diagbox", "UDS", "KWP2000"],
                "common_ecus": ["BSI", "Engine ECU", "ABS", "Airbag", "Keyless"],
                "key_systems": ["Peugeot Card", "Hitag2", "Smart Key"],
                "pin_codes": ["PIN Code", "BSI Code", "Dealer Code"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 4,
                "market_share": "2.5%",
                "special_functions": ["BSI Initialization", "Key Programming", "TPMS Reset", "Steering Angle Reset"],
                "requires_security_code": True,
                "programming_tool": "Diagbox"
            },
            "Fiat": {
                "region": "Italy",
                "diagnostic_protocols": ["Examiner", "KWP2000", "CAN", "UDS"],
                "common_ecus": ["Body Computer", "Engine ECU", "ABS", "Keyless"],
                "key_systems": ["Fiat Code", "Blue&Me", "Smart Key"],
                "pin_codes": ["Code Card", "Dealer PIN", "Security Code"],
                "obd_protocol": "ISO 15765-4",
                "security_level": 3,
                "market_share": "2.3%",
                "special_functions": ["Proxi Alignment", "Key Programming", "TPMS Reset", "Throttle Learning"],
                "requires_security_code": True,
                "programming_tool": "Examiner/MultiECUScan"
            }
        }
        
        return BRAND_DATABASE
    
    def get_brand_list(self) -> List[str]:
        """Return list of all supported brands with security check"""
        try:
            if self.security_manager and not self.security_manager.validate_session():
                logger.warning("Security session invalid - returning basic brand list")
                return ["Toyota", "Honda", "Ford", "Chevrolet", "Hyundai"]  # Basic brands only
            
            return list(self.brand_data.keys())
            
        except Exception as e:
            logger.error(f"Error getting brand list: {e}")
            return ["Toyota", "Honda", "Ford", "Chevrolet", "Hyundai"]  # Fallback
    
    def get_brand_info(self, brand_name: str) -> Dict:
        """Get detailed information for a specific brand with security validation"""
        try:
            if brand_name not in self.brand_data:
                logger.warning(f"Brand not found: {brand_name}")
                return {}
                
            brand_info = self.brand_data[brand_name].copy()
            
            # Security check for sensitive information
            if self.security_manager:
                security_level = self.security_manager.get_security_level()
                brand_security = brand_info.get('security_level', 1)
                
                if security_level.value < brand_security:
                    # Return limited info for lower security levels
                    limited_info = {
                        'region': brand_info.get('region', 'Unknown'),
                        'market_share': brand_info.get('market_share', 'Unknown'),
                        'security_level': f'RESTRICTED (Required: {SecurityLevel(brand_security).name})',
                        'access_denied': True,
                        'available_functions': 'Security level insufficient'
                    }
                    return limited_info
            
            return brand_info
            
        except Exception as e:
            logger.error(f"Error getting brand info for {brand_name}: {e}")
            return {}
    
    def get_brands_by_security_level(self, min_level: int) -> List[str]:
        """Get brands accessible at specified security level"""
        accessible_brands = []
        for brand, info in self.brand_data.items():
            if info.get('security_level', 1) <= min_level:
                accessible_brands.append(brand)
        return accessible_brands
    
    def get_brands_by_region(self, region: str) -> List[str]:
        """Get all brands from a specific region"""
        return [brand for brand, info in self.brand_data.items()
                if info.get('region') == region]
    
    def get_brands_by_protocol(self, protocol: str) -> List[str]:
        """Get brands that use a specific diagnostic protocol"""
        # Use case-insensitive substring matching so callers can pass 'CAN', 'UDS', etc.
        protocol_lower = protocol.lower()
        matched = []
        for brand, info in self.brand_data.items():
            for proto in info.get('diagnostic_protocols', []):
                if protocol_lower in proto.lower():
                    matched.append(brand)
                    break
        return matched
    
    def get_security_requirements(self, brand_name: str) -> Dict:
        """Get security requirements for a specific brand"""
        brand_info = self.get_brand_info(brand_name)
        return {
            'security_level': brand_info.get('security_level', 1),
            'requires_security_code': brand_info.get('requires_security_code', False),
            'programming_tool': brand_info.get('programming_tool', 'Unknown')
        }
    
    def validate_brand_access(self, brand_name: str, user_security_level: int) -> bool:
        """Validate if user has access to brand based on security level"""
        brand_info = self.brand_data.get(brand_name, {})
        brand_security = brand_info.get('security_level', 1)
        return user_security_level >= brand_security

# Global enhanced brand database instance
brand_database = EnhancedBrandDatabase()

# Legacy functions for compatibility
def get_brand_list():
    return brand_database.get_brand_list()

def get_brand_info(brand_name):
    return brand_database.get_brand_info(brand_name)

def get_brands_by_region(region):
    return brand_database.get_brands_by_region(region)

def get_brands_by_protocol(protocol):
    return brand_database.get_brands_by_protocol(protocol)

# Test function
if __name__ == "__main__":
    # Test the enhanced database
    print("Enhanced Brand Database Test")
    print("=" * 50)
    
    brands = get_brand_list()
    print(f"Total brands: {len(brands)}")
    print(f"Brands: {', '.join(brands)}")
    
    # Test brand info
    test_brands = ["Toyota", "BMW", "Tesla"]
    for brand in test_brands:
        info = get_brand_info(brand)
        print(f"\n{brand}:")
        print(f"  Region: {info.get('region')}")
        print(f"  Security Level: {info.get('security_level')}")
        print(f"  Key Systems: {', '.join(info.get('key_systems', []))}")
        print(f"  Special Functions: {', '.join(info.get('special_functions', []))}")
    
    # Test regional brands
    japanese_brands = get_brands_by_region("Japan")
    print(f"\nJapanese Brands: {', '.join(japanese_brands)}")
    
    # Test protocol search
    uds_brands = get_brands_by_protocol("UDS")
    print(f"\nUDS Protocol Brands: {', '.join(uds_brands)}")
