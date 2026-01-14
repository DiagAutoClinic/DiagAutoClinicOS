
import sys
import os
import logging

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'AutoDiag'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ThemeVerifier")

print(f"Project root: {project_root}")
print(f"sys.path: {sys.path}")

try:
    from shared.themes.dacos_cyber_teal import DACOS_THEME, DACOS_STYLESHEET
    print("\n✅ Successfully imported DACOS_THEME")
    print("Theme Colors:")
    for k, v in DACOS_THEME.items():
        print(f"  {k}: {v}")
        
    print(f"\nStylesheet length: {len(DACOS_STYLESHEET)}")
    print(f"Stylesheet start: {DACOS_STYLESHEET[:100]}...")
    
except ImportError as e:
    print(f"\n❌ Failed to import DACOS_THEME: {e}")
    import traceback
    traceback.print_exc()

try:
    from shared.style_manager import style_manager
    print("\n✅ Successfully imported style_manager")
    print(f"Available themes: {style_manager.get_theme_names()}")
except ImportError as e:
    print(f"\n❌ Failed to import style_manager: {e}")

