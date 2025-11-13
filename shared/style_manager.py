#!/usr/bin/env python3
"""
Enhanced Style Manager for DiagAutoClinicOS
Full open-source ready version with all themes completed
"""

import os
import logging
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication, QStyleFactory

logger = logging.getLogger(__name__)

class EnhancedStyleManager:
    def __init__(self):
        self.settings = QSettings("DiagAutoClinicOS", "Style")
        self.current_theme = self.settings.value("theme", "futuristic")
        self.font_family = self.settings.value("font_family", "Segoe UI")
        self.font_size = int(self.settings.value("font_size", "10"))
        self.security_level = "basic"
        
    def set_security_level(self, level: str):
        """Update security level and re-apply current theme"""
        self.security_level = level.lower()
        self.set_theme(self.current_theme)
        
    def set_theme(self, theme_name: str):
        """Apply theme by name with security integration"""
        valid_themes = self.get_theme_names()
        if theme_name not in valid_themes:
            logger.warning(f"Unknown theme '{theme_name}'. Falling back to 'futuristic'.")
            theme_name = "futuristic"
        
        self.current_theme = theme_name
        self.settings.setValue("theme", theme_name)
        
        theme_map = {
            "dark": self.apply_dark_theme,
            "light": self.apply_light_theme,
            "security": self.apply_security_theme,
            "professional": self.apply_professional_theme,
            "futuristic": self.apply_futuristic_theme,
            "neon_clinic": self.apply_neon_clinic_theme
        }
        
        apply_func = theme_map.get(theme_name, self.apply_futuristic_theme)
        apply_func()
            
    def set_font(self, font_family: str = None, font_size: int = None):
        """Update font settings and re-apply theme"""
        if font_family:
            self.font_family = font_family
            self.settings.setValue("font_family", font_family)
        if font_size:
            self.font_size = font_size
            self.settings.setValue("font_size", str(font_size))
        self.set_theme(self.current_theme)

    def apply_futuristic_theme(self):
        """Apply Futuristic Teal theme"""
        app = QApplication.instance()
        app.setStyle(QStyleFactory.create("Fusion"))
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(10, 25, 25))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 255, 250))
        palette.setColor(QPalette.ColorRole.Base, QColor(15, 35, 35))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(20, 45, 45))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(20, 77, 77))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(220, 255, 250))
        palette.setColor(QPalette.ColorRole.Button, QColor(20, 77, 77))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 255, 250))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(100, 255, 218))
        palette.setColor(QPalette.ColorRole.Link, QColor(20, 184, 166))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(20, 184, 166))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        app.setPalette(palette)
        app.setStyleSheet(self.get_futuristic_stylesheet())

    def apply_security_theme(self):
        """Apply Security Blue theme with level adjustments"""
        app = QApplication.instance()
        app.setStyle(QStyleFactory.create("Fusion"))
        
        palette = QPalette()
        if self.security_level == "dealer":
            palette.setColor(QPalette.ColorRole.Window, QColor(10, 15, 25))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 230, 255))
            accent = QColor(74, 138, 255)
        else:
            palette.setColor(QPalette.ColorRole.Window, QColor(15, 20, 30))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(200, 210, 235))
            accent = QColor(90, 110, 180)
        
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 30, 40))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 40, 50))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(45, 50, 60))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(220, 230, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(220, 230, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(60, 70, 100))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 230, 255))
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.cyan)
        palette.setColor(QPalette.ColorRole.Link, accent)
        palette.setColor(QPalette.ColorRole.Highlight, accent)
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        app.setPalette(palette)
        app.setStyleSheet(self.get_security_stylesheet())

    def apply_dark_theme(self):
        """Apply Dark theme"""
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
        """Apply Light theme"""
        app = QApplication.instance()
        app.setStyle(QStyleFactory.create("Fusion"))
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 245))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(30, 30, 35))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 250))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(30, 30, 35))
        palette.setColor(QPalette.ColorRole.Text, QColor(30, 30, 35))
        palette.setColor(QPalette.ColorRole.Button, QColor(220, 220, 230))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(30, 30, 35))
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 122, 204))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 122, 204))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        app.setPalette(palette)
        app.setStyleSheet(self.get_light_stylesheet())

    def apply_professional_theme(self):
        """Apply Professional (VS Code inspired) theme"""
        app = QApplication.instance()
        app.setStyle(QStyleFactory.create("Fusion"))
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 48))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(50, 50, 50))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Button, QColor(60, 60, 60))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 122, 204))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 122, 204))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        app.setPalette(palette)
        app.setStyleSheet(self.get_professional_stylesheet())

