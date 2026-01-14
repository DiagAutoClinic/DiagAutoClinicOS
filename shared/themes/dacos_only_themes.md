// DACOS THEMES v0.0.1 // 
Below are three full Qt stylesheets, engineered to be DACOS-only

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

/* Confidence scaling */
QLabel[class="low-confidence"] { color: rgba(16,20,23,0.45); }
QLabel[class="mid-confidence"] { color: rgba(16,20,23,0.75); }
QLabel[class="high-confidence"] { color: #101417; }
"""

How you should wire this (important)

Do not switch purely by color theme.

Switch by cognitive mode:

THEMES = {
    "instrument": DACOS_INSTRUMENT_WHITE,
    "void": DACOS_DEEP_TEAL_VOID,
    "lattice": DACOS_COGNITIVE_LATTICE
}


Then bind:

Live Data / Calibration → Instrument

CAN / Advanced / RE → Void

AI / Prognostics / Correlation → Lattice

That separation is what makes DACOS feel intentional, not skinned.