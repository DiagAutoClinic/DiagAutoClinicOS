# ai/core/evidence.py

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

class EvidenceType(Enum):
    """Types of evidence that can be observed"""
    BOOLEAN = "boolean"  # True/False observations
    NUMERIC = "numeric"  # Numeric values with thresholds
    CATEGORICAL = "categorical"  # Discrete categories

@dataclass
class EvidenceItem:
    """Single piece of evidence"""
    name: str
    value: Any
    evidence_type: EvidenceType
    confidence: float = 1.0  # How confident we are in this evidence

class EvidenceVector:
    """Collection of evidence observations"""

    def __init__(self):
        self.evidence: Dict[str, EvidenceItem] = {}

    def add_evidence(self, name: str, value: Any, evidence_type: EvidenceType, confidence: float = 1.0):
        """Add a piece of evidence to the vector"""
        self.evidence[name] = EvidenceItem(name, value, evidence_type, confidence)

    def get_evidence(self, name: str) -> EvidenceItem:
        """Get evidence by name"""
        return self.evidence.get(name)

    def has_evidence(self, name: str) -> bool:
        """Check if evidence exists"""
        return name in self.evidence

    def get_all_evidence_names(self) -> List[str]:
        """Get list of all evidence names"""
        return list(self.evidence.keys())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            name: {
                "value": item.value,
                "type": item.evidence_type.value,
                "confidence": item.confidence
            }
            for name, item in self.evidence.items()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvidenceVector':
        """Create from dictionary"""
        vector = cls()
        for name, item_data in data.items():
            evidence_type = EvidenceType(item_data["type"])
            vector.add_evidence(
                name=name,
                value=item_data["value"],
                evidence_type=evidence_type,
                confidence=item_data.get("confidence", 1.0)
            )
        return vector

# Common evidence types for automotive diagnostics
AUTOMOTIVE_EVIDENCE_TYPES = {
    "coolant_temp_high": EvidenceType.BOOLEAN,
    "battery_voltage_low": EvidenceType.BOOLEAN,
    "dtc_present": EvidenceType.BOOLEAN,
    "rpm_instability": EvidenceType.BOOLEAN,
    "engine_misfire": EvidenceType.BOOLEAN,
    "fuel_pressure_low": EvidenceType.BOOLEAN,
    "oxygen_sensor_fault": EvidenceType.BOOLEAN,
    "catalytic_converter_efficiency": EvidenceType.NUMERIC,
    "transmission_slip": EvidenceType.BOOLEAN,
    "brake_system_warning": EvidenceType.BOOLEAN
}