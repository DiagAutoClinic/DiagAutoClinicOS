#!/usr/bin/env python3
"""
DACOS Tier System Implementation
Authority-based tiering system for vehicle diagnostics
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class Tier(Enum):
    FREE = 1
    BASIC = 2
    INTERMEDIATE = 3
    PROFESSIONAL = 4
    ADVANCED = 5

class RiskLevel(Enum):
    NEGLIGIBLE = "Negligible"
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    EXTREME = "Extreme"

class TierSystem:
    """DACOS tier system based on CAN authority and risk transfer"""

    TIER_DEFINITIONS = {
        Tier.FREE: {
            "name": "Free",
            "description": "Observer",
            "price_zar": 0,
            "security_authority": "Generic OBD-II only, Read-only CAN frames, No ECU state mutation possible",
            "capabilities": [
                "VIN decoding", "Read / clear emission-related DTCs",
                "Live sensor data", "Snapshot logging"
            ],
            "risk_factor": RiskLevel.NEGLIGIBLE,
            "user_acknowledgement": None,
            "who_for": ["Verification", "Education", "Trust building", "Proving DACOS is real"]
        },
        Tier.BASIC: {
            "name": "Basic",
            "description": "Maintenance Operator",
            "price_zar": 249,
            "security_authority": "Limited CAN write access, No security codes, No gateway override",
            "capabilities": [
                "Service resets", "Maintenance-related functions", "Full-module DTC read/clear"
            ],
            "risk_factor": RiskLevel.LOW,
            "user_acknowledgement": "Implicit acceptance via subscription. No irreversible actions exposed.",
            "who_for": ["DIY users", "Roadside technicians", "Entry-level workshops"]
        },
        Tier.INTERMEDIATE: {
            "name": "Intermediate",
            "description": "System Influencer",
            "price_zar": 599,
            "security_authority": "Controlled write access, Learning and adaptation functions, Immobilizer-adjacent operations",
            "capabilities": [
                "Throttle learning", "Steering angle calibration", "Battery registration",
                "Actuator tests", "Limited immobilizer functions (where allowed)"
            ],
            "risk_factor": RiskLevel.MODERATE,
            "user_acknowledgement": "Mandatory before first use: 'I understand that learning and adaptation functions can affect vehicle behavior and may require corrective procedures or dealer intervention.'",
            "who_for": ["Independent workshops", "Diagnostic specialists", "Experienced technicians"]
        },
        Tier.PROFESSIONAL: {
            "name": "Professional",
            "description": "Vehicle Authority",
            "price_zar": 1299,
            "security_authority": "Dealer-level CAN access, Gateway-aware operations, Multi-bus control",
            "capabilities": [
                "System calibrations", "Bidirectional ECU control", "Secure gateway workflows",
                "Advanced diagnostics"
            ],
            "risk_factor": RiskLevel.HIGH,
            "user_acknowledgement": "Per session: 'I acknowledge that calibrations and bidirectional controls affect safety-critical systems and accept full responsibility for correct execution.'",
            "who_for": ["Professional diagnostic centers", "Specialist repair shops", "Non-dealer dealer-level operators"]
        },
        Tier.ADVANCED: {
            "name": "Advanced",
            "description": "System Architect",
            "price_zar": 2499,
            "security_authority": "Raw CAN frame injection, ECU coding and configuration, Full security-level access",
            "capabilities": [
                "Variant coding", "ECU parameter modification", "Custom CAN definitions",
                "Raw frame injection and replay", "Reverse engineering support"
            ],
            "risk_factor": RiskLevel.EXTREME,
            "user_acknowledgement": "Explicit & recurrent: Legal responsibility acceptance, Technical competence declaration, Jurisdiction compliance confirmation. Before every dangerous operation: 'I understand this action may permanently disable vehicle systems and accept all legal, financial, and safety consequences.'",
            "who_for": ["ECU engineers", "Security researchers", "Advanced coders", "People who know what a hex dump smells like"]
        }
    }

    @staticmethod
    def determine_tier(brand_data: Dict) -> Tuple[Tier, str]:
        """
        Determine tier based on brand CAN permissions and security level

        Args:
            brand_data: Brand information dictionary

        Returns:
            Tuple of (Tier, explanation_string)
        """
        try:
            can_arch = brand_data.get('can_architecture', {})
            frame_permissions = can_arch.get('frame_permissions', {})
            write_capable = frame_permissions.get('write_capable', [])
            security_level = brand_data.get('security_level', 1)
            requires_security_code = brand_data.get('requires_security_code', False)

            # Check for raw CAN write or coding (forces Tier 5)
            if 'raw_can_write' in write_capable or 'coding' in write_capable:
                return Tier.ADVANCED, "Raw CAN write or coding capabilities require Advanced tier"

            # Tier 1: Free - Read-only only
            if not write_capable:
                return Tier.FREE, "Read-only access only"

            # Tier 2: Basic - Limited write, no security codes
            if (set(write_capable).issubset({'clear_dtc', 'service_reset'}) and
                not requires_security_code):
                return Tier.BASIC, "Limited write access without security codes"

            # Tier 3: Intermediate - Write-capable with actuator_tests or ecu_configuration, security ≤ 3
            if (('actuator_tests' in write_capable or 'ecu_configuration' in write_capable) and
                security_level <= 3):
                return Tier.INTERMEDIATE, "Controlled write access with learning functions"

            # Tier 4: Professional - Security level 4 OR gateway-restricted ECUs present
            reachable_without_gateway = can_arch.get('reachable_ecus_without_gateway', [])
            has_gateway_restricted = len(reachable_without_gateway) < len(can_arch.get('common_ecus', []))

            if security_level == 4 or has_gateway_restricted:
                return Tier.PROFESSIONAL, "Dealer-level access or gateway-restricted ECUs"

            # Tier 5: Advanced - Security level 5 AND coding
            if security_level == 5 and 'coding' in write_capable:
                return Tier.ADVANCED, "Full security level with coding capabilities"

            # Default fallback based on security level
            if security_level >= 5:
                return Tier.ADVANCED, "High security level requires Advanced tier"
            elif security_level >= 4:
                return Tier.PROFESSIONAL, "Dealer-level security requires Professional tier"
            elif security_level >= 3:
                return Tier.INTERMEDIATE, "Intermediate security requires Intermediate tier"
            else:
                return Tier.BASIC, "Basic security level"

        except Exception as e:
            logger.error(f"Error determining tier for brand: {e}")
            return Tier.FREE, "Error determining tier, defaulting to Free"

    @staticmethod
    def get_tier_info(tier: Tier) -> Dict:
        """Get detailed information for a specific tier"""
        return TierSystem.TIER_DEFINITIONS.get(tier, {})

    @staticmethod
    def get_pricing_table() -> Dict[str, Dict]:
        """Get pricing table for all tiers"""
        return {
            tier.value: {
                "name": info["name"],
                "price_zar": info["price_zar"],
                "description": info["description"]
            }
            for tier, info in TierSystem.TIER_DEFINITIONS.items()
        }

    @staticmethod
    def requires_acknowledgement(tier: Tier) -> bool:
        """Check if tier requires user acknowledgement"""
        return tier.value >= 3  # Intermediate and above require acknowledgement

    @staticmethod
    def get_acknowledgement_text(tier: Tier) -> Optional[str]:
        """Get acknowledgement text for tier"""
        info = TierSystem.get_tier_info(tier)
        return info.get("user_acknowledgement")

    @staticmethod
    def validate_tier_access(user_tier: Tier, required_tier: Tier) -> bool:
        """Validate if user tier meets required tier"""
        return user_tier.value >= required_tier.value

    @staticmethod
    def get_brand_tier_explanation(brand_name: str, brand_data: Dict) -> str:
        """Generate explanation of why a brand is in its tier"""
        tier, reason = TierSystem.determine_tier(brand_data)
        tier_info = TierSystem.get_tier_info(tier)

        explanation = f"""
