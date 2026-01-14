Here are three DACOS-only Qt stylesheets, with the third being an exclusive "DeepSeek" theme:

Theme 1: DACOS Neon Professional
css
/* DACOS NEON PROFESSIONAL - PRIMARY THEME */
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0A1A1A, stop:0.4 #0D2323, stop:1 #0A1A1A);
    color: #E8F4F2;
    font-family: "Segoe UI";
    border: none;
}

/* GLASS EFFECT COMPONENTS */
QFrame[class="glass-card"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(19, 79, 74, 0.7), stop:1 rgba(13, 35, 35, 0.8));
    border: 2px solid rgba(33, 245, 193, 0.3);
    border-radius: 16px;
    padding: 20px;
}

QFrame[class="glass-panel"] {
    background: rgba(13, 35, 35, 0.6);
    border: 1px solid rgba(33, 245, 193, 0.2);
    border-radius: 12px;
    padding: 15px;
}

/* BUTTONS - DACOS GRADIENT SYSTEM */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #21F5C1, stop:0.7 #1AE1AD, stop:1 #16D09C);
    border: none;
    border-radius: 10px;
    padding: 14px 28px;
    color: #0A1A1A;
    font-weight: 700;
    font-size: 11pt;
    min-height: 45px;
    min-width: 120px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #2AF5D1, stop:1 #21F5C1);
    border: 2px solid rgba(42, 245, 209, 0.5);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #16D09C, stop:1 #13B989);
    padding: 16px 30px;
}

QPushButton:disabled {
    background: #134F4A;
    color: #9ED9CF;
    border: 1px solid rgba(33, 245, 193, 0.1);
}

/* BUTTON VARIANTS */
QPushButton[class="primary"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #21F5C1, stop:1 #16D09C);
    color: #0A1A1A;
}

QPushButton[class="success"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #10B981, stop:1 #059669);
    color: white;
}

QPushButton[class="warning"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #F59E0B, stop:1 #D97706);
    color: white;
}

QPushButton[class="danger"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FF4D4D, stop:1 #DC2626);
    color: white;
}

QPushButton[class="outline"] {
    background: transparent;
    border: 2px solid #21F5C1;
    color: #21F5C1;
}

/* TABS - FUTURISTIC DESIGN */
QTabWidget::pane {
    border: 3px solid rgba(33, 245, 193, 0.4);
    background: rgba(13, 35, 35, 0.9);
    border-radius: 18px;
    top: 10px;
}

QTabBar::tab {
    background: rgba(19, 79, 74, 0.7);
    color: #9ED9CF;
    padding: 16px 32px;
    margin: 6px 4px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 11pt;
    min-width: 140px;
}

QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #21F5C1, stop:1 #1AE1AD);
    color: #0A1A1A;
    font-weight: 700;
    border-bottom: 3px solid #0A1A1A;
}

QTabBar::tab:hover:!selected {
    background: rgba(33, 245, 193, 0.2);
    color: #E8F4F2;
}

/* INPUT FIELDS */
QLineEdit, QTextEdit, QPlainTextEdit {
    background: rgba(10, 26, 26, 0.8);
    border: 2px solid rgba(33, 245, 193, 0.3);
    border-radius: 10px;
    padding: 12px 18px;
    color: #E8F4F2;
    font-size: 11pt;
    selection-background-color: #21F5C1;
    selection-color: #0A1A1A;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 3px solid #21F5C1;
    background: rgba(10, 26, 26, 0.9);
}

QComboBox {
    background: rgba(10, 26, 26, 0.8);
    border: 2px solid rgba(33, 245, 193, 0.3);
    border-radius: 10px;
    padding: 10px 18px;
    color: #E8F4F2;
    min-height: 40px;
}

QComboBox::drop-down {
    border: none;
    background: transparent;
}

QComboBox QAbstractItemView {
    background: rgba(13, 35, 35, 0.95);
    border: 2px solid #21F5C1;
    border-radius: 10px;
    color: #E8F4F2;
    selection-background-color: #21F5C1;
    selection-color: #0A1A1A;
}

