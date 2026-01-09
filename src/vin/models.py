"""
src/vin/models.py

Central shared data models and epistemology types for the entire VIN decoding pipeline.

Philosophy:
- Never return naked values
- Every field must carry provenance, confidence, and epistemological status
- "Do I know this, or am I inferring it?" is enforced structurally
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from datetime import datetime


class EpistemologicalStatus(Enum):
    """Core epistemological classification of any decoded value"""
    VERIFIED     = "verified"      # Multiple independent sources agree (highest trust)
    CONFIRMED    = "confirmed"     # Strong rule match + context, no conflict
    INFERRED     = "inferred"      # Pattern-based, market-aware guess
    CONFLICTED   = "conflicted"    # Multiple sources disagree
    UNKNOWN      = "unknown"       # No information available
    DEFERRED     = "deferred"      # Explicitly cannot be determined from VIN alone


class SourceType(Enum):
    """Where the information came from"""
    LAYER_0_SANITY        = "layer_0_sanity"
    LAYER_1_ISO           = "layer_1_iso"           # WMI, year, plant, serial
    LAYER_2_VDS_RULE      = "layer_2_vds_rule"      # OEM grammar patterns
    LAYER_3_MARKET        = "layer_3_market"
    COMMERCIAL_DB         = "commercial_db"         # TecDoc, JATO, etc.
    ECU_READ              = "ecu_read"              # Physical reality from vehicle
    BUILD_SHEET           = "build_sheet"
    PR_CODES              = "pr_codes"
    TRANSUNION_ZA         = "transunion_auto_za"    # ZA-specific authoritative
    OTHER                 = "other"


@dataclass
class FieldSource:
    """Provenance record for a single value or inference"""
    source_type: SourceType
    source_id: str                          # e.g. rule_id, API name, ECU parameter
    confidence: float                       # 0.0-1.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    notes: Optional[str] = None             # e.g. "Market hint ZA applied"


@dataclass
class EpistemologicalValue:
    """
    A value that is NEVER naked - always carries epistemology.
    This is the core building block of the entire system.
    """
    value: Any
    status: EpistemologicalStatus
    confidence: float                       # Final aggregated confidence (0.0-1.0)
    unit: Optional[str] = None              # e.g. "cc", "kW", None for strings
    sources: List[FieldSource] = field(default_factory=list)
    explanation: Optional[str] = None       # Human-readable audit trail
    conflicts: List[str] = field(default_factory=list)  # If conflicted

    @property
    def is_reliable(self) -> bool:
        """Quick helper: should this value be trusted for decisions?"""
        return self.status in (EpistemologicalStatus.VERIFIED, EpistemologicalStatus.CONFIRMED) \
               and self.confidence >= 0.90

    def add_source(self, source: FieldSource):
        """Append a new contributing source and update confidence/status if needed"""
        self.sources.append(source)
        # Naive aggregation example - can be made much smarter later
        self.confidence = max(s.confidence for s in self.sources) if self.sources else 0.0


@dataclass
class VinDecodeResult:
    """
    The final, rich output object returned by decode_vin().
    Every field is epistemologically annotated.
    """
    vin_normalized: str
    is_valid: bool                              # Layer 0 result

    # Layer 1 - deterministic ISO fields
    wmi: EpistemologicalValue
    manufacturer: EpistemologicalValue
    country_of_origin: EpistemologicalValue
    model_year: EpistemologicalValue
    assembly_plant_code: EpistemologicalValue
    assembly_plant: EpistemologicalValue
    serial_number: EpistemologicalValue

    # Layer 2+ - OEM grammar & inferred fields
    model: Optional[EpistemologicalValue] = None
    platform: Optional[EpistemologicalValue] = None
    engine_family: Optional[EpistemologicalValue] = None
    displacement_cc: Optional[EpistemologicalValue] = None
    fuel_type: Optional[EpistemologicalValue] = None
    cylinders: Optional[EpistemologicalValue] = None
    engine_config: Optional[EpistemologicalValue] = None  # V6, I4, etc.
    series: Optional[EpistemologicalValue] = None
    trim_level: Optional[EpistemologicalValue] = None
    body_type: Optional[EpistemologicalValue] = None
    assembly_location: Optional[EpistemologicalValue] = None    # e.g. "Rosslyn, South Africa"

    # Aggregated epistemology
    overall_confidence: float = 0.0
    epistemology_notes: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Calculate overall confidence (simple max for skeleton)"""
        values = [
            v for v in vars(self).values()
            if isinstance(v, EpistemologicalValue)
        ]
        if values:
            self.overall_confidence = max((v.confidence for v in values), default=0.0)


@dataclass
class DecodeContext:
    """Input context that can influence inference (Layer 3+)"""
    market_hint: Optional[str] = None           # "ZA", "EU", "US", etc.
    plate_number: Optional[str] = None          # Optional ZA plate
    known_vin_prefix: Optional[str] = None      # Sometimes used in workshops


# Helper factory functions (very useful in layers)
def verified_value(value: Any, source_id: str, confidence: float = 1.0, unit: Optional[str] = None) -> EpistemologicalValue:
    return EpistemologicalValue(
        value=value,
        unit=unit,
        status=EpistemologicalStatus.VERIFIED,
        confidence=confidence,
        sources=[FieldSource(SourceType.LAYER_1_ISO, source_id, confidence)]
    )


def inferred_value(value: Any, rule_id: str, confidence: float, meaning: Dict = None) -> EpistemologicalValue:
    return EpistemologicalValue(
        value=value,
        status=EpistemologicalStatus.INFERRED,
        confidence=confidence,
        sources=[FieldSource(SourceType.LAYER_2_VDS_RULE, rule_id, confidence)],
        explanation=f"Inferred from VDS rule {rule_id}"
    )