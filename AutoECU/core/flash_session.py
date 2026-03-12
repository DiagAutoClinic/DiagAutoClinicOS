"""
AutoECU/core/flash_session.py
─────────────────────────────
Enforced flash-session state machine.

Allowed transitions (no bypass without an explicit developer override):

    IDLE → PREFLIGHT → PROGRAMMING → VERIFY → COMPLETE
                                             ↘ FAILED

Any attempt to skip a step raises :class:`InvalidStateTransitionError`.

A developer-level bypass is available via :meth:`FlashSession.force_state`
but it **must** supply a non-empty ``reason`` string and the call is
recorded in the session audit trail so that every override is traceable.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from enum import Enum, auto
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# State enumeration
# ---------------------------------------------------------------------------

class FlashState(Enum):
    """All possible states in a flash session lifecycle."""

    IDLE = auto()
    PREFLIGHT = auto()
    PROGRAMMING = auto()
    VERIFY = auto()
    COMPLETE = auto()
    FAILED = auto()


# ---------------------------------------------------------------------------
# Allowed transitions (defines the enforced state machine)
# ---------------------------------------------------------------------------

_ALLOWED_TRANSITIONS: Dict[FlashState, List[FlashState]] = {
    FlashState.IDLE: [FlashState.PREFLIGHT, FlashState.FAILED],
    FlashState.PREFLIGHT: [FlashState.PROGRAMMING, FlashState.FAILED],
    FlashState.PROGRAMMING: [FlashState.VERIFY, FlashState.FAILED],
    FlashState.VERIFY: [FlashState.COMPLETE, FlashState.FAILED],
    FlashState.COMPLETE: [],
    FlashState.FAILED: [],
}


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class InvalidStateTransitionError(Exception):
    """Raised when a disallowed state transition is attempted."""


class PreflightError(Exception):
    """Raised when a preflight check fails."""


class VerificationError(Exception):
    """Raised when post-flash verification fails."""


# ---------------------------------------------------------------------------
# Preflight result
# ---------------------------------------------------------------------------

class PreflightResult:
    """Holds the outcome of all preflight checks."""

    def __init__(self) -> None:
        self.battery_ok: bool = False
        self.comm_stable: bool = False
        self.ecu_identified: bool = False
        self.protocol_compatible: bool = False
        self.calibration_compatible: bool = False
        self.failures: List[str] = []

    @property
    def passed(self) -> bool:
        """Return True only when every check has passed."""
        return (
            self.battery_ok
            and self.comm_stable
            and self.ecu_identified
            and self.protocol_compatible
            and self.calibration_compatible
            and not self.failures
        )


# ---------------------------------------------------------------------------
# FlashSession
# ---------------------------------------------------------------------------

class FlashSession:
    """
    Manages a single ECU flash lifecycle with an enforced state machine.

    Parameters
    ----------
    operator:
        Username / operator identifier (required for the audit trail).
    hwid:
        Hardware identifier of the tool performing the flash.
    vin:
        Vehicle Identification Number (may be empty if unknown at session
        creation time; should be populated before PREFLIGHT).
    ecu_id:
        ECU identifier / part number.
    protocol:
        Protocol string used for communication (e.g. ``"ISO15765-11BIT"``).
    """

    def __init__(
        self,
        operator: str,
        hwid: str,
        vin: str = "",
        ecu_id: str = "",
        protocol: str = "",
    ) -> None:
        self._session_id: str = str(uuid.uuid4())
        self._state: FlashState = FlashState.IDLE
        self._operator: str = operator
        self._hwid: str = hwid
        self._vin: str = vin
        self._ecu_id: str = ecu_id
        self._protocol: str = protocol

        # Firmware / calibration hash stored after integrity check
        self._firmware_hash: Optional[str] = None
        self._software_number: Optional[str] = None

        # Post-flash verification results
        self._ecu_responded_after_flash: bool = False
        self._readback_verified: bool = False
        self._status_frames_ok: bool = False

        # Preflight results
        self._preflight_result: Optional[PreflightResult] = None

        # Audit trail – list of transition records
        self._audit_trail: List[Dict[str, Any]] = []

        # Record session creation
        self._record_event("SESSION_CREATED", "Flash session initialised")

    # ------------------------------------------------------------------
    # Public properties
    # ------------------------------------------------------------------

    @property
    def session_id(self) -> str:
        """Unique identifier for this session."""
        return self._session_id

    @property
    def state(self) -> FlashState:
        """Current state of the session."""
        return self._state

    @property
    def operator(self) -> str:
        return self._operator

    @property
    def hwid(self) -> str:
        return self._hwid

    @property
    def vin(self) -> str:
        return self._vin

    @vin.setter
    def vin(self, value: str) -> None:
        self._vin = value

    @property
    def ecu_id(self) -> str:
        return self._ecu_id

    @ecu_id.setter
    def ecu_id(self, value: str) -> None:
        self._ecu_id = value

    @property
    def protocol(self) -> str:
        return self._protocol

    @protocol.setter
    def protocol(self, value: str) -> None:
        self._protocol = value

    @property
    def firmware_hash(self) -> Optional[str]:
        """SHA-256 hash of the firmware/calibration file (set by caller)."""
        return self._firmware_hash

    @firmware_hash.setter
    def firmware_hash(self, value: str) -> None:
        self._firmware_hash = value

    @property
    def software_number(self) -> Optional[str]:
        """ECU software / calibration part number."""
        return self._software_number

    @software_number.setter
    def software_number(self, value: str) -> None:
        self._software_number = value

    @property
    def audit_trail(self) -> List[Dict[str, Any]]:
        """Read-only snapshot of all recorded audit events."""
        return list(self._audit_trail)

    @property
    def preflight_result(self) -> Optional[PreflightResult]:
        """Result of the most recent preflight execution."""
        return self._preflight_result

    # ------------------------------------------------------------------
    # State-machine transitions
    # ------------------------------------------------------------------

    def _transition(self, new_state: FlashState, reason: str) -> None:
        """
        Perform a validated state transition.

        Parameters
        ----------
        new_state:
            Target state.
        reason:
            Human-readable description logged in the audit trail.

        Raises
        ------
        InvalidStateTransitionError
            When the requested transition is not permitted by the state
            machine.
        """
        allowed = _ALLOWED_TRANSITIONS.get(self._state, [])
        if new_state not in allowed:
            raise InvalidStateTransitionError(
                f"Cannot transition from {self._state.name} to "
                f"{new_state.name}. Allowed: "
                f"{[s.name for s in allowed]}"
            )
        old_state = self._state
        self._state = new_state
        self._record_event(
            "STATE_TRANSITION",
            f"{old_state.name} → {new_state.name}: {reason}",
        )

    def start_preflight(self) -> None:
        """
        Advance from IDLE to PREFLIGHT.

        Call before executing individual preflight checks.

        Raises
        ------
        InvalidStateTransitionError
            When the session is not in IDLE state.
        """
        self._transition(FlashState.PREFLIGHT, "Beginning preflight checks")

    def complete_preflight(self, result: PreflightResult) -> None:
        """
        Record the preflight outcome and advance to PROGRAMMING (or FAILED).

        Parameters
        ----------
        result:
            Populated :class:`PreflightResult` instance.

        Raises
        ------
        PreflightError
            When one or more preflight checks failed (session moves to FAILED).
        InvalidStateTransitionError
            When the session is not in PREFLIGHT state.
        """
        if self._state != FlashState.PREFLIGHT:
            raise InvalidStateTransitionError(
                f"complete_preflight() called from {self._state.name}, "
                "expected PREFLIGHT"
            )
        self._preflight_result = result
        if result.passed:
            self._transition(
                FlashState.PROGRAMMING, "All preflight checks passed"
            )
        else:
            self._transition(
                FlashState.FAILED,
                f"Preflight failed: {result.failures}",
            )
            raise PreflightError(
                f"Preflight checks failed: {result.failures}"
            )

    def start_verify(self) -> None:
        """
        Advance from PROGRAMMING to VERIFY.

        Call after all ECU write operations are complete.

        Raises
        ------
        InvalidStateTransitionError
            When the session is not in PROGRAMMING state.
        """
        self._transition(
            FlashState.VERIFY, "Programming complete; beginning verification"
        )

    def complete_verify(
        self,
        ecu_responded: bool,
        readback_ok: bool,
        status_frames_ok: bool,
    ) -> None:
        """
        Record verification results and advance to COMPLETE or FAILED.

        A session is only considered **successful** when **all three**
        verification conditions are met:

        1. The ECU responds after programming.
        2. Readback or CRC verification passes.
        3. Status frames confirm programming completed.

        UI messages must only report success once this method advances the
        state to COMPLETE – never based on internal flags alone.

        Parameters
        ----------
        ecu_responded:
            ``True`` if the ECU responded to a communication attempt after
            the flash operation.
        readback_ok:
            ``True`` if readback / CRC check of the written data passed.
        status_frames_ok:
            ``True`` if ECU status frames confirm the programming is done.

        Raises
        ------
        VerificationError
            When verification fails (session moves to FAILED).
        InvalidStateTransitionError
            When the session is not in VERIFY state.
        """
        if self._state != FlashState.VERIFY:
            raise InvalidStateTransitionError(
                f"complete_verify() called from {self._state.name}, "
                "expected VERIFY"
            )
        self._ecu_responded_after_flash = ecu_responded
        self._readback_verified = readback_ok
        self._status_frames_ok = status_frames_ok

        if ecu_responded and readback_ok and status_frames_ok:
            self._transition(
                FlashState.COMPLETE,
                "Verification passed: ECU responded, readback OK, "
                "status frames confirmed",
            )
        else:
            failures = []
            if not ecu_responded:
                failures.append("ECU did not respond after programming")
            if not readback_ok:
                failures.append("Readback/CRC check failed")
            if not status_frames_ok:
                failures.append("Status frames did not confirm completion")
            self._transition(
                FlashState.FAILED,
                f"Verification failed: {'; '.join(failures)}",
            )
            raise VerificationError(
                f"Post-flash verification failed: {'; '.join(failures)}"
            )

    def fail(self, reason: str) -> None:
        """
        Move the session to FAILED from any non-terminal state.

        Parameters
        ----------
        reason:
            Description of why the session is failing.
        """
        if self._state in (FlashState.COMPLETE, FlashState.FAILED):
            return  # already terminal – nothing to do
        self._transition(FlashState.FAILED, reason)

    # ------------------------------------------------------------------
    # Developer override
    # ------------------------------------------------------------------

    def force_state(self, target: FlashState, reason: str) -> None:
        """
        **Developer override** – bypass the normal transition rules.

        This method exists for testing and exceptional recovery scenarios.
        Every call is **always** recorded in the audit trail with the
        supplied reason so that the bypass is fully traceable.

        Parameters
        ----------
        target:
            The state to force the session into.
        reason:
            **Mandatory** non-empty explanation for the override.

        Raises
        ------
        ValueError
            When ``reason`` is empty or whitespace-only.
        """
        if not reason or not reason.strip():
            raise ValueError(
                "force_state() requires a non-empty 'reason' for auditability"
            )
        old_state = self._state
        self._state = target
        self._record_event(
            "DEVELOPER_OVERRIDE",
            f"FORCED {old_state.name} → {target.name}: {reason}",
        )

    # ------------------------------------------------------------------
    # Audit helpers
    # ------------------------------------------------------------------

    def _record_event(self, event_type: str, detail: str) -> None:
        """Append a timestamped event to the internal audit trail."""
        self._audit_trail.append(
            {
                "timestamp": time.time(),
                "session_id": self._session_id,
                "operator": self._operator,
                "hwid": self._hwid,
                "vin": self._vin,
                "ecu_id": self._ecu_id,
                "event_type": event_type,
                "detail": detail,
                "state": self._state.name,
            }
        )

    def summary(self) -> Dict[str, Any]:
        """
        Return a serialisable summary of the session suitable for logging.

        Returns
        -------
        dict
            Session summary with all key fields populated.
        """
        return {
            "session_id": self._session_id,
            "operator": self._operator,
            "hwid": self._hwid,
            "vin": self._vin,
            "ecu_id": self._ecu_id,
            "software_number": self._software_number,
            "protocol": self._protocol,
            "firmware_hash": self._firmware_hash,
            "final_state": self._state.name,
            "ecu_responded_after_flash": self._ecu_responded_after_flash,
            "readback_verified": self._readback_verified,
            "status_frames_ok": self._status_frames_ok,
            "audit_trail": self.audit_trail,
        }

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"FlashSession(id={self._session_id!r}, "
            f"state={self._state.name}, "
            f"operator={self._operator!r})"
        )