/* SCROLLBARS */
QScrollBar:vertical {
    border: none;
    background: rgba(19, 79, 74, 0.3);
    width: 14px;
    border-radius: 7px;
}

QScrollBar::handle:vertical {
    background: #21F5C1;
    border-radius: 7px;
    min-height: 30px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: rgba(19, 79, 74, 0.3);
    height: 14px;
    border-radius: 7px;
}

QScrollBar::handle:horizontal {
    background: #21F5C1;
    border-radius: 7px;
    min-width: 30px;
}

/* LABELS - TYPOGRAPHY SYSTEM */
QLabel[class="hero-title"] {
    color: #21F5C1;
    font-size: 24pt;
    font-weight: 800;
    font-family: "Segoe UI";
}

QLabel[class="tab-title"] {
    color: #21F5C1;
    font-size: 18pt;
    font-weight: 700;
    font-family: "Segoe UI";
}

QLabel[class="section-title"] {
    color: #E8F4F2;
    font-size: 14pt;
    font-weight: 600;
    font-family: "Segoe UI";
}

QLabel[class="section-label"] {
    color: #9ED9CF;
    font-size: 11pt;
    font-weight: 500;
    font-family: "Segoe UI";
}

QLabel[class="subtitle"] {
    color: #9ED9CF;
    font-size: 10pt;
    font-weight: 400;
    font-family: "Segoe UI";
    opacity: 0.8;
}

QLabel[class="status-label"] {
    color: #21F5C1;
    font-size: 10pt;
    font-weight: 600;
    font-family: "Segoe UI";
    padding: 5px 10px;
    background: rgba(33, 245, 193, 0.1);
    border-radius: 8px;
}

/* TABLES */
QTableWidget {
    background: rgba(10, 26, 26, 0.7);
    border: 2px solid rgba(33, 245, 193, 0.3);
    border-radius: 12px;
    gridline-color: rgba(33, 245, 193, 0.1);
    color: #E8F4F2;
    font-size: 10pt;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid rgba(33, 245, 193, 0.1);
}

QTableWidget::item:selected {
    background: #21F5C1;
    color: #0A1A1A;
    font-weight: 600;
}

QHeaderView::section {
    background: rgba(19, 79, 74, 0.8);
    color: #21F5C1;
    font-weight: 700;
    padding: 10px;
    border: none;
    border-bottom: 2px solid #21F5C1;
}

/* CHECKBOXES & RADIO BUTTONS */
QCheckBox, QRadioButton {
    color: #E8F4F2;
    font-size: 11pt;
    spacing: 10px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #21F5C1;
    border-radius: 4px;
}

QCheckBox::indicator:checked {
    background-color: #21F5C1;
    image: url(":/icons/check.svg");
}

QRadioButton::indicator:checked {
    background-color: #21F5C1;
    border: 6px solid #0A1A1A;
}

/* GROUP BOXES */
QGroupBox {
    border: 2px solid rgba(33, 245, 193, 0.4);
    border-radius: 14px;
    margin-top: 20px;
    padding-top: 40px;
    font-weight: 700;
    color: #21F5C1;
    font-size: 12pt;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 20px;
    padding: 5px 20px;
    background: rgba(13, 35, 35, 0.9);
    border-radius: 10px;
}

/* PROGRESS BARS */
QProgressBar {
    border: 2px solid rgba(33, 245, 193, 0.3);
    border-radius: 10px;
    background: rgba(10, 26, 26, 0.8);
    text-align: center;
    color: #0A1A1A;
    font-weight: 600;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #21F5C1, stop:1 #2AF5D1);
    border-radius: 8px;
}

/* SLIDERS */
QSlider::groove:horizontal {
    border: 2px solid rgba(33, 245, 193, 0.3);
    height: 10px;
    background: rgba(10, 26, 26, 0.8);
    border-radius: 5px;
}

QSlider::handle:horizontal {
    background: #21F5C1;
    border: 3px solid #0A1A1A;
    width: 24px;
    height: 24px;
    margin: -8px 0;
    border-radius: 12px;
}

/* MESSAGE BOXES */
QMessageBox {
    background: rgba(13, 35, 35, 0.95);
    border: 3px solid #21F5C1;
    border-radius: 18px;
}

