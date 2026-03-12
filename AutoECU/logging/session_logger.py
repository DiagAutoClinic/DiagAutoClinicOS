"""
AutoECU/logging/session_logger.py
───────────────────────────────────
Immutable JSONL audit trail for AutoECU flash sessions.

Each flash session produces exactly **one** audit log entry appended to
``<log_dir>/autoecu_<date>.jsonl``.

Tamper-resistance
-----------------
Every log entry includes a ``prev_hash`` field that is the SHA-256 digest
of the preceding entry's JSON text (or the sentinel value ``"GENESIS"`` for
the very first entry in a file).  This creates a **hash chain**: modifying
any earlier entry invalidates every subsequent ``prev_hash``, making
tampering immediately detectable via :func:`verify_log_chain`.

Required fields (per the problem spec)
---------------------------------------
* ``timestamp``        – ISO-8601 UTC string
* ``operator``         – operator / user identity
* ``hwid``             – hardware identifier
* ``vin``              – Vehicle Identification Number
* ``ecu_id``           – ECU identifier / software number
* ``software_number``  – calibration / software part number
* ``protocol``         – protocol used
* ``firmware_hash``    – SHA-256 of the firmware/calibration file
* ``actions``          – list of action strings from the audit trail
* ``result_state``     – final flash session state name
* ``prev_hash``        – SHA-256 of the preceding log line (hash chain)
* ``entry_hash``       – SHA-256 of this entry (self-hash for quick lookup)
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from AutoECU.core.flash_session import FlashSession


# ---------------------------------------------------------------------------
# Default log directory
# ---------------------------------------------------------------------------

def _default_log_dir() -> Path:
    """
    Return the platform-appropriate default log directory.

    * Windows: ``%ProgramData%\\DACOS\\logs\\autoecu\\``
    * Linux/macOS: ``~/.dacos/logs/autoecu/``
    """
    if sys.platform == "win32":
        program_data = os.environ.get("ProgramData", "C:\\ProgramData")
        return Path(program_data) / "DACOS" / "logs" / "autoecu"
    return Path.home() / ".dacos" / "logs" / "autoecu"


#: Module-level default; can be overridden by callers.
DEFAULT_LOG_DIR: Path = _default_log_dir()


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return (
        datetime.datetime.now(datetime.timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def _sha256_text(text: str) -> str:
    """Return the SHA-256 hex digest of a UTF-8 encoded string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read_last_entry(log_path: Path) -> Optional[str]:
    """
    Return the last non-empty line of ``log_path``, or ``None`` if the file
    does not exist / is empty.
    """
    if not log_path.exists():
        return None
    last: Optional[str] = None
    with open(log_path, "r", encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()
            if stripped:
                last = stripped
    return last


def _prev_hash_for(log_path: Path) -> str:
    """
    Compute the ``prev_hash`` to embed in the next log entry.

    Returns
    -------
    str
        SHA-256 of the last entry in the log file, or ``"GENESIS"`` when
        the file is empty / absent (first entry in the chain).
    """
    last = _read_last_entry(log_path)
    if last is None:
        return "GENESIS"
    return _sha256_text(last)


# ---------------------------------------------------------------------------
# SessionLogger
# ---------------------------------------------------------------------------

class SessionLogger:
    """
    Writes tamper-resistant JSONL audit log entries for flash sessions.

    Parameters
    ----------
    log_dir:
        Directory to write log files to.  Created automatically if absent.
        Defaults to :data:`DEFAULT_LOG_DIR`.
    """

    def __init__(self, log_dir: Optional[Path] = None) -> None:
        self._log_dir: Path = log_dir if log_dir is not None else DEFAULT_LOG_DIR
        self._log_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log_session(self, session: FlashSession) -> Path:
        """
        Append a complete audit log entry for ``session`` to the JSONL file.

        Parameters
        ----------
        session:
            The completed (or failed) :class:`~AutoECU.core.flash_session.FlashSession`.

        Returns
        -------
        Path
            The path to the log file that was written.
        """
        log_path = self._current_log_path()
        entry = self._build_entry(session, log_path)
        line = json.dumps(entry, separators=(",", ":"), sort_keys=True)
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        return log_path

    def log_entry(self, entry_data: Dict[str, Any]) -> Tuple[Path, str]:
        """
        Append an arbitrary audit entry dict to the log.

        The ``prev_hash`` and ``entry_hash`` fields are computed and
        injected automatically; callers should **not** supply them.

        Parameters
        ----------
        entry_data:
            Dictionary of fields to record.  ``timestamp`` is injected if
            absent.

        Returns
        -------
        tuple[Path, str]
            ``(log_path, entry_hash)``
        """
        log_path = self._current_log_path()
        if "timestamp" not in entry_data:
            entry_data = {"timestamp": _utc_now_iso(), **entry_data}
        prev_hash = _prev_hash_for(log_path)
        entry = {**entry_data, "prev_hash": prev_hash}
        line = json.dumps(entry, separators=(",", ":"), sort_keys=True)
        entry_hash = _sha256_text(line)
        entry["entry_hash"] = entry_hash
        line = json.dumps(entry, separators=(",", ":"), sort_keys=True)
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        return log_path, entry_hash

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _current_log_path(self) -> Path:
        """Return the path to today's log file."""
        date_str = datetime.date.today().isoformat()  # e.g. "2025-03-12"
        return self._log_dir / f"autoecu_{date_str}.jsonl"

    def _build_entry(
        self,
        session: FlashSession,
        log_path: Path,
    ) -> Dict[str, Any]:
        """Build a complete audit entry dict from a FlashSession."""
        summary = session.summary()

        # Collect distinct action strings from the audit trail
        actions: List[str] = [
            event.get("detail", "")
            for event in summary.get("audit_trail", [])
        ]

        prev_hash = _prev_hash_for(log_path)

        entry: Dict[str, Any] = {
            "timestamp": _utc_now_iso(),
            "operator": summary.get("operator", ""),
            "hwid": summary.get("hwid", ""),
            "vin": summary.get("vin", ""),
            "ecu_id": summary.get("ecu_id", ""),
            "software_number": summary.get("software_number") or "",
            "protocol": summary.get("protocol", ""),
            "firmware_hash": summary.get("firmware_hash") or "",
            "actions": actions,
            "result_state": summary.get("final_state", ""),
            "session_id": summary.get("session_id", ""),
            "prev_hash": prev_hash,
        }

        # Self-hash for quick integrity lookup
        line_without_self_hash = json.dumps(
            entry, separators=(",", ":"), sort_keys=True
        )
        entry["entry_hash"] = _sha256_text(line_without_self_hash)
        return entry


# ---------------------------------------------------------------------------
# Hash-chain verification
# ---------------------------------------------------------------------------

def verify_log_chain(log_path: Path) -> Tuple[bool, List[str]]:
    """
    Verify the hash chain of a JSONL log file.

    Reads every entry in ``log_path`` and checks that each entry's
    ``prev_hash`` matches the SHA-256 of the preceding entry's serialised
    text.  Also verifies each entry's ``entry_hash`` self-hash.

    Parameters
    ----------
    log_path:
        Path to the ``.jsonl`` file to verify.

    Returns
    -------
    tuple[bool, list[str]]
        ``(is_valid, list_of_error_messages)``
        When ``is_valid`` is ``True`` the error list is empty.
    """
    errors: List[str] = []

    if not log_path.exists():
        errors.append(f"Log file not found: {log_path}")
        return False, errors

    lines: List[str] = []
    with open(log_path, "r", encoding="utf-8") as fh:
        for raw_line in fh:
            stripped = raw_line.strip()
            if stripped:
                lines.append(stripped)

    if not lines:
        return True, []  # empty file is valid (no entries yet)

    for idx, line in enumerate(lines):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"Line {idx + 1}: JSON parse error – {exc}")
            continue

        # 1. Verify prev_hash
        if idx == 0:
            expected_prev = "GENESIS"
        else:
            expected_prev = _sha256_text(lines[idx - 1])

        actual_prev = entry.get("prev_hash", "")
        if actual_prev != expected_prev:
            errors.append(
                f"Line {idx + 1}: prev_hash mismatch "
                f"(expected {expected_prev!r}, got {actual_prev!r})"
            )

        # 2. Verify entry_hash self-hash
        stored_entry_hash = entry.pop("entry_hash", None)
        if stored_entry_hash is not None:
            recomputed_line = json.dumps(
                entry, separators=(",", ":"), sort_keys=True
            )
            recomputed_hash = _sha256_text(recomputed_line)
            if recomputed_hash != stored_entry_hash:
                errors.append(
                    f"Line {idx + 1}: entry_hash mismatch – "
                    "entry may have been tampered with"
                )

    return len(errors) == 0, errors
