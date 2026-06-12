# dacos_theme_suite.py - THREE COMPLETE QT STYLESHEETS FOR AUTODIAG PRO
"""
DACOS Theme Suite - Professional Qt Stylesheets
================================================
Three production-ready themes for AutoDiag Pro diagnostic suite:
1. DACOS Teal Fusion (Original) - Teal/cyan with glass morphism
2. DACOS Midnight Carbon - Dark blue/purple with carbon fiber aesthetic
3. DACOS Claude Exclusive - Claude AI-inspired copper/warm theme

Usage:
    from dacos_theme_suite import DACOS_TEAL_FUSION, DACOS_MIDNIGHT_CARBON, DACOS_CLAUDE_EXCLUSIVE
    app.setStyleSheet(DACOS_TEAL_FUSION)
"""

# ============================================================================
# THEME 1: DACOS TEAL FUSION (ORIGINAL)
# Teal/Cyan glass morphism with holographic accents
# ============================================================================

DACOS_TEAL_FUSION = """
QMainWindow { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0A1A1A, stop:0.5 #0D2323, stop:1 #0A1A1A); color: #E8F4F2; font-family: "Segoe UI"; }
QWidget { background: transparent; color: #E8F4F2; }
QScrollBar:vertical { background: rgba(13,35,35,0.5); width: 12px; border-radius: 6px; }
QScrollBar::handle:vertical { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #21F5C1, stop:1 #2AF5D1); border-radius: 6px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #2AF5D1; }
QScrollBar:horizontal { background: rgba(13,35,35,0.5); height: 12px; border-radius: 6px; }
QScrollBar::handle:horizontal { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #21F5C1, stop:1 #2AF5D1); border-radius: 6px; min-width: 30px; }
QFrame[class="glass-card"] { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(19,79,74,0.95), stop:0.5 rgba(13,35,35,0.92), stop:1 rgba(19,79,74,0.95)); border: 2px solid rgba(33,245,193,0.5); border-radius: 16px; padding: 20px; }
QFrame[class="glass-card"]:hover { border: 2px solid rgba(42,245,209,0.7); background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(19,79,74,1.0), stop:1 rgba(19,79,74,1.0)); }
QGroupBox { background: rgba(13,35,35,0.7); border: 2px solid rgba(33,245,193,0.4); border-radius: 12px; padding: 20px 10px 10px 10px; margin-top: 12px; font-weight: bold; color: #21F5C1; }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; left: 15px; padding: 5px 15px; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(33,245,193,0.3), stop:0.5 rgba(42,245,209,0.5), stop:1 rgba(33,245,193,0.3)); border-radius: 8px; color: #E8F4F2; }
QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #21F5C1, stop:0.5 #1FD9B0, stop:1 #21F5C1); border: none; border-radius: 10px; padding: 12px 24px; color: #0A1A1A; font-weight: bold; min-height: 40px; }
QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2AF5D1, stop:0.5 #25E5C0, stop:1 #2AF5D1); border: 2px solid rgba(255,255,255,0.3); }
QPushButton:pressed { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1AC9A1, stop:1 #18B591); padding-top: 14px; }
QPushButton:disabled { background: rgba(33,245,193,0.2); color: rgba(232,244,242,0.3); }
QPushButton[class="primary"] { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #21F5C1, stop:1 #1AC9A1); color: #0A1A1A; }
QPushButton[class="success"] { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #10B981, stop:1 #059669); color: white; }
QPushButton[class="warning"] { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F59E0B, stop:1 #D97706); color: white; }
QPushButton[class="danger"] { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FF4D4D, stop:1 #DC2626); color: white; }
QTabWidget::pane { border: 2px solid rgba(33,245,193,0.4); background: rgba(13,35,35,0.5); border-radius: 16px; padding: 10px; }
QTabBar::tab { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(19,79,74,0.8), stop:1 rgba(13,35,35,0.9)); color: #9ED9CF; padding: 14px 28px; border-radius: 10px 10px 0 0; margin: 2px 1px 0 1px; font-weight: bold; border: 2px solid rgba(33,245,193,0.2); border-bottom: none; min-width: 120px; }
QTabBar::tab:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(33,245,193,0.3), stop:1 rgba(19,79,74,0.9)); color: #E8F4F2; border: 2px solid rgba(42,245,209,0.4); }
QTabBar::tab:selected { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #21F5C1, stop:1 #1AC9A1); color: #0A1A1A; border: 2px solid #2AF5D1; padding-bottom: 16px; }
QLineEdit, QTextEdit, QPlainTextEdit { background: rgba(13,35,35,0.8); border: 2px solid rgba(33,245,193,0.3); border-radius: 10px; padding: 10px 15px; color: #E8F4F2; selection-background-color: rgba(33,245,193,0.4); }
QLineEdit:focus, QTextEdit:focus { border: 2px solid #21F5C1; background: rgba(19,79,74,0.5); }
QComboBox { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(19,79,74,0.9), stop:1 rgba(13,35,35,0.9)); border: 2px solid rgba(33,245,193,0.4); border-radius: 10px; padding: 10px 15px; color: #E8F4F2; min-width: 120px; }
QComboBox:hover { border: 2px solid rgba(42,245,209,0.6); }
QComboBox::drop-down { border: none; width: 30px; }
QComboBox::down-arrow { border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 6px solid #21F5C1; margin-right: 8px; }
QComboBox QAbstractItemView { background: rgba(13,35,35,0.98); border: 2px solid #21F5C1; border-radius: 8px; color: #E8F4F2; selection-background-color: rgba(33,245,193,0.4); }
QComboBox QAbstractItemView::item { padding: 8px 15px; border-radius: 6px; min-height: 30px; }
QComboBox QAbstractItemView::item:hover { background: rgba(33,245,193,0.3); }
QTableWidget, QTableView { background: rgba(13,35,35,0.7); border: 2px solid rgba(33,245,193,0.3); border-radius: 12px; gridline-color: rgba(33,245,193,0.2); color: #E8F4F2; selection-background-color: rgba(33,245,193,0.3); }
QTableWidget::item:hover { background: rgba(33,245,193,0.15); }
QHeaderView::section { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(33,245,193,0.3), stop:1 rgba(19,79,74,0.8)); color: #E8F4F2; padding: 10px; border: none; font-weight: bold; }
QListWidget { background: rgba(13,35,35,0.7); border: 2px solid rgba(33,245,193,0.3); border-radius: 12px; padding: 5px; color: #E8F4F2; }
QListWidget::item { padding: 10px 15px; border-radius: 8px; margin: 2px; }
QListWidget::item:hover { background: rgba(33,245,193,0.2); }
QListWidget::item:selected { background: rgba(33,245,193,0.4); }
QLabel[class="hero-title"] { color: #21F5C1; font-size: 22pt; font-weight: bold; }
QLabel[class="tab-title"] { color: #21F5C1; font-size: 18pt; font-weight: bold; }
QLabel[class="section-title"] { color: #E8F4F2; font-size: 14pt; font-weight: bold; }
QLabel[class="section-label"] { color: #9ED9CF; font-size: 10pt; }
QLabel[class="subtitle"] { color: #9ED9CF; font-size: 9pt; }
QProgressBar { background: rgba(13,35,35,0.8); border: 2px solid rgba(33,245,193,0.3); border-radius: 10px; text-align: center; color: #E8F4F2; font-weight: bold; min-height: 25px; }
QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #21F5C1, stop:0.5 #2AF5D1, stop:1 #21F5C1); border-radius: 8px; }
QStatusBar { background: rgba(10,26,26,0.95); border-top: 2px solid rgba(33,245,193,0.3); color: #9ED9CF; }
QToolTip { background: rgba(19,79,74,0.98); border: 2px solid #21F5C1; border-radius: 8px; padding: 8px 12px; color: #E8F4F2; }
QCheckBox, QRadioButton { color: #E8F4F2; spacing: 8px; }
QCheckBox::indicator { width: 20px; height: 20px; border: 2px solid rgba(33,245,193,0.5); border-radius: 5px; background: rgba(13,35,35,0.8); }
QCheckBox::indicator:checked { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #21F5C1, stop:1 #1AC9A1); }
QMenu { background: rgba(13,35,35,0.98); border: 2px solid #21F5C1; border-radius: 10px; padding: 5px; }
QMenu::item { padding: 10px 30px 10px 20px; border-radius: 6px; color: #E8F4F2; }
QMenu::item:selected { background: rgba(33,245,193,0.3); }
QSpinBox, QDoubleSpinBox { background: rgba(13,35,35,0.8); border: 2px solid rgba(33,245,193,0.3); border-radius: 10px; padding: 8px 12px; color: #E8F4F2; }
QSpinBox:focus, QDoubleSpinBox:focus { border: 2px solid #21F5C1; }
QSlider::groove:horizontal { background: rgba(13,35,35,0.8); height: 8px; border-radius: 4px; }
QSlider::handle:horizontal { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #21F5C1, stop:1 #2AF5D1); width: 20px; height: 20px; margin: -6px 0; border-radius: 10px; }
"""

