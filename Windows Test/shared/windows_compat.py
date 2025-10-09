# shared/windows_compat.py
import platform
import sys

def is_windows():
    return platform.system() == "Windows"

def setup_windows_paths():
    if is_windows():
        # Add Windows-specific DLL paths if needed
        if hasattr(sys, 'frozen'):
            # Running as compiled executable
            os.environ['PATH'] = sys._MEIPASS + ';' + os.environ['PATH']
