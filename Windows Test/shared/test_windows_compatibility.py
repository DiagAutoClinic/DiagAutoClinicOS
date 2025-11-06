#!/usr/bin/env python3
"""
Comprehensive Windows compatibility test suite for DiagAutoClinicOS
"""

import sys
import os
import platform
import importlib
import subprocess
from pathlib import Path

class WindowsCompatibilityTester:
    def __init__(self):
        self.results = {}
        self.windows_version = platform.version()
        
    def log_test(self, name, success, message=""):
        """Log test result"""
        status = "PASS" if success else "FAIL"
        self.results[name] = (status, message)
        print(f"{status}: {name} - {message}")
        
    def test_platform(self):
        """Test basic platform compatibility"""
        try:
            is_windows = platform.system() == "Windows"
            self.log_test("Windows Platform", is_windows, 
                         f"Running on Windows {self.windows_version}")
            return is_windows
        except Exception as e:
            self.log_test("Windows Platform", False, str(e))
            return False
    
    def test_python_version(self):
        """Test Python version compatibility"""
        try:
            version = sys.version_info
            compatible = version.major == 3 and version.minor >= 8
            self.log_test("Python Version", compatible,
                         f"Python {version.major}.{version.minor}.{version.micro}")
            return compatible
        except Exception as e:
            self.log_test("Python Version", False, str(e))
            return False
    
    def test_import_module(self, module_name, install_name=None):
        """Test if a module can be imported"""
        try:
            importlib.import_module(module_name)
            self.log_test(f"Import {module_name}", True, "Module imported successfully")
            return True
        except ImportError as e:
            install_cmd = install_name or module_name
            self.log_test(f"Import {module_name}", False, 
                         f"Failed to import: {e}. Try: pip install {install_cmd}")
            return False
        except Exception as e:
            self.log_test(f"Import {module_name}", False, f"Import error: {e}")
            return False
    
    def test_qt_components(self):
        """Test PyQt6 components"""
        qt_modules = [
            "PyQt6",
            "PyQt6.QtCore", 
            "PyQt6.QtGui",
            "PyQt6.QtWidgets",
            "PyQt6.QtSerialPort",
            "PyQt6.QtCharts"
        ]
        
        results = []
        for module in qt_modules:
            results.append(self.test_import_module(module))
        
        return all(results)
    
    def test_hardware_modules(self):
        """Test hardware communication modules"""
        hardware_modules = [
            ("serial", "pyserial"),
            ("can", "python-can"),
            ("cryptography", "cryptography"),
            ("usb", "pyusb"),
            ("bleak", "bleak"),
        ]
        
        results = []
        for module, install_name in hardware_modules:
            results.append(self.test_import_module(module, install_name))
        
        return all(results)
    
    def test_automotive_modules(self):
        """Test automotive-specific modules"""
        auto_modules = [
            ("obd", "obd"),
            ("isotp", "can-isotp"), 
            ("udsoncan", "udsoncan"),
        ]
        
        results = []
        for module, install_name in auto_modules:
            results.append(self.test_import_module(module, install_name))
        
        return all(results)
    
    def test_file_operations(self):
        """Test file system operations"""
        try:
            # Test Windows path operations
            test_dir = Path(os.environ.get('TEMP', '')) / 'diagautoclinic_test'
            test_dir.mkdir(exist_ok=True)
            
            # Test file creation with different path styles
            test_file = test_dir / "test_file.txt"
            test_file.write_text("Windows compatibility test")
            
            # Test path joins
            joined_path = os.path.join("C:", "ProgramData", "DiagAutoClinic", "config.ini")
            
            # Cleanup
            test_file.unlink()
            test_dir.rmdir()
            
            self.log_test("File Operations", True, "Windows file operations successful")
            return True
        except Exception as e:
            self.log_test("File Operations", False, f"File operation error: {e}")
            return False
    
    def test_serial_ports(self):
        """Test serial port enumeration"""
        try:
            import serial.tools.list_ports
            ports = list(serial.tools.list_ports.comports())
            port_names = [port.device for port in ports]
            self.log_test("Serial Port Detection", True, 
                         f"Found {len(ports)} ports: {', '.join(port_names)}")
            return True
        except Exception as e:
            self.log_test("Serial Port Detection", False, f"Serial port error: {e}")
            return False
    
    def test_can_backends(self):
        """Test CAN bus backends"""
        try:
            import can
            available_backends = can.detect_available_configs()
            backend_names = [backend['interface'] for backend in available_backends]
            self.log_test("CAN Backends", len(available_backends) > 0,
                         f"Available backends: {', '.join(backend_names)}")
            return len(available_backends) > 0
        except Exception as e:
            self.log_test("CAN Backends", False, f"CAN backend error: {e}")
            return False
    
    def test_privileges(self):
        """Test system privileges"""
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            self.log_test("Administrator Privileges", is_admin,
                         "Running as admin" if is_admin else "Not running as admin")
            return is_admin
        except Exception as e:
            self.log_test("Administrator Privileges", False, f"Privilege check error: {e}")
            return False
    
    def test_windows_api(self):
        """Test Windows API access"""
        try:
            import win32api
            import win32con
            current_dir = win32api.GetCurrentDirectory()
            self.log_test("Windows API", True, "Windows API accessible")
            return True
        except Exception as e:
            self.log_test("Windows API", False, f"Windows API error: {e}")
            return False
    
    def test_j2534_compatibility(self):
        """Test J2534 compatibility layer"""
        try:
            # Try to import J2534 module
            import j2534
            self.log_test("J2534 Support", True, "J2534 module loaded")
            return True
        except ImportError:
            self.log_test("J2534 Support", False, "J2534 module not available")
            return False
        except Exception as e:
            self.log_test("J2534 Support", False, f"J2534 error: {e}")
            return False
    
    def test_rfid_smartcard(self):
        """Test RFID and smart card support"""
        try:
            import smartcard
            from smartcard.System import readers
            reader_list = readers()
            self.log_test("Smart Card Support", True, 
                         f"Found {len(reader_list)} smart card readers")
            return True
        except ImportError:
            self.log_test("Smart Card Support", False, "pyscard not installed")
            return False
        except Exception as e:
            self.log_test("Smart Card Support", False, f"Smart card error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all compatibility tests"""
        print("DiagAutoClinicOS - Windows Compatibility Test")
        print("=" * 60)
        
        tests = [
            self.test_platform,
            self.test_python_version,
            self.test_qt_components,
            self.test_hardware_modules,
            self.test_automotive_modules,
            self.test_file_operations,
            self.test_serial_ports,
            self.test_can_backends,
            self.test_privileges,
            self.test_windows_api,
            self.test_j2534_compatibility,
            self.test_rfid_smartcard,
        ]
        
        for test in tests:
            test()
        
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("COMPATIBILITY TEST REPORT")
        print("=" * 60)
        
        passed = sum(1 for result in self.results.values() if result[0] == "PASS")
        total = len(self.results)
        
        print(f"Overall Score: {passed}/{total} ({passed/total*100:.1f}%)")
        
        print("\nDetailed Results:")
        for test_name, (status, message) in self.results.items():
            status_icon = "✓" if status == "PASS" else "✗"
            print(f"  {status_icon} {test_name}: {message}")
        
        # Recommendations
        print("\nRECOMMENDATIONS:")
        if "Import j2534" in str(self.results.get("J2534 Support", ("", ""))):
            print("• Install J2534 drivers for your interface device")
        
        if not self.results.get("Administrator Privileges", (False, ""))[0] == "PASS":
            print("• Run as Administrator for full hardware access")
        
        if not self.results.get("CAN Backends", (False, ""))[0] == "PASS":
            print("• Install CAN interface drivers (Vector, PEAK, Kvaser, etc.)")
        
        if not self.results.get("Smart Card Support", (False, ""))[0] == "PASS":
            print("• Ensure Smart Card Service is running and readers are connected")

def main():
    tester = WindowsCompatibilityTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
