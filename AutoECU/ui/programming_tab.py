#!/usr/bin/env python3
"""
AutoECU - Programming Tab
Separate tab implementation for easier customization
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
                            QTextEdit, QProgressBar, QScrollArea)
from PyQt6.QtCore import Qt

# Import color function
try:
    from shared.themes.dacos_cyber_teal import get_dacos_color
except ImportError:
    # Fallback color function
    def get_dacos_color(color_name):
        DACOS_THEME = {
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
        return DACOS_THEME.get(color_name, DACOS_THEME['accent'])

class ProgrammingTab:
    """
    Programming Tab for ECU memory operations.
    """

    def __init__(self, parent_window):
        """
        Initialize the Programming Tab.

        Args:
            parent_window: The main application window instance
        """
        self.parent = parent_window
        self.hex_viewer = None
        self.prog_progress = None

    def create_tab(self) -> tuple[QWidget, str]:
        """
        Create the programming tab and return the widget.

        Returns:
            tuple: (tab_widget, tab_title)
        """
        prog_tab = QWidget()
        layout = QVBoxLayout(prog_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)

        header_label = QLabel("⚙️ ECU Programming")
        header_label.setStyleSheet(f"color: {get_dacos_color('accent')}; font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(header_label)

        # Programming controls
        prog_frame = QFrame()
        prog_frame.setProperty("class", "glass-card")
        prog_layout = QVBoxLayout(prog_frame)
        prog_layout.setSpacing(15)
        prog_layout.setContentsMargins(20, 20, 20, 20)

        # Control buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        read_btn = QPushButton("📖 Read ECU Memory")
        read_btn.setProperty("class", "primary")
        read_btn.setMinimumHeight(50)
        read_btn.clicked.connect(self.parent.read_ecu)

        write_btn = QPushButton("✍️ Write ECU Memory")
        write_btn.setProperty("class", "danger")
        write_btn.setMinimumHeight(50)
        write_btn.clicked.connect(self.parent.write_ecu)

        verify_btn = QPushButton("✅ Verify Data")
        verify_btn.setProperty("class", "success")
        verify_btn.setMinimumHeight(50)
        verify_btn.clicked.connect(self.parent.verify_ecu)

        btn_layout.addWidget(read_btn)
        btn_layout.addWidget(write_btn)
        btn_layout.addWidget(verify_btn)

        prog_layout.addLayout(btn_layout)

        # Hex viewer
        hex_label = QLabel("📄 ECU Memory View:")
        hex_label.setStyleSheet(f"color: {get_dacos_color('text_muted')}; font-weight: bold; margin-top: 10px;")

        self.hex_viewer = QTextEdit()
        self.hex_viewer.setPlaceholderText("ECU memory content will appear here...\nClick 'Read ECU Memory' to start")
        self.hex_viewer.setMinimumHeight(300)

        prog_layout.addWidget(hex_label)
        prog_layout.addWidget(self.hex_viewer)

        # Programming progress
        progress_label = QLabel("Programming Progress:")
        progress_label.setStyleSheet(f"color: {get_dacos_color('text_muted')}; font-weight: bold;")

        self.prog_progress = QProgressBar()
        self.prog_progress.setMinimumHeight(35)
        self.prog_progress.setTextVisible(True)
        self.prog_progress.setValue(0)

        prog_layout.addWidget(progress_label)
        prog_layout.addWidget(self.prog_progress)

        # === Final layout with scroll area (important for small screens) ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.addWidget(header_frame)
        content_layout.addWidget(prog_frame)
        content_layout.addStretch()

        scroll.setWidget(content_widget)

        layout.addWidget(scroll)

        return prog_tab, "⚙️ Programming"