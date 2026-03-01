"""
DiagAutoClinicOS - Central Configuration
"""
import os
from pathlib import Path

# === PROJECT STRUCTURE ===
PROJECT_ROOT = Path(__file__).parent.absolute()
SHARED_DIR = PROJECT_ROOT / 'shared'
AUTODIAG_DIR = PROJECT_ROOT / 'AutoDiag'
AUTOECU_DIR = PROJECT_ROOT / 'AutoECU'
AUTOKEY_DIR = PROJECT_ROOT / 'AutoKey'
DOCS_DIR = PROJECT_ROOT / 'docs'
TESTS_DIR = PROJECT_ROOT / 'tests'

# === APPLICATION DATA (Windows: %AppData%\DACOS, Linux/Mac: ~/.dacos) ===
if os.name == 'nt':
    _appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
    APP_DATA_DIR = Path(_appdata) / 'DACOS'
else:
    APP_DATA_DIR = Path(os.path.expanduser('~')) / '.dacos'

APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

# === APPLICATION INFO ===
APP_NAME = "DiagAutoClinicOS"
APP_VERSION = "3.2.0"
APP_AUTHOR = "Shaun Smit & DiagAutoClinic Team"
APP_URL = "https://diagautoclinic.co.za"
APP_LICENSE = "GPL-3.0"

# === SECURITY SETTINGS ===
SESSION_TIMEOUT = 3600  # 1 hour
MAX_LOGIN_ATTEMPTS = 3
PASSWORD_MIN_LENGTH = 12
REQUIRE_MFA = False  # Enable in production
AUDIT_LOG_RETENTION = 90  # days

# === HARDWARE SETTINGS ===
SAFE_PORT_PATTERNS = [
    r'^/dev/ttyUSB[0-9]+$',
    r'^/dev/ttyACM[0-9]+$',
    r'^COM[1-9][0-9]*$',
]

DEVICE_SCAN_TIMEOUT = 5  # seconds
MOCK_MODE_DEFAULT = False

# === LOGGING SETTINGS ===
LOG_LEVEL = "INFO"
LOG_FILE = APP_DATA_DIR / "dacos.log"
LOG_ROTATION = "1 day"
LOG_RETENTION = "30 days"

# === UI SETTINGS ===
DEFAULT_THEME = "dacos_cyber_teal"
AVAILABLE_THEMES = [
    "dacos_cyber_teal"
]

# === PERFORMANCE ===
STATS_UPDATE_INTERVAL = 3000  # milliseconds
MAX_LOG_LINES = 50
ENABLE_ANIMATIONS = True

# === DEVELOPMENT ===
DEBUG_MODE = False
ENABLE_PROFILING = False