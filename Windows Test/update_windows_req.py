# In your install script, add platform detection for Windows
import platform

def install_windows_specific():
    if platform.system() == "Windows":
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "python-can[windows]",
            "pywin32"  # Windows API support
        ])
