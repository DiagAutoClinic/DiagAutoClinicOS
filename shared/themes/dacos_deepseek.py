"""
DACOS DeepSeek Themes
Location: shared/themes/dacos_deepseek.py
"""

import logging

logger = logging.getLogger(__name__)

# ===== PALETTES =====

PALETTE_NEON = {
    "bg_main": "#0A1A1A",
    "bg_panel": "#0D2323",
    "bg_card": "#0D2323",
    "accent": "#21F5C1",
    "accent_hover": "#2AF5D1",
    "text_main": "#E8F4F2",
    "text_muted": "#9ED9CF",
    "border": "#21F5C1"
}

PALETTE_MATRIX = {
    "bg_main": "#081010",
    "bg_panel": "#0A1414",
    "bg_card": "#082020",
    "accent": "#00FFCC",
    "accent_hover": "#00FFFF",
    "text_main": "#00FFCC",
    "text_muted": "rgba(0, 255, 204, 0.7)",
    "border": "#00FFCC"
}

PALETTE_EXCLUSIVE = {
    "bg_main": "#0F2B46",
    "bg_panel": "#1A365D",
    "bg_card": "#1E293B",
    "accent": "#38B2AC",
    "accent_hover": "#4FD1C5",
    "text_main": "#E2E8F0",
    "text_muted": "#CBD5E0",
    "border": "#38B2AC"
}

# Default for external access
DACOS_THEME = PALETTE_NEON

def get_stylesheet(palette):
    return f"""
/* =====================================================================
   DACOS Modern Layout - DeepSeek Edition
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
    background-color: rgba(0, 0, 0, 0.2);
    color: {palette['accent']};
    border: 1px solid {palette['border']};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: rgba(255, 255, 255, 0.1);
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
    background-color: rgba(0, 0, 0, 0.2);
    border: 1px solid {palette['border']};
    border-radius: 4px;
    padding: 8px;
    color: {palette['text_main']};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border: 1px solid {palette['accent']};
    background-color: rgba(0, 0, 0, 0.3);
}}

/* ===== TABS ===== */
QTabWidget::pane {{
    border: 1px solid {palette['border']};
    background: {palette['bg_panel']};
    border-radius: 4px;
}}

QTabBar::tab {{
    background: rgba(0, 0, 0, 0.2);
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
        
        if theme_name == "DACOS Matrix Dark":
            style = get_stylesheet(PALETTE_MATRIX)
        elif theme_name == "DACOS DeepSeek Exclusive":
            style = get_stylesheet(PALETTE_EXCLUSIVE)
        else:
            # Default to Neon Professional
            style = get_stylesheet(PALETTE_NEON)
            
        app.setStyleSheet(style)
        logger.info(f"{theme_name} applied successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to apply {theme_name}: {e}")
        return False

DACOS_STYLESHEET = get_stylesheet(DACOS_THEME)