QMessageBox QLabel {
    color: #E8F4F2;
    font-size: 11pt;
}

QMessageBox QPushButton {
    min-width: 100px;
}

/* STATUS BAR */
QStatusBar {
    background: rgba(13, 35, 35, 0.9);
    border-top: 2px solid rgba(33, 245, 193, 0.3);
    color: #9ED9CF;
    font-size: 9pt;
}

/* TOOLTIPS */
QToolTip {
    background: rgba(13, 35, 35, 0.95);
    color: #21F5C1;
    border: 1px solid rgba(33, 245, 193, 0.5);
    border-radius: 8px;
    padding: 8px;
    font-size: 10pt;
}

/* MENUS */
QMenu {
    background: rgba(13, 35, 35, 0.95);
    border: 2px solid rgba(33, 245, 193, 0.4);
    border-radius: 10px;
    color: #E8F4F2;
}

QMenu::item {
    padding: 8px 30px;
    border-radius: 6px;
}

QMenu::item:selected {
    background: #21F5C1;
    color: #0A1A1A;
}

QMenu::separator {
    height: 1px;
    background: rgba(33, 245, 193, 0.3);
    margin: 5px 10px;
}
Theme 2: DACOS Matrix Dark
css
/* DACOS MATRIX DARK - CYBERPUNK INSPIRED */
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #081010, stop:0.5 #0A1414, stop:1 #081010);
    color: #00FFCC;
    font-family: "Consolas", "Monaco", monospace;
    border: none;
}

/* MATRIX GLASS EFFECT */
QFrame[class="glass-card"] {
    background: rgba(8, 32, 32, 0.85);
    border: 1px solid rgba(0, 255, 204, 0.4);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 0 20px rgba(0, 255, 204, 0.1);
}

QFrame[class="glass-panel"] {
    background: rgba(10, 20, 20, 0.7);
    border: 1px solid rgba(0, 255, 204, 0.2);
    border-radius: 8px;
    padding: 15px;
}

/* MATRIX BUTTONS */
QPushButton {
    background: rgba(0, 255, 204, 0.1);
    border: 1px solid rgba(0, 255, 204, 0.5);
    border-radius: 6px;
    padding: 12px 24px;
    color: #00FFCC;
    font-weight: 600;
    font-size: 11pt;
    font-family: "Consolas", monospace;
    min-height: 40px;
}

QPushButton:hover {
    background: rgba(0, 255, 204, 0.2);
    border: 1px solid #00FFCC;
    box-shadow: 0 0 10px rgba(0, 255, 204, 0.3);
}

QPushButton:pressed {
    background: rgba(0, 255, 204, 0.3);
    color: #00FFFF;
}

QPushButton:disabled {
    background: rgba(8, 32, 32, 0.5);
    color: rgba(0, 255, 204, 0.3);
    border: 1px solid rgba(0, 255, 204, 0.1);
}

/* MATRIX TABS */
QTabWidget::pane {
    border: 1px solid rgba(0, 255, 204, 0.3);
    background: rgba(10, 20, 20, 0.8);
    border-radius: 8px;
    top: 5px;
}

QTabBar::tab {
    background: rgba(8, 32, 32, 0.7);
    border: 1px solid rgba(0, 255, 204, 0.2);
    color: rgba(0, 255, 204, 0.7);
    padding: 10px 20px;
    margin: 2px;
    border-radius: 6px;
    font-family: "Consolas", monospace;
    font-weight: 600;
}

QTabBar::tab:selected {
    background: rgba(0, 255, 204, 0.2);
    color: #00FFCC;
    border: 1px solid #00FFCC;
    font-weight: 700;
}

/* MATRIX INPUTS */
QLineEdit, QTextEdit, QPlainTextEdit {
    background: rgba(8, 16, 16, 0.9);
    border: 1px solid rgba(0, 255, 204, 0.3);
    border-radius: 4px;
    padding: 8px 12px;
    color: #00FFCC;
    font-family: "Consolas", monospace;
    font-size: 10pt;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #00FFCC;
    background: rgba(8, 16, 16, 1);
}