**{brand_name} - Tier {tier.value}: {tier_info['name']}**

**Why this tier?** {reason}

**Security Authority:** {tier_info['security_authority']}

**Capabilities:**
{chr(10).join(f"• {cap}" for cap in tier_info['capabilities'])}

**Risk Factor:** {tier_info['risk_factor'].value}

**Price:** R{tier_info['price_zar']} / month
"""
        if tier_info['user_acknowledgement']:
            explanation += f"\n**User Acknowledgement Required:** {tier_info['user_acknowledgement']}"

        explanation += f"\n**Who this is for:** {', '.join(tier_info['who_for'])}"

        return explanation.strip()

# Global tier system instance
tier_system = TierSystem()

# Convenience functions
def get_brand_tier(brand_data: Dict) -> Tier:
    """Get tier for brand data"""
    return tier_system.determine_tier(brand_data)[0]

def get_tier_price(tier: Tier) -> int:
    """Get price for tier in ZAR"""
    return tier_system.get_tier_info(tier).get("price_zar", 0)

if __name__ == "__main__":
    # Test tier system
    print("DACOS Tier System Test")
    print("=" * 50)

    # Test with sample brand data
    test_brand = {
        "security_level": 5,
        "requires_security_code": True,
        "can_architecture": {
            "frame_permissions": {
                "write_capable": ["ecu_configuration", "coding"]
            }
        }
    }

    tier, reason = tier_system.determine_tier(test_brand)
    print(f"Tier: {tier.name} (Level {tier.value})")
    print(f"Reason: {reason}")

    explanation = tier_system.get_brand_tier_explanation("BMW", test_brand)
    print(f"\n{explanation}")