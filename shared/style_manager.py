"""
DiagAutoClinicOS - Enhanced Style Manager
FIXED: Proper class name and method names
Consolidated: Themes now loaded from separate .qss files
"""

import logging
import os

logger = logging.getLogger(__name__)

class StyleManager:
    def __init__(self):
        self.themes_dir = os.path.join(os.path.dirname(__file__), 'themes')
        self.available_themes = {}
        self._load_themes()
        self.active_theme = 'neon_clinic'
        self.app = None

    def _load_themes(self):
        """Load all theme files from the themes directory"""
        theme_files = {
            'futuristic': 'futuristic.qss',
            'dark_clinic': 'dark_clinic.qss',
            'neon_clinic': 'neon_clinic.qss',
            'security': 'security.qss',
            'dark': 'dark.qss',
            'light': 'light.qss',
            'professional': 'professional.qss',
            'dacos': 'dacos.qss'
        }

        for theme_name, filename in theme_files.items():
            theme_path = os.path.join(self.themes_dir, filename)
            try:
                with open(theme_path, 'r', encoding='utf-8') as f:
                    self.available_themes[theme_name] = f.read()
                logger.info(f"✓ Loaded theme: {theme_name}")
            except FileNotFoundError:
                logger.warning(f"Theme file not found: {theme_path}")
                # Fallback to basic theme
                self.available_themes[theme_name] = self._create_fallback_theme(theme_name)
            except Exception as e:
                logger.error(f"Error loading theme {theme_name}: {e}")
                self.available_themes[theme_name] = self._create_fallback_theme(theme_name)

    def _create_fallback_theme(self, theme_name):
        """Create a basic fallback theme if file loading fails"""
        return f"""
            QMainWindow {{
                background: #2c3e50;
                color: #ecf0f1;
            }}
            QFrame[class="glass-card"] {{
                background: #34495e;
                border: 1px solid #46627f;
                border-radius: 8px;
                padding: 16px;
                margin: 8px;
            }}
            /* Fallback theme for {theme_name} */
        """

    def set_theme(self, theme_name):
        """Set the application theme"""
        if theme_name not in self.available_themes:
            logger.warning(f"Unknown theme '{theme_name}'. Falling back to 'neon_clinic'.")
            theme_name = 'neon_clinic'

        self.active_theme = theme_name
        logger.info(f"✓ Applied theme: {theme_name}")
        return self.available_themes[theme_name]

    def set_app(self, app):
        """Set the QApplication instance for theme application"""
        self.app = app

    def apply_theme(self):
        """Apply the active theme to the stored QApplication"""
        if self.app and hasattr(self.app, 'setStyleSheet') and self.active_theme in self.available_themes:
            self.app.setStyleSheet(self.available_themes[self.active_theme])
            logger.info(f"✓ Theme applied to application: {self.active_theme}")
        else:
            logger.warning("Could not apply theme to application")

    def get_theme_names(self):
        """Get list of available theme names"""
        return list(self.available_themes.keys())

    def get_theme_info(self):
        """Return theme metadata for UI display"""
        return {theme: {"name": theme.replace('_', ' ').title()} for theme in self.available_themes}

    def set_security_level(self, level):
        """Set security level (stub for compatibility)"""
        logger.info(f"Security level set to: {level}")
        # Could modify theme based on security level if needed

# Create global instance
style_manager = StyleManager()
# At the very end of style_manager.py, after style_manager = StyleManager()
print("style_manager instance created successfully")  # Temporary debug