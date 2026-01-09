"""
src/vin/layer3_market.py

Layer 3 — Market Context Resolver
Applies market-specific context to adjust confidence, prefer local profiles,
and add epistemology traceability.
Critical for South Africa due to local assembly variations.
"""

from typing import Optional, Dict, List
from dataclasses import replace

from .models import (
    EpistemologicalValue,
    EpistemologicalStatus,
    FieldSource,
    SourceType,
    DecodeContext
)


# Market priority & confidence multipliers
# Higher = stronger preference when hint matches
MARKET_STRATEGIES = {
    "ZA": {
        "multiplier": 1.25,             # boost ZA-local rules
        "priority_local": True,
        "notes": "South Africa market hint → prefer local assembly profiles"
    },
    "EU": {
        "multiplier": 1.10,
        "priority_local": False,
        "notes": "EU market hint → slight preference for EU-spec rules"
    },
    "US": {
        "multiplier": 1.15,
        "priority_local": False,
        "notes": "US market hint → prefer US-spec patterns"
    },
    # Add JP, CA, MX, etc. later
}


ZA_LOCAL_PREFIXES = {
    "AAU", "ADM", "AHT", "AAV", "AFA"   # Rosslyn BMW, East London MB, Prospecton Toyota, Kariega VW, Silverton Ford
}


def apply_market_context(
    vin_normalized: str,
    layer1_result,                      # from decode_iso()
    layer2_result,                      # from OemGrammarDecoder.evaluate()
    context: DecodeContext
) -> tuple[Dict[str, EpistemologicalValue], List[str], List[str]]:
    """
    Layer 3 logic:
    - Adjusts confidence based on market hint
    - Prefers ZA-local profiles when WMI or hint points to South Africa
    - Returns updated inferred fields + notes + warnings
    """
    if not context.market_hint:
        return {}, ["No market hint provided → no Layer 3 adjustments"], []

    market = context.market_hint.upper()
    if market not in MARKET_STRATEGIES:
        return {}, [f"Unknown market hint '{market}' → no adjustments applied"], []

    strategy = MARKET_STRATEGIES[market]
    adjustments = {}
    notes = [strategy["notes"]]
    warnings = []

    # 1. Check if VIN appears to be ZA-local assembled (WMI-based hint)
    wmi = vin_normalized[:3]
    is_likely_za_local = wmi in ZA_LOCAL_PREFIXES

    if market == "ZA" and is_likely_za_local:
        notes.append(f"Detected ZA-local WMI prefix '{wmi}' → strong preference for local profiles")
        confidence_boost = 1.35  # even stronger than general ZA multiplier
    else:
        confidence_boost = strategy["multiplier"]

    # 2. Re-evaluate / boost Layer 2 matches that match the market
    boosted_fields = {}

    for match in layer2_result.matches:
        rule = match.rule
        if not rule.markets:  # rule applies everywhere
            continue

        if market in [m.upper() for m in rule.markets]:
            # Boost confidence for market-matching rules
            new_conf = min(match.confidence * confidence_boost, 0.99)
            
            if new_conf > match.confidence + 0.05:  # only record meaningful boosts
                for key, value in rule.meaning.items():
                    # Create or update field with boosted confidence
                    ev = EpistemologicalValue(
                        value=value,
                        status=EpistemologicalStatus.CONFIRMED if new_conf >= 0.95 else EpistemologicalStatus.INFERRED,
                        confidence=new_conf,
                        sources=[
                            FieldSource(
                                source_type=SourceType.LAYER_3_MARKET,
                                source_id=f"market_hint_{market}",
                                confidence=confidence_boost,
                                notes=f"Boosted from base conf {match.confidence:.2f}",
                            ),
                        ]
                        + (list(match.rule_sources) if hasattr(match, "rule_sources") else []),
                        explanation=f"Market {market} context boosted rule '{rule.rule_id}'"
                    )
                    boosted_fields[key] = ev

    # 3. Special ZA handling: if no good matches but WMI suggests local → warning
    if market == "ZA" and is_likely_za_local and not any(m.confidence >= 0.9 for m in boosted_fields.values()):
        warnings.append(
            "ZA market hint + local WMI prefix detected, but no strong VDS match. "
            "Consider TransUnion Auto lookup for authoritative ZA-specific data."
        )

    notes.append(f"Applied market multiplier: ×{confidence_boost:.2f}")

    return boosted_fields, notes, warnings
