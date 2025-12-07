#!/usr/bin/env python3
"""
Test script to validate COM2 connection fix for GoDiag GD101
Comprehensive validation of the connection fix solution
"""

import logging
import sys
import os
import time
import subprocess
from typing import Optional, List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_com2_connection_fix():
    """Test the COM2 connection fix solution"""
    logger.info("Starting COM2 connection fix validation test")

    try:
        # Test 1: Import the fix module
        logger.info("Test 1: Importing COM2 connection fix module...")
        try:
            from com2_connection_fix import COM2ConnectionFix, ConnectionStatus
            logger.info("✅ SUCCESS: COM2 connection fix module imported successfully")
        except ImportError as e:
            logger.error(f"❌ FAILED: Could not import COM2 connection fix module: {e}")
            return False

        # Test 2: Create fix instance
        logger.info("\nTest 2: Creating COM2 connection fix instance...")
        try:
            fixer = COM2ConnectionFix()
            logger.info("✅ SUCCESS: COM2 connection fix instance created")
        except Exception as e:
            logger.error(f"❌ FAILED: Could not create COM2 connection fix instance: {e}")
            return False

        # Test 3: Run comprehensive fix routine
        logger.info("\nTest 3: Running comprehensive COM2 fix routine...")
        try:
            fix_success = fixer.comprehensive_fix_routine()
            if fix_success:
                logger.info("✅ SUCCESS: COM2 fix routine completed successfully")
            else:
                logger.error("❌ FAILED: COM2 fix routine failed")
                return False
        except Exception as e:
            logger.error(f"❌ FAILED: COM2 fix routine error: {e}")
            return False

        # Test 4: Check connection status
        logger.info("\nTest 4: Checking connection status...")
        if fixer.connection_status == ConnectionStatus.CONNECTED:
            logger.info("✅ SUCCESS: COM2 connection established")
        else:
            logger.error(f"❌ FAILED: Connection status is {fixer.connection_status.name}")
            return False

        # Test 5: Test connection quality
        logger.info("\nTest 5: Testing connection quality...")
        quality = fixer.test_connection_quality()
        if quality >= 80:
            logger.info(f"✅ SUCCESS: Connection quality is {quality}%")
        else:
            logger.warning(f"⚠️  Connection quality is {quality}% - may need improvement")

        # Test 6: Generate fix report
        logger.info("\nTest 6: Generating fix report...")
        try:
            report = fixer.generate_fix_report()
            logger.info("✅ SUCCESS: Fix report generated successfully")
        except Exception as e:
            logger.error(f"❌ FAILED: Could not generate fix report: {e}")
            return False

        return True

    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_system_commands():
    """Test system-level commands for COM2 troubleshooting"""
    logger.info("\n" + "="*60)
    logger.info("SYSTEM-LEVEL COM2 TROUBLESHOOTING")
    logger.info("="*60)

    commands = [
        ("Check COM2 port status", "mode COM2"),
        ("List serial ports", "wmic path Win32_SerialPort get DeviceID,Name,Status"),
        ("Check port configuration", "mode COM2 BAUD=115200 PARITY=N DATA=8 STOP=1")
    ]

    for description, command in commands:
        logger.info(f"\n{description}: {command}")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            logger.info(f"Exit code: {result.returncode}")
            if result.stdout:
                logger.info(f"Output: {result.stdout.strip()}")
            if result.stderr:
                logger.error(f"Error: {result.stderr.strip()}")
        except Exception as e:
            logger.error(f"❌ Command failed: {e}")

def main():
    """Main test function"""
    logger.info("="*60)
    logger.info("COM2 CONNECTION FIX VALIDATION TEST")
    logger.info("="*60)

    # Test the connection fix
    test_success = test_com2_connection_fix()

    # Run system-level tests
    test_system_commands()

    # Final summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)

    if test_success:
        logger.info("✅ COM2 Connection Fix Test: PASSED")
        logger.info("COM2 connection fix is working correctly")
    else:
        logger.error("❌ COM2 Connection Fix Test: FAILED")
        logger.error("COM2 connection fix requires additional troubleshooting")

    logger.info("="*60)

    return test_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)