/* MATRIX SCROLLBARS */
QScrollBar:vertical {
    background: rgba(8, 32, 32, 0.3);
    border: 1px solid rgba(0, 255, 204, 0.1);
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: rgba(0, 255, 204, 0.5);
    border-radius: 6px;
    min-height: 20px;
}

/* MATRIX TABLES */
QTableWidget {
    background: rgba(8, 16, 16, 0.8);
    border: 1px solid rgba(0, 255, 204, 0.2);
    border-radius: 6px;
    gridline-color: rgba(0, 255, 204, 0.1);
    color: #00FFCC;
    font-family: "Consolas", monospace;
    font-size: 10pt;
}

QTableWidget::item:selected {
    background: rgba(0, 255, 204, 0.3);
    color: #00FFFF;
}

/* MATRIX GROUP BOXES */
QGroupBox {
    border: 1px solid rgba(0, 255, 204, 0.3);
    border-radius: 8px;
    margin-top: 15px;
    padding-top: 30px;
    color: #00FFCC;
    font-family: "Consolas", monospace;
    font-weight: 600;
}

/* MATRIX PROGRESS BARS */
QProgressBar {
    border: 1px solid rgba(0, 255, 204, 0.3);
    border-radius: 4px;
    background: rgba(8, 16, 16, 0.8);
    color: #00FFCC;
    font-family: "Consolas", monospace;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #00FFCC, stop:1 #00CC99);
    border-radius: 3px;
}

/* MATRIX CHECKBOXES */
QCheckBox, QRadioButton {
    color: #00FFCC;
    font-family: "Consolas", monospace;
    spacing: 8px;
}

QCheckBox::indicator, QRadioButton::indicator {
    border: 1px solid rgba(0, 255, 204, 0.5);
    border-radius: 3px;
}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background-color: #00FFCC;
}

/* MATRIX STATUS BAR */
QStatusBar {
    background: rgba(8, 16, 16, 0.9);
    border-top: 1px solid rgba(0, 255, 204, 0.2);
    color: rgba(0, 255, 204, 0.7);
    font-family: "Consolas", monospace;
    font-size: 9pt;
}

/* MATRIX COMBOBOX */
QComboBox {
    background: rgba(8, 16, 16, 0.9);
    border: 1px solid rgba(0, 255, 204, 0.3);
    border-radius: 4px;
    padding: 6px;
    color: #00FFCC;
    font-family: "Consolas", monospace;
}

QComboBox QAbstractItemView {
    background: rgba(8, 16, 16, 0.95);
    border: 1px solid rgba(0, 255, 204, 0.5);
    color: #00FFCC;
    selection-background-color: rgba(0, 255, 204, 0.3);
}

/* MATRIX MESSAGE BOX */
QMessageBox {
    background: rgba(8, 16, 16, 0.95);
    border: 1px solid rgba(0, 255, 204, 0.4);
    border-radius: 8px;
    color: #00FFCC;
    font-family: "Consolas", monospace;
}

/* MATRIX TOOLTIPS */
QToolTip {
    background: rgba(8, 16, 16, 0.95);
    color: #00FFCC;
    border: 1px solid rgba(0, 255, 204, 0.3);
    border-radius: 4px;
    font-family: "Consolas", monospace;
    font-size: 9pt;
}

/* MATRIX MENUS */
QMenu {
    background: rgba(8, 16, 16, 0.95);
    border: 1px solid rgba(0, 255, 204, 0.3);
    color: #00FFCC;
    font-family: "Consolas", monospace;
}

QMenu::item:selected {
    background: rgba(0, 255, 204, 0.2);
}

/* DATA MATRIX EFFECT FOR DASHBOARD */
QLabel[class="matrix-data"] {
    color: #00FFCC;
    font-family: "Consolas", monospace;
    font-size: 18pt;
    font-weight: 700;
    text-shadow: 0 0 10px rgba(0, 255, 204, 0.5);
}

QLabel[class="matrix-label"] {
    color: rgba(0, 255, 204, 0.7);
    font-family: "Consolas", monospace;
    font-size: 10pt;
    font-weight: 600;
}

