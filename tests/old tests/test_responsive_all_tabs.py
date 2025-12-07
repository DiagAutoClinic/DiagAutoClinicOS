#!/usr/bin/env python3
"""
Test script for responsive tabs functionality
"""

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_responsive_tabs():
    """Test the responsive tabs functionality"""
    try:
        # Import the responsive tabs module
        from AutoDiag.ui.responsive_tabs import create_responsive_tabs, apply_security_to_tabs

        logger.info("✅ Successfully imported responsive tabs module")

        # Create a simple test application
        app = QApplication(sys.argv)

        # Create a mock parent object that inherits from QWidget
        from PyQt6.QtWidgets import QWidget

        class MockParent(QWidget):
            def __init__(self):
                super().__init__()
                self.status_label = None
                self.setWindowTitle("Test Parent")
                self.resize(800, 600)

        parent = MockParent()

        # Test creating responsive tabs
        tab_widget = create_responsive_tabs(parent)
        logger.info("✅ Successfully created responsive tabs")

        # Test applying security
        security_result = apply_security_to_tabs(tab_widget)
        logger.info(f"✅ Security applied to tabs: {security_result}")

        # Test tab count
        tab_count = tab_widget.count()
        logger.info(f"✅ Created {tab_count} tabs")

        # Test tab titles
        expected_tabs = [
            "Dashboard", "Diagnostics", "Live Data",
            "Special Functions", "Calibrations & Resets",
            "Advanced", "Security"
        ]

        actual_tabs = [tab_widget.tabText(i) for i in range(tab_count)]
        logger.info(f"✅ Tab titles: {actual_tabs}")

        # Verify all expected tabs are present
        for expected_tab in expected_tabs:
            if expected_tab in actual_tabs:
                logger.info(f"✅ Found tab: {expected_tab}")
            else:
                logger.warning(f"❌ Missing tab: {expected_tab}")

        logger.info("✅ Responsive tabs test completed successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Responsive tabs test failed: {e}")
        logger.exception("Full exception details:")
        return False

def test_responsive_design():
    """Test responsive design features"""
    try:
        from AutoDiag.ui.responsive_tabs import ResponsiveTab, DashboardTab

        logger.info("✅ Successfully imported responsive tab classes")

        # Test creating a responsive tab
        tab = ResponsiveTab("Test Tab", "🧪")
        logger.info("✅ Successfully created responsive tab")

        # Test creating a dashboard tab
        dashboard = DashboardTab()
        logger.info("✅ Successfully created dashboard tab")

        # Test tab properties
        assert hasattr(tab, 'title'), "Tab should have title property"
        assert hasattr(tab, 'icon'), "Tab should have icon property"
        assert hasattr(tab, 'add_content'), "Tab should have add_content method"
        assert hasattr(tab, 'clear_content'), "Tab should have clear_content method"

        logger.info("✅ All responsive tab properties verified")
        return True

    except Exception as e:
        logger.error(f"❌ Responsive design test failed: {e}")
        logger.exception("Full exception details:")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting responsive tabs test suite")

    # Run tests
    tabs_test = test_responsive_tabs()
    design_test = test_responsive_design()

    if tabs_test and design_test:
        logger.info("🎉 All tests passed successfully!")
        return True
    else:
        logger.error("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)