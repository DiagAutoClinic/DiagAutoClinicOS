"""
DACOS Website Integration Module
ONE OF A KIND DACOS VIN DECODING SYSTEM - Website Integration

This module provides the interface for dacos.co.za to integrate with the
DACOS VIN Truth Engine API. It handles 47 manufacturers and captures
VIN data for Charlemaine's training.

LEGACY BROTHER - This is our immortal contribution to mankind and AI.
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib
import hmac
from pathlib import Path

logger = logging.getLogger(__name__)

class DACOSWebsiteIntegration:
    """
    Website integration for the ONE OF A KIND DACOS VIN system
    Handles communication between dacos.co.za and the VIN Truth Engine
    """

    def __init__(self, api_base_url: str = "http://localhost:8000",
                 api_key: Optional[str] = None):
        """
        Initialize DACOS website integration

        Args:
            api_base_url: Base URL of the VIN Truth Engine API
            api_key: Optional API key for authentication
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.manufacturers_supported = self._get_supported_manufacturers()

        logger.info("🎯 DACOS Website Integration initialized")
        logger.info(f"🔗 API Endpoint: {self.api_base_url}")
        logger.info(f"🏭 Manufacturers supported: {len(self.manufacturers_supported)}")
        logger.info("💫 ONE OF A KIND DACOS VIN system ready for dacos.co.za")

    def _get_supported_manufacturers(self) -> List[str]:
        """Get list of supported manufacturers (47 total)"""
        # This would ideally come from the API, but hardcoded for now
        return [
            "BMW", "Mercedes-Benz", "Audi", "Volkswagen", "Porsche",
            "Toyota", "Honda", "Nissan", "Ford", "Chevrolet", "GMC",
            "Jeep", "Chrysler", "Dodge", "Ram", "Cadillac", "Buick",
            "Lincoln", "Acura", "Infiniti", "Lexus", "Mazda", "Subaru",
            "Hyundai", "Kia", "Genesis", "Volvo", "Jaguar", "Land Rover",
            "Mini", "Smart", "Fiat", "Alfa Romeo", "Maserati", "Ferrari",
            "Lamborghini", "Bentley", "Rolls-Royce", "Aston Martin",
            "McLaren", "Tesla", "Rivian", "Lucid", "Polestar", "BYD",
            "NIO", "XPeng"  # 47 manufacturers
        ]

    def decode_vin(self, vin: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Decode a VIN using the DACOS Truth Engine

        Args:
            vin: Vehicle Identification Number
            context: Optional context (market, session info, etc.)

        Returns:
            Decoded VIN information with DACOS verification
        """
        try:
            # Prepare request
            payload = {
                "vin": vin.upper().strip(),
                "context": context or {},
                "source": "dacos_website",
                "timestamp": datetime.utcnow().isoformat()
            }

            # Add authentication if API key provided
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["X-API-Key"] = self.api_key
                # Create HMAC signature for security
                payload_str = json.dumps(payload, sort_keys=True)
                signature = hmac.new(
                    self.api_key.encode(),
                    payload_str.encode(),
                    hashlib.sha256
                ).hexdigest()
                headers["X-Signature"] = signature

            # Make API call - send VIN as JSON body
            url = f"{self.api_base_url}/api/vin-decoder.php"
            
            # Match PHP API expected format
            api_payload = {
                "vin": payload['vin'],
                "include_patterns": True,
                "enhanced_data": True,
                "ai_enhancement": True,
                "context": payload.get("context", {})
            }
            
            response = self.session.post(url, json=api_payload, headers=headers, timeout=30)

            if response.status_code == 200:
                result = response.json()

                # Capture VIN data for Charlemaine training
                self._capture_for_charlemaine_training(vin, result)

                # Add website-specific metadata and detailed VIN information
                result["website_integration"] = True
                result["dacos_legacy"] = True
                result["decoded_at"] = datetime.utcnow().isoformat()

                # Extract detailed vehicle information for website display
                decoded = result.get("data", {}).get("decoded", {})
                result["vehicle_details"] = self._extract_vehicle_details(decoded)

                logger.info(f"✅ VIN decoded via DACOS Truth Engine: {vin[:8]}...")
                return result

            else:
                error_msg = f"API call failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "vin": vin,
                    "dacos_legacy": True
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error calling DACOS API: {e}")
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "vin": vin,
                "dacos_legacy": True
            }
        except Exception as e:
            logger.error(f"Unexpected error in VIN decoding: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "vin": vin,
                "dacos_legacy": True
            }

    def verify_result_integrity(self, integrity_hash: str) -> Dict[str, Any]:
        """
        Verify the integrity of a previous decoding result

        Args:
            integrity_hash: Hash from previous decoding

        Returns:
            Verification result
        """
        try:
            url = f"{self.api_base_url}/api/v1/verify/{integrity_hash}"
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "verification": "FAILED",
                    "error": f"API returned {response.status_code}",
                    "dacos_legacy": True
                }

        except Exception as e:
            logger.error(f"Error verifying result integrity: {e}")
            return {
                "verification": "ERROR",
                "error": str(e),
                "dacos_legacy": True
            }

    def _capture_for_charlemaine_training(self, vin: str, result: Dict[str, Any]):
        """
        Capture VIN decoding data for Charlemaine's training

        This feeds the ONE OF A KIND DACOS system with real-world data
        to improve Charlemaine's diagnostic capabilities.
        """
        try:
            import os
            from pathlib import Path

            training_data = {
                "vin": vin,
                "decoded": result.get("data", {}).get("decoded", {}),
                "integrity_hash": result.get("data", {}).get("integrity", {}).get("integrity_proof"),
                "timestamp": datetime.utcnow().isoformat(),
                "source": "dacos_website_integration",
                "manufacturer_count": len(self.manufacturers_supported),
                "vin_hash": hashlib.sha256(vin.encode()).hexdigest()[:16]  # Anonymized VIN for training
            }

            # Create training data directory if it doesn't exist
            training_dir = Path("charlemaine_training_data")
            training_dir.mkdir(exist_ok=True)

            # Save to daily training file
            today = datetime.utcnow().strftime("%Y%m%d")
            training_file = training_dir / f"vin_training_{today}.jsonl"

            # Append to JSON Lines file for efficient streaming
            with open(training_file, 'a', encoding='utf-8') as f:
                json.dump(training_data, f, ensure_ascii=False)
                f.write('\n')

            # Also save to a rolling buffer for Charlemaine's immediate use
            buffer_file = training_dir / "latest_training_buffer.jsonl"
            with open(buffer_file, 'a', encoding='utf-8') as f:
                json.dump(training_data, f, ensure_ascii=False)
                f.write('\n')

            # Keep buffer to last 1000 entries for memory efficiency
            self._maintain_training_buffer(buffer_file, max_entries=1000)

            logger.info(f"📚 Captured VIN data for Charlemaine training: {vin[:8]}... ({len(self.manufacturers_supported)} manufacturers)")

        except Exception as e:
            logger.warning(f"Failed to capture training data for Charlemaine: {e}")

    def _maintain_training_buffer(self, buffer_file: Path, max_entries: int = 1000):
        """Maintain the training buffer to prevent it from growing too large"""
        try:
            if not buffer_file.exists():
                return

            # Read all lines
            with open(buffer_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Keep only the most recent entries
            if len(lines) > max_entries:
                lines = lines[-max_entries:]

                # Rewrite the file
                with open(buffer_file, 'w', encoding='utf-8') as f:
                    f.writelines(lines)

        except Exception as e:
            logger.warning(f"Failed to maintain training buffer: {e}")

    def _extract_vehicle_details(self, decoded: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract detailed vehicle information for website display

        This provides comprehensive vehicle details including WMI, VDS, VIS information
        to attract users and feed the Charlemaine training database.
        """
        details = {
            "vin_segments": {
                "wmi": decoded.get("iso", {}).get("wmi", {}).get("value", ""),
                "vds": decoded.get("iso", {}).get("vds", {}).get("value", ""),
                "vis": decoded.get("iso", {}).get("vis", {}).get("value", "")
            },
            "basic_info": {
                "brand": decoded.get("manufacturer", {}).get("value", "Unknown"),
                "make": decoded.get("manufacturer", {}).get("value", "Unknown"),
                "model": decoded.get("model", {}).get("value", "Unknown"),
                "engine_type_capacity": self._format_engine_info(decoded.get("engine", {})),
                "plant": decoded.get("vis_details", {}).get("details", {}).get("plant", {}).get("value", "Unknown"),
                "manufacture_year": decoded.get("vis_details", {}).get("details", {}).get("model_year", {}).get("value", "Unknown"),
                "series": decoded.get("vis_details", {}).get("details", {}).get("series", {}).get("value") or
                        decoded.get("model", {}).get("details", {}).get("series", "Unknown"),
                "transmission": decoded.get("vis_details", {}).get("details", {}).get("transmission", {}).get("value", "Unknown"),
                "gearbox_type_model": decoded.get("vis_details", {}).get("details", {}).get("gearbox", {}).get("value", "Unknown")
            },
            "confidence_scores": {
                "overall": decoded.get("overall_confidence", 0.0),
                "manufacturer": decoded.get("manufacturer", {}).get("confidence", 0.0),
                "model": decoded.get("model", {}).get("confidence", 0.0),
                "engine": decoded.get("engine", {}).get("confidence", 0.0),
                "vis_details": decoded.get("vis_details", {}).get("confidence", 0.0)
            },
            "additional_specs": {
                "market": decoded.get("market", {}).get("value", "Unknown"),
                "body_type": decoded.get("model", {}).get("details", {}).get("body_type", "Unknown"),
                "trim_level": decoded.get("model", {}).get("details", {}).get("trim_level", "Unknown"),
                "engine_displacement_cc": decoded.get("engine", {}).get("details", {}).get("displacement_cc"),
                "fuel_type": decoded.get("engine", {}).get("details", {}).get("fuel_type", "Unknown"),
                "aspiration": decoded.get("engine", {}).get("details", {}).get("aspiration", "Unknown"),
                "serial_number": decoded.get("vis_details", {}).get("details", {}).get("serial_number", {}).get("value", "Unknown")
            },
            "verification": {
                "cryptographic_hash": decoded.get("integrity", {}).get("integrity_proof", ""),
                "verification_level": decoded.get("epistemology", {}).get("verification_level", "UNKNOWN"),
                "recommended_uses": decoded.get("epistemology", {}).get("recommended_use", [])
            }
        }

        return details

    def _format_engine_info(self, engine_data: Dict[str, Any]) -> str:
        """Format engine information for display"""
        engine_type = engine_data.get("value", "Unknown")
        displacement = engine_data.get("details", {}).get("displacement_cc")
        fuel = engine_data.get("details", {}).get("fuel_type")
        aspiration = engine_data.get("details", {}).get("aspiration")

        parts = []
        if engine_type and engine_type != "Unknown":
            parts.append(engine_type)
        if displacement:
            parts.append(f"{displacement}cc")
        if fuel and fuel != "Unknown":
            parts.append(fuel)
        if aspiration and aspiration != "Unknown":
            parts.append(aspiration)

        return " ".join(parts) if parts else "Unknown"

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the status of the DACOS VIN Truth Engine system

        Returns:
            System status information
        """
        return {
            "system": "DACOS VIN Truth Engine",
            "integration": "Website (dacos.co.za)",
            "manufacturers_supported": len(self.manufacturers_supported),
            "api_endpoint": self.api_base_url,
            "legacy": "ONE OF A KIND DACOS SYSTEM",
            "status": "ACTIVE",
            "charlemaine_training": "ENABLED",
            "timestamp": datetime.utcnow().isoformat()
        }

    def batch_decode_vins(self, vins: List[str], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Batch decode multiple VINs for efficiency

        Args:
            vins: List of VINs to decode
            context: Optional context for all VINs

        Returns:
            List of decoding results
        """
        results = []
        for vin in vins:
            result = self.decode_vin(vin, context)
            results.append(result)

            # Small delay to be respectful to the API
            import time
            time.sleep(0.1)

        logger.info(f"📊 Batch decoded {len(vins)} VINs for dacos.co.za")
        return results


# Global website integration instance
_dacos_website_integration = None

def get_dacos_website_integration(api_base_url: str = "http://localhost:8000",
                                 api_key: Optional[str] = None) -> DACOSWebsiteIntegration:
    """
    Get the global DACOS website integration instance

    Args:
        api_base_url: Base URL of the VIN Truth Engine API
        api_key: Optional API key

    Returns:
        DACOSWebsiteIntegration instance
    """
    global _dacos_website_integration
    if _dacos_website_integration is None:
        _dacos_website_integration = DACOSWebsiteIntegration(api_base_url, api_key)
    return _dacos_website_integration


# Convenience functions for website use
def decode_vehicle_vin(vin: str, market: str = "ZA") -> Dict[str, Any]:
    """
    Convenience function for the website to decode VINs

    Args:
        vin: Vehicle Identification Number
        market: Market code (default: ZA for South Africa)

    Returns:
        Decoded VIN information
    """
    integration = get_dacos_website_integration()
    context = {"market": market, "source": "dacos_website"}
    return integration.decode_vin(vin, context)


def get_dacos_system_info() -> Dict[str, Any]:
    """Get DACOS system information for the website"""
    integration = get_dacos_website_integration()
    return integration.get_system_status()


if __name__ == "__main__":
    # Test the integration
    print("🧪 Testing DACOS Website Integration...")

    integration = DACOSWebsiteIntegration()

    # Test system status
    status = integration.get_system_status()
    print(f"📊 System Status: {status}")

    # Test VIN decoding (will fail without API running, but shows structure)
    test_vin = "1HGCM82633A123456"  # Honda Accord example
    result = integration.decode_vin(test_vin, {"market": "ZA"})
    print(f"🎯 VIN Decode Result: {result}")

    print("✅ DACOS Website Integration test complete")
    print("💫 ONE OF A KIND DACOS VIN system ready for dacos.co.za")