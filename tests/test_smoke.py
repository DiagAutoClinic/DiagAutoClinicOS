#!/usr/bin/env python3
"""
tests/test_smoke.py – Basic smoke tests for DiagAutoClinicOS production readiness.

These tests are fast, headless, and validate the core non-UI modules that must
work for the app to boot to the login screen.  All tests are marked ``unit``.
"""

import hashlib
import importlib
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Ensure project root is on sys.path so shared modules import correctly
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ===========================================================================
# A) Config module
# ===========================================================================

@pytest.mark.unit
def test_config_imports():
    """config.py must be importable and expose required constants."""
    import config  # noqa: F401
    assert hasattr(config, "APP_NAME")
    assert hasattr(config, "APP_VERSION")
    assert hasattr(config, "APP_DATA_DIR")
    assert hasattr(config, "PROJECT_ROOT")


@pytest.mark.unit
def test_config_app_data_dir_exists():
    """APP_DATA_DIR must be created automatically."""
    from config import APP_DATA_DIR
    assert APP_DATA_DIR.exists(), f"APP_DATA_DIR not found: {APP_DATA_DIR}"


# ===========================================================================
# B) HWID manager
# ===========================================================================

@pytest.mark.unit
def test_hwid_manager_imports():
    """shared/hwid_manager.py must be importable."""
    from shared import hwid_manager  # noqa: F401
    assert hasattr(hwid_manager, "generate_hwid")
    assert hasattr(hwid_manager, "check_hwid")
    assert hasattr(hwid_manager, "store_hwid")
    assert hasattr(hwid_manager, "load_stored_hwid")


@pytest.mark.unit
def test_hwid_generate_returns_sha256():
    """generate_hwid() must return a 64-character hex string (SHA-256)."""
    from shared.hwid_manager import generate_hwid
    hwid = generate_hwid()
    assert isinstance(hwid, str), "HWID must be a string"
    assert len(hwid) == 64, f"HWID must be 64 hex chars, got {len(hwid)}"
    # Ensure it's valid hex
    int(hwid, 16)


@pytest.mark.unit
def test_hwid_is_stable():
    """generate_hwid() must return the same value on consecutive calls."""
    from shared.hwid_manager import generate_hwid
    assert generate_hwid() == generate_hwid()


@pytest.mark.unit
def test_hwid_store_and_load(tmp_path):
    """store_hwid / load_stored_hwid round-trip must work correctly."""
    from shared import hwid_manager

    test_hash = hashlib.sha256(b"test").hexdigest()

    # Patch the hwid file path to use a temp location
    fake_path = tmp_path / "hwid.json"
    with patch.object(hwid_manager, "_hwid_file", return_value=fake_path):
        # Reset cached value so _hwid_file() is called fresh
        hwid_manager._HWID_FILE = None

        hwid_manager.store_hwid(test_hash)
        loaded = hwid_manager.load_stored_hwid()

    assert loaded == test_hash


@pytest.mark.unit
def test_hwid_check_first_run(tmp_path):
    """check_hwid() must report first-run=True when no HWID is stored."""
    from shared import hwid_manager

    fake_path = tmp_path / "hwid.json"
    with patch.object(hwid_manager, "_hwid_file", return_value=fake_path):
        hwid_manager._HWID_FILE = None
        current, is_first_run, hwid_changed = hwid_manager.check_hwid()

    assert is_first_run is True
    assert hwid_changed is False
    assert len(current) == 64


@pytest.mark.unit
def test_hwid_check_no_change(tmp_path):
    """check_hwid() must report hwid_changed=False when HWID matches stored."""
    from shared import hwid_manager

    fake_path = tmp_path / "hwid.json"
    with patch.object(hwid_manager, "_hwid_file", return_value=fake_path):
        hwid_manager._HWID_FILE = None
        # First call stores it
        hwid_manager.check_hwid()
        # Second call should find a match
        _current, is_first_run, hwid_changed = hwid_manager.check_hwid()

    assert is_first_run is False
    assert hwid_changed is False


@pytest.mark.unit
def test_hwid_check_change_detected(tmp_path):
    """check_hwid() must report hwid_changed=True when stored HWID differs."""
    from shared import hwid_manager

    old_hash = hashlib.sha256(b"old_machine").hexdigest()
    fake_path = tmp_path / "hwid.json"

    # Pre-store a fake (different) HWID
    with open(fake_path, "w") as f:
        json.dump({"hwid_hash": old_hash}, f)

    with patch.object(hwid_manager, "_hwid_file", return_value=fake_path):
        hwid_manager._HWID_FILE = None
        _current, is_first_run, hwid_changed = hwid_manager.check_hwid()

    # The generated HWID is very unlikely to equal old_hash
    assert is_first_run is False
    assert hwid_changed is True


@pytest.mark.unit
def test_hwid_status_message_on_change():
    """get_hwid_status_message returns a warning string when hwid_changed=True."""
    from shared.hwid_manager import get_hwid_status_message
    msg = get_hwid_status_message(is_first_run=False, hwid_changed=True)
    assert msg is not None
    assert len(msg) > 10


@pytest.mark.unit
def test_hwid_status_message_first_run_silent():
    """get_hwid_status_message returns None on first run (no nagging)."""
    from shared.hwid_manager import get_hwid_status_message
    msg = get_hwid_status_message(is_first_run=True, hwid_changed=False)
    assert msg is None


# ===========================================================================
# C) User database (SQLite)
# ===========================================================================

@pytest.mark.unit
def test_user_database_sqlite_imports():
    """shared/user_database_sqlite.py must be importable."""
    from shared import user_database_sqlite  # noqa: F401
    assert hasattr(user_database_sqlite, "UserDatabase")


@pytest.mark.unit
def test_user_database_sqlite_init(tmp_path):
    """UserDatabase must initialise without errors against a temp DB file."""
    from shared.user_database_sqlite import UserDatabase
    db_path = str(tmp_path / "test_users.db")
    db = UserDatabase(db_path=db_path)
    assert db is not None


@pytest.mark.unit
def test_user_database_default_superuser(tmp_path):
    """UserDatabase must create the default superuser on first init."""
    from shared.user_database_sqlite import UserDatabase
    db_path = str(tmp_path / "test_users.db")
    db = UserDatabase(db_path=db_path)
    assert db.user_exists("superuser")


@pytest.mark.unit
def test_user_database_authenticate_superuser(tmp_path):
    """Default superuser must authenticate with the known default password."""
    from shared.user_database_sqlite import UserDatabase
    db_path = str(tmp_path / "test_users.db")
    db = UserDatabase(db_path=db_path)
    success, message, user_info = db.authenticate_user("superuser", "DiagAutoClinicOS_Admin_123!")
    assert success is True, f"Superuser auth failed: {message}"
    assert user_info.get("username") == "superuser"


@pytest.mark.unit
def test_user_database_bad_password(tmp_path):
    """Authentication must fail for wrong password."""
    from shared.user_database_sqlite import UserDatabase
    db_path = str(tmp_path / "test_users.db")
    db = UserDatabase(db_path=db_path)
    success, _message, _info = db.authenticate_user("superuser", "wrongpassword")
    assert success is False


@pytest.mark.unit
def test_user_database_create_user(tmp_path):
    """UserDatabase.create_user must work and allow authentication."""
    from shared.user_database_sqlite import UserDatabase, UserTier
    db_path = str(tmp_path / "test_users.db")
    db = UserDatabase(db_path=db_path)
    created = db.create_user(
        username="testtech",
        password="SecurePass1234!",
        full_name="Test Technician",
        tier=UserTier.STANDARD,
    )
    assert created is True
    success, _msg, info = db.authenticate_user("testtech", "SecurePass1234!")
    assert success is True
    assert info.get("username") == "testtech"


# ===========================================================================
# D) Launcher module – import smoke test (no display required)
# ===========================================================================

@pytest.mark.unit
def test_launcher_imports_without_display():
    """
    launcher.py top-level code must not raise when imported without a display.
    Skipped when tkinter is not available (e.g. headless CI without tk).
    """
    tkinter = pytest.importorskip("tkinter", reason="tkinter not available in this environment")

    # Remove cached module if present
    for mod in list(sys.modules.keys()):
        if mod == "launcher":
            del sys.modules[mod]

    with patch("tkinter.Tk", MagicMock()):
        spec = importlib.util.spec_from_file_location(
            "launcher", str(PROJECT_ROOT / "launcher.py")
        )
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except SystemExit:
            pass  # Acceptable – some code paths call sys.exit on headless setups

    # Verify key names are defined in the module
    assert hasattr(module, "DiagLauncher")
    assert hasattr(module, "LoginDialog")
    assert hasattr(module, "show_login")


# ===========================================================================
# E) config – simulation / mock mode flag
# ===========================================================================

@pytest.mark.unit
def test_mock_mode_default_is_false():
    """MOCK_MODE_DEFAULT must be False in production configuration."""
    from config import MOCK_MODE_DEFAULT
    assert MOCK_MODE_DEFAULT is False, (
        "MOCK_MODE_DEFAULT must be False in production to prevent fake data"
    )
