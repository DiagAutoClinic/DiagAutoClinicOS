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
from tkinter import ttk
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
        self.geometry("1000x650")
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
        self.start_animations()

    def build_background(self):
        """Create futuristic animated background"""
        self.bg_canvas = tk.Canvas(self, bg=BG_MAIN, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Create gradient effect with rectangles
        for i in range(0, 650, 10):
            color_intensity = int(46 + (i / 650) * 20)  # Vary teal intensity
            color = f"#{color_intensity:02x}{color_intensity+10:02x}{color_intensity-5:02x}"
            self.bg_canvas.create_rectangle(0, i, 1000, i+10, fill=color, outline="")

        # Scanning line
        self.scan_line = self.bg_canvas.create_line(0, 0, 1000, 0, fill=GLOW, width=2)

        # Corner accents
        self.bg_canvas.create_oval(950, 10, 990, 50, fill=GLOW, outline="")
        self.bg_canvas.create_oval(10, 600, 50, 640, fill=GLOW, outline="")

    def start_animations(self):
        """Start background animations"""
        def animate():
            while True:
                self.scan_line_y = (self.scan_line_y + 2) % 650
                self.bg_canvas.coords(self.scan_line, 0, self.scan_line_y, 1000, self.scan_line_y)
                self.glow_intensity = (self.glow_intensity + 5) % 100
                time.sleep(0.05)
        thread = threading.Thread(target=animate, daemon=True)
        thread.start()

    def build_top(self):
        top = tk.Frame(self, bg=BG_MAIN, height=100)
        top.pack(fill="x")

        title = tk.Label(
            top,
            text="DiagAutoClinicOS",
            fg=TEXT_MAIN,
            bg=BG_MAIN,
            font=FONT_TITLE
        )
        title.place(x=30, y=25)

        subtitle = tk.Label(
            top,
            text="Where Mechanics Meet Future Intelligence",
            fg=TEXT_MUTED,
            bg=BG_MAIN,
            font=FONT_SUB
        )
        subtitle.place(x=35, y=65)

    def card(self, parent, title_text, body_text):
        # Outer frame for shadow effect
        shadow = tk.Frame(parent, bg="#0A2927", width=290, height=130)
        shadow.pack_propagate(False)

        # Inner card with glassmorphic effect
        card = tk.Frame(shadow, bg=BG_CARD, width=280, height=120, relief="raised", bd=2)
        card.pack_propagate(False)
        card.place(x=5, y=5)

        # Glow border
        border = tk.Frame(card, bg=GLOW, width=278, height=118)
        border.pack_propagate(False)
        border.place(x=1, y=1)

        # Content frame
        content = tk.Frame(border, bg=BG_CARD, width=276, height=116)
        content.pack_propagate(False)
        content.place(x=1, y=1)

        title = tk.Label(
            content,
            text=title_text,
            fg=TEXT_MAIN,
            bg=BG_CARD,
            font=("Segoe UI", 12, "bold")
        )
        title.pack(anchor="w", padx=15, pady=(15, 5))

        body = tk.Label(
            content,
            text=body_text,
            fg=TEXT_MUTED,
            bg=BG_CARD,
            font=FONT_SMALL,
            justify="left"
        )
        body.pack(anchor="w", padx=15)

        # Hover effects
        def on_enter(e):
            card.config(relief="sunken")
            border.config(bg=ACCENT)

        def on_leave(e):
            card.config(relief="raised")
            border.config(bg=GLOW)

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        return shadow

    def build_dashboard(self):
        mid = tk.Frame(self, bg=BG_MAIN)
        mid.pack(expand=True, fill="both", pady=10)

        row1 = tk.Frame(mid, bg=BG_MAIN)
        row1.pack(pady=10)

        self.card(row1, "Vehicle Diagnostics", "Scan faults & live data").pack(side="left", padx=15)
        self.card(row1, "ECU Programming", "Flash & coding tools").pack(side="left", padx=15)
        self.card(row1, "Service Reset", "Oil / DPF / EPB resets").pack(side="left", padx=15)

        row2 = tk.Frame(mid, bg=BG_MAIN)
        row2.pack(pady=10)

        self.card(row2, "Security & IMMO", "Key programming & sync").pack(side="left", padx=15)
        self.card(row2, "Sensor Monitor", "Live sensor graphing").pack(side="left", padx=15)
        self.card(row2, "System Health", "Suite diagnostics status").pack(side="left", padx=15)

    def build_bottom(self):
        bottom = tk.Frame(self, bg=BG_MAIN, height=80)
        bottom.pack(fill="x")

        # Button container for glow effect
        btn_container = tk.Frame(bottom, bg=BG_MAIN)
        btn_container.pack(pady=15)

        # Glow frame
        glow_frame = tk.Frame(btn_container, bg=GLOW, width=310, height=52)
        glow_frame.pack_propagate(False)
        glow_frame.pack()

        # Button
        self.launch_btn = tk.Button(
            glow_frame,
            text="▶ LAUNCH DiagAutoClinicOS",
            bg=ACCENT,
            fg="#002F2C",
            font=FONT_BTN,
            width=28,
            height=1,
            bd=0,
            relief="raised",
            command=self.launch_main
        )
        self.launch_btn.pack(pady=2, padx=2)

        # Hover effects for button
        def btn_enter(e):
            glow_frame.config(bg=ACCENT)
            self.launch_btn.config(bg="#1AE5B1", relief="sunken")

        def btn_leave(e):
            glow_frame.config(bg=GLOW)
            self.launch_btn.config(bg=ACCENT, relief="raised")

        self.launch_btn.bind("<Enter>", btn_enter)
        self.launch_btn.bind("<Leave>", btn_leave)

        # Status indicator
        self.status_label = tk.Label(bottom, text="● SYSTEM READY", fg=GLOW, bg=BG_MAIN, font=FONT_SMALL)
        self.status_label.pack(side="bottom", pady=5)

    def launch_main(self):
        # Animate launch sequence
        self.status_label.config(text="● INITIALIZING...", fg=ACCENT)
        self.launch_btn.config(state="disabled", text="LAUNCHING...")
        self.update()

        # Simulate loading
        for i in range(10):
            self.status_label.config(text=f"● LOADING... {i*10}%")
            time.sleep(0.1)
            self.update()

        self.status_label.config(text="● LAUNCH COMPLETE", fg=TEXT_MAIN)

        # Launch the actual AutoDiag application
        try:
            import subprocess
            import sys
            import os

            # Get the path to AutoDiag/main.py
            autodiag_path = os.path.join(os.path.dirname(__file__), 'AutoDiag', 'main.py')

            # Launch the PyQt6 application
            subprocess.Popen([sys.executable, autodiag_path])

        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to launch AutoDiag: {e}")
            # Re-open launcher if launch failed
            DiagLauncher().mainloop()


if __name__ == "__main__":
    app = DiagLauncher()
    app.mainloop()