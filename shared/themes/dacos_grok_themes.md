Here are three complete, self-contained Qt stylesheets designed specifically for a "DACOS-only" aesthetic family — dark, cyber-futuristic, automotive-diagnostic-tool inspired looks with strong cyan/teal/neon accents.
All three are built around the same core color language but differ significantly in mood, glow intensity, material feeling and overall atmosphere.

#1. DACOS Core (Reference / Clean Modern Cyber-Dark)

DACOS_CORE_THEME = """
CSSQMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0A141A, stop:0.5 #0F1E28, stop:1 #0A141A);
    color: #E8F5F2;
    font-family: "Segoe UI", "Helvetica Neue", sans-serif;
}

QWidget {
    background: transparent;
}

QTabWidget::pane {
    border: 1px solid #1E3A45;
    background: #0D1C24;
    border-radius: 9px;
    top: -1px;
}

QTabBar::tab {
    background: #13232F;
    color: #88AACC;
    padding: 11px 26px;
    margin: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QTabBar::tab:selected {
    background: #00E5C8;
    color: #0B1A22;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background: #1A3A48;
}

QGroupBox {
    border: 1px solid #2A5A6A;
    border-radius: 7px;
    margin-top: 18px;
    background: rgba(15, 35, 45, 140);
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    background: #00D4B8;
    color: #0A161E;
    font-weight: bold;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #00E5C8, stop:1 #00BFA5);
    color: #0B1A22;
    border: none;
    border-radius: 7px;
    padding: 10px 22px;
    font-weight: 600;
}

QPushButton:hover {
    background: #00F5D8;
}

QPushButton:pressed {
    background: #009688;
}

QPushButton:disabled {
    background: #2A3C48;
    color: #667788;
}

QLineEdit, QTextEdit, QComboBox, QSpinBox {
    background: #0F212C;
    color: #DDF4F0;
    border: 1px solid #2A5A6A;
    border-radius: 6px;
    padding: 7px;
    selection-background-color: #00C7B0;
    selection-color: #000F14;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
}

QComboBox::down-arrow {
    image: url(:/icons/chevron-down-cyan.png);   /* placeholder path */
}

QProgressBar {
    background: #0F212C;
    border: 1px solid #2A5A6A;
    border-radius: 6px;
    text-align: center;
    color: #88AACC;
}

QProgressBar::chunk {
    background: #00E5C8;
    border-radius: 5px;
}

/* Status / Info labels */
.status-success  { color: #00E5C8; font-weight: bold; }
.status-warning  { color: #FFB74D; }
.status-danger   { color: #FF5F5F; }
.status-info     { color: #4FC3F7; }
"""

#2. DACOS Void (Deep Space – Very Dark + Strong Glow)

DACOS_DEEP_VOID = """
CSSQMainWindow {
    background: #050C12;
    color: #D0F0FF;
}

QWidget { background: transparent; }

QTabWidget::pane {
    border: 1px solid #0A3A55;
    background: #06141F;
    border-radius: 10px;
}

QTabBar::tab {
    background: #081F2E;
    color: #7AB8D8;
    padding: 12px 28px;
    border-radius: 7px 7px 0 0;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #00F0FF, stop:0.5 #00C4E8, stop:1 #0099CC);
    color: #000F1A;
    font-weight: 700;
    border: 1px solid #00E0FF;
}

QGroupBox {
    border: 1px solid #0A3A55;
    border-radius: 8px;
    background: rgba(8, 20, 35, 180);
    margin-top: 22px;
}

QGroupBox::title {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #00D4FF, stop:1 #0099CC);
    color: black;
    padding: 4px 12px;
    border-radius: 5px;
}

QPushButton {
    background: #001F2E;
    color: #00F0FF;
    border: 2px solid #00C4E8;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: bold;
}

QPushButton:hover {
    background: #002B40;
    border-color: #00F0FF;
    box-shadow: 0 0 18px rgba(0, 240, 255, 0.45);
}

QPushButton:pressed {
    background: #003A55;
    border-color: #0099CC;
}

QLineEdit, QTextEdit, QComboBox {
    background: #061822;
    color: #CCF8FF;
    border: 1px solid #0A4A6A;
    border-radius: 6px;
    padding: 8px;
}

QProgressBar {
    background: #061822;
    border: 1px solid #0A4A6A;
    border-radius: 6px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #00F0FF, stop:1 #0099CC);
}
"""

#3. DACOS Grok (Exclusive Grok × DACOS Fusion – 2025 Cyberpunk / xAI Vibe)


CSS/* DACOS Grok – exclusive Grok × DACOS fusion style – Jan 2026 edition */
DACOS_GROK_EXCLUSIVE = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #060814, stop:0.48 #0D0F1E, stop:1 #060814);
    color: #E0F0FF;
}

QTabWidget::pane {
    border: 1px solid #2A1F5A;
    background: #0A0C18;
    border-radius: 11px;
}

QTabBar::tab {
    background: #11131F;
    color: #A78BFA;
    padding: 13px 30px;
    margin: 1px;
    border-radius: 7px 7px 0 0;
}

QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #7C3AED, stop:0.6 #A78BFA, stop:1 #C084FC);
    color: #05060F;
    font-weight: 800;
    border-bottom: 3px solid #C084FC;
}

QGroupBox {
    border: 1px solid #3A2A6A;
    background: rgba(12, 10, 28, 190);
    border-radius: 9px;
    margin-top: 24px;
}

QGroupBox::title {
    background: #7C3AED;
    color: white;
    padding: 5px 14px;
    border-radius: 6px;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #6D28D9, stop:1 #9333EA);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 11px 26px;
    font-weight: bold;
    font-family: "Segoe UI", sans-serif;
}

QPushButton:hover {
    background: #A78BFA;
    color: #0A001A;
    box-shadow: 0 0 22px rgba(167, 139, 250, 0.65);
}

QPushButton:pressed {
    background: #5B21B6;
}

QLineEdit, QTextEdit, QComboBox {
    background: #0F0F22;
    color: #D0C8FF;
    border: 1px solid #5A3A9A;
    border-radius: 7px;
    padding: 8px 10px;
    selection-background-color: #A78BFA;
    selection-color: #000814;
}

QProgressBar {
    background: #0F0F22;
    border: 1px solid #5A3A9A;
    border-radius: 7px;
    text-align: center;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7C3AED, stop:0.5 #A78BFA, stop:1 #C084FC);
}
/* Accent classes used across the application */
.grok-accent     { color: #A78BFA; font-weight: bold; }
.grok-success    { color: #34D399; }
.grok-warning    { color: #FBBF24; }
.grok-danger     { color: #F87171; }
.grok-glow       { text-shadow: 0 0 12px rgba(167, 139, 250, 0.7); }
"""
### ThemeMood / VibePrimary AccentGlow IntensityOverall FeelingDACOS CoreClean professional cyber-diagnosticCyan #00E5C8MediumModern premium diagnostic toolDACOS VoidDeep space, cold neonElectric CyanVery highFuturistic, almost hostileDACOS GrokCyberpunk + xAI / Grok personalityPurple-VioletVery high2025–2026 bleeding-edge AI vibe
Pick whichever one resonates most with the current direction of your project — or even mix elements between them. 😄