# ============================================================================
# THEME 2: DACOS MIDNIGHT CARBON
# Dark blue/purple with carbon fiber aesthetic and electric accents
# ============================================================================

DACOS_MIDNIGHT_CARBON = """
QMainWindow { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0B0C1E, stop:0.5 #141633, stop:1 #0B0C1E); color: #E3E8FF; font-family: "Segoe UI"; }
QWidget { background: transparent; color: #E3E8FF; }
QScrollBar:vertical { background: rgba(20,22,51,0.5); width: 12px; border-radius: 6px; }
QScrollBar::handle:vertical { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:1 #8B5CF6); border-radius: 6px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #8B5CF6; }
QScrollBar:horizontal { background: rgba(20,22,51,0.5); height: 12px; border-radius: 6px; }
QScrollBar::handle:horizontal { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6366F1, stop:1 #8B5CF6); border-radius: 6px; min-width: 30px; }
QFrame[class="glass-card"] { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(30,32,75,0.95), stop:0.5 rgba(20,22,51,0.92), stop:1 rgba(30,32,75,0.95)); border: 2px solid rgba(99,102,241,0.5); border-radius: 16px; padding: 20px; }
QFrame[class="glass-card"]:hover { border: 2px solid rgba(139,92,246,0.7); background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(30,32,75,1.0), stop:1 rgba(30,32,75,1.0)); }
QGroupBox { background: rgba(20,22,51,0.7); border: 2px solid rgba(99,102,241,0.4); border-radius: 12px; padding: 20px 10px 10px 10px; margin-top: 12px; font-weight: bold; color: #6366F1; }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; left: 15px; padding: 5px 15px; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(99,102,241,0.3), stop:0.5 rgba(139,92,246,0.5), stop:1 rgba(99,102,241,0.3)); border-radius: 8px; color: #E3E8FF; }
QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6366F1, stop:0.5 #5558D9, stop:1 #6366F1); border: none; border-radius: 10px; padding: 12px 24px; color: #FFFFFF; font-weight: bold; min-height: 40px; }
QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #8B5CF6, stop:0.5 #7C3AED, stop:1 #8B5CF6); border: 2px solid rgba(255,255,255,0.3); }
QPushButton:pressed { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4F46E5, stop:1 #4338CA); padding-top: 14px; }
QPushButton:disabled { background: rgba(99,102,241,0.2); color: rgba(227,232,255,0.3); }
QPushButton[class="primary"] { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6366F1, stop:1 #4F46E5); color: #FFFFFF; }
QPushButton[class="success"] { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #10B981, stop:1 #059669); color: white; }
QPushButton[class="warning"] { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F59E0B, stop:1 #D97706); color: white; }
QPushButton[class="danger"] { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #EF4444, stop:1 #DC2626); color: white; }
QTabWidget::pane { border: 2px solid rgba(99,102,241,0.4); background: rgba(20,22,51,0.5); border-radius: 16px; padding: 10px; }
QTabBar::tab { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(30,32,75,0.8), stop:1 rgba(20,22,51,0.9)); color: #A5B4FC; padding: 14px 28px; border-radius: 10px 10px 0 0; margin: 2px 1px 0 1px; font-weight: bold; border: 2px solid rgba(99,102,241,0.2); border-bottom: none; min-width: 120px; }
QTabBar::tab:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(99,102,241,0.3), stop:1 rgba(30,32,75,0.9)); color: #E3E8FF; border: 2px solid rgba(139,92,246,0.4); }
QTabBar::tab:selected { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6366F1, stop:1 #4F46E5); color: #FFFFFF; border: 2px solid #8B5CF6; padding-bottom: 16px; }
QLineEdit, QTextEdit, QPlainTextEdit { background: rgba(20,22,51,0.8); border: 2px solid rgba(99,102,241,0.3); border-radius: 10px; padding: 10px 15px; color: #E3E8FF; selection-background-color: rgba(99,102,241,0.4); }
QLineEdit:focus, QTextEdit:focus { border: 2px solid #6366F1; background: rgba(30,32,75,0.5); }
QComboBox { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(30,32,75,0.9), stop:1 rgba(20,22,51,0.9)); border: 2px solid rgba(99,102,241,0.4); border-radius: 10px; padding: 10px 15px; color: #E3E8FF; min-width: 120px; }
QComboBox:hover { border: 2px solid rgba(139,92,246,0.6); }
QComboBox::drop-down { border: none; width: 30px; }
QComboBox::down-arrow { border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 6px solid #6366F1; margin-right: 8px; }
QComboBox QAbstractItemView { background: rgba(20,22,51,0.98); border: 2px solid #6366F1; border-radius: 8px; color: #E3E8FF; selection-background-color: rgba(99,102,241,0.4); }
QComboBox QAbstractItemView::item { padding: 8px 15px; border-radius: 6px; min-height: 30px; }
QComboBox QAbstractItemView::item:hover { background: rgba(99,102,241,0.3); }
QTableWidget, QTableView { background: rgba(20,22,51,0.7); border: 2px solid rgba(99,102,241,0.3); border-radius: 12px; gridline-color: rgba(99,102,241,0.2); color: #E3E8FF; selection-background-color: rgba(99,102,241,0.3); }
QTableWidget::item:hover { background: rgba(99,102,241,0.15); }
QHeaderView::section { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(99,102,241,0.3), stop:1 rgba(30,32,75,0.8)); color: #E3E8FF; padding: 10px; border: none; font-weight: bold; }
QListWidget { background: rgba(20,22,51,0.7); border: 2px solid rgba(99,102,241,0.3); border-radius: 12px; padding: 5px; color: #E3E8FF; }
QListWidget::item { padding: 10px 15px; border-radius: 8px; margin: 2px; }
QListWidget::item:hover { background: rgba(99,102,241,0.2); }
QListWidget::item:selected { background: rgba(99,102,241,0.4); }
QLabel[class="hero-title"] { color: #6366F1; font-size: 22pt; font-weight: bold; }
QLabel[class="tab-title"] { color: #8B5CF6; font-size: 18pt; font-weight: bold; }
QLabel[class="section-title"] { color: #E3E8FF; font-size: 14pt; font-weight: bold; }
QLabel[class="section-label"] { color: #A5B4FC; font-size: 10pt; }
QLabel[class="subtitle"] { color: #A5B4FC; font-size: 9pt; }
QProgressBar { background: rgba(20,22,51,0.8); border: 2px solid rgba(99,102,241,0.3); border-radius: 10px; text-align: center; color: #E3E8FF; font-weight: bold; min-height: 25px; }
QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:0.5 #8B5CF6, stop:1 #6366F1); border-radius: 8px; }
QStatusBar { background: rgba(11,12,30,0.95); border-top: 2px solid rgba(99,102,241,0.3); color: #A5B4FC; }
QToolTip { background: rgba(30,32,75,0.98); border: 2px solid #6366F1; border-radius: 8px; padding: 8px 12px; color: #E3E8FF; }
QCheckBox, QRadioButton { color: #E3E8FF; spacing: 8px; }
QCheckBox::indicator { width: 20px; height: 20px; border: 2px solid rgba(99,102,241,0.5); border-radius: 5px; background: rgba(20,22,51,0.8); }
QCheckBox::indicator:checked { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6366F1, stop:1 #4F46E5); }
QMenu { background: rgba(20,22,51,0.98); border: 2px solid #6366F1; border-radius: 10px; padding: 5px; }
QMenu::item { padding: 10px 30px 10px 20px; border-radius: 6px; color: #E3E8FF; }
QMenu::item:selected { background: rgba(99,102,241,0.3); }
QSpinBox, QDoubleSpinBox { background: rgba(20,22,51,0.8); border: 2px solid rgba(99,102,241,0.3); border-radius: 10px; padding: 8px 12px; color: #E3E8FF; }
QSpinBox:focus, QDoubleSpinBox:focus { border: 2px solid #6366F1; }
QSlider::groove:horizontal { background: rgba(20,22,51,0.8); height: 8px; border-radius: 4px; }
QSlider::handle:horizontal { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:1 #8B5CF6); width: 20px; height: 20px; margin: -6px 0; border-radius: 10px; }
"""

