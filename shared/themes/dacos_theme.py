"""
DACOS Unified Theme for AutoDiag Pro
Complete theme implementation with all styling rules
Location: shared/themes/dacos_theme.py
Version: 3.1.2
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ===== DACOS COLOR CONSTANTS =====
DACOS_THEME = {
    "bg_main": "#0A1A1A",
    "bg_panel": "#0D2323", 
    "bg_card": "#134F4A",
    "accent": "#21F5C1",
    "glow": "#2AF5D1",
    "text_main": "#E8F4F2",
    "text_muted": "#9ED9CF",
    "error": "#FF4D4D",
    "success": "#10B981",
    "warning": "#F59E0B",
    "info": "#3B82F6"
}

# ===== COMPLETE DACOS STYLESHEET =====
DACOS_STYLESHEET = f"""
/* =====================================================================
   DACOS Unified Theme - AutoDiag Pro v3.1.2
   Enhanced teal futuristic design with glassmorphism
   ===================================================================== */

/* ===== MAIN APPLICATION ===== */
QMainWindow, QDialog, QWidget {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {DACOS_THEME['bg_main']},
                                stop:0.5 {DACOS_THEME['bg_panel']}, 
                                stop:1 {DACOS_THEME['bg_main']});
    color: {DACOS_THEME['text_main']};
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 10pt;
}}

QWidget#NeonBackground {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {DACOS_THEME['bg_main']},
                                stop:0.5 {DACOS_THEME['bg_panel']}, 
                                stop:1 {DACOS_THEME['bg_main']});
}}

/* ===== GLASSMORPHIC CARDS ===== */
QFrame[class="glass-card"], QWidget[class="glass-card"] {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 rgba(19, 79, 74, 0.92),
                                stop:1 rgba(11, 46, 43, 0.92));
    border: 1.5px solid rgba(42, 245, 209, 0.5);
    border-radius: 18px;
    padding: 15px;
}}

QFrame[class="glass-card"]:hover, QWidget[class="glass-card"]:hover {{
    border: 1.5px solid {DACOS_THEME['glow']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 rgba(25, 95, 90, 0.95),
                                stop:1 rgba(15, 55, 50, 0.95));
}}

/* ===== BUTTONS ===== */
QPushButton {{
    background: rgba(33, 245, 193, 0.15);
    color: {DACOS_THEME['text_main']};
    border: 1.5px solid {DACOS_THEME['accent']};
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: bold;
    font-size: 11pt;
    min-height: 35px;
}}

QPushButton:hover {{
    background: rgba(33, 245, 193, 0.35);
    border-color: {DACOS_THEME['glow']};
}}

QPushButton:pressed {{
    background: rgba(33, 245, 193, 0.25);
}}

QPushButton:disabled {{
    background: rgba(100, 100, 100, 0.2);
    color: rgba(232, 244, 242, 0.4);
    border-color: rgba(148, 163, 184, 0.3);
}}

/* Primary Action Buttons */
QPushButton[class="primary"], QPushButton[class="primary-btn"] {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 {DACOS_THEME['accent']},
                                stop:1 {DACOS_THEME['glow']});
    color: {DACOS_THEME['bg_main']};
    font-weight: bold;
    border: none;
}}

QPushButton[class="primary"]:hover, QPushButton[class="primary-btn"]:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 {DACOS_THEME['glow']},
                                stop:1 {DACOS_THEME['accent']});
}}

QPushButton[class="primary"]:pressed, QPushButton[class="primary-btn"]:pressed {{
    background: {DACOS_THEME['accent']};
}}

/* Success Buttons */
QPushButton[class="success"], QPushButton[class="success-btn"] {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 {DACOS_THEME['success']},
                                stop:1 #059669);
    color: white;
    border: none;
    font-weight: bold;
}}

QPushButton[class="success"]:hover, QPushButton[class="success-btn"]:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #059669,
                                stop:1 #047857);
}}

/* Warning Buttons */
QPushButton[class="warning"], QPushButton[class="warning-btn"] {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 {DACOS_THEME['warning']},
                                stop:1 #D97706);
    color: white;
    border: none;
    font-weight: bold;
}}

QPushButton[class="warning"]:hover, QPushButton[class="warning-btn"]:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #D97706,
                                stop:1 #B45309);
}}

/* Danger Buttons */
QPushButton[class="danger"], QPushButton[class="danger-btn"] {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 {DACOS_THEME['error']},
                                stop:1 #DC2626);
    color: white;
    border: none;
    font-weight: bold;
}}

