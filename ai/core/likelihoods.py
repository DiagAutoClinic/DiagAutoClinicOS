# ai/core/likelihoods.py

from typing import Dict, Any, List
import numpy as np
from .evidence import EvidenceVector, EvidenceItem, EvidenceType

class LikelihoodTable:
    """Likelihood table P(E|H) for Bayesian updates"""

    def __init__(self):
        # P(E|H) - probability of evidence given hypothesis
        self.likelihoods: Dict[str, Dict[str, float]] = {}

        # Initialize with handcrafted automotive diagnostic likelihoods
        self._initialize_automotive_likelihoods()

    def _initialize_automotive_likelihoods(self):
        """Initialize likelihoods for common automotive faults"""

        # Engine issue likelihoods
        self.likelihoods["engine_issue"] = {
            "coolant_temp_high": 0.8,      # High coolant temp is strong evidence for engine issues
            "battery_voltage_low": 0.2,    # Low voltage is weak evidence for engine issues
            "dtc_present": 0.7,            # DTCs are common with engine issues
            "rpm_instability": 0.9,        # RPM instability is very strong evidence
            "engine_misfire": 0.85,        # Misfire is strong evidence
            "fuel_pressure_low": 0.6,      # Low fuel pressure can indicate engine issues
            "oxygen_sensor_fault": 0.4,    # O2 sensor issues can be related
            "transmission_slip": 0.1,      # Transmission issues are unrelated
            "brake_system_warning": 0.05   # Brake issues are unrelated
        }

        # Sensor fault likelihoods
        self.likelihoods["sensor_fault"] = {
            "coolant_temp_high": 0.3,      # Moderate evidence (false positive from bad sensor)
            "battery_voltage_low": 0.1,    # Weak evidence
            "dtc_present": 0.9,            # DTCs very common with sensor faults
            "rpm_instability": 0.2,        # Weak evidence
            "engine_misfire": 0.1,         # Weak evidence
            "fuel_pressure_low": 0.2,      # Moderate evidence
            "oxygen_sensor_fault": 0.95,   # Very strong evidence
            "transmission_slip": 0.05,     # Unrelated
            "brake_system_warning": 0.1    # Weak evidence
        }

        # Electrical fault likelihoods
        self.likelihoods["electrical_fault"] = {
            "coolant_temp_high": 0.1,      # Weak evidence
            "battery_voltage_low": 0.9,    # Very strong evidence
            "dtc_present": 0.6,            # Moderate evidence
            "rpm_instability": 0.3,        # Moderate evidence
            "engine_misfire": 0.2,         # Weak evidence
            "fuel_pressure_low": 0.1,      # Weak evidence
            "oxygen_sensor_fault": 0.3,    # Moderate evidence
            "transmission_slip": 0.2,      # Weak evidence
            "brake_system_warning": 0.4    # Moderate evidence
        }

        # Normal operation likelihoods (baseline)
        self.likelihoods["normal_operation"] = {
            "coolant_temp_high": 0.05,     # Very rare in normal operation
            "battery_voltage_low": 0.1,    # Occasional but not strong evidence
            "dtc_present": 0.1,            # Some DTCs can be stored but not active
            "rpm_instability": 0.02,       # Very rare
            "engine_misfire": 0.01,        # Extremely rare
            "fuel_pressure_low": 0.03,     # Rare
            "oxygen_sensor_fault": 0.02,   # Rare
            "transmission_slip": 0.01,     # Extremely rare
            "brake_system_warning": 0.02   # Rare
        }

    def get_likelihood(self, hypothesis: str, evidence_name: str) -> float:
        """Get P(E|H) for specific hypothesis and evidence"""
        if hypothesis not in self.likelihoods:
            return 0.5  # Default neutral likelihood

        return self.likelihoods[hypothesis].get(evidence_name, 0.5)

    def get_all_hypotheses(self) -> List[str]:
        """Get all available hypotheses"""
        return list(self.likelihoods.keys())

    def get_evidence_for_hypothesis(self, hypothesis: str) -> Dict[str, float]:
        """Get all evidence likelihoods for a hypothesis"""
        return self.likelihoods.get(hypothesis, {})

    def update_likelihood(self, hypothesis: str, evidence_name: str, likelihood: float):
        """Update a specific likelihood value (for learning)"""
        if hypothesis not in self.likelihoods:
            self.likelihoods[hypothesis] = {}

        self.likelihoods[hypothesis][evidence_name] = likelihood

# Global likelihood table instance
likelihood_table = LikelihoodTable()