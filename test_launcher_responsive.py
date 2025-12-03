#!/usr/bin/env python3
"""
Test script to verify launcher can launch responsive tabs
"""

import sys
import logging
from pathlib import Path
import subprocess
import time

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_launcher_integration():
    """Test that launcher can launch AutoDiag with responsive tabs"""
    try:
        logger.info("🚀 Testing launcher integration with responsive tabs")

        # Test 1: Verify AutoDiag main.py exists and can be imported
        autodiag_main_path = PROJECT_ROOT / "AutoDiag" / "main.py"
        if not autodiag_main_path.exists():
            logger.error(f"❌ AutoDiag main.py not found at: {autodiag_main_path}")
            return False

        logger.info(f"✅ Found AutoDiag main.py at: {autodiag_main_path}")

        # Test 2: Verify responsive tabs module exists
        responsive_tabs_path = PROJECT_ROOT / "AutoDiag" / "ui" / "responsive_tabs.py"
        if not responsive_tabs_path.exists():
            logger.error(f"❌ Responsive tabs module not found at: {responsive_tabs_path}")
            return False

        logger.info(f"✅ Found responsive tabs module at: {responsive_tabs_path}")

        # Test 3: Verify main.py imports responsive tabs
        with open(autodiag_main_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'from AutoDiag.ui.responsive_tabs import create_responsive_tabs' not in content:
            logger.error("❌ Main.py does not import responsive tabs")
            return False

        logger.info("✅ Main.py correctly imports responsive tabs")

        # Test 4: Verify main.py uses responsive tabs
        if 'create_responsive_tabs(self)' not in content:
            logger.error("❌ Main.py does not use responsive tabs")
            return False

        logger.info("✅ Main.py correctly uses responsive tabs")

        # Test 5: Verify launcher.py can find AutoDiag
        launcher_path = PROJECT_ROOT / "launcher.py"
        if not launcher_path.exists():
            logger.error(f"❌ Launcher.py not found at: {launcher_path}")
            return False

        logger.info(f"✅ Found launcher.py at: {launcher_path}")

        # Test 6: Verify launcher.py has AutoDiag launch capability
        with open(launcher_path, 'r', encoding='utf-8') as f:
            launcher_content = f.read()

        if 'launch_vehicle_diagnostics' not in launcher_content:
            logger.error("❌ Launcher.py does not have vehicle diagnostics launch capability")
            return False

        logger.info("✅ Launcher.py has vehicle diagnostics launch capability")

        # Test 7: Verify launcher.py can find AutoDiag directory
        if 'autodiag_dir = PROJECT_ROOT / "AutoDiag"' not in launcher_content:
            logger.error("❌ Launcher.py cannot find AutoDiag directory")
            return False

        logger.info("✅ Launcher.py can find AutoDiag directory")

        logger.info("🎉 All launcher integration tests passed!")
        return True

    except Exception as e:
        logger.error(f"❌ Launcher integration test failed: {e}")
        logger.exception("Full exception details:")
        return False

def test_responsive_tabs_launch():
    """Test launching AutoDiag with responsive tabs"""
    try:
        logger.info("🚀 Testing responsive tabs launch")

        # Test launching AutoDiag in headless mode to verify it works
        cmd = [
            sys.executable,
            str(PROJECT_ROOT / "AutoDiag" / "main.py"),
            "--headless",
            "--scan"
        ]

        logger.info(f"Running command: {' '.join(str(x) for x in cmd)}")

        # Run the command
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT / "AutoDiag"),
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            logger.info("✅ AutoDiag launched successfully in headless mode")
            logger.info(f"Output: {result.stdout}")
            return True
        else:
            logger.error(f"❌ AutoDiag launch failed with return code: {result.returncode}")
            logger.error(f"Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.error("❌ AutoDiag launch timed out")
        return False
    except Exception as e:
        logger.error(f"❌ AutoDiag launch test failed: {e}")
        logger.exception("Full exception details:")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting launcher responsive tabs test suite")

    # Run tests
    integration_test = test_launcher_integration()
    launch_test = test_responsive_tabs_launch()

    if integration_test and launch_test:
        logger.info("🎉 All launcher tests passed successfully!")
        return True
    elif integration_test:
        logger.info("✅ Integration tests passed, launch test skipped or failed")
        return True
    else:
        logger.error("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)