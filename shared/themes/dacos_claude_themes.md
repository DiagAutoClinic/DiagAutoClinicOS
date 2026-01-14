# dacos_cyber_teal_suite.py - THREE COMPLETE QT STYLESHEETS FOR AUTODIAG PRO
"""
DACOS Theme Suite - Professional Qt Stylesheets
================================================
Three production-ready themes for AutoDiag Pro diagnostic suite:
   - **DACOS Cyber-Teal**: The default, primary theme (`dacos_cyber_teal.py`).
   - **DACOS Industrial**: A robust, high-contrast theme (`dacos_industrial.py`).
   - **DACOS Modern**: A clean, modern variation (`dacos_modern.py`).

All themes feature:
- Glass morphism effects
- Gradient backgrounds
- Smooth animations
- Professional color palettes
- Complete widget coverage
- Optimized for diagnostic applications
"""

# ============================================================================
# THEME 1: DACOS TEAL FUSION (ORIGINAL)
# ============================================================================
DACOS_TEAL_FUSION = """
/* ========================================
   DACOS TEAL FUSION - ORIGINAL THEME
   Teal/Cyan glass morphism with holographic accents
   ======================================== */

/* === MAIN WINDOW & GLOBAL === */
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0A1A1A, stop:0.3 #0D2323, stop:0.7 #0D2323, stop:1 #0A1A1A);
    color: #E8F4F2;
    font-family: "Segoe UI", "Roboto", "Arial", sans-serif;
    font-size: 10pt;
}

QWidget {
    background: transparent;
    color: #E8F4F2;
    font-family: "Segoe UI", "Roboto", "Arial", sans-serif;
}

/* === SCROLLBAR === */
QScrollBar:vertical {
    background: rgba(13, 35, 35, 0.5);
    width: 12px;
    border-radius: 6px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #21F5C1, stop:1 #2AF5D1);
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #2AF5D1;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: rgba(13, 35, 35, 0.5);
    height: 12px;
    border-radius: 6px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #21F5C1, stop:1 #2AF5D1);
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: #2AF5D1;
}

/* === FRAMES & CONTAINERS === */
QFrame[class="glass-card"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(19, 79, 74, 0.95), 
        stop:0.5 rgba(13, 35, 35, 0.92),
        stop:1 rgba(19, 79, 74, 0.95));
    border: 2px solid rgba(33, 245, 193, 0.5);
    border-radius: 16px;
    padding: 20px;
}

QFrame[class="glass-card"]:hover {
    border: 2px solid rgba(42, 245, 209, 0.7);
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(19, 79, 74, 1.0), 
        stop:0.5 rgba(13, 35, 35, 0.95),
        stop:1 rgba(19, 79, 74, 1.0));
}

QGroupBox {
    background: rgba(13, 35, 35, 0.7);
    border: 2px solid rgba(33, 245, 193, 0.4);
    border-radius: 12px;
    padding: 20px 10px 10px 10px;
    margin-top: 12px;
    font-weight: bold;
    color: #21F5C1;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 15px;
    padding: 5px 15px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(33, 245, 193, 0.3), 
        stop:0.5 rgba(42, 245, 209, 0.5),
        stop:1 rgba(33, 245, 193, 0.3));
    border-radius: 8px;
    color: #E8F4F2;
}

/* === BUTTONS === */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #21F5C1, stop:0.5 #1FD9B0, stop:1 #21F5C1);
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    color: #0A1A1A;
    font-weight: bold;
    font-size: 10pt;
    min-height: 40px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #2AF5D1, stop:0.5 #25E5C0, stop:1 #2AF5D1);
    border: 2px solid rgba(255, 255, 255, 0.3);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1AC9A1, stop:1 #18B591);
    padding-top: 14px;
    padding-bottom: 10px;
}

QPushButton:disabled {
    background: rgba(33, 245, 193, 0.2);
    color: rgba(232, 244, 242, 0.3);
}

/* Button Variants */
QPushButton[class="primary"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #21F5C1, stop:1 #1AC9A1);
    color: #0A1A1A;
    font-weight: bold;
}

QPushButton[class="primary"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #2AFFDB, stop:1 #20D9B1);
    box-shadow: 0 0 20px rgba(33, 245, 193, 0.5);
}

QPushButton[class="success"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #10B981, stop:1 #059669);
    color: white;
}

QPushButton[class="success"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #14D899, stop:1 #0AAF77);
}

QPushButton[class="warning"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #F59E0B, stop:1 #D97706);
    color: white;
}

QPushButton[class="warning"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FBBF24, stop:1 #F59E0B);
}

QPushButton[class="danger"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FF4D4D, stop:1 #DC2626);
    color: white;
}

QPushButton[class="danger"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FF6B6B, stop:1 #EF4444);
}

/* === TABS === */
QTabWidget::pane {
    border: 2px solid rgba(33, 245, 193, 0.4);
    background: rgba(13, 35, 35, 0.5);
    border-radius: 16px;
    padding: 10px;
    top: -2px;
}

QTabBar::tab {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(19, 79, 74, 0.8), 
        stop:1 rgba(13, 35, 35, 0.9));
    color: #9ED9CF;
    padding: 14px 28px;
    border-radius: 10px 10px 0 0;
    margin: 2px 1px 0 1px;
    font-weight: bold;
    font-size: 10pt;
    border: 2px solid rgba(33, 245, 193, 0.2);
    border-bottom: none;
    min-width: 120px;
}

QTabBar::tab:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(33, 245, 193, 0.3), 
        stop:1 rgba(19, 79, 74, 0.9));
    color: #E8F4F2;
    border: 2px solid rgba(42, 245, 209, 0.4);
    border-bottom: none;
}

QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #21F5C1, stop:1 #1AC9A1);
    color: #0A1A1A;
    border: 2px solid #2AF5D1;
    border-bottom: none;
    padding-bottom: 16px;
}

QTabBar::tab:!selected {
    margin-top: 4px;
}

/* === INPUT FIELDS === */
QLineEdit, QTextEdit, QPlainTextEdit {
    background: rgba(13, 35, 35, 0.8);
    border: 2px solid rgba(33, 245, 193, 0.3);
    border-radius: 10px;
    padding: 10px 15px;
    color: #E8F4F2;
    selection-background-color: rgba(33, 245, 193, 0.4);
    font-size: 10pt;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #21F5C1;
    background: rgba(19, 79, 74, 0.5);
}

QLineEdit:disabled, QTextEdit:disabled {
    background: rgba(13, 35, 35, 0.4);
    color: rgba(232, 244, 242, 0.4);
    border: 2px solid rgba(33, 245, 193, 0.1);
}

/* === COMBOBOX === */
QComboBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(19, 79, 74, 0.9), 
        stop:1 rgba(13, 35, 35, 0.9));
    border: 2px solid rgba(33, 245, 193, 0.4);
    border-radius: 10px;
    padding: 10px 15px;
    color: #E8F4F2;
    min-width: 120px;
    font-weight: 500;
}

QComboBox:hover {
    border: 2px solid rgba(42, 245, 209, 0.6);
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(33, 245, 193, 0.2), 
        stop:1 rgba(19, 79, 74, 0.9));
}

QComboBox:on {
    border: 2px solid #21F5C1;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #21F5C1;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background: rgba(13, 35, 35, 0.98);
    border: 2px solid #21F5C1;
    border-radius: 8px;
    padding: 5px;
    color: #E8F4F2;
    selection-background-color: rgba(33, 245, 193, 0.4);
    outline: none;
}

QComboBox QAbstractItemView::item {
    padding: 8px 15px;
    border-radius: 6px;
    min-height: 30px;
}

QComboBox QAbstractItemView::item:hover {
    background: rgba(33, 245, 193, 0.3);
    color: #2AF5D1;
}

QComboBox QAbstractItemView::item:selected {
    background: rgba(33, 245, 193, 0.5);
    color: #E8F4F2;
}

/* === SPINBOX === */
QSpinBox, QDoubleSpinBox {
    background: rgba(13, 35, 35, 0.8);
    border: 2px solid rgba(33, 245, 193, 0.3);
    border-radius: 10px;
    padding: 8px 12px;
    color: #E8F4F2;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #21F5C1;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    background: rgba(33, 245, 193, 0.2);
    border-radius: 5px;
    margin: 2px;
}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
    background: rgba(33, 245, 193, 0.4);
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    background: rgba(33, 245, 193, 0.2);
    border-radius: 5px;
    margin: 2px;
}

QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background: rgba(33, 245, 193, 0.4);
}

/* === TABLES === */
QTableWidget, QTableView {
    background: rgba(13, 35, 35, 0.7);
    alternate-background-color: rgba(19, 79, 74, 0.4);
    border: 2px solid rgba(33, 245, 193, 0.3);
    border-radius: 12px;
    gridline-color: rgba(33, 245, 193, 0.2);
    color: #E8F4F2;
    selection-background-color: rgba(33, 245, 193, 0.3);
}

QTableWidget::item, QTableView::item {
    padding: 8px;
    border: none;
}

QTableWidget::item:hover, QTableView::item:hover {
    background: rgba(33, 245, 193, 0.15);
}

QTableWidget::item:selected, QTableView::item:selected {
    background: rgba(33, 245, 193, 0.4);
    color: #E8F4F2;
}

QHeaderView::section {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(33, 245, 193, 0.3), 
        stop:1 rgba(19, 79, 74, 0.8));
    color: #E8F4F2;
    padding: 10px;
    border: none;
    border-right: 1px solid rgba(33, 245, 193, 0.2);
    border-bottom: 2px solid rgba(33, 245, 193, 0.4);
    font-weight: bold;
}

QHeaderView::section:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(42, 245, 209, 0.4), 
        stop:1 rgba(19, 79, 74, 0.9));
}

/* === LIST WIDGET === */
QListWidget {
    background: rgba(13, 35, 35, 0.7);
    border: 2px solid rgba(33, 245, 193, 0.3);
    border-radius: 12px;
    padding: 5px;
    color: #E8F4F2;
    outline: none;
}

QListWidget::item {
    padding: 10px 15px;
    border-radius: 8px;
    margin: 2px;
}

QListWidget::item:hover {
    background: rgba(33, 245, 193, 0.2);
}

QListWidget::item:selected {
    background: rgba(33, 245, 193, 0.4);
    color: #E8F4F2;
}

/* === LABELS === */
QLabel[class="hero-title"] {
    color: #21F5C1;
    font-size: 22pt;
    font-weight: bold;
    text-shadow: 0 0 20px rgba(33, 245, 193, 0.5);
}

QLabel[class="tab-title"] {
    color: #21F5C1;
    font-size: 18pt;
    font-weight: bold;
    text-shadow: 0 0 15px rgba(33, 245, 193, 0.4);
}

QLabel[class="section-title"] {
    color: #E8F4F2;
    font-size: 14pt;
    font-weight: bold;
}

QLabel[class="section-label"] {
    color: #9ED9CF;
    font-size: 10pt;
    font-weight: 500;
}

QLabel[class="subtitle"] {
    color: #9ED9CF;
    font-size: 9pt;
}

QLabel[class="status-label"] {
    color: #21F5C1;
    font-weight: bold;
    padding: 5px 10px;
}

/* === PROGRESS BAR === */
QProgressBar {
    background: rgba(13, 35, 35, 0.8);
    border: 2px solid rgba(33, 245, 193, 0.3);
    border-radius: 10px;
    text-align: center;
    color: #E8F4F2;
    font-weight: bold;
    min-height: 25px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #21F5C1, stop:0.5 #2AF5D1, stop:1 #21F5C1);
    border-radius: 8px;
}

/* === STATUS BAR === */
QStatusBar {
    background: rgba(10, 26, 26, 0.95);
    border-top: 2px solid rgba(33, 245, 193, 0.3);
    color: #9ED9CF;
}

QStatusBar::item {
    border: none;
}

/* === TOOLTIPS === */
QToolTip {
    background: rgba(19, 79, 74, 0.98);
    border: 2px solid #21F5C1;
    border-radius: 8px;
    padding: 8px 12px;
    color: #E8F4F2;
    font-size: 9pt;
}

/* === SLIDER === */
QSlider::groove:horizontal {
    background: rgba(13, 35, 35, 0.8);
    height: 8px;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #21F5C1, stop:1 #2AF5D1);
    width: 20px;
    height: 20px;
    margin: -6px 0;
    border-radius: 10px;
}

QSlider::handle:horizontal:hover {
    background: #2AF5D1;
}

/* === CHECKBOX & RADIO === */
QCheckBox, QRadioButton {
    color: #E8F4F2;
    spacing: 8px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid rgba(33, 245, 193, 0.5);
    border-radius: 5px;
    background: rgba(13, 35, 35, 0.8);
}

QCheckBox::indicator:hover, QRadioButton::indicator:hover {
    border: 2px solid #21F5C1;
    background: rgba(33, 245, 193, 0.1);
}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #21F5C1, stop:1 #1AC9A1);
    border: 2px solid #2AF5D1;
}

QRadioButton::indicator {
    border-radius: 10px;
}

/* === MENU === */
QMenu {
    background: rgba(13, 35, 35, 0.98);
    border: 2px solid #21F5C1;
    border-radius: 10px;
    padding: 5px;
}

QMenu::item {
    padding: 10px 30px 10px 20px;
    border-radius: 6px;
    color: #E8F4F2;
}

QMenu::item:selected {
    background: rgba(33, 245, 193, 0.3);
    color: #2AF5D1;
}

QMenu::separator {
    height: 2px;
    background: rgba(33, 245, 193, 0.3);
    margin: 5px 10px;
}

/* === MESSAGE BOX === */
QMessageBox {
    background: #0D2323;
}

QMessageBox QLabel {
    color: #E8F4F2;
}

QMessageBox QPushButton {
    min-width: 80px;
}
"""

