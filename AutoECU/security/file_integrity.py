"""
AutoECU/security/file_integrity.py
────────────────────────────────────
Firmware / calibration file integrity checking.

All firmware or calibration files **must** pass this module's checks
before being passed to a flash session.  Unknown or modified binaries are
blocked by default; an explicit override (with mandatory audit reason) is
required to bypass the block.

Features
--------
* SHA-256 checksum verification.
* Optional digital-signature verification (interface is present; signature
  verification can be backed by a real implementation without changing the
  public API).
* Allowlist of known-good file hashes (managed at runtime).
* Explicit, auditable override for files not in the allowlist.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Optional


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class FileIntegrityError(Exception):
    """Raised when a file fails integrity verification."""


class UnknownFileError(FileIntegrityError):
    """
    Raised when a file's hash is not in the allowlist and no explicit
    override has been granted.
    """


class HashMismatchError(FileIntegrityError):
    """Raised when the file's computed hash does not match the expected hash."""


# ---------------------------------------------------------------------------
# Signature verification stub
# ---------------------------------------------------------------------------

def _stub_verify_signature(
    file_bytes: bytes,
    signature: bytes,
    public_key_pem: bytes,
) -> bool:
    """
    Signature verification stub.

    This function exists as an explicit design hook.  A production
    implementation should replace the body with real verification using
    a cryptographic library (e.g. ``cryptography`` or ``OpenSSL``).

    Returns
    -------
    bool
        Always returns ``False`` in the stub implementation so that callers
        are forced to either supply a real verifier or explicitly opt-out of
        signature checking.
    """
    # TODO: Replace stub with real Ed25519 / RSA-PSS verification.
    return False  # pragma: no cover – stub, tested via the public API


# ---------------------------------------------------------------------------
# FileIntegrityChecker
# ---------------------------------------------------------------------------

