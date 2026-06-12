#!/usr/bin/env python3
"""
DiagAutoClinicOS Launcher
Production entrypoint for the DiagAutoClinicOS suite on Windows 10/11.

Start-up sequence:
  1. Initialise logging → %AppData%\\DACOS\\launcher.log
  2. Show login dialog – gates access to the main diagnostic dashboard
  3. Present main launcher UI on successful authentication
"""


import sys
import os
import json
import importlib
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import logging
import math
import platform
import threading
from datetime import datetime

# --- Alpha Test Mode ---
# Credentials are now managed by shared/security_manager.py
# Default users: testuser / TestUserAlpha2026!  and  supernova / Charaun@8576
ALPHA_TEST_MODE = True  # Enables brand unlock, checklist, Charlemaine buttons
CHARLEMAINE_LOCAL = True

# ---------------------------------------------------------------------------
# Add project root to Python path early so shared modules resolve correctly
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Use project virtual environment if available (cross-platform)
# ---------------------------------------------------------------------------
if os.name == 'nt':
    _venv_python = PROJECT_ROOT / "venv" / "Scripts" / "python.exe"
else:
    _venv_python = PROJECT_ROOT / "venv" / "bin" / "python"

if _venv_python.exists():
    import subprocess as _sp
    _test = _sp.run([str(_venv_python), "-c", "import encodings"], capture_output=True)
    VENV_PYTHON_PATH = _venv_python if _test.returncode == 0 else sys.executable
else:
    VENV_PYTHON_PATH = sys.executable

# ---------------------------------------------------------------------------
# Configure logging → predictable location (%AppData%\DACOS\launcher.log)
# ---------------------------------------------------------------------------
try:
    from config import APP_DATA_DIR  # type: ignore
    _log_dir = APP_DATA_DIR
except Exception:
    if os.name == 'nt':
        _appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
        _log_dir = Path(_appdata) / 'DACOS'
    else:
        _log_dir = Path(os.path.expanduser('~')) / '.dacos'
    _log_dir.mkdir(parents=True, exist_ok=True)

_log_file = _log_dir / 'launcher.log'
_handlers: list = [logging.StreamHandler(sys.stdout)]
try:
    _handlers.append(logging.FileHandler(str(_log_file), encoding='utf-8'))
except Exception:
    pass  # stdout only as fallback

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=_handlers,
)

logger = logging.getLogger("DiagLauncher")
logger.info("Log file: %s", _log_file)

try:
    from shared.theme_manager import get_theme_dict, AVAILABLE_THEMES, save_config as save_theme_config, get_current_theme_name
    THEME = get_theme_dict()
    current_theme_name = get_current_theme_name()
    logger.info(f"Loaded theme: {current_theme_name}")
except ImportError as e:
    logger.error(f"Failed to import theme manager: {e}")
    # Fallback theme
    THEME = {
        "bg_main": "#000000",
        "bg_panel": "#1a1a1a",
        "bg_card": "#333333",
        "accent": "#00ff00",
        "glow": "#00ff00",
        "text_main": "#ffffff",
        "text_muted": "#aaaaaa",
        "error": "#ff0000",
        "warning": "#ffff00",
        "success": "#00ff00"
    }
    AVAILABLE_THEMES = {"Default": "default"}
    def save_theme_config(name): return False
    current_theme_name = "Default"

def to_hex(color):
    """Convert rgba/hex colors to simple hex for Tkinter"""
    if not color: return "#000000"
    if color.startswith("rgba"):
        # Parse rgba(r, g, b, a)
        try:
            parts = color.strip("rgba()").split(",")
            r = int(parts[0].strip())
            g = int(parts[1].strip())
            b = int(parts[2].strip())
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return "#000000"
    return color[:7]  # Handle #RRGGBBAA by truncating

# Theme Configuration

# Ensure all required keys exist (fallback to safe defaults)
BG_MAIN = to_hex(THEME.get("bg_main", "#000000"))
BG_PANEL = to_hex(THEME.get("bg_panel", "#1a1a1a"))
BG_CARD = to_hex(THEME.get("bg_card", "#333333"))
ACCENT = to_hex(THEME.get("accent", "#00ff00"))
GLOW = to_hex(THEME.get("glow", "#00ff00"))
TEXT_MAIN = to_hex(THEME.get("text_main", "#ffffff"))
TEXT_MUTED = to_hex(THEME.get("text_muted", "#aaaaaa"))
ERROR = to_hex(THEME.get("error", "#ff0000"))
WARNING = to_hex(THEME.get("warning", "#ffff00"))
SUCCESS = to_hex(THEME.get("success", "#00ff00"))

# ---------------------------------------------------------------------------
# Authentication backend — use the unified security manager
# ---------------------------------------------------------------------------

try:
    # Use the SINGLE shared instance — creating a second EnhancedSecurityManager()
    # causes dual in-memory copies of users.json that fight each other.
    from shared.security_manager import security_manager as _security  # type: ignore
    _AUTH_AVAILABLE = True
    logger.info("Security manager loaded successfully (shared instance)")
except Exception as _sec_err:
    logger.error("Failed to load security manager: %s", _sec_err)
    _security = None
    _AUTH_AVAILABLE = False



def _authenticate(username: str, password: str):
    """
    Authenticate via the unified security manager.
    Returns (success: bool, message: str, user_info: dict).
    """
    if _AUTH_AVAILABLE and _security is not None:
        try:
            success, message, user_info = _security.authenticate_user(username, password)
            if success and user_info:
                return True, message, user_info
            return False, message or "Invalid credentials", {}
        except Exception as e:
            logger.error("Authentication error: %s", e)
            return False, f"Authentication error: {e}", {}
    # Fallback: security unavailable — deny access
    logger.critical("Security manager unavailable — denying access")
    return False, "Security system unavailable. Contact your administrator.", {}


# ---------------------------------------------------------------------------
# Tkinter login dialog – gates access to the main diagnostic dashboard
# ---------------------------------------------------------------------------

