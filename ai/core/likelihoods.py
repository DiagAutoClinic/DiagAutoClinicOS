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
            "brake_system_warning": 0.05,  # Brake issues are unrelated
            "lean_condition_detected": 0.6 # Lean condition often means engine issue
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
            "brake_system_warning": 0.1,   # Weak evidence
            "lean_condition_detected": 0.4 # Sensor faults (MAF/O2) cause lean indications
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
            "brake_system_warning": 0.4,   # Moderate evidence
            "lean_condition_detected": 0.1 # Electrical faults rarely cause lean directly
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
            "brake_system_warning": 0.02,  # Rare
            "lean_condition_detected": 0.01 # Lambda > 1.1 is NOT normal (Phase 1 Mandate)
        }

        # Phase 3: Lean Condition Hypotheses
        # "Mandatory categories: Air-side, Fuel-side, Sensor-bias"

        # Air-side: Vacuum Leak
        self.likelihoods["vacuum_leak"] = {
            "coolant_temp_high": 0.1,
            "battery_voltage_low": 0.05,
            "dtc_present": 0.8,            # P0171/P0174
            "rpm_instability": 0.7,        # Rough idle is common
            "engine_misfire": 0.4,         # Can cause lean misfire
            "fuel_pressure_low": 0.05,     # Unrelated
            "oxygen_sensor_fault": 0.1,    # O2 is working correctly reporting lean
            "transmission_slip": 0.01,
            "brake_system_warning": 0.01,
            "lean_condition_detected": 0.99 # Almost guaranteed
        }

        # Fuel-side: Fuel Starvation (Pump/Filter/Injectors)
        self.likelihoods["fuel_starvation"] = {
            "coolant_temp_high": 0.2,      # Lean can run hot
            "battery_voltage_low": 0.1,
            "dtc_present": 0.8,            # P0171, P0087
            "rpm_instability": 0.6,        # Stumbling
            "engine_misfire": 0.5,         # Lean misfire
            "fuel_pressure_low": 0.95,     # Defining characteristic
            "oxygen_sensor_fault": 0.1,
            "transmission_slip": 0.01,
            "brake_system_warning": 0.01,
            "lean_condition_detected": 0.99
        }

        # Sensor-bias: MAF Sensor Bias
        self.likelihoods["maf_bias"] = {
            "coolant_temp_high": 0.1,
            "battery_voltage_low": 0.05,
            "dtc_present": 0.7,            # P0171, maybe MAF codes
            "rpm_instability": 0.3,
            "engine_misfire": 0.2,
            "fuel_pressure_low": 0.05,
            "oxygen_sensor_fault": 0.2,
            "transmission_slip": 0.05,     # Bad load calculation can affect shifting
            "brake_system_warning": 0.01,
            "lean_condition_detected": 0.95 # Reporting less air -> less fuel -> actually lean? 
                                            # Wait, if MAF under-reports air, ECU injects less fuel. 
                                            # Real air > Reported air. 
                                            # Mixture becomes LEAN. Yes.
        }

        # Air-side: Exhaust Leak (Pre-O2)
        self.likelihoods["exhaust_leak"] = {
            "coolant_temp_high": 0.1,
            "battery_voltage_low": 0.05,
            "dtc_present": 0.6,
            "rpm_instability": 0.1,
            "engine_misfire": 0.1,
            "fuel_pressure_low": 0.05,
            "oxygen_sensor_fault": 0.3,    # Can mimic O2 fault
            "transmission_slip": 0.01,
            "brake_system_warning": 0.01,
            "lean_condition_detected": 0.9 # O2 sees fresh air -> reports lean
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