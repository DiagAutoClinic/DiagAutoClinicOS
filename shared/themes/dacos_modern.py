"""
DACOS Modern Theme
"Cyber-Teal Horizon" - Refined Standard Edition
Location: shared/themes/dacos_modern.py
"""

import logging

logger = logging.getLogger(__name__)

# ===== DACOS MODERN PALETTE =====
DACOS_THEME = {
    "bg_main": "#050505",      # Almost Black
    "bg_panel": "rgba(5, 25, 30, 0.85)", # Deep Teal
    "bg_card": "rgba(10, 40, 45, 0.7)",  # Card Background
    "accent": "#00f2ff",       # Electric Cyan
    "accent_hover": "#80f9ff", # Light Cyan
    "glow": "#00e5ff",         # Glow
    "text_main": "#ffffff",    # White
    "text_muted": "#8bdfe6",   # Muted Cyan
    "border": "#005f66",       # Teal Border
    "border_active": "#00f2ff",# Active Border
    "error": "#ff2a6d",        # Cyber Red
    "success": "#05ffa1",      # Neon Green
    "warning": "#ffcc00",      # Amber
    "info": "#00a8ff"          # Blue
}

DACOS_STYLESHEET = f"""
/* =====================================================================
   DACOS Modern Theme - Cyber-Teal Horizon
   Standard DACOS Experience
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
    background-color: rgba(0, 242, 255, 0.1);
    color: {DACOS_THEME['accent']};
    border: 1px solid {DACOS_THEME['border']};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: rgba(0, 242, 255, 0.2);
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
    background-color: rgba(0, 242, 255, 0.05);
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

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}
"""

def apply_theme(app):
    try:
        app.setStyle('Fusion')
        app.setStyleSheet(DACOS_STYLESHEET)
        logger.info("DACOS Modern Theme applied")
        return True
    except Exception as e:
        logger.error(f"Failed to apply DACOS Modern Theme: {e}")
        return False
