"""
DACOS Cognitive Lattice
Uncertainty is first-class. Inference != fact. Contradiction is visible.
"""
import logging

logger = logging.getLogger(__name__)

DACOS_THEME = {
    "bg_main": "#F6F8F9",
    "bg_panel": "#FFFFFF",
    "bg_card": "#FFFFFF",
    "accent": "#00E5FF",
    "accent_hover": "#00BFD6",
    "glow": "#00E5FF",
    "text_main": "#101417",
    "text_muted": "rgba(16, 20, 23, 0.75)",
    "border": "#DCEEF2",
    "border_active": "#00E5FF",
    "error": "#EF4444",
    "success": "#10B981",
    "warning": "#F59E0B",
    "info": "#00E5FF"
}

DACOS_STYLESHEET = f"""
/* =====================================================================
   DACOS Modern Layout - Adapted for Cognitive Lattice
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
    selection-color: #FFFFFF;
}}

/* ===== CARDS ===== */
QFrame[class="glass-card"], QWidget[class="glass-card"] {{
    background-color: {DACOS_THEME['bg_card']};
    border: 1px solid {DACOS_THEME['border']};
    border-radius: 12px;
}}

/* ===== BUTTONS ===== */
QPushButton {{
    background-color: #F0F4F6;
    color: {DACOS_THEME['text_main']};
    border: 1px solid {DACOS_THEME['border']};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: #E0E8EC;
    border: 1px solid {DACOS_THEME['accent']};
}}

QPushButton:pressed {{
    background-color: {DACOS_THEME['accent']};
    color: #FFFFFF;
}}

QPushButton[class="primary"] {{
    background-color: {DACOS_THEME['accent']};
    color: #FFFFFF;
    border: none;
}}

QPushButton[class="primary"]:hover {{
    background-color: {DACOS_THEME['accent_hover']};
}}

/* ===== INPUTS ===== */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox {{
    background-color: #FFFFFF;
    border: 1px solid {DACOS_THEME['border']};
    border-radius: 4px;
    padding: 8px;
    color: {DACOS_THEME['text_main']};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border: 1px solid {DACOS_THEME['accent']};
    background-color: #F0FBFF;
}}

/* ===== TABS ===== */
QTabWidget::pane {{
    border: 1px solid {DACOS_THEME['border']};
    background: {DACOS_THEME['bg_panel']};
    border-radius: 4px;
}}

QTabBar::tab {{
    background: #E0E8EC;
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
    background: #E0E8EC;
    width: 12px;
}}

QScrollBar::handle:vertical {{
    background: #B0BEC5;
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
        logger.info("DACOS Cognitive Lattice (Modern Layout) applied")
        return True
    except Exception as e:
        logger.error(f"Failed to apply theme: {e}")
        return False
