# ai/rules/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from ..utils.logging import logger
from ..core.evidence import EvidenceVector, EvidenceType

class DiagnosticIssue:
    def __init__(self, message: str, severity: str = "NORMAL", category: str = "GENERAL"):
        self.message = message
        self.severity = severity
        self.category = category

    def __str__(self):
        return f"[{self.severity}] {self.message}"

class RuleResult:
    def __init__(self, issues: List[DiagnosticIssue], confidence: float = 0.8):
        self.issues = issues
        self.confidence = confidence

class EvidenceResult:
    """Result from evidence-generating rules"""
    def __init__(self, evidence_vector: EvidenceVector, confidence: float = 1.0):
        self.evidence_vector = evidence_vector
        self.confidence = confidence

class BaseRule(ABC):
    """Base class for diagnostic rules."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def evaluate(self, data: Dict[str, Any]) -> Optional[RuleResult]:
        """Evaluate the rule against the provided data."""
        pass

    def _extract_parameter(self, data: Dict[str, Any], param_name: str, default: Any = None) -> Any:
        """Helper to extract parameter values from live data."""
        params = data.get("live_parameters", {})
        param_data = params.get(param_name, {})
        return param_data.get("value", default)

class EvidenceRule(ABC):
    """Base class for evidence-generating rules."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def evaluate_evidence(self, data: Dict[str, Any]) -> Optional[EvidenceResult]:
        """Evaluate evidence from the provided data."""
        pass

    def _extract_parameter(self, data: Dict[str, Any], param_name: str, default: Any = None) -> Any:
        """Helper to extract parameter values from live data."""
        params = data.get("live_parameters", {})
        param_data = params.get(param_name, {})
        return param_data.get("value", default)

    def _check_threshold(self, value: float, threshold: float, comparison: str = "gt") -> bool:
        """Check if value meets threshold condition."""
        if comparison == "gt":
            return value > threshold
        elif comparison == "lt":
            return value < threshold
        elif comparison == "ge":
            return value >= threshold
        elif comparison == "le":
            return value <= threshold
        elif comparison == "eq":
            return value == threshold
        else:
            return False

class RuleEngine:
    """Engine for managing and executing diagnostic rules."""

    def __init__(self):
        self.rules: List[BaseRule] = []
        self.evidence_rules: List[EvidenceRule] = []

    def add_rule(self, rule: BaseRule):
        self.rules.append(rule)

    def add_evidence_rule(self, rule: EvidenceRule):
        self.evidence_rules.append(rule)

    def evaluate_all(self, data: Dict[str, Any]) -> List[DiagnosticIssue]:
        """Evaluate all rules and collect issues."""
        all_issues = []
        for rule in self.rules:
            try:
                result = rule.evaluate(data)
                if result and result.issues:
                    all_issues.extend(result.issues)
            except Exception as e:
                logger.warning(f"Rule {rule.name} failed: {e}")
        return all_issues

    def evaluate_evidence_all(self, data: Dict[str, Any]) -> EvidenceVector:
        """Evaluate all evidence rules and collect evidence."""
        combined_evidence = EvidenceVector()

        for rule in self.evidence_rules:
            try:
                result = rule.evaluate_evidence(data)
                if result and result.evidence_vector:
                    # Merge evidence from this rule
                    for name, evidence_item in result.evidence_vector.evidence.items():
                        combined_evidence.add_evidence(
                            name=name,
                            value=evidence_item.value,
                            evidence_type=evidence_item.evidence_type,
                            confidence=evidence_item.confidence
                        )
            except Exception as e:
                logger.warning(f"Evidence rule {rule.name} failed: {e}")

        return combined_evidence