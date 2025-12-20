# ai/core/diagnostic_trace.py

from typing import Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict, field
from .evidence import EvidenceVector

@dataclass
class DiagnosticTrace:
    """Complete trace of a diagnostic session with belief tracking"""

    # Required fields (no defaults)
    timestamp: str
    belief_before: Dict[str, float]

    # Optional fields (with defaults)
    agent: str = "Charlemaine"
    mode: str = "LOCAL OFFLINE AI"
    belief_after: Dict[str, float] = field(default_factory=dict)
    evidence_used: List[str] = field(default_factory=list)
    information_gain: float = 0.0
    diagnosis: str = ""
    confidence: float = 0.0
    severity: str = "UNKNOWN"
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiagnosticTrace':
        """Create from dictionary"""
        return cls(**data)

    def calculate_information_gain(self) -> float:
        """Calculate information gain from belief states"""
        import math

        def entropy(probs: Dict[str, float]) -> float:
            return -sum(p * math.log(p + 1e-9) for p in probs.values() if p > 0)

        prior_entropy = entropy(self.belief_before)
        posterior_entropy = entropy(self.belief_after)

        self.information_gain = prior_entropy - posterior_entropy
        return self.information_gain

    @classmethod
    def create_initial_trace(cls, belief_state: Dict[str, float]) -> 'DiagnosticTrace':
        """Create initial trace with prior beliefs"""
        return cls(
            timestamp=datetime.now().isoformat(),
            belief_before=belief_state.copy(),
            belief_after={},  # Will be filled after update
            evidence_used=[],
            information_gain=0.0,
            diagnosis="",
            confidence=0.0,
            severity="UNKNOWN",
            recommendations=[]
        )

    def finalize_trace(self, final_belief: Dict[str, float], evidence_used: List[str],
                      diagnosis: str, confidence: float, severity: str, recommendations: List[str]):
        """Finalize the trace with posterior beliefs and diagnostic outcome"""
        self.belief_after = final_belief.copy()
        self.evidence_used = evidence_used.copy()
        self.diagnosis = diagnosis
        self.confidence = confidence
        self.severity = severity
        self.recommendations = recommendations.copy()
        self.calculate_information_gain()