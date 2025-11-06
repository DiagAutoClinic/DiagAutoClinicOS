# config/windows_config.py
import platform

if platform.system() == "Windows":
    CAN_BACKEND = 'vector'  # or 'socketcan', 'pcan', etc.
    SERIAL_TIMEOUT = 2.0
else:
    CAN_BACKEND = 'socketcan'
    SERIAL_TIMEOUT = 1.0

# Replace any hardcoded Unix paths
# config_dir = os.path.join(os.environ.get('APPDATA', ''), 'DiagAutoClinic')
# Remove the "#" and add the line above