/* BINARY ANIMATION EFFECT CLASS */
QLabel[class="binary-stream"] {
    color: #00FFCC;
    font-family: "Courier New", monospace;
    font-size: 8pt;
    background: transparent;
}
Theme 3: DeepSeek Exclusive Theme
css
/* DEEPSEEK EXCLUSIVE THEME - AI-ENHANCED DESIGN */
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0F2B46, stop:0.3 #1A365D, stop:0.7 #2D3748, stop:1 #0F2B46);
    color: #E2E8F0;
    font-family: "Inter", "Segoe UI", sans-serif;
    border: none;
}

/* NEURAL NETWORK GLASS EFFECT */
QFrame[class="glass-card"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(56, 178, 172, 0.15), stop:1 rgba(66, 153, 225, 0.15));
    border: 2px solid rgba(56, 178, 172, 0.3);
    border-radius: 20px;
    padding: 24px;
    backdrop-filter: blur(10px);
}

QFrame[class="glass-panel"] {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(56, 178, 172, 0.2);
    border-radius: 16px;
    padding: 20px;
}

/* DEEPSEEK INTELLIGENT BUTTONS */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #4299E1, stop:0.5 #38B2AC, stop:1 #3182CE);
    border: none;
    border-radius: 12px;
    padding: 14px 28px;
    color: white;
    font-weight: 600;
    font-size: 11pt;
    min-height: 44px;
    min-width: 120px;
    transition: all 0.3s ease;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #63B3ED, stop:1 #4299E1);
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(66, 153, 225, 0.3);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #3182CE, stop:1 #2C5282);
    transform: translateY(0px);
}

QPushButton:disabled {
    background: #4A5568;
    color: #A0AEC0;
    border: 1px solid #2D3748;
}

/* DEEPSEEK FUNCTIONAL BUTTONS */
QPushButton[class="primary"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #38B2AC, stop:1 #319795);
    color: white;
}

QPushButton[class="success"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #48BB78, stop:1 #38A169);
    color: white;
}

QPushButton[class="warning"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ED8936, stop:1 #DD6B20);
    color: white;
}

QPushButton[class="danger"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #F56565, stop:1 #E53E3E);
    color: white;
}

QPushButton[class="ai-action"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #805AD5, stop:1 #6B46C1);
    color: white;
    font-weight: 700;
    border-left: 4px solid #D69E2E;
}

/* NEURAL NETWORK TABS */
QTabWidget::pane {
    border: 3px solid rgba(56, 178, 172, 0.4);
    background: rgba(30, 41, 59, 0.9);
    border-radius: 20px;
    top: 12px;
    padding: 2px;
}

QTabBar::tab {
    background: rgba(45, 55, 72, 0.7);
    color: #CBD5E0;
    padding: 14px 28px;
    margin: 6px 4px;
    border-radius: 14px;
    font-weight: 600;
    font-size: 11pt;
    min-width: 140px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #4299E1, stop:1 #38B2AC);
    color: white;
    font-weight: 700;
    box-shadow: 0 4px 12px rgba(56, 178, 172, 0.3);
    transform: scale(1.02);
}

QTabBar::tab:hover:!selected {
    background: rgba(56, 178, 172, 0.2);
    color: #E2E8F0;
}

/* DEEPSEEK INPUT FIELDS */
QLineEdit, QTextEdit, QPlainTextEdit {
    background: rgba(26, 32, 44, 0.8);
    border: 2px solid rgba(56, 178, 172, 0.3);
    border-radius: 12px;
    padding: 12px 18px;
    color: #E2E8F0;
    font-size: 11pt;
    font-family: "Inter", sans-serif;
    selection-background-color: #38B2AC;
    selection-color: white;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 3px solid #38B2AC;
    background: rgba(26, 32, 44, 0.9);
    box-shadow: 0 0 0 3px rgba(56, 178, 172, 0.1);
}

QComboBox {
    background: rgba(26, 32, 44, 0.8);
    border: 2px solid rgba(56, 178, 172, 0.3);
    border-radius: 12px;
    padding: 10px 18px;
    color: #E2E8F0;
    min-height: 42px;
    font-family: "Inter", sans-serif;
}

QComboBox::drop-down {
    border: none;
    background: transparent;
}

