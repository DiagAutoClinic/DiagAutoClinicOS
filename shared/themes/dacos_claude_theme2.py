"""
DACOS Midnight Carbon
Dark blue/purple with carbon fiber aesthetic and electric accents
"""
import logging

logger = logging.getLogger(__name__)

DACOS_THEME = {
    "bg_main": "#0B0C1E",
    "bg_panel": "#141633",
    "bg_card": "rgba(30, 32, 75, 0.95)",
    "accent": "#6366F1",
    "accent_hover": "#8B5CF6",
    "glow": "#6366F1",
    "text_main": "#E3E8FF",
    "text_muted": "#A5B4FC",
    "border": "rgba(99, 102, 241, 0.4)",
    "border_active": "#6366F1",
    "error": "#EF4444",
    "success": "#10B981",
    "warning": "#F59E0B",
    "info": "#6366F1"
}

DACOS_STYLESHEET = f"""
/* =====================================================================
   DACOS Modern Layout - Adapted for Midnight Carbon
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
    background-color: rgba(99, 102, 241, 0.1);
    color: {DACOS_THEME['accent']};
    border: 1px solid {DACOS_THEME['border']};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: rgba(99, 102, 241, 0.2);
    border: 1px solid {DACOS_THEME['accent']};
    color: #FFFFFF;
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
    background-color: rgba(0, 0, 0, 0.3);
    border: 1px solid {DACOS_THEME['border']};
    border-radius: 4px;
    padding: 8px;
    color: {DACOS_THEME['text_main']};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border: 1px solid {DACOS_THEME['accent']};
    background-color: rgba(99, 102, 241, 0.1);
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
        logger.info("DACOS Midnight Carbon (Modern Layout) applied")
        return True
    except Exception as e:
        logger.error(f"Failed to apply theme: {e}")
        return False
