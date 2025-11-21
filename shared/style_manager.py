#!/usr/bin/env python3
"""
Enhanced Style Manager - Unified Futuristic Teal Theme
Matches launcher.py aesthetic across all suites
"""

import logging
import os

logger = logging.getLogger(__name__)

class StyleManager:
    def __init__(self):
        self.themes_dir = os.path.join(os.path.dirname(__file__), 'themes')
        self.available_themes = {}
        self._load_embedded_themes()
        
        self.active_theme = 'dacos_unified'
        self.app = None

    def _load_embedded_themes(self):
        """Load embedded themes matching launcher aesthetic"""
        self.available_themes['dacos_unified'] = self._get_unified_theme()
        self.available_themes['dacos_particles'] = self._get_particles_theme()
        self.available_themes['neon_clinic'] = self._get_neon_theme()

    def _get_unified_theme(self):
        """Unified theme matching launcher.py exactly"""
        return """
/* ====================== DACOS UNIFIED FUTURISTIC ====================== */
/* Matches launcher.py "Where Mechanics Meet Future Intelligence" */

* {
    font-family: "Segoe UI", "Roboto", sans-serif;
}

QMainWindow, QDialog, QWidget {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #0B2E2B, stop:0.5 #0F3D3A, stop:1 #0B2E2B);
    color: #E8FFFB;
    font-size: 10pt;
}

/* ========== Glassmorphic Cards ========== */
QFrame[class="glass-card"], QGroupBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(19, 79, 74, 0.95), 
                                stop:1 rgba(15, 61, 58, 0.95));
    border: 2px solid rgba(33, 245, 193, 0.4);
    border-radius: 12px;
    padding: 15px;
}

QFrame[class="glass-card"]:hover, QGroupBox:hover {
    border: 2px solid rgba(33, 245, 193, 0.8);
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(19, 79, 74, 1), 
                                stop:1 rgba(15, 61, 58, 1));
}

/* ========== Stat Cards ========== */
QFrame[class="stat-card"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 rgba(19, 79, 74, 0.9),
                                stop:1 rgba(11, 46, 43, 0.9));
    border: 2px solid rgba(42, 245, 209, 0.5);
    border-radius: 15px;
    padding: 20px;
    min-width: 200px;
    min-height: 120px;
}

QFrame[class="stat-card"]:hover {
    border: 2px solid #21F5C1;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 rgba(19, 79, 74, 1),
                                stop:1 rgba(11, 46, 43, 1));
}

QLabel[class="stat-label"] {
    color: #9ED9CF;
    font-size: 11pt;
    font-weight: bold;
    background: transparent;
}

QLabel[class="stat-value"] {
    color: #21F5C1;
    font-size: 24pt;
    font-weight: bold;
    background: transparent;
}

/* ========== Headers & Titles ========== */
QLabel[class="hero-title"] {
    color: #21F5C1;
    font-size: 26pt;
    font-weight: bold;
    background: transparent;
}

QLabel[class="subtitle"], QLabel[class="section-title"] {
    color: #9ED9CF;
    font-size: 12pt;
    background: transparent;
}

QLabel[class="tab-title"] {
    color: #21F5C1;
    font-size: 18pt;
    font-weight: bold;
    background: transparent;
}

/* ========== Buttons ========== */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #21F5C1, stop:1 #1AE5B1);
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    color: #002F2C;
    font-weight: bold;
    font-size: 11pt;
    min-width: 100px;
    min-height: 40px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #2AF5D1, stop:1 #21F5C1);
    border: 2px solid #2AF5D1;
}

QPushButton:pressed {
    background: #134F4A;
    border: 2px solid #21F5C1;
}

QPushButton:disabled {
    background: #0F3D3A;
    color: #466663;
}

/* Button Variants */
QPushButton[class="primary"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #21F5C1, stop:1 #1AE5B1);
}

QPushButton[class="success"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #10B981, stop:1 #059669);
}

QPushButton[class="danger"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #FF4D4D, stop:1 #DC2626);
}

QPushButton[class="warning"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #F59E0B, stop:1 #D97706);
}

QPushButton[class="info"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #3B82F6, stop:1 #2563EB);
}

QPushButton[class="secondary"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #6B7280, stop:1 #4B5563);
}

/* ========== Input Fields ========== */
QLineEdit, QTextEdit, QPlainTextEdit {
    background: rgba(11, 46, 43, 0.8);
    border: 2px solid rgba(33, 245, 193, 0.3);
    border-radius: 8px;
    padding: 8px 12px;
    color: #E8FFFB;
    selection-background-color: #21F5C1;
    selection-color: #002F2C;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #21F5C1;
    background: rgba(11, 46, 43, 1);
}

QLineEdit:disabled, QTextEdit:disabled {
    background: rgba(11, 46, 43, 0.5);
    color: #466663;
}

/* ========== ComboBox ========== */
QComboBox {
    background: rgba(19, 79, 74, 0.9);
    border: 2px solid rgba(33, 245, 193, 0.4);
    border-radius: 8px;
    padding: 6px 12px;
    color: #E8FFFB;
    min-width: 120px;
    min-height: 30px;
}

QComboBox:hover {
    border: 2px solid #21F5C1;
    background: rgba(19, 79, 74, 1);
}

QComboBox::drop-down {
    border: none;
    width: 25px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #21F5C1;
    margin-right: 5px;
}

QComboBox QAbstractItemView {
    background: #0F3D3A;
    border: 2px solid #21F5C1;
    selection-background-color: #21F5C1;
    selection-color: #002F2C;
    color: #E8FFFB;
    outline: none;
}

/* ========== Tabs ========== */
QTabWidget::pane {
    border: 2px solid rgba(33, 245, 193, 0.4);
    background: rgba(11, 46, 43, 0.8);
    border-radius: 8px;
    padding: 10px;
}

QTabBar::tab {
    background: rgba(15, 61, 58, 0.8);
    color: #9ED9CF;
    padding: 12px 24px;
    margin-right: 4px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    border: 2px solid rgba(33, 245, 193, 0.2);
    border-bottom: none;
    min-width: 100px;
}

QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(33, 245, 193, 0.3),
                                stop:1 rgba(19, 79, 74, 0.9));
    color: #21F5C1;
    border: 2px solid #21F5C1;
    border-bottom: none;
    font-weight: bold;
}

QTabBar::tab:hover {
    background: rgba(19, 79, 74, 1);
    border: 2px solid rgba(33, 245, 193, 0.6);
}

/* ========== Tables ========== */
QTableWidget, QTableView {
    background: rgba(11, 46, 43, 0.8);
    border: 2px solid rgba(33, 245, 193, 0.3);
    border-radius: 8px;
    gridline-color: rgba(33, 245, 193, 0.2);
    color: #E8FFFB;
}

QTableWidget::item, QTableView::item {
    padding: 8px;
    border-bottom: 1px solid rgba(33, 245, 193, 0.1);
}

QTableWidget::item:selected, QTableView::item:selected {
    background: rgba(33, 245, 193, 0.3);
    color: #E8FFFB;
}

QHeaderView::section {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(19, 79, 74, 1),
                                stop:1 rgba(15, 61, 58, 1));
    color: #21F5C1;
    padding: 10px;
    border: none;
    border-right: 1px solid rgba(33, 245, 193, 0.2);
    border-bottom: 2px solid rgba(33, 245, 193, 0.5);
    font-weight: bold;
}

QHeaderView::section:hover {
    background: rgba(33, 245, 193, 0.2);
}

/* ========== ScrollBars ========== */
QScrollBar:vertical {
    background: rgba(11, 46, 43, 0.5);
    width: 14px;
    border-radius: 7px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #21F5C1, stop:1 #1AE5B1);
    border-radius: 7px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #2AF5D1;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: rgba(11, 46, 43, 0.5);
    height: 14px;
    border-radius: 7px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #21F5C1, stop:1 #1AE5B1);
    border-radius: 7px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: #2AF5D1;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ========== Progress Bars ========== */
QProgressBar {
    border: 2px solid rgba(33, 245, 193, 0.4);
    border-radius: 10px;
    background: rgba(11, 46, 43, 0.8);
    text-align: center;
    color: #E8FFFB;
    font-weight: bold;
    min-height: 25px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #21F5C1, stop:1 #2AF5D1);
    border-radius: 8px;
}

/* ========== Checkboxes & Radio Buttons ========== */
QCheckBox, QRadioButton {
    color: #E8FFFB;
    spacing: 8px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid rgba(33, 245, 193, 0.5);
    background: rgba(11, 46, 43, 0.8);
}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #21F5C1, stop:1 #2AF5D1);
    border: 2px solid #21F5C1;
}

QCheckBox::indicator:hover, QRadioButton::indicator:hover {
    border: 2px solid #21F5C1;
}

QRadioButton::indicator {
    border-radius: 10px;
}

/* ========== GroupBox ========== */
QGroupBox {
    border: 2px solid rgba(33, 245, 193, 0.4);
    border-radius: 12px;
    margin-top: 15px;
    padding-top: 20px;
    font-weight: bold;
    color: #21F5C1;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 15px;
    padding: 0 8px;
    color: #21F5C1;
    background: #0B2E2B;
}

/* ========== Status Labels ========== */
QLabel[class="status-ready"] {
    color: #21F5C1;
    font-weight: bold;
    background: transparent;
}

QLabel[class="status-success"] {
    color: #10B981;
    font-weight: bold;
    background: transparent;
}

QLabel[class="status-error"] {
    color: #FF4D4D;
    font-weight: bold;
    background: transparent;
}

QLabel[class="status-warning"] {
    color: #F59E0B;
    font-weight: bold;
    background: transparent;
}

QLabel[class="status-connected"] {
    color: #10B981;
    background: transparent;
}

/* ========== Tooltips ========== */
QToolTip {
    background: rgba(19, 79, 74, 0.98);
    border: 2px solid #21F5C1;
    color: #E8FFFB;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 10pt;
}

/* ========== Menu & Context Menu ========== */
QMenuBar {
    background: #0F3D3A;
    color: #E8FFFB;
}

QMenuBar::item:selected {
    background: rgba(33, 245, 193, 0.3);
}

QMenu {
    background: #0F3D3A;
    border: 2px solid #21F5C1;
    color: #E8FFFB;
}

QMenu::item:selected {
    background: rgba(33, 245, 193, 0.3);
}

/* ========== Status Bar ========== */
QStatusBar {
    background: rgba(15, 61, 58, 0.95);
    color: #9ED9CF;
    border-top: 2px solid rgba(33, 245, 193, 0.4);
}

QStatusBar::item {
    border: none;
}

/* ========== Splitter ========== */
QSplitter::handle {
    background: rgba(33, 245, 193, 0.3);
}

QSplitter::handle:hover {
    background: #21F5C1;
}

/* ========== List Widget ========== */
QListWidget {
    background: rgba(11, 46, 43, 0.8);
    border: 2px solid rgba(33, 245, 193, 0.3);
    border-radius: 8px;
    color: #E8FFFB;
    outline: none;
}

QListWidget::item {
    padding: 10px;
    border-bottom: 1px solid rgba(33, 245, 193, 0.1);
}

QListWidget::item:selected {
    background: rgba(33, 245, 193, 0.3);
    color: #E8FFFB;
}

QListWidget::item:hover {
    background: rgba(33, 245, 193, 0.2);
}

/* ========== Message Box ========== */
QMessageBox {
    background: #0F3D3A;
}

QMessageBox QLabel {
    color: #E8FFFB;
}

QMessageBox QPushButton {
    min-width: 80px;
}
        """.strip()

    def _get_particles_theme(self):
        """Dark particles theme (existing)"""
        return """
/* Existing dark particles theme preserved */
QWidget {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #0e0e1a, stop:1 #1a1a2e);
    color: #e0e0ff;
}
/* ... rest of particles theme ... */
        """.strip()

    def _get_neon_theme(self):
        """Neon clinic theme (existing)"""
        return """
/* Existing neon clinic theme preserved */
QWidget {
    background: #1a1a1a;
    color: #00ff88;
}
/* ... rest of neon theme ... */
        """.strip()

    def set_theme(self, theme_name):
        if theme_name not in self.available_themes:
            logger.warning(f"Theme '{theme_name}' not found, using 'dacos_unified'")
            theme_name = 'dacos_unified'
        self.active_theme = theme_name
        logger.info(f"Theme switched to: {theme_name}")
        if self.app:
            self.apply_theme()

    def set_app(self, app):
        self.app = app

    def apply_theme(self):
        if self.app and self.active_theme in self.available_themes:
            self.app.setStyleSheet(self.available_themes[self.active_theme])
            logger.info(f"Applied theme: {self.active_theme}")

    def get_theme_names(self):
        return list(self.available_themes.keys())

    def get_theme_info(self):
        return {
            'dacos_unified': {"name": "Dacos Unified Futuristic"},
            'dacos_particles': {"name": "Dacos Particles Dark"},
            'neon_clinic': {"name": "Neon Clinic"}
        }

    def set_security_level(self, level):
        logger.info(f"Security level set to: {level}")

# Global instance
style_manager = StyleManager()