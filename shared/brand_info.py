#!/usr/bin/env python3
"""
Brand Information Module
Provides brand-specific information and utilities for DiagAutoClinicOS
Integrated with Enhanced Global Automotive Brand Database
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class BrandInfo:
    """Class for managing brand information with enhanced database integration"""

    def __init__(self):
        self.brand_info = {}
        # Import and use the enhanced brand database
        try:
            from brand_database import brand_database
            self.enhanced_db = brand_database
            logger.info("Enhanced brand database integrated successfully")
        except ImportError as e:
            logger.error(f"Failed to import enhanced brand database: {e}")
            self.enhanced_db = None

    def get_brand_info(self, brand_name: str) -> Dict:
        """Get comprehensive information for a specific brand"""
        # First try enhanced database
        if self.enhanced_db:
            try:
                enhanced_info = self.enhanced_db.get_brand_info(brand_name)
                if enhanced_info:
                    return enhanced_info
            except Exception as e:
                logger.warning(f"Enhanced database lookup failed for {brand_name}: {e}")
        
        # Fallback to local data
        return self.brand_info.get(brand_name, {})

    def add_brand_info(self, brand_name: str, info: Dict):
        """Add custom information for a brand (overrides/enhances database info)"""
        self.brand_info[brand_name] = info

    def get_all_brands(self) -> List[str]:
        """Get list of all supported brands"""
        if self.enhanced_db:
            try:
                return self.enhanced_db.get_brand_list()
            except Exception as e:
                logger.warning(f"Enhanced database brand list failed: {e}")
        
        # Fallback to local keys
        return list(self.brand_info.keys())

    def get_brands_by_region(self, region: str) -> List[str]:
        """Get all brands from a specific region"""
        if self.enhanced_db:
            try:
                return self.enhanced_db.get_brands_by_region(region)
            except Exception as e:
                logger.warning(f"Enhanced database region filter failed: {e}")
        
        # Fallback implementation
        return [brand for brand, info in self.brand_info.items() 
                if info.get('region') == region]

    def get_brands_by_protocol(self, protocol: str) -> List[str]:
        """Get brands that use a specific diagnostic protocol"""
        if self.enhanced_db:
            try:
                return self.enhanced_db.get_brands_by_protocol(protocol)
            except Exception as e:
                logger.warning(f"Enhanced database protocol filter failed: {e}")
        
        # Fallback implementation
        protocol_lower = protocol.lower()
        matched = []
        for brand, info in self.brand_info.items():
            for proto in info.get('diagnostic_protocols', []):
                if protocol_lower in proto.lower():
                    matched.append(brand)
                    break
        return matched

    def get_security_info(self, brand_name: str) -> Dict:
        """Get security requirements for a specific brand"""
        if self.enhanced_db:
            try:
                return self.enhanced_db.get_security_requirements(brand_name)
            except Exception as e:
                logger.warning(f"Enhanced database security info failed: {e}")
        
        # Fallback to local data
        brand_info = self.get_brand_info(brand_name)
        return {
            'security_level': brand_info.get('security_level', 1),
            'requires_security_code': brand_info.get('requires_security_code', False),
            'programming_tool': brand_info.get('programming_tool', 'Unknown')
        }

    def validate_access(self, brand_name: str, user_security_level: int) -> bool:
        """Validate if user has access to brand based on security level"""
        if self.enhanced_db:
            try:
                return self.enhanced_db.validate_brand_access(brand_name, user_security_level)
            except Exception as e:
                logger.warning(f"Enhanced database access validation failed: {e}")
        
        # Fallback: assume access if brand exists in local data
        return brand_name in self.brand_info or brand_name in self.get_all_brands()

    def get_brand_summary(self, brand_name: str) -> Dict:
        """Get a summary of brand information"""
        full_info = self.get_brand_info(brand_name)
        if not full_info:
            return {}
        
        return {
            'name': brand_name,
            'region': full_info.get('region', 'Unknown'),
            'market_share': full_info.get('market_share', 'Unknown'),
            'security_level': full_info.get('security_level', 1),
            'key_systems': full_info.get('key_systems', []),
            'diagnostic_protocols': full_info.get('diagnostic_protocols', []),
            'programming_tool': full_info.get('programming_tool', 'Unknown')
        }

# Global instance
brand_info_manager = BrandInfo()

# Compatibility functions
def get_brand_info(brand_name: str) -> Dict:
    """Get information for a specific brand"""
    return brand_info_manager.get_brand_info(brand_name)

def get_all_brands() -> List[str]:
    """Get list of all supported brands"""
    return brand_info_manager.get_all_brands()

def get_brands_by_region(region: str) -> List[str]:
    """Get all brands from a specific region"""
    return brand_info_manager.get_brands_by_region(region)

def get_brands_by_protocol(protocol: str) -> List[str]:
    """Get brands that use a specific diagnostic protocol"""
    return brand_info_manager.get_brands_by_protocol(protocol)

# Test function
if __name__ == "__main__":
    # Test the enhanced brand info system
    print("Enhanced Brand Information System Test")
    print("=" * 50)
    
    brands = get_all_brands()
    print(f"Total brands available: {len(brands)}")
    
    # Test brand info retrieval
    test_brands = ["Toyota", "BMW", "Tesla", "UnknownBrand"]
    for brand in test_brands:
        info = get_brand_info(brand)
        if info:
            summary = brand_info_manager.get_brand_summary(brand)
            print(f"\n{brand}:")
            print(f"  Region: {summary.get('region')}")
            print(f"  Market Share: {summary.get('market_share')}")
            print(f"  Security Level: {summary.get('security_level')}")
            print(f"  Key Systems: {', '.join(summary.get('key_systems', []))}")
        else:
            print(f"\n{brand}: Not found")
    
    # Test regional filter
    japanese_brands = get_brands_by_region("Japan")
    print(f"\nJapanese Brands: {', '.join(japanese_brands)}")
    
    # Test protocol filter
    can_brands = get_brands_by_protocol("CAN")
    print(f"\nCAN Protocol Brands: {len(can_brands)} brands")