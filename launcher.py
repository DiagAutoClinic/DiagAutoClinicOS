#!/usr/bin/env python3
"""
DiagAutoClinicOS Launcher - Futuristic Teal Glassmorphic Theme
Inspired by "Where Mechanics Meet Future Intelligence"
"""

import sys
from pathlib import Path
# Always add the project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]   # two levels up from current file
sys.path.insert(0, str(PROJECT_ROOT))
import tkinter as tk
from tkinter import messagebox
import time
import threading
from shared.theme_constants import THEME

# ==============================
# Theme Configuration
# ==============================
BG_MAIN   = THEME["bg_main"]
BG_PANEL  = THEME["bg_panel"]
BG_CARD   = THEME["bg_card"]
ACCENT    = THEME["accent"]
GLOW      = THEME["glow"]
TEXT_MAIN = THEME["text_main"]
TEXT_MUTED= THEME["text_muted"]
ERROR     = THEME["error"]

FONT_TITLE = ("Segoe UI", 26, "bold")
FONT_SUB = ("Segoe UI", 12)
FONT_BTN = ("Segoe UI", 11, "bold")
FONT_SMALL = ("Segoe UI", 10)

# ==============================
# Main App
# ==============================
class DiagLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DiagAutoClinicOS Launcher")
        self.geometry("1366x768")
        self.configure(bg=BG_MAIN)
        self.resizable(False, False)

        # Animation variables
        self.scan_line_y = 0
        self.glow_intensity = 0
        self.animating = False

        self.build_background()
        self.build_top()
        self.build_dashboard()
        self.build_bottom()
        
        # Start health monitoring after UI is built
        self.after(1000, self.start_health_monitoring)
        
        self.start_animations()

    def build_background(self):
        """Create futuristic animated background"""
        self.bg_canvas = tk.Canvas(self, bg=BG_MAIN, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Create gradient effect with rectangles
        for i in range(0, 768, 10):
            color_intensity = int(46 + (i / 768) * 20)  # Vary teal intensity
            color = f"#{color_intensity:02x}{color_intensity+10:02x}{color_intensity-5:02x}"
            self.bg_canvas.create_rectangle(0, i, 1366, i+10, fill=color, outline="")

        # Scanning line
        self.scan_line = self.bg_canvas.create_line(0, 0, 1366, 0, fill=GLOW, width=2)

        # Corner accents
        self.bg_canvas.create_oval(1316, 10, 1356, 50, fill=GLOW, outline="")
        self.bg_canvas.create_oval(10, 718, 50, 758, fill=GLOW, outline="")

    def start_animations(self):
        """Start background animations"""
        def animate():
            while True:
                self.scan_line_y = (self.scan_line_y + 2) % 768
                self.bg_canvas.coords(self.scan_line, 0, self.scan_line_y, 1366, self.scan_line_y)
                self.glow_intensity = (self.glow_intensity + 5) % 100
                time.sleep(0.05)
        thread = threading.Thread(target=animate, daemon=True)
        thread.start()

    def build_top(self):
        top = tk.Frame(self, bg=BG_MAIN, height=120)
        top.pack(fill="x", pady=(10, 0))

        # Calculate center positions based on window width (1366px)
        title_width = 300  # Approximate width of "DiagAutoClinicOS" text
        subtitle_width = 300  # Approximate width of subtitle text
        center_x = (1366 - title_width) // 2
        subtitle_center_x = (1366 - subtitle_width) // 2

        title = tk.Label(
            top,
            text="DiagAutoClinicOS",
            fg=TEXT_MAIN,
            bg=BG_MAIN,
            font=FONT_TITLE
        )
        title.place(x=center_x, y=10)

        subtitle = tk.Label(
            top,
            text="Where Mechanics Meet Future Intelligence",
            fg=TEXT_MUTED,
            bg=BG_MAIN,
            font=FONT_SUB
        )
        subtitle.place(x=subtitle_center_x, y=70)

    def card(self, parent, title_text, body_text):
        # Outer glow container with enhanced bubble effect
        glow_container = tk.Frame(parent, bg=GLOW, width=314, height=144)
        glow_container.pack_propagate(False)

        # Middle shadow layer for depth
        shadow_layer = tk.Frame(glow_container, bg="#061816", width=310, height=140)
        shadow_layer.pack_propagate(False)
        shadow_layer.place(x=2, y=2)

        # Inner shadow for more depth
        inner_shadow = tk.Frame(shadow_layer, bg="#08211F", width=306, height=136)
        inner_shadow.pack_propagate(False)
        inner_shadow.place(x=2, y=2)

        # Main card frame with bubble effect
        card_frame = tk.Frame(inner_shadow, bg=BG_CARD, width=302, height=132, relief="raised", borderwidth=1)
        card_frame.pack_propagate(False)
        card_frame.place(x=2, y=2)

        # Glossy overlay effect (top half lighter)
        gloss_top = tk.Frame(card_frame, bg="#1A5B54", height=66)
        gloss_top.place(x=0, y=0, relwidth=1)

        # Content container
        content = tk.Frame(card_frame, bg=BG_CARD)
        content.place(x=0, y=0, relwidth=1, relheight=1)

        # Header with pulsing status indicator
        header_frame = tk.Frame(content, bg=BG_CARD, height=40)
        header_frame.pack(fill="x", padx=18, pady=(15, 5))
        header_frame.pack_propagate(False)

        # Animated status dot
        status_canvas = tk.Canvas(header_frame, bg=BG_CARD, width=12, height=12, highlightthickness=0)
        status_canvas.place(x=0, y=10)
        status_dot = status_canvas.create_oval(2, 2, 10, 10, fill=GLOW, outline=ACCENT, width=1)

        # Title with futuristic font
        title = tk.Label(
            header_frame,
            text=title_text,
            fg=TEXT_MAIN,
            bg=BG_CARD,
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        )
        title.place(x=20, y=5)

        # Holographic separator with gradient effect
        sep_frame = tk.Frame(content, bg=BG_CARD, height=2)
        sep_frame.pack(fill="x", padx=18, pady=(0, 8))
        sep_canvas = tk.Canvas(sep_frame, bg=BG_CARD, height=2, highlightthickness=0)
        sep_canvas.pack(fill="x")
        sep_canvas.create_line(0, 1, 300, 1, fill=GLOW, width=1)

        # Description text
        body_frame = tk.Frame(content, bg=BG_CARD, height=40)
        body_frame.pack(fill="x", padx=18, pady=(0, 10))
        body_frame.pack_propagate(False)

        body = tk.Label(
            body_frame,
            text=body_text,
            fg=TEXT_MUTED,
            bg=BG_CARD,
            font=("Segoe UI", 10),
            anchor="w",
            justify="left"
        )
        body.place(x=0, y=5)

        # Bottom indicator bar with pulse effect
        indicator_bar = tk.Frame(content, bg=BG_CARD, height=25)
        indicator_bar.pack(fill="x", padx=18, pady=(0, 8))

        # Mini pulse indicators
        pulse_canvas = tk.Canvas(indicator_bar, bg=BG_CARD, height=10, highlightthickness=0)
        pulse_canvas.pack(anchor="w")
        
        pulse_dots = []
        for i in range(5):
            dot = pulse_canvas.create_oval(i*12, 2, i*12+6, 8, fill=GLOW, outline="")
            pulse_dots.append(dot)

        # Enhanced hover effects with smooth transitions
        def on_enter(e):
            glow_container.config(bg=ACCENT, width=318, height=148)
            shadow_layer.place(x=1, y=1)
            gloss_top.config(bg="#22766D")
            title.config(fg=ACCENT)
            body.config(fg=TEXT_MAIN)
            status_canvas.itemconfig(status_dot, fill=ACCENT, outline=ACCENT, width=2)
            
            # Pulse effect on indicators
            for i, dot in enumerate(pulse_dots):
                pulse_canvas.itemconfig(dot, fill=ACCENT)
                pulse_canvas.coords(dot, i*12, 0, i*12+8, 10)

        def on_leave(e):
            glow_container.config(bg=GLOW, width=314, height=144)
            shadow_layer.place(x=2, y=2)
            gloss_top.config(bg="#1A5B54")
            title.config(fg=TEXT_MAIN)
            body.config(fg=TEXT_MUTED)
            status_canvas.itemconfig(status_dot, fill=GLOW, outline=ACCENT, width=1)
            
            # Reset indicators
            for i, dot in enumerate(pulse_dots):
                pulse_canvas.itemconfig(dot, fill=GLOW)
                pulse_canvas.coords(dot, i*12, 2, i*12+6, 8)

        # Bind hover only to the outer container
        glow_container.bind("<Enter>", on_enter)
        glow_container.bind("<Leave>", on_leave)

        # Store canvas references for animation
        glow_container.status_canvas = status_canvas
        glow_container.status_dot = status_dot
        glow_container.pulse_canvas = pulse_canvas
        glow_container.pulse_dots = pulse_dots

        return glow_container

    def build_dashboard(self):
        mid = tk.Frame(self, bg=BG_MAIN)
        mid.pack(expand=True, fill="both", pady=20)

        row1 = tk.Frame(mid, bg=BG_MAIN)
        row1.pack(pady=15)
        
        # Initialize suite status tracking
        self.suite_status = {
            "AutoDiag": "Ready",
            "AutoECU": "Ready", 
            "AutoKey": "Ready"
        }
        
        # Main Suite Cards - Top Priority
        self.autodiag_card = self.card(row1, "Vehicle Diagnostics", "Scan faults & live data")
        self.autodiag_card.pack(side="left", padx=15)
        self.bind_card_launch(self.autodiag_card, "AutoDiag")
        
        self.autoecu_card = self.card(row1, "ECU Programming", "Flash & coding tools")
        self.autoecu_card.pack(side="left", padx=15)
        self.bind_card_launch(self.autoecu_card, "AutoECU")
        
        self.autokey_card = self.card(row1, "Security & IMMO", "Key programming & sync")
        self.autokey_card.pack(side="left", padx=15)
        self.bind_card_launch(self.autokey_card, "AutoKey")
        
        row2 = tk.Frame(mid, bg=BG_MAIN)
        row2.pack(pady=15)
        
        # Additional Suite Cards
        sensor_card = self.card(row2, "Sensor Monitor", "Live sensor graphing")
        sensor_card.pack(side="left", padx=15)
        self.bind_card_launch(sensor_card, "AutoDiag")
        
        health_card = self.card(row2, "System Health", "Suite diagnostics status")
        health_card.pack(side="left", padx=15)
        self.bind_card_launch(health_card, "AutoDiag")
        
        reset_card = self.card(row2, "Service Reset", "Oil / DPF / EPB resets")
        reset_card.pack(side="left", padx=15)
        self.bind_card_launch(reset_card, "AutoDiag")
    
    def bind_card_launch(self, card_widget, suite_name):
        """Bind launch functionality to entire card and all its children"""
        def launch_handler(e):
            self.launch_suite(suite_name)
        
        # Bind to the card and all its children recursively
        def bind_recursive(widget):
            widget.bind("<Button-1>", launch_handler)
            for child in widget.winfo_children():
                bind_recursive(child)
        
        bind_recursive(card_widget)

    def build_bottom(self):
        """Build futuristic status bar at bottom"""
        bottom = tk.Frame(self, bg=BG_MAIN, height=70)
        bottom.pack(side="bottom", fill="x", pady=(0, 15))

        # Create holographic status container
        status_container = tk.Frame(bottom, bg="#061816", height=50)
        status_container.pack(fill="x", padx=30)
        status_container.pack_propagate(False)

        # Inner glow frame
        inner_glow = tk.Frame(status_container, bg=GLOW, height=48)
        inner_glow.pack(fill="x", padx=1, pady=1)
        inner_glow.pack_propagate(False)

        # Main status bar
        status_bar = tk.Frame(inner_glow, bg=BG_CARD, height=46)
        status_bar.pack(fill="x", padx=1, pady=1)
        status_bar.pack_propagate(False)

        # Left section - System status
        left_section = tk.Frame(status_bar, bg=BG_CARD)
        left_section.pack(side="left", padx=25, pady=13)

        # Pulsing status indicator
        self.status_canvas = tk.Canvas(left_section, bg=BG_CARD, width=16, height=16, highlightthickness=0)
        self.status_canvas.pack(side="left", padx=(0, 10))
        self.status_indicator = self.status_canvas.create_oval(3, 3, 13, 13, fill=GLOW, outline=ACCENT, width=2)

        # Status text
        self.status_label = tk.Label(
            left_section,
            text="● SYSTEM READY",
            fg=GLOW,
            bg=BG_CARD,
            font=("Segoe UI", 10, "bold")
        )
        self.status_label.pack(side="left")

        # Center section - Suite status
        center_section = tk.Frame(status_bar, bg=BG_CARD)
        center_section.pack(side="left", expand=True, padx=30)

        suites = ["AutoDiag", "AutoECU", "AutoKey"]
        self.suite_indicators = {}
        
        for suite in suites:
            suite_frame = tk.Frame(center_section, bg=BG_CARD)
            suite_frame.pack(side="left", padx=12)

            # Mini indicator dot
            indicator_canvas = tk.Canvas(suite_frame, bg=BG_CARD, width=8, height=8, highlightthickness=0)
            indicator_canvas.pack(side="left", padx=(0, 5))
            dot = indicator_canvas.create_oval(1, 1, 7, 7, fill=TEXT_MUTED, outline="")
            
            # Suite label
            label = tk.Label(
                suite_frame,
                text=suite,
                fg=TEXT_MUTED,
                bg=BG_CARD,
                font=("Segoe UI", 9)
            )
            label.pack(side="left")
            
            self.suite_indicators[suite] = (indicator_canvas, dot, label)

        # Right section - Version/Time
        right_section = tk.Frame(status_bar, bg=BG_CARD)
        right_section.pack(side="right", padx=25, pady=13)

        version_label = tk.Label(
            right_section,
            text="v1.0.0 | DACOS",
            fg=TEXT_MUTED,
            bg=BG_CARD,
            font=("Segoe UI", 9)
        )
        version_label.pack()

        # Start status animation
        self.animate_status_pulse()

    def animate_status_pulse(self):
        """Animate the status indicator pulse"""
        def pulse():
            colors = [GLOW, ACCENT, GLOW]
            sizes = [(3, 3, 13, 13), (2, 2, 14, 14), (3, 3, 13, 13)]
            idx = 0
            
            while True:
                try:
                    self.status_canvas.itemconfig(self.status_indicator, fill=colors[idx % 3])
                    self.status_canvas.coords(self.status_indicator, *sizes[idx % 3])
                    idx += 1
                    time.sleep(0.8)
                except:
                    break
        
        pulse_thread = threading.Thread(target=pulse, daemon=True)
        pulse_thread.start()

    def launch_suite(self, suite_name):
        """Launch a specific diagnostic suite"""
        self.status_label.config(text=f"● LAUNCHING {suite_name.upper()}...", fg=ACCENT)
        
        # Update suite status indicator
        if suite_name in self.suite_indicators:
            canvas, dot, label = self.suite_indicators[suite_name]
            canvas.itemconfig(dot, fill=ACCENT)
            label.config(fg=ACCENT)
        
        try:
            import subprocess
            import sys
            from pathlib import Path

            # Get the path to the specific suite main.py
            project_root = Path(__file__).resolve().parent
            suite_path = project_root / suite_name / 'main.py'

            if not suite_path.exists():
                raise FileNotFoundError(f"{suite_name}/main.py not found at: {suite_path}")

            # Try multiple Python executables in order of preference
            python_executables = [
                sys.executable,  # Current Python interpreter
                r"C:\Python312\python.exe",
                r"C:\Python310\python.exe",
                r"C:\Users\DACOS\AppData\Local\Programs\Python\Python312\python.exe",
                r"C:\Users\DACOS\AppData\Local\Microsoft\WindowsApps\python.exe",
                "python3",
                "python"
            ]

            launched = False
            last_error = None
            
            for python_exe in python_executables:
                try:
                    # Check if python executable exists (skip 'python' and 'python3' system commands)
                    if python_exe not in ["python", "python3"]:
                        if not Path(python_exe).exists():
                            continue
                    
                    # Launch the suite in a new process
                    process = subprocess.Popen(
                        [python_exe, str(suite_path)],
                        cwd=str(project_root),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
                    )
                    
                    # Give it a moment to start
                    self.after(500, lambda: self.check_suite_launched(process, suite_name, python_exe))
                    launched = True
                    break
                    
                except Exception as e:
                    last_error = f"Failed with {python_exe}: {str(e)}"
                    continue

            if not launched:
                raise Exception(last_error or "No suitable Python executable found")

        except FileNotFoundError as e:
            error_msg = f"Suite not found:\n\n{str(e)}\n\nPlease ensure {suite_name} folder exists with main.py"
            messagebox.showerror("Launch Error", error_msg)
            
            if suite_name in self.suite_indicators:
                canvas, dot, label = self.suite_indicators[suite_name]
                canvas.itemconfig(dot, fill=ERROR)
                label.config(fg=ERROR)
                
            self.status_label.config(text=f"● {suite_name} NOT FOUND", fg=ERROR)
            
        except Exception as e:
            error_msg = f"Failed to launch {suite_name}:\n\n{str(e)}\n\nPlease check:\n1. Python is installed\n2. PyQt6 is installed (pip install PyQt6)\n3. All dependencies are available"
            messagebox.showerror("Launch Error", error_msg)
            
            if suite_name in self.suite_indicators:
                canvas, dot, label = self.suite_indicators[suite_name]
                canvas.itemconfig(dot, fill=ERROR)
                label.config(fg=ERROR)
                
            self.status_label.config(text=f"● {suite_name} LAUNCH FAILED", fg=ERROR)
    
    def check_suite_launched(self, process, suite_name, python_exe):
        """Check if suite launched successfully"""
        try:
            # Check if process is still running
            if process.poll() is None:
                # Process is running
                messagebox.showinfo("Success", f"{suite_name} launched successfully!\n\nUsing: {python_exe}")
                
                if suite_name in self.suite_indicators:
                    canvas, dot, label = self.suite_indicators[suite_name]
                    canvas.itemconfig(dot, fill=THEME["success"])
                    label.config(fg=THEME["success"])
                    
                self.status_label.config(text=f"● {suite_name} ACTIVE", fg=THEME["success"])
            else:
                # Process ended immediately - likely an error
                stdout, stderr = process.communicate()
                error_msg = stderr if stderr else stdout if stdout else "Process terminated immediately"
                
                messagebox.showerror("Launch Failed", 
                                   f"{suite_name} failed to start:\n\n{error_msg}\n\n"
                                   f"Check that PyQt6 is installed:\n"
                                   f"pip install PyQt6")
                
                if suite_name in self.suite_indicators:
                    canvas, dot, label = self.suite_indicators[suite_name]
                    canvas.itemconfig(dot, fill=ERROR)
                    label.config(fg=ERROR)
                    
                self.status_label.config(text=f"● {suite_name} CRASHED", fg=ERROR)
        except Exception as e:
            # Error checking status
            if suite_name in self.suite_indicators:
                canvas, dot, label = self.suite_indicators[suite_name]
                canvas.itemconfig(dot, fill=TEXT_MUTED)
                label.config(fg=TEXT_MUTED)
            
            self.status_label.config(text=f"● {suite_name} STATUS UNKNOWN", fg=TEXT_MUTED)
    
    def launch_main(self):
        """Legacy method - redirects to AutoDiag"""
        self.launch_suite("AutoDiag")
    
    def on_card_hover(self, card_type, entering):
        """Legacy hover handler - no longer needed with new card system"""
        pass

    def start_health_monitoring(self):
        """Start monitoring system health for all suites"""
        def monitor_health():
            while True:
                try:
                    # Check each suite's status
                    for suite in ["AutoDiag", "AutoECU", "AutoKey"]:
                        if suite in self.suite_indicators:
                            suite_path = Path(__file__).resolve().parent / suite / 'main.py'
                            canvas, dot, label = self.suite_indicators[suite]
                            
                            if suite_path.exists():
                                # Suite exists and ready - set to ready if not already running
                                current_color = canvas.itemcget(dot, "fill")
                                if current_color == TEXT_MUTED:
                                    canvas.itemconfig(dot, fill=GLOW)
                                    label.config(fg=GLOW)
                            else:
                                # Suite missing
                                canvas.itemconfig(dot, fill=ERROR)
                                label.config(fg=ERROR)
                    
                    time.sleep(5)
                except:
                    break
        
        monitor_thread = threading.Thread(target=monitor_health, daemon=True)
        monitor_thread.start()

    def update_health_indicators(self):
        """Update visual health indicators for suites"""
        # This method is no longer needed as build_bottom handles indicators
        pass
    
    def get_suite_info(self, suite_name):
        """Get information about a suite"""
        suite_info = {
            "AutoDiag": {
                "full_name": "AutoDiag Pro",
                "description": "Professional Vehicle Diagnostics",
                "requirements": ["PyQt6", "shared modules"]
            },
            "AutoECU": {
                "full_name": "AutoECU Pro", 
                "description": "ECU Programming & Flash Tools",
                "requirements": ["PyQt6", "shared modules"]
            },
            "AutoKey": {
                "full_name": "AutoKey Pro",
                "description": "Key Programming & IMMO",
                "requirements": ["PyQt6", "shared modules"]
            }
        }
        return suite_info.get(suite_name, {})


if __name__ == "__main__":
    app = DiagLauncher()
    app.mainloop()