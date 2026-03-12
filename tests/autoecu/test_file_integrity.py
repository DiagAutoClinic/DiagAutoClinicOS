"""
tests/autoecu/test_file_integrity.py
──────────────────────────────────────
Unit tests for AutoECU/security/file_integrity.py.

All tests are hardware-free and use only in-memory bytes.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

import pytest

from AutoECU.security.file_integrity import (
    FileIntegrityChecker,
    FileIntegrityError,
    HashMismatchError,
    UnknownFileError,
)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

SAMPLE_DATA = b"firmware binary content for testing"
SAMPLE_HASH = hashlib.sha256(SAMPLE_DATA).hexdigest()


@pytest.fixture()
def checker_with_allowlist():
    """FileIntegrityChecker with SAMPLE_HASH pre-approved."""
    c = FileIntegrityChecker(require_allowlist=True)
    c.add_to_allowlist(SAMPLE_HASH, "test firmware v1.0")
    return c


@pytest.fixture()
def open_checker():
    """FileIntegrityChecker that does NOT require the allowlist."""
    return FileIntegrityChecker(require_allowlist=False)


# ---------------------------------------------------------------------------
# A) compute_sha256
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_compute_sha256_returns_64_hex_chars():
    result = FileIntegrityChecker.compute_sha256(b"hello")
    assert isinstance(result, str)
    assert len(result) == 64
    int(result, 16)  # must be valid hex


@pytest.mark.unit
def test_compute_sha256_is_deterministic():
    assert (
        FileIntegrityChecker.compute_sha256(b"data")
        == FileIntegrityChecker.compute_sha256(b"data")
    )


@pytest.mark.unit
def test_compute_sha256_different_data():
    assert (
        FileIntegrityChecker.compute_sha256(b"data1")
        != FileIntegrityChecker.compute_sha256(b"data2")
    )


@pytest.mark.unit
def test_compute_sha256_from_path(tmp_path):
    f = tmp_path / "fw.bin"
    f.write_bytes(SAMPLE_DATA)
    result = FileIntegrityChecker.compute_sha256_from_path(f)
    assert result == SAMPLE_HASH


# ---------------------------------------------------------------------------
# B) Verify – hash match
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_verify_correct_expected_hash(checker_with_allowlist):
    result = checker_with_allowlist.verify(SAMPLE_DATA, expected_hash=SAMPLE_HASH)
    assert result == SAMPLE_HASH


@pytest.mark.unit
def test_verify_wrong_expected_hash_raises(checker_with_allowlist):
    bad_hash = "a" * 64
    with pytest.raises(HashMismatchError):
        checker_with_allowlist.verify(SAMPLE_DATA, expected_hash=bad_hash)


@pytest.mark.unit
def test_verify_no_expected_hash_passes(checker_with_allowlist):
    """When expected_hash is None, only the allowlist check runs."""
    result = checker_with_allowlist.verify(SAMPLE_DATA)
    assert result == SAMPLE_HASH


# ---------------------------------------------------------------------------
# C) Allowlist enforcement
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_unknown_file_blocked_by_default():
    checker = FileIntegrityChecker(require_allowlist=True)
    # No entry in the allowlist → must block
    with pytest.raises(UnknownFileError):
        checker.verify(SAMPLE_DATA)


@pytest.mark.unit
def test_unknown_file_allowed_with_reason():
    checker = FileIntegrityChecker(require_allowlist=True)
    result = checker.verify(SAMPLE_DATA, override_reason="development test bypass")
    assert result == SAMPLE_HASH


@pytest.mark.unit
def test_override_without_reason_blocked():
    checker = FileIntegrityChecker(require_allowlist=True)
    with pytest.raises(UnknownFileError):
        checker.verify(SAMPLE_DATA, override_reason="")


@pytest.mark.unit
def test_override_whitespace_reason_blocked():
    checker = FileIntegrityChecker(require_allowlist=True)
    with pytest.raises(UnknownFileError):
        checker.verify(SAMPLE_DATA, override_reason="   ")


@pytest.mark.unit
def test_override_recorded_in_log():
    checker = FileIntegrityChecker(require_allowlist=True)
    reason = "explicit dev override for CI"
    checker.verify(SAMPLE_DATA, override_reason=reason)
    assert len(checker.override_log) == 1
    assert checker.override_log[0]["hash"] == SAMPLE_HASH
    assert checker.override_log[0]["reason"] == reason


@pytest.mark.unit
def test_allowlist_bypass_not_needed_for_known_file(checker_with_allowlist):
    """No override required when file is in allowlist."""
    result = checker_with_allowlist.verify(SAMPLE_DATA)
    assert result == SAMPLE_HASH
    assert len(checker_with_allowlist.override_log) == 0


@pytest.mark.unit
def test_require_allowlist_false_passes_any_file(open_checker):
    unknown_data = b"totally unknown firmware"
    result = open_checker.verify(unknown_data)
    assert len(result) == 64


# ---------------------------------------------------------------------------
# D) Allowlist management
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_add_to_allowlist():
    checker = FileIntegrityChecker()
    checker.add_to_allowlist(SAMPLE_HASH, "fw v1.0")
    assert SAMPLE_HASH in checker.allowlist


@pytest.mark.unit
def test_remove_from_allowlist():
    checker = FileIntegrityChecker()
    checker.add_to_allowlist(SAMPLE_HASH, "fw v1.0")
    checker.remove_from_allowlist(SAMPLE_HASH)
    assert SAMPLE_HASH not in checker.allowlist


@pytest.mark.unit
def test_add_to_allowlist_invalid_hash_raises():
    checker = FileIntegrityChecker()
    with pytest.raises(ValueError):
        checker.add_to_allowlist("tooshort", "bad")


# ---------------------------------------------------------------------------
# E) Allowlist persistence (JSON round-trip)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_save_and_load_allowlist(tmp_path):
    checker = FileIntegrityChecker()
    checker.add_to_allowlist(SAMPLE_HASH, "test fw")

    json_path = tmp_path / "allowlist.json"
    checker.save_allowlist_to_json(json_path)

    checker2 = FileIntegrityChecker(require_allowlist=True)
    checker2.load_allowlist_from_json(json_path)
    assert SAMPLE_HASH in checker2.allowlist


@pytest.mark.unit
def test_load_allowlist_invalid_json_raises(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("[1, 2, 3]")  # array, not object
    checker = FileIntegrityChecker()
    with pytest.raises(ValueError):
        checker.load_allowlist_from_json(bad_file)


# ---------------------------------------------------------------------------
# F) Signature verification hook
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_signature_required_when_provided(open_checker):
    """Providing a signature without a public key must raise."""
    with pytest.raises(FileIntegrityError):
        open_checker.verify(SAMPLE_DATA, signature=b"fakesig")


@pytest.mark.unit
def test_signature_verifier_called(open_checker):
    """Custom signature_verifier returning True must allow the file."""
    def always_ok(data, sig, pubkey):
        return True

    checker = FileIntegrityChecker(
        require_allowlist=False,
        signature_verifier=always_ok,
    )
    result = checker.verify(
        SAMPLE_DATA,
        signature=b"fakesig",
        public_key_pem=b"fakepem",
    )
    assert result == SAMPLE_HASH


@pytest.mark.unit
def test_signature_verifier_failure_raises(open_checker):
    """Custom signature_verifier returning False must raise FileIntegrityError."""
    def always_fail(data, sig, pubkey):
        return False

    checker = FileIntegrityChecker(
        require_allowlist=False,
        signature_verifier=always_fail,
    )
    with pytest.raises(FileIntegrityError):
        checker.verify(
            SAMPLE_DATA,
            signature=b"badsig",
            public_key_pem=b"fakepem",
        )


# ---------------------------------------------------------------------------
# G) verify_from_path
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_verify_from_path(tmp_path):
    fw_file = tmp_path / "firmware.bin"
    fw_file.write_bytes(SAMPLE_DATA)

    checker = FileIntegrityChecker(require_allowlist=True)
    checker.add_to_allowlist(SAMPLE_HASH, "sample fw")

    result = checker.verify_from_path(fw_file, expected_hash=SAMPLE_HASH)
    assert result == SAMPLE_HASH