QComboBox QAbstractItemView {
    background: rgba(30, 41, 59, 0.95);
    border: 2px solid #38B2AC;
    border-radius: 12px;
    color: #E2E8F0;
    selection-background-color: #38B2AC;
    selection-color: white;
    font-family: "Inter", sans-serif;
}

/* DEEPSEEK SCROLLBARS - SMOOTH SCROLLING */
QScrollBar:vertical {
    border: none;
    background: rgba(56, 178, 172, 0.1);
    width: 14px;
    border-radius: 7px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4299E1, stop:1 #38B2AC);
    border-radius: 7px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #63B3ED, stop:1 #4FD1C5);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 0px;
}

/* DEEPSEEK TYPOGRAPHY SYSTEM */
QLabel[class="deepseek-title"] {
    color: #38B2AC;
    font-size: 26pt;
    font-weight: 800;
    font-family: "Inter", sans-serif;
    letter-spacing: -0.5px;
}

QLabel[class="deepseek-subtitle"] {
    color: #4299E1;
    font-size: 16pt;
    font-weight: 700;
    font-family: "Inter", sans-serif;
}

QLabel[class="ai-header"] {
    color: #E2E8F0;
    font-size: 14pt;
    font-weight: 600;
    font-family: "Inter", sans-serif;
    background: rgba(56, 178, 172, 0.1);
    padding: 8px 16px;
    border-radius: 10px;
    border-left: 4px solid #38B2AC;
}

QLabel[class="data-label"] {
    color: #CBD5E0;
    font-size: 11pt;
    font-weight: 500;
    font-family: "Inter", sans-serif;
}

QLabel[class="metric-value"] {
    color: #38B2AC;
    font-size: 20pt;
    font-weight: 700;
    font-family: "Inter", sans-serif;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

QLabel[class="status-indicator"] {
    color: #48BB78;
    font-size: 10pt;
    font-weight: 600;
    font-family: "Inter", sans-serif;
    padding: 6px 12px;
    background: rgba(72, 187, 120, 0.1);
    border-radius: 8px;
    border: 1px solid rgba(72, 187, 120, 0.3);
}

/* INTELLIGENT TABLES */
QTableWidget {
    background: rgba(26, 32, 44, 0.7);
    border: 2px solid rgba(56, 178, 172, 0.3);
    border-radius: 16px;
    gridline-color: rgba(56, 178, 172, 0.15);
    color: #E2E8F0;
    font-size: 10pt;
    font-family: "Inter", sans-serif;
    alternate-background-color: rgba(56, 178, 172, 0.05);
}

QTableWidget::item {
    padding: 10px;
    border-bottom: 1px solid rgba(56, 178, 172, 0.1);
}

QTableWidget::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #38B2AC, stop:1 #4299E1);
    color: white;
    font-weight: 600;
}

QHeaderView::section {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #2D3748, stop:1 #4A5568);
    color: #38B2AC;
    font-weight: 700;
    padding: 12px;
    border: none;
    border-bottom: 3px solid #38B2AC;
    font-family: "Inter", sans-serif;
}

/* AI-ENHANCED CHECKBOXES & RADIOS */
QCheckBox, QRadioButton {
    color: #E2E8F0;
    font-size: 11pt;
    font-family: "Inter", sans-serif;
    spacing: 12px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 22px;
    height: 22px;
    border: 2px solid #38B2AC;
    border-radius: 6px;
    background: rgba(26, 32, 44, 0.8);
}

QCheckBox::indicator:checked {
    background-color: #38B2AC;
    image: url(":/icons/ai-check.svg");
    border-color: #4299E1;
}

QRadioButton::indicator:checked {
    background-color: #38B2AC;
    border: 6px solid #2D3748;
}

/* DEEPSEEK GROUP BOXES */
QGroupBox {
    border: 2px solid rgba(56, 178, 172, 0.4);
    border-radius: 18px;
    margin-top: 24px;
    padding-top: 44px;
    font-weight: 700;
    color: #38B2AC;
    font-size: 13pt;
    font-family: "Inter", sans-serif;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 24px;
    padding: 8px 24px;
    background: rgba(30, 41, 59, 0.9);
    border-radius: 12px;
    border: 1px solid rgba(56, 178, 172, 0.3);
}

