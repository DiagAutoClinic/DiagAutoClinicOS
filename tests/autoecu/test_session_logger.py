"""
tests/autoecu/test_session_logger.py
──────────────────────────────────────
Unit tests for AutoECU/logging/session_logger.py.

Covers:
* JSONL structure and required fields
* Hash-chain integrity (prev_hash chaining)
* Entry self-hash (entry_hash)
* verify_log_chain – passes on untampered log, detects tampering
* Multi-entry chaining
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from AutoECU.core.flash_session import FlashSession, FlashState, PreflightResult
from AutoECU.logging.session_logger import SessionLogger, verify_log_chain


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = {
    "timestamp",
    "operator",
    "hwid",
    "vin",
    "ecu_id",
    "software_number",
    "protocol",
    "firmware_hash",
    "actions",
    "result_state",
    "prev_hash",
    "entry_hash",
    "session_id",
}


def _make_session(
    operator: str = "tech_user",
    hwid: str = "HWID-LOGGER-001",
    vin: str = "VIN-TEST-1234",
    ecu_id: str = "ECU-LOGGER-001",
) -> FlashSession:
    return FlashSession(
        operator=operator,
        hwid=hwid,
        vin=vin,
        ecu_id=ecu_id,
        protocol="ISO15765-11BIT",
    )


def _passing_preflight() -> PreflightResult:
    pr = PreflightResult()
    pr.battery_ok = True
    pr.comm_stable = True
    pr.ecu_identified = True
    pr.protocol_compatible = True
    pr.calibration_compatible = True
    return pr


def _run_to_complete(session: FlashSession) -> None:
    session.start_preflight()
    session.complete_preflight(_passing_preflight())
    session.start_verify()
    session.complete_verify(True, True, True)


def _run_to_failed(session: FlashSession) -> None:
    session.fail("simulated failure")


@pytest.fixture()
def log_dir(tmp_path) -> Path:
    return tmp_path / "autoecu_logs"


@pytest.fixture()
def logger(log_dir) -> SessionLogger:
    return SessionLogger(log_dir=log_dir)


# ---------------------------------------------------------------------------
# A) Log directory creation
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_log_dir_created_automatically(tmp_path):
    new_dir = tmp_path / "new" / "nested" / "dir"
    assert not new_dir.exists()
    SessionLogger(log_dir=new_dir)
    assert new_dir.exists()


# ---------------------------------------------------------------------------
# B) JSONL structure and required fields
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_log_session_writes_a_file(logger, log_dir):
    session = _make_session()
    _run_to_complete(session)
    log_path = logger.log_session(session)
    assert log_path.exists()
    assert log_path.suffix == ".jsonl"


@pytest.mark.unit
def test_log_session_produces_valid_json(logger):
    session = _make_session()
    _run_to_complete(session)
    log_path = logger.log_session(session)
    line = log_path.read_text(encoding="utf-8").strip()
    entry = json.loads(line)  # must not raise
    assert isinstance(entry, dict)


@pytest.mark.unit
def test_log_session_contains_required_fields(logger):
    session = _make_session()
    _run_to_complete(session)
    log_path = logger.log_session(session)
    entry = json.loads(log_path.read_text(encoding="utf-8").strip())
    for field in REQUIRED_FIELDS:
        assert field in entry, f"Missing required field: {field!r}"


@pytest.mark.unit
def test_log_session_operator_matches(logger):
    session = _make_session(operator="alice")
    _run_to_complete(session)
    log_path = logger.log_session(session)
    entry = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert entry["operator"] == "alice"


@pytest.mark.unit
def test_log_session_hwid_matches(logger):
    session = _make_session(hwid="HWID-XYZ")
    _run_to_complete(session)
    log_path = logger.log_session(session)
    entry = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert entry["hwid"] == "HWID-XYZ"


@pytest.mark.unit
def test_log_session_vin_matches(logger):
    session = _make_session(vin="VIN-12345")
    _run_to_complete(session)
    log_path = logger.log_session(session)
    entry = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert entry["vin"] == "VIN-12345"


@pytest.mark.unit
def test_log_session_result_state_complete(logger):
    session = _make_session()
    _run_to_complete(session)
    log_path = logger.log_session(session)
    entry = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert entry["result_state"] == "COMPLETE"


@pytest.mark.unit
def test_log_session_result_state_failed(logger):
    session = _make_session()
    _run_to_failed(session)
    log_path = logger.log_session(session)
    entry = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert entry["result_state"] == "FAILED"


@pytest.mark.unit
def test_log_session_actions_is_list(logger):
    session = _make_session()
    _run_to_complete(session)
    log_path = logger.log_session(session)
    entry = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert isinstance(entry["actions"], list)
    assert len(entry["actions"]) > 0


@pytest.mark.unit
def test_log_session_firmware_hash_stored(logger):
    session = _make_session()
    session.firmware_hash = "a" * 64
    _run_to_complete(session)
    log_path = logger.log_session(session)
    entry = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert entry["firmware_hash"] == "a" * 64


# ---------------------------------------------------------------------------
# C) Genesis / first-entry hash chain
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_first_entry_has_genesis_prev_hash(logger):
    session = _make_session()
    _run_to_complete(session)
    log_path = logger.log_session(session)
    entry = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert entry["prev_hash"] == "GENESIS"


@pytest.mark.unit
def test_entry_hash_is_64_hex_chars(logger):
    session = _make_session()
    _run_to_complete(session)
    log_path = logger.log_session(session)
    entry = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert len(entry["entry_hash"]) == 64
    int(entry["entry_hash"], 16)  # valid hex


# ---------------------------------------------------------------------------
# D) Multi-entry hash chain
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_second_entry_prev_hash_references_first(logger):
    s1 = _make_session(operator="op1")
    _run_to_complete(s1)
    log_path = logger.log_session(s1)

    # Read first entry as raw line
    lines = [l.strip() for l in log_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    first_line = lines[0]

    import hashlib
    expected_prev = hashlib.sha256(first_line.encode("utf-8")).hexdigest()

    s2 = _make_session(operator="op2")
    _run_to_complete(s2)
    logger.log_session(s2)

    lines = [l.strip() for l in log_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    second_entry = json.loads(lines[1])
    assert second_entry["prev_hash"] == expected_prev


@pytest.mark.unit
def test_three_entries_form_valid_chain(logger):
    for i in range(3):
        s = _make_session(operator=f"op{i}")
        _run_to_complete(s)
        logger.log_session(s)

    log_path = logger._current_log_path()
    valid, errors = verify_log_chain(log_path)
    assert valid, f"Chain validation failed: {errors}"


# ---------------------------------------------------------------------------
# E) verify_log_chain
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_verify_log_chain_on_untampered_log(logger):
    for _ in range(5):
        s = _make_session()
        _run_to_complete(s)
        logger.log_session(s)

    log_path = logger._current_log_path()
    valid, errors = verify_log_chain(log_path)
    assert valid, errors


@pytest.mark.unit
def test_verify_log_chain_missing_file(tmp_path):
    missing = tmp_path / "nonexistent.jsonl"
    valid, errors = verify_log_chain(missing)
    assert not valid
    assert errors


@pytest.mark.unit
def test_verify_log_chain_empty_file(tmp_path):
    empty_file = tmp_path / "empty.jsonl"
    empty_file.write_text("")
    valid, errors = verify_log_chain(empty_file)
    assert valid
    assert not errors


@pytest.mark.unit
def test_verify_log_chain_detects_tampered_prev_hash(logger):
    """Manually tamper with a prev_hash and expect chain validation to fail."""
    for _ in range(2):
        s = _make_session()
        _run_to_complete(s)
        logger.log_session(s)

    log_path = logger._current_log_path()
    lines = [l for l in log_path.read_text(encoding="utf-8").splitlines() if l.strip()]

    # Tamper with the second entry's prev_hash
    second_entry = json.loads(lines[1])
    second_entry["prev_hash"] = "tampered" + "0" * 57
    lines[1] = json.dumps(second_entry, separators=(",", ":"), sort_keys=True)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    valid, errors = verify_log_chain(log_path)
    assert not valid
    assert errors


@pytest.mark.unit
def test_verify_log_chain_detects_tampered_content(logger):
    """Modify an entry's content and expect entry_hash mismatch."""
    s = _make_session()
    _run_to_complete(s)
    logger.log_session(s)

    log_path = logger._current_log_path()
    lines = [l for l in log_path.read_text(encoding="utf-8").splitlines() if l.strip()]

    entry = json.loads(lines[0])
    entry["operator"] = "TAMPERED_USER"
    lines[0] = json.dumps(entry, separators=(",", ":"), sort_keys=True)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    valid, errors = verify_log_chain(log_path)
    assert not valid
    assert errors


# ---------------------------------------------------------------------------
# F) log_entry generic helper
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_log_entry_returns_path_and_hash(logger):
    log_path, entry_hash = logger.log_entry({"operator": "alice", "action": "test"})
    assert log_path.exists()
    assert len(entry_hash) == 64


@pytest.mark.unit
def test_log_entry_injects_timestamp(logger):
    log_path, _ = logger.log_entry({"action": "no_ts"})
    line = log_path.read_text(encoding="utf-8").strip()
    entry = json.loads(line)
    assert "timestamp" in entry
