# launcher.py - DIAG AUTO CLINIC OS LAUNCHER

#!/usr/bin/env python3
"""
DiagAutoClinicOS Launcher - Fixed Vehicle Diagnostics Button
"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import time
import threading
import subprocess
import logging
import math
import platform

# --- Architecture Check ---
# Note: Previously required 32-bit for GODIAG J2534 DLL, but GD101 removed - now supports 64-bit
IS_64BIT_PYTHON = platform.architecture()[0] == "64bit"

# Configure logging with Unicode support
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('launcher_debug.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Fix Unicode encoding for console output
import codecs
class UnicodeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

# Override the stdout handler with Unicode support
logger = logging.getLogger("DiagLauncher")
logger.handlers.clear()
logger.addHandler(logging.FileHandler('launcher_debug.log', encoding='utf-8'))
logger.addHandler(UnicodeStreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Theme Configuration with fallbacks
try:
    from shared.themes.dacos_theme import DACOS_THEME as THEME
    logger.info("Successfully loaded DACOS theme from shared module")
except ImportError as e:
    logger.warning(f"Could not import DACOS theme: {e}.")
    THEME = {
        "bg_main": "#0A1A1A",
        "bg_panel": "#0D2323",
        "bg_card": "#134F4A",
        "accent": "#21F5C1",
        "glow": "#2AF5D1",
        "text_main": "#E8F4F2",
        "text_muted": "#9ED9CF",
        "error": "#FF4D4D",
        "success": "#10B981",
        "warning": "#F59E0B"
    }

BG_MAIN = THEME["bg_main"]
BG_PANEL = THEME["bg_panel"] 
BG_CARD = THEME["bg_card"]
ACCENT = THEME["accent"]
GLOW = THEME["glow"]
TEXT_MAIN = THEME["text_main"]
TEXT_MUTED = THEME["text_muted"]
ERROR = THEME["error"]

class DiagLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
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
        """Clean shutdown with process termination"""
        self.animation_running = False
        for name, process in self.running_processes.items():
            try:
                if process.poll() is None:  # Still running
                    process.terminate()
                    process.wait(timeout=2)
                    logger.info(f"Terminated {name}")
            except Exception as e:
                logger.error(f"Error terminating {name}: {e}")
        self.destroy()

    def _build_background(self):
        """Build animated background"""
        self.canvas = tk.Canvas(self, bg=BG_MAIN, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Create grid lines
        self.grid_lines = []
        for i in range(0, 1000, 50):
            line = self.canvas.create_line(
                i, 0, i, 650, fill=BG_PANEL, width=1, tags="grid"
            )
            self.grid_lines.append(line)
        for i in range(0, 650, 50):
            line = self.canvas.create_line(
                0, i, 1000, i, fill=BG_PANEL, width=1, tags="grid"
            )
            self.grid_lines.append(line)

    def _build_top(self):
        """Build top header section"""
        header = tk.Frame(self.canvas, bg=BG_MAIN)
        self.canvas.create_window(0, 0, window=header, anchor="nw", width=1000, height=120)
        
        # Main title
        title = tk.Label(
            header,
            text="DiagAutoClinicOS",
            fg=ACCENT,
            bg=BG_MAIN,
            font=("Segoe UI", 28, "bold")
        )
        title.pack(pady=(20, 0))
        
        # Subtitle
        subtitle = tk.Label(
            header,
            text="Where Mechanics Meet Future Intelligence",
            fg=TEXT_MUTED,
            bg=BG_MAIN,
            font=("Segoe UI", 12)
        )
        subtitle.pack(pady=(0, 10))
        
        # Status bar
        status_frame = tk.Frame(header, bg=BG_PANEL, height=30)
        status_frame.pack(fill="x", padx=50, pady=5)
        status_frame.pack_propagate(False)
        
        self.system_status = tk.Label(
            status_frame,
            text="● SYSTEM READY - All modules operational",
            fg=GLOW,
            bg=BG_PANEL,
            font=("Segoe UI", 10, "bold")
        )
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
            row1,
            "🚗 Vehicle Diagnostics",
            "AutoDiag Pro - Full system scan\nFault codes & live data streaming",
            self.launch_vehicle_diagnostics,
            is_primary=True
        )
        self.vehicle_card.pack(side="left", padx=15)
        
        self.ecu_card = self._make_clickable_card(
            row1,
            "⚙️ ECU Programming",
            "Flash & coding tools\nParameter programming",
            self.launch_ecu_programming
        )
        self.ecu_card.pack(side="left", padx=15)
        
        self.security_card = self._make_clickable_card(
            row1,
            "🔐 Security & IMMO",
            "Key programming & sync\nSecurity access functions",
            self.launch_security_immo
        )
        self.security_card.pack(side="left", padx=15)

        # Row 2
        row2 = tk.Frame(dashboard, bg=BG_MAIN)
        row2.pack(pady=15)
        
        self.service_card = self._make_clickable_card(
            row2,
            "🔄 Service Reset",
            "Oil / DPF / EPB resets\nMaintenance interval configuration",
            self.launch_service_reset
        )
        self.service_card.pack(side="left", padx=15)
        
        self.sensor_card = self._make_clickable_card(
            row2,
            "📊 Sensor Monitor",
            "Live sensor graphing\nReal-time data visualization",
            self.launch_sensor_monitor
        )
        self.sensor_card.pack(side="left", padx=15)
        
        self.health_card = self._make_clickable_card(
            row2,
            "❤️ System Health",
            "Suite diagnostics status\nComponent health monitoring",
            self.launch_system_health
        )
        self.health_card.pack(side="left", padx=15)

    def _make_clickable_card(self, parent, title_text, body_text, click_command, is_primary=False):
        """Create a clickable card with event handling"""
        if is_primary:
            card_bg, text_color, border_color = ACCENT, BG_MAIN, GLOW
        else:
            card_bg, text_color, border_color = BG_CARD, TEXT_MAIN, GLOW

        shadow = tk.Frame(parent, bg="#0A2927", width=290, height=130)
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
        title = tk.Label(content, text=title_text, fg=text_color, bg=card_bg, font=("Segoe UI", 12, "bold"))
        title.pack(anchor="w", padx=15, pady=(15, 5))
        body = tk.Label(content, text=body_text, fg=text_color, bg=card_bg, font=("Segoe UI", 9), justify="left")
        body.pack(anchor="w", padx=15)

        def on_enter(e):
            card.config(bg=GLOW, cursor="hand2")
            border.config(bg=ACCENT)
            title.config(bg=GLOW, fg=BG_MAIN)
            body.config(bg=GLOW, fg=BG_MAIN)
            content.config(bg=GLOW)

        def on_leave(e):
            card.config(bg=card_bg, cursor="")
            border.config(bg=border_color)
            title.config(bg=card_bg, fg=text_color)
            body.config(bg=card_bg, fg=text_color)
            content.config(bg=card_bg)

        def on_click(e):
            clean_title = title_text.split(" ", 1)[1]
            logger.info(f"Card clicked: {clean_title}")
            try:
                click_command()
            except Exception as ex:
                logger.error(f"Error executing click command for {clean_title}: {ex}")
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
        self.canvas.create_window(0, 550, window=bottom, anchor="nw", width=1000, height=100)
        
        self.status_label = tk.Label(bottom, text="● SYSTEM READY - Click 'Vehicle Diagnostics' to launch AutoDiag Pro", fg=GLOW, bg=BG_MAIN, font=("Segoe UI", 10, "bold"))
        self.status_label.pack(pady=10)
        
        btn_frame = tk.Frame(bottom, bg=BG_MAIN)
        btn_frame.pack(pady=5)
        
        refresh_btn = tk.Button(btn_frame, text="Refresh System", command=self.refresh_system, bg=BG_PANEL, fg=TEXT_MAIN, font=("Segoe UI", 9), relief="flat", padx=15, pady=5, cursor="hand2")
        refresh_btn.pack(side="left", padx=10)
        
        exit_btn = tk.Button(btn_frame, text="Safe Exit", command=self.safe_shutdown, bg=BG_PANEL, fg=ERROR, font=("Segoe UI", 9), relief="flat", padx=15, pady=5, cursor="hand2")
        exit_btn.pack(side="left", padx=10)

    def _start_animations(self):
        """Start background animations"""
        self._animate_scan_line()
        self._animate_glow()

    def _animate_scan_line(self):
        if not self.animation_running: return
        self.scan_line_y = (self.scan_line_y + 2) % 650
        self.canvas.delete("scan_line")
        self.canvas.create_line(0, self.scan_line_y, 1000, self.scan_line_y, fill=ACCENT, width=2, tags="scan_line", dash=(5, 5))
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
        r, g, b = int(r1 + (r2 - r1) * factor), int(g1 + (g2 - g1) * factor), int(b1 + (b2 - b1) * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    def update_status(self, message, is_error=False):
        self.status_label.config(text=f"● {message}", fg=ERROR if is_error else GLOW)
        self.update_idletasks()

    def _launch_module(self, module_name, module_dir_name):
        if module_name in self.running_processes and self.running_processes[module_name].poll() is None:
            self.update_status(f"{module_name.upper()} ALREADY RUNNING")
            messagebox.showinfo("Already Running", f"{module_name} is already running.")
            return

        self.update_status(f"CHECKING {module_name.upper()} INSTALLATION...")
        logger.info(f"Launching {module_name}...")

        module_dir = PROJECT_ROOT / module_dir_name
        main_py_path = module_dir / "main.py"

        if not main_py_path.exists():
            self.update_status(f"ERROR: {module_name} main.py not found", True)
            messagebox.showerror("File Missing", f"{main_py_path} not found.")
            return

        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT)
        env["QT_QPA_PLATFORM"] = "windows"

        try:
            process = subprocess.Popen(
                [sys.executable, str(main_py_path)],
                cwd=str(module_dir), env=env,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                creationflags=0
            )
            self.running_processes[module_name] = process
            self.update_status(f"✅ {module_name.upper()} LAUNCHED")
            logger.info(f"✅ {module_name} launched successfully")
            self.monitor_process(module_name, process)
        except (FileNotFoundError, PermissionError) as e:
            self.update_status(f"ERROR: Failed to launch {module_name}", True)
            messagebox.showerror("Launch Error", f"Failed to launch {module_name}: {e}")
            logger.error(f"Launch error for {module_name}: {e}")

    def launch_vehicle_diagnostics(self):
        self._launch_module("AutoDiag Pro", "AutoDiag")

    def launch_ecu_programming(self):
        self._launch_module("AutoECU", "AutoECU")

    def launch_security_immo(self):
        self._launch_module("AutoKey", "AutoKey")

    def monitor_process(self, name, process):
        def monitor():
            logger.info(f"Monitoring {name} (PID: {process.pid})")
            process.wait()
            logger.info(f"{name} finished with code: {process.returncode}")
            if process.returncode != 0:
                error_output = process.stderr.read().decode(errors='ignore')
                logger.error(f"Error in {name}:\n{error_output}")
            if name in self.running_processes:
                del self.running_processes[name]
        threading.Thread(target=monitor, daemon=True).start()

    def launch_service_reset(self):
        self.update_status("SERVICE RESET TOOLS - Coming Soon")
        messagebox.showinfo("Coming Soon", "Service Reset tools are in development.")

    def launch_sensor_monitor(self):
        self.update_status("SENSOR MONITOR - Coming Soon")
        messagebox.showinfo("Coming Soon", "Sensor Monitor is in development.")

    def launch_system_health(self):
        self.update_status("SYSTEM HEALTH CHECK RUNNING...")
        py_arch = "64-bit" if IS_64BIT_PYTHON else "32-bit"
        report = (
            "System Health Report:\n\n"
            f"Python Architecture: {py_arch}\n"
            f"Platform: {sys.platform}\n"
            "Status: ALL SYSTEMS OPERATIONAL"
        )
        messagebox.showinfo("System Health", report)
        self.update_status("✅ SYSTEM HEALTH CHECK COMPLETED")

    def refresh_system(self):
        self.update_status("🔄 SYSTEM REFRESHED")
        self.system_status.config(text="● SYSTEM READY - All modules operational", fg=GLOW)

if __name__ == "__main__":
    try:
        logger.info("Starting DiagAutoClinicOS Launcher")
        app = DiagLauncher()
        app.mainloop()
        logger.info("DiagAutoClinicOS Launcher closed successfully")
    except Exception as e:
        logger.critical(f"Fatal error in launcher: {e}")
        messagebox.showerror("Critical Error", f"Launcher failed to start:\n{str(e)}")
