from PyQt6.QtGui import QPalette, QColor

DACOS_THEME = {
    "name": "DACOS Command Center",
    "bg_main": "#000000",
    "bg_secondary": "#111111",
    "bg_tertiary": "#222222",
    "text_main": "#e0e0e0",
    "text_secondary": "#aaaaaa",
    "accent": "#d68a00", # Amber
    "border": "#444444",
    "success": "#00ff00",
    "warning": "#d68a00",
    "error": "#ff0000",
}

DACOS_STYLESHEET = """
/* DACOS Command Center Theme */
/* A Dark Cockpit / Flight Deck Style */

QWidget {
    background-color: #000000;
    color: #e0e0e0;
    font-family: 'Segoe UI', 'Verdana', sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #000000;
}

/* --- Frames & Containers --- */
QFrame {
    border: none;
    background-color: #111111;
}

QFrame[class="glass-card"] {
    background-color: #111111;
    border-bottom: 2px solid #333333;
    border-radius: 0px;
}

QFrame[class="info-card"] {
    background-color: #1a1a1a;
    border: 1px solid #333333;
}

/* --- Typography --- */
QLabel {
    color: #e0e0e0;
}

QLabel[class="header-title"] {
    color: #ffffff;
    font-weight: bold;
    font-size: 20px;
}

QLabel[class="header-text"] {
    color: #aaaaaa;
    font-weight: bold;
}

QLabel[class="h1"] { font-size: 22px; font-weight: bold; color: #ffffff; }
QLabel[class="h2"] { font-size: 18px; font-weight: bold; color: #d68a00; } /* Amber headers */
QLabel[class="label"] { color: #aaaaaa; }
QLabel[class="value"] { color: #ffffff; font-weight: bold; font-size: 14px; }

/* --- Inputs & Interactive --- */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #000000;
    border: 1px solid #444444;
    color: #ffffff;
    padding: 6px;
    font-weight: bold;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #d68a00; /* Amber focus */
    background-color: #111111;
}

QPushButton {
    background-color: #222222;
    border: 2px solid #444444;
    color: #cccccc;
    padding: 8px 16px;
    font-weight: bold;
    border-radius: 2px;
}

QPushButton:hover {
    background-color: #444444;
    border-color: #888888;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #d68a00;
    color: #000000;
    border-color: #d68a00;
}

QPushButton[class="action-btn"] {
    background-color: #003300;
    border: 2px solid #006600;
    color: #ffffff;
}

/* --- Tabs --- */
QTabWidget::pane {
    border: 1px solid #333333;
    background-color: #000000;
}

QTabBar::tab {
    background-color: #111111;
    color: #888888;
    border: 1px solid #333333;
    padding: 10px 20px;
    margin-right: 4px;
    font-weight: bold;
    text-transform: uppercase;
}

QTabBar::tab:selected {
    background-color: #d68a00;
    color: #000000;
    border: 1px solid #d68a00;
}

QTabBar::tab:hover {
    background-color: #333333;
    color: #ffffff;
}

/* --- Lists & Trees --- */
QTreeWidget, QListWidget, QTableWidget {
    background-color: #111111;
    border: 1px solid #333333;
    gridline-color: #333333;
    color: #ffffff;
    alternate-background-color: #080808;
}

QHeaderView::section {
    background-color: #222222;
    color: #aaaaaa;
    border: 1px solid #333333;
    padding: 6px;
    font-weight: bold;
    text-transform: uppercase;
}

QTableWidget::item:selected, QTreeWidget::item:selected {
    background-color: #d68a00;
    color: #000000;
}

/* --- Scrollbars --- */
QScrollBar:vertical {
    border: none;
    background: #111111;
    width: 14px;
}

QScrollBar::handle:vertical {
    background: #444444;
    min-height: 30px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

def apply_theme(app):
    """Apply the Command Center theme"""
    app.setStyle("Fusion")
    
    # Set Palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(DACOS_THEME["bg_main"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(DACOS_THEME["text_main"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(DACOS_THEME["bg_secondary"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(DACOS_THEME["bg_secondary"]))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(DACOS_THEME["bg_tertiary"]))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(DACOS_THEME["text_main"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(DACOS_THEME["text_main"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(DACOS_THEME["bg_tertiary"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(DACOS_THEME["text_main"]))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(DACOS_THEME["accent"]))
    palette.setColor(QPalette.ColorRole.Link, QColor(DACOS_THEME["accent"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(DACOS_THEME["accent"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
    
    app.setPalette(palette)
    app.setStyleSheet(DACOS_STYLESHEET)
    return True
