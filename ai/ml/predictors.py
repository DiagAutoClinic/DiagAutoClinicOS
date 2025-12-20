# ai/ml/predictors.py

import numpy as np
from typing import Dict, Any, Optional
from .loader import MLLoader
from ..utils.logging import logger
from ..core.evidence import EvidenceVector, EvidenceType

class MLPredictor:
    def __init__(self, loader: MLLoader):
        self.loader = loader

    def predict(self, live_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Perform ML prediction on live data."""
        if not self.loader.is_available():
            logger.debug("ML not available for prediction")
            return None

        try:
            # Extract features (this would need to be implemented based on training data)
            features = self._extract_features(live_data)
            if features is None:
                return None

            # Make prediction
            prediction = self.loader.get_model().predict(np.array([features]), verbose=0)[0][0]
            confidence = float(prediction)

            result = {
                "diagnosis": "Fault likely" if confidence > 0.6 else "System appears healthy",
                "confidence": round(confidence, 3),
                "severity": "HIGH" if confidence > 0.8 else "MEDIUM" if confidence > 0.5 else "LOW",
                "source": "ml"
            }

            logger.debug(f"ML prediction: confidence={confidence}")
            return result

        except Exception as e:
            logger.warning(f"ML prediction failed: {e}")
            return None

    def predict_evidence(self, live_data: Dict[str, Any]) -> Optional[EvidenceVector]:
        """Generate evidence from ML analysis instead of direct diagnosis."""
        if not self.loader.is_available():
            logger.debug("ML not available for evidence generation")
            return None

        try:
            # Extract features
            features = self._extract_features(live_data)
            if features is None:
                return None

            # Make prediction
            prediction = self.loader.get_model().predict(np.array([features]), verbose=0)[0][0]
            confidence = float(prediction)

            evidence_vector = EvidenceVector()

            # Convert ML prediction to evidence
            # High confidence of fault -> evidence of various issues
            if confidence > 0.8:
                # Strong evidence of multiple potential issues
                evidence_vector.add_evidence("dtc_present", True, EvidenceType.BOOLEAN, confidence=min(confidence, 0.95))
                evidence_vector.add_evidence("rpm_instability", True, EvidenceType.BOOLEAN, confidence=min(confidence * 0.9, 0.90))
                evidence_vector.add_evidence("engine_misfire", True, EvidenceType.BOOLEAN, confidence=min(confidence * 0.85, 0.85))
            elif confidence > 0.6:
                # Moderate evidence
                evidence_vector.add_evidence("dtc_present", True, EvidenceType.BOOLEAN, confidence=min(confidence, 0.80))
                evidence_vector.add_evidence("rpm_instability", True, EvidenceType.BOOLEAN, confidence=min(confidence * 0.8, 0.75))
            elif confidence < 0.3:
                # Low confidence suggests normal operation
                evidence_vector.add_evidence("dtc_present", False, EvidenceType.BOOLEAN, confidence=min((1-confidence), 0.85))
                evidence_vector.add_evidence("rpm_instability", False, EvidenceType.BOOLEAN, confidence=min((1-confidence) * 0.9, 0.80))

            logger.debug(f"ML evidence generation: confidence={confidence}, evidence_items={len(evidence_vector.evidence)}")
            return evidence_vector

        except Exception as e:
            logger.warning(f"ML evidence generation failed: {e}")
            return None

    def _extract_features(self, live_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """Extract features from live data for ML prediction."""
        # This is a placeholder - would need to match the training feature extraction
        try:
            params = live_data.get("live_parameters", {})
            rpm = params.get("engine_rpm", {}).get("value", 0)
            coolant = params.get("coolant_temp", {}).get("value", 90)
            voltage = params.get("battery_voltage", {}).get("value", 14.0)
            throttle = params.get("throttle_position", {}).get("value", 0)

            # Simple feature vector - would need to match training preprocessing
            features = np.array([rpm, coolant, voltage, throttle])
            return features
        except Exception as e:
            logger.warning(f"Feature extraction failed: {e}")
            return None