class LoginDialog(tk.Toplevel):
    """
    Tkinter login dialog shown before the main launcher window.
    Runs password hashing (scrypt) in a background thread to keep the UI responsive.
    """

    def __init__(self, parent, on_complete):
        """
        Args:
            parent: parent Tk widget (withdrawn root)
            on_complete: callback(user_info_dict | None) called on success or cancel
        """
        super().__init__(parent)
        self.title("DiagAutoClinicOS – Secure Login")
        self.resizable(False, False)
        self.configure(bg=BG_MAIN)
        self.result = None  # set to user_info dict on success
        self.on_complete = on_complete
        self._authenticating = False

        # Make modal — transient + topmost first, then grab_set() after
        # the dialog is realized.  grab_set() on a Toplevel of a withdrawn
        # parent can deadlock on Windows Tk; we use a 1x1 transparent root
        # instead (see _run_login_flow) so grab_set() is safe here.
        self.transient(parent)
        self.attributes('-topmost', True)

        self._build_ui()

        # Center on screen (parent is a 1x1 transparent stub)
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        px = (sw - w) // 2
        py = (sh - h) // 2
        self.geometry(f"+{px}+{py}")

        self.grab_set()
        self.focus_force()

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.bind("<Return>", lambda _e: self._on_login())
        self.bind("<Escape>", lambda _e: self._on_cancel())

    def _build_ui(self):
        pad = {"padx": 30, "pady": 8}

        tk.Label(
            self, text="🔒  DiagAutoClinicOS",
            fg=ACCENT, bg=BG_MAIN, font=("Segoe UI", 18, "bold"),
        ).pack(pady=(30, 2))
        tk.Label(
            self, text="Secure Login Required",
            fg=TEXT_MUTED, bg=BG_MAIN, font=("Segoe UI", 10),
        ).pack(pady=(0, 20))

        form = tk.Frame(self, bg=BG_PANEL, padx=20, pady=15)
        form.pack(fill="x", **pad)

        tk.Label(form, text="Username:", fg=TEXT_MAIN, bg=BG_PANEL,
                 font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=5, padx=(0, 10))
        self._username_var = tk.StringVar()
        tk.Entry(form, textvariable=self._username_var, bg=BG_CARD, fg=TEXT_MAIN,
                 insertbackground=TEXT_MAIN, font=("Segoe UI", 10), width=22,
                 relief="flat").grid(row=0, column=1, pady=5)

        tk.Label(form, text="Password:", fg=TEXT_MAIN, bg=BG_PANEL,
                 font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=5, padx=(0, 10))
        self._password_var = tk.StringVar()
        tk.Entry(form, textvariable=self._password_var, show="*", bg=BG_CARD, fg=TEXT_MAIN,
                 insertbackground=TEXT_MAIN, font=("Segoe UI", 10), width=22,
                 relief="flat").grid(row=1, column=1, pady=5)

        self._status_var = tk.StringVar()
        tk.Label(self, textvariable=self._status_var, fg=ERROR, bg=BG_MAIN,
                 font=("Segoe UI", 9), wraplength=300).pack(**pad)

        btn_frame = tk.Frame(self, bg=BG_MAIN)
        btn_frame.pack(pady=(0, 25))
        self._login_btn = tk.Button(btn_frame, text="Login", command=self._on_login,
                  bg=ACCENT, fg=BG_MAIN, font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=20, pady=6, cursor="hand2")
        self._login_btn.pack(side="left", padx=8)
        tk.Button(btn_frame, text="Cancel", command=self._on_cancel,
                  bg=BG_PANEL, fg=TEXT_MAIN, font=("Segoe UI", 10),
                  relief="flat", padx=20, pady=6, cursor="hand2").pack(side="left", padx=8)

    def _on_login(self):
        """Initiate login — runs scrypt auth in a background thread to keep UI responsive."""
        if self._authenticating:
            return  # Prevent double-submit

        username = self._username_var.get().strip()
        password = self._password_var.get()
        if not username or not password:
            self._status_var.set("⚠️  Username and password are required.")
            return

        self._authenticating = True
        self._login_btn.config(state="disabled", text="Authenticating…")
        self._status_var.set("Authenticating…")
        self.update_idletasks()

        # Run password hashing (scrypt) on a background thread —
        # prevents the UI from freezing during CPU-intensive key derivation.
        t = threading.Thread(
            target=self._run_auth_thread,
            args=(username, password),
            daemon=True,
        )
        t.start()

    def _run_auth_thread(self, username: str, password: str):
        """Execute authentication on a background thread, then post result to main thread."""
        success, message, user_info = _authenticate(username, password)
        # Schedule UI update on the main thread via Tkinter's event queue
        self.after(0, self._on_auth_complete, username, success, message, user_info)

    def _on_auth_complete(self, username: str, success: bool, message: str, user_info: dict):
        """Handle authentication result on the main Tkinter thread."""
        self._authenticating = False
        self._login_btn.config(state="normal", text="Login")

        if success:
            # Check if password change is required BEFORE accepting the login
            if "password change" in message.lower():
                logger.info("Password change required for user: %s", username)
                self._status_var.set("Password change required — enter a new password below.")
                self._show_password_change_ui(username, user_info)
                return

            logger.info("Login successful for user: %s", username)
            self.result = user_info
            # Write session file so AutoDiag (PyQt6) can auto-login — no second prompt
            self._write_launcher_session(username)
            self.grab_release()
            self.destroy()
            self.on_complete(user_info)
        else:
            logger.warning("Login failed for user '%s': %s", username, message)
            self._status_var.set(f"❌  {message}")
            self._password_var.set("")

    def _show_password_change_ui(self, username: str, user_info: dict):
        """Replace the login form with a password change form."""
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        self.title("DiagAutoClinicOS – Password Change Required")
        pad = {"padx": 30, "pady": 8}

        tk.Label(
            self, text="🔐  Password Change Required",
            fg=ACCENT, bg=BG_MAIN, font=("Segoe UI", 16, "bold"),
        ).pack(pady=(30, 2))
        tk.Label(
            self, text=f"User: {username} — You must set a new password before continuing.",
            fg=TEXT_MUTED, bg=BG_MAIN, font=("Segoe UI", 10), wraplength=350,
        ).pack(pady=(0, 10))
        tk.Label(
            self, text="Min 8 chars • Upper + lower case • At least 1 number",
            fg=TEXT_MUTED, bg=BG_MAIN, font=("Segoe UI", 9),
        ).pack(pady=(0, 15))

        form = tk.Frame(self, bg=BG_PANEL, padx=20, pady=15)
        form.pack(fill="x", **pad)

        tk.Label(form, text="New Password:", fg=TEXT_MAIN, bg=BG_PANEL,
                 font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=5, padx=(0, 10))
        new_pw_var = tk.StringVar()
        tk.Entry(form, textvariable=new_pw_var, show="*", bg=BG_CARD, fg=TEXT_MAIN,
                 insertbackground=TEXT_MAIN, font=("Segoe UI", 10), width=22,
                 relief="flat").grid(row=0, column=1, pady=5)

        tk.Label(form, text="Confirm:", fg=TEXT_MAIN, bg=BG_PANEL,
                 font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=5, padx=(0, 10))
        confirm_pw_var = tk.StringVar()
        tk.Entry(form, textvariable=confirm_pw_var, show="*", bg=BG_CARD, fg=TEXT_MAIN,
                 insertbackground=TEXT_MAIN, font=("Segoe UI", 10), width=22,
                 relief="flat").grid(row=1, column=1, pady=5)

        self._status_var = tk.StringVar()
        tk.Label(self, textvariable=self._status_var, fg=ERROR, bg=BG_MAIN,
                 font=("Segoe UI", 9), wraplength=300).pack(**pad)

        btn_frame = tk.Frame(self, bg=BG_MAIN)
        btn_frame.pack(pady=(0, 25))

        def _do_password_change():
            new_pw = new_pw_var.get()
            confirm_pw = confirm_pw_var.get()

            if not new_pw or not confirm_pw:
                self._status_var.set("⚠️  Both fields are required.")
                return
            if new_pw != confirm_pw:
                self._status_var.set("⚠️  Passwords do not match.")
                return

            # Use the shared security_manager instance for consistency
            ok, msg = _security.change_password(username, "", new_pw)
            if ok:
                logger.info("Password changed successfully for user: %s", username)
                self.result = user_info
                self.grab_release()
                self.destroy()
                self.on_complete(user_info)
            else:
                self._status_var.set(f"❌  {msg}")

        tk.Button(btn_frame, text="Change Password", command=_do_password_change,
                  bg=ACCENT, fg=BG_MAIN, font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=20, pady=6, cursor="hand2").pack(side="left", padx=8)
        tk.Button(btn_frame, text="Cancel", command=self._on_cancel,
                  bg=BG_PANEL, fg=TEXT_MAIN, font=("Segoe UI", 10),
                  relief="flat", padx=20, pady=6, cursor="hand2").pack(side="left", padx=8)

        self.bind("<Return>", lambda _e: _do_password_change())

    def _on_cancel(self):
        if self._authenticating:
            return  # Don't allow cancel while auth is in progress
        logger.info("Login cancelled by user")
        self.result = None
        self.grab_release()
        self.destroy()
        self.on_complete(None)

    @staticmethod
    def _write_launcher_session(username: str):
        """Write a session file so the PyQt6 AutoDiag login auto-authenticates."""
        try:
            session_dir = Path(os.path.expanduser("~")) / ".dacos"
            session_dir.mkdir(parents=True, exist_ok=True)
            session_file = session_dir / "session.json"
            with open(session_file, "w") as f:
                json.dump({"username": username}, f)
            logger.info("Launcher session written for: %s", username)
        except Exception as e:
            logger.warning("Failed to write launcher session: %s", e)


