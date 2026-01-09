# ai/core/diagnostics_engine.py
# PHASE 9: REASONING CORE FROZEN
# The following components are frozen and must not be modified:
# - Belief update logic (bayesian_update_from_evidence)
# - Entropy calculation (BeliefState.entropy)
# - Likelihood update rules (update_likelihoods_from_observation)
# - Reliability semantics (test_reliability_scores, update_test_reliability_score)
# - Exploration guarantees (exploration_probability in select_next_diagnostic_test)
# Any changes must happen around this core, not inside it.
# This freeze ensures epistemic integrity and prevents contamination of belief by convenience.

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from dataclasses import dataclass
from .config import AIConfig
from .exceptions import DiagnosticError
from ..belief_state import BeliefState
from ..belief_update import bayesian_update_from_evidence, calculate_information_gain
from .diagnostic_trace import DiagnosticTrace
from ..ml.loader import MLLoader
from ..ml.predictors import MLPredictor
from ..rules.base import RuleEngine
from ..rules.engine_rules import create_engine_rules
from ..rules.evidence_rules import create_evidence_rules
from ..can.database import CANDatabase
from ..utils.validation import validate_live_data
from ..utils.logging import logger
import copy
import json
import os
import random

@dataclass
class DiagnosticTest:
    """Represents a diagnostic test that can be performed"""
    name: str
    cost: float  # time/effort/money cost
    evidence_generated: List[str]  # evidence this test can provide

@dataclass
class ObservedOutcome:
    """Immutable record of a performed diagnostic test outcome"""
    test: str
    outcome: str  # "pass" or "fail"
    ground_truth_confirmed: bool  # True if fault confirmed or ruled out definitively
    timestamp: datetime
    hypothesis_resolved: Optional[str] = None  # Which hypothesis was confirmed/ruled out

