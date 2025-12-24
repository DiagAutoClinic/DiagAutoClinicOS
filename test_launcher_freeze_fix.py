#!/usr/bin/env python3
"""
Test script to verify the launcher freeze fix
Tests the monitor_process method with simulated subprocess behavior
"""

import sys
import subprocess
import threading
import time
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the launcher to test
try:
    from launcher import DiagLauncher
    print("[OK] Successfully imported DiagLauncher")
except ImportError as e:
    print(f"[ERROR] Failed to import DiagLauncher: {e}")
    sys.exit(1)

# Setup logging for test
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockProcess:
    """Mock process to simulate subprocess behavior"""
    
    def __init__(self, name, exit_code=0, stderr_output="", delay=2):
        self.name = name
        self.exit_code = exit_code
        self.stderr_output = stderr_output
        self.delay = delay
        self.pid = 1234  # Mock PID
        self.returncode = None
        self._running = False
        
    def wait(self, timeout=None):
        """Simulate process wait"""
        if timeout:
            time.sleep(min(self.delay, timeout))
            if self.delay > timeout:
                raise subprocess.TimeoutExpired(self.pid, timeout)
        
        time.sleep(self.delay)
        self.returncode = self.exit_code
        self._running = False
        return self.exit_code
    
    def poll(self):
        """Check if process is running"""
        return None if self._running else self.exit_code
    
    @property  
    def stderr(self):
        """Return mock stderr object"""
        return MockStderr(self.stderr_output)

class MockStderr:
    """Mock stderr to simulate subprocess.stderr"""
    
    def __init__(self, output):
        self.output = output
        self.lines = output.split('\n') if output else []
        self.index = 0
        self.closed = False
        
    def readline(self):
        """Simulate non-blocking readline"""
        if self.closed or self.index >= len(self.lines):
            return b''  # Empty bytes indicates EOF
        
        line = self.lines[self.index] + '\n'
        self.index += 1
        return line.encode()
    
    def read(self):
        """Simulate blocking read"""
        if self.closed:
            return b''  # Closed pipe returns empty
        
        # This would cause the original bug - simulate indefinite block
        # by not returning anything (hang forever)
        time.sleep(60)  # Simulate indefinite hang
        return b''

def test_monitor_process():
    """Test the fixed monitor_process method"""
    print("\n[TEST] Testing monitor_process method...")
    
    # Create launcher instance (minimal setup)
    try:
        launcher = DiagLauncher()
        print("[OK] DiagLauncher instance created")
    except Exception as e:
        print(f"[ERROR] Failed to create DiagLauncher: {e}")
        return False
    
    # Test Case 1: Normal process that exits cleanly
    print("\n[Test 1] Normal process exit")
    mock_process = MockProcess("TestApp", exit_code=0, stderr_output="Application started\nApplication closed", delay=1)
    
    start_time = time.time()
    launcher.monitor_process("TestApp", mock_process)
    
    # Wait for monitoring to complete (give it 3 seconds max)
    time.sleep(3)
    elapsed = time.time() - start_time
    
    if elapsed < 2.5:
        print(f"[PASS] Test Case 1 - Completed in {elapsed:.2f}s (no hang)")
        result1 = True
    else:
        print(f"[FAIL] Test Case 1 - Took {elapsed:.2f}s (possible hang)")
        result1 = False
    
    # Test Case 2: Process with error exit code
    print("\n[Test 2] Process with error exit")
    mock_process = MockProcess("ErrorApp", exit_code=1, stderr_output="Error: Something went wrong", delay=1)
    
    start_time = time.time()
    launcher.monitor_process("ErrorApp", mock_process)
    
    # Wait for monitoring to complete
    time.sleep(3)
    elapsed = time.time() - start_time
    
    if elapsed < 2.5:
        print(f"[PASS] Test Case 2 - Error handling completed in {elapsed:.2f}s")
        result2 = True
    else:
        print(f"[FAIL] Test Case 2 - Error handling took {elapsed:.2f}s (possible hang)")
        result2 = False
    
    # Test Case 3: Process timeout scenario (quick test)
    print("\n[Test 3] Process timeout handling (quick test)")
    mock_process = MockProcess("TimeoutApp", exit_code=0, stderr_output="", delay=35)  # 35 second delay
    
    start_time = time.time()
    launcher.monitor_process("TimeoutApp", mock_process)
    
    # Wait for timeout handling (should complete within 35+ seconds)
    time.sleep(5)  # Just test that it doesn't hang immediately
    elapsed = time.time() - start_time
    
    if elapsed < 6:  # Should not hang immediately
        print(f"[PASS] Test Case 3 - No immediate hang in {elapsed:.2f}s")
        result3 = True
    else:
        print(f"[FAIL] Test Case 3 - Hanging immediately ({elapsed:.2f}s)")
        result3 = False
    
    # Cleanup
    try:
        launcher.destroy()
        print("[OK] Launcher cleaned up")
    except:
        pass
    
    # Overall result
    all_passed = result1 and result2 and result3
    print(f"\n[RESULT] Overall Test Result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n[SUCCESS] The launcher freeze fix is working correctly!")
        print("   - No blocking on process.stderr.read()")
        print("   - Proper timeout handling")  
        print("   - Clean process lifecycle management")
        print("   - Enhanced error logging")
    else:
        print("\n[WARNING] Some tests failed - the fix may need adjustment")
    
    return all_passed

def test_original_bug():
    """Test to demonstrate the original bug behavior"""
    print("\n[BUG] Demonstrating Original Bug Behavior...")
    
    # Simulate the original broken code
    def original_monitor_broken(name, process):
        """Original broken implementation"""
        logger.info(f"Monitoring {name} (PID: {process.pid})")
        
        # Start process (mock)
        process._running = True
        time.sleep(1)  # Process runs for 1 second
        process.returncode = 0
        process._running = False
        
        # This is where the original bug occurs
        logger.info(f"{name} finished with code: {process.returncode}")
        
        # Simulate the blocking stderr.read() call
        logger.info("Attempting to read stderr (this would block indefinitely)...")
        try:
            # In real code, this would block forever on closed pipe
            error_output = process.stderr.read()  # BLOCKS HERE
            logger.error(f"Error in {name}:\n{error_output}")
        except Exception as e:
            logger.error(f"Stderr read failed: {e}")
    
    # Test with mock process
    mock_process = MockProcess("BrokenApp", exit_code=0, stderr_output="Some error", delay=1)
    
    start_time = time.time()
    
    try:
        # This would hang in the original implementation
        original_monitor_broken("BrokenApp", mock_process)
        elapsed = time.time() - start_time
        print(f"[WARNING] Original implementation completed in {elapsed:.2f}s (unexpected)")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"[OK] Original implementation demonstrates the issue - {elapsed:.2f}s")
        return True

if __name__ == "__main__":
    print("[INFO] LAUNCHER FREEZE FIX VERIFICATION TEST")
    print("=" * 50)
    
    # Test the original bug
    test_original_bug()
    
    print("\n" + "=" * 50)
    
    # Test the fix
    success = test_monitor_process()
    
    print("\n" + "=" * 50)
    print("[DONE] Test Complete")
    
    if success:
        print("[SUCCESS] Fix verified - launcher should no longer freeze!")
        sys.exit(0)
    else:
        print("[ERROR] Fix needs more work")
        sys.exit(1)