# ============================================================================
# THEME 2: DACOS MIDNIGHT CARBON
# ============================================================================
DACOS_MIDNIGHT_CARBON = """
/* ========================================
   DACOS MIDNIGHT CARBON THEME
   Dark blue/purple with carbon fiber aesthetic
   ======================================== */

/* === MAIN WINDOW & GLOBAL === */
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0B0C1E, stop:0.3 #141633, stop:0.7 #141633, stop:1 #0B0C1E);
    color: #E3E8FF;
    font-family: "Segoe UI", "Roboto", "Arial", sans-serif;
    font-size: 10pt;
}

QWidget {
    background: transparent;
    color: #E3E8FF;
    font-family: "Segoe UI", "Roboto", "Arial", sans-serif;
}

/* === SCROLLBAR === */
QScrollBar:vertical {
    background: rgba(20, 22, 51, 0.5);
    width: 12px;
    border-radius: 6px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366F1, stop:1 #8B5CF6);
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #8B5CF6;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: rgba(20, 22, 51, 0.5);
    height: 12px;
    border-radius: 6px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #6366F1, stop:1 #8B5CF6);
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: #8B5CF6;
}

/* === FRAMES & CONTAINERS === */
QFrame[class="glass-card"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(30, 32, 75, 0.95), 
        stop:0.5 rgba(20, 22, 51, 0.92),
        stop:1 rgba(30, 32, 75, 0.95));
    border: 2px solid rgba(99, 102, 241, 0.5);
    border-radius: 16px;
    padding: 20px;
}

QFrame[class="glass-card"]:hover {
    border: 2px solid rgba(139, 92, 246, 0.7);
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(30, 32, 75, 1.0), 
        stop:0.5 rgba(20, 22, 51, 0.95),
        stop:1 rgba(30, 32, 75, 1.0));
}

QGroupBox {
    background: rgba(20, 22, 51, 0.7);
    border: 2px solid rgba(99, 102, 241, 0.4);
    border-radius: 12px;
    padding: 20px 10px 10px 10px;
    margin-top: 12px;
    font-weight: bold;
    color: #6366F1;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 15px;
    padding: 5px 15px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(99, 102, 241, 0.3), 
        stop:0.5 rgba(139, 92, 246, 0.5),
        stop:1 rgba(99, 102, 241, 0.3));
    border-radius: 8px;
    color: #E3E8FF;
}

/* === BUTTONS === */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #6366F1, stop:0.5 #5558D9, stop:1 #6366F1);
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    color: #FFFFFF;
    font-weight: bold;
    font-size: 10pt;
    min-height: 40px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #8B5CF6, stop:0.5 #7C3AED, stop:1 #8B5CF6);
    border: 2px solid rgba(255, 255, 255, 0.3);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #4F46E5, stop:1 #4338CA);
    padding-top: 14px;
    padding-bottom: 10px;
}

QPushButton:disabled {
    background: rgba(99, 102, 241, 0.2);
    color: rgba(227, 232, 255, 0.3);
}

/* Button Variants */
QPushButton[class="primary"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #6366F1, stop:1 #4F46E5);
    color: #FFFFFF;
    font-weight: bold;
}

QPushButton[class="primary"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #818CF8, stop:1 #6366F1);
}

QPushButton[class="success"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #10B981