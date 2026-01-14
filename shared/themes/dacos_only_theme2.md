THEME 2
DACOS_DEEP_TEAL_VOID

Machine-room calm. No glow unless justified.

DACOS_DEEP_TEAL_VOID = """
QMainWindow, QDialog {
    background-color: #041C20;
    color: #E6F7FA;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 10.5pt;
}

QWidget {
    background-color: transparent;
    color: #E6F7FA;
}

/* Panels */
QFrame, QWidget[class="panel"] {
    background-color: rgba(6, 36, 42, 0.85);
    border: 1px solid #0E6F78;
    border-radius: 14px;
}

/* Titles */
QLabel[class="hero-title"] {
    color: #00E5FF;
    font-size: 23pt;
    font-weight: 800;
    letter-spacing: 2px;
}

QLabel[class="section-title"] {
    color: #E6F7FA;
    font-size: 14pt;
    font-weight: 700;
    border-left: 4px solid #00E5FF;
    padding-left: 12px;
}

/* Buttons */
QPushButton {
    background-color: rgba(0, 0, 0, 0.3);
    color: #8FEFFF;
    border: 1px solid #0E6F78;
    border-radius: 6px;
    padding: 9px 20px;
    font-weight: 700;
}

QPushButton:hover {
    border-color: #00E5FF;
    color: #FFFFFF;
}

QPushButton[class="primary"] {
    background-color: rgba(0,229,255,0.2);
    border: 1px solid #00E5FF;
    color: #00E5FF;
}

/* Inputs */
QLineEdit, QTextEdit, QComboBox {
    background-color: rgba(0,0,0,0.4);
    border: 1px solid #0E6F78;
    border-radius: 6px;
    padding: 8px 12px;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border-color: #00E5FF;
}
"""