"""
src/vin/layer4_commercial_stub.py

Layer 4 — Commercial Knowledge Injectors (STUB / Placeholder)

This layer represents external commercial databases, APIs, or lookup services
that provide higher-confidence data when VIN-derived inference is weak.

In production this would call real APIs (e.g. TecDoc, JATO, TransUnion ZA, etc.).
For now it's a simple stub that simulates enrichment based on manufacturer + basic fields.
"""

from typing import Dict, Optional, List
from dataclasses import replace

from .models import (
    EpistemologicalValue,
    EpistemologicalStatus,
    FieldSource,
    SourceType,
    DecodeContext
)


# Simulated "commercial DB" lookup table (expandable mock data)
# In reality this would be replaced by real API calls or cached DB queries
COMMERCIAL_MOCK_DB = {
    "BMW": {
        "G20 330i": {
            "engine_family": "B58B30",
            "displacement_cc": 2998,
            "power_kw": 190,
            "model_year_range": [2019, 2026],
            "confidence": 0.97,
            "source": "TecDoc/JATO mock"
        },
        "X3 G01 (ZA)": {
            "assembly": "Rosslyn, South Africa",
            "engine_family": "B48/B58",
            "market_specific": "ZA spec (emissions)",
            "confidence": 0.96,
            "source": "TransUnion Auto mock"
        }
    },
    "Mercedes-Benz": {
        "C-Class W205/W206": {
            "engine_family": "OM654 / M264",
            "displacement_cc": 1950,  # common diesel
            "confidence": 0.95
        }
    }
    # Add more as needed
}


def commercial_enrichment_stub(
    vin_normalized: str,
    manufacturer: str,
    model_year: Optional[int] = None,
    context: DecodeContext = None
) -> tuple[Dict[str, EpistemologicalValue], List[str], List[str]]:
    """
    Layer 4 stub: Simulate enrichment from commercial databases.
    
    Returns:
        - enriched_fields: dict of field_name → EpistemologicalValue
        - notes
        - warnings
    """
    notes = ["Layer 4 (commercial) is currently a placeholder/stub"]
    warnings = []
    enriched = {}

    if not manufacturer or manufacturer == "Unknown Manufacturer":
        notes.append("No manufacturer identified → skipping commercial enrichment")
        return enriched, notes, warnings

    mfr_key = manufacturer.upper()

    # Simulate lookup (very naive – real version would use VIN + year + market)
    mock_entries = COMMERCIAL_MOCK_DB.get(mfr_key, {})

    if not mock_entries:
        notes.append(f"No commercial mock data for manufacturer '{mfr_key}'")
        return enriched, notes, warnings

    # Very basic matching (in reality: API call with VIN prefix + year + market)
    matched_key = None
    if "G20" in vin_normalized or "330i" in vin_normalized:  # silly heuristic
        matched_key = "G20 330i"
    elif "X3" in vin_normalized and context and context.market_hint == "ZA":
        matched_key = "X3 G01 (ZA)"
    elif "C-Class" in vin_normalized:
        matched_key = "C-Class W205/W206"

    if matched_key:
        data = mock_entries[matched_key]
        conf = data.get("confidence", 0.90)

        for key, value in data.items():
            if key in ("confidence", "source"):
                continue

            status = EpistemologicalStatus.VERIFIED if conf >= 0.95 else EpistemologicalStatus.CONFIRMED

            ev = EpistemologicalValue(
                value=value,
                status=status,
                confidence=conf,
                sources=[
                    FieldSource(
                        source_type=SourceType.COMMERCIAL_DB,
                        source_id=f"mock_{matched_key}",
                        confidence=conf,
                        notes=f"Simulated commercial DB entry for {mfr_key}"
                    )
                ],
                explanation=f"Commercial stub enrichment for '{matched_key}'"
            )

            enriched[key] = ev

        notes.append(f"Commercial stub matched: {matched_key} (conf: {conf:.2f})")
    else:
        notes.append("No matching commercial mock entry found")

    return enriched, notes, warnings