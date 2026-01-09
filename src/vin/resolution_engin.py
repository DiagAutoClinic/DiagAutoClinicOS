"""
/src/vin/resolution_engin.py

"""
from enum import Enum, IntEnum
from dataclasses import dataclass
from typing import Any, List, Optional
import time

class Authority(IntEnum):
    ISO = 10
    OEM_GRAMMAR = 20
    MARKET = 30
    COMMERCIAL = 40
    ECU = 100

class Severity(IntEnum):
    INFO = 10
    WARNING = 20
    CRITICAL = 100

@dataclass(frozen=True)
class Rule:
    source: str
    authority: Authority
    field: str                 # e.g. "engine_capacity", "engine_code"
    value: Any
    severity: Severity
    provenance: str            # VIN / ECU / API name
    timestamp: int = int(time.time())

@dataclass
class Resolution:
    field: str
    resolved_value: Any | None
    winning_rule: Rule | None
    conflicts: List[Rule]
    severity: Severity

class ResolutionEngine:

    def resolve_field(self, rules: List[Rule], field: str) -> Resolution:
        relevant = [r for r in rules if r.field == field]

        if not relevant:
            return Resolution(
                field=field,
                resolved_value=None,
                winning_rule=None,
                conflicts=[],
                severity=Severity.INFO
            )

        # Sort by authority descending
        relevant.sort(key=lambda r: r.authority, reverse=True)
        winner = relevant[0]

        conflicts = []
        max_severity = winner.severity

        for r in relevant[1:]:
            if r.value != winner.value:
                conflicts.append(r)
                max_severity = max(max_severity, r.severity)

        return Resolution(
            field=field,
            resolved_value=winner.value,
            winning_rule=winner,
            conflicts=conflicts,
            severity=max_severity
        )

    def resolve_all(rules: List[Rule]) -> dict[str, Resolution]:
        engine = ResolutionEngine()
        fields = set(r.field for r in rules)

        return {
            field: engine.resolve_field(rules, field)
            for field in fields
        }

class FlashDecision(Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"

@dataclass
class LawResult:
    decision: FlashDecision
    reasons: List[str]

    def pre_flash_safety_law(
        vin_resolution: dict[str, Resolution],
        ecu_snapshot: dict[str, Any]
    ) -> LawResult:

        reasons = []

        engine_res = vin_resolution.get("engine_code")

        if engine_res and engine_res.resolved_value:
            ecu_engine = ecu_snapshot.get("engine_code")

            if ecu_engine and ecu_engine != engine_res.resolved_value:
                reasons.append(
                    f"CRITICAL: ECU engine ({ecu_engine}) "
                    f"≠ VIN/Market engine ({engine_res.resolved_value})"
                )

        if reasons:
            return LawResult(FlashDecision.DENY, reasons)

        return LawResult(FlashDecision.ALLOW, [])

        rules = [
            Rule("ISO", Authority.ISO, "engine_code", None, Severity.INFO, "VIN"),
            Rule("VAG_GRAMMAR", Authority.OEM_GRAMMAR, "engine_code", "CAXA", Severity.WARNING, "VDS"),
            Rule("TransUnion", Authority.MARKET, "engine_code", "CAXA", Severity.WARNING, "ZA_DB"),
            Rule("ECU", Authority.ECU, "engine_code", "CAVA", Severity.CRITICAL, "ME7")
        ]

        ecu_snapshot = {"engine_code": "CAVA"}

        resolution = resolve_all(rules)
        law = pre_flash_safety_law(resolution, ecu_snapshot)

