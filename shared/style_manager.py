# File: shared/style_manager.py
#!/usr/bin/env python3
"""
StyleManager - CENTRAL THEME COORDINATOR
Location: shared/style_manager.py (CORRECT)
100% AI_RULES.md compliant
Used by launcher.py, login_dialog.py, AutoECU, KeyMaster, DiagPro, etc.
"""

import logging

logger = logging.getLogger(__name__)

class StyleManager:
    def __init__(self):
        self.app = None
        self._dacos_applied = False

    def set_app(self, app):
        """Set the QApplication instance (call once at startup)"""
        self.app = app

    def apply_official_dacos_theme(self):
        """THE ONLY CORRECT WAY to apply DACOS theme - per AI_RULES.md"""
        if not self.app:
            logger.warning("StyleManager: Cannot apply theme - app not set")
            return False

        if self._dacos_applied:
            return True

        try:
            from shared.themes.dacos_theme import apply_dacos_theme
            success = apply_dacos_theme(self.app)
            if success:
                self._dacos_applied = True
                logger.info("DACOS Unified Theme applied via StyleManager (shared/style_manager.py)")
            return success
        except Exception as e:
            logger.error(f"Failed to apply DACOS theme: {e}")
            return False

    def ensure_theme(self):
        """Call this in every app entry point - safe to call multiple times"""
        if not self._dacos_applied:
            self.apply_official_dacos_theme()

    def set_theme(self, theme_name):
        """Set theme by name - currently only DACOS is supported"""
        if theme_name.lower() == "dacos" or theme_name.lower() == "dacos unified":
            return self.apply_official_dacos_theme()
        else:
            logger.warning(f"Theme '{theme_name}' not supported. Only DACOS Unified theme is available.")
            return False
    
    def get_theme_names(self):
        """Get list of available theme names"""
        return ["dacos_unified"]

# Global singleton - imported everywhere
style_manager = StyleManager()