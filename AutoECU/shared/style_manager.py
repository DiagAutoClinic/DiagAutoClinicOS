#!/usr/bin/env python3
"""
Enhanced Style Manager for DiagAutoClinicOS
Now with FUTURISTIC glassmorphic theme!
"""

from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtWidgets import QApplication, QStyleFactory
import logging

logger = logging.getLogger(__name__)

class EnhancedStyleManager:
    def __init__(self):
        self.settings = QSettings("DiagAutoClinicOS", "Style")
        self.current_theme = self.settings.value("theme", "futuristic")
        self.font_family = self.settings.value("font_family", "Segoe UI")
        self.font_size = int(self.settings.value("font_size", "10"))
        self.security_level = "basic"
        
    def set_security_level(self, level: str):
        """Set security level for theme adaptation"""
        self.security_level = level
        self.set_theme(self.current_theme)
        
    def set_theme(self, theme_name):
        """Set the application theme with security integration"""
        if theme_name not in self.get_theme_names():
            logger.warning(f"Unknown theme {theme_name}. Using futuristic theme.")
            theme_name = "futuristic"
        
        self.current_theme = theme_name
        self.settings.setValue("theme", theme_name)
        
        theme_methods = {
            "dark": self.apply_dark_theme,
            "light": self.apply_light_theme,
            "security": self.apply_security_theme,
            "professional": self.apply_professional_theme,
            "futuristic": self.apply_futuristic_theme  # NEW!
        }
        
        theme_methods.get(theme_name, self.apply_futuristic_theme)()
            
    def set_font(self, font_family=None, font_size=None):
        """Set application font with security considerations"""
        if font_family:
            self.font_family = font_family
            self.settings.setValue("font_family", font_family)
        if font_size:
            self.font_size = font_size
            self.settings.setValue("font_size", str(font_size))
        
        self.set_theme(self.current_theme)
    
    def apply_futuristic_theme(self):
        """Apply FUTURISTIC glassmorphic theme - TEAL/EMERALD"""
        app = QApplication.instance()
        app.setStyle(QStyleFactory.create("Fusion"))
        
        # Futuristic color palette - Teal/Emerald
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(10, 25, 25))  # Dark teal
        palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 255, 250))  # Light cyan
        palette.setColor(QPalette.ColorRole.Base, QColor(15, 35, 35))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(20, 45, 45))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(20, 77, 77))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(220, 255, 250))
        palette.setColor(QPalette.ColorRole.Button, QColor(20, 77, 77))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 255, 250))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(100, 255, 218))
        palette.setColor(QPalette.ColorRole.Link, QColor(20, 184, 166))  # Teal-500
        palette.setColor(QPalette.ColorRole.Highlight, QColor(20, 184, 166))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        app.setPalette(palette)
        app.setStyleSheet(self.get_futuristic_stylesheet())
        
    def apply_security_theme(self):
        """Apply security-focused theme for diagnostic operations"""
        app = QApplication.instance()
        app.setStyle(QStyleFactory.create("Fusion"))
        
        # Security-based color palette
        palette = QPalette()
        if self.security_level == "dealer":
            palette.setColor(QPalette.ColorRole.Window, QColor(10, 15, 25))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 230, 255))
            accent_color = QColor(74, 138, 255)
        else:
            palette.setColor(QPalette.ColorRole.Window, QColor(15, 20, 30))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(200, 210, 235))
            accent_color = QColor(90, 110, 180)
        
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 30, 40))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 40, 50))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(45, 50, 60))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(220, 230, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(220, 230, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(60, 70, 100))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 230, 255))
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.cyan)
        palette.setColor(QPalette.ColorRole.Link, accent_color)
        palette.setColor(QPalette.ColorRole.Highlight, accent_color)
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        app.setPalette(palette)
        app.setStyleSheet(self.get_security_stylesheet())
        
    def apply_dark_theme(self):
        """Apply modern dark theme"""
        app = QApplication.instance()
        app.setStyle(QStyleFactory.create("Fusion"))
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 35))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Base, QColor(40, 40, 45))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(50, 50, 55))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(60, 60, 65))
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Button, QColor(70, 70, 80))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(120, 160, 255))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(100, 140, 235))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        app.setPalette(palette)
        app.setStyleSheet(self.get_dark_stylesheet())

    def apply_light_theme(self):
        """Apply light theme"""
        app = QApplication.instance()
        app.setStyle(QStyleFactory.create("Fusion"))
        palette = QPalette()
        # Light theme colors...
        app.setPalette(palette)

    def apply_professional_theme(self):
        """Apply professional theme"""
        app = QApplication.instance()
        app.setStyle(QStyleFactory.create("Fusion"))
        palette = QPalette()
        # Professional theme colors...
        app.setPalette(palette)

    def _get_base_stylesheet(self):
        """Common styles shared across themes"""
        return f"""
            QWidget {{
                font-family: '{self.font_family}';
                font-size: {self.font_size}pt;
            }}
            
            QToolTip {{
                padding: 5px;
                border: 1px solid #555;
                background-color: #2a2a35;
                color: #ffffff;
                opacity: 240;
            }}
        """

    def get_futuristic_stylesheet(self):
        """FUTURISTIC GLASSMORPHIC THEME - The Fire! 🔥"""
        base = self._get_base_stylesheet()
        return base + """
        /* ========================================
           FUTURISTIC GLASSMORPHIC THEME
           Teal/Emerald with Glass Effects
           ======================================== */
        
        QMainWindow, QDialog {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 #0a1919, stop: 0.5 #0d2626, stop: 1 #0a1919);
        }
        
        /* ========== GLASSMORPHIC CARDS ========== */
        QFrame[class="glass-card"] {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(20, 77, 77, 0.4),
                stop: 1 rgba(10, 45, 45, 0.3));
            border: 1px solid rgba(20, 184, 166, 0.3);
            border-radius: 16px;
            padding: 20px;
        }
        
        QFrame[class="glass-card-hover"]:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(20, 77, 77, 0.6),
                stop: 1 rgba(10, 45, 45, 0.5));
            border: 1px solid rgba(20, 184, 166, 0.5);
        }
        
        /* ========== HERO SECTION ========== */
        QLabel[class="hero-title"] {
            font-size: 32pt;
            font-weight: bold;
            color: #14b8a6;
            text-shadow: 0 0 20px rgba(20, 184, 166, 0.5);
        }
        
        QLabel[class="hero-subtitle"] {
            font-size: 14pt;
            color: #5eead4;
            opacity: 0.8;
        }
        
        /* ========== MODERN APP CARDS ========== */
        QFrame[class="app-card"] {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(20, 77, 77, 0.5),
                stop: 1 rgba(15, 55, 55, 0.4));
            border: 2px solid rgba(20, 184, 166, 0.3);
            border-radius: 20px;
            padding: 24px;
        }
        
        QFrame[class="app-card"]:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(20, 77, 77, 0.7),
                stop: 1 rgba(15, 55, 55, 0.6));
            border: 2px solid rgba(20, 184, 166, 0.6);
        }
        
        /* ========== STAT CARDS ========== */
        QFrame[class="stat-card"] {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 rgba(20, 77, 77, 0.4),
                stop: 1 rgba(15, 55, 55, 0.3));
            border: 1px solid rgba(20, 184, 166, 0.4);
            border-radius: 12px;
            padding: 16px;
        }
        
        QLabel[class="stat-value"] {
            font-size: 28pt;
            font-weight: bold;
            color: #14b8a6;
            text-shadow: 0 0 15px rgba(20, 184, 166, 0.4);
        }
        
        QLabel[class="stat-label"] {
            font-size: 10pt;
            color: #5eead4;
            opacity: 0.7;
        }
        
        /* ========== BUTTONS ========== */
        QPushButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(20, 184, 166, 0.8),
                stop: 1 rgba(13, 148, 136, 0.8));
            color: white;
            border: 1px solid rgba(20, 184, 166, 0.5);
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: bold;
            min-height: 35px;
        }
        
        QPushButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 rgba(20, 184, 166, 1.0),
                stop: 1 rgba(13, 148, 136, 1.0));
            border: 1px solid rgba(94, 234, 212, 0.8);
        }
        
        QPushButton:pressed {
            background: rgba(13, 148, 136, 0.9);
            padding-top: 14px;
        }
        
        QPushButton[class="primary"] {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #14b8a6, stop: 1 #0d9488);
            border: 2px solid #5eead4;
        }
        
        QPushButton[class="success"] {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #10b981, stop: 1 #059669);
            border: 2px solid #6ee7b7;
        }
        
        QPushButton[class="danger"] {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #ef4444, stop: 1 #dc2626);
            border: 2px solid #fca5a5;
        }
        
        /* ========== GROUP BOXES ========== */
        QGroupBox {
            color: #14b8a6;
            font-weight: bold;
            font-size: 12pt;
            border: 2px solid rgba(20, 184, 166, 0.4);
            border-radius: 12px;
            margin-top: 12px;
            padding-top: 16px;
            background: rgba(20, 77, 77, 0.2);
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 16px;
            padding: 0 12px;
            color: #5eead4;
            background: rgba(20, 77, 77, 0.6);
            border-radius: 6px;
        }
        
        /* ========== LISTS ========== */
        QListWidget {
            background: rgba(15, 45, 45, 0.6);
            color: #dcfff7;
            border: 1px solid rgba(20, 184, 166, 0.3);
            border-radius: 10px;
            padding: 8px;
        }
        
        QListWidget::item {
            padding: 12px;
            border-bottom: 1px solid rgba(20, 184, 166, 0.2);
            border-radius: 6px;
            margin: 3px;
        }
        
        QListWidget::item:selected {
            background: rgba(20, 184, 166, 0.4);
            border: 1px solid #14b8a6;
        }
        
        QListWidget::item:hover {
            background: rgba(20, 184, 166, 0.2);
        }
        
        /* ========== TEXT AREAS ========== */
        QTextEdit {
            background: rgba(15, 45, 45, 0.6);
            color: #dcfff7;
            border: 1px solid rgba(20, 184, 166, 0.3);
            border-radius: 10px;
            padding: 12px;
            selection-background-color: rgba(20, 184, 166, 0.5);
        }
        
        QTextEdit:focus {
            border: 2px solid #14b8a6;
        }
        
        /* ========== LINE EDITS ========== */
        QLineEdit {
            background: rgba(15, 45, 45, 0.6);
            color: #dcfff7;
            border: 1px solid rgba(20, 184, 166, 0.3);
            border-radius: 8px;
            padding: 10px;
            min-height: 25px;
        }
        
        QLineEdit:focus {
            border: 2px solid #14b8a6;
            background: rgba(20, 77, 77, 0.4);
        }
        
        /* ========== COMBO BOXES ========== */
        QComboBox {
            background: rgba(15, 45, 45, 0.6);
            color: #dcfff7;
            border: 1px solid rgba(20, 184, 166, 0.3);
            border-radius: 8px;
            padding: 8px;
            min-width: 120px;
        }
        
        QComboBox:hover {
            border: 1px solid #14b8a6;
            background: rgba(20, 77, 77, 0.4);
        }
        
        QComboBox::drop-down {
            border: none;
            width: 30px;
        }
        
        QComboBox QAbstractItemView {
            background: rgba(15, 45, 45, 0.95);
            color: #dcfff7;
            border: 1px solid rgba(20, 184, 166, 0.5);
            selection-background-color: rgba(20, 184, 166, 0.4);
            border-radius: 6px;
        }
        
        /* ========== TABLES ========== */
        QTableWidget {
            background: rgba(15, 45, 45, 0.5);
            color: #dcfff7;
            gridline-color: rgba(20, 184, 166, 0.2);
            border: 1px solid rgba(20, 184, 166, 0.3);
            border-radius: 10px;
            alternate-background-color: rgba(20, 77, 77, 0.3);
        }
        
        QTableWidget::item {
            padding: 10px;
        }
        
        QTableWidget::item:selected {
            background: rgba(20, 184, 166, 0.4);
        }
        
        QHeaderView::section {
            background: rgba(20, 77, 77, 0.7);
            color: #5eead4;
            padding: 10px;
            border: none;
            font-weight: bold;
            border-bottom: 2px solid #14b8a6;
        }
        
        /* ========== PROGRESS BARS ========== */
        QProgressBar {
            border: 1px solid rgba(20, 184, 166, 0.4);
            border-radius: 8px;
            background: rgba(15, 45, 45, 0.6);
            text-align: center;
            color: #dcfff7;
            min-height: 20px;
        }
        
        QProgressBar::chunk {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #14b8a6, stop: 1 #5eead4);
            border-radius: 6px;
        }
        
        /* ========== TABS ========== */
        QTabWidget::pane {
            border: 1px solid rgba(20, 184, 166, 0.3);
            background: rgba(10, 35, 35, 0.4);
            border-radius: 10px;
            top: -1px;
        }
        
        QTabBar::tab {
            background: rgba(20, 77, 77, 0.4);
            color: #5eead4;
            padding: 10px 20px;
            margin: 2px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            border: 1px solid rgba(20, 184, 166, 0.2);
        }
        
        QTabBar::tab:selected {
            background: rgba(20, 184, 166, 0.5);
            color: white;
            border: 1px solid #14b8a6;
            border-bottom: none;
        }
        
        QTabBar::tab:hover {
            background: rgba(20, 184, 166, 0.3);
        }
        
        /* ========== STATUS LABELS ========== */
        QLabel[class="status-connected"] {
            color: #10b981;
            font-weight: bold;
        }
        
        QLabel[class="status-disconnected"] {
            color: #ef4444;
            font-weight: bold;
        }
        
        /* ========== CIRCULAR GAUGE ========== */
        QFrame[class="circular-gauge"] {
            background: qradialgradient(cx: 0.5, cy: 0.5, radius: 0.5,
                fx: 0.5, fy: 0.5,
                stop: 0 rgba(20, 184, 166, 0.2),
                stop: 0.7 rgba(20, 184, 166, 0.1),
                stop: 1 rgba(10, 45, 45, 0.3));
            border: 3px solid rgba(20, 184, 166, 0.4);
            border-radius: 75px;
        }
        
        /* ========== SCROLL BARS ========== */
        QScrollBar:vertical {
            background: rgba(15, 45, 45, 0.3);
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background: rgba(20, 184, 166, 0.5);
            border-radius: 6px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: rgba(20, 184, 166, 0.7);
        }
        """

    def get_security_stylesheet(self):
        """Return enhanced security theme stylesheet"""
        base_styles = self._get_base_stylesheet()
        security_styles = """
        /* Security Theme (Keeping your original) */
        QMainWindow, QDialog {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #0a0f1a, stop: 1 #151a25);
            color: #dce5ff;
        }
        /* ... rest of your security theme ... */
        """
        return base_styles + security_styles

    def get_dark_stylesheet(self):
        """Return dark theme stylesheet"""
        base_styles = self._get_base_stylesheet()
        return base_styles + """
            /* Dark Theme */
            QMainWindow, QDialog {
                background-color: #1a1520;
                color: #f0f0f0;
            }
        """

    def get_theme_names(self):
        """Return available theme names"""
        return ["futuristic", "dark", "light", "security", "professional"]
    
    def get_theme_info(self):
        """Return theme metadata for UI display"""
        return {
            "futuristic": {
                "name": "Futuristic Teal",
                "description": "Modern glassmorphic theme with teal/emerald colors",
                "preview_color": "#14b8a6"
            },
            "dark": {
                "name": "Dark Mode", 
                "description": "Modern dark theme for diagnostics",
                "preview_color": "#1a1520"
            },
            "light": {
                "name": "Light Mode", 
                "description": "Clean light theme for bright environments", 
                "preview_color": "#f5f5f5"
            },
            "security": {
                "name": "Security Blue", 
                "description": "Security-focused blue theme with enhanced visibility",
                "preview_color": "#0a0f1a"
            },
            "professional": {
                "name": "Professional", 
                "description": "VS Code inspired professional theme",
                "preview_color": "#2d2d30"
            }
        }

# Global style manager instance
style_manager = EnhancedStyleManager()