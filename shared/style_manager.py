#!/usr/bin/env python3
"""
Enhanced Style Manager for DiagAutoClinicOS
Fixed security integration and comprehensive theming
"""

from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtWidgets import QApplication, QStyleFactory
import logging

logger = logging.getLogger(__name__)

class EnhancedStyleManager:
    def __init__(self):
        self.settings = QSettings("DiagAutoClinicOS", "Style")
        self.current_theme = self.settings.value("theme", "security")
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
            logger.warning(f"Unknown theme {theme_name}. Using security theme.")
            theme_name = "security"
        
        self.current_theme = theme_name
        self.settings.setValue("theme", theme_name)
        
        theme_methods = {
            "dark": self.apply_dark_theme,
            "light": self.apply_light_theme,
            "security": self.apply_security_theme,
            "professional": self.apply_professional_theme
        }
        
        theme_methods.get(theme_name, self.apply_security_theme)()
            
    def set_font(self, font_family=None, font_size=None):
        """Set application font with security considerations"""
        if font_family:
            self.font_family = font_family
            self.settings.setValue("font_family", font_family)
        if font_size:
            self.font_size = font_size
            self.settings.setValue("font_size", str(font_size))
        
        self.set_theme(self.current_theme)
        
    def apply_security_theme(self):
        """Apply security-focused theme for diagnostic operations"""
        app = QApplication.instance()
        app.setStyle(QStyleFactory.create("Fusion"))
        
        # Security-based color palette
        palette = QPalette()
        if self.security_level == "dealer":
            # Dealer-level security - enhanced colors
            palette.setColor(QPalette.ColorRole.Window, QColor(10, 15, 25))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 230, 255))
            accent_color = QColor(74, 138, 255)
        else:
            # Standard security
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

    def get_security_stylesheet(self):
        """Return enhanced security theme stylesheet - FIXED VERSION"""
        base_styles = self._get_base_stylesheet()
        security_styles = """
        /* Enhanced Security Theme for DiagAutoClinicOS */
        QMainWindow, QDialog {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #0a0f1a, stop: 1 #151a25);
            color: #dce5ff;
        }
        
        /* User Info Header */
        QLabel[class="user-info"] {
            color: #4a8aff;
            font-weight: bold;
            padding: 8px 12px;
            background-color: rgba(74, 138, 255, 0.15);
            border-radius: 6px;
            border: 1px solid rgba(74, 138, 255, 0.3);
        }
        
        /* Tab Headers */
        QLabel[class="tab-header"] {
            font-size: 16pt;
            font-weight: bold;
            color: #4a8aff;
            padding: 12px;
            background-color: rgba(74, 138, 255, 0.1);
            border-radius: 8px;
            margin: 8px;
            border: 1px solid rgba(74, 138, 255, 0.2);
        }
        
        /* Function/Procedure Names */
        QLabel[class="function-name"], QLabel[class="procedure-name"] {
            font-size: 14pt;
            font-weight: bold;
            color: #ffaa00;
            padding: 8px;
            background-color: rgba(255, 170, 0, 0.1);
            border-radius: 4px;
        }
        
        /* Security Level Indicators */
        QLabel[class="security-info"] {
            color: #ff6b6b;
            font-weight: bold;
            padding: 6px 10px;
            background-color: rgba(255, 107, 107, 0.15);
            border-radius: 4px;
            border: 1px solid rgba(255, 107, 107, 0.3);
        }
        
        QLabel[class="security-success"] {
            color: #6bff6b;
            font-weight: bold;
            padding: 6px 10px;
            background-color: rgba(107, 255, 107, 0.15);
            border-radius: 4px;
            border: 1px solid rgba(107, 255, 107, 0.3);
        }
        
        /* Enhanced Group Boxes */
        QGroupBox {
            color: #4a8aff;
            font-weight: bold;
            border: 2px solid #3a4a6a;
            border-radius: 8px;
            margin-top: 1ex;
            padding-top: 12px;
            background-color: rgba(30, 35, 45, 0.7);
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 10px 0 10px;
            color: #4a8aff;
            background-color: rgba(30, 35, 45, 0.9);
        }
        
        /* Security Lists */
        QListWidget {
            background-color: #1a1f2a;
            color: #dce5ff;
            border: 1px solid #2a3a5a;
            border-radius: 6px;
            padding: 5px;
        }
        
        QListWidget::item {
            padding: 10px;
            border-bottom: 1px solid #2a3a5a;
            border-radius: 3px;
            margin: 2px;
        }
        
        QListWidget::item:selected {
            background-color: #2a5aaa;
            color: white;
            border: 1px solid #3a6aba;
        }
        
        QListWidget::item:hover {
            background-color: #1a4a9a;
        }
        
        /* Enhanced Text Areas */
        QTextEdit {
            background-color: #1a1f2a;
            color: #dce5ff;
            border: 1px solid #2a3a5a;
            border-radius: 6px;
            padding: 10px;
            selection-background-color: #2a5aaa;
        }
        
        QTextEdit:focus {
            border: 1px solid #4a8aff;
        }
        
        /* Security Status Display */
        QTextEdit[class="security-log"] {
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 9pt;
            background-color: #0a0f1a;
            color: #a0b0ff;
            border: 1px solid #1a2a3a;
        }
        
        /* Buttons with Security Levels */
        QPushButton[class="security-button"] {
            background-color: #4a6cd4;
            color: white;
            border: 2px solid #3a5cb4;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: bold;
            min-width: 120px;
        }
        
        QPushButton[class="security-button"]:hover {
            background-color: #3a5cb4;
            border-color: #2a4c94;
        }
        
        QPushButton[class="security-button"]:pressed {
            background-color: #2a4c94;
        }
        
        QPushButton[class="high-security"] {
            background-color: #d44a4a;
            border-color: #b43a3a;
        }
        
        QPushButton[class="medium-security"] {
            background-color: #d4a44a;
            border-color: #b4943a;
        }
        
        QPushButton[class="low-security"] {
            background-color: #4ad44a;
            border-color: #3ab43a;
        }
        
        /* Tables for Diagnostic Data */
        QTableWidget {
            background-color: #1a1f2a;
            color: #dce5ff;
            gridline-color: #2a3a5a;
            border: 1px solid #2a3a5a;
            border-radius: 6px;
            alternate-background-color: #202530;
        }
        
        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #2a3a5a;
        }
        
        QTableWidget::item:selected {
            background-color: #2a5aaa;
            color: white;
        }
        
        QHeaderView::section {
            background-color: #2a3a5a;
            color: #dce5ff;
            padding: 8px;
            border: none;
            font-weight: bold;
        }
        
        /* Progress Bars */
        QProgressBar {
            border: 1px solid #2a3a5a;
            border-radius: 4px;
            background-color: #1a1f2a;
            text-align: center;
            color: #dce5ff;
        }
        
        QProgressBar::chunk {
            background-color: #4a8aff;
            border-radius: 3px;
        }
        
        /* Combo Boxes */
        QComboBox {
            background-color: #1a1f2a;
            color: #dce5ff;
            border: 1px solid #2a3a5a;
            border-radius: 4px;
            padding: 5px;
            min-width: 100px;
        }
        
        QComboBox::drop-down {
            border: none;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 1px solid #2a3a5a;
            padding: 5px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #1a1f2a;
            color: #dce5ff;
            border: 1px solid #2a3a5a;
            selection-background-color: #2a5aaa;
        }
        
        /* Line Edits */
        QLineEdit {
            background-color: #1a1f2a;
            color: #dce5ff;
            border: 1px solid #2a3a5a;
            border-radius: 4px;
            padding: 8px;
        }
        
        QLineEdit:focus {
            border: 1px solid #4a8aff;
        }
        
        QLineEdit[class="security-input"] {
            color: #ffcc00;
            font-family: 'Consolas', 'Monaco', monospace;
            font-weight: bold;
            letter-spacing: 1px;
        }
        
        /* Tab Widget */
        QTabWidget::pane {
            border: 1px solid #2a3a5a;
            background-color: #1a1f2a;
            border-radius: 6px;
        }
        
        QTabWidget::tab-bar {
            alignment: center;
        }
        
        QTabBar::tab {
            background-color: #2a3a5a;
            color: #a0b0ff;
            padding: 8px 16px;
            margin: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }
        
        QTabBar::tab:selected {
            background-color: #4a8aff;
            color: white;
        }
        
        QTabBar::tab:hover {
            background-color: #3a7aef;
        }
        """
        return base_styles + security_styles

    def get_dark_stylesheet(self):
        """Return dark theme stylesheet"""
        base_styles = self._get_base_stylesheet()
        return base_styles + """
            /* Dark Theme for DiagAutoClinicOS */
            QMainWindow, QDialog {
                background-color: #1a1520;
                color: #f0f0f0;
            }
            /* Additional dark theme styles... */
        """

    def get_theme_names(self):
        """Return available theme names"""
        return ["dark", "light", "security", "professional"]
    
    def get_theme_info(self):
        """Return theme metadata for UI display"""
        return {
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
