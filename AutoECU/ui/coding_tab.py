#!/usr/bin/env python3
"""
AutoECU - Coding Tab
Separate tab implementation for easier customization
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QScrollArea)
from PyQt6.QtCore import Qt

# Import color function
try:
    from shared.themes.dacos_theme import get_dacos_color
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

class CodingTab:
    """
    Coding Tab for module coding and adaptations.
    """

    def __init__(self, parent_window):
        """
        Initialize the Coding Tab.

        Args:
            parent_window: The main application window instance
        """
        self.parent = parent_window

    def create_tab(self) -> tuple[QWidget, str]:
        """
        Create the coding tab and return the widget.

        Returns:
            tuple: (tab_widget, tab_title)
        """
        coding_tab = QWidget()
        layout = QVBoxLayout(coding_tab)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "glass-card")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)

        header_label = QLabel("🔐 Module Coding & Adaptations")
        header_label.setStyleSheet(f"color: {get_dacos_color('accent')}; font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(header_label)

        # Content
        content_frame = QFrame()
        content_frame.setProperty("class", "glass-card")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)

        placeholder = QLabel("🚧 Module coding interface under development\n\n"
                            "This tab will include:\n"
                            "• Long coding editor\n"
                            "• Adaptation values\n"
                            "• Module configuration\n"
                            "• Security access")
        placeholder.setStyleSheet(f"color: {get_dacos_color('text_muted')}; font-size: 12pt; line-height: 1.8;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)

        content_layout.addWidget(placeholder)

        # === Final layout with scroll area (important for small screens) ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.addWidget(header_frame)
        content_layout.addWidget(content_frame)
        content_layout.addStretch()

        scroll.setWidget(content_widget)

        layout.addWidget(scroll)

        return coding_tab, "🔐 Coding"