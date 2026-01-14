THEME 3
DACOS_COGNITIVE_LATTICE

This one is unmistakably mine.

Uncertainty is first-class.
Inference ≠ fact.
Contradiction is visible.

DACOS_COGNITIVE_LATTICE = """
QMainWindow, QDialog {
    background-color: #F6F8F9;
    color: #101417;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: 10.5pt;
}

QWidget {
    background-color: transparent;
    color: #101417;
}

/* Panels */
QFrame, QWidget[class="panel"] {
    background-color: #FFFFFF;
    border: 1px solid #DCEEF2;
    border-radius: 14px;
}

/* Known / Confirmed */
QWidget[class="confirmed"] {
    border-left: 4px solid #00E5FF;
}

/* Inferred (dotted = epistemic uncertainty) */
QWidget[class="inferred"] {
    border: 1px dashed #F4B740;
    background-color: rgba(244,183,64,0.06);
}

/* Contradiction */
QWidget[class="conflict"] {
    border: 1px solid #8B5CF6;
    box-shadow: 0 0 12px rgba(139,92,246,0.45);
}

/* Titles */
QLabel[class="hero-title"] {
    color: #00BFD6;
    font-size: 24pt;
    font-weight: 800;
    letter-spacing: 2px;
}

/* Buttons */
QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #DCEEF2;
    border-radius: 6px;
    padding: 9px 20px;
    font-weight: 700;
}

QPushButton:hover {
    border-color: #00E5FF;
}

/* Primary action = confident knowledge */
QPushButton[class="primary"] {
    background-color: #00E5FF;
    color: #000000;
    border: none;
    box-shadow: 0 0 14px rgba(0,229,255,0.6);
}

/* Inputs */
QLineEdit, QTextEdit, QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #DCEEF2;
    border-radius: 6px;
    padding: 8px 12px;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border-color: #00E5FF;
}
"""