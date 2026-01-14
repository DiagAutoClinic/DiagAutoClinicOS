"""
DACOS Gemini Exclusive Theme
"Starlight Nebula" - AI Powered Experience
Location: shared/themes/gemini_theme.py
"""

import logging

logger = logging.getLogger(__name__)

# ===== GEMINI EXCLUSIVE PALETTE =====
DACOS_THEME = {
    "bg_main": "#0b0f19",      # Deep Space Blue
    "bg_panel": "rgba(20, 24, 45, 0.85)", # Nebula Blue
    "bg_card": "rgba(30, 35, 60, 0.6)",   # Star Field
    "accent": "#8860f4",       # Gemini Violet
    "accent_hover": "#a485ff", # Bright Violet
    "secondary": "#4fabff",    # Gemini Blue
    "glow": "#c6a6ff",         # Starlight Glow
    "text_main": "#ffffff",    # Star White
    "text_muted": "#a0aabf",   # Space Grey
    "border": "#4a4560",       # Nebula Border
    "border_active": "#8860f4",# Active Violet
    "error": "#ff5252",        # Red Giant
    "success": "#69f0ae",      # Nebula Green
    "warning": "#ffd740",      # Star Yellow
    "info": "#40c4ff"          # Blue Dwarf
}

DACOS_STYLESHEET = f"""
/* =====================================================================
   DACOS Modern Layout - Gemini Starlight
   Standardized DACOS Experience
   ===================================================================== */

QMainWindow, QDialog {{
    background-color: {DACOS_THEME['bg_main']};
    color: {DACOS_THEME['text_main']};
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 10pt;
}}

QWidget {{
    background-color: transparent;
    color: {DACOS_THEME['text_main']};
    selection-background-color: {DACOS_THEME['accent']};
    selection-color: #000000;
}}

/* ===== CARDS ===== */
QFrame[class="glass-card"], QWidget[class="glass-card"] {{
    background-color: {DACOS_THEME['bg_card']};
    border: 1px solid {DACOS_THEME['border']};
    border-radius: 12px;
}}

/* ===== BUTTONS ===== */
QPushButton {{
    background-color: rgba(136, 96, 244, 0.1);
    color: {DACOS_THEME['accent']};
    border: 1px solid {DACOS_THEME['border']};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: rgba(136, 96, 244, 0.2);
    border: 1px solid {DACOS_THEME['accent']};
    color: #FFFFFF;
}}

QPushButton:pressed {{
    background-color: {DACOS_THEME['accent']};
    color: #000000;
}}

QPushButton[class="primary"] {{
    background-color: {DACOS_THEME['accent']};
    color: #000000;
    border: none;
}}

QPushButton[class="primary"]:hover {{
    background-color: {DACOS_THEME['accent_hover']};
}}

/* ===== INPUTS ===== */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox {{
    background-color: rgba(0, 0, 0, 0.3);
    border: 1px solid {DACOS_THEME['border']};
    border-radius: 4px;
    padding: 8px;
    color: {DACOS_THEME['text_main']};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border: 1px solid {DACOS_THEME['accent']};
    background-color: rgba(136, 96, 244, 0.05);
}}

/* ===== TABS ===== */
QTabWidget::pane {{
    border: 1px solid {DACOS_THEME['border']};
    background: {DACOS_THEME['bg_panel']};
    border-radius: 4px;
}}

QTabBar::tab {{
    background: rgba(0, 0, 0, 0.2);
    color: {DACOS_THEME['text_muted']};
    padding: 10px 20px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}}

QTabBar::tab:selected {{
    background: {DACOS_THEME['bg_panel']};
    color: {DACOS_THEME['accent']};
    border-bottom: 2px solid {DACOS_THEME['accent']};
}}

/* ===== SCROLLBARS ===== */
QScrollBar:vertical {{
    background: #1e1e1e;
    width: 12px;
}}

QScrollBar::handle:vertical {{
    background: #424242;
    border-radius: 4px;
    border: 1px solid {DACOS_THEME['border']};
}}

QScrollBar::handle:vertical:hover {{
    background: {DACOS_THEME['accent']};
}}

QScrollBar:add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}
"""

def apply_theme(app):
    try:
        app.setStyle('Fusion')
        app.setStyleSheet(DACOS_STYLESHEET)
        logger.info("DACOS Gemini Theme applied")
        return True
    except Exception as e:
        logger.error(f"Failed to apply DACOS Gemini Theme: {e}")
        return False
