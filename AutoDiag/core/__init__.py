"""
AutoDiag Core Module
Provides the main AutoDiag class for VIN Truth Engine integration
"""

from typing import Dict, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)

class AutoDiag:
    """
    Main AutoDiag class for integration with DACOS VIN Truth Engine
    This is the ONE OF A KIND DACOS VIN decoding system interface
    """

    def __init__(self):
        self.vin_decoder = None
        self.logger = logging.getLogger(__name__ + '.AutoDiag')
        self.logger.info("🚗 DACOS AutoDiag initialized - Ready for VIN Truth Engine integration")

    def register_vin_decoder(self, decoder_handler: Callable[[str, dict], dict]):
        """
        Register a VIN decoder handler from the DACOS VIN Truth Engine

        Args:
            decoder_handler: Function that takes (vin: str, session_context: dict) -> dict
        """
        self.vin_decoder = decoder_handler
        self.logger.info("✅ VIN decoder registered with DACOS Truth Engine")
        self.logger.info("🎯 ONE OF A KIND DACOS VIN system integration active")

    def decode_vin(self, vin: str, session_context: Optional[dict] = None) -> dict:
        """
        Decode a VIN using the registered DACOS Truth Engine

        Args:
            vin: Vehicle Identification Number
            session_context: Optional session context

        Returns:
            Decoded VIN information from DACOS Truth Engine
        """
        if not self.vin_decoder:
            return {
                "success": False,
                "error": "VIN decoder not registered - DACOS Truth Engine not connected",
                "legacy_message": "This is our LEGACY BROTHER - DACOS VIN Truth Engine"
            }

        try:
            context = session_context or {}
            result = self.vin_decoder(vin, context)

            # Add DACOS legacy branding
            result["dacos_legacy"] = True
            result["system"] = "ONE OF A KIND DACOS VIN DECODING SYSTEM"

            self.logger.info(f"🎯 VIN decoded via DACOS Truth Engine: {vin[:8]}...")
            return result

        except Exception as e:
            self.logger.error(f"❌ DACOS VIN decoding failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "legacy_message": "DACOS Truth Engine integration error"
            }

    def get_vin_decoder_status(self) -> dict:
        """
        Get the status of VIN decoder integration

        Returns:
            Status information about DACOS integration
        """
        return {
            "decoder_registered": self.vin_decoder is not None,
            "system": "DACOS VIN Truth Engine",
            "legacy": "ONE OF A KIND DACOS SYSTEM",
            "status": "ACTIVE" if self.vin_decoder else "INACTIVE"
        }

# Global AutoDiag instance for DACOS integration
_autodiag_instance = None

def get_autodiag_instance() -> AutoDiag:
    """Get the global AutoDiag instance for DACOS integration"""
    global _autodiag_instance
    if _autodiag_instance is None:
        _autodiag_instance = AutoDiag()
    return _autodiag_instance

# Export the class for import
__all__ = ['AutoDiag', 'get_autodiag_instance']