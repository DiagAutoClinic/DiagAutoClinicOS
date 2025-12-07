#!/usr/bin/env python3
"""
Test script to verify responsive CAN bus tab layout
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QFrame, QSplitter
from PyQt6.QtCore import Qt, QSize
from AutoDiag.ui.can_bus_tab import CANBusDataTab

def test_responsive_layout():
    """Test the responsive layout of CAN bus tab"""
    print("Testing CAN Bus Tab Responsive Layout...")

    # Create application
    app = QApplication(sys.argv)

    # Create test window
    window = QMainWindow()
    window.setWindowTitle("CAN Bus Responsive Test")
    window.resize(1366, 768)

    # Create tab widget
    tab_widget = QTabWidget()
    window.setCentralWidget(tab_widget)

    # Create CAN bus tab
    can_bus_tab = CANBusDataTab(window)
    can_bus_widget, can_bus_title = can_bus_tab.create_tab()
    tab_widget.addTab(can_bus_widget, can_bus_title)

    # Test different screen sizes
    test_sizes = [
        (800, 600, "Compact"),
        (1024, 768, "Standard"),
        (1366, 768, "HD"),
        (1920, 1080, "Full HD")
    ]

    for width, height, name in test_sizes:
        print(f"\nTesting {name} ({width}x{height})...")

        # Resize window
        window.resize(width, height)

        # Test layout responsiveness
        can_bus_widget.updateGeometry()
        can_bus_widget.adjustSize()

        # Check if widgets are properly sized
        children = can_bus_widget.findChildren(QFrame)
        for child in children:
            if child.property("class") == "glass-card":
                size = child.size()
                print(f"  Glass card: {size.width()}x{size.height()}")

        # Check splitter behavior
        splitters = can_bus_widget.findChildren(QSplitter)
        for splitter in splitters:
            sizes = splitter.sizes()
            print(f"  Splitter sizes: {sizes}")

    print("\nResponsive layout test completed!")
    print("Summary of improvements:")
    print("  • Vertical layouts for better responsiveness")
    print("  • Expanding size policies on key widgets")
    print("  • Scroll areas for overflow content")
    print("  • Screen-width based splitter sizing")
    print("  • Word wrapping on labels")
    print("  • Flexible button layouts")

    # Clean up
    window.close()
    app.quit()

if __name__ == "__main__":
    test_responsive_layout()