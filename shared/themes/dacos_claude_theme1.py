"""
DACOS Teal Fusion (Original)
Teal/Cyan glass morphism with holographic accents
"""
import logging

logger = logging.getLogger(__name__)

DACOS_THEME = {
    "bg_main": "#0A1A1A",
    "bg_panel": "#0D2323",
    "bg_card": "rgba(19, 79, 74, 0.95)",
    "accent": "#21F5C1",
    "accent_hover": "#2AF5D1",
    "glow": "#21F5C1",
    "text_main": "#E8F4F2",
    "text_muted": "#9ED9CF",
    "border": "rgba(33, 245, 193, 0.4)",
    "border_active": "#21F5C1",
    "error": "#FF4D4D",
    "success": "#10B981",
    "warning": "#F59E0B",
    "info": "#4FC3F7"
}

DACOS_STYLESHEET = f"""
/* =====================================================================
   DACOS Modern Layout - Adapted for Teal Fusion
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
        logger.info("DACOS Teal Fusion (Modern Layout) applied")
        return True
    except Exception as e:
        logger.error(f"Failed to apply theme: {e}")
        return False
