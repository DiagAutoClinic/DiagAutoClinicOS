import json
import os
import sys
import logging
import importlib
from pathlib import Path

logger = logging.getLogger(__name__)

# Define available themes and their module paths
AVAILABLE_THEMES = {
    "DACOS Cyber-Teal": "shared.themes.dacos_cyber_teal",
    "DACOS Industrial": "shared.themes.dacos_industrial",
    "DACOS Modern": "shared.themes.dacos_modern",
    "DACOS Light": "shared.themes.dacos_light",
    "DACOS Claude Teal Fusion": "shared.themes.dacos_claude_theme1",
    "DACOS Claude Midnight Carbon": "shared.themes.dacos_claude_theme2",
    "DACOS Claude Exclusive": "shared.themes.dacos_claude_theme3",
    "DACOS DeepSeek Neon": "shared.themes.dacos_deepseek_theme1",
    "DACOS DeepSeek Matrix": "shared.themes.dacos_deepseek_theme2",
    "DACOS DeepSeek Exclusive": "shared.themes.dacos_deepseek_theme3",
    "DACOS Grok Core": "shared.themes.dacos_grok_theme1",
    "DACOS Grok Void": "shared.themes.dacos_grok_theme2",
    "DACOS Grok Fusion": "shared.themes.dacos_grok_theme3",
    "DACOS Instrument White": "shared.themes.dacos_only_theme1",
    "DACOS Deep Teal Void": "shared.themes.dacos_only_theme2",
    "DACOS Cognitive Lattice": "shared.themes.dacos_only_theme3",
    "Gemini Theme": "shared.themes.gemini_theme"
}

# Config file location (shared across all apps)
CONFIG_FILE = Path(__file__).resolve().parent / "theme_config.json"

def load_config():
    """Load theme configuration"""
    default_config = {"theme": "DACOS Cyber-Teal"}
    if not CONFIG_FILE.exists():
        # Check for legacy launcher config if new config doesn't exist
        legacy_config = Path(__file__).resolve().parent.parent / "launcher_config.json"
        if legacy_config.exists():
            try:
                with open(legacy_config, 'r') as f:
                    return json.load(f)
            except:
                pass
        return default_config
        
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load theme config: {e}")
        return default_config

def save_config(theme_name):
    """Save theme configuration"""
    try:
        config = {"theme": theme_name}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        logger.info(f"Theme configuration saved: {theme_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to save theme config: {e}")
        return False

def get_current_theme_name():
    """Get currently selected theme name"""
    config = load_config()
    return config.get("theme", "DACOS Cyber-Teal")

def get_theme_module(theme_name=None):
    """Import and return the theme module"""
    if not theme_name:
        theme_name = get_current_theme_name()
    
    module_path = AVAILABLE_THEMES.get(theme_name, "shared.themes.dacos_cyber_teal")
    try:
        return importlib.import_module(module_path)
    except ImportError as e:
        logger.error(f"Failed to import theme module {module_path}: {e}")
        # Fallback to default
        return importlib.import_module("shared.themes.dacos_cyber_teal")

def apply_theme(app):
    """Apply the current theme to a Qt Application"""
    theme_name = get_current_theme_name()
    logger.info(f"Applying theme: {theme_name}")
    
    module = get_theme_module(theme_name)
    
    # Try to find an apply_theme function in the module
    if hasattr(module, "apply_theme"):
        try:
            # Check if the function accepts theme_name argument
            import inspect
            sig = inspect.signature(module.apply_theme)
            if len(sig.parameters) >= 2:
                return module.apply_theme(app, theme_name)
            else:
                return module.apply_theme(app)
        except Exception as e:
            logger.error(f"Error calling apply_theme for {theme_name}: {e}")
            # Continue to fallback
    
    # Fallback: manually apply stylesheet if available
    if hasattr(module, "DACOS_STYLESHEET"):
        try:
            app.setStyle("Fusion")
            app.setStyleSheet(module.DACOS_STYLESHEET)
            return True
        except Exception as e:
            logger.error(f"Failed to apply stylesheet: {e}")
            return False
            
    return False

def get_theme_dict():
    """Get the raw theme dictionary (colors)"""
    module = get_theme_module()
    # Check for various naming conventions
    if hasattr(module, "DACOS_THEME"):
        return module.DACOS_THEME
    if hasattr(module, "THEME"):
        return module.THEME
    
    # Fallback
    from shared.themes.dacos_cyber_teal import DACOS_THEME
    return DACOS_THEME

def get_stylesheet():
    """Get the raw stylesheet string"""
    module = get_theme_module()
    if hasattr(module, "DACOS_STYLESHEET"):
        return module.DACOS_STYLESHEET
    if hasattr(module, "STYLESHEET"):
        return module.STYLESHEET
    
    # Fallback
    from shared.themes.dacos_cyber_teal import DACOS_STYLESHEET
    return DACOS_STYLESHEET
