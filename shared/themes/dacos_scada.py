from PyQt6.QtGui import QPalette, QColor

DACOS_THEME = {
    "name": "DACOS Industrial SCADA",
    "bg_main": "#f0f0f0",
    "bg_secondary": "#ffffff",
    "bg_tertiary": "#e0e0e0",
    "text_main": "#000000",
    "text_secondary": "#444444",
    "accent": "#0066cc", # Blue
    "border": "#a0a0a0",
    "success": "#009900",
    "warning": "#ffcc00",
    "error": "#cc0000",
}

DACOS_STYLESHEET = """
/* DACOS Industrial SCADA Theme */
/* A PLC / Engineering Workstation Style */

QWidget {
    background-color: #f0f0f0;
    color: #000000;
    font-family: 'Tahoma', 'Verdana', sans-serif;
    font-size: 11px;
}

QMainWindow, QDialog {
    background-color: #f0f0f0;
}

/* --- Frames & Containers --- */
QFrame {
    border: 1px solid #a0a0a0;
    background-color: #f0f0f0;
}

QFrame[class="glass-card"] {
    background-color: #ffffff;
    border: 1px solid #a0a0a0;
    border-radius: 0px;
}

QFrame[class="info-card"] {
    background-color: #ffffff;
    border: 1px solid #808080;
}

/* --- Typography --- */
QLabel {
    color: #000000;
}

QLabel[class="header-title"] {
    color: #000000;
    font-weight: bold;
    font-size: 16px;
}

QLabel[class="header-text"] {
    color: #444444;
}

QLabel[class="h1"] { font-size: 14px; font-weight: bold; color: #000000; }
QLabel[class="h2"] { font-size: 12px; font-weight: bold; color: #000000; }
QLabel[class="label"] { color: #444444; }
QLabel[class="value"] { color: #000000; font-weight: bold; }

/* --- Inputs & Interactive --- */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    border: 1px solid #a0a0a0;
    color: #000000;
    padding: 2px;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #0066cc;
    background-color: #ffffff;
}

QPushButton {
    background-color: #e0e0e0;
    border: 1px solid #808080;
    color: #000000;
    padding: 4px 8px;
    border-radius: 2px;
}

QPushButton:hover {
    background-color: #d0d0d0;
    border: 1px solid #606060;
}

QPushButton:pressed {
    background-color: #c0c0c0;
    padding-left: 5px; /* slight shift */
    padding-top: 5px;
}

QPushButton[class="action-btn"] {
    background-color: #dddddd;
    font-weight: bold;
}

/* --- Tabs --- */
QTabWidget::pane {
    border: 1px solid #a0a0a0;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #e0e0e0;
    color: #000000;
    border: 1px solid #a0a0a0;
    border-bottom: none;
    padding: 6px 12px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #a0a0a0;
    border-bottom: 1px solid #ffffff; /* Blend */
    top: 1px;
}

QTabBar::tab:hover {
    background-color: #f5f5f5;
}

/* --- Lists & Trees --- */
QTreeWidget, QListWidget, QTableWidget {
    background-color: #ffffff;
    border: 1px solid #a0a0a0;
    gridline-color: #e0e0e0;
    color: #000000;
    alternate-background-color: #f9f9f9;
}

QHeaderView::section {
    background-color: #e0e0e0;
    color: #000000;
    border: 1px solid #a0a0a0;
    padding: 4px;
    font-weight: bold;
}

QTableWidget::item:selected, QTreeWidget::item:selected {
    background-color: #0066cc;
    color: #ffffff;
}

/* --- Scrollbars --- */
QScrollBar:vertical {
    border: 1px solid #e0e0e0;
    background: #f0f0f0;
    width: 16px;
}

QScrollBar::handle:vertical {
    background: #c0c0c0;
    min-height: 20px;
    border: 1px solid #a0a0a0;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 16px;
    background: #e0e0e0;
    subcontrol-origin: margin;
}
"""

def apply_theme(app):
    """Apply the Industrial SCADA theme"""
    app.setStyle("Windows") # Prefer standard windows style base if available, else Fusion
    
    # Set Palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(DACOS_THEME["bg_main"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(DACOS_THEME["text_main"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(DACOS_THEME["bg_secondary"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(DACOS_THEME["bg_main"]))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffcc"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(DACOS_THEME["text_main"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(DACOS_THEME["text_main"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(DACOS_THEME["bg_tertiary"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(DACOS_THEME["text_main"]))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(DACOS_THEME["accent"]))
    palette.setColor(QPalette.ColorRole.Link, QColor(DACOS_THEME["accent"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(DACOS_THEME["accent"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    
    app.setPalette(palette)
    app.setStyleSheet(DACOS_STYLESHEET)
    return True
