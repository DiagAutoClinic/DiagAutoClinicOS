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

    def apply_official_theme(self):
        """THE ONLY CORRECT WAY to apply DACOS theme - per AI_RULES.md"""
        if not self.app:
            logger.warning("StyleManager: Cannot apply theme - app not set")
            return False

        if self._dacos_applied:
            return True

        try:
            from shared.themes.dacos_cyber_teal import apply_theme
            success = apply_theme(self.app)
            if success:
                self._dacos_applied = True
                logger.info("DACOS Cyber-Teal Theme applied via StyleManager (shared/style_manager.py)")
            return success
        except Exception as e:
            logger.error(f"Failed to apply DACOS theme: {e}")
            return False

    def ensure_theme(self):
        """Call this in every app entry point - safe to call multiple times"""
        if not self._dacos_applied:
            self.apply_official_theme()

    def set_theme(self, theme_name):
        """Set theme by name"""
        if not self.app:
            logger.warning("StyleManager: Cannot apply theme - app not set")
            return False
            
        theme_key = theme_name.lower().replace(" ", "_")
        
        try:
            # === EXISTING THEMES ===
            if theme_key in ["dacos", "modern", "dacos_modern", "standard"]:
                from shared.themes.dacos_modern import apply_theme
                logger.info(f"Switching to DACOS Modern theme")
                return apply_theme(self.app)
                
            elif theme_key in ["industrial", "pro", "dacos_industrial", "workshop"]:
                from shared.themes.dacos_industrial import apply_theme
                logger.info(f"Switching to DACOS Industrial theme")
                return apply_theme(self.app)
                
            elif theme_key in ["gemini", "gemini_exclusive", "starlight"]:
                from shared.themes.gemini_theme import apply_theme
                logger.info(f"Switching to Gemini Exclusive theme")
                return apply_theme(self.app)
                
            elif theme_key in ["dacos_cyber_teal", "cyber_teal"]:
                 return self.apply_official_theme()

            # === CLAUDE THEMES ===
            elif theme_key == "dacos_teal_fusion":
                from shared.themes.dacos_claude import apply_theme
                return apply_theme(self.app, "DACOS Teal Fusion")
            elif theme_key == "dacos_midnight_carbon":
                from shared.themes.dacos_claude import apply_theme
                return apply_theme(self.app, "DACOS Midnight Carbon")

            # === DEEPSEEK THEMES ===
            elif theme_key == "dacos_neon_professional":
                from shared.themes.dacos_deepseek import apply_theme
                return apply_theme(self.app, "DACOS Neon Professional")
            elif theme_key == "dacos_matrix_dark":
                from shared.themes.dacos_deepseek import apply_theme
                return apply_theme(self.app, "DACOS Matrix Dark")
            elif theme_key == "dacos_deepseek_exclusive":
                from shared.themes.dacos_deepseek import apply_theme
                return apply_theme(self.app, "DACOS DeepSeek Exclusive")

            # === GROK THEMES ===
            elif theme_key == "dacos_core":
                from shared.themes.dacos_grok import apply_theme
                return apply_theme(self.app, "DACOS Core")
            elif theme_key == "dacos_void":
                from shared.themes.dacos_grok import apply_theme
                return apply_theme(self.app, "DACOS Void")
            elif theme_key == "dacos_grok":
                from shared.themes.dacos_grok import apply_theme
                return apply_theme(self.app, "DACOS Grok")

            # === LIGHT THEME ===
            elif theme_key in ["dacos_light", "light", "white_horizon"]:
                from shared.themes.dacos_light import apply_theme
                return apply_theme(self.app)

            # === DACOS ONLY THEMES ===
            elif theme_key == "dacos_instrument_white":
                from shared.themes.dacos_only import apply_theme
                return apply_theme(self.app, "DACOS Instrument White")
            elif theme_key == "dacos_deep_teal_void":
                from shared.themes.dacos_only import apply_theme
                return apply_theme(self.app, "DACOS Deep Teal Void")
            elif theme_key == "dacos_cognitive_lattice":
                from shared.themes.dacos_only import apply_theme
                return apply_theme(self.app, "DACOS Cognitive Lattice")
                 
            else:
                logger.warning(f"Theme '{theme_name}' not supported. Defaulting to DACOS Cyber-Teal.")
                return self.apply_official_theme()
                
        except ImportError as e:
            logger.error(f"Failed to import theme module for '{theme_name}': {e}")
            return False
        except Exception as e:
            logger.error(f"Error applying theme '{theme_name}': {e}")
            return False
    
    def get_theme_names(self):
        """Get list of available theme names"""
        return [
            "Modern", "Industrial", "Gemini", "DACOS Cyber-Teal",
            "DACOS Teal Fusion", "DACOS Midnight Carbon",
            "DACOS Neon Professional", "DACOS Matrix Dark", "DACOS DeepSeek Exclusive",
            "DACOS Core", "DACOS Void", "DACOS Grok",
            "DACOS Light",
            "DACOS Instrument White", "DACOS Deep Teal Void", "DACOS Cognitive Lattice",
            "DACOS Kinetic Blueprint", "DACOS Command Center", "DACOS Industrial SCADA"
        ]

# Global singleton - imported everywhere
style_manager = StyleManager()