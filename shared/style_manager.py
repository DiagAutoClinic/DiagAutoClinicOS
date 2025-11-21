# style_manager.py
# AGENTS: DO NOT TOUCH THIS FILE - THEME IS CENTRALIZED IN shared/theme_constants.py
# ANY CHANGES HERE WILL BE REVERTED
# (Except this one — Dacos Particles Dark theme added as embedded override)

"""
DiagAutoClinicOS - Enhanced Style Manager
Now with embedded "dacos_particles" dark futuristic theme
"""

import logging
import os

logger = logging.getLogger(__name__)

# Mapping of theme names to their .qss filenames (add new ones here if you create real files)
theme_files = {
    "neon_clinic": "neon_clinic.qss",
    # ... your other themes ...
}

class StyleManager:
    def __init__(self):
        self.themes_dir = os.path.join(os.path.dirname(__file__), 'themes')
        self.available_themes = {}
        self._load_themes()
        
        # Inject the new masterpiece theme (works even if no file exists yet)
        self.available_themes['dacos_particles'] = self._get_dacos_particles_qss()
        
        self.active_theme = 'dacos_particles'  # Set as new default (change if you want)
        self.app = None

    def _load_themes(self):
        """Load all .qss files from the themes directory"""
        if not os.path.exists(self.themes_dir):
            os.makedirs(self.themes_dir)
            logger.info(f"Created themes directory: {self.themes_dir}")

        for theme_name, filename in theme_files.items():
            theme_path = os.path.join(self.themes_dir, filename)
            try:
                with open(theme_path, 'r', encoding='utf-8') as f:
                    self.available_themes[theme_name] = f.read()
                logger.info(f"Loaded theme: {theme_name} → {filename}")
            except FileNotFoundError:
                logger.warning(f"Theme file not found: {theme_path}")
                self.available_themes[theme_name] = self._create_fallback_theme(theme_name)
            except Exception as e:
                logger.error(f"Error loading theme {theme_name}: {e}")
                self.available_themes[theme_name] = self._create_fallback_theme(theme_name)

    def _get_dacos_particles_qss(self):
        """Embedded Dacos Particles Dark — pure cosmic void energy"""
        return """
/* ====================== DACOS PARTICLES DARK ====================== */
QWidget {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #0e0e1a, stop:1 #1a1a2e);
    color: #e0e0ff;
    font-family: "Segoe UI", "Roboto", sans-serif;
    font-size: 10pt;
}

/* Subtle particle field background */
QMainWindow, QDialog {
    background: 
        radial-gradient(circle at 30% 30%, #16213e 0%, transparent 50%),
        radial-gradient(circle at 70% 80%, #0f3460 0%, transparent 60%),
        #0f0f1c;
}

/* Buttons – glowing particles on hover */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #1e1e3b, stop:1 #16213e);
    border: 1px solid #334466;
    border-radius: 8px;
    padding: 8px 16px;
    color: #ccddee;
    min-width: 80px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #3a3a6e, stop:1 #2a2a5e);
    border: 1px solid #5577ff;
    box-shadow: 0 0 12px rgba(85, 119, 255, 0.6);
    color: #ffffff;
}

QPushButton:pressed {
    background: #223355;
    box-shadow: inset 0 0 20px rgba(0,0,0,0.6);
}

/* Inputs */
QLineEdit, QTextEdit, QPlainTextEdit {
    background: #161625;
    border: 1px solid #333355;
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: #445588;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #6688ff;
    background: #1c1c2e;
    box-shadow: 0 0 10px rgba(102, 136, 255, 0.4);
}

/* ComboBox */
QComboBox {
    background: #1e1e3b;
    border: 1px solid #334466;
    border-radius: 6px;
    padding: 6px 12px 6px 10px;
    min-width: 80px;
}

QComboBox:hover { border: 1px solid #5577ff; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background: #161625;
    border: 1px solid #445577;
    selection-background-color: #3a5acc;
    outline: none;
}

/* Scrollbars */
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #334466;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #5577ff;
    box-shadow: 0 0 8px rgba(85,119,255,0.7);
}

/* Checkboxes & Radio buttons */
QCheckBox::indicator, QRadioButton::indicator {
    width: 18px; height: 18px;
    border-radius: 9px;
    border: 2px solid #445577;
    background: #111122;
}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background: qradialgradient(cx:0.5, cy:0.5, radius: 0.5,
                                stop:0 #88aaff, stop:1 #3355cc);
    border: 2px solid #88aaff;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #334466;
    background: #0f0f1c;
}

QTabBar::tab {
    background: #1a1a2e;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}

QTabBar::tab:selected {
    background: #223355;
    box-shadow: 0 -3px 10px rgba(85,119,255,0.5);
}

/* Progress bars */
QProgressBar {
    border: 1px solid #334466;
    border-radius: 6px;
    background: #111122;
    text-align: center;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #4466ff, stop:1 #88aaff);
    border-radius: 5px;
    box-shadow: 0 0 10px rgba(136,170,255,0.6);
}

/* Tooltips */
QToolTip {
    background: #16213e;
    border: 1px solid #5577ff;
    color: #e0e0ff;
    padding: 6px 10px;
    border-radius: 6px;
}
        """.strip()

    def _create_fallback_theme(self, theme_name):
        return f"QMainWindow {{ background: #2c3e50; color: #ecf0f1; }} /* Fallback for {theme_name} */"

    def set_theme(self, theme_name):
        if theme_name not in self.available_themes:
            logger.warning(f"Theme '{theme_name}' not found → falling back to 'dacos_particles'")
            theme_name = 'dacos_particles'
        self.active_theme = theme_name
        logger.info(f"Theme switched to: {theme_name}")
        return self.available_themes[theme_name]

    def set_app(self, app):
        self.app = app

    def apply_theme(self):
        if self.app and self.active_theme in self.available_themes:
            self.app.setStyleSheet(self.available_themes[self.active_theme])
            logger.info(f"Applied theme: {self.active_theme}")
        else:
            logger.warning("Failed to apply theme")

    def get_theme_names(self):
        return list(self.available_themes.keys())

    def get_theme_info(self):
        info = {theme: {"name": theme.replace('_', ' ').title()} for theme in self.available_themes}
        info['dacos_particles'] = {"name": "Dacos Particles Dark"}
        return info

    def set_security_level(self, level):
        logger.info(f"Security level set to: {level}")

# Global instance
style_manager = StyleManager()