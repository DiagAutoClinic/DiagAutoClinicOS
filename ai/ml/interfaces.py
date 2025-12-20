# ai/ml/interfaces.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class PredictionResult:
    def __init__(self, diagnosis: str, confidence: float, severity: str, source: str):
        self.diagnosis = diagnosis
        self.confidence = confidence
        self.severity = severity
        self.source = source

class PredictorInterface(ABC):
    """Abstract interface for ML predictors.

    This interface is frozen. Changes must be backward compatible.
    """

    @abstractmethod
    def predict(self, data: Dict[str, Any]) -> Optional[PredictionResult]:
        """Perform prediction on input data."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the predictor is available for use."""
        pass