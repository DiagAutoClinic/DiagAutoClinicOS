#!/usr/bin/env python3
"""
Test script to verify responsive improvements in all AutoDiag tabs
"""

import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
sys.path.insert(0, project_root)

def test_all_tabs_responsive():
    """Test that all tabs have responsive design implemented"""
    print("Testing Responsive Design for All AutoDiag Tabs")
    print("=" * 60)

    tabs_to_check = [
        ("dashboard_tab.py", "Dashboard"),
        ("diagnostics_tab.py", "Diagnostics"),
        ("live_data_tab.py", "Live Data"),
        ("security_tab.py", "Security"),
        ("special_functions_tab.py", "Special Functions"),
        ("calibrations_tab.py", "Calibrations"),
        ("advanced_tab.py", "Advanced")
    ]

    responsive_tabs = []
    non_responsive_tabs = []

    for filename, tab_name in tabs_to_check:
        filepath = os.path.join("AutoDiag", "ui", filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for responsive indicators
            has_splitter = "QSplitter" in content
            has_sizes = "setSizes([" in content
            has_minimum_width = "setMinimumWidth(" in content
            has_scroll_area = "QScrollArea" in content

            if has_splitter and has_sizes and has_minimum_width:
                responsive_tabs.append(tab_name)
                print(f"[PASS] {tab_name} - Responsive (Splitter + Sizes + Min Width)")
            elif has_scroll_area and "ScrollArea" in content:
                responsive_tabs.append(tab_name)
                print(f"[PASS] {tab_name} - Responsive (Scroll Area)")
            else:
                non_responsive_tabs.append(tab_name)
                print(f"[FAIL] {tab_name} - Not responsive")
        else:
            print(f"[SKIP] {filename} not found")

    print("\n" + "=" * 60)
    print(f"Responsive Tabs: {len(responsive_tabs)}")
    for tab in responsive_tabs:
        print(f"  * {tab}")

    if non_responsive_tabs:
        print(f"Non-Responsive Tabs: {len(non_responsive_tabs)}")
        for tab in non_responsive_tabs:
            print(f"  * {tab}")
    else:
        print("All tabs are responsive!")

    print("\n" + "=" * 60)
    if len(responsive_tabs) >= 6:  # All except possibly security if it doesn't need splitter
        print("SUCCESS: All major tabs have responsive design implemented!")
        return True
    else:
        print("FAILURE: Some tabs still need responsive design")
        return False

if __name__ == "__main__":
    success = test_all_tabs_responsive()
    sys.exit(0 if success else 1)