class FileIntegrityChecker:
    """
    Verifies firmware / calibration files before flashing.

    Parameters
    ----------
    allowlist:
        Optional mapping of ``sha256_hex → description`` for pre-approved
        files.  Files whose hashes are in the allowlist will pass the
        unknown-file check automatically.
    require_allowlist:
        When ``True`` (default) a file *must* be in the allowlist or an
        explicit override must be granted.  Set to ``False`` only in
        controlled development / test environments.
    signature_verifier:
        Optional callable with the same signature as
        :func:`_stub_verify_signature`.  When ``None`` the stub is used and
        signature verification is effectively disabled.
    """

    def __init__(
        self,
        allowlist: Optional[Dict[str, str]] = None,
        require_allowlist: bool = True,
        signature_verifier=None,
    ) -> None:
        self._allowlist: Dict[str, str] = dict(allowlist or {})
        self._require_allowlist: bool = require_allowlist
        self._signature_verifier = signature_verifier or _stub_verify_signature

        # Audit log of every override granted in this checker instance.
        self._override_log: list = []

    # ------------------------------------------------------------------
    # Allowlist management
    # ------------------------------------------------------------------

    def add_to_allowlist(self, sha256_hex: str, description: str = "") -> None:
        """
        Add a known-good hash to the allowlist.

        Parameters
        ----------
        sha256_hex:
            64-character lower-case hex string of the SHA-256 hash.
        description:
            Human-readable label (e.g. firmware version string).
        """
        sha256_hex = sha256_hex.lower()
        if len(sha256_hex) != 64:
            raise ValueError(
                f"Expected a 64-char hex string; got {len(sha256_hex)} chars"
            )
        self._allowlist[sha256_hex] = description

    def remove_from_allowlist(self, sha256_hex: str) -> None:
        """Remove a hash from the allowlist (no-op if not present)."""
        self._allowlist.pop(sha256_hex.lower(), None)

    @property
    def allowlist(self) -> Dict[str, str]:
        """Read-only view of the current allowlist."""
        return dict(self._allowlist)

    # ------------------------------------------------------------------
    # Core verification
    # ------------------------------------------------------------------

    @staticmethod
    def compute_sha256(data: bytes) -> str:
        """
        Compute the SHA-256 hash of ``data``.

        Parameters
        ----------
        data:
            Raw bytes to hash.

        Returns
        -------
        str
            64-character lower-case hex digest.
        """
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def compute_sha256_from_path(path: Path) -> str:
        """
        Compute the SHA-256 hash of a file on disk.

        Parameters
        ----------
        path:
            Path to the file.

        Returns
        -------
        str
            64-character lower-case hex digest.
        """
        sha = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                sha.update(chunk)
        return sha.hexdigest()

    def verify(
        self,
        data: bytes,
        expected_hash: Optional[str] = None,
        override_reason: Optional[str] = None,
        signature: Optional[bytes] = None,
        public_key_pem: Optional[bytes] = None,
    ) -> str:
        """
        Verify ``data`` against the allowlist (and optionally a hash /
        digital signature).

        Parameters
        ----------
        data:
            Raw file bytes to verify.
        expected_hash:
            When supplied, the computed hash must match this value.
        override_reason:
            When the file is not in the allowlist, the caller **must**
            supply a non-empty reason string to unlock it.  This reason
            is recorded in the override audit log.
        signature:
            Optional DER/raw signature bytes.
        public_key_pem:
            PEM-encoded public key for signature verification.  Required
            when ``signature`` is provided.

        Returns
        -------
        str
            The computed SHA-256 hex digest (so callers can store it in the
            audit record without re-hashing).

        Raises
        ------
        HashMismatchError
            When ``expected_hash`` is supplied and doesn't match.
        UnknownFileError
            When the file is not in the allowlist and no valid override is
            provided.
        FileIntegrityError
            On signature verification failure (when signature is provided).
        """
        computed = self.compute_sha256(data)

        # 1. Hash match check
        if expected_hash is not None:
            if computed != expected_hash.lower():
                raise HashMismatchError(
                    f"Hash mismatch: expected {expected_hash!r}, "
                    f"computed {computed!r}"
                )

        # 2. Allowlist check
        if self._require_allowlist and computed not in self._allowlist:
            if not override_reason or not override_reason.strip():
                raise UnknownFileError(
                    f"File hash {computed!r} is not in the allowlist. "
                    "Supply a non-empty override_reason to explicitly allow "
                    "this file."
                )
            # Record the override for audit purposes
            import time
            self._override_log.append(
                {
                    "timestamp": time.time(),
                    "hash": computed,
                    "reason": override_reason,
                }
            )

        # 3. Optional signature verification
        if signature is not None:
            if public_key_pem is None:
                raise FileIntegrityError(
                    "public_key_pem is required when signature is provided"
                )
            sig_ok = self._signature_verifier(data, signature, public_key_pem)
            if not sig_ok:
                raise FileIntegrityError(
                    "Digital signature verification failed"
                )

        return computed

    def verify_from_path(
        self,
        path: Path,
        expected_hash: Optional[str] = None,
        override_reason: Optional[str] = None,
        signature: Optional[bytes] = None,
        public_key_pem: Optional[bytes] = None,
    ) -> str:
        """
        Convenience wrapper – read a file from disk and call :meth:`verify`.

        Parameters
        ----------
        path:
            Path to the firmware or calibration file.

        All other parameters are forwarded to :meth:`verify`.

        Returns
        -------
        str
            SHA-256 hex digest of the file.
        """
        with open(path, "rb") as fh:
            data = fh.read()
        return self.verify(
            data,
            expected_hash=expected_hash,
            override_reason=override_reason,
            signature=signature,
            public_key_pem=public_key_pem,
        )

    # ------------------------------------------------------------------
    # Override log
    # ------------------------------------------------------------------

    @property
    def override_log(self) -> list:
        """Read-only snapshot of all overrides granted in this instance."""
        return list(self._override_log)

    # ------------------------------------------------------------------
    # Allowlist persistence helpers
    # ------------------------------------------------------------------

    def load_allowlist_from_json(self, path: Path) -> None:
        """
        Merge a JSON file into the current allowlist.

        The file must be a JSON object mapping sha256_hex → description.

        Parameters
        ----------
        path:
            Path to the JSON allowlist file.
        """
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            raise ValueError("Allowlist JSON must be a top-level object")
        for key, value in data.items():
            self.add_to_allowlist(key, str(value))

    def save_allowlist_to_json(self, path: Path) -> None:
        """
        Persist the current allowlist to a JSON file.

        Parameters
        ----------
        path:
            Destination path (will be created or overwritten).
        """
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self._allowlist, fh, indent=2, sort_keys=True)
