# ai/rules/evidence_rules.py

from typing import Dict, Any, Optional
from .base import EvidenceRule, EvidenceResult
from ..core.evidence import EvidenceVector, EvidenceType

class CoolantTempEvidenceRule(EvidenceRule):
    """Rule to detect high coolant temperature evidence"""

    def __init__(self):
        super().__init__("Coolant Temperature Evidence")

    def evaluate_evidence(self, data: Dict[str, Any]) -> Optional[EvidenceResult]:
        coolant_temp = self._extract_parameter(data, "coolant_temp", 90)
        if not isinstance(coolant_temp, (int, float)):
            return None

        evidence_vector = EvidenceVector()
        # High coolant temp is evidence for engine issues
        is_high = self._check_threshold(coolant_temp, 105, "gt")
        evidence_vector.add_evidence("coolant_temp_high", is_high, EvidenceType.BOOLEAN, confidence=0.95)

        return EvidenceResult(evidence_vector, confidence=0.95)

class BatteryVoltageEvidenceRule(EvidenceRule):
    """Rule to detect low battery voltage evidence"""

    def __init__(self):
        super().__init__("Battery Voltage Evidence")

    def evaluate_evidence(self, data: Dict[str, Any]) -> Optional[EvidenceResult]:
        voltage = self._extract_parameter(data, "battery_voltage", 14.0)
        if not isinstance(voltage, (int, float)):
            return None

        evidence_vector = EvidenceVector()
        # Low voltage is evidence for electrical faults
        is_low = self._check_threshold(voltage, 12.0, "lt")
        evidence_vector.add_evidence("battery_voltage_low", is_low, EvidenceType.BOOLEAN, confidence=0.90)

        return EvidenceResult(evidence_vector, confidence=0.90)

class DTCEvidenceRule(EvidenceRule):
    """Rule to detect DTC presence evidence"""

    def __init__(self):
        super().__init__("DTC Evidence")

    def evaluate_evidence(self, data: Dict[str, Any]) -> Optional[EvidenceResult]:
        dtc_codes = data.get("dtc_codes", [])
        has_dtcs = len(dtc_codes) > 0

        evidence_vector = EvidenceVector()
        evidence_vector.add_evidence("dtc_present", has_dtcs, EvidenceType.BOOLEAN, confidence=0.95)

        return EvidenceResult(evidence_vector, confidence=0.95)

class RPMInstabilityEvidenceRule(EvidenceRule):
    """Rule to detect RPM instability evidence"""

    def __init__(self):
        super().__init__("RPM Instability Evidence")

    def evaluate_evidence(self, data: Dict[str, Any]) -> Optional[EvidenceResult]:
        rpm = self._extract_parameter(data, "engine_rpm", 800)
        if not isinstance(rpm, (int, float)):
            return None

        # Check for unstable RPM (this is a simplified check - in reality would need time series)
        # For now, we'll consider RPM outside normal idle range as potentially unstable
        is_unstable = rpm < 600 or rpm > 1200  # Outside typical idle range

        evidence_vector = EvidenceVector()
        evidence_vector.add_evidence("rpm_instability", is_unstable, EvidenceType.BOOLEAN, confidence=0.80)

        return EvidenceResult(evidence_vector, confidence=0.80)

class EngineMisfireEvidenceRule(EvidenceRule):
    """Rule to detect engine misfire evidence from DTCs"""

    def __init__(self):
        super().__init__("Engine Misfire Evidence")

    def evaluate_evidence(self, data: Dict[str, Any]) -> Optional[EvidenceResult]:
        dtc_codes = data.get("dtc_codes", [])
        has_misfire = any("P030" in str(code) for code in dtc_codes)

        evidence_vector = EvidenceVector()
        evidence_vector.add_evidence("engine_misfire", has_misfire, EvidenceType.BOOLEAN, confidence=0.95)

        return EvidenceResult(evidence_vector, confidence=0.95)