# dacos_claude_exclusive.py - COMPLETE CLAUDE EXCLUSIVE THEME
"""
DACOS Claude Exclusive Theme
=============================
Claude AI-inspired copper/warm theme with sophisticated amber accents
Premium theme with rich earth tones and golden highlights
"""

DACOS_CLAUDE_EXCLUSIVE = """
QMainWindow { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1A0F0A, stop:0.5 #2D1810, stop:1 #1A0F0A); color: #FFF5E6; font-family: "Segoe UI"; }
QWidget { background: transparent; color: #FFF5E6; }
QScrollBar:vertical { background: rgba(45,24,16,0.5); width: 12px; border-radius: 6px; }
QScrollBar::handle:vertical { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #D97706, stop:1 #F59E0B); border-radius: 6px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #FBBF24; }
QScrollBar:horizontal { background: rgba(45,24,16,0.5); height: 12px; border-radius: 6px; }
QScrollBar::handle:horizontal { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #D97706, stop:1 #F59E0B); border-radius: 6px; min-width: 30px; }
QFrame[class="glass-card"] { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(68,42,28,0.95), stop:0.5 rgba(45,24,16,0.92), stop:1 rgba(68,42,28,0.95)); border: 2px solid rgba(217,119,6,0.5); border-radius: 16px; padding: 20px; }
QFrame[class="glass-card"]:hover { border: 2px solid rgba(245,158,11,0.7); background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(68,42,28,1.0), stop:1 rgba(68,42,28,1.0)); }
QGroupBox { background: rgba(45,24,16,0.7); border: 2px solid rgba(217,119,6,0.4); border-radius: 12px; padding: 20px 10px 10px 10px; margin-top: 12px; font-weight: bold; color: #F59E0B; }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; left: 15px; padding: 5px 15px; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(217,119,6,0.3), stop:0.5 rgba(245,158,11,0.5), stop:1 rgba(217,119,6,0.3)); border-radius: 8px; color: #FFF5E6; }
QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F59E0B, stop:0.5 #D97706, stop:1 #F59E0B); border: none; border-radius: 10px; padding: 12px 24px; color: #1A0F0A; font-weight: bold; min-height: 40px; }
QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FBBF24, stop:0.5 #F59E0B, stop:1 #FBBF24); border: 2px solid rgba(255,255,255,0.3); }
QPushButton:pressed { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #D97706, stop:1 #B45309); padding-top: 14px; }
QPushButton:disabled { background: rgba(217,119,6,0.2); color: rgba(255,245,230,0.3); }
QPushButton[class="primary"] { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F59E0B, stop:1 #D97706); color: #1A0F0A; }
QPushButton[class="primary"]:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FCD34D, stop:1 #F59E0B); }
QPushButton[class="success"] { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #10B981, stop:1 #059669); color: white; }
QPushButton[class="success"]:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #14D899, stop:1 #0AAF77); }
QPushButton[class="warning"] { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FB923C, stop:1 #EA580C); color: white; }
QPushButton[class="warning"]:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FDBA74, stop:1 #FB923C); }
QPushButton[class="danger"] { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #EF4444, stop:1 #DC2626); color: white; }
QPushButton[class="danger"]:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F87171, stop:1 #EF4444); }
QTabWidget::pane { border: 2px solid rgba(217,119,6,0.4); background: rgba(45,24,16,0.5); border-radius: 16px; padding: 10px; }
QTabBar::tab { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(68,42,28,0.8), stop:1 rgba(45,24,16,0.9)); color: #FDB863; padding: 14px 28px; border-radius: 10px 10px 0 0; margin: 2px 1px 0 1px; font-weight: bold; border: 2px solid rgba(217,119,6,0.2); border-bottom: none; min-width: 120px; }
QTabBar::tab:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(217,119,6,0.3), stop:1 rgba(68,42,28,0.9)); color: #FFF5E6; border: 2px solid rgba(245,158,11,0.4); }
QTabBar::tab:selected { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F59E0B, stop:1 #D97706); color: #1A0F0A; border: 2px solid #FBBF24; padding-bottom: 16px; }
QLineEdit, QTextEdit, QPlainTextEdit { background: rgba(45,24,16,0.8); border: 2px solid rgba(217,119,6,0.3); border-radius: 10px; padding: 10px 15px; color: #FFF5E6; selection-background-color: rgba(217,119,6,0.4); }
QLineEdit:focus, QTextEdit:focus { border: 2px solid #F59E0B; background: rgba(68,42,28,0.5); }
QComboBox { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(68,42,28,0.9), stop:1 rgba(45,24,16,0.9)); border: 2px solid rgba(217,119,6,0.4); border-radius: 10px; padding: 10px 15px; color: #FFF5E6; min-width: 120px; }
QComboBox:hover { border: 2px solid rgba(245,158,11,0.6); }
QComboBox::drop-down { border: none; width: 30px; }
QComboBox::down-arrow { border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 6px solid #F59E0B; margin-right: 8px; }
QComboBox QAbstractItemView { background: rgba(45,24,16,0.98); border: 2px solid #F59E0B; border-radius: 8px; color: #FFF5E6; selection-background-color: rgba(217,119,6,0.4); }
QComboBox QAbstractItemView::item { padding: 8px 15px; border-radius: 6px; min-height: 30px; }
QComboBox QAbstractItemView::item:hover { background: rgba(217,119,6,0.3); }
QTableWidget, QTableView { background: rgba(45,24,16,0.7); border: 2px solid rgba(217,119,6,0.3); border-radius: 12px; gridline-color: rgba(217,119,6,0.2); color: #FFF5E6; selection-background-color: rgba(217,119,6,0.3); }
QTableWidget::item:hover { background: rgba(217,119,6,0.15); }
QHeaderView::section { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(217,119,6,0.3), stop:1 rgba(68,42,28,0.8)); color: #FFF5E6; padding: 10px; border: none; font-weight: bold; }
QListWidget { background: rgba(45,24,16,0.7); border: 2px solid rgba(217,119,6,0.3); border-radius: 12px; padding: 5px; color: #FFF5E6; }
QListWidget::item { padding: 10px 15px; border-radius: 8px; margin: 2px; }
QListWidget::item:hover { background: rgba(217,119,6,0.2); }
QListWidget::item:selected { background: rgba(217,119,6,0.4); }
QLabel[class="hero-title"] { color: #F59E0B; font-size: 22pt; font-weight: bold; }
QLabel[class="tab-title"] { color: #FBBF24; font-size: 18pt; font-weight: bold; }
QLabel[class="section-title"] { color: #FFF5E6; font-size: 14pt; font-weight: bold; }
QLabel[class="section-label"] { color: #FDB863; font-size: 10pt; }
QLabel[class="subtitle"] { color: #FDB863; font-size: 9pt; }
QProgressBar { background: rgba(45,24,16,0.8); border: 2px solid rgba(217,119,6,0.3); border-radius: 10px; text-align: center; color: #FFF5E6; font-weight: bold; min-height: 25px; }
QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F59E0B, stop:0.5 #FBBF24, stop:1 #F59E0B); border-radius: 8px; }
QStatusBar { background: rgba(26,15,10,0.95); border-top: 2px solid rgba(217,119,6,0.3); color: #FDB863; }
QToolTip { background: rgba(68,42,28,0.98); border: 2px solid #F59E0B; border-radius: 8px; padding: 8px 12px; color: #FFF5E6; }
QCheckBox, QRadioButton { color: #FFF5E6; spacing: 8px; }
QCheckBox::indicator { width: 20px; height: 20px; border: 2px solid rgba(217,119,6,0.5); border-radius: 5px; background: rgba(45,24,16,0.8); }
QCheckBox::indicator:checked { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F59E0B, stop:1 #D97706); }
QRadioButton::indicator { width: 20px; height: 20px; border: 2px solid rgba(217,119,6,0.5); border-radius: 10px; background: rgba(45,24,16,0.8); }
QRadioButton::indicator:checked { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F59E0B, stop:1 #D97706); }
QMenu { background: rgba(45,24,16,0.98); border: 2px solid #F59E0B; border-radius: 10px; padding: 5px; }
QMenu::item { padding: 10px 30px 10px 20px; border-radius: 6px; color: #FFF5E6; }
QMenu::item:selected { background: rgba(217,119,6,0.3); }
QMenu::separator { height: 2px; background: rgba(217,119,6,0.3); margin: 5px 10px; }
QSpinBox, QDoubleSpinBox { background: rgba(45,24,16,0.8); border: 2px solid rgba(217,119,6,0.3); border-radius: 10px; padding: 8px 12px; color: #FFF5E6; }
QSpinBox:focus, QDoubleSpinBox:focus { border: 2px solid #F59E0B; }
QSpinBox::up-button, QDoubleSpinBox::up-button { background: rgba(217,119,6,0.2); border-radius: 5px; margin: 2px; }
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover { background: rgba(217,119,6,0.4); }
QSpinBox::down-button, QDoubleSpinBox::down-button { background: rgba(217,119,6,0.2); border-radius: 5px; margin: 2px; }
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover { background: rgba(217,119,6,0.4); }
QSlider::groove:horizontal { background: rgba(45,24,16,0.8); height: 8px; border-radius: 4px; }
QSlider::handle:horizontal { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F59E0B, stop:1 #FBBF24); width: 20px; height: 20px; margin: -6px 0; border-radius: 10px; }
QSlider::handle:horizontal:hover { background: #FCD34D; }
QSlider::groove:vertical { background: rgba(45,24,16,0.8); width: 8px; border-radius: 4px; }
QSlider::handle:vertical { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F59E0B, stop:1 #FBBF24); width: 20px; height: 20px; margin: 0 -6px; border-radius: 10px; }
QSlider::handle:vertical:hover { background: #FCD34D; }
QMessageBox { background: #2D1810; }
QMessageBox QLabel { color: #FFF5E6; }
QMessageBox QPushButton { min-width: 80px; }
QDialog { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1A0F0A, stop:0.5 #2D1810, stop:1 #1A0F0A); color: #FFF5E6; }
"""

# Color palette reference for DACOS Claude Exclusive
CLAUDE_COLORS = {
    "bg_main": "#1A0F0A",
    "bg_panel": "#2D1810",
    "bg_card": "#442A1C",
    "accent": "#F59E0B",
    "glow": "#FBBF24",
    "text_main": "#FFF5E6",
    "text_muted": "#FDB863",
    "error": "#EF4444",
    "success": "#10B981",
    "warning": "#FB923C",
    "info": "#3B82F6"
}

def apply_claude_theme(app):
    """
    Apply the DACOS Claude Exclusive theme to a QApplication instance
    
    Args:
        app: QApplication instance
        
    Returns:
        bool: True if theme applied successfully
    """
    try:
        app.setStyleSheet(DACOS_CLAUDE_EXCLUSIVE)
        return True
    except Exception as e:
        print(f"Failed to apply Claude theme: {e}")
        return False