def apply_neon_clinic_theme(self):
    """Apply Neon Clinic theme with security tint"""
    app = QApplication.instance()
    app.setStyle(QStyleFactory.create("Fusion"))

    # === Palette ===
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(10, 26, 46))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(224, 248, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(15, 30, 55))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(20, 40, 70))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(20, 50, 90))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(224, 248, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(20, 50, 90))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(224, 248, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(0, 255, 170))
    palette.setColor(QPalette.ColorRole.Link, QColor(0, 212, 255))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 212, 255))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)

    if self.security_level == "dealer":
        palette.setColor(QPalette.ColorRole.Highlight, QColor(100, 180, 255))

    app.setPalette(palette)

    # === Load QSS with FIXED image path ===
    qss_path = os.path.join(os.path.dirname(__file__), "themes", "neon_clinic.qss")
    
    if not os.path.exists(qss_path):
        logger.warning(f"QSS not found: {qss_path}")
        app.setStyleSheet(self.get_futuristic_stylesheet())
        return

    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            qss = f.read()

        # === CORRECT PROJECT ROOT (only go up once from shared/) ===
        from pathlib import Path
        shared_dir = Path(__file__).resolve().parent
        project_root = shared_dir.parent  # This is DiagAutoClinicOS/
        img_path = project_root / "resources" / "bg" / "neon_clinic_bg.jpg"
        img_url = f"file:///{img_path.as_posix().replace('\\', '/')}"

        logger.info(f"[NeonClinic] Using image: {img_path}")

        # Replace ANY relative path with absolute
        qss = qss.replace("../../resources/bg/neon_clinic_bg.jpg", img_url)
        qss = qss.replace("../resources/bg/neon_clinic_bg.jpg", img_url)
        qss = qss.replace("resources/bg/neon_clinic_bg.jpg", img_url)
        qss = qss.replace("neon_clinic_bg.jpg", img_url)

        app.setStyleSheet(qss)
        logger.info("Neon Clinic theme applied successfully")

    except Exception as e:
        logger.error(f"Failed to apply theme: {e}")
        app.setStyleSheet(self.get_futuristic_stylesheet())

    def get_futuristic_stylesheet(self):
        """Return Futuristic theme stylesheet"""
        return """
        * { font-family: "Segoe UI", sans-serif; font-size: 10pt; }
        QMainWindow { background: #0a1a2e; }
        QFrame.glass-card {
            background: rgba(15, 45, 45, 0.6);
            border: 1px solid rgba(20, 184, 166, 0.3);
            border-radius: 12px;
            padding: 10px;
        }
        QPushButton {
            background: #14b8a6;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
        }
        QPushButton:hover { background: #5eead4; }
        QComboBox {
            background: #0f2b4a;
            color: #e0f7ff;
            border: 1px solid #00a8cc;
            border-radius: 6px;
            padding: 4px;
        }
        QProgressBar { background: #0f2b4a; border: 1px solid #00a8cc; color: #e0f7ff; }
        QTabWidget::pane { border: 1px solid #00a8cc; background: #0a1f38; }
        """

    def get_security_stylesheet(self):
        """Return Security theme stylesheet"""
        return """
        QMainWindow { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0a0f1a, stop:1 #151a25); color: #dce5ff; }
        QFrame.glass-card { background: rgba(20, 40, 60, 0.6); border: 1px solid rgba(74, 138, 255, 0.3); }
        QPushButton { background: #4a8aff; color: white; }
        QPushButton:hover { background: #74aaff; }
        QComboBox { background: #151a25; color: #dce5ff; border: 1px solid #4a8aff; }
        QProgressBar { background: #151a25; border: 1px solid #4a8aff; color: #dce5ff; }
        QTabWidget::pane { border: 1px solid #4a8aff; background: #0a0f1a; }
        """

    def get_dark_stylesheet(self):
        """Return Dark theme stylesheet"""
        return """
        QMainWindow { background-color: #1a1a1a; color: #f0f0f0; }
        QFrame.glass-card { background: rgba(30, 30, 30, 0.6); border: 1px solid rgba(50, 50, 50, 0.3); }
        QPushButton { background: #333333; color: #f0f0f0; }
        QPushButton:hover { background: #444444; }
        QComboBox { background: #222222; color: #f0f0f0; border: 1px solid #333333; }
        QProgressBar { background: #222222; border: 1px solid #333333; color: #f0f0f0; }
        QTabWidget::pane { border: 1px solid #333333; background: #1a1a1a; }
        """

    def get_light_stylesheet(self):
        """Return Light theme stylesheet"""
        return """
        QMainWindow { background-color: #f0f0f0; color: #333333; }
        QFrame.glass-card { background: rgba(255, 255, 255, 0.8); border: 1px solid rgba(200, 200, 200, 0.3); }
        QPushButton { background: #dddddd; color: #333333; }
        QPushButton:hover { background: #cccccc; }
        QComboBox { background: #ffffff; color: #333333; border: 1px solid #dddddd; }
        QProgressBar { background: #ffffff; border: 1px solid #dddddd; color: #333333; }
        QTabWidget::pane { border: 1px solid #dddddd; background: #f0f0f0; }
        """

    def get_professional_stylesheet(self):
        """Return Professional theme stylesheet"""
        return """
        QMainWindow { background-color: #1e1e1e; color: #d4d4d4; }
        QFrame.glass-card { background: rgba(37, 37, 38, 0.6); border: 1px solid rgba(60, 60, 60, 0.3); }
        QPushButton { background: #252526; color: #d4d4d4; }
        QPushButton:hover { background: #333333; }
        QComboBox { background: #252526; color: #d4d4d4; border: 1px solid #333333; }
        QProgressBar { background: #252526; border: 1px solid #333333; color: #d4d4d4; }
        QTabWidget::pane { border: 1px solid #333333; background: #1e1e1e; }
        """

    def get_theme_names(self):
        """Return available theme names"""
        return ["futuristic", "dark", "light", "security", "professional", "neon_clinic"]
    
    def get_theme_info(self):
        """Return theme metadata for UI display"""
        return {
            "futuristic": {"name": "Futuristic Teal", "description": "Modern glassmorphic theme with teal/emerald colors", "preview_color": "#14b8a6"},
            "dark": {"name": "Dark Mode", "description": "Modern dark theme for diagnostics", "preview_color": "#1a1520"},
            "light": {"name": "Light Mode", "description": "Clean light theme for bright environments", "preview_color": "#f5f5f5"},
            "security": {"name": "Security Blue", "description": "Security-focused blue theme with enhanced visibility", "preview_color": "#0a0f1a"},
            "professional": {"name": "Professional", "description": "VS Code inspired professional theme", "preview_color": "#2d2d30"},
            "neon_clinic": {"name": "Neon Clinic", "description": "Sci-fi neon teal with glow effects", "preview_color": "#00d4ff"}
        }

# Global style manager instance
style_manager = EnhancedStyleManager()