"""
Windows compatibility layer for DiagAutoClinicOS
"""

import os
import sys
import platform
from pathlib import Path

class WindowsCompatibility:
    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.setup_compatibility()
    
    def setup_compatibility(self):
        """Setup Windows-specific configurations"""
        if not self.is_windows:
            return
        
        # Add current directory to DLL search path
        if hasattr(os, 'add_dll_directory'):
            try:
                os.add_dll_directory(os.getcwd())
            except Exception:
                pass
        
        # Set up Windows-specific environment
        self.setup_windows_environment()
    
    def setup_windows_environment(self):
        """Configure Windows-specific environment settings"""
        # AppData directory for configuration
        self.appdata_dir = Path(os.environ.get('APPDATA', '')) / 'DiagAutoClinicOS'
        self.appdata_dir.mkdir(exist_ok=True)
        
        # ProgramData directory for shared data
        self.programdata_dir = Path(os.environ.get('ProgramData', '')) / 'DiagAutoClinicOS'
        self.programdata_dir.mkdir(exist_ok=True)
        
        # Temp directory
        self.temp_dir = Path(os.environ.get('TEMP', '')) / 'DiagAutoClinicOS'
        self.temp_dir.mkdir(exist_ok=True)
    
    def get_config_path(self, filename):
        """Get platform-appropriate config file path"""
        if self.is_windows:
            return self.appdata_dir / filename
        else:
            return Path.home() / '.config' / 'DiagAutoClinicOS' / filename
    
    def get_data_path(self, filename):
        """Get platform-appropriate data file path"""
        if self.is_windows:
            return self.programdata_dir / filename
        else:
            return Path('/var/lib') / 'DiagAutoClinicOS' / filename
    
    def get_temp_path(self, filename):
        """Get platform-appropriate temp file path"""
        if self.is_windows:
            return self.temp_dir / filename
        else:
            return Path('/tmp') / 'DiagAutoClinicOS' / filename
    
    def is_admin(self):
        """Check if running with administrator privileges"""
        if not self.is_windows:
            return os.geteuid() == 0  # Unix root check
        
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def setup_can_backend(self):
        """Configure appropriate CAN backend for Windows"""
        if not self.is_windows:
            return 'socketcan'
        
        # Try different Windows CAN backends in order of preference
        backends = ['vector', 'ixxat', 'neovi', 'pcan', 'socketcan']
        
        for backend in backends:
            try:
                import can
                bus = can.Bus(channel='0', interface=backend, receive_own_messages=False)
                bus.shutdown()
                return backend
            except:
                continue
        
        return 'vector'  # Default fallback
    
    def get_serial_ports(self):
        """Get available serial ports with Windows-specific handling"""
        try:
            import serial.tools.list_ports
            ports = list(serial.tools.list_ports.comports())
            
            if self.is_windows:
                # Windows-specific port filtering and ordering
                return [port.device for port in ports 
                       if 'COM' in port.device or 'LPT' in port.device]
            else:
                return [port.device for port in ports]
                
        except ImportError:
            return []
    
    def check_drivers(self):
        """Check for required Windows drivers"""
        if not self.is_windows:
            return {}
        
        driver_status = {}
        
        # Check for common automotive interface drivers
        drivers_to_check = [
            ('J2534', 'C:\\Windows\\System32\\J2534.dll'),
            ('FTDI', 'C:\\Windows\\System32\\ftd2xx.dll'),
            ('Vector', 'C:\\Windows\\System32\\vxlapi.dll'),
        ]
        
        for driver_name, driver_path in drivers_to_check:
            driver_status[driver_name] = os.path.exists(driver_path)
        
        return driver_status

# Global instance
win_compat = WindowsCompatibility()

# Convenience functions
def is_windows():
    return win_compat.is_windows

def get_config_path(filename):
    return win_compat.get_config_path(filename)

def get_data_path(filename):
    return win_compat.get_data_path(filename)

def is_admin():
    return win_compat.is_admin()

def setup_can_backend():
    return win_compat.setup_can_backend()