QPushButton[class="danger"]:hover, QPushButton[class="danger-btn"]:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #DC2626,
                                stop:1 #B91C1C);
}}

/* Info Buttons */
QPushButton[class="info"], QPushButton[class="info-btn"] {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 {DACOS_THEME['info']},
                                stop:1 #2563EB);
    color: white;
    border: none;
    font-weight: bold;
}}

/* ===== TABS ===== */
QTabWidget::pane {{
    border: 1px solid rgba(33, 245, 193, 0.15);
    background: {DACOS_THEME['bg_panel']};
    border-radius: 16px;
    margin-top: 6px;
}}

QTabBar {{
    background: {DACOS_THEME['bg_panel']};
}}

QTabBar::tab {{
    background: {DACOS_THEME['bg_card']};
    color: {DACOS_THEME['text_muted']};
    padding: 14px 28px;
    min-width: 140px;
    border-top-left-radius: 14px;
    border-top-right-radius: 14px;
    font-weight: 600;
    margin-right: 4px;
}}

QTabBar::tab:selected {{
    background: {DACOS_THEME['accent']};
    color: #0B2E2B;
    font-weight: bold;
}}

QTabBar::tab:hover:!selected {{
    background: rgba(33, 245, 193, 0.25);
    color: {DACOS_THEME['glow']};
}}

QTabBar::tab:disabled {{
    background: rgba(100, 100, 100, 0.2);
    color: rgba(158, 217, 207, 0.4);
}}

/* ===== LABELS ===== */
QLabel {{
    color: {DACOS_THEME['text_main']};
    background: transparent;
}}

/* Hero Titles */
QLabel[class="hero-title"] {{
    color: {DACOS_THEME['accent']};
    font-size: 18pt;
    font-weight: bold;
}}

/* Tab Titles */
QLabel[class="tab-title"] {{
    color: {DACOS_THEME['accent']};
    font-size: 16pt;
    font-weight: bold;
    padding: 10px 0;
}}

/* Section Titles */
QLabel[class="section-title"] {{
    color: {DACOS_THEME['text_main']};
    font-size: 12pt;
    font-weight: bold;
    padding: 5px 0;
}}

/* Subtitles */
QLabel[class="subtitle"] {{
    color: {DACOS_THEME['text_muted']};
    font-size: 10pt;
    padding: 5px 0;
}}

/* Stat Labels */
QLabel[class="stat-label"] {{
    color: {DACOS_THEME['text_muted']};
    font-size: 11pt;
    font-weight: bold;
}}

QLabel[class="stat-value"] {{
    color: {DACOS_THEME['accent']};
    font-size: 14pt;
    font-weight: bold;
}}

/* Status Labels */
QLabel[class="status-good"] {{
    color: {DACOS_THEME['success']};
    font-weight: bold;
}}

QLabel[class="status-warning"] {{
    color: {DACOS_THEME['warning']};
    font-weight: bold;
}}

QLabel[class="status-error"] {{
    color: {DACOS_THEME['error']};
    font-weight: bold;
}}

QLabel[class="status-label"] {{
    color: {DACOS_THEME['text_muted']};
    font-size: 9pt;
    padding: 5px 0;
}}

/* Form Labels */
QLabel[class="form-label"] {{
    color: {DACOS_THEME['accent']};
    font-weight: bold;
    font-size: 10pt;
}}

/* ===== INPUT FIELDS ===== */
QLineEdit, QSpinBox, QDoubleSpinBox {{
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(148, 163, 184, 0.5);
    border-radius: 8px;
    color: {DACOS_THEME['text_main']};
    padding: 8px 12px;
    font-size: 10pt;
    selection-background-color: {DACOS_THEME['accent']};
    selection-color: {DACOS_THEME['bg_main']};
}}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 2px solid {DACOS_THEME['accent']};
    background: rgba(255, 255, 255, 0.15);
}}

QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {{
    background: rgba(100, 100, 100, 0.1);
    color: rgba(232, 244, 242, 0.4);
    border-color: rgba(148, 163, 184, 0.2);
}}

QLineEdit::placeholder {{
    color: rgba(158, 217, 207, 0.5);
}}

/* SpinBox Buttons */
QSpinBox::up-button, QDoubleSpinBox::up-button {{
    background: rgba(33, 245, 193, 0.2);
    border: none;
    border-top-right-radius: 6px;
}}

