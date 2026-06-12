"""
DACOS Light Theme
Location: shared/themes/dacos_light.py
"""

import logging

logger = logging.getLogger(__name__)

# ===== DACOS LIGHT PALETTE (High Contrast) =====
DACOS_THEME = {
    "bg_main": "#ccfef4",      # Light Mint/Teal (User Requested)
    "bg_panel": "#b2dfdb",     # Slightly darker Teal for panels (Material Teal 100)
    "bg_card": "#FFFFFF",      # White cards
    "accent": "#00796B",       # Dark Teal (High Contrast)
    "accent_hover": "#004D40", # Even Darker Teal
    "glow": "#004D40",         # Dark Teal for "Glow" effects
    "text_main": "#000000",    # Pure Black
    "text_muted": "#455A64",   # Dark Blue Grey
    "border": "#00796B",       # Teal Border
    "border_active": "#004D40",# Dark Active Border
    "error": "#D32F2F",        # Red
    "success": "#388E3C",      # Green
    "warning": "#FBC02D",      # Yellow
    "info": "#1976D2"          # Blue
}

DACOS_STYLESHEET = f"""
/* =====================================================================
   DACOS Modern Layout - Light Edition (High Contrast)
   Standardized DACOS Experience
   ===================================================================== */

QMainWindow, QDialog {{
    background-color: {DACOS_THEME['bg_main']};
    color: {DACOS_THEME['text_main']};
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 10pt;
}}

/* Force Central Widget / Backgrounds to be Light */
QWidget#NeonBackground, QWidget#centralWidget {{
    background-color: {DACOS_THEME['bg_panel']};
    background: {DACOS_THEME['bg_panel']}; 
}}

QWidget {{
    background-color: transparent;
    color: {DACOS_THEME['text_main']};
    selection-background-color: {DACOS_THEME['accent']};
    selection-color: #FFFFFF;
}}

/* ===== CARDS ===== */
QFrame[class="glass-card"], QWidget[class="glass-card"] {{
    background-color: {DACOS_THEME['bg_card']};
    border: 2px solid {DACOS_THEME['border']};
    border-radius: 8px;
    color: {DACOS_THEME['text_main']};
}}

/* ===== BUTTONS (High Contrast) ===== */
QPushButton {{
    background-color: #FFFFFF;
    color: {DACOS_THEME['text_main']};
    border: 2px solid {DACOS_THEME['accent']};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 700;
}}

QPushButton:hover {{
    background-color: #E0F2F1;
    border: 2px solid {DACOS_THEME['accent_hover']};
    color: {DACOS_THEME['text_main']};
}}

QPushButton:pressed {{
    background-color: {DACOS_THEME['accent']};
    color: #FFFFFF;
}}

/* Primary Action Button - Solid Color */
QPushButton[class="primary"] {{
    background-color: {DACOS_THEME['accent']};
    color: #FFFFFF;
    border: 2px solid {DACOS_THEME['accent_hover']};
}}

QPushButton[class="primary"]:hover {{
    background-color: {DACOS_THEME['accent_hover']};
    color: #FFFFFF;
}}

QPushButton[class="danger"] {{
    background-color: {DACOS_THEME['error']};
    color: #FFFFFF;
    border: none;
}}

/* ===== INPUTS ===== */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox {{
    background-color: #FFFFFF;
    border: 2px solid {DACOS_THEME['border']};
    border-radius: 4px;
    padding: 8px;
    color: {DACOS_THEME['text_main']};
    font-weight: 500;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border: 2px solid {DACOS_THEME['accent']};
    background-color: #FAFAFA;
}}

/* ===== TABS ===== */
QTabWidget::pane {{
    border: 2px solid {DACOS_THEME['border']};
    background: {DACOS_THEME['bg_panel']};
    border-radius: 4px;
}}

QTabBar::tab {{
    background: #E0E0E0;
    color: {DACOS_THEME['text_main']};
    padding: 10px 20px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    border: 1px solid {DACOS_THEME['border']};
    border-bottom: none;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background: {DACOS_THEME['bg_panel']};
    color: {DACOS_THEME['accent']};
    border-top: 4px solid {DACOS_THEME['accent']};
    border-bottom: 2px solid {DACOS_THEME['bg_panel']};
    font-weight: bold;
}}

/* ===== SCROLLBARS ===== */
QScrollBar:vertical {{
    background: #F0F0F0;
    width: 16px;
}}

QScrollBar::handle:vertical {{
    background: #90A4AE;
    border-radius: 8px;
    border: 1px solid #78909C;
}}

QScrollBar::handle:vertical:hover {{
    background: {DACOS_THEME['accent']};
}}

QScrollBar:add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

/* ===== LABELS & HEADERS ===== */
QLabel {{
    color: {DACOS_THEME['text_main']};
}}

QLabel[class="hero-title"] {{
    color: {DACOS_THEME['accent']};
    font-weight: 900;
    text-transform: uppercase;
}}

QLabel[class="section-title"] {{
    color: {DACOS_THEME['text_main']};
    border-left: 6px solid {DACOS_THEME['accent']};
    padding-left: 10px;
    font-weight: bold;
}}

QLabel[class="status-label"] {{
    color: {DACOS_THEME['text_main']};
    font-weight: bold;
}}

/* ===== TABLES & LISTS ===== */
QTableWidget, QTreeWidget, QListWidget, QTableView, QTreeView, QListView {{
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid {DACOS_THEME['border']};
    gridline-color: #E0E0E0;
    selection-background-color: {DACOS_THEME['accent']};
    selection-color: #FFFFFF;
}}

QHeaderView::section {{
    background-color: #F5F5F5;
    color: #000000;
    padding: 6px;
    border: 1px solid #E0E0E0;
    font-weight: bold;
}}

QHeaderView {{
    background-color: #FFFFFF;
}}

QTableCornerButton::section {{
    background-color: #F5F5F5;
    border: 1px solid #E0E0E0;
}}

/* ===== DIALOGS & MESSAGE BOXES ===== */
QMessageBox {{
    background-color: #FFFFFF;
    color: #000000;
}}

QMessageBox QLabel {{
    color: #000000;
    background-color: transparent;
}}

/* Ensure dialog buttons are visible */
QDialogButtonBox QPushButton {{
    min-width: 80px;
}}
"""

def apply_theme(app, theme_name=None):
    try:
        app.setStyle('Fusion')
        app.setStyleSheet(DACOS_STYLESHEET)
        logger.info("DACOS Light Theme applied successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to apply DACOS Light Theme: {e}")
        return False