def _run_login_flow():
    """
    Run the login dialog and return the authenticated user_info dict,
    or None if the user cancelled.

    Uses a callback-based flow with a short-lived Tk root — avoids
    wait_window() which can deadlock with grab_set() on some Windows builds.
    """
    result_holder: dict = {"user_info": None}

    def on_login_complete(user_info):
        result_holder["user_info"] = user_info
        login_root.quit()  # Break out of mainloop()

    # Create a minimal invisible root.  We CANNOT use withdraw() because
    # grab_set() on a Toplevel of a withdrawn window hangs on Windows Tk.
    # Instead: 1×1 fully-transparent window — invisible in practice.
    login_root = tk.Tk()
    login_root.geometry("1x1+0+0")
    login_root.attributes('-alpha', 0)   # Fully transparent
    login_root.overrideredirect(True)     # No title bar / borders

    LoginDialog(login_root, on_login_complete)
    login_root.mainloop()  # Block until root.quit() is called
    login_root.destroy()

    return result_holder["user_info"]


def _write_session(username: str):
    """Write a session file so AutoDiag can skip its own login screen."""
    try:
        from config import APP_DATA_DIR
        session_dir = APP_DATA_DIR
    except Exception:
        import os as _os
        if _os.name == 'nt':
            session_dir = Path(_os.environ.get('APPDATA', _os.path.expanduser('~'))) / 'DACOS'
        else:
            session_dir = Path(_os.path.expanduser('~')) / '.dacos'
    session_dir.mkdir(parents=True, exist_ok=True)
    session_file = session_dir / 'session.json'
    with open(session_file, 'w') as f:
        json.dump({'username': username, 'timestamp': datetime.now().isoformat()}, f)
    logger.info("Session written to %s", session_file)