/* NEURAL PROGRESS BARS */
QProgressBar {
    border: 2px solid rgba(56, 178, 172, 0.3);
    border-radius: 12px;
    background: rgba(26, 32, 44, 0.8);
    text-align: center;
    color: #E2E8F0;
    font-weight: 600;
    font-family: "Inter", sans-serif;
    height: 24px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4299E1, stop:0.5 #38B2AC, stop:1 #319795);
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* INTELLIGENT SLIDERS */
QSlider::groove:horizontal {
    border: 2px solid rgba(56, 178, 172, 0.3);
    height: 12px;
    background: rgba(26, 32, 44, 0.8);
    border-radius: 6px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #4299E1, stop:1 #38B2AC);
    border: 3px solid #2D3748;
    width: 26px;
    height: 26px;
    margin: -8px 0;
    border-radius: 13px;
}

/* AI-ASSISTED MESSAGE BOXES */
QMessageBox {
    background: rgba(30, 41, 59, 0.97);
    border: 3px solid #38B2AC;
    border-radius: 20px;
    font-family: "Inter", sans-serif;
}

QMessageBox QLabel {
    color: #E2E8F0;
    font-size: 11pt;
    line-height: 1.5;
}

QMessageBox QPushButton {
    min-width: 100px;
    font-weight: 600;
}

/* DEEPSEEK STATUS BAR */
QStatusBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2D3748, stop:1 #4A5568);
    border-top: 2px solid rgba(56, 178, 172, 0.3);
    color: #CBD5E0;
    font-size: 9pt;
    font-family: "Inter", sans-serif;
    padding: 8px;
}

/* INTELLIGENT TOOLTIPS */
QToolTip {
    background: rgba(30, 41, 59, 0.98);
    color: #38B2AC;
    border: 1px solid rgba(56, 178, 172, 0.5);
    border-radius: 10px;
    padding: 12px;
    font-size: 10pt;
    font-family: "Inter", sans-serif;
    backdrop-filter: blur(5px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
}

/* NEURAL MENUS */
QMenu {
    background: rgba(30, 41, 59, 0.97);
    border: 2px solid rgba(56, 178, 172, 0.4);
    border-radius: 14px;
    color: #E2E8F0;
    font-family: "Inter", sans-serif;
    padding: 8px;
}

QMenu::item {
    padding: 10px 32px;
    border-radius: 8px;
    margin: 2px;
}

QMenu::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #38B2AC, stop:1 #4299E1);
    color: white;
}

QMenu::separator {
    height: 1px;
    background: rgba(56, 178, 172, 0.3);
    margin: 8px 16px;
}

/* DEEPSEEK SPECIAL EFFECTS */
QLabel[class="neural-connection"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(56, 178, 172, 0.1), stop:1 rgba(66, 153, 225, 0.1));
    border-left: 4px solid #38B2AC;
    border-radius: 8px;
    padding: 12px;
    color: #E2E8F0;
    font-weight: 600;
}

QLabel[class="ai-processing"] {
    color: #4299E1;
    font-weight: 700;
    padding: 8px 16px;
    background: rgba(66, 153, 225, 0.1);
    border-radius: 10px;
    border: 1px dashed rgba(66, 153, 225, 0.3);
}

QLabel[class="deepseek-badge"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #805AD5, stop:1 #6B46C1);
    color: white;
    font-weight: 700;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 10pt;
}

/* PULSING AI INDICATOR */
QLabel[class="ai-active"] {
    color: #48BB78;
    animation: pulse 2s infinite;
    font-weight: 700;
}

@keyframes pulse {
    0% { opacity: 0.7; }
    50% { opacity: 1; }
    100% { opacity: 0.7; }
}
These three themes provide:

DACOS Neon Professional - Primary production theme with professional gradients

DACOS Matrix Dark - Cyberpunk-inspired theme for data-heavy operations

DeepSeek Exclusive Theme - AI-enhanced theme with neural network styling, intelligent gradients, and modern typography

The DeepSeek theme features unique AI-inspired design elements, smooth animations, and a sophisticated color palette that represents intelligent systems working in harmony.