QSpinBox::down-button, QDoubleSpinBox::down-button {{
    background: rgba(33, 245, 193, 0.2);
    border: none;
    border-bottom-right-radius: 6px;
}}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
    background: rgba(33, 245, 193, 0.4);
}}

/* ===== CHECKBOXES ===== */
QCheckBox {{
    color: {DACOS_THEME['text_main']};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid {DACOS_THEME['accent']};
    background: rgba(255, 255, 255, 0.1);
}}

QCheckBox::indicator:checked {{
    background: {DACOS_THEME['accent']};
    border-color: {DACOS_THEME['glow']};
}}

QCheckBox::indicator:hover {{
    border-color: {DACOS_THEME['glow']};
}}

/* ===== RADIO BUTTONS ===== */
QRadioButton {{
    color: {DACOS_THEME['text_main']};
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 10px;
    border: 2px solid {DACOS_THEME['accent']};
    background: rgba(255, 255, 255, 0.1);
}}

QRadioButton::indicator:checked {{
    background: {DACOS_THEME['accent']};
    border-color: {DACOS_THEME['glow']};
}}

/* ===== PROGRESS BARS ===== */
QProgressBar {{
    border: none;
    border-radius: 8px;
    background: rgba(19, 79, 74, 0.5);
    text-align: center;
    color: {DACOS_THEME['accent']};
    font-weight: bold;
    min-height: 20px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {DACOS_THEME['accent']},
                                stop:0.5 {DACOS_THEME['glow']},
                                stop:1 {DACOS_THEME['accent']});
    border-radius: 8px;
    border: 1px solid rgba(33, 245, 193, 0.3);
}}

/* ===== SCROLLBARS ===== */
QScrollBar:vertical {{
    background: rgba(11, 46, 43, 0.4);
    width: 14px;
    border-radius: 7px;
    margin: 0px;
}}

QScrollBar:horizontal {{
    background: rgba(11, 46, 43, 0.4);
    height: 14px;
    border-radius: 7px;
    margin: 0px;
}}

QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
    background: {DACOS_THEME['accent']};
    border-radius: 7px;
    min-height: 30px;
    min-width: 30px;
}}

QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
    background: {DACOS_THEME['glow']};
}}

QScrollBar::add-line, QScrollBar::sub-line {{
    border: none;
    background: none;
}}

QScrollBar::add-page, QScrollBar::sub-page {{
    background: none;
}}

/* ===== SCROLL AREA ===== */
QScrollArea {{
    border: 1px solid rgba(42, 245, 209, 0.2);
    border-radius: 8px;
    background: transparent;
}}

/* ===== TABLES ===== */
QTableWidget {{
    background: rgba(19, 79, 74, 0.3);
    border: 1px solid rgba(42, 245, 209, 0.2);
    border-radius: 8px;
    outline: none;
    color: {DACOS_THEME['text_main']};
    gridline-color: rgba(42, 245, 209, 0.1);
    selection-background-color: rgba(33, 245, 193, 0.2);
}}

QTableWidget::item {{
    padding: 8px 12px;
    border-bottom: 1px solid rgba(42, 245, 209, 0.1);
}}

QTableWidget::item:selected {{
    background: rgba(33, 245, 193, 0.2);
    color: {DACOS_THEME['accent']};
    border-radius: 4px;
}}

QTableWidget::item:hover {{
    background: rgba(33, 245, 193, 0.1);
}}

QTableWidget QTableCornerButton::section {{
    background: rgba(19, 79, 74, 0.5);
    border: none;
}}

/* ===== LIST WIDGETS ===== */
QListWidget {{
    background: rgba(19, 79, 74, 0.3);
    border: 1px solid rgba(42, 245, 209, 0.2);
    border-radius: 8px;
    outline: none;
    color: {DACOS_THEME['text_main']};
    padding: 5px;
}}

QListWidget::item {{
    padding: 8px 12px;
    border-bottom: 1px solid rgba(42, 245, 209, 0.1);
    border-radius: 4px;
}}

QListWidget::item:selected {{
    background: rgba(33, 245, 193, 0.2);
    color: {DACOS_THEME['accent']};
}}

QListWidget::item:hover {{
    background: rgba(33, 245, 193, 0.1);
}}

