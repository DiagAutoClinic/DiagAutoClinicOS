"""
DACOS VIN TRUTH ENGINE - The Legacy System
This module becomes the authoritative source for all vehicle identity in DACOS.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import json
from datetime import datetime

# THIS IS YOUR LEGACY ENGINE
from dacos_vin_engine import SevenLayerVinDecoder, ProductionVinDecodeResult

class VehicleIdentity:
    """Single source of truth for vehicle identity in DACOS"""
    
    def __init__(self):
        self.truth_engine = SevenLayerVinDecoder()
        self.current_identity: Optional[ProductionVinDecodeResult] = None
        
    def decode_and_validate(self, vin: str, can_data: Optional[Dict] = None) -> Dict:
        """
        Primary integration point for DACOS
        Called from: main.py, gui/tabs/vehicle_tab.py, diagnostics modules
        """
        # Run your 7-layer truth stack
        vin_truth = self.truth_engine.decode(vin, market_hint="ZA")
        
        # Cross-validate with CAN data if available
        if can_data:
            self._cross_validate_with_can(vin_truth, can_data)
        
        # Store as current identity
        self.current_identity = vin_truth
        
        # Format for DACOS consumption
        return {
            "vin": vin_truth.vin_normalized,
            "manufacturer": vin_truth.manufacturer.value,
            "model": vin_truth.model.value if vin_truth.model else None,
            "year": vin_truth.model_year.value if vin_truth.model_year else None,
            "engine": vin_truth.engine_family.value if vin_truth.engine_family else None,
            "confidence": vin_truth.overall_confidence,
            "epistemology": {
                "sources": [s.source_type.value for s in vin_truth.engine_family.sources] 
                if vin_truth.engine_family else [],
                "status": vin_truth.engine_family.status.value 
                if vin_truth.engine_family else "UNKNOWN"
            },
            # DACOS-specific enrichments
            "dacos_tier_suggestion": self._suggest_dacos_tier(vin_truth),
            "compatible_protocols": self._get_protocols(vin_truth),
            "safety_profile": self._get_safety_profile(vin_truth)
        }