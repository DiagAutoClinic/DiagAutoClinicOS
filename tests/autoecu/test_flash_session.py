"""
tests/autoecu/test_flash_session.py
─────────────────────────────────────
Unit tests for AutoECU/core/flash_session.py.

All tests are hardware-free and run in pure Python.
"""

from __future__ import annotations

import pytest

from AutoECU.core.flash_session import (
    FlashSession,
    FlashState,
    InvalidStateTransitionError,
    PreflightError,
    PreflightResult,
    VerificationError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_session(**kwargs) -> FlashSession:
    """Return a minimal FlashSession for testing."""
    defaults = dict(
        operator="test_tech",
        hwid="HWID-TEST-001",
        vin="WVWZZZ1JZXW000001",
        ecu_id="ECU-001",
        protocol="ISO15765-11BIT",
    )
    defaults.update(kwargs)
    return FlashSession(**defaults)


def _passing_preflight() -> PreflightResult:
    pr = PreflightResult()
    pr.battery_ok = True
    pr.comm_stable = True
    pr.ecu_identified = True
    pr.protocol_compatible = True
    pr.calibration_compatible = True
    return pr


def _failing_preflight(reason: str = "battery low") -> PreflightResult:
    pr = PreflightResult()
    pr.battery_ok = False
    pr.comm_stable = True
    pr.ecu_identified = True
    pr.protocol_compatible = True
    pr.calibration_compatible = True
    pr.failures = [reason]
    return pr


# ---------------------------------------------------------------------------
# A) Initial state
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_initial_state_is_idle():
    session = _make_session()
    assert session.state == FlashState.IDLE


@pytest.mark.unit
def test_session_id_is_set():
    session = _make_session()
    assert session.session_id
    assert len(session.session_id) == 36  # UUID4 format


@pytest.mark.unit
def test_operator_and_hwid_stored():
    session = _make_session(operator="alice", hwid="HWID-XYZ")
    assert session.operator == "alice"
    assert session.hwid == "HWID-XYZ"


# ---------------------------------------------------------------------------
# B) Happy-path transitions: IDLE → PREFLIGHT → PROGRAMMING → VERIFY → COMPLETE
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_happy_path_full_transition():
    session = _make_session()

    session.start_preflight()
    assert session.state == FlashState.PREFLIGHT

    session.complete_preflight(_passing_preflight())
    assert session.state == FlashState.PROGRAMMING

    session.start_verify()
    assert session.state == FlashState.VERIFY

    session.complete_verify(
        ecu_responded=True,
        readback_ok=True,
        status_frames_ok=True,
    )
    assert session.state == FlashState.COMPLETE


# ---------------------------------------------------------------------------
# C) Disallowed / skipping transitions
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_cannot_skip_preflight():
    """Jumping straight from IDLE to PROGRAMMING must raise."""
    session = _make_session()
    with pytest.raises(InvalidStateTransitionError):
        session.start_verify()


@pytest.mark.unit
def test_cannot_skip_programming():
    """Jumping from PREFLIGHT to VERIFY without going through PROGRAMMING must raise."""
    session = _make_session()
    session.start_preflight()
    with pytest.raises(InvalidStateTransitionError):
        session.start_verify()


@pytest.mark.unit
def test_cannot_skip_verify():
    """Calling complete_verify from PROGRAMMING (bypassing start_verify) must raise."""
    session = _make_session()
    session.start_preflight()
    session.complete_preflight(_passing_preflight())
    # PROGRAMMING state – calling complete_verify is invalid
    with pytest.raises(InvalidStateTransitionError):
        session.complete_verify(True, True, True)


@pytest.mark.unit
def test_cannot_restart_from_complete():
    session = _make_session()
    session.start_preflight()
    session.complete_preflight(_passing_preflight())
    session.start_verify()
    session.complete_verify(True, True, True)
    assert session.state == FlashState.COMPLETE
    with pytest.raises(InvalidStateTransitionError):
        session.start_preflight()


@pytest.mark.unit
def test_cannot_restart_from_failed():
    session = _make_session()
    session.fail("test failure")
    assert session.state == FlashState.FAILED
    with pytest.raises(InvalidStateTransitionError):
        session.start_preflight()


# ---------------------------------------------------------------------------
# D) Failure paths
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_preflight_failure_moves_to_failed():
    session = _make_session()
    session.start_preflight()
    with pytest.raises(PreflightError):
        session.complete_preflight(_failing_preflight("battery low"))
    assert session.state == FlashState.FAILED


@pytest.mark.unit
def test_verify_ecu_not_responded():
    session = _make_session()
    session.start_preflight()
    session.complete_preflight(_passing_preflight())
    session.start_verify()
    with pytest.raises(VerificationError):
        session.complete_verify(
            ecu_responded=False,
            readback_ok=True,
            status_frames_ok=True,
        )
    assert session.state == FlashState.FAILED


@pytest.mark.unit
def test_verify_readback_failed():
    session = _make_session()
    session.start_preflight()
    session.complete_preflight(_passing_preflight())
    session.start_verify()
    with pytest.raises(VerificationError):
        session.complete_verify(
            ecu_responded=True,
            readback_ok=False,
            status_frames_ok=True,
        )
    assert session.state == FlashState.FAILED


@pytest.mark.unit
def test_verify_status_frames_failed():
    session = _make_session()
    session.start_preflight()
    session.complete_preflight(_passing_preflight())
    session.start_verify()
    with pytest.raises(VerificationError):
        session.complete_verify(
            ecu_responded=True,
            readback_ok=True,
            status_frames_ok=False,
        )
    assert session.state == FlashState.FAILED


@pytest.mark.unit
def test_fail_from_any_active_state():
    for advance in [
        lambda s: None,                          # IDLE
        lambda s: s.start_preflight(),           # PREFLIGHT
        lambda s: (
            s.start_preflight(),
            s.complete_preflight(_passing_preflight()),
        ),                                        # PROGRAMMING
    ]:
        session = _make_session()
        advance(session)
        session.fail("explicit fail")
        assert session.state == FlashState.FAILED


@pytest.mark.unit
def test_fail_on_terminal_state_is_noop():
    """Calling fail() on an already-terminal state must not raise."""
    session = _make_session()
    session.fail("first")
    assert session.state == FlashState.FAILED
    session.fail("second")  # should be a no-op
    assert session.state == FlashState.FAILED


# ---------------------------------------------------------------------------
# E) Developer override
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_force_state_requires_reason():
    session = _make_session()
    with pytest.raises(ValueError):
        session.force_state(FlashState.PROGRAMMING, "")


@pytest.mark.unit
def test_force_state_whitespace_reason_rejected():
    session = _make_session()
    with pytest.raises(ValueError):
        session.force_state(FlashState.PROGRAMMING, "   ")


@pytest.mark.unit
def test_force_state_records_developer_override():
    session = _make_session()
    session.force_state(FlashState.PROGRAMMING, "recovery test bypass")
    assert session.state == FlashState.PROGRAMMING
    events = [e["event_type"] for e in session.audit_trail]
    assert "DEVELOPER_OVERRIDE" in events


@pytest.mark.unit
def test_force_state_override_detail_in_audit():
    session = _make_session()
    reason = "deliberate skip for integration test"
    session.force_state(FlashState.VERIFY, reason)
    override_events = [
        e for e in session.audit_trail
        if e["event_type"] == "DEVELOPER_OVERRIDE"
    ]
    assert override_events, "DEVELOPER_OVERRIDE event not found"
    assert reason in override_events[-1]["detail"]


# ---------------------------------------------------------------------------
# F) Audit trail
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_audit_trail_created_at_init():
    session = _make_session()
    assert len(session.audit_trail) >= 1
    first = session.audit_trail[0]
    assert first["event_type"] == "SESSION_CREATED"
    assert first["operator"] == "test_tech"
    assert first["hwid"] == "HWID-TEST-001"


@pytest.mark.unit
def test_audit_trail_grows_on_transitions():
    session = _make_session()
    initial_len = len(session.audit_trail)
    session.start_preflight()
    assert len(session.audit_trail) > initial_len


@pytest.mark.unit
def test_summary_contains_required_fields():
    session = _make_session()
    summary = session.summary()
    required = {
        "session_id", "operator", "hwid", "vin", "ecu_id",
        "protocol", "firmware_hash", "final_state", "audit_trail",
    }
    for field in required:
        assert field in summary, f"Missing field: {field}"


@pytest.mark.unit
def test_summary_final_state_is_string():
    session = _make_session()
    session.start_preflight()
    session.complete_preflight(_passing_preflight())
    session.start_verify()
    session.complete_verify(True, True, True)
    assert session.summary()["final_state"] == "COMPLETE"
