THEME 1
DACOS_INSTRUMENT_WHITE

Metrology-grade. Courtroom-safe. Zero nonsense.

DACOS_INSTRUMENT_WHITE = """
QMainWindow, QDialog {
    background-color: #FFFFFF;
    color: #0B0E11;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 10.5pt;
}

QWidget {
    background-color: transparent;
    color: #0B0E11;
}

/* Panels */
QFrame, QWidget[class="panel"] {
    background-color: #F7FAFB;
    border: 1px solid #CDEFF4;
    border-radius: 12px;
}

/* Titles */
QLabel[class="hero-title"] {
    color: #00E5FF;
    font-size: 24pt;
    font-weight: 800;
    letter-spacing: 2px;
    text-shadow: 0 0 10px rgba(0,229,255,0.55);
}

QLabel[class="section-title"] {
    color: #0B0E11;
    font-size: 14.5pt;
    font-weight: 700;
    border-left: 4px solid #00E5FF;
    padding-left: 12px;
}

/* Buttons */
QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #CDEFF4;
    border-radius: 6px;
    padding: 9px 20px;
    font-weight: 700;
}

QPushButton:hover {
    border-color: #00E5FF;
    box-shadow: 0 0 10px rgba(0,229,255,0.4);
}

QPushButton[class="primary"] {
    background-color: #00E5FF;
    color: #000000;
    border: none;
    box-shadow: 0 0 16px rgba(0,229,255,0.65);
}

/* Inputs */
QLineEdit, QTextEdit, QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #CDEFF4;
    border-radius: 6px;
    padding: 8px 12px;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border-color: #00E5FF;
    box-shadow: 0 0 8px rgba(0,229,255,0.5);
}
"""