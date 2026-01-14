
import sys
import os

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
sys.path.insert(0, project_root)

print(f"Checking theme in: {project_root}")

try:
    from shared.themes import dacos_cyber_teal
    print(f"Imported dacos_cyber_teal from: {dacos_cyber_teal.__file__}")
    print(f"Background Color: {dacos_cyber_teal.DACOS_THEME.get('bg_main')}")
    
    if dacos_cyber_teal.DACOS_THEME.get('bg_main') == "#000000":
        print("✅ SUCCESS: Cyber-Teal Theme detected!")
    else:
        print(f"❌ FAIL: Old theme detected. Value: {dacos_cyber_teal.DACOS_THEME.get('bg_main')}")

except ImportError as e:
    print(f"❌ ImportError: {e}")
    import traceback
    traceback.print_exc()