class FuelPressureEvidenceRule(EvidenceRule):
    """Rule to detect low fuel pressure evidence"""

    def __init__(self):
        super().__init__("Fuel Pressure Evidence")

    def evaluate_evidence(self, data: Dict[str, Any]) -> Optional[EvidenceResult]:
        fuel_pressure = self._extract_parameter(data, "fuel_pressure", 45)  # PSI
        if not isinstance(fuel_pressure, (int, float)):
            return None

        is_low = self._check_threshold(fuel_pressure, 35, "lt")  # Below 35 PSI is low

        evidence_vector = EvidenceVector()
        evidence_vector.add_evidence("fuel_pressure_low", is_low, EvidenceType.BOOLEAN, confidence=0.85)

        return EvidenceResult(evidence_vector, confidence=0.85)

class OxygenSensorEvidenceRule(EvidenceRule):
    """Rule to detect oxygen sensor fault evidence"""

    def __init__(self):
        super().__init__("Oxygen Sensor Evidence")

    def evaluate_evidence(self, data: Dict[str, Any]) -> Optional[EvidenceResult]:
        dtc_codes = data.get("dtc_codes", [])
        has_o2_fault = any("P013" in str(code) or "P014" in str(code) or "P015" in str(code) or "P016" in str(code)
                          for code in dtc_codes)

        evidence_vector = EvidenceVector()
        evidence_vector.add_evidence("oxygen_sensor_fault", has_o2_fault, EvidenceType.BOOLEAN, confidence=0.90)

        return EvidenceResult(evidence_vector, confidence=0.90)

class TransmissionSlipEvidenceRule(EvidenceRule):
    """Rule to detect transmission slip evidence"""

    def __init__(self):
        super().__init__("Transmission Slip Evidence")

    def evaluate_evidence(self, data: Dict[str, Any]) -> Optional[EvidenceResult]:
        dtc_codes = data.get("dtc_codes", [])
        has_slip = any("P073" in str(code) or "P074" in str(code) for code in dtc_codes)

        evidence_vector = EvidenceVector()
        evidence_vector.add_evidence("transmission_slip", has_slip, EvidenceType.BOOLEAN, confidence=0.85)

        return EvidenceResult(evidence_vector, confidence=0.85)

class BrakeSystemEvidenceRule(EvidenceRule):
    """Rule to detect brake system warning evidence"""

    def __init__(self):
        super().__init__("Brake System Evidence")

    def evaluate_evidence(self, data: Dict[str, Any]) -> Optional[EvidenceResult]:
        dtc_codes = data.get("dtc_codes", [])
        has_brake_warning = any("C1" in str(code) for code in dtc_codes)  # Common brake DTC prefix

        evidence_vector = EvidenceVector()
        evidence_vector.add_evidence("brake_system_warning", has_brake_warning, EvidenceType.BOOLEAN, confidence=0.90)

        return EvidenceResult(evidence_vector, confidence=0.90)

class LeanConditionEvidenceRule(EvidenceRule):
    """Rule to detect lean condition evidence (Lambda > 1.1)"""

    def __init__(self):
        super().__init__("Lean Condition Evidence")

    def evaluate_evidence(self, data: Dict[str, Any]) -> Optional[EvidenceResult]:
        # Extract lambda value (Phase 3: Governing Variable)
        live_params = data.get('live_parameters', {})
        lambda_val = live_params.get('lambda', {}).get('value')
        
        # If lambda is missing, check if we can infer it or just return None
        if lambda_val is None:
             return None

        evidence_vector = EvidenceVector()
        # Lambda > 1.1 is definitive evidence of lean condition
        is_lean = lambda_val > 1.1
        
        # High confidence because lambda is the governing variable
        evidence_vector.add_evidence("lean_condition_detected", is_lean, EvidenceType.BOOLEAN, confidence=0.99)

        return EvidenceResult(evidence_vector, confidence=0.99)

def create_evidence_rules() -> list:
    """Factory function to create all evidence-generating rules."""
    return [
        CoolantTempEvidenceRule(),
        BatteryVoltageEvidenceRule(),
        DTCEvidenceRule(),
        RPMInstabilityEvidenceRule(),
        EngineMisfireEvidenceRule(),
        FuelPressureEvidenceRule(),
        OxygenSensorEvidenceRule(),
        TransmissionSlipEvidenceRule(),
        BrakeSystemEvidenceRule(),
        LeanConditionEvidenceRule(),
    ]