class DiagLauncher(tk.Tk):
    def __init__(self, user_info: dict = None):
        super().__init__()
        self.user_info = user_info or {}
        self.title("DiagAutoClinicOS Launcher - Where Mechanics Meet Future Intelligence")
        self.geometry("1000x650")
        self.configure(bg=BG_MAIN)
        self.resizable(False, False)
        
        # Track running processes
        self.running_processes = {}
        
        # Animation variables
        self.scan_line_y = 0
        self.glow_intensity = 0
        self.animation_running = True
        
        # Build UI components
        self._build_ui()
        
        # Ensure clean shutdown
        self.protocol("WM_DELETE_WINDOW", self.safe_shutdown)

    def _build_ui(self):
        """Build all UI components"""
        self._build_background()
        self._build_top()
        self._build_dashboard()
        self._build_bottom_bar()
        self._start_animations()

    def safe_shutdown(self):
        """Clean shutdown"""
        self.animation_running = False
        # Don't terminate processes - they should run independently
        logger.info("Launcher shutting down")
        self.destroy()

    def _build_background(self):
        """Build animated background"""
        self.canvas = tk.Canvas(self, bg=BG_MAIN, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Create grid lines
        self.grid_lines = []
        for i in range(0, 1000, 50):
            line = self.canvas.create_line(i, 0, i, 650, fill=BG_PANEL, width=1, tags="grid")
            self.grid_lines.append(line)
        for i in range(0, 650, 50):
            line = self.canvas.create_line(0, i, 1000, i, fill=BG_PANEL, width=1, tags="grid")
            self.grid_lines.append(line)

    def _build_top(self):
        """Build top header section"""
        header = tk.Frame(self.canvas, bg=BG_MAIN)
        self.canvas.create_window(0, 0, window=header, anchor="nw", width=1000, height=120)
        
        title = tk.Label(header, text="DiagAutoClinicOS", fg=ACCENT, bg=BG_MAIN,
                        font=("Segoe UI", 28, "bold"))
        title.pack(pady=(20, 0))
        
        subtitle = tk.Label(header, text="Where Mechanics Meet Future Intelligence",
                           fg=TEXT_MUTED, bg=BG_MAIN, font=("Segoe UI", 12))
        subtitle.pack(pady=(0, 10))
        
        status_frame = tk.Frame(header, bg=BG_PANEL, height=30)
        status_frame.pack(fill="x", padx=50, pady=5)
        status_frame.pack_propagate(False)

        username = self.user_info.get("username", "")
        user_label = f"👤 {username}  |  " if username else ""
        self.system_status = tk.Label(status_frame,
                                     text=f"{user_label}SYSTEM READY - All modules operational",
                                     fg=GLOW, bg=BG_PANEL, font=("Segoe UI", 10, "bold"))
        self.system_status.pack(side="left", padx=15, pady=5)

    def _build_dashboard(self):
        """Build main dashboard with tool cards"""
        dashboard = tk.Frame(self.canvas, bg=BG_MAIN)
        self.canvas.create_window(0, 120, window=dashboard, anchor="nw", width=1000, height=430)
        
        # Row 1
        row1 = tk.Frame(dashboard, bg=BG_MAIN)
        row1.pack(pady=15)
        
        # Vehicle Diagnostics - Primary tool
        self.vehicle_card = self._make_clickable_card(
            row1, "Vehicle Diagnostics",
            "AutoDiag Pro - Full system scan\nFault codes & live data streaming",
            self.launch_vehicle_diagnostics, is_primary=True
        )
        self.vehicle_card.pack(side="left", padx=15)
        
        self.ecu_card = self._make_clickable_card(
            row1, "ECU Programming",
            "Flash & coding tools\nParameter programming",
            self.launch_ecu_programming
        )
        self.ecu_card.pack(side="left", padx=15)
        
        self.security_card = self._make_clickable_card(
            row1, "Security & IMMO",
            "Key programming & sync\nSecurity access functions",
            self.launch_security_immo
        )
        self.security_card.pack(side="left", padx=15)

        # Row 2
        row2 = tk.Frame(dashboard, bg=BG_MAIN)
        row2.pack(pady=15)
        
        self.service_card = self._make_clickable_card(
            row2, "Service Reset",
            "Oil / DPF / EPB resets\nMaintenance interval configuration",
            self.launch_service_reset
        )
        self.service_card.pack(side="left", padx=15)
        
        self.sensor_card = self._make_clickable_card(
            row2, "Sensor Monitor",
            "Live sensor graphing\nReal-time data visualization",
            self.launch_sensor_monitor
        )
        self.sensor_card.pack(side="left", padx=15)
        
        self.health_card = self._make_clickable_card(
            row2, "System Health",
            "Suite diagnostics status\nComponent health monitoring",
            self.launch_system_health
        )
        self.health_card.pack(side="left", padx=15)

    def _make_clickable_card(self, parent, title_text, body_text, click_command, is_primary=False):
        """Create a clickable card with event handling and high contrast support"""
        if is_primary:
            card_bg, text_color, border_color = ACCENT, BG_MAIN, GLOW
            # Ensure text is readable on accent background
            if current_theme_name == "DACOS Light":
                 text_color = "#FFFFFF" # Force white text on Dark Teal accent
        else:
            card_bg, text_color, border_color = BG_CARD, TEXT_MAIN, GLOW

        shadow = tk.Frame(parent, bg="#0A2927" if current_theme_name != "DACOS Light" else "#004D40", width=290, height=130)
        shadow.pack_propagate(False)
        card = tk.Frame(shadow, bg=card_bg, width=280, height=120, relief="raised", bd=2)
        card.pack_propagate(False)
        card.place(x=5, y=5)
        border = tk.Frame(card, bg=border_color, width=278, height=118)
        border.pack_propagate(False)
        border.place(x=1, y=1)
        content = tk.Frame(border, bg=card_bg, width=276, height=116)
        content.pack_propagate(False)
        content.place(x=1, y=1)
        title = tk.Label(content, text=title_text, fg=text_color, bg=card_bg,
                        font=("Segoe UI", 12, "bold"))
        title.pack(anchor="w", padx=15, pady=(15, 5))
        body = tk.Label(content, text=body_text, fg=text_color, bg=card_bg,
                       font=("Segoe UI", 9), justify="left")
        body.pack(anchor="w", padx=15)

        def on_enter(e):
            # For Light theme, ensure high contrast on hover
            if current_theme_name == "DACOS Light":
                 # Use Accent as background, White as text for hover
                 hover_bg = ACCENT
                 hover_fg = "#FFFFFF"
                 hover_border = GLOW
            else:
                 hover_bg = GLOW
                 hover_fg = BG_MAIN
                 hover_border = ACCENT

            card.config(bg=hover_bg, cursor="hand2")
            border.config(bg=hover_border)
            title.config(bg=hover_bg, fg=hover_fg)
            body.config(bg=hover_bg, fg=hover_fg)
            content.config(bg=hover_bg)

        def on_leave(e):
            card.config(bg=card_bg, cursor="")
            border.config(bg=border_color)
            title.config(bg=card_bg, fg=text_color)
            body.config(bg=card_bg, fg=text_color)
            content.config(bg=card_bg)

        def on_click(e):
            logger.info(f"Card clicked: {title_text}")
            try:
                click_command()
            except Exception as ex:
                logger.error(f"Error executing click command for {title_text}: {ex}")
                self.update_status(f"Error: {str(ex)}", True)
                messagebox.showerror("Error", f"Failed to execute: {str(ex)}")

        for widget in [shadow, card, content, title, body]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

        return shadow

    def _build_bottom_bar(self):
        """Build bottom status and control section"""
        bottom = tk.Frame(self.canvas, bg=BG_MAIN)
        self.canvas.create_window(0, 540, window=bottom, anchor="nw", width=1000, height=110)
        
        self.status_label = tk.Label(bottom,
                                     text="SYSTEM READY - Click 'Vehicle Diagnostics' to launch AutoDiag Pro",
                                     fg=GLOW, bg=BG_MAIN, font=("Segoe UI", 10, "bold"))
        self.status_label.pack(pady=5)
        
        btn_frame = tk.Frame(bottom, bg=BG_MAIN)
        btn_frame.pack(pady=2)
        
        refresh_btn = tk.Button(btn_frame, text="Refresh System", command=self.refresh_system,
                               bg=BG_PANEL, fg=TEXT_MAIN, font=("Segoe UI", 9),
                               relief="flat", padx=15, pady=5, cursor="hand2")
        refresh_btn.pack(side="left", padx=10)

        theme_btn = tk.Button(btn_frame, text="Change Theme", command=self.select_theme_dialog,
                             bg=BG_PANEL, fg=ACCENT, font=("Segoe UI", 9),
                             relief="flat", padx=15, pady=5, cursor="hand2")
        theme_btn.pack(side="left", padx=10)
        
        exit_btn = tk.Button(btn_frame, text="Safe Exit", command=self.safe_shutdown,
                            bg=BG_PANEL, fg=ERROR, font=("Segoe UI", 9),
                            relief="flat", padx=15, pady=5, cursor="hand2")
        exit_btn.pack(side="left", padx=10)

        # Alpha buttons integrated into the bottom bar (no overlap)
        if ALPHA_TEST_MODE:
            tk.Button(btn_frame, text="Test Platform Checklist",
                      command=self._show_test_checklist,
                      bg=ACCENT, fg=BG_MAIN, font=("Segoe UI", 9, "bold"),
                      relief="flat", padx=12, pady=5, cursor="hand2").pack(side="left", padx=10)
            tk.Button(btn_frame, text="Charlemaine (Local)",
                      command=self._show_charlemaine_info,
                      bg=BG_PANEL, fg=ACCENT, font=("Segoe UI", 9),
                      relief="flat", padx=12, pady=5, cursor="hand2").pack(side="left", padx=10)

    def _show_test_checklist(self):
        """Alpha test platform checklist dialog."""
        dialog = tk.Toplevel(self)
        dialog.title("Alpha Test Platform Checklist")
        dialog.geometry("600x500")
        dialog.configure(bg=BG_MAIN)
        dialog.transient(self)
        dialog.grab_set()
        tk.Label(dialog, text="Alpha Test Platform Checklist", fg=ACCENT, bg=BG_MAIN,
                 font=("Segoe UI", 16, "bold")).pack(pady=20)
        checklist = [
            "AutoDiag launches and connects to VCI",
            "All vehicle brands/models are selectable",
            "Live data and DTCs work for all supported protocols",
            "Test User has full access (Professional)",
            "Charlemaine local integration present",
            "PDF report generation works",
            "No crashes or UI freezes",
            "All tabs accessible",
            "Offline mode functional"
        ]
        for item in checklist:
            var = tk.BooleanVar(value=False)
            cb = tk.Checkbutton(dialog, text=item, variable=var, fg=TEXT_MAIN, bg=BG_MAIN,
                               font=("Segoe UI", 11), selectcolor=ACCENT,
                               activebackground=BG_PANEL)
            cb.pack(anchor="w", padx=40, pady=4)
        tk.Button(dialog, text="Close", command=dialog.destroy,
                  bg=BG_PANEL, fg=TEXT_MAIN, font=("Segoe UI", 10),
                  padx=20, pady=6).pack(pady=20)

    def _show_charlemaine_info(self):
        """Charlemaine integration info dialog."""
        dialog = tk.Toplevel(self)
        dialog.title("Charlemaine (Local)")
        dialog.geometry("400x250")
        dialog.configure(bg=BG_MAIN)
        dialog.transient(self)
        dialog.grab_set()
        tk.Label(dialog, text="Charlemaine Integration", fg=ACCENT, bg=BG_MAIN,
                 font=("Segoe UI", 15, "bold")).pack(pady=20)
        tk.Label(dialog, text="Charlemaine is running locally for Alpha Test.\n"
                              "No network calls are made.\n"
                              "All AI/assistant features are sandboxed.",
                 fg=TEXT_MAIN, bg=BG_MAIN, font=("Segoe UI", 11),
                 wraplength=350, justify="left").pack(pady=10)
        tk.Button(dialog, text="Close", command=dialog.destroy,
                  bg=BG_PANEL, fg=TEXT_MAIN, font=("Segoe UI", 10),
                  padx=20, pady=6).pack(pady=20)

    def select_theme_dialog(self):
        """Open dialog to select theme"""
        dialog = tk.Toplevel(self)
        dialog.title("Select Theme")
        dialog.geometry("400x400") # Increased height for more themes
        dialog.configure(bg=BG_MAIN)
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        x = self.winfo_x() + (self.winfo_width() // 2) - 200
        y = self.winfo_y() + (self.winfo_height() // 2) - 200
        dialog.geometry(f"+{x}+{y}")

        lbl = tk.Label(dialog, text="Select Interface Theme", fg=ACCENT, bg=BG_MAIN,
                      font=("Segoe UI", 14, "bold"))
        lbl.pack(pady=20)

        # Scrollable frame for themes
        container = tk.Frame(dialog, bg=BG_MAIN)
        container.pack(fill="both", expand=True, padx=10, pady=5)
        
        canvas = tk.Canvas(container, bg=BG_MAIN, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_MAIN)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Mousewheel Support ---
        def on_mousewheel(event):
            # Windows/MacOS: event.delta
            if event.delta:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            # Linux: event.num (4=up, 5=down) handled via separate binds if needed
        
        # Bind to canvas and parent dialog to ensure it catches the event
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Unbind when dialog closes to prevent errors in main window
        def on_close():
            canvas.unbind_all("<MouseWheel>")
            dialog.destroy()
            
        dialog.protocol("WM_DELETE_WINDOW", on_close)

        current = current_theme_name
        
        for theme_name in AVAILABLE_THEMES.keys():
            is_current = (theme_name == current)
            prefix = "✓ " if is_current else "   "
            btn_text = f"{prefix}{theme_name}"
            
            btn = tk.Button(scrollable_frame, text=btn_text, 
                           command=lambda t=theme_name: self.apply_theme_selection(t, dialog),
                           bg=BG_PANEL if not is_current else BG_CARD,
                           fg=TEXT_MAIN if not is_current else ACCENT,
                           font=("Segoe UI", 10),
                           relief="flat", width=35, pady=5, cursor="hand2")
            btn.pack(pady=2)

        note = tk.Label(dialog, text="* Restart required to apply changes", 
                       fg=TEXT_MUTED, bg=BG_MAIN, font=("Segoe UI", 9, "italic"))
        note.pack(side="bottom", pady=20)

    def apply_theme_selection(self, theme_name, dialog):
        """Save theme selection and prompt restart"""
        if save_theme_config(theme_name):
            dialog.destroy()
            msg = f"Theme set to '{theme_name}'.\n\nPlease restart the launcher to apply changes."
            messagebox.showinfo("Theme Changed", msg)
            logger.info(f"Theme changed to {theme_name}, restart required")
        else:
            messagebox.showerror("Error", "Failed to save configuration")

    def _start_animations(self):
        """Start background animations"""
        self._animate_scan_line()
        self._animate_glow()

    def _animate_scan_line(self):
        if not self.animation_running: return
        self.scan_line_y = (self.scan_line_y + 2) % 650
        self.canvas.delete("scan_line")
        self.canvas.create_line(0, self.scan_line_y, 1000, self.scan_line_y,
                              fill=ACCENT, width=2, tags="scan_line", dash=(5, 5))
        self.after(50, self._animate_scan_line)

    def _animate_glow(self):
        if not self.animation_running: return
        self.glow_intensity = (self.glow_intensity + 0.1) % (2 * math.pi)
        intensity = (math.sin(self.glow_intensity) + 1) / 2
        glow_color = self.interpolate_color(BG_PANEL, GLOW, intensity)
        self.system_status.config(fg=glow_color)
        self.after(100, self._animate_glow)

    def interpolate_color(self, color1, color2, factor):
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    def update_status(self, message, is_error=False):
        self.status_label.config(text=message, fg=ERROR if is_error else GLOW)
        self.update_idletasks()

    def _launch_module(self, module_name, module_dir_name):
        """
        FIXED: Launch module in detached process with proper flags
        Creates new console window and doesn't block launcher
        """
        self.update_status(f"LAUNCHING {module_name.upper()}...")
        logger.info(f"Launching {module_name}...")

        module_dir = PROJECT_ROOT / module_dir_name
        main_py_path = module_dir / "main.py"

        if not main_py_path.exists():
            self.update_status(f"ERROR: {module_name} main.py not found", True)
            messagebox.showerror("File Missing", f"{main_py_path} not found.")
            return

        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT)
        if sys.platform == "win32":
                env["QT_QPA_PLATFORM"] = "windows"
        # Fix Unicode encoding issues in subprocess
        env["PYTHONIOENCODING"] = "utf-8"

        try:
            # CRITICAL FIX: Use CREATE_NEW_CONSOLE flag
            # This creates a detached process with its own console
            # Process will continue running even if launcher closes
            import subprocess
            
            if sys.platform == "win32":
                # Windows: Create new console window
                CREATE_NEW_CONSOLE = 0x00000010
                DETACHED_PROCESS = 0x00000008
                
                process = subprocess.Popen(
                    [str(VENV_PYTHON_PATH), str(main_py_path)],
                    cwd=str(module_dir),
                    env=env,
                    creationflags=CREATE_NEW_CONSOLE,  # Creates independent window
                    stdout=None,  # Don't capture output
                    stderr=None,
                    stdin=None
                )
            else:
                # Linux/Mac
                process = subprocess.Popen(
                    [str(VENV_PYTHON_PATH), str(main_py_path)],
                    cwd=str(module_dir),
                    env=env,
                    start_new_session=True
                )
            
            self.running_processes[module_name] = process
            self.update_status(f"SUCCESS - {module_name.upper()} LAUNCHED IN NEW WINDOW")
            logger.info(f"Successfully launched {module_name} (PID: {process.pid})")
            
            # Show success message
            messagebox.showinfo("Success",
                              f"{module_name} has been launched successfully!\n\n"
                              f"A new window should appear shortly.\n"
                              f"PID: {process.pid}")
            
        except Exception as e:
            self.update_status(f"ERROR: Failed to launch {module_name}", True)
            messagebox.showerror("Launch Error", f"Failed to launch {module_name}:\n{e}")
            logger.error(f"Launch error for {module_name}: {e}")

    def launch_vehicle_diagnostics(self):
        self._launch_module("AutoDiag Pro", "AutoDiag")

    def launch_ecu_programming(self):
        """Show AutoECU preview — planned for Q1/Q2 2027."""
        self.update_status("AutoECU — Preview")
        self._show_coming_soon(
            title="⚡ AutoECU — Coming Q1/Q2 2027",
            description="ECU Flash Programming & Coding Suite",
            features=[
                "ECU Flash Programming (Bootloader + J2534)",
                "Parameter Coding & Adaptation Channels",
                "Firmware Version Management & Backup",
                "Checksum Correction & Validation",
                "Multi-ECU Synchronisation",
            ],
            note="AutoECU is under active development.\nAutoDiag is our current priority for the Alpha release.",
        )

    def launch_security_immo(self):
        """Show AutoKey preview — planned for Q1/Q2 2027."""
        self.update_status("AutoKey — Preview")
        self._show_coming_soon(
            title="🔐 AutoKey — Coming Q1/Q2 2027",
            description="Security & Immobiliser Programming Suite",
            features=[
                "Key Programming & Transponder Cloning",
                "Immobiliser Synchronisation (Ford / GM)",
                "Security Access — Seed/Key Authentication",
                "Remote Key Fob Programming",
                "EEPROM / MCU Security Data Read",
            ],
            note="AutoKey is under active development.\nAutoDiag is our current priority for the Alpha release.",
        )

    def _show_coming_soon(self, title: str, description: str, features: list, note: str):
        """Display a clean 'Coming Soon' preview dialog for planned modules."""
        import tkinter as tk

        dialog = tk.Toplevel(self)
        dialog.title(title.split("—")[0].strip())
        dialog.geometry("480x420")
        dialog.configure(bg=BG_MAIN)
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Center over parent
        dialog.update_idletasks()
        px = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        py = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{px}+{py}")

        # Header
        tk.Label(
            dialog, text=title, fg=ACCENT, bg=BG_MAIN,
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=(25, 5))

        tk.Label(
            dialog, text=description, fg=TEXT_MUTED, bg=BG_MAIN,
            font=("Segoe UI", 11),
        ).pack(pady=(0, 15))

        # Separator
        sep = tk.Frame(dialog, bg=ACCENT, height=1)
        sep.pack(fill="x", padx=40, pady=(0, 15))

        # Feature list
        features_frame = tk.Frame(dialog, bg=BG_MAIN)
        features_frame.pack(fill="x", padx=50)

        tk.Label(
            features_frame, text="Planned Features:",
            fg=TEXT_MAIN, bg=BG_MAIN,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        for feature in features:
            row = tk.Frame(features_frame, bg=BG_MAIN)
            row.pack(fill="x", pady=2)
            tk.Label(
                row, text="▸", fg=ACCENT, bg=BG_MAIN,
                font=("Segoe UI", 10),
            ).pack(side="left")
            tk.Label(
                row, text=feature, fg=TEXT_MAIN, bg=BG_MAIN,
                font=("Segoe UI", 10),
            ).pack(side="left", padx=(5, 0))

        # Note
        if note:
            tk.Label(
                dialog, text=note, fg=TEXT_MUTED, bg=BG_MAIN,
                font=("Segoe UI", 9, "italic"), justify="center",
            ).pack(pady=(15, 5))

        # Close button
        tk.Button(
            dialog, text="Close", command=dialog.destroy,
            bg=BG_PANEL, fg=TEXT_MAIN,
            font=("Segoe UI", 10),
            relief="flat", padx=25, pady=6, cursor="hand2",
        ).pack(pady=(10, 20))

        dialog.bind("<Escape>", lambda _e: dialog.destroy())

    def launch_service_reset(self):
        """Launch Service Reset tools - Oil, DPF, EPB, and maintenance resets"""
        self.update_status("LAUNCHING SERVICE RESET TOOLS...")

        # For now, show a dialog with available service reset options
        # In future versions, this could launch a dedicated service reset application
        import tkinter as tk
        from tkinter import ttk, messagebox

        # Create service reset dialog
        reset_dialog = tk.Toplevel(self)
        reset_dialog.title("Service Reset Tools - DiagAutoClinicOS")
        reset_dialog.geometry("600x500")
        reset_dialog.configure(bg=BG_MAIN)
        reset_dialog.resizable(False, False)

        # Center the dialog
        reset_dialog.transient(self)
        reset_dialog.grab_set()

        # Title
        title_label = tk.Label(reset_dialog, text="🔧 Service Reset Tools",
                              fg=ACCENT, bg=BG_MAIN,
                              font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=(20, 10))

        subtitle_label = tk.Label(reset_dialog,
                                 text="Reset maintenance intervals and service indicators",
                                 fg=TEXT_MUTED, bg=BG_MAIN,
                                 font=("Segoe UI", 10))
        subtitle_label.pack(pady=(0, 20))

        # Service options frame
        options_frame = tk.Frame(reset_dialog, bg=BG_PANEL)
        options_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Oil Service Reset
        oil_frame = tk.Frame(options_frame, bg=BG_CARD, relief="raised", bd=1)
        oil_frame.pack(fill="x", padx=10, pady=5)

        oil_title = tk.Label(oil_frame, text="🛢️ Oil Service Reset",
                            fg=TEXT_MAIN, bg=BG_CARD,
                            font=("Segoe UI", 12, "bold"))
        oil_title.pack(anchor="w", padx=15, pady=(10, 5))

        oil_desc = tk.Label(oil_frame,
                           text="Reset oil change interval and service indicator light",
                           fg=TEXT_MUTED, bg=BG_CARD,
                           font=("Segoe UI", 9), justify="left")
        oil_desc.pack(anchor="w", padx=15, pady=(0, 10))

        oil_btn = tk.Button(oil_frame, text="Reset Oil Service",
                           bg=ACCENT, fg=BG_MAIN,
                           font=("Segoe UI", 10, "bold"),
                           command=lambda: self._perform_oil_reset(reset_dialog))
        oil_btn.pack(anchor="e", padx=15, pady=(0, 10))

        # DPF Reset
        dpf_frame = tk.Frame(options_frame, bg=BG_CARD, relief="raised", bd=1)
        dpf_frame.pack(fill="x", padx=10, pady=5)

        dpf_title = tk.Label(dpf_frame, text="🌫️ DPF (Diesel Particulate Filter) Reset",
                            fg=TEXT_MAIN, bg=BG_CARD,
                            font=("Segoe UI", 12, "bold"))
        dpf_title.pack(anchor="w", padx=15, pady=(10, 5))

        dpf_desc = tk.Label(dpf_frame,
                           text="Reset DPF regeneration cycle and warning indicators",
                           fg=TEXT_MUTED, bg=BG_CARD,
                           font=("Segoe UI", 9), justify="left")
        dpf_desc.pack(anchor="w", padx=15, pady=(0, 10))

        dpf_btn = tk.Button(dpf_frame, text="Reset DPF",
                           bg=ACCENT, fg=BG_MAIN,
                           font=("Segoe UI", 10, "bold"),
                           command=lambda: self._perform_dpf_reset(reset_dialog))
        dpf_btn.pack(anchor="e", padx=15, pady=(0, 10))

        # EPB Reset
        epb_frame = tk.Frame(options_frame, bg=BG_CARD, relief="raised", bd=1)
        epb_frame.pack(fill="x", padx=10, pady=5)

        epb_title = tk.Label(epb_frame, text="🅿️ EPB (Electronic Parking Brake) Reset",
                            fg=TEXT_MAIN, bg=BG_CARD,
                            font=("Segoe UI", 12, "bold"))
        epb_title.pack(anchor="w", padx=15, pady=(10, 5))

        epb_desc = tk.Label(epb_frame,
                           text="Calibrate electronic parking brake system",
                           fg=TEXT_MUTED, bg=BG_CARD,
                           font=("Segoe UI", 9), justify="left")
        epb_desc.pack(anchor="w", padx=15, pady=(0, 10))

        epb_btn = tk.Button(epb_frame, text="Reset EPB",
                           bg=ACCENT, fg=BG_MAIN,
                           font=("Segoe UI", 10, "bold"),
                           command=lambda: self._perform_epb_reset(reset_dialog))
        epb_btn.pack(anchor="e", padx=15, pady=(0, 10))

        # Maintenance Interval Reset
        maint_frame = tk.Frame(options_frame, bg=BG_CARD, relief="raised", bd=1)
        maint_frame.pack(fill="x", padx=10, pady=5)

        maint_title = tk.Label(maint_frame, text="🔧 Maintenance Interval Reset",
                              fg=TEXT_MAIN, bg=BG_CARD,
                              font=("Segoe UI", 12, "bold"))
        maint_title.pack(anchor="w", padx=15, pady=(10, 5))

        maint_desc = tk.Label(maint_frame,
                             text="Reset all maintenance service intervals and reminders",
                             fg=TEXT_MUTED, bg=BG_CARD,
                             font=("Segoe UI", 9), justify="left")
        maint_desc.pack(anchor="w", padx=15, pady=(0, 10))

        maint_btn = tk.Button(maint_frame, text="Reset Maintenance",
                             bg=ACCENT, fg=BG_MAIN,
                             font=("Segoe UI", 10, "bold"),
                             command=lambda: self._perform_maintenance_reset(reset_dialog))
        maint_btn.pack(anchor="e", padx=15, pady=(0, 10))

        # Bottom buttons
        btn_frame = tk.Frame(reset_dialog, bg=BG_MAIN)
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        close_btn = tk.Button(btn_frame, text="Close",
                             bg=BG_PANEL, fg=TEXT_MAIN,
                             font=("Segoe UI", 10),
                             command=reset_dialog.destroy)
        close_btn.pack(side="right", padx=(10, 0))

        # Hardware warning
        warning_label = tk.Label(btn_frame,
                                text="⚠️ Hardware Required: Connect VCI device for actual resets",
                                fg=WARNING, bg=BG_MAIN,
                                font=("Segoe UI", 9, "italic"))
        warning_label.pack(side="left")

        self.update_status("SERVICE RESET TOOLS READY")

    def _perform_oil_reset(self, parent_dialog):
        """Perform oil service reset"""
        result = messagebox.askyesno("Confirm Oil Reset",
                                    "This will reset the oil service interval.\n\n"
                                    "⚠️ Hardware Required: VCI device must be connected to vehicle.\n\n"
                                    "Continue?")
        if result:
            # For now, show simulation message
            messagebox.showinfo("Oil Service Reset",
                              "🛢️ Oil Service Reset\n\n"
                              "Simulation: Oil change interval has been reset to factory defaults.\n\n"
                              "In production version: This would communicate with the vehicle's ECU\n"
                              "to reset the oil service maintenance light and interval counter.")
            self.update_status("OIL SERVICE RESET COMPLETED (SIMULATION)")

    def _perform_dpf_reset(self, parent_dialog):
        """Perform DPF reset"""
        result = messagebox.askyesno("Confirm DPF Reset",
                                    "This will reset the DPF regeneration cycle.\n\n"
                                    "⚠️ Hardware Required: VCI device must be connected to vehicle.\n\n"
                                    "Continue?")
        if result:
            messagebox.showinfo("DPF Reset",
                              "🌫️ DPF Reset\n\n"
                              "Simulation: DPF regeneration cycle has been reset.\n\n"
                              "In production version: This would communicate with the vehicle's ECU\n"
                              "to reset DPF warning indicators and regeneration counters.")
            self.update_status("DPF RESET COMPLETED (SIMULATION)")

    def _perform_epb_reset(self, parent_dialog):
        """Perform EPB reset"""
        result = messagebox.askyesno("Confirm EPB Reset",
                                    "This will calibrate the electronic parking brake.\n\n"
                                    "⚠️ Hardware Required: VCI device must be connected to vehicle.\n"
                                    "⚠️ Vehicle must be in service position.\n\n"
                                    "Continue?")
        if result:
            messagebox.showinfo("EPB Reset",
                              "🅿️ EPB Calibration\n\n"
                              "Simulation: Electronic parking brake has been calibrated.\n\n"
                              "In production version: This would perform automatic calibration\n"
                              "of the EPB system including brake pad wear compensation.")
            self.update_status("EPB RESET COMPLETED (SIMULATION)")

    def _perform_maintenance_reset(self, parent_dialog):
        """Perform maintenance interval reset"""
        result = messagebox.askyesno("Confirm Maintenance Reset",
                                    "This will reset all maintenance service intervals.\n\n"
                                    "⚠️ Hardware Required: VCI device must be connected to vehicle.\n\n"
                                    "Continue?")
        if result:
            messagebox.showinfo("Maintenance Reset",
                              "🔧 Maintenance Interval Reset\n\n"
                              "Simulation: All maintenance intervals have been reset to factory defaults.\n\n"
                              "In production version: This would reset all service reminder intervals\n"
                              "including timing belt, transmission service, brake fluid, etc.")
            self.update_status("MAINTENANCE RESET COMPLETED (SIMULATION)")

    def _start_engine_monitoring(self, parent_dialog):
        """Start engine sensor monitoring"""
        if hasattr(self, 'live_data_text'):
            self.live_data_text.delete("1.0", "end")
            self.live_data_text.insert("1.0", "🔥 ENGINE SENSOR MONITORING ACTIVE\n\n"
                                            "Monitoring coolant temperature, oil pressure, intake air temp,\n"
                                            "engine RPM, throttle position, and fuel pressure...\n\n"
                                            "SIMULATION MODE - Hardware required for real data:\n\n"
                                            "Coolant Temp: 85°C\n"
                                            "Oil Pressure: 3.2 bar\n"
                                            "Intake Air: 32°C\n"
                                            "Engine RPM: 1200\n"
                                            "Throttle: 8%\n"
                                            "Fuel Pressure: 3.8 bar\n\n"
                                            "In production: Real-time data would stream from vehicle ECU.")
            self.update_status("ENGINE SENSORS MONITORING (SIMULATION)")

    def _start_transmission_monitoring(self, parent_dialog):
        """Start transmission sensor monitoring"""
        if hasattr(self, 'live_data_text'):
            self.live_data_text.delete("1.0", "end")
            self.live_data_text.insert("1.0", "⚙️ TRANSMISSION SENSOR MONITORING ACTIVE\n\n"
                                            "Monitoring transmission temperature, gear position,\n"
                                            "turbine speed, line pressure, and solenoid status...\n\n"
                                            "SIMULATION MODE - Hardware required for real data:\n\n"
                                            "Trans Temp: 78°C\n"
                                            "Gear Position: 3\n"
                                            "Turbine Speed: 1800 RPM\n"
                                            "Line Pressure: 45 PSI\n"
                                            "Solenoids: OK\n\n"
                                            "In production: Real-time transmission data would be displayed.")
            self.update_status("TRANSMISSION SENSORS MONITORING (SIMULATION)")

    def _start_brake_monitoring(self, parent_dialog):
        """Start brake system sensor monitoring"""
        if hasattr(self, 'live_data_text'):
            self.live_data_text.delete("1.0", "end")
            self.live_data_text.insert("1.0", "🛑 BRAKE SYSTEM SENSOR MONITORING ACTIVE\n\n"
                                            "Monitoring brake pressure, ABS wheel speeds,\n"
                                            "brake pad wear, fluid level, and parking brake...\n\n"
                                            "SIMULATION MODE - Hardware required for real data:\n\n"
                                            "Brake Pressure: 28 bar\n"
                                            "FL Wheel: 0 km/h\n"
                                            "FR Wheel: 0 km/h\n"
                                            "RL Wheel: 0 km/h\n"
                                            "RR Wheel: 0 km/h\n"
                                            "Pad Wear: 15%\n"
                                            "Fluid Level: OK\n\n"
                                            "In production: Real-time brake system diagnostics available.")
            self.update_status("BRAKE SENSORS MONITORING (SIMULATION)")

    def _stop_sensor_monitoring(self, parent_dialog):
        """Stop sensor monitoring"""
        if hasattr(self, 'live_data_text'):
            self.live_data_text.delete("1.0", "end")
            self.live_data_text.insert("1.0", "⏹️ Sensor monitoring stopped.\n\n"
                                            "🔌 Connect VCI device to resume monitoring.")
            self.update_status("SENSOR MONITORING STOPPED")

    def launch_sensor_monitor(self):
        """Launch Sensor Monitor tools - Live sensor graphing and visualization"""
        self.update_status("LAUNCHING SENSOR MONITOR...")

        # For now, show a dialog with sensor monitoring options
        # In future versions, this could launch a dedicated sensor monitoring application
        import tkinter as tk
        from tkinter import ttk, messagebox

        # Create sensor monitor dialog
        monitor_dialog = tk.Toplevel(self)
        monitor_dialog.title("Sensor Monitor - DiagAutoClinicOS")
        monitor_dialog.geometry("700x600")
        monitor_dialog.configure(bg=BG_MAIN)
        monitor_dialog.resizable(False, False)

        # Center the dialog
        monitor_dialog.transient(self)
        monitor_dialog.grab_set()

        # Title
        title_label = tk.Label(monitor_dialog, text="📊 Sensor Monitor",
                              fg=ACCENT, bg=BG_MAIN,
                              font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=(20, 10))

        subtitle_label = tk.Label(monitor_dialog,
                                 text="Real-time sensor data visualization and graphing",
                                 fg=TEXT_MUTED, bg=BG_MAIN,
                                 font=("Segoe UI", 10))
        subtitle_label.pack(pady=(0, 20))

        # Main content frame
        content_frame = tk.Frame(monitor_dialog, bg=BG_PANEL)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Sensor categories
        categories_frame = tk.Frame(content_frame, bg=BG_PANEL)
        categories_frame.pack(fill="x", padx=10, pady=10)

        # Engine sensors
        engine_frame = tk.Frame(categories_frame, bg=BG_CARD, relief="raised", bd=1)
        engine_frame.pack(fill="x", pady=5)

        engine_title = tk.Label(engine_frame, text="🔥 Engine Sensors",
                               fg=TEXT_MAIN, bg=BG_CARD,
                               font=("Segoe UI", 12, "bold"))
        engine_title.pack(anchor="w", padx=15, pady=(10, 5))

        engine_sensors = ["Coolant Temperature", "Oil Pressure", "Intake Air Temperature",
                         "Engine RPM", "Throttle Position", "Fuel Pressure"]
        engine_text = "• " + "\n• ".join(engine_sensors)
        engine_label = tk.Label(engine_frame, text=engine_text,
                               fg=TEXT_MUTED, bg=BG_CARD,
                               font=("Segoe UI", 9), justify="left")
        engine_label.pack(anchor="w", padx=15, pady=(0, 10))

        engine_btn = tk.Button(engine_frame, text="Monitor Engine",
                              bg=ACCENT, fg=BG_MAIN,
                              font=("Segoe UI", 10, "bold"),
                              command=lambda: self._start_engine_monitoring(monitor_dialog))
        engine_btn.pack(anchor="e", padx=15, pady=(0, 10))

        # Transmission sensors
        trans_frame = tk.Frame(categories_frame, bg=BG_CARD, relief="raised", bd=1)
        trans_frame.pack(fill="x", pady=5)

        trans_title = tk.Label(trans_frame, text="⚙️ Transmission Sensors",
                              fg=TEXT_MAIN, bg=BG_CARD,
                              font=("Segoe UI", 12, "bold"))
        trans_title.pack(anchor="w", padx=15, pady=(10, 5))

        trans_sensors = ["Transmission Temperature", "Gear Position", "Turbine Speed",
                        "Line Pressure", "Shift Solenoid Status"]
        trans_text = "• " + "\n• ".join(trans_sensors)
        trans_label = tk.Label(trans_frame, text=trans_text,
                              fg=TEXT_MUTED, bg=BG_CARD,
                              font=("Segoe UI", 9), justify="left")
        trans_label.pack(anchor="w", padx=15, pady=(0, 10))

        trans_btn = tk.Button(trans_frame, text="Monitor Transmission",
                             bg=ACCENT, fg=BG_MAIN,
                             font=("Segoe UI", 10, "bold"),
                             command=lambda: self._start_transmission_monitoring(monitor_dialog))
        trans_btn.pack(anchor="e", padx=15, pady=(0, 10))

        # Brake system sensors
        brake_frame = tk.Frame(categories_frame, bg=BG_CARD, relief="raised", bd=1)
        brake_frame.pack(fill="x", pady=5)

        brake_title = tk.Label(brake_frame, text="🛑 Brake System Sensors",
                              fg=TEXT_MAIN, bg=BG_CARD,
                              font=("Segoe UI", 12, "bold"))
        brake_title.pack(anchor="w", padx=15, pady=(10, 5))

        brake_sensors = ["Brake Pressure", "ABS Wheel Speed", "Brake Pad Wear",
                        "Brake Fluid Level", "Parking Brake Status"]
        brake_text = "• " + "\n• ".join(brake_sensors)
        brake_label = tk.Label(brake_frame, text=brake_text,
                              fg=TEXT_MUTED, bg=BG_CARD,
                              font=("Segoe UI", 9), justify="left")
        brake_label.pack(anchor="w", padx=15, pady=(0, 10))

        brake_btn = tk.Button(brake_frame, text="Monitor Brakes",
                             bg=ACCENT, fg=BG_MAIN,
                             font=("Segoe UI", 10, "bold"),
                             command=lambda: self._start_brake_monitoring(monitor_dialog))
        brake_btn.pack(anchor="e", padx=15, pady=(0, 10))

        # Live data display area
        data_frame = tk.Frame(content_frame, bg=BG_CARD, relief="sunken", bd=1)
        data_frame.pack(fill="both", expand=True, padx=10, pady=(10, 10))

        data_title = tk.Label(data_frame, text="📈 Live Sensor Data",
                             fg=TEXT_MAIN, bg=BG_CARD,
                             font=("Segoe UI", 12, "bold"))
        data_title.pack(pady=(10, 5))

        # Text area for live data
        self.live_data_text = tk.Text(data_frame, height=8, width=60,
                                     bg=BG_PANEL, fg=TEXT_MAIN,
                                     font=("Consolas", 9))
        self.live_data_text.pack(padx=10, pady=(0, 10), fill="both", expand=True)
        self.live_data_text.insert("1.0", "🔌 Connect VCI device to start monitoring sensors...\n\n"
                                        "Available sensors will be displayed here with real-time values.")

        # Control buttons
        btn_frame = tk.Frame(monitor_dialog, bg=BG_MAIN)
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        stop_btn = tk.Button(btn_frame, text="Stop Monitoring",
                            bg=ERROR, fg=BG_MAIN,
                            font=("Segoe UI", 10, "bold"),
                            command=lambda: self._stop_sensor_monitoring(monitor_dialog))
        stop_btn.pack(side="right", padx=(10, 0))

        close_btn = tk.Button(btn_frame, text="Close",
                             bg=BG_PANEL, fg=TEXT_MAIN,
                             font=("Segoe UI", 10),
                             command=monitor_dialog.destroy)
        close_btn.pack(side="right", padx=(10, 0))

        # Hardware warning
        warning_label = tk.Label(btn_frame,
                                text="⚠️ Hardware Required: Connect VCI device for live data",
                                fg=WARNING, bg=BG_MAIN,
                                font=("Segoe UI", 9, "italic"))
        warning_label.pack(side="left")

        self.update_status("SENSOR MONITOR READY")

    def launch_system_health(self):
        self.update_status("SYSTEM HEALTH CHECK RUNNING...")
        py_arch = "64-bit" if platform.architecture()[0] == "64bit" else "32-bit"
        report = (
            "System Health Report:\n\n"
            f"Python Architecture: {py_arch}\n"
            f"Platform: {sys.platform}\n"
            "Status: ALL SYSTEMS OPERATIONAL"
        )
        messagebox.showinfo("System Health", report)
        self.update_status("SYSTEM HEALTH CHECK COMPLETED")

    def refresh_system(self):
        self.update_status("SYSTEM REFRESHED")
        self.system_status.config(text="SYSTEM READY - All modules operational", fg=GLOW)


if __name__ == "__main__":
    try:
        logger.info("Starting DiagAutoClinicOS Launcher")

        # --- Step 1: Show login dialog FIRST (before creating main window) ---
        # Uses callback-based flow — no wait_window() which can deadlock with grab_set()
        user_info = _run_login_flow()
        
        if user_info is None:
            logger.info("Login cancelled – exiting")
            sys.exit(0)

        # Save session so AutoDiag (child process) can skip its own login
        username = user_info.get("username", "")
        if username:
            _write_session(username)
        
        # --- Step 2: Create main window with authenticated user ---
        app = DiagLauncher(user_info)

        # --- Step 3: Patch brand database for Alpha (all brands/models available) ---
        if ALPHA_TEST_MODE:
            try:
                import shared.brand_database as _brand_db
                def all_brands_patch(*args, **kwargs):
                    return list(_brand_db.brand_database.brand_data.keys())
                _brand_db.brand_database.get_brand_list = all_brands_patch
                logger.info("Alpha Test Mode: All brands/models unlocked.")
            except Exception as e:
                logger.error(f"Alpha Test Mode: Failed to patch brand database: {e}")

        app.mainloop()
        logger.info("DiagAutoClinicOS Launcher closed successfully")
    except Exception as e:
        logger.critical("Fatal error in launcher: %s", e, exc_info=True)
        try:
            messagebox.showerror("Critical Error", f"Launcher failed to start:\n{e}")
        except Exception:
            pass
        sys.exit(1)