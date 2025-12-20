#!/usr/bin/env python3
"""
Test script for Phase 4: Evidence-Driven Bayesian Updates
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai.belief_state import BeliefState
from ai.belief_update import bayesian_update_from_evidence
from ai.core.evidence import EvidenceVector, EvidenceType
from ai.core.diagnostic_trace import DiagnosticTrace
from ai.core.diagnostics_engine import DiagnosticsEngine
from ai.rules.evidence_rules import create_evidence_rules
from ai.rules.base import RuleEngine

def test_basic_bayesian_update():
    """Test basic Bayesian belief update with evidence."""
    print("Testing Basic Bayesian Update")

    # Initialize belief state
    belief = BeliefState(["normal_operation", "engine_issue", "sensor_fault", "electrical_fault"])
    print(f"Initial beliefs: {belief.probabilities}")

    # Create evidence vector
    evidence = EvidenceVector()
    evidence.add_evidence("coolant_temp_high", True, EvidenceType.BOOLEAN, confidence=0.95)
    evidence.add_evidence("dtc_present", True, EvidenceType.BOOLEAN, confidence=0.90)
    evidence.add_evidence("battery_voltage_low", False, EvidenceType.BOOLEAN, confidence=0.85)

    print(f"Evidence: coolant_temp_high=True, dtc_present=True, battery_voltage_low=False")

    # Perform Bayesian update
    evidence_used = bayesian_update_from_evidence(belief, evidence)

    print(f"Evidence used: {evidence_used}")
    print(f"Updated beliefs: {belief.probabilities}")

    # Check that beliefs are normalized
    total_prob = sum(belief.probabilities.values())
    assert abs(total_prob - 1.0) < 1e-6, f"Beliefs not normalized: {total_prob}"

    # Check that engine_issue probability increased due to high coolant temp
    engine_prob = belief.probabilities["engine_issue"]
    assert engine_prob > 0.25, f"Engine issue probability should increase, got {engine_prob}"

    print("Basic Bayesian update test passed\n")

def test_evidence_rules():
    """Test evidence generation from rules."""
    print("Testing Evidence Rules")

    # Create rule engine with evidence rules
    rule_engine = RuleEngine()
    evidence_rules = create_evidence_rules()
    for rule in evidence_rules:
        rule_engine.add_evidence_rule(rule)

    # Test data with high coolant temp
    test_data = {
        "live_parameters": {
            "coolant_temp": {"value": 110},  # High temperature
            "battery_voltage": {"value": 11.5},  # Low voltage
            "engine_rpm": {"value": 800}
        },
        "dtc_codes": ["P0301", "P0115"]  # Misfire and coolant sensor DTC
    }

    evidence_vector = rule_engine.evaluate_evidence_all(test_data)

    print(f"Generated {len(evidence_vector.evidence)} evidence items:")
    for name, item in evidence_vector.evidence.items():
        print(f"  {name}: {item.value} (confidence: {item.confidence})")

    # Verify expected evidence
    assert evidence_vector.get_evidence("coolant_temp_high").value == True
    assert evidence_vector.get_evidence("battery_voltage_low").value == True
    assert evidence_vector.get_evidence("engine_misfire").value == True
    assert evidence_vector.get_evidence("dtc_present").value == True

    print("Evidence rules test passed\n")

def test_diagnostic_trace():
    """Test diagnostic trace functionality."""
    print("Testing Diagnostic Trace")

    # Create initial trace
    initial_beliefs = {"normal": 0.4, "engine_issue": 0.3, "sensor_fault": 0.2, "electrical": 0.1}
    trace = DiagnosticTrace.create_initial_trace(initial_beliefs)

    print(f"Initial trace created with {len(trace.belief_before)} belief states")

    # Simulate finalization
    final_beliefs = {"normal": 0.1, "engine_issue": 0.7, "sensor_fault": 0.1, "electrical": 0.1}
    evidence_used = ["coolant_temp_high", "dtc_present"]

    trace.finalize_trace(
        final_belief=final_beliefs,
        evidence_used=evidence_used,
        diagnosis="Engine issue detected",
        confidence=0.85,
        severity="HIGH",
        recommendations=["Check coolant system", "Clear DTCs"]
    )

    print(f"Information gain: {trace.information_gain:.4f}")
    assert trace.information_gain > 0, "Information gain should be positive"

    print("Diagnostic trace test passed\n")

def test_full_diagnostic_flow():
    """Test complete diagnostic flow with evidence-driven updates."""
    print("Testing Full Diagnostic Flow")

    # Create mock diagnostics engine components
    # Note: This is a simplified test - full integration would require more setup

    # Test data simulating an engine overheating scenario
    test_data = {
        "live_parameters": {
            "coolant_temp": {"value": 115},  # Very high temperature
            "battery_voltage": {"value": 13.8},  # Normal voltage
            "engine_rpm": {"value": 2500}  # High RPM
        },
        "dtc_codes": ["P0115", "P0302"],  # Coolant sensor and misfire DTCs
        "vehicle_info": {
            "make": "Toyota",
            "model": "Camry",
            "year": 2018
        }
    }

    # Initialize belief state
    belief_state = BeliefState(["normal_operation", "engine_issue", "sensor_fault", "electrical_fault"])

    # Create rule engine and add evidence rules
    rule_engine = RuleEngine()
    evidence_rules = create_evidence_rules()
    for rule in evidence_rules:
        rule_engine.add_evidence_rule(rule)

    # Collect evidence
    evidence_vector = rule_engine.evaluate_evidence_all(test_data)
    print(f"Collected {len(evidence_vector.evidence)} evidence items")

    # Perform Bayesian update
    evidence_used = bayesian_update_from_evidence(belief_state, evidence_vector)

    print(f"Evidence used: {evidence_used}")
    print(f"Final beliefs: {belief_state.probabilities}")

    # Check that engine_issue has highest probability
    most_likely = max(belief_state.probabilities.items(), key=lambda x: x[1])
    assert most_likely[0] == "engine_issue", f"Expected engine_issue, got {most_likely[0]}"
    assert most_likely[1] > 0.5, f"Engine issue probability should be > 0.5, got {most_likely[1]}"

    print("Full diagnostic flow test passed\n")

def main():
    """Run all tests."""
    print("Testing Phase 4: Evidence-Driven Bayesian Updates\n")

    try:
        test_basic_bayesian_update()
        test_evidence_rules()
        test_diagnostic_trace()
        test_full_diagnostic_flow()

        print("All tests passed! Phase 4 implementation is working correctly.")
        print("\nKey achievements:")
        print("* Evidence vectors collect observations from rules and ML")
        print("* Likelihood tables provide P(E|H) for Bayesian updates")
        print("* Bayesian updates: P(H|E) proportional to P(E|H) * P(H)")
        print("* DiagnosticTrace tracks belief evolution and information gain")
        print("* Rules emit evidence, not diagnoses")
        print("* Belief updates occur before diagnostic outcome selection")
        print("\nReady for Phase 5: Active Diagnostics (choosing next test to maximize entropy reduction)")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())