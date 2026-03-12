"""
AutoECU/core/truth_gate.py
──────────────────────────
Pre-flash safety gates and post-flash verification rules.

The :class:`TruthGate` class enforces the "no-fake-data" contract:

* **Pre-flash**: All mandatory safety conditions must pass before
  programming may start.  Each condition has a design-interface method
  that callers implement (or override with real hardware) and a
  corresponding check method here.

* **Post-flash**: Programming is only considered successful when **all**
  of the following are confirmed from the real ECU:
  1. ECU responds after programming.
  2. Readback or CRC verification passes.
  3. Status frames confirm programming completed.

This module has **no hardware dependency**: all hardware-facing checks are
expressed as boolean parameters supplied by the caller, so the logic can be
unit-tested without any physical device.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from AutoECU.core.flash_session import FlashState, PreflightResult


# ---------------------------------------------------------------------------
# Voltage / communication thresholds (design constants)
# ---------------------------------------------------------------------------

#: Minimum battery voltage required to start a flash session (V).
BATTERY_VOLTAGE_MIN: float = 12.0

#: Maximum battery voltage accepted (V) – protects against charging spikes.
BATTERY_VOLTAGE_MAX: float = 15.5


# ---------------------------------------------------------------------------
# Entitlement roles
# ---------------------------------------------------------------------------

ROLE_ADMIN = "admin"
ROLE_TECHNICIAN = "technician"

#: Roles that are permitted to initiate a flash session.
PERMITTED_FLASH_ROLES: List[str] = [ROLE_ADMIN, ROLE_TECHNICIAN]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class PreflightInput:
    """
    All inputs required to execute the preflight truth gate.

    Every field maps to one of the five mandatory pre-flash checks.
    Fields that require real hardware are supplied as booleans or numeric
    values by the caller; :class:`TruthGate` only evaluates them.
    """

    #: Measured battery voltage in Volts (design interface – no HW dep).
    battery_voltage: float

    #: ``True`` when the communication channel is stable (design interface).
    comm_stable: bool

    #: ECU identifier string read from the vehicle (empty = not identified).
    ecu_id: str

    #: Protocol string expected for this ECU (e.g. ``"ISO15765-11BIT"``).
    expected_protocol: str

    #: Protocol string currently configured on the tool.
    actual_protocol: str

    #: VIN or calibration part number expected for the target ECU.
    expected_calibration_id: str

    #: VIN or calibration part number read from the vehicle.
    actual_calibration_id: str


@dataclass
class EntitlementContext:
    """
    Caller-supplied licence / entitlement information.

    All validation is done offline (workshop environments may not have
    internet connectivity).
    """

    #: Login identity of the operator (username or e-mail).
    operator: str

    #: Hardware identifier of the tool.
    hwid: str

    #: Role assigned to the operator.
    role: str

    #: Whether the entitlement token has been validated (offline or online).
    entitlement_valid: bool


@dataclass
class TruthGateResult:
    """Return value from :meth:`TruthGate.run_preflight`."""

    passed: bool
    failures: List[str] = field(default_factory=list)

    def as_preflight_result(self) -> PreflightResult:
        """Convert to a :class:`~AutoECU.core.flash_session.PreflightResult`."""
        pr = PreflightResult()
        # Mark individual checks from the failures list
        pr.battery_ok = "battery" not in " ".join(self.failures).lower()
        pr.comm_stable = "communication" not in " ".join(self.failures).lower()
        pr.ecu_identified = "ecu" not in " ".join(self.failures).lower()
        pr.protocol_compatible = "protocol" not in " ".join(self.failures).lower()
        pr.calibration_compatible = "calibration" not in " ".join(self.failures).lower()
        pr.failures = list(self.failures)
        return pr


# ---------------------------------------------------------------------------
# TruthGate
# ---------------------------------------------------------------------------

class TruthGate:
    """
    Evaluates pre-flash and post-flash truth conditions.

    This class is stateless – create a new instance per session or reuse
    across sessions; it holds no mutable session data.
    """

    # ------------------------------------------------------------------
    # Pre-flash gate
    # ------------------------------------------------------------------

    def run_preflight(
        self,
        inputs: PreflightInput,
        entitlement: Optional[EntitlementContext] = None,
    ) -> TruthGateResult:
        """
        Run all mandatory pre-flash safety checks.

        Parameters
        ----------
        inputs:
            Hardware / protocol state supplied by the caller.
        entitlement:
            Optional entitlement context.  When provided, the operator's
            role and HWID are validated as part of preflight.

        Returns
        -------
        TruthGateResult
            Contains a ``passed`` flag and a list of human-readable failure
            descriptions.
        """
        failures: List[str] = []

        # 1. Battery voltage check
        if not (BATTERY_VOLTAGE_MIN <= inputs.battery_voltage <= BATTERY_VOLTAGE_MAX):
            failures.append(
                f"Battery voltage out of range: {inputs.battery_voltage:.1f}V "
                f"(required {BATTERY_VOLTAGE_MIN}–{BATTERY_VOLTAGE_MAX}V)"
            )

        # 2. Communication stability
        if not inputs.comm_stable:
            failures.append("Communication channel is not stable")

        # 3. ECU identification
        if not inputs.ecu_id or not inputs.ecu_id.strip():
            failures.append("ECU could not be identified (empty ecu_id)")

        # 4. Protocol compatibility
        if inputs.expected_protocol != inputs.actual_protocol:
            failures.append(
                f"Protocol mismatch: expected {inputs.expected_protocol!r}, "
                f"got {inputs.actual_protocol!r}"
            )

        # 5. Calibration compatibility
        if inputs.expected_calibration_id != inputs.actual_calibration_id:
            failures.append(
                f"Calibration ID mismatch: expected "
                f"{inputs.expected_calibration_id!r}, "
                f"got {inputs.actual_calibration_id!r}"
            )

        # 6. Entitlement (optional but validated when provided)
        if entitlement is not None:
            self._check_entitlement(entitlement, failures)

        return TruthGateResult(passed=len(failures) == 0, failures=failures)

    # ------------------------------------------------------------------
    # Post-flash verification gate
    # ------------------------------------------------------------------

    def verify_flash_result(
        self,
        ecu_responded: bool,
        readback_ok: bool,
        status_frames_ok: bool,
    ) -> TruthGateResult:
        """
        Validate that a flash operation actually succeeded.

        A result is **valid** only if all three conditions are met.
        UI messages must **only** report success when this method returns
        a passing result – never based on internal control-flow flags.

        Parameters
        ----------
        ecu_responded:
            ``True`` if the ECU responded to a post-flash communication
            attempt.
        readback_ok:
            ``True`` if readback or CRC verification of the written data
            passed.
        status_frames_ok:
            ``True`` if ECU status frames confirm programming completed.

        Returns
        -------
        TruthGateResult
            ``passed=True`` only when all three conditions hold.
        """
        failures: List[str] = []

        if not ecu_responded:
            failures.append("ECU did not respond after programming")
        if not readback_ok:
            failures.append("Readback/CRC verification failed")
        if not status_frames_ok:
            failures.append("Status frames did not confirm programming completion")

        return TruthGateResult(passed=len(failures) == 0, failures=failures)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_entitlement(
        self,
        entitlement: EntitlementContext,
        failures: List[str],
    ) -> None:
        """Validate operator role, HWID presence, and entitlement token."""
        if not entitlement.operator or not entitlement.operator.strip():
            failures.append("Entitlement: operator identity is missing")

        if not entitlement.hwid or not entitlement.hwid.strip():
            failures.append("Entitlement: HWID is missing")

        if entitlement.role not in PERMITTED_FLASH_ROLES:
            failures.append(
                f"Entitlement: role {entitlement.role!r} is not permitted "
                f"(allowed: {PERMITTED_FLASH_ROLES})"
            )

        if not entitlement.entitlement_valid:
            failures.append(
                "Entitlement: licence/entitlement token is not valid "
                "(offline validation failed)"
            )
