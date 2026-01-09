"""
Layer 2 - OEM Grammar Decoder (VDS logic)
Declarative pattern matching on positions 4-8 (sometimes others)
Each rule has explicit confidence + source context
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
import re
import json
from pathlib import Path

from .vin_validator_layer0 import validate_vin
from .layer1_iso import decode_iso, IsoLayer1Result


@dataclass
class VdsRule:
    """Single declarative rule for VDS positions"""
    rule_id: str
    pattern: Dict[str, Any]                              # {"type": "exact", "value": "B58C"}
    meaning: Dict[str, Any]                              # what it implies
    description: str = ""
    markets: List[str] = field(default_factory=list)     # e.g. ["ZA", "EU", "US"]
    positions: List[int] = field(default_factory=list)   # 1-based: [4,5,6,7,8]
    confidence: float = 0.85
    force_verification: bool = False
    force_defer: bool = False
    notes: str = ""


@dataclass
class VdsMatch:
    """Result of a single rule match"""
    rule: VdsRule
    matched_value: str
    confidence: float
    applied: bool = False


@dataclass
class Layer2Result:
    """Aggregated Layer 2 findings with epistemology"""
    matches: List[VdsMatch] = field(default_factory=list)
    best_confidence: float = 0.0
    inferred_fields: Dict[str, Any] = field(default_factory=dict)
    conflicts: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


BRAND_ALIASES = {
    "TOYOTA SOUTH AFRICA (PROSPECTON)": "TOYOTA",
    "TOYOTA SOUTH AFRICA": "TOYOTA",
    "BMW SOUTH AFRICA (ROSSLYN)": "BMW",
    "BMW SOUTH AFRICA": "BMW",
    "BMW AG": "BMW",
    "MERCEDES-BENZ SOUTH AFRICA (EAST LONDON)": "MERCEDES-BENZ",
    "MERCEDES-BENZ SOUTH AFRICA": "MERCEDES-BENZ",
    "VOLKSWAGEN SOUTH AFRICA (KARIEGA)": "VAG",
    "VOLKSWAGEN SOUTH AFRICA": "VAG",
    "VOLKSWAGEN": "VAG",
    "VOLKSWAGEN COMMERCIAL": "VAG",
    "AUDI": "VAG",
    "AUDI SOUTH AFRICA": "VAG",
    "SEAT": "VAG",
    "SKODA": "VAG",
    "ŠKODA": "VAG",
    "BMW USA": "BMW",
    "MERCEDES-BENZ USA": "MERCEDES-BENZ",
    "FORD SOUTH AFRICA (SILVERTON)": "FORD",
    "FORD EUROPE": "FORD",
    "FORD USA": "FORD",
}


class OemGrammarDecoder:
    """Minimal Layer 2 engine - declarative pattern matching"""

    def __init__(self, rules_path: Union[str, Path] = "src/vin/rules/dacos_vin_rules_v0.0.4.json"):
        self.rules: Dict[str, List[VdsRule]] = {}  # brand -> list of rules
        self.load_rules(rules_path)

    def load_rules(self, path: Union[str, Path]):
        path = Path(path)
        if not path.exists():
            print(f"Warning: Rules file not found: {path}")
            return

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        for brand, profile in data.get("oem_profiles", {}).items():
            brand_key = brand.upper()
            print(f"DEBUG: Loading rules for {brand_key}")
            self.rules[brand_key] = []
            
            for rule_data in profile.get("vds_rules", []):
                # Handle both "id" and "rule_id"
                rule_id = rule_data.get("id") or rule_data.get("rule_id")
                if not rule_id:
                    continue
                    
                positions = rule_data.get("positions", rule_data.get("position", []))
                if isinstance(positions, int):
                    positions = [positions]
                    
                rule = VdsRule(
                    rule_id=rule_id,
                    description=rule_data.get("description", ""),
                    markets=rule_data.get("markets", []),
                    positions=positions,
                    pattern=rule_data["pattern"],
                    meaning=rule_data["meaning"],
                    confidence=rule_data.get("confidence", 0.80),
                    force_verification=rule_data.get("force_verification", False),
                    force_defer=rule_data.get("force_defer", False),
                    notes=rule_data.get("notes", "")
                )
                self.rules[brand_key].append(rule)

    def evaluate(self, vin: str, iso_result: IsoLayer1Result, market_hint: Optional[str] = None) -> Layer2Result:
        """Run all relevant rules against the VIN"""
        if not iso_result.manufacturer or not iso_result.manufacturer.value:
            return Layer2Result(notes=["No manufacturer identified in Layer 1 -> skipping Layer 2"])

        brand_key = iso_result.manufacturer.value.upper()
        # Apply alias normalization
        brand_key = BRAND_ALIASES.get(brand_key, brand_key)
        
        # DEBUG
        print(f"DEBUG: Layer 2 evaluate. VIN={vin}, Manuf={iso_result.manufacturer.value}, BrandKey={brand_key}")
        
        rules = self.rules.get(brand_key, [])
        print(f"DEBUG: Found {len(rules)} rules for brand {brand_key}")

        result = Layer2Result()

        vin_upper = vin.upper()

        for rule in rules:
            # Market filter
            if rule.markets and market_hint and market_hint.upper() not in [m.upper() for m in rule.markets]:
                # print(f"DEBUG: Skipping rule {rule.rule_id} due to market filter. Hint={market_hint}, RuleMarkets={rule.markets}")
                continue

            # Extract substring to match
            try:
                substr = "".join(vin_upper[i-1] for i in rule.positions)
            except IndexError:
                result.notes.append(f"Rule {rule.rule_id} has invalid positions")
                continue

            matched = self._match_pattern(substr, rule.pattern)
            if rule.rule_id == "vw_polo_vivo_local":
               print(f"DEBUG: Checking {rule.rule_id}. Substr={substr}, Pattern={rule.pattern}, Matched={matched}")

            if matched:
                match = VdsMatch(
                    rule=rule,
                    matched_value=substr,
                    confidence=rule.confidence * (1.1 if market_hint and market_hint.upper() in rule.markets else 1.0),
                    applied=True
                )
                result.matches.append(match)
                result.inferred_fields.update(rule.meaning)
                result.best_confidence = max(result.best_confidence, match.confidence)

        if not result.matches:
            result.notes.append("No matching VDS rules found")

        return result

    def _match_pattern(self, text: str, pattern: Dict[str, Any]) -> bool:
        ptype = pattern.get("type", "exact").lower()
        value = pattern.get("value", "")

        if ptype == "exact":
            return text == value.upper()
        elif ptype == "prefix":
            return text.startswith(value.upper())
        elif ptype == "regex":
            return bool(re.match(value, text, re.IGNORECASE))
        elif ptype == "one_of":
            return text in [v.upper() for v in pattern.get("values", [])]
        elif ptype == "starts_with":
            return text.startswith(value.upper())
        # ... can easily add "contains", "range", etc later
        return False


# Quick usage example / smoke test
if __name__ == "__main__":
    decoder = OemGrammarDecoder()  # will warn if no file
    # Later: real call after we have iso_result
    print("Layer 2 skeleton loaded. Rules loaded:", len(decoder.rules))