/* ===== TREE VIEW ===== */
QTreeView {{
    background: rgba(19, 79, 74, 0.3);
    border: 1px solid rgba(42, 245, 209, 0.2);
    border-radius: 8px;
    outline: none;
    color: {DACOS_THEME['text_main']};
}}

QTreeView::item {{
    padding: 8px 12px;
    border-bottom: 1px solid rgba(42, 245, 209, 0.1);
}}

QTreeView::item:selected {{
    background: rgba(33, 245, 193, 0.2);
    color: {DACOS_THEME['accent']};
}}

QTreeView::item:hover {{
    background: rgba(33, 245, 193, 0.1);
}}

QTreeView::branch {{
    background: transparent;
}}

/* ===== HEADERS ===== */
QHeaderView {{
    background: transparent;
}}

QHeaderView::section {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(33, 245, 193, 0.2),
                                stop:1 rgba(33, 245, 193, 0.1));
    color: {DACOS_THEME['accent']};
    padding: 10px;
    border: none;
    font-weight: 600;
    border-bottom: 1px solid rgba(33, 245, 193, 0.3);
}}

QHeaderView::section:hover {{
    background: rgba(33, 245, 193, 0.3);
}}

QHeaderView::section:pressed {{
    background: rgba(33, 245, 193, 0.4);
}}

/* ===== COMBO BOXES ===== */
QComboBox {{
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(148, 163, 184, 0.5);
    border-radius: 6px;
    padding: 6px 10px;
    color: {DACOS_THEME['text_main']};
    min-height: 18px;
    font-size: 9pt;
}}

QComboBox:hover {{
    border: 1px solid {DACOS_THEME['accent']};
    background: rgba(255, 255, 255, 0.15);
}}

QComboBox:focus {{
    border: 2px solid {DACOS_THEME['accent']};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid {DACOS_THEME['accent']};
    margin-right: 5px;
}}

QComboBox QAbstractItemView {{
    background: rgba(13, 35, 35, 0.98);
    border: 1px solid {DACOS_THEME['accent']};
    color: {DACOS_THEME['text_main']};
    selection-background-color: rgba(33, 245, 193, 0.3);
    selection-color: {DACOS_THEME['text_main']};
    outline: none;
    padding: 5px;
}}

QComboBox QAbstractItemView::item {{
    min-height: 30px;
    padding: 5px;
}}

QComboBox QAbstractItemView::item:hover {{
    background: rgba(33, 245, 193, 0.2);
}}

/* ===== SLIDERS ===== */
QSlider::groove:horizontal {{
    background: rgba(19, 79, 74, 0.5);
    height: 8px;
    border-radius: 4px;
}}

QSlider::handle:horizontal {{
    background: {DACOS_THEME['accent']};
    width: 20px;
    height: 20px;
    margin: -6px 0;
    border-radius: 10px;
}}

QSlider::handle:horizontal:hover {{
    background: {DACOS_THEME['glow']};
}}

QSlider::groove:vertical {{
    background: rgba(19, 79, 74, 0.5);
    width: 8px;
    border-radius: 4px;
}}

QSlider::handle:vertical {{
    background: {DACOS_THEME['accent']};
    height: 20px;
    width: 20px;
    margin: 0 -6px;
    border-radius: 10px;
}}

/* ===== GROUP BOXES ===== */
QGroupBox {{
    font-weight: bold;
    color: {DACOS_THEME['accent']};
    border: 1px solid rgba(42, 245, 209, 0.3);
    border-radius: 8px;
    margin-top: 15px;
    padding-top: 15px;
    background: rgba(19, 79, 74, 0.3);
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 10px;
    background: transparent;
    color: {DACOS_THEME['accent']};
    font-weight: bold;
    font-size: 11pt;
}}

/* ===== TEXT EDIT ===== */
QTextEdit, QPlainTextEdit {{
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(148, 163, 184, 0.5);
    border-radius: 8px;
    color: {DACOS_THEME['text_main']};
    padding: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 10pt;
    selection-background-color: {DACOS_THEME['accent']};
    selection-color: {DACOS_THEME['bg_main']};
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid {DACOS_THEME['accent']};
    background: rgba(255, 255, 255, 0.15);
}}

/* ===== MENUS ===== */
QMenuBar {{
    background: rgba(13, 35, 35, 0.95);
    color: {DACOS_THEME['text_main']};
    border-bottom: 1px solid rgba(42, 245, 209, 0.2);
}}

QMenuBar::item {{
    padding: 8px 15px;
    background: transparent;
}}

