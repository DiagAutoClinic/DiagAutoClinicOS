# ai/belief_update.py

from typing import Dict, Any, List
import numpy as np
from .belief_state import BeliefState
from .core.evidence import EvidenceVector
from .core.likelihoods import likelihood_table

def update_belief(belief: BeliefState, observation: Any, likelihood_fn) -> None:
    """Legacy belief update function for backward compatibility"""
    for fault in belief.probabilities:
        likelihood = likelihood_fn(fault, observation)
        belief.probabilities[fault] *= likelihood

    # Normalize
    total = sum(belief.probabilities.values())
    for fault in belief.probabilities:
        belief.probabilities[fault] /= total

def bayesian_update_from_evidence(belief: BeliefState, evidence_vector: EvidenceVector) -> List[str]:
    """
    Perform Bayesian belief update from evidence vector.

    Returns list of evidence names that were used in the update.
    """
    evidence_used = []

    # Store prior beliefs for entropy calculation
    prior_belief = belief.probabilities.copy()

    # For each piece of evidence, update beliefs
    for evidence_name, evidence_item in evidence_vector.evidence.items():
        evidence_used.append(evidence_name)

        # Get likelihoods for this evidence across all hypotheses
        likelihoods = {}
        for hypothesis in belief.probabilities.keys():
            likelihood = likelihood_table.get_likelihood(hypothesis, evidence_name)

            # For boolean evidence, use likelihood directly if True, or (1-likelihood) if False
            if evidence_item.evidence_type.name == "BOOLEAN":
                if evidence_item.value:
                    likelihoods[hypothesis] = likelihood
                else:
                    likelihoods[hypothesis] = 1.0 - likelihood
            else:
                # For other types, use likelihood as-is (can be extended for numeric/categorical)
                likelihoods[hypothesis] = likelihood

        # Apply Bayesian update: P(H|E) ∝ P(E|H) * P(H)
        for hypothesis in belief.probabilities:
            belief.probabilities[hypothesis] *= likelihoods[hypothesis]

    # Normalize the posterior beliefs
    total = sum(belief.probabilities.values())
    if total > 0:
        for hypothesis in belief.probabilities:
            belief.probabilities[hypothesis] /= total
    else:
        # If all probabilities became 0, reset to uniform
        num_hypotheses = len(belief.probabilities)
        uniform_prob = 1.0 / num_hypotheses
        for hypothesis in belief.probabilities:
            belief.probabilities[hypothesis] = uniform_prob

    return evidence_used

def calculate_information_gain(prior_entropy: float, posterior_entropy: float) -> float:
    """Calculate information gain from entropy reduction"""
    return prior_entropy - posterior_entropy
