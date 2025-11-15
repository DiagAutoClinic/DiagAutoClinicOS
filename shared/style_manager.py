"""
DiagAutoClinicOS - Enhanced Style Manager
FIXED: Proper class name and method names
"""

import logging

logger = logging.getLogger(__name__)

class StyleManager:
    def __init__(self):
        self.available_themes = {
            'futuristic': self._futuristic_theme(),
            'dark_clinic': self._dark_clinic_theme(),
            'neon_clinic': self._neon_clinic_theme(),
            'security': self._security_theme(),
            'dark': self._dark_theme(),
            'light': self._light_theme(),
            'professional': self._professional_theme()
        }
        self.active_theme = 'neon_clinic'

    def _futuristic_theme(self):
        return """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f172a, stop:1 #1e293b);
                color: #e2e8f0;
            }
            QFrame[class="glass-card"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 41, 59, 0.8), 
                    stop:1 rgba(15, 23, 42, 0.9));
                border: 1px solid rgba(148, 163, 184, 0.3);
                border-radius: 15px;
            }
            QPushButton[class="primary"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #14b8a6, stop:1 #0d9488);
                border: none;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton[class="primary"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0d9488, stop:1 #0f766e);
            }
        """

    def _dark_clinic_theme(self):
        return """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a, stop:1 #1a1a1a);
                color: #ffffff;
            }
            QFrame[class="glass-card"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(40, 40, 40, 0.9), 
                    stop:1 rgba(20, 20, 20, 0.9));
                border: 1px solid rgba(100, 100, 100, 0.3);
                border-radius: 12px;
            }
        """

    def _neon_clinic_theme(self):
        return """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0b0c10, stop:1 #1f2833);
                color: #c5c6c7;
            }
            QFrame[class="glass-card"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(31, 40, 51, 0.9), 
                    stop:1 rgba(11, 12, 16, 0.9));
                border: 1px solid rgba(102, 252, 241, 0.3);
                border-radius: 15px;
            }
            QPushButton[class="primary"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #66fcf1, stop:1 #45a29e);
                border: none;
                border-radius: 10px;
                color: #0b0c10;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton[class="primary"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #45a29e, stop:1 #1f7a75);
            }
            .hero-title {
                color: #66fcf1;
                font-size: 24pt;
                font-weight: bold;
            }
            .stat-card {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(31, 40, 51, 0.8), 
                    stop:1 rgba(11, 12, 16, 0.9));
                border: 1px solid rgba(102, 252, 241, 0.2);
                border-radius: 10px;
                padding: 15px;
            }
        """

    def _security_theme(self):
        return """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1f2c, stop:1 #0d1117);
                color: #e2e8f0;
            }
            QFrame[class="glass-card"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 41, 59, 0.9), 
                    stop:1 rgba(15, 23, 42, 0.9));
                border: 1px solid rgba(239, 68, 68, 0.3);
                border-radius: 12px;
            }
        """

    def _dark_theme(self):
        return """
            QMainWindow {
                background: #1e1e1e;
                color: #ffffff;
            }
            QFrame[class="glass-card"] {
                background: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 8px;
            }
        """

    def _light_theme(self):
        return """
            QMainWindow {
                background: #f5f5f5;
                color: #333333;
            }
            QFrame[class="glass-card"] {
                background: #ffffff;
                border: 1px solid #dddddd;
                border-radius: 8px;
            }
        """

    def _professional_theme(self):
        return """
            QMainWindow {
                background: #2c3e50;
                color: #ecf0f1;
            }
            QFrame[class="glass-card"] {
                background: #34495e;
                border: 1px solid #46627f;
                border-radius: 6px;
            }
        """

    def set_theme(self, theme_name):
        """Set the application theme"""
        if theme_name not in self.available_themes:
            logger.warning(f"Unknown theme '{theme_name}'. Falling back to 'neon_clinic'.")
            theme_name = 'neon_clinic'

        self.active_theme = theme_name
        logger.info(f"✓ Applied theme: {theme_name}")
        return self.available_themes[theme_name]

    def get_theme_names(self):
        """Get list of available theme names"""
        return list(self.available_themes.keys())

    def get_theme_info(self):
        """Return theme metadata for UI display"""
        return {theme: {"name": theme.replace('_', ' ').title()} for theme in self.available_themes}

# Create global instance
style_manager = StyleManager()
# At the very end of style_manager.py, after style_manager = StyleManager()
print("style_manager instance created successfully")  # Temporary debug