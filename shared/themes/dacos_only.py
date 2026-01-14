"""
DACOS Only Themes
Location: shared/themes/dacos_only.py
"""

import logging

logger = logging.getLogger(__name__)

# ===== PALETTES =====

PALETTE_VOID = {
    "bg_main": "#041C20",
    "bg_panel": "#06242A",
    "bg_card": "#06242A",
    "accent": "#00E5FF",
    "accent_hover": "#8FEFFF",
    "text_main": "#E6F7FA",
    "text_muted": "#8FEFFF",
    "border": "#0E6F78"
}

PALETTE_WHITE = {
    "bg_main": "#FFFFFF",
    "bg_panel": "#F7FAFB",
    "bg_card": "#FFFFFF",
    "accent": "#00E5FF",
    "accent_hover": "#7CF3FF",
    "text_main": "#0B0E11",
    "text_muted": "#4A5560",
    "border": "#CDEFF4"
}

PALETTE_LATTICE = {
    "bg_main": "#F6F8F9",
    "bg_panel": "#FFFFFF",
    "bg_card": "#FFFFFF",
    "accent": "#00E5FF",
    "accent_hover": "#00BFD6",
    "text_main": "#101417",
    "text_muted": "rgba(16,20,23,0.75)",
    "border": "#DCEEF2"
}

# Default for external access
DACOS_THEME = PALETTE_VOID

def get_stylesheet(palette):
    # Calculate simple RGBA for accents if needed, or just use hardcoded low opacity
    # For simplicity in this template, we use the hex codes directly or generic RGBA
    return f"""
/* =====================================================================
   DACOS Modern Layout
   Standardized DACOS Experience
   ===================================================================== */

QMainWindow, QDialog {{
    background-color: {palette['bg_main']};
    color: {palette['text_main']};
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 10pt;
}}

QWidget {{
    background-color: transparent;
    color: {palette['text_main']};
    selection-background-color: {palette['accent']};
    selection-color: #000000;
}}

/* ===== CARDS ===== */
QFrame[class="glass-card"], QWidget[class="glass-card"] {{
    background-color: {palette['bg_card']};
    border: 1px solid {palette['border']};
    border-radius: 12px;
}}

/* ===== BUTTONS ===== */
QPushButton {{
    background-color: rgba(0, 229, 255, 0.1); /* Generic Cyan Tint */
    color: {palette['accent']};
    border: 1px solid {palette['border']};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: rgba(0, 229, 255, 0.2);
    border: 1px solid {palette['accent']};
    color: {palette['text_main']}; 
}}

QPushButton:pressed {{
    background-color: {palette['accent']};
    color: #000000;
}}

QPushButton[class="primary"] {{
    background-color: {palette['accent']};
    color: #000000;
    border: none;
}}

QPushButton[class="primary"]:hover {{
    background-color: {palette['accent_hover']};
}}

/* ===== INPUTS ===== */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox {{
    background-color: rgba(0, 0, 0, 0.05);
    border: 1px solid {palette['border']};
    border-radius: 4px;
    padding: 8px;
    color: {palette['text_main']};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border: 1px solid {palette['accent']};
    background-color: rgba(0, 229, 255, 0.05);
}}

/* ===== TABS ===== */
QTabWidget::pane {{
    border: 1px solid {palette['border']};
    background: {palette['bg_panel']};
    border-radius: 4px;
}}

QTabBar::tab {{
    background: rgba(0, 0, 0, 0.05);
    color: {palette['text_muted']};
    padding: 10px 20px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}}

QTabBar::tab:selected {{
    background: {palette['bg_panel']};
    color: {palette['accent']};
    border-bottom: 2px solid {palette['accent']};
}}

/* ===== SCROLLBARS ===== */
QScrollBar:vertical {{
    background: {palette['bg_main']};
    width: 12px;
}}

QScrollBar::handle:vertical {{
    background: {palette['border']};
    border-radius: 4px;
    border: 1px solid {palette['border']};
}}

QScrollBar::handle:vertical:hover {{
    background: {palette['accent']};
}}

QScrollBar:add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}
"""

def apply_theme(app, theme_name):
    try:
        app.setStyle('Fusion')
        
        if theme_name == "DACOS Instrument White":
            style = get_stylesheet(PALETTE_WHITE)
        elif theme_name == "DACOS Cognitive Lattice":
            style = get_stylesheet(PALETTE_LATTICE)
        else:
            # Default to Deep Teal Void
            style = get_stylesheet(PALETTE_VOID)
            
        app.setStyleSheet(style)
        logger.info(f"{theme_name} applied successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to apply {theme_name}: {e}")
        return False

DACOS_STYLESHEET = get_stylesheet(DACOS_THEME)
