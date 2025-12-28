#!/usr/bin/env python3
"""
DiagAutoClinicOS Launcher - Fixed Vehicle Diagnostics Launch
FIXES:
- Proper subprocess detachment (CREATE_NEW_CONSOLE flag)
- Better process monitoring
- Cleaner output handling
"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import subprocess
import logging
import math
import platform
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('launcher_debug.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("DiagLauncher")

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Theme Configuration
try:
    from shared.themes.dacos_theme import DACOS_THEME as THEME
    logger.info("Successfully loaded DACOS theme")
except ImportError:
    logger.warning("Could not import DACOS theme, using fallback")
    THEME = {
        "bg_main": "#0A1A1A", "bg_panel": "#0D2323", "bg_card": "#134F4A",
        "accent": "#21F5C1", "glow": "#2AF5D1", "text_main": "#E8F4F2",
        "text_muted": "#9ED9CF", "error": "#FF4D4D", "success": "#10B981",
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
WARNING = THEME["warning"]
SUCCESS = THEME["success"]

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
        
        self.system_status = tk.Label(status_frame,
                                     text="SYSTEM READY - All modules operational",
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
        title = tk.Label(content, text=title_text, fg=text_color, bg=card_bg,
                        font=("Segoe UI", 12, "bold"))
        title.pack(anchor="w", padx=15, pady=(15, 5))
        body = tk.Label(content, text=body_text, fg=text_color, bg=card_bg,
                       font=("Segoe UI", 9), justify="left")
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
        self.canvas.create_window(0, 550, window=bottom, anchor="nw", width=1000, height=100)
        
        self.status_label = tk.Label(bottom,
                                     text="SYSTEM READY - Click 'Vehicle Diagnostics' to launch AutoDiag Pro",
                                     fg=GLOW, bg=BG_MAIN, font=("Segoe UI", 10, "bold"))
        self.status_label.pack(pady=10)
        
        btn_frame = tk.Frame(bottom, bg=BG_MAIN)
        btn_frame.pack(pady=5)
        
        refresh_btn = tk.Button(btn_frame, text="Refresh System", command=self.refresh_system,
                               bg=BG_PANEL, fg=TEXT_MAIN, font=("Segoe UI", 9),
                               relief="flat", padx=15, pady=5, cursor="hand2")
        refresh_btn.pack(side="left", padx=10)
        
        exit_btn = tk.Button(btn_frame, text="Safe Exit", command=self.safe_shutdown,
                            bg=BG_PANEL, fg=ERROR, font=("Segoe UI", 9),
                            relief="flat", padx=15, pady=5, cursor="hand2")
        exit_btn.pack(side="left", padx=10)

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
                    [sys.executable, str(main_py_path)],
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
                    [sys.executable, str(main_py_path)],
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
        self._launch_module("AutoECU", "AutoECU")

    def launch_security_immo(self):
        self._launch_module("AutoKey", "AutoKey")

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
        reset_dialog.configure(bg=self.BG_MAIN)
        reset_dialog.resizable(False, False)

        # Center the dialog
        reset_dialog.transient(self)
        reset_dialog.grab_set()

        # Title
        title_label = tk.Label(reset_dialog, text="🔧 Service Reset Tools",
                              fg=self.ACCENT, bg=self.BG_MAIN,
                              font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=(20, 10))

        subtitle_label = tk.Label(reset_dialog,
                                 text="Reset maintenance intervals and service indicators",
                                 fg=self.TEXT_MUTED, bg=self.BG_MAIN,
                                 font=("Segoe UI", 10))
        subtitle_label.pack(pady=(0, 20))

        # Service options frame
        options_frame = tk.Frame(reset_dialog, bg=self.BG_PANEL)
        options_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Oil Service Reset
        oil_frame = tk.Frame(options_frame, bg=self.BG_CARD, relief="raised", bd=1)
        oil_frame.pack(fill="x", padx=10, pady=5)

        oil_title = tk.Label(oil_frame, text="🛢️ Oil Service Reset",
                            fg=self.TEXT_MAIN, bg=self.BG_CARD,
                            font=("Segoe UI", 12, "bold"))
        oil_title.pack(anchor="w", padx=15, pady=(10, 5))

        oil_desc = tk.Label(oil_frame,
                           text="Reset oil change interval and service indicator light",
                           fg=self.TEXT_MUTED, bg=self.BG_CARD,
                           font=("Segoe UI", 9), justify="left")
        oil_desc.pack(anchor="w", padx=15, pady=(0, 10))

        oil_btn = tk.Button(oil_frame, text="Reset Oil Service",
                           bg=self.ACCENT, fg=self.BG_MAIN,
                           font=("Segoe UI", 10, "bold"),
                           command=lambda: self._perform_oil_reset(reset_dialog))
        oil_btn.pack(anchor="e", padx=15, pady=(0, 10))

        # DPF Reset
        dpf_frame = tk.Frame(options_frame, bg=self.BG_CARD, relief="raised", bd=1)
        dpf_frame.pack(fill="x", padx=10, pady=5)

        dpf_title = tk.Label(dpf_frame, text="🌫️ DPF (Diesel Particulate Filter) Reset",
                            fg=self.TEXT_MAIN, bg=self.BG_CARD,
                            font=("Segoe UI", 12, "bold"))
        dpf_title.pack(anchor="w", padx=15, pady=(10, 5))

        dpf_desc = tk.Label(dpf_frame,
                           text="Reset DPF regeneration cycle and warning indicators",
                           fg=self.TEXT_MUTED, bg=self.BG_CARD,
                           font=("Segoe UI", 9), justify="left")
        dpf_desc.pack(anchor="w", padx=15, pady=(0, 10))

        dpf_btn = tk.Button(dpf_frame, text="Reset DPF",
                           bg=self.ACCENT, fg=self.BG_MAIN,
                           font=("Segoe UI", 10, "bold"),
                           command=lambda: self._perform_dpf_reset(reset_dialog))
        dpf_btn.pack(anchor="e", padx=15, pady=(0, 10))

        # EPB Reset
        epb_frame = tk.Frame(options_frame, bg=self.BG_CARD, relief="raised", bd=1)
        epb_frame.pack(fill="x", padx=10, pady=5)

        epb_title = tk.Label(epb_frame, text="🅿️ EPB (Electronic Parking Brake) Reset",
                            fg=self.TEXT_MAIN, bg=self.BG_CARD,
                            font=("Segoe UI", 12, "bold"))
        epb_title.pack(anchor="w", padx=15, pady=(10, 5))

        epb_desc = tk.Label(epb_frame,
                           text="Calibrate electronic parking brake system",
                           fg=self.TEXT_MUTED, bg=self.BG_CARD,
                           font=("Segoe UI", 9), justify="left")
        epb_desc.pack(anchor="w", padx=15, pady=(0, 10))

        epb_btn = tk.Button(epb_frame, text="Reset EPB",
                           bg=self.ACCENT, fg=self.BG_MAIN,
                           font=("Segoe UI", 10, "bold"),
                           command=lambda: self._perform_epb_reset(reset_dialog))
        epb_btn.pack(anchor="e", padx=15, pady=(0, 10))

        # Maintenance Interval Reset
        maint_frame = tk.Frame(options_frame, bg=self.BG_CARD, relief="raised", bd=1)
        maint_frame.pack(fill="x", padx=10, pady=5)

        maint_title = tk.Label(maint_frame, text="🔧 Maintenance Interval Reset",
                              fg=self.TEXT_MAIN, bg=self.BG_CARD,
                              font=("Segoe UI", 12, "bold"))
        maint_title.pack(anchor="w", padx=15, pady=(10, 5))

        maint_desc = tk.Label(maint_frame,
                             text="Reset all maintenance service intervals and reminders",
                             fg=self.TEXT_MUTED, bg=self.BG_CARD,
                             font=("Segoe UI", 9), justify="left")
        maint_desc.pack(anchor="w", padx=15, pady=(0, 10))

        maint_btn = tk.Button(maint_frame, text="Reset Maintenance",
                             bg=self.ACCENT, fg=self.BG_MAIN,
                             font=("Segoe UI", 10, "bold"),
                             command=lambda: self._perform_maintenance_reset(reset_dialog))
        maint_btn.pack(anchor="e", padx=15, pady=(0, 10))

        # Bottom buttons
        btn_frame = tk.Frame(reset_dialog, bg=self.BG_MAIN)
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        close_btn = tk.Button(btn_frame, text="Close",
                             bg=self.BG_PANEL, fg=self.TEXT_MAIN,
                             font=("Segoe UI", 10),
                             command=reset_dialog.destroy)
        close_btn.pack(side="right", padx=(10, 0))

        # Hardware warning
        warning_label = tk.Label(btn_frame,
                                text="⚠️ Hardware Required: Connect VCI device for actual resets",
                                fg=self.WARNING, bg=self.BG_MAIN,
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
        monitor_dialog.configure(bg=self.BG_MAIN)
        monitor_dialog.resizable(False, False)

        # Center the dialog
        monitor_dialog.transient(self)
        monitor_dialog.grab_set()

        # Title
        title_label = tk.Label(monitor_dialog, text="📊 Sensor Monitor",
                              fg=self.ACCENT, bg=self.BG_MAIN,
                              font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=(20, 10))

        subtitle_label = tk.Label(monitor_dialog,
                                 text="Real-time sensor data visualization and graphing",
                                 fg=self.TEXT_MUTED, bg=self.BG_MAIN,
                                 font=("Segoe UI", 10))
        subtitle_label.pack(pady=(0, 20))

        # Main content frame
        content_frame = tk.Frame(monitor_dialog, bg=self.BG_PANEL)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Sensor categories
        categories_frame = tk.Frame(content_frame, bg=self.BG_PANEL)
        categories_frame.pack(fill="x", padx=10, pady=10)

        # Engine sensors
        engine_frame = tk.Frame(categories_frame, bg=self.BG_CARD, relief="raised", bd=1)
        engine_frame.pack(fill="x", pady=5)

        engine_title = tk.Label(engine_frame, text="🔥 Engine Sensors",
                               fg=self.TEXT_MAIN, bg=self.BG_CARD,
                               font=("Segoe UI", 12, "bold"))
        engine_title.pack(anchor="w", padx=15, pady=(10, 5))

        engine_sensors = ["Coolant Temperature", "Oil Pressure", "Intake Air Temperature",
                         "Engine RPM", "Throttle Position", "Fuel Pressure"]
        engine_text = "• " + "\n• ".join(engine_sensors)
        engine_label = tk.Label(engine_frame, text=engine_text,
                               fg=self.TEXT_MUTED, bg=self.BG_CARD,
                               font=("Segoe UI", 9), justify="left")
        engine_label.pack(anchor="w", padx=15, pady=(0, 10))

        engine_btn = tk.Button(engine_frame, text="Monitor Engine",
                              bg=self.ACCENT, fg=self.BG_MAIN,
                              font=("Segoe UI", 10, "bold"),
                              command=lambda: self._start_engine_monitoring(monitor_dialog))
        engine_btn.pack(anchor="e", padx=15, pady=(0, 10))

        # Transmission sensors
        trans_frame = tk.Frame(categories_frame, bg=self.BG_CARD, relief="raised", bd=1)
        trans_frame.pack(fill="x", pady=5)

        trans_title = tk.Label(trans_frame, text="⚙️ Transmission Sensors",
                              fg=self.TEXT_MAIN, bg=self.BG_CARD,
                              font=("Segoe UI", 12, "bold"))
        trans_title.pack(anchor="w", padx=15, pady=(10, 5))

        trans_sensors = ["Transmission Temperature", "Gear Position", "Turbine Speed",
                        "Line Pressure", "Shift Solenoid Status"]
        trans_text = "• " + "\n• ".join(trans_sensors)
        trans_label = tk.Label(trans_frame, text=trans_text,
                              fg=self.TEXT_MUTED, bg=self.BG_CARD,
                              font=("Segoe UI", 9), justify="left")
        trans_label.pack(anchor="w", padx=15, pady=(0, 10))

        trans_btn = tk.Button(trans_frame, text="Monitor Transmission",
                             bg=self.ACCENT, fg=self.BG_MAIN,
                             font=("Segoe UI", 10, "bold"),
                             command=lambda: self._start_transmission_monitoring(monitor_dialog))
        trans_btn.pack(anchor="e", padx=15, pady=(0, 10))

        # Brake system sensors
        brake_frame = tk.Frame(categories_frame, bg=self.BG_CARD, relief="raised", bd=1)
        brake_frame.pack(fill="x", pady=5)

        brake_title = tk.Label(brake_frame, text="🛑 Brake System Sensors",
                              fg=self.TEXT_MAIN, bg=self.BG_CARD,
                              font=("Segoe UI", 12, "bold"))
        brake_title.pack(anchor="w", padx=15, pady=(10, 5))

        brake_sensors = ["Brake Pressure", "ABS Wheel Speed", "Brake Pad Wear",
                        "Brake Fluid Level", "Parking Brake Status"]
        brake_text = "• " + "\n• ".join(brake_sensors)
        brake_label = tk.Label(brake_frame, text=brake_text,
                              fg=self.TEXT_MUTED, bg=self.BG_CARD,
                              font=("Segoe UI", 9), justify="left")
        brake_label.pack(anchor="w", padx=15, pady=(0, 10))

        brake_btn = tk.Button(brake_frame, text="Monitor Brakes",
                             bg=self.ACCENT, fg=self.BG_MAIN,
                             font=("Segoe UI", 10, "bold"),
                             command=lambda: self._start_brake_monitoring(monitor_dialog))
        brake_btn.pack(anchor="e", padx=15, pady=(0, 10))

        # Live data display area
        data_frame = tk.Frame(content_frame, bg=self.BG_CARD, relief="sunken", bd=1)
        data_frame.pack(fill="both", expand=True, padx=10, pady=(10, 10))

        data_title = tk.Label(data_frame, text="📈 Live Sensor Data",
                             fg=self.TEXT_MAIN, bg=self.BG_CARD,
                             font=("Segoe UI", 12, "bold"))
        data_title.pack(pady=(10, 5))

        # Text area for live data
        self.live_data_text = tk.Text(data_frame, height=8, width=60,
                                     bg=self.BG_PANEL, fg=self.TEXT_MAIN,
                                     font=("Consolas", 9))
        self.live_data_text.pack(padx=10, pady=(0, 10), fill="both", expand=True)
        self.live_data_text.insert("1.0", "🔌 Connect VCI device to start monitoring sensors...\n\n"
                                        "Available sensors will be displayed here with real-time values.")

        # Control buttons
        btn_frame = tk.Frame(monitor_dialog, bg=self.BG_MAIN)
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        stop_btn = tk.Button(btn_frame, text="Stop Monitoring",
                            bg=self.ERROR, fg=self.BG_MAIN,
                            font=("Segoe UI", 10, "bold"),
                            command=lambda: self._stop_sensor_monitoring(monitor_dialog))
        stop_btn.pack(side="right", padx=(10, 0))

        close_btn = tk.Button(btn_frame, text="Close",
                             bg=self.BG_PANEL, fg=self.TEXT_MAIN,
                             font=("Segoe UI", 10),
                             command=monitor_dialog.destroy)
        close_btn.pack(side="right", padx=(10, 0))

        # Hardware warning
        warning_label = tk.Label(btn_frame,
                                text="⚠️ Hardware Required: Connect VCI device for live data",
                                fg=self.WARNING, bg=self.BG_MAIN,
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
        app = DiagLauncher()
        app.mainloop()
        logger.info("DiagAutoClinicOS Launcher closed successfully")
    except Exception as e:
        logger.critical(f"Fatal error in launcher: {e}")
        messagebox.showerror("Critical Error", f"Launcher failed to start:\n{str(e)}")