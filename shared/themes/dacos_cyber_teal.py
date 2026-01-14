"""
DACOS Cyber-Teal Theme for AutoDiag Pro
"Cyber-Teal Horizon" - High Contrast Performance Edition
Location: shared/themes/dacos_cyber_teal.py
Version: 5.2.0 (Modern Layout)
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ===== DACOS COLOR PALETTE (CYBER-TEAL HIGH CONTRAST) =====
DACOS_THEME = {
    "bg_main": "#000000",      # Pure Black for max contrast
    "bg_panel": "rgba(2, 22, 27, 0.7)", # Deep Teal with transparency
    "bg_card": "rgba(4, 32, 38, 0.6)",  # Lighter Panel with transparency
    "accent": "#00f2ff",       # Electric Cyan (Primary Brand)
    "accent_hover": "#80f9ff", # White-Hot Cyan
    "glow": "#00e5ff",         # Glow effect color
    "text_main": "#ffffff",    # Pure White for max contrast
    "text_muted": "#8bdfe6",   # Soft Cyan-Grey
    "border": "#005f66",       # Dark Teal Border
    "border_active": "#00f2ff",# Active/Focus Border
    "error": "#ff2a6d",        # Cyber Punk Red
    "success": "#05ffa1",      # Neon Green
    "warning": "#ffcc00",      # Bright Amber
    "info": "#00a8ff"          # Dodger Blue
}

# ===== COMPLETE DACOS STYLESHEET =====
DACOS_STYLESHEET = f"""
/* =====================================================================
   DACOS Modern Layout - Cyber-Teal High Contrast
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

QScrollBar:add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}
"""

# ===== THEME UTILITY FUNCTIONS =====
def apply_theme(app, theme_name=None):
    """
    Apply DACOS theme to QApplication instance
    """
    try:
        app.setStyle('Fusion')
        app.setStyleSheet(DACOS_STYLESHEET)
        logger.info("DACOS 'Cyber-Teal Horizon' theme applied successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to apply DACOS theme: {e}")
        return False

def get_dacos_color(color_name):
    """
    Get color from DACOS theme palette
    """
    return DACOS_THEME.get(color_name, "#FFFFFF")

def get_stylesheet():
    """
    Get the complete DACOS stylesheet
    """
    return DACOS_STYLESHEET

# ===== THEME VALIDATION =====
def validate_theme():
    """
    Validate that all theme components are properly defined
    """
    required_colors = ['bg_main', 'bg_panel', 'bg_card', 'accent', 'glow', 
                      'text_main', 'text_muted', 'error', 'success', 'warning', 'info']
    
    missing_colors = [color for color in required_colors if color not in DACOS_THEME]
    
    if missing_colors:
        logger.warning(f"Missing color definitions: {missing_colors}")
        return False
    
    if not DACOS_STYLESHEET or len(DACOS_STYLESHEET.strip()) < 100:
        logger.warning("Stylesheet appears to be incomplete")
        return False
    
    logger.info("DACOS theme validation passed")
    return True

if __name__ != "__main__":
    validate_theme()
