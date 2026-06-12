from PyQt6.QtGui import QPalette, QColor

DACOS_THEME = {
    "name": "DACOS Kinetic Blueprint",
    "bg_main": "#0b1021",
    "bg_secondary": "#0f152b",
    "bg_tertiary": "#002222",
    "text_main": "#00ffff",
    "text_secondary": "#00aa00",
    "accent": "#00ffff",
    "border": "#004444",
    "success": "#00ff00",
    "warning": "#ffff00",
    "error": "#ff3333",
}

DACOS_STYLESHEET = """
/* DACOS Kinetic Blueprint Theme */
/* A Technical Digital Twin Style */

QWidget {
    background-color: #0b1021;
    color: #00ffff;
    font-family: 'Consolas', 'Courier New', monospace;
    selection-background-color: #004444;
    selection-color: #ffffff;
}

QMainWindow, QDialog {
    background-color: #0b1021;
}

/* --- Frames & Containers --- */
QFrame {
    border: 1px solid #004444;
    background-color: #0f152b;
}

QFrame[class="glass-card"] {
    background-color: #0f152b;
    border: 1px solid #00ffff;
    border-radius: 0px;
}

QFrame[class="info-card"] {
    background-color: #002222;
    border: 1px dashed #00aaaa;
}

/* --- Typography --- */
QLabel {
    color: #00ffff;
    font-family: 'Consolas', monospace;
}

QLabel[class="header-title"] {
    color: #00ffff;
    font-weight: bold;
    font-size: 18px;
    text-transform: uppercase;
}

QLabel[class="header-text"] {
    color: #00aaaa;
}

QLabel[class="h1"] { font-size: 20px; font-weight: bold; color: #ffffff; }
QLabel[class="h2"] { font-size: 16px; font-weight: bold; color: #00ffff; }
QLabel[class="label"] { color: #00aaaa; }
QLabel[class="value"] { color: #00ff00; font-weight: bold; }

/* --- Inputs & Interactive --- */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #080c18;
    border: 1px solid #004444;
    color: #00ff00;
    padding: 4px;
    font-family: 'Consolas', monospace;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #00ffff;
    background-color: #001111;
}

QPushButton {
    background-color: #0f152b;
    border: 1px solid #00aaaa;
    color: #00ffff;
    padding: 6px 12px;
    border-radius: 0px;
    font-weight: bold;
    text-transform: uppercase;
}

QPushButton:hover {
    background-color: #004444;
    border: 1px solid #00ffff;
}

QPushButton:pressed {
    background-color: #006666;
}

QPushButton[class="action-btn"] {
    background-color: #003333;
    border: 1px solid #00ffff;
}

/* --- Tabs --- */
QTabWidget::pane {
    border: 1px solid #004444;
    background-color: #0b1021;
}

QTabBar::tab {
    background-color: #0f152b;
    color: #00aaaa;
    border: 1px solid #004444;
    border-bottom: none;
    padding: 8px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #0b1021;
    color: #00ffff;
    border: 1px solid #00ffff;
    border-bottom: 1px solid #0b1021; /* Blend with pane */
}

QTabBar::tab:hover {
    background-color: #002222;
}

/* --- Lists & Trees --- */
QTreeWidget, QListWidget, QTableWidget {
    background-color: #0f152b;
    border: 1px solid #004444;
    gridline-color: #004444;
    color: #00ffff;
    alternate-background-color: #0b1021;
}

QHeaderView::section {
    background-color: #002222;
    color: #00ffff;
    border: 1px solid #004444;
    padding: 4px;
}

QTableWidget::item:selected, QTreeWidget::item:selected {
    background-color: #004444;
    color: #ffffff;
}

/* --- Scrollbars --- */
QScrollBar:vertical {
    border: none;
    background: #0b1021;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: #004444;
    min-height: 20px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

def apply_theme(app):
    """Apply the Kinetic Blueprint theme"""
    app.setStyle("Fusion")
    
    # Set Palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(DACOS_THEME["bg_main"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(DACOS_THEME["text_main"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(DACOS_THEME["bg_secondary"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(DACOS_THEME["bg_main"]))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(DACOS_THEME["bg_tertiary"]))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(DACOS_THEME["text_main"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(DACOS_THEME["text_main"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(DACOS_THEME["bg_secondary"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(DACOS_THEME["text_main"]))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(DACOS_THEME["accent"]))
    palette.setColor(QPalette.ColorRole.Link, QColor(DACOS_THEME["accent"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(DACOS_THEME["border"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    
    app.setPalette(palette)
    app.setStyleSheet(DACOS_STYLESHEET)
    return True