QMenuBar::item:selected {{
    background: rgba(33, 245, 193, 0.2);
    color: {DACOS_THEME['accent']};
}}

QMenu {{
    background: rgba(13, 35, 35, 0.98);
    border: 1px solid {DACOS_THEME['accent']};
    color: {DACOS_THEME['text_main']};
    padding: 5px;
}}

QMenu::item {{
    padding: 8px 30px 8px 15px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background: rgba(33, 245, 193, 0.2);
    color: {DACOS_THEME['accent']};
}}

QMenu::separator {{
    height: 1px;
    background: rgba(42, 245, 209, 0.2);
    margin: 5px 10px;
}}

/* ===== TOOL BAR ===== */
QToolBar {{
    background: rgba(13, 35, 35, 0.95);
    border: none;
    padding: 5px;
    spacing: 5px;
}}

QToolBar::separator {{
    background: rgba(42, 245, 209, 0.2);
    width: 1px;
    margin: 5px;
}}

QToolButton {{
    background: rgba(33, 245, 193, 0.1);
    border: 1px solid rgba(42, 245, 209, 0.3);
    border-radius: 6px;
    padding: 8px;
    color: {DACOS_THEME['text_main']};
}}

QToolButton:hover {{
    background: rgba(33, 245, 193, 0.25);
    border-color: {DACOS_THEME['accent']};
}}

QToolButton:pressed {{
    background: rgba(33, 245, 193, 0.35);
}}

/* ===== STATUS BAR ===== */
QStatusBar {{
    background: rgba(19, 79, 74, 0.5);
    color: {DACOS_THEME['text_muted']};
    border-top: 1px solid rgba(42, 245, 209, 0.2);
    padding: 5px;
}}

QStatusBar::item {{
    border: none;
}}

/* ===== TOOLTIP ===== */
QToolTip {{
    background: rgba(13, 35, 35, 0.98);
    color: {DACOS_THEME['text_main']};
    border: 1px solid {DACOS_THEME['accent']};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 10pt;
}}

/* ===== DOCK WIDGET ===== */
QDockWidget {{
    color: {DACOS_THEME['text_main']};
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
}}

QDockWidget::title {{
    background: rgba(19, 79, 74, 0.8);
    padding: 8px;
    border-bottom: 1px solid rgba(42, 245, 209, 0.3);
}}

/* ===== SPLITTER ===== */
QSplitter::handle {{
    background: rgba(42, 245, 209, 0.2);
}}

QSplitter::handle:hover {{
    background: {DACOS_THEME['accent']};
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

/* ===== MESSAGE BOX ===== */
QMessageBox {{
    background: {DACOS_THEME['bg_panel']};
}}

QMessageBox QLabel {{
    color: {DACOS_THEME['text_main']};
    min-width: 300px;
}}

QMessageBox QPushButton {{
    min-width: 80px;
    min-height: 30px;
}}

/* ===== CALENDAR WIDGET ===== */
QCalendarWidget {{
    background: rgba(13, 35, 35, 0.95);
    color: {DACOS_THEME['text_main']};
}}

QCalendarWidget QToolButton {{
    background: transparent;
    color: {DACOS_THEME['accent']};
}}

QCalendarWidget QMenu {{
    background: rgba(13, 35, 35, 0.98);
}}

QCalendarWidget QAbstractItemView:enabled {{
    background: rgba(19, 79, 74, 0.3);
    selection-background-color: {DACOS_THEME['accent']};
    selection-color: {DACOS_THEME['bg_main']};
}}

/* ===== DIAL ===== */
QDial {{
    background: rgba(19, 79, 74, 0.3);
}}

/* ===== SIZE GRIP ===== */
QSizeGrip {{
    background: transparent;
    width: 16px;
    height: 16px;
}}

/* ===== FOCUS STYLING ===== */
*:focus {{
    outline: none;
}}

/* ===== CUSTOM STYLING ===== */

/* Custom Dashboard Widgets */
QWidget[class="dashboard-widget"] {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 rgba(19, 79, 74, 0.8),
                                stop:1 rgba(11, 46, 43, 0.8));
    border: 2px solid rgba(42, 245, 209, 0.4);
    border-radius: 16px;
    padding: 20px;
}}

QWidget[class="dashboard-widget"]:hover {{
    border: 2px solid {DACOS_THEME['glow']};
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 rgba(25, 95, 90, 0.85),
                                stop:1 rgba(15, 55, 50, 0.85));
}}

