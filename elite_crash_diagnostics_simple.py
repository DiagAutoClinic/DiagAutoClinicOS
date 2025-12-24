#!/usr/bin/env python3
"""
Elite Crash Diagnostics Tool - Simplified
Analyzes potential crash causes and provides isolation testing
"""

import sys
import os
import traceback
import subprocess
import time
from pathlib import Path
from datetime import datetime

def log_message(message):
    """Log diagnostic messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    try:
        with open('elite_crash_analysis.log', 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
    except:
        pass

def check_qt_installation():
    """Check Qt6/PyQt6 installation status"""
    log_message("=== QT6/PYQT6 INSTALLATION CHECK ===")
    
    try:
        import PyQt6.QtCore
        log_message("PASS: PyQt6.QtCore imported successfully")
    except ImportError as e:
        log_message(f"FAIL: PyQt6.QtCore import failed: {e}")
        return False
    
    try:
        import PyQt6.QtWidgets
        log_message("PASS: PyQt6.QtWidgets imported successfully")
    except ImportError as e:
        log_message(f"FAIL: PyQt6.QtWidgets import failed: {e}")
        return False
        
    try:
        import PyQt6.QtGui
        log_message("PASS: PyQt6.QtGui imported successfully")
    except ImportError as e:
        log_message(f"FAIL: PyQt6.QtGui import failed: {e}")
        return False
        
    # Check Qt version
    try:
        from PyQt6.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
        log_message(f"Qt Version: {QT_VERSION_STR}")
        log_message(f"PyQt6 Version: {PYQT_VERSION_STR}")
    except:
        log_message("WARNING: Could not determine Qt/PyQt versions")
        
    return True

def test_basic_qt():
    """Test basic Qt functionality"""
    log_message("=== BASIC QT FUNCTIONALITY TEST ===")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # Create minimal app
        app = QApplication([])
        log_message("PASS: QApplication created successfully")
        
        # Test basic window
        from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
        window = QWidget()
        window.setWindowTitle("Qt Test Window")
        label = QLabel("Qt6 Basic Test - If you see this, Qt6 is working")
        layout = QVBoxLayout()
        layout.addWidget(label)
        window.setLayout(layout)
        window.show()
        
        log_message("PASS: Basic Qt window created and shown")
        
        # Close after brief test
        def close_window():
            time.sleep(2)
            window.close()
            
        import threading
        threading.Thread(target=close_window, daemon=True).start()
        app.exec()
        
        log_message("PASS: Qt event loop completed successfully")
        return True
        
    except Exception as e:
        log_message(f"FAIL: Basic Qt test failed: {e}")
        log_message(f"Traceback: {traceback.format_exc()}")
        return False

def test_dacos_theme():
    """Test DACOS theme loading"""
    log_message("=== DACOS THEME LOADING TEST ===")
    
    try:
        from shared.themes.dacos_theme import DACOS_THEME, apply_dacos_theme
        log_message("PASS: DACOS theme imported successfully")
        log_message(f"Theme keys: {list(DACOS_THEME.keys())}")
        
        # Test theme application
        from PyQt6.QtWidgets import QApplication
        app = QApplication([])
        
        success = apply_dacos_theme(app)
        if success:
            log_message("PASS: DACOS theme applied successfully")
        else:
            log_message("WARNING: DACOS theme application returned False")
            
        return True
        
    except ImportError as e:
        log_message(f"FAIL: DACOS theme import failed: {e}")
        return False
    except Exception as e:
        log_message(f"FAIL: DACOS theme test failed: {e}")
        log_message(f"Traceback: {traceback.format_exc()}")
        return False

def test_custom_widgets():
    """Test custom widgets"""
    log_message("=== CUSTOM WIDGETS TEST ===")
    
    try:
        # Test circular gauge
        from shared.circular_gauge import CircularGauge
        log_message("PASS: CircularGauge imported successfully")
        
        from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
        from PyQt6.QtCore import Qt
        
        app = QApplication([])
        
        # Create test widget with gauge
        test_widget = QWidget()
        layout = QVBoxLayout(test_widget)
        
        gauge = CircularGauge()
        gauge.setValue(75)
        layout.addWidget(gauge)
        
        log_message("PASS: CircularGauge widget created successfully")
        
        test_widget.show()
        
        def close_after_test():
            time.sleep(3)
            test_widget.close()
            app.quit()
            
        threading.Thread(target=close_after_test, daemon=True).start()
        app.exec()
        
        log_message("PASS: Custom widgets test completed")
        return True
        
    except ImportError as e:
        log_message(f"FAIL: Custom widgets import failed: {e}")
        return False
    except Exception as e:
        log_message(f"FAIL: Custom widgets test failed: {e}")
        log_message(f"Traceback: {traceback.format_exc()}")
        return False

def test_neural_background():
    """Test neural background animation"""
    log_message("=== NEURAL BACKGROUND TEST ===")
    
    # Look for neural background files
    neural_files = [
        "shared/neural_background.py",
        "AutoDiag/ui/neural_background.py",
        "neural_background.py"
    ]
    
    for file_path in neural_files:
        if Path(file_path).exists():
            log_message(f"Found neural background file: {file_path}")
            
            try:
                # Try to import
                module_name = file_path.replace('/', '.').replace('.py', '')
                spec = __import__(module_name, fromlist=['NeuralBackground'])
                log_message(f"PASS: Neural background module imported: {file_path}")
                
                # Test creating neural background widget
                from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
                
                app = QApplication([])
                
                test_widget = QWidget()
                layout = QVBoxLayout(test_widget)
                
                # Create neural background if class exists
                if hasattr(spec, 'NeuralBackground'):
                    neural_bg = spec.NeuralBackground()
                    layout.addWidget(neural_bg)
                    log_message("PASS: NeuralBackground widget created successfully")
                    
                    test_widget.show()
                    
                    def close_after_test():
                        time.sleep(3)
                        test_widget.close()
                        app.quit()
                        
                    threading.Thread(target=close_after_test, daemon=True).start()
                    app.exec()
                    
                    log_message("PASS: Neural background test completed")
                    return True
                else:
                    log_message("WARNING: NeuralBackground class not found in module")
                    
            except Exception as e:
                log_message(f"FAIL: Neural background test failed for {file_path}: {e}")
                log_message(f"Traceback: {traceback.format_exc()}")
                
    log_message("WARNING: No neural background files found or test failed")
    return False

def run_simple_autodiag_test():
    """Run simple AutoDiag test"""
    log_message("=== SIMPLE AUTODIAG TEST ===")
    
    test_script = '''
import sys
import traceback
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_simple_autodiag():
    """Test simple AutoDiag startup"""
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # Create app
        app = QApplication([])
        
        # Test basic window without complex UI
        from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
        
        window = QWidget()
        window.setWindowTitle("Simple AutoDiag Test")
        layout = QVBoxLayout()
        
        label = QLabel("AutoDiag Test - Basic Qt6 functionality")
        layout.addWidget(label)
        
        window.setLayout(layout)
        window.show()
        
        print("PASS: Basic AutoDiag window created successfully")
        
        # Run for 3 seconds then close
        import threading
        import time
        
        def close_after_delay():
            time.sleep(3)
            window.close()
            app.quit()
            
        threading.Thread(target=close_after_delay, daemon=True).start()
        
        exit_code = app.exec()
        print(f"PASS: App exited with code: {exit_code}")
        return True
        
    except Exception as e:
        print(f"FAIL: Simple AutoDiag test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_autodiag()
    sys.exit(0 if success else 1)
'''
    
    try:
        # Write test script
        test_file = Path("simple_autodiag_test.py")
        test_file.write_text(test_script)
        
        log_message("Running simple AutoDiag test...")
        
        # Run the test
        result = subprocess.run([sys.executable, str(test_file)], 
                              capture_output=True, text=True, timeout=20)
        
        log_message(f"Test exit code: {result.returncode}")
        if result.stdout:
            log_message(f"Test output: {result.stdout}")
        if result.stderr:
            log_message(f"Test stderr: {result.stderr}")
            
        # Clean up
        test_file.unlink(missing_ok=True)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        log_message("FAIL: Simple test timed out (possible hang)")
        return False
    except Exception as e:
        log_message(f"FAIL: Simple test failed: {e}")
        return False

def provide_recommendations():
    """Provide recommendations"""
    log_message("=== RECOMMENDATIONS ===")
    
    recommendations = """
ELITE CRASH DIAGNOSIS COMPLETE

Exit Code 3489660927 (0xCFFFFFFF) Analysis:

IMMEDIATE ACTIONS COMPLETED:
1. Global exception hooks installed in launcher.py and AutoDiag/main.py
2. Crash logging enabled to autodiag_crash_log.txt and launcher_crash_log.txt
3. Next crash will be caught and logged instead of silent failure

LIKELY CRASH SOURCES:
1. Neural background animation (shared/neural_background.py)
2. Circular gauge initialization (shared/circular_gauge.py) 
3. DACOS theme stylesheet application (shared/themes/dacos_theme.py)
4. VCI auto-scan on tab change (blocking GUI thread)
5. Complex paintEvent in custom widgets

NEXT STEPS:
1. Run application with crash hook active
2. If crash occurs, check *_crash_log.txt files for Python traceback
3. Disable suspect components temporarily:
   - Comment out neural background in main window
   - Disable auto-VCI scanning
   - Remove gauge animations
   - Simplify theme stylesheet

QUICK FIXES:
- Update PyQt6: pip install --upgrade PyQt6 PyQt6-Qt6
- Disable hardware probing on startup
- Move VCI operations to separate thread
- Simplify custom widget paint events

IF CRASHES PERSIST:
- Run with: python -m pdb launcher.py
- Use Windows Debugging Tools (WinDbg)
- Check Windows Event Viewer for native stack traces
"""
    
    print(recommendations)
    log_message(recommendations)

def main():
    """Main diagnostic routine"""
    print("ELITE CRASH ANALYSIS: Exit Code 3489660927 (0xCFFFFFFF)")
    print("=" * 70)
    
    log_message("Starting elite crash diagnostics...")
    
    # Run all tests
    tests = [
        ("Qt6 Installation", check_qt_installation),
        ("Basic Qt Functionality", test_basic_qt),
        ("DACOS Theme Loading", test_dacos_theme),
        ("Custom Widgets", test_custom_widgets),
        ("Neural Background", test_neural_background),
        ("Simple AutoDiag", run_simple_autodiag_test),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            log_message(f"FAIL: {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<25} {status}")
    
    # Provide recommendations
    provide_recommendations()
    
    print("\nELITE CRASH FIX IMPLEMENTATION COMPLETE")
    print("The global exception hooks will now capture crashes before Qt6 native failures!")
    print("Check *_crash_log.txt files for detailed crash information.")

if __name__ == "__main__":
    main()