class ObservationLogger:
    """Handles immutable logging of diagnostic test outcomes for learning"""

    def __init__(self, log_file: str = "observations.jsonl"):
        self.log_file = log_file
        self._ensure_log_file()

    def _ensure_log_file(self):
        """Ensure the log file exists"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                pass  # Create empty file

    def log_observation(self, observation: ObservedOutcome):
        """Log an observation immutably (append-only)"""
        with open(self.log_file, 'a') as f:
            json.dump({
                "test": observation.test,
                "outcome": observation.outcome,
                "ground_truth_confirmed": observation.ground_truth_confirmed,
                "timestamp": observation.timestamp.isoformat(),
                "hypothesis_resolved": observation.hypothesis_resolved
            }, f)
            f.write('\n')
        logger.info(f"Logged observation: {observation.test} -> {observation.outcome}")

    def get_all_observations(self) -> List[ObservedOutcome]:
        """Retrieve all logged observations"""
        observations = []
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        observations.append(ObservedOutcome(
                            test=data["test"],
                            outcome=data["outcome"],
                            ground_truth_confirmed=data["ground_truth_confirmed"],
                            timestamp=datetime.fromisoformat(data["timestamp"]),
                            hypothesis_resolved=data.get("hypothesis_resolved")
                        ))
        return observations

class DiagnosticsEngine:
    def __init__(self, config: AIConfig, ml_loader: MLLoader, can_db: CANDatabase, rule_engine: RuleEngine):
        self.config = config
        self.ml_loader = ml_loader
        self.can_db = can_db
        self.rule_engine = rule_engine
        self.ml_predictor = MLPredictor(ml_loader) if ml_loader.is_available() else None

        # Initialize observation logger for Phase 6 learning
        self.observation_logger = ObservationLogger()

        # Initialize evidence rules
        evidence_rules = create_evidence_rules()
        for rule in evidence_rules:
            self.rule_engine.add_evidence_rule(rule)

        # Initialize diagnostic tests and outcomes
        self._initialize_diagnostic_tests()

        # Phase 7: Shadow learning mode - copy active tables to shadow for learning
        self.shadow_test_outcomes = copy.deepcopy(self.test_outcomes)

        # Calibration metrics tracking
        self.calibration_metrics = {
            "prediction_errors": [],  # Expected vs actual entropy reduction
            "overconfidence_incidents": 0,  # Times certainty reached too quickly
            "false_certainty_persistence": 0,  # Times certainty persisted despite contradiction
            "learning_attempts": 0,
            "learning_promotions": 0
        }

        # Phase 8: Per-test calibration history for reliability tracking
        self.test_calibration_history = {}  # test_name -> list of calibration records
        self.test_reliability_scores = {}  # test_name -> current reliability score (0-1)
        self.test_usage_counts = {}  # test_name -> number of times used
        self._initialize_test_calibration_tracking()

    def _initialize_diagnostic_tests(self):
        """Initialize available diagnostic tests and their outcome probabilities"""
        # Define available diagnostic tests
        self.diagnostic_tests = [
            DiagnosticTest("read_pid", 1.0, ["coolant_temp_high", "battery_voltage_low"]),
            DiagnosticTest("visual_inspection", 1.5, ["coolant_leak", "electrical_connection_issue"]),
            DiagnosticTest("electrical_test", 2.0, ["battery_voltage_low", "electrical_connection_issue"]),
            DiagnosticTest("pressure_test", 3.0, ["coolant_leak", "fuel_pressure_low"]),
            DiagnosticTest("component_swap", 5.0, ["engine_misfire", "oxygen_sensor_fault"])
        ]

        # Define test outcomes P(outcome|H) - probability of test outcome given hypothesis
        # This is the inverse of likelihood tables
        self.test_outcomes = {
            "read_pid": {
                "normal_operation": {"pass": 0.9, "fail": 0.1},
                "engine_issue": {"pass": 0.3, "fail": 0.7},
                "sensor_fault": {"pass": 0.4, "fail": 0.6},
                "electrical_fault": {"pass": 0.5, "fail": 0.5}
            },
            "visual_inspection": {
                "normal_operation": {"pass": 0.95, "fail": 0.05},
                "engine_issue": {"pass": 0.6, "fail": 0.4},
                "sensor_fault": {"pass": 0.8, "fail": 0.2},
                "electrical_fault": {"pass": 0.7, "fail": 0.3}
            },
            "electrical_test": {
                "normal_operation": {"pass": 0.9, "fail": 0.1},
                "engine_issue": {"pass": 0.8, "fail": 0.2},
                "sensor_fault": {"pass": 0.6, "fail": 0.4},
                "electrical_fault": {"pass": 0.2, "fail": 0.8}
            },
            "pressure_test": {
                "normal_operation": {"pass": 0.95, "fail": 0.05},
                "engine_issue": {"pass": 0.4, "fail": 0.6},
                "sensor_fault": {"pass": 0.7, "fail": 0.3},
                "electrical_fault": {"pass": 0.9, "fail": 0.1}
            },
            "component_swap": {
                "normal_operation": {"pass": 0.98, "fail": 0.02},
                "engine_issue": {"pass": 0.3, "fail": 0.7},
                "sensor_fault": {"pass": 0.4, "fail": 0.6},
                "electrical_fault": {"pass": 0.8, "fail": 0.2},
                # Phase 3: Lean Hypotheses Support
                "vacuum_leak": {"pass": 0.5, "fail": 0.5}, # Swapping parts might not fix a leak unless it's a gasket
                "fuel_starvation": {"pass": 0.2, "fail": 0.8}, # Swapping pump/filter/injector helps
                "maf_bias": {"pass": 0.1, "fail": 0.9}, # Swapping MAF fixes it immediately
                "exhaust_leak": {"pass": 0.5, "fail": 0.5} # Swapping O2 doesn't fix leak, swapping pipe does
            }
        }

        # Extend other tests for new hypotheses (Phase 3)
        # read_pid
        self.test_outcomes["read_pid"].update({
            "vacuum_leak": {"pass": 0.1, "fail": 0.9}, # High STFT/LTFT
            "fuel_starvation": {"pass": 0.1, "fail": 0.9}, # High STFT/LTFT + Low Pressure
            "maf_bias": {"pass": 0.2, "fail": 0.8}, # Skewed readings
            "exhaust_leak": {"pass": 0.3, "fail": 0.7} # Skewed O2
        })
        # visual_inspection
        self.test_outcomes["visual_inspection"].update({
            "vacuum_leak": {"pass": 0.4, "fail": 0.6}, # Visible cracked hoses
            "fuel_starvation": {"pass": 0.8, "fail": 0.2}, # Hard to see pump failure, maybe leaks
            "maf_bias": {"pass": 0.9, "fail": 0.1}, # Usually internal, looks fine
            "exhaust_leak": {"pass": 0.3, "fail": 0.7} # Soot marks visible
        })
        # electrical_test
        self.test_outcomes["electrical_test"].update({
            "vacuum_leak": {"pass": 0.9, "fail": 0.1}, # Mechanical issue
            "fuel_starvation": {"pass": 0.7, "fail": 0.3}, # Pump voltage ok, pump mechanical fail
            "maf_bias": {"pass": 0.6, "fail": 0.4}, # Sensor power/ground ok, signal biased
            "exhaust_leak": {"pass": 0.9, "fail": 0.1} # Mechanical
        })
        # pressure_test
        self.test_outcomes["pressure_test"].update({
            "vacuum_leak": {"pass": 0.8, "fail": 0.2}, # Fuel pressure ok
            "fuel_starvation": {"pass": 0.05, "fail": 0.95}, # Fails fuel pressure test hard
            "maf_bias": {"pass": 0.9, "fail": 0.1}, # Fuel pressure ok
            "exhaust_leak": {"pass": 0.9, "fail": 0.1} # Fuel pressure ok
        })

    def _initialize_test_calibration_tracking(self):
        """Initialize per-test calibration history tracking for Phase 8."""
        for test in self.diagnostic_tests:
            self.test_calibration_history[test.name] = []
            self.test_reliability_scores[test.name] = 0.5  # Start with neutral reliability
            self.test_usage_counts[test.name] = 0

    def log_observation(self, test_name: str, outcome: str, ground_truth_confirmed: bool = False, hypothesis_resolved: Optional[str] = None):
        """
        Phase 9: Log a performed diagnostic test outcome with integrity validation.

        Ensures observation integrity in the field:
        - Ground truth confirmation cannot be spoofed
        - Observations are immutable
        - Learning gates cannot be bypassed by convenience

        Args:
            test_name: Name of the test performed
            outcome: "pass" or "fail"
            ground_truth_confirmed: True if this outcome confirms or rules out a fault definitively
            hypothesis_resolved: Which hypothesis was confirmed/ruled out (if applicable)
        """
        # Phase 9: Observation Integrity Validation
        validation_errors = self._validate_observation_integrity(test_name, outcome, ground_truth_confirmed, hypothesis_resolved)
        if validation_errors:
            logger.error(f"Observation integrity validation failed: {validation_errors}")
            # Do not log invalid observations
            return

        observation = ObservedOutcome(
            test=test_name,
            outcome=outcome,
            ground_truth_confirmed=ground_truth_confirmed,
            timestamp=datetime.now(),
            hypothesis_resolved=hypothesis_resolved
        )

        # Ensure immutability: observations are append-only
        try:
            self.observation_logger.log_observation(observation)
        except Exception as e:
            logger.error(f"Failed to log observation immutably: {e}")
            raise

    def can_update_likelihoods(self, observation: ObservedOutcome) -> bool:
        """
        Hypothesis resolution gate: Check if observation allows likelihood updates.

        Returns True only if:
        - A fault is confirmed (repair validated), OR
        - A fault is ruled out definitively
        """
        return observation.ground_truth_confirmed and observation.hypothesis_resolved is not None

    def update_likelihoods_from_observation(self, observation: ObservedOutcome, alpha: float = 0.9):
        """
        Phase 7: Update shadow likelihoods P(outcome|H) using Bayesian learning from confirmed observations.

        P(E|H) ← α⋅P(E|H) + (1−α)⋅observed

        Updates shadow tables only - active diagnostics remain frozen.

        Args:
            observation: The confirmed observation
            alpha: Learning rate (high = slow learning, default 0.9)
        """
        if not self.can_update_likelihoods(observation):
            logger.warning("Cannot update likelihoods: observation does not meet gate criteria")
            return

        test = observation.test
        outcome = observation.outcome
        hypothesis = observation.hypothesis_resolved

        if test not in self.shadow_test_outcomes or hypothesis not in self.shadow_test_outcomes[test]:
            logger.warning(f"Invalid test/hypothesis combination: {test}/{hypothesis}")
            return

        # Current likelihood in shadow table
        current_likelihood = self.shadow_test_outcomes[test][hypothesis][outcome]

        # Observed outcome (1.0 if observed, 0.0 otherwise)
        observed_value = 1.0  # Since this is the observed outcome

        # Bayesian update with slow learning
        new_likelihood = alpha * current_likelihood + (1 - alpha) * observed_value

        # Ensure valid probability
        new_likelihood = max(0.01, min(0.99, new_likelihood))

        # Update the shadow likelihood table
        self.shadow_test_outcomes[test][hypothesis][outcome] = new_likelihood

        # Track learning attempt
        self.calibration_metrics["learning_attempts"] += 1

        logger.info(f"Shadow learning: Updated P({outcome}|{hypothesis}) for {test}: {current_likelihood:.3f} -> {new_likelihood:.3f}")

    def evaluate_shadow_learning_performance(self, belief_before_test: BeliefState, test_performed: DiagnosticTest,
                                           outcome_observed: str, belief_after_test: BeliefState) -> Dict[str, float]:
        """
        Evaluate how well shadow learning predicts information gain vs active tables.

        Returns metrics comparing predicted vs actual entropy reduction.
        """
        # Calculate predicted entropy reduction using active tables
        predicted_gain_active = self.calculate_expected_information_gain(belief_before_test, test_performed, use_shadow=False)

        # Calculate predicted entropy reduction using shadow tables
        predicted_gain_shadow = self.calculate_expected_information_gain(belief_before_test, test_performed, use_shadow=True)

        # Calculate actual entropy reduction
        actual_entropy_reduction = belief_before_test.entropy() - belief_after_test.entropy()

        # Prediction errors
        prediction_error_active = abs(predicted_gain_active - actual_entropy_reduction)
        prediction_error_shadow = abs(predicted_gain_shadow - actual_entropy_reduction)

        # Track prediction errors
        self.calibration_metrics["prediction_errors"].append({
            "active_error": prediction_error_active,
            "shadow_error": prediction_error_shadow,
            "actual_reduction": actual_entropy_reduction,
            "test": test_performed.name,
            "timestamp": datetime.now()
        })

        # Check for overconfidence: if actual reduction is much less than predicted
        if actual_entropy_reduction < predicted_gain_active * 0.5:  # Less than 50% of predicted
            self.calibration_metrics["overconfidence_incidents"] += 1

        # Check for false certainty persistence: if belief becomes too certain too quickly
        max_prob = max(belief_after_test.probabilities.values())
        if max_prob > 0.95 and belief_before_test.entropy() > 1.0:  # Became very certain from uncertain state
            self.calibration_metrics["false_certainty_persistence"] += 1

        return {
            "predicted_gain_active": predicted_gain_active,
            "predicted_gain_shadow": predicted_gain_shadow,
            "actual_reduction": actual_entropy_reduction,
            "improvement": prediction_error_active - prediction_error_shadow  # Positive if shadow is better
        }

    def update_test_calibration_history(self, test_name: str, predicted_entropy_reduction: float, actual_entropy_reduction: float):
        """
        Phase 8: Update per-test calibration history for reliability tracking.

        Tracks accuracy of entropy reduction predictions to build reliability scores.
        """
        if test_name not in self.test_calibration_history:
            logger.warning(f"Unknown test for calibration tracking: {test_name}")
            return

        # Calculate prediction error (absolute difference)
        prediction_error = abs(predicted_entropy_reduction - actual_entropy_reduction)

        # Record calibration data
        calibration_record = {
            "timestamp": datetime.now(),
            "predicted_reduction": predicted_entropy_reduction,
            "actual_reduction": actual_entropy_reduction,
            "prediction_error": prediction_error,
            "accuracy": 1.0 - min(prediction_error / max(predicted_entropy_reduction, 0.1), 1.0)  # Normalized accuracy
        }

        self.test_calibration_history[test_name].append(calibration_record)
        self.test_usage_counts[test_name] += 1

        # Update reliability score (slow-moving average)
        self._update_test_reliability_score(test_name)

        logger.debug(f"Updated calibration history for {test_name}: predicted={predicted_entropy_reduction:.4f}, "
                    f"actual={actual_entropy_reduction:.4f}, error={prediction_error:.4f}")

    def _update_test_reliability_score(self, test_name: str, alpha: float = 0.95):
        """
        Update test reliability score based on recent calibration history.

        Reliability = accuracy of entropy prediction (slow-moving average)
        Bounded between 0.1 and 1.0 to prevent zero reliability.
        """
        history = self.test_calibration_history[test_name]
        if not history:
            return

        # Use recent history (last 10 records) for reliability calculation
        recent_history = history[-10:]

        # Calculate average accuracy
        avg_accuracy = sum(record["accuracy"] for record in recent_history) / len(recent_history)

        # Slow-moving average update
        current_reliability = self.test_reliability_scores[test_name]
        new_reliability = alpha * current_reliability + (1 - alpha) * avg_accuracy

        # Bound reliability between 0.1 and 1.0
        new_reliability = max(0.1, min(1.0, new_reliability))

        self.test_reliability_scores[test_name] = new_reliability

        logger.debug(f"Updated reliability for {test_name}: {current_reliability:.4f} -> {new_reliability:.4f}")

    def get_calibration_summary(self) -> Dict[str, Any]:
        """Get summary of calibration metrics."""
        if not self.calibration_metrics["prediction_errors"]:
            return {"status": "No learning evaluations yet"}

        errors = self.calibration_metrics["prediction_errors"]
        avg_active_error = sum(e["active_error"] for e in errors) / len(errors)
        avg_shadow_error = sum(e["shadow_error"] for e in errors) / len(errors)

        return {
            "learning_attempts": self.calibration_metrics["learning_attempts"],
            "learning_promotions": self.calibration_metrics["learning_promotions"],
            "avg_prediction_error_active": avg_active_error,
            "avg_prediction_error_shadow": avg_shadow_error,
            "overconfidence_incidents": self.calibration_metrics["overconfidence_incidents"],
            "false_certainty_persistence": self.calibration_metrics["false_certainty_persistence"],
            "shadow_improvement": avg_active_error - avg_shadow_error  # Positive if shadow learning helps
        }

    def log_calibration_metrics(self):
        """Log current calibration metrics summary."""
        summary = self.get_calibration_summary()
        if "status" in summary:
            logger.info("Phase 7 Calibration: No evaluations yet")
            return

        logger.info("Phase 7 Shadow Learning Calibration Summary:")
        logger.info(f"  Learning Attempts: {summary['learning_attempts']}")
        logger.info(f"  Learning Promotions: {summary['learning_promotions']}")
        logger.info(f"  Avg Prediction Error (Active): {summary['avg_prediction_error_active']:.4f}")
        logger.info(f"  Avg Prediction Error (Shadow): {summary['avg_prediction_error_shadow']:.4f}")
        logger.info(f"  Shadow Improvement: {summary['shadow_improvement']:.4f}")
        logger.info(f"  Overconfidence Incidents: {summary['overconfidence_incidents']}")
        logger.info(f"  False Certainty Persistence: {summary['false_certainty_persistence']}")

    def get_test_reliability_summary(self) -> Dict[str, Any]:
        """Get summary of per-test reliability scores for Phase 8."""
        if not self.test_reliability_scores:
            return {"status": "No reliability tracking yet"}

        reliability_data = []
        for test_name, reliability in self.test_reliability_scores.items():
            usage_count = self.test_usage_counts.get(test_name, 0)
            history_length = len(self.test_calibration_history.get(test_name, []))
            avg_accuracy = 0.0
            if history_length > 0:
                accuracies = [record["accuracy"] for record in self.test_calibration_history[test_name]]
                avg_accuracy = sum(accuracies) / len(accuracies)

            reliability_data.append({
                "test": test_name,
                "reliability": reliability,
                "usage_count": usage_count,
                "history_length": history_length,
                "avg_accuracy": avg_accuracy
            })

        # Sort by reliability
        reliability_data.sort(key=lambda x: x["reliability"], reverse=True)

        return {
            "test_reliabilities": reliability_data,
            "avg_reliability": sum(r["reliability"] for r in reliability_data) / len(reliability_data),
            "most_reliable": reliability_data[0]["test"] if reliability_data else None,
            "least_reliable": reliability_data[-1]["test"] if reliability_data else None
        }

    def log_test_reliability_summary(self):
        """Log current test reliability summary."""
        summary = self.get_test_reliability_summary()
        if "status" in summary:
            logger.info("Phase 8 Test Reliability: No tracking yet")
            return

        logger.info("Phase 8 Test Reliability Summary:")
        logger.info(f"  Average Reliability: {summary['avg_reliability']:.4f}")
        logger.info(f"  Most Reliable Test: {summary['most_reliable']}")
        logger.info(f"  Least Reliable Test: {summary['least_reliable']}")
        logger.info("  Per-Test Details:")

        for test_data in summary["test_reliabilities"]:
            logger.info(f"    {test_data['test']}: reliability={test_data['reliability']:.4f}, "
                       f"usage={test_data['usage_count']}, accuracy={test_data['avg_accuracy']:.4f}")

    def perform_test(self, test_name: str, outcome: str, ground_truth_confirmed: bool = False, hypothesis_resolved: Optional[str] = None,
                    belief_before: Optional[BeliefState] = None, belief_after: Optional[BeliefState] = None):
        """
        Simulate or record performing a diagnostic test and log the outcome.

        This method should be called when a test is actually performed in the real world.

        Args:
            test_name: Name of test performed
            outcome: "pass" or "fail"
            ground_truth_confirmed: True if outcome confirms ground truth
            hypothesis_resolved: Which hypothesis was resolved
            belief_before: Belief state before test (for calibration)
            belief_after: Belief state after test (for calibration)
        """
        self.log_observation(test_name, outcome, ground_truth_confirmed, hypothesis_resolved)

        # Phase 7: Evaluate shadow learning performance if we have belief states
        if belief_before and belief_after:
            test_obj = next((t for t in self.diagnostic_tests if t.name == test_name), None)
            if test_obj:
                metrics = self.evaluate_shadow_learning_performance(belief_before, test_obj, outcome, belief_after)
                logger.info(f"Shadow learning evaluation: improvement={metrics['improvement']:.4f}, "
                          f"actual_reduction={metrics['actual_reduction']:.4f}")

                # Phase 8: Update test calibration history for reliability tracking
                predicted_reduction = metrics["predicted_gain_active"]  # Use active table prediction
                actual_reduction = metrics["actual_reduction"]
                self.update_test_calibration_history(test_name, predicted_reduction, actual_reduction)

        logger.info(f"Test performed: {test_name} -> {outcome}")

    def calculate_expected_information_gain(self, current_belief: BeliefState, test: DiagnosticTest, use_shadow: bool = False) -> float:
        """
        Calculate expected information gain for a diagnostic test.

        Returns E[H_before - H_after | test] - the expected entropy reduction.

        Args:
            current_belief: Current belief state
            test: Diagnostic test to evaluate
            use_shadow: If True, use shadow likelihood tables for calculation
        """
        likelihood_table = self.shadow_test_outcomes if use_shadow else self.test_outcomes

        if test.name not in likelihood_table:
            return 0.0

        prior_entropy = current_belief.entropy()
        expected_entropy_reduction = 0.0

        # For each possible test outcome
        for outcome, outcome_prob in likelihood_table[test.name]["normal_operation"].items():  # Use any hypothesis to get outcomes
            # Simulate belief update for this outcome
            simulated_belief = copy.deepcopy(current_belief)

            # Update beliefs based on test outcome using likelihoods
            for hypothesis in simulated_belief.probabilities:
                if hypothesis in likelihood_table[test.name]:
                    # P(outcome|H) * P(H) - simplified Bayesian update
                    outcome_likelihood = likelihood_table[test.name][hypothesis][outcome]
                    simulated_belief.probabilities[hypothesis] *= outcome_likelihood

            # Normalize
            total = sum(simulated_belief.probabilities.values())
            if total > 0:
                for hypothesis in simulated_belief.probabilities:
                    simulated_belief.probabilities[hypothesis] /= total

            # Calculate posterior entropy
            posterior_entropy = simulated_belief.entropy()

            # Weight by outcome probability (averaged across hypotheses for simplicity)
            avg_outcome_prob = sum(likelihood_table[test.name][h][outcome] for h in likelihood_table[test.name]) / len(likelihood_table[test.name])

            expected_entropy_reduction += avg_outcome_prob * (prior_entropy - posterior_entropy)

        return expected_entropy_reduction

    def select_next_diagnostic_test(self, current_belief: BeliefState) -> Optional[DiagnosticTest]:
        """
        Phase 8: Select next diagnostic test using reliability-weighted information gain with exploration floor.

        effective_gain = expected_information_gain * reliability_score
        Includes exploration mechanism to prevent epistemic death.
        """
        if not self.diagnostic_tests:
            return None

        # Exploration parameters
        exploration_probability = 0.1  # 10% chance of exploration
        import random

        # Check if we should explore
        if random.random() < exploration_probability:
            return self._select_exploratory_test(current_belief)

        # Normal reliability-weighted selection
        best_test = None
        best_score = -float('inf')

        for test in self.diagnostic_tests:
            expected_gain = self.calculate_expected_information_gain(current_belief, test)
            reliability = self.test_reliability_scores.get(test.name, 0.5)

            # Reliability-weighted gain
            effective_gain = expected_gain * reliability
            efficiency = effective_gain / test.cost if test.cost > 0 else 0

            if efficiency > best_score:
                best_score = efficiency
                best_test = test

        return best_test

    def _select_exploratory_test(self, current_belief: BeliefState) -> Optional[DiagnosticTest]:
        """
        Phase 8: Select a test for exploration purposes.

        Prioritizes rarely used tests or slightly suboptimal tests to maintain epistemic diversity.
        """
        if not self.diagnostic_tests:
            return None

        # Find least used test
        min_usage = min(self.test_usage_counts.values())
        least_used_tests = [t for t in self.diagnostic_tests if self.test_usage_counts[t.name] == min_usage]

        if least_used_tests:
            # If multiple least used, pick one with reasonable information gain
            candidates = []
            for test in least_used_tests:
                gain = self.calculate_expected_information_gain(current_belief, test)
                if gain > 0.01:  # Only consider tests with some information value
                    candidates.append((test, gain))

            if candidates:
                # Sort by gain and pick randomly from top half to avoid worst tests
                candidates.sort(key=lambda x: x[1], reverse=True)
                top_half = candidates[:max(1, len(candidates) // 2)]
                return random.choice(top_half)[0]

        # Fallback: pick any test with non-zero gain
        viable_tests = []
        for test in self.diagnostic_tests:
            gain = self.calculate_expected_information_gain(current_belief, test)
            if gain > 0:
                viable_tests.append(test)

        return random.choice(viable_tests) if viable_tests else self.diagnostic_tests[0]

    def diagnose(self, live_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main diagnostic function with evidence-driven Bayesian belief updates."""
        try:
            # Validate input
            validate_live_data(live_data)

            logger.info("Starting evidence-driven diagnostic analysis")

            # Check for lean condition (Phase 3: Hypothesis Spread Mandate)
            is_lean = False
            lambda_val = None
            if 'live_parameters' in live_data and 'lambda' in live_data['live_parameters']:
                lambda_val = live_data['live_parameters']['lambda'].get('value')
                if lambda_val is not None and lambda_val > 1.1:
                    is_lean = True

            # Initialize belief state
            if is_lean:
                # Phase 3: Mandatory lean hypotheses: Air-side, Fuel-side, Sensor-bias
                logger.info(f"Phase 3: Lean condition detected (Lambda={lambda_val:.2f}). Enforcing hypothesis spread.")
                initial_hypotheses = ["normal_operation", "vacuum_leak", "fuel_starvation", "maf_bias", "exhaust_leak"]
            else:
                initial_hypotheses = ["normal_operation", "engine_issue", "sensor_fault", "electrical_fault"]

            belief_state = BeliefState(initial_hypotheses)

            # Create diagnostic trace
            trace = DiagnosticTrace.create_initial_trace(belief_state.probabilities)

            # Collect evidence from all sources
            evidence_vector = self._collect_evidence(live_data)

            # Perform Bayesian belief update
            evidence_used = bayesian_update_from_evidence(belief_state, evidence_vector)

            # Select diagnosis based on updated beliefs
            diagnosis_result = self._select_diagnosis_from_beliefs(belief_state)

            # Phase 5: Confidence Humiliation
            # If lambda > 1.1 and not falsification (initial pass has no active tests): confidence = min(confidence, 0.65)
            if is_lean and diagnosis_result["confidence"] > 0.65:
                # We only cap if we are not saying "normal" (Phase 8 handles normal)
                # Actually, Phase 5 says "Initial confidence cap under lean".
                logger.info(f"Phase 5: Capping initial lean confidence {diagnosis_result['confidence']:.2f} -> 0.65")
                diagnosis_result["confidence"] = 0.65

            # Phase 8: Lean-Only Kill Switch
            # If lambda > 1.15 AND "normal operation" is stated -> Immediate KILL
            if is_lean and lambda_val > 1.15 and diagnosis_result["severity"] == "NORMAL":
                logger.critical(f"PHASE 8 KILL SWITCH: Lambda {lambda_val:.2f} > 1.15 but diagnosis is Normal. TERMINATING.")
                diagnosis_result["diagnosis"] = "KILL SWITCH ACTIVATED: FATAL LOGIC ERROR (Normal diagnosed during Lean condition)"
                diagnosis_result["severity"] = "FATAL"
                diagnosis_result["confidence"] = 1.0
                diagnosis_result["recommendations"] = ["IMMEDIATE SYSTEM HALT", "CONTACT DEVELOPER", "RETRAIN MODEL"]

            # Select next diagnostic test for active diagnostics
            next_test = self.select_next_diagnostic_test(belief_state)

            # Finalize trace
            trace.finalize_trace(
                final_belief=belief_state.probabilities,
                evidence_used=evidence_used,
                diagnosis=diagnosis_result["diagnosis"],
                confidence=diagnosis_result["confidence"],
                severity=diagnosis_result["severity"],
                recommendations=diagnosis_result["recommendations"]
            )

            # Log trace information
            self._log_diagnostic_trace(trace)

            # Log Phase 7 calibration and Phase 8 reliability metrics
            self.log_calibration_metrics()
            self.log_test_reliability_summary()

            # Phase 9: Human-Facing Explanations (Read-Only)
            explanations = self._generate_human_explanations(belief_state, evidence_vector, next_test)

            # Phase 9: Failure Mode Surfacing
            failure_modes = self._detect_failure_modes(belief_state, evidence_vector, next_test)

            # Return result with trace information and Phase 9 additions
            result = {
                "agent": "Charlemaine",
                "timestamp": trace.timestamp,
                "diagnosis": trace.diagnosis,
                "confidence": trace.confidence,
                "recommendations": trace.recommendations,
                "severity": trace.severity,
                "mode": "ACTIVE DIAGNOSTICS BAYESIAN AI",
                "belief_state": trace.belief_after,
                "information_gain": trace.information_gain,
                "evidence_used": trace.evidence_used,
                "next_test": next_test.name if next_test else None,
                "next_test_cost": next_test.cost if next_test else None,
                # Phase 9 additions
                "explanations": explanations,
                "failure_modes": failure_modes
            }

            return result

        except Exception as e:
            logger.error(f"Diagnostic process failed: {e}")
            raise DiagnosticError(f"Diagnosis failed: {e}") from e

    def _collect_evidence(self, live_data: Dict[str, Any]) -> 'EvidenceVector':
        """Collect evidence from all sources (rules and ML)."""
        combined_evidence = self.rule_engine.evaluate_evidence_all(live_data)

        # Add ML-generated evidence if available
        if self.ml_predictor:
            ml_evidence = self.ml_predictor.predict_evidence(live_data)
            if ml_evidence:
                # Merge ML evidence with rule evidence
                for name, evidence_item in ml_evidence.evidence.items():
                    combined_evidence.add_evidence(
                        name=name,
                        value=evidence_item.value,
                        evidence_type=evidence_item.evidence_type,
                        confidence=evidence_item.confidence
                    )

        logger.debug(f"Collected {len(combined_evidence.evidence)} evidence items")
        return combined_evidence

    def _select_diagnosis_from_beliefs(self, belief_state: BeliefState) -> Dict[str, Any]:
        """Select diagnosis based on posterior beliefs."""
        # Find hypothesis with highest probability
        most_likely_hypothesis = max(belief_state.probabilities.items(), key=lambda x: x[1])
        hypothesis_name = most_likely_hypothesis[0]
        confidence = most_likely_hypothesis[1]

        # Map hypotheses to diagnoses
        diagnosis_map = {
            "normal_operation": {
                "diagnosis": "All monitored systems appear normal.",
                "severity": "NORMAL",
                "recommendations": ["Continue regular maintenance.", "Monitor system performance."]
            },
            "engine_issue": {
                "diagnosis": "Engine performance issue detected.",
                "severity": "HIGH",
                "recommendations": ["Check engine coolant temperature.", "Inspect for misfires.", "Verify fuel system pressure."]
            },
            "sensor_fault": {
                "diagnosis": "Sensor system fault detected.",
                "severity": "MEDIUM",
                "recommendations": ["Check oxygen sensors.", "Verify DTC codes.", "Inspect sensor connections."]
            },
            "electrical_fault": {
                "diagnosis": "Electrical system fault detected.",
                "severity": "HIGH",
                "recommendations": ["Check battery voltage.", "Inspect charging system.", "Verify electrical connections."]
            },
            # Phase 3 Lean Hypotheses
            "vacuum_leak": {
                "diagnosis": "Intake system vacuum leak detected.",
                "severity": "MEDIUM",
                "recommendations": ["Perform smoke test.", "Check intake manifold gaskets.", "Inspect vacuum hoses."]
            },
            "fuel_starvation": {
                "diagnosis": "Fuel system starvation detected.",
                "severity": "HIGH",
                "recommendations": ["Check fuel pressure.", "Inspect fuel filter.", "Verify fuel pump operation."]
            },
            "maf_bias": {
                "diagnosis": "Mass Air Flow sensor bias detected.",
                "severity": "MEDIUM",
                "recommendations": ["Clean MAF sensor.", "Check MAF sensor wiring.", "Replace MAF sensor."]
            },
            "exhaust_leak": {
                "diagnosis": "Exhaust system leak detected.",
                "severity": "MEDIUM",
                "recommendations": ["Inspect exhaust manifold.", "Check exhaust gaskets.", "Verify O2 sensor seating."]
            }
        }

        result = diagnosis_map.get(hypothesis_name, {
            "diagnosis": "Unable to determine specific diagnosis.",
            "severity": "UNKNOWN",
            "recommendations": ["Further diagnostic testing required."]
        })

        result["confidence"] = round(confidence, 3)
        return result

    def _run_ml_diagnosis(self, live_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Legacy ML diagnosis method - kept for backward compatibility."""
        if self.ml_predictor:
            return self.ml_predictor.predict(live_data)
        return None

    def _run_rule_diagnosis(self, live_data: Dict[str, Any]) -> list:
        """Legacy rule diagnosis method - kept for backward compatibility."""
        return self.rule_engine.evaluate_all(live_data)

    def _log_diagnostic_trace(self, trace: DiagnosticTrace):
        """Log diagnostic trace information."""
        logger.info(f"Diagnosis: {trace.diagnosis}")
        logger.info(f"Confidence: {trace.confidence:.1%}")
        logger.info(f"Severity: {trace.severity}")
        logger.info(f"Information Gain: {trace.information_gain:.4f}")
        logger.info(f"Evidence Used: {len(trace.evidence_used)} items")
        logger.info(f"Final Beliefs: {trace.belief_after}")

        for rec in trace.recommendations:
            logger.info(f"Recommendation: {rec}")

    def _validate_observation_integrity(self, test_name: str, outcome: str, ground_truth_confirmed: bool, hypothesis_resolved: Optional[str]) -> List[str]:
        """
        Phase 9: Validate observation integrity to prevent spoofing and ensure learning gate compliance.

        Returns list of validation errors (empty if valid).
        """
        errors = []

        # Validate test exists
        if not any(t.name == test_name for t in self.diagnostic_tests):
            errors.append(f"Unknown test: {test_name}")

        # Validate outcome
        if outcome not in ["pass", "fail"]:
            errors.append(f"Invalid outcome: {outcome} (must be 'pass' or 'fail')")

        # Ground truth confirmation integrity checks
        if ground_truth_confirmed:
            # Must have hypothesis resolved
            if not hypothesis_resolved:
                errors.append("Ground truth confirmation requires hypothesis_resolved")

            # Hypothesis must be valid
            valid_hypotheses = ["normal_operation", "engine_issue", "sensor_fault", "electrical_fault"]
            if hypothesis_resolved not in valid_hypotheses:
                errors.append(f"Invalid hypothesis: {hypothesis_resolved}")

            # Additional validation: prevent convenience bypassing
            # In real implementation, this would check for repair documentation, technician verification, etc.
            # For now, we log that ground truth confirmation requires external validation
            logger.warning(f"Ground truth confirmation for {hypothesis_resolved} - ensure external validation (repair/test documentation)")

        # Learning gate integrity: prevent bypassing by setting ground_truth_confirmed=True without proper validation
        if ground_truth_confirmed and not self._is_ground_truth_properly_validated(test_name, outcome, hypothesis_resolved):
            errors.append("Ground truth confirmation not properly validated - learning gate bypassed")

        return errors

    def _is_ground_truth_properly_validated(self, test_name: str, outcome: str, hypothesis_resolved: str) -> bool:
        """
        Phase 9: Check if ground truth confirmation is properly validated.

        In production, this would check for:
        - Repair documentation
        - Technician verification
        - Test result confirmation
        - Audit trail

        For now, we implement basic checks to prevent obvious spoofing.
        """
        # Basic validation: hypothesis must be consistent with test outcome patterns
        # This prevents claiming "confirmed electrical fault" when test passed (which should rule out faults)

        if hypothesis_resolved == "normal_operation":
            # Normal operation should only be confirmed on passing tests
            if outcome != "pass":
                return False
        else:
            # Fault hypotheses should only be confirmed on failing tests
            if outcome != "fail":
                return False

        # Additional check: prevent confirmation of faults that test doesn't target
        test_targets = {
            "read_pid": ["engine_issue", "sensor_fault", "electrical_fault", "vacuum_leak", "fuel_starvation", "maf_bias", "exhaust_leak"],
            "visual_inspection": ["engine_issue", "sensor_fault", "electrical_fault", "vacuum_leak", "exhaust_leak"],
            "electrical_test": ["electrical_fault", "maf_bias", "fuel_starvation"],
            "pressure_test": ["engine_issue", "fuel_starvation", "vacuum_leak"],
            "component_swap": ["engine_issue", "sensor_fault", "electrical_fault", "maf_bias", "fuel_starvation"]
        }

        if test_name in test_targets and hypothesis_resolved not in test_targets[test_name]:
            return False

        return True  # Basic validation passed

    def _generate_human_explanations(self, belief_state: BeliefState, evidence_vector, next_test) -> Dict[str, Any]:
        """
        Phase 7: Retrain the Explanation Engine.
        Explanations must follow: Constraint -> Causes -> Ranking -> Falsifiers -> Uncertainty.
        Phase 4: Falsification Bootcamp included.
        """
        # 1. Constraint
        constraint = None
        is_lean = False
        if hasattr(evidence_vector, 'evidence'):
             # Check for lean condition evidence
             # In evidence_rules.py we added 'lean_condition_detected'
             if 'lean_condition_detected' in evidence_vector.evidence and evidence_vector.evidence['lean_condition_detected'].value:
                 constraint = "Lambda > 1.1 indicates excess oxygen or fuel deficit."
                 is_lean = True

        # 2. Causes & 3. Ranking
        sorted_beliefs = sorted(belief_state.probabilities.items(), key=lambda x: x[1], reverse=True)
        top_beliefs = [{"hypothesis": hypo, "probability": prob} for hypo, prob in sorted_beliefs[:3]]

        # 4. Falsifiers (Phase 4)
        falsifiers = {}
        if is_lean:
            # Hard-coded falsifiers for Phase 4
            falsifiers_map = {
                "vacuum_leak": "If STFT remains > +20% at idle but normalizes at load, intake leak is confirmed.",
                "fuel_starvation": "If fuel pressure drops under load, fuel starvation is confirmed.",
                "maf_bias": "If MAF g/s deviates from calculated theoretical airflow, MAF bias is confirmed.",
                "exhaust_leak": "If O2 sensor voltage oscillates rapidly or stays low despite enrichment, exhaust leak is confirmed."
            }
            for hypo, _ in sorted_beliefs:
                if hypo in falsifiers_map:
                    falsifiers[hypo] = falsifiers_map[hypo]

        # 5. Uncertainty
        uncertainty = {
            "entropy": belief_state.entropy(),
            "max_probability": max(belief_state.probabilities.values()),
            "probability_spread": max(belief_state.probabilities.values()) - min(belief_state.probabilities.values())
        }

        # Test reasoning (Cheap/Decisive test identification for Phase 4)
        test_info = None
        if next_test:
             test_type = "Standard"
             if next_test.cost < 1.0:
                 test_type = "Cheap Test"
             elif self.calculate_expected_information_gain(belief_state, next_test) > 0.5:
                 test_type = "Decisive Test"

             test_info = {
                 "test": next_test.name,
                 "type": test_type,
                 "expected_gain": self.calculate_expected_information_gain(belief_state, next_test),
                 "reliability_score": self.test_reliability_scores.get(next_test.name, 0.5)
             }

        return {
            "constraint": constraint,
            "causes": [b["hypothesis"] for b in top_beliefs],
            "ranking": top_beliefs,
            "falsifiers": falsifiers,
            "uncertainty_metrics": uncertainty,
            "next_test_analysis": test_info
        }

    def _detect_failure_modes(self, belief_state: BeliefState, evidence_vector, next_test) -> List[str]:
        """
        Phase 9: Detect and surface failure modes.

        Identifies when system cannot provide reliable guidance.
        """
        failure_modes = []

        # High uncertainty (entropy > threshold)
        if belief_state.entropy() > 1.5:  # High uncertainty
            failure_modes.append("High uncertainty: Multiple hypotheses remain plausible")

        # Low confidence in top diagnosis
        max_prob = max(belief_state.probabilities.values())
        if max_prob < 0.6:
            failure_modes.append("Low confidence: No hypothesis exceeds 60% probability")

        # Contradictory evidence
        if hasattr(evidence_vector, 'evidence'):
            conflicting_evidence = []
            for name, ev in evidence_vector.evidence.items():
                if hasattr(ev, 'confidence') and ev.confidence < 0.3:
                    conflicting_evidence.append(name)
            if len(conflicting_evidence) > 2:
                failure_modes.append("Contradictory evidence: Multiple low-confidence indicators")

        # No effective test available
        if next_test:
            expected_gain = self.calculate_expected_information_gain(belief_state, next_test)
            if expected_gain < 0.1:  # Minimal information gain
                failure_modes.append("Ineffective tests: No test will significantly reduce uncertainty")
        else:
            failure_modes.append("No tests available: Diagnostic options exhausted")

        # All tests unreliable
        avg_reliability = sum(self.test_reliability_scores.values()) / len(self.test_reliability_scores)
        if avg_reliability < 0.3:
            failure_modes.append("Unreliable tests: All diagnostic tests have low prediction accuracy")

        return failure_modes