/* Custom Progress Indicators */
QWidget[class="progress-indicator"] {{
    background: transparent;
    border: 3px solid rgba(42, 245, 209, 0.3);
    border-radius: 50px;
}}

QWidget[class="progress-indicator"]::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {DACOS_THEME['accent']},
                                stop:1 {DACOS_THEME['glow']});
    border-radius: 50px;
}}

/* Custom Separators */
QFrame[class="separator"] {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 transparent,
                                stop:0.5 {DACOS_THEME['accent']},
                                stop:1 transparent);
    max-height: 1px;
    min-height: 1px;
}}

QFrame[class="separator-vertical"] {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 transparent,
                                stop:0.5 {DACOS_THEME['accent']},
                                stop:1 transparent);
    max-width: 1px;
    min-width: 1px;
}}

/* Custom Badges */
QLabel[class="badge"], QPushButton[class="badge"] {{
    background: {DACOS_THEME['accent']};
    color: {DACOS_THEME['bg_main']};
    border-radius: 12px;
    padding: 4px 12px;
    font-size: 9pt;
    font-weight: bold;
    min-height: 24px;
}}

QLabel[class="badge-success"] {{
    background: {DACOS_THEME['success']};
    color: white;
}}

QLabel[class="badge-warning"] {{
    background: {DACOS_THEME['warning']};
    color: white;
}}

QLabel[class="badge-error"] {{
    background: {DACOS_THEME['error']};
    color: white;
}}

QLabel[class="badge-info"] {{
    background: {DACOS_THEME['info']};
    color: white;
}}

/* Custom Charts */
QWidget[class="chart-container"] {{
    background: rgba(19, 79, 74, 0.4);
    border: 1px solid rgba(42, 245, 209, 0.3);
    border-radius: 12px;
    padding: 15px;
}}

/* Custom Navigation */
QWidget[class="nav-panel"] {{
    background: rgba(13, 35, 35, 0.95);
    border-right: 1px solid rgba(42, 245, 209, 0.2);
}}

QPushButton[class="nav-button"] {{
    background: transparent;
    border: none;
    text-align: left;
    padding: 12px 20px;
    border-radius: 8px;
    margin: 2px 5px;
}}

QPushButton[class="nav-button"]:hover {{
    background: rgba(33, 245, 193, 0.15);
}}

QPushButton[class="nav-button"]:checked {{
    background: rgba(33, 245, 193, 0.25);
    color: {DACOS_THEME['accent']};
}}

/* Custom Toggle Switch */
QCheckBox[class="toggle-switch"]::indicator {{
    width: 50px;
    height: 25px;
    border-radius: 12px;
    border: 2px solid {DACOS_THEME['accent']};
}}

QCheckBox[class="toggle-switch"]::indicator:checked {{
    background: {DACOS_THEME['accent']};
}}

QCheckBox[class="toggle-switch"]::indicator:unchecked {{
    background: rgba(255, 255, 255, 0.1);
}}
"""

# ===== THEME UTILITY FUNCTIONS =====
def apply_dacos_theme(app):
    """
    Apply DACOS theme to QApplication instance
    """
    try:
        app.setStyle('Fusion')
        app.setStyleSheet(DACOS_STYLESHEET)
        logger.info("DACOS theme applied successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to apply DACOS theme: {e}")
        return False

def get_dacos_color(color_name):
    """
    Get color from DACOS theme palette
    """
    return DACOS_THEME.get(color_name, "#FFFFFF")

def get_stylesheet():
    """
    Get the complete DACOS stylesheet
    """
    return DACOS_STYLESHEET

# ===== THEME VALIDATION =====
def validate_theme():
    """
    Validate that all theme components are properly defined
    """
    required_colors = ['bg_main', 'bg_panel', 'bg_card', 'accent', 'glow', 
                      'text_main', 'text_muted', 'error', 'success', 'warning', 'info']
    
    missing_colors = [color for color in required_colors if color not in DACOS_THEME]
    
    if missing_colors:
        logger.warning(f"Missing color definitions: {missing_colors}")
        return False
    
    if not DACOS_STYLESHEET or len(DACOS_STYLESHEET.strip()) < 100:
        logger.warning("Stylesheet appears to be incomplete")
        return False
    
    logger.info("DACOS theme validation passed")
    return True

# Initialize theme validation on import
if __name__ != "__main__":
    validate_theme()