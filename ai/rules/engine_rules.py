# ai/rules/engine_rules.py

from typing import Dict, Any, Optional, List
from .base import BaseRule, RuleResult, DiagnosticIssue

class EngineOverheatRule(BaseRule):
    def __init__(self):
        super().__init__("Engine Overheat Detection")

    def evaluate(self, data: Dict[str, Any]) -> Optional[RuleResult]:
        coolant_temp = self._extract_parameter(data, "coolant_temp", 90)
        if not isinstance(coolant_temp, (int, float)):
            return None
        if coolant_temp > 105:
            issue = DiagnosticIssue(
                "URGENT: Engine overheating detected",
                severity="CRITICAL",
                category="ENGINE"
            )
            return RuleResult([issue], confidence=0.95)
        return None

class CoolantTemperatureRule(BaseRule):
    def __init__(self):
        super().__init__("Coolant Temperature Check")

    def evaluate(self, data: Dict[str, Any]) -> Optional[RuleResult]:
        coolant_temp = self._extract_parameter(data, "coolant_temp", 90)
        if not isinstance(coolant_temp, (int, float)):
            return None
        if coolant_temp < 70:
            issue = DiagnosticIssue(
                "Coolant temperature too low - thermostat issue?",
                severity="WARNING",
                category="ENGINE"
            )
            return RuleResult([issue], confidence=0.85)
        return None

class BatteryVoltageRule(BaseRule):
    def __init__(self):
        super().__init__("Battery Voltage Check")

    def evaluate(self, data: Dict[str, Any]) -> Optional[RuleResult]:
        voltage = self._extract_parameter(data, "battery_voltage", 14.0)
        if not isinstance(voltage, (int, float)):
            return None
        if voltage < 12.0:
            issue = DiagnosticIssue(
                "URGENT: Low battery voltage - charging system fault",
                severity="HIGH",
                category="ELECTRICAL"
            )
            return RuleResult([issue], confidence=0.90)
        return None

class MisfireDetectionRule(BaseRule):
    def __init__(self):
        super().__init__("Cylinder Misfire Detection")

    def evaluate(self, data: Dict[str, Any]) -> Optional[RuleResult]:
        dtc_codes = data.get("dtc_codes", [])
        if any("P030" in str(code) for code in dtc_codes):
            issue = DiagnosticIssue(
                "Cylinder misfire detected",
                severity="HIGH",
                category="ENGINE"
            )
            return RuleResult([issue], confidence=0.95)
        return None

class DTCDetectionRule(BaseRule):
    def __init__(self):
        super().__init__("DTC Code Reporting")

    def evaluate(self, data: Dict[str, Any]) -> Optional[RuleResult]:
        dtc_codes = data.get("dtc_codes", [])
        if dtc_codes:
            issue = DiagnosticIssue(
                f"DTCs present: {', '.join(dtc_codes)}",
                severity="MEDIUM",
                category="GENERAL"
            )
            return RuleResult([issue], confidence=0.95)
        return None

def create_engine_rules() -> List[BaseRule]:
    """Factory function to create all engine-related rules."""
    return [
        EngineOverheatRule(),
        CoolantTemperatureRule(),
        BatteryVoltageRule(),
        MisfireDetectionRule(),
        DTCDetectionRule(),
    ]