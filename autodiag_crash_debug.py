#!/usr/bin/env python3
"""
AutoDiag Pro Crash Debug Logger
Comprehensive logging to identify the exact crash point
"""

import logging
import sys
import traceback
import threading
import time
from datetime import datetime
from pathlib import Path

# Create comprehensive debug logging
def setup_crash_debug_logging():
    """Setup comprehensive crash debugging"""
    debug_log_path = Path('autodiag_crash_debug.log')
    
    # Create detailed formatter
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - '
        '[%(filename)s:%(lineno)d] - %(message)s'
    )
    
    # File handler with detailed logging
    file_handler = logging.FileHandler(debug_log_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(detailed_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return debug_log_path

class CrashDetector:
    """Advanced crash detection and logging"""
    
    def __init__(self):
        self.logger = logging.getLogger('CrashDetector')
        self.start_time = time.time()
        self.pulse_count = 0
        self.thread_count = 0
        self.active_threads = {}
        
    def log_application_start(self):
        """Log application startup with full context"""
        self.logger.info("=" * 80)
        self.logger.info("AUTODIAG PRO CRASH DETECTION STARTED")
        self.logger.info("=" * 80)
        self.logger.info(f"Start time: {datetime.now()}")
        self.logger.info(f"Python version: {sys.version}")
        self.logger.info(f"Platform: {sys.platform}")
        self.logger.info(f"Process ID: {os.getpid()}")
        
        # Log active threads
        self.log_active_threads("Startup")
        
    def log_active_threads(self, context=""):
        """Log currently active threads"""
        self.thread_count += 1
        current_threads = []
        
        for thread in threading.enumerate():
            thread_info = {
                'name': thread.name,
                'id': thread.ident,
                'is_alive': thread.is_alive(),
                'is_daemon': getattr(thread, 'daemon', False),
                'type': type(thread).__name__
            }
            current_threads.append(thread_info)
            
        self.logger.info(f"THREAD SCAN #{self.thread_count} - {context}")
        self.logger.info(f"Active threads count: {len(current_threads)}")
        
        for i, thread_info in enumerate(current_threads):
            self.logger.info(f"  Thread {i+1}: {thread_info}")
            
        self.active_threads[f"scan_{self.thread_count}"] = current_threads
        
    def log_watchdog_pulse(self, pulse_number):
        """Log each watchdog pulse with context"""
        self.pulse_count = pulse_number
        elapsed = time.time() - self.start_time
        
        self.logger.warning(f"🚨 WATCHDOG PULSE #{pulse_number} at {elapsed:.1f}s")
        
        # Log thread state on every pulse
        if pulse_number % 3 == 0:  # Every 3rd pulse
            self.log_active_threads(f"Watchdog Pulse #{pulse_number}")
            
        # Check for potential crash conditions
        if pulse_number >= 10:
            self.logger.error(f"⚠️  CRASH RISK: {pulse_count} pulses completed")
            
        if pulse_number >= 12:
            self.logger.critical(f"🚨 CRASH IMMINENT: {pulse_count} pulses - typical crash pattern detected!")
            
    def log_crash_detection(self, crash_type="Unknown"):
        """Log detected crash with full context"""
        elapsed = time.time() - self.start_time
        
        self.logger.critical("=" * 80)
        self.logger.critical("🚨 AUTODIAG PRO CRASH DETECTED!")
        self.logger.critical("=" * 80)
        self.logger.critical(f"Crash type: {crash_type}")
        self.logger.critical(f"Total runtime: {elapsed:.1f} seconds")
        self.logger.critical(f"Watchdog pulses: {self.pulse_count}")
        self.logger.critical(f"Thread scans: {self.thread_count}")
        
        # Log final thread state
        self.log_active_threads("Crash Detection")
        
        # Log stack trace if available
        try:
            raise Exception("Crash detection point")
        except Exception:
            stack_trace = traceback.format_exc()
            self.logger.critical(f"Stack trace:\n{stack_trace}")
            
    def log_safe_shutdown(self):
        """Log safe shutdown sequence"""
        self.logger.info("🔄 Initiating safe shutdown sequence...")
        self.log_active_threads("Safe Shutdown")
        
        # Log thread cleanup attempts
        for thread_info in self.active_threads.get('scan_1', []):
            if thread_info['is_daemon']:
                self.logger.info(f"  Daemon thread will be cleaned up: {thread_info['name']}")

# Global crash detector instance
crash_detector = None

def install_crash_detection():
    """Install comprehensive crash detection"""
    global crash_detector
    
    # Setup logging
    debug_log_path = setup_crash_debug_logging()
    
    # Create crash detector
    crash_detector = CrashDetector()
    crash_detector.log_application_start()
    
    # Install enhanced exception hook
    def enhanced_except_hook(exctype, value, tb):
        """Enhanced exception hook with crash detection"""
        crash_detector.log_crash_detection(f"Unhandled Exception: {exctype.__name__}")
        
        # Call original hook
        try:
            import os
            original_hook = getattr(enhanced_except_hook, '_original_hook', None)
            if original_hook:
                original_hook(exctype, value, tb)
        except:
            pass
            
        sys.exit(1)
    
    # Store original hook and install new one
    enhanced_except_hook._original_hook = sys.excepthook
    sys.excepthook = enhanced_except_hook
    
    return debug_log_path

def log_watchdog_pulse(pulse_number):
    """Log watchdog pulse with crash detection"""
    if crash_detector:
        crash_detector.log_watchdog_pulse(pulse_number)

def log_safe_shutdown():
    """Log safe shutdown sequence"""
    if crash_detector:
        crash_detector.log_safe_shutdown()

# Import os for process ID
import os

if __name__ == "__main__":
    print("AutoDiag Pro Crash Debug Logger installed")
    debug_log_path = install_crash_detection()
    print(f"Debug logging to: {debug_log_path}")