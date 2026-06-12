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
# B) User database (SQLite)
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
