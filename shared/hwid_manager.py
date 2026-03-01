#!/usr/bin/env python3
"""
DiagAutoClinicOS - Hardware ID (HWID) Manager
Generates a stable, anonymous machine fingerprint for installation tracking.

Windows: combines Registry MachineGuid + SMBIOS UUID (via WMI/wmic), then SHA-256.
Linux/Mac: falls back to /etc/machine-id or hostname-based hash.

Enforcement is SOFT: an HWID change emits a warning and is logged; it does NOT
lock the user out.  An admin must explicitly rebind the installation.
"""

import hashlib
import json
import logging
import os
import platform
import subprocess
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Resolve app-data directory (import lazily to avoid circular imports at module level)
def _get_app_data_dir() -> Path:
    try:
        from config import APP_DATA_DIR  # type: ignore
        return APP_DATA_DIR
    except ImportError:
        pass
    try:
        import sys
        root = Path(__file__).resolve().parent.parent
        sys.path.insert(0, str(root))
        from config import APP_DATA_DIR  # type: ignore
        return APP_DATA_DIR
    except ImportError:
        fallback = Path(os.path.expanduser("~")) / ".dacos"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


_HWID_FILE = None  # resolved lazily


def _hwid_file() -> Path:
    global _HWID_FILE
    if _HWID_FILE is None:
        _HWID_FILE = _get_app_data_dir() / "hwid.json"
    return _HWID_FILE


# ---------------------------------------------------------------------------
# Low-level component readers
# ---------------------------------------------------------------------------

def _read_windows_machine_guid() -> Optional[str]:
    """Read MachineGuid from HKLM\\SOFTWARE\\Microsoft\\Cryptography."""
    try:
        import winreg  # type: ignore
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography",
        )
        value, _ = winreg.QueryValueEx(key, "MachineGuid")
        winreg.CloseKey(key)
        return str(value).strip()
    except Exception:
        return None


def _read_windows_smbios_uuid() -> Optional[str]:
    """Read SMBIOS UUID via wmic (Win32_ComputerSystemProduct)."""
    try:
        result = subprocess.run(
            ["wmic", "csproduct", "get", "UUID"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
        # Output is: ["UUID", "<value>"] - skip header line
        for line in lines:
            if line.upper() != "UUID" and len(line) > 8:
                return line
    except Exception:
        pass
    return None


def _read_linux_machine_id() -> Optional[str]:
    """Read /etc/machine-id or /var/lib/dbus/machine-id on Linux."""
    for path in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
        try:
            with open(path) as f:
                val = f.read().strip()
                if val:
                    return val
        except OSError:
            continue
    return None


def _read_macos_platform_uuid() -> Optional[str]:
    """Read IOPlatformUUID on macOS via ioreg."""
    try:
        result = subprocess.run(
            ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        for line in result.stdout.splitlines():
            if "IOPlatformUUID" in line:
                parts = line.split('"')
                if len(parts) >= 4:
                    return parts[-2]
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# HWID generation
# ---------------------------------------------------------------------------

def generate_hwid() -> str:
    """
    Generate a stable SHA-256 HWID for the current machine.

    The raw components used depend on the OS but are never stored; only the
    final hash is persisted.
    """
    system = platform.system()
    components: list[str] = []

    if system == "Windows":
        guid = _read_windows_machine_guid()
        if guid:
            components.append(f"MachineGuid:{guid}")
        uuid = _read_windows_smbios_uuid()
        if uuid:
            components.append(f"SMBIOS:{uuid}")

    elif system == "Linux":
        mid = _read_linux_machine_id()
        if mid:
            components.append(f"machine-id:{mid}")

    elif system == "Darwin":
        puuid = _read_macos_platform_uuid()
        if puuid:
            components.append(f"IOPlatformUUID:{puuid}")

    if not components:
        # Final fallback: hostname (not stable across renames, but better than nothing)
        import socket
        hostname = socket.gethostname()
        logger.warning(
            "No stable machine identifier found; falling back to hostname '%s'. "
            "HWID may change if the hostname is modified.",
            hostname,
        )
        components.append(f"hostname:{hostname}")

    raw = "|".join(components)
    hwid_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    logger.debug("HWID generated (components: %d)", len(components))
    return hwid_hash


# ---------------------------------------------------------------------------
# Persistence & enforcement
# ---------------------------------------------------------------------------

def load_stored_hwid() -> Optional[str]:
    """Return the previously stored HWID hash, or None if not yet recorded."""
    path = _hwid_file()
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("hwid_hash")
    except Exception as e:
        logger.warning("Failed to read stored HWID: %s", e)
        return None


def store_hwid(hwid_hash: str) -> None:
    """Persist the HWID hash to the app-data directory."""
    path = _hwid_file()
    try:
        existing: dict = {}
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                pass
        existing["hwid_hash"] = hwid_hash
        with open(path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)
        logger.debug("HWID stored to %s", path)
    except Exception as e:
        logger.error("Failed to store HWID: %s", e)


def check_hwid() -> Tuple[str, bool, bool]:
    """
    Generate the current HWID, compare with stored, and persist if new.

    Returns:
        (hwid_hash, is_first_run, hwid_changed)
        - hwid_hash   : current machine HWID hash
        - is_first_run: True when no HWID was previously stored
        - hwid_changed: True when the current HWID differs from the stored one
    """
    current = generate_hwid()
    stored = load_stored_hwid()

    if stored is None:
        # First run – record it
        store_hwid(current)
        logger.info("HWID recorded for the first time (first-run installation)")
        return current, True, False

    if current != stored:
        logger.warning(
            "HWID mismatch detected – hardware may have changed. "
            "Stored: %s… Current: %s…",
            stored[:12],
            current[:12],
        )
        # Soft enforcement: update the stored hash so repeated startups don't
        # spam warnings, but the change is logged for audit purposes.
        store_hwid(current)
        return current, False, True

    logger.debug("HWID matches stored value – OK")
    return current, False, False


def get_hwid_status_message(is_first_run: bool, hwid_changed: bool) -> Optional[str]:
    """
    Return a human-readable message if action is required, else None.
    Used by the launcher to display warnings.
    """
    if is_first_run:
        return None  # Silent on first run
    if hwid_changed:
        return (
            "⚠️  Hardware change detected.\n\n"
            "This installation's hardware fingerprint has changed.\n"
            "The change has been logged.  If this was unexpected, contact your administrator."
        )
    return None
