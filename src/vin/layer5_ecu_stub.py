"""
src/vin/layer5_ecu_stub.py

Layer 5 — ECU Cross-Validation (STUB / Placeholder)

This is the highest epistemological layer: physical reality from the vehicle.
When ECU data is available, it overrides all lower layers (VIN inference, commercial DB, etc.).

In production this would:
- Read VIN + engine codes + other parameters from the vehicle's ECU (via OBD-II/DoIP/etc.)
- Perform hash-based attestation if possible
- Cross-validate against Layers 1–4

For now it's a simple stub that simulates ECU feedback.
"""

from typing import Dict, Optional, List, Tuple
from dataclasses import replace

from .models import (
    EpistemologicalValue,
    EpistemologicalStatus,
    FieldSource,
    SourceType,
    DecodeContext
)


# Simulated "ECU read" mock data (keyed by example VIN prefixes)
# In reality this would come from actual OBD-II / diagnostic tool read
ECU_MOCK_DATA = {
    "WBA5A7": {  # BMW G20 330i example
        "ecu_vin": "WBA5A7C54FG142391",
        "engine_family": "B58B30M0",
        "displacement_cc": 2998,
        "power_kw": 190,
        "fuel_type": "Petrol",
        "production_date": "2020-06",
        "confidence": 1.00,
        "source": "ECU direct read (simulated)",
        "matches_lower_layers": True
    },
    "AAU59": {  # ZA Rosslyn X3 example
        "ecu_vin": "AAU59... (partial)",
        "engine_family": "B48B20",
        "displacement_cc": 1998,
        "assembly": "Rosslyn, South Africa",
        "market_specific": "ZA emissions",
        "confidence": 0.99,
        "source": "ECU direct read (simulated)",
        "matches_lower_layers": True
    },
    # Add more real patterns as you collect ECU data
}


def ecu_cross_validation_stub(
    vin_normalized: str,
    lower_layer_fields: Dict[str, EpistemologicalValue],  # from Layers 1–4
    context: DecodeContext = None
) -> Tuple[Dict[str, EpistemologicalValue], List[str], List[str]]:
    """
    Layer 5 stub: Simulate ECU read + cross-validation against lower layers.
    
    Returns:
        enriched_fields (overrides lower layers when conflict)
        notes
        warnings (especially on mismatches)
    """
    notes = ["Layer 5 (ECU) is currently a placeholder/stub"]
    warnings = []
    enriched = {}

    # Very basic VIN prefix matching (real version would use full ECU VIN read)
    prefix = vin_normalized[:6]  # first 6 chars usually enough for engine family
    mock_data = None

    for ecu_prefix, data in ECU_MOCK_DATA.items():
        if vin_normalized.startswith(ecu_prefix):
            mock_data = data
            break

    if not mock_data:
        notes.append("No ECU mock data available for this VIN prefix → Layer 5 skipped")
        return enriched, notes, warnings

    # Simulate ECU read success
    conf = mock_data.get("confidence", 1.00)
    notes.append(f"ECU stub match found (conf: {conf:.2f})")

    # Create high-trust values from "ECU"
    def ecu_value(key: str, value: any) -> EpistemologicalValue:
        return EpistemologicalValue(
            value=value,
            status=EpistemologicalStatus.VERIFIED,
            confidence=conf,
            sources=[
                FieldSource(
                    source_type=SourceType.ECU_READ,
                    source_id=f"ecu_stub_{key}",
                    confidence=conf,
                    notes="Direct ECU parameter read (simulated)"
                )
            ],
            explanation=f"Physical ECU reality: {key} = {value}"
        )

    # Map ECU data → enriched fields (will override lower layers)
    enriched["engine_family"] = ecu_value("engine_family", mock_data.get("engine_family"))
    enriched["displacement_cc"] = ecu_value("displacement_cc", mock_data.get("displacement_cc"))
    if "fuel_type" in mock_data:
        enriched["fuel_type"] = ecu_value("fuel_type", mock_data["fuel_type"])
    if "assembly" in mock_data:
        enriched["assembly_location"] = ecu_value("assembly_location", mock_data["assembly"])

    # Cross-check: warn on conflicts with lower layers
    for field, ecu_ev in enriched.items():
        if field in lower_layer_fields:
            lower_ev = lower_layer_fields[field]
            if lower_ev.value != ecu_ev.value:
                warnings.append(
                    f"CONFLICT DETECTED: {field} mismatch! "
                    f"Lower layers say '{lower_ev.value}' (conf {lower_ev.confidence:.2f}), "
                    f"ECU says '{ecu_ev.value}' (conf {ecu_ev.confidence:.2f}). "
                    "ECU overrides all lower layers."
                )

    notes.append("ECU cross-validation complete — overrides applied where present")

    return enriched, notes, warnings