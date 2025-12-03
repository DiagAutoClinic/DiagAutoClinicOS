# AutoDiag Tabs - Complete Usage Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Tab Structure Overview](#tab-structure-overview)
3. [Basic Tab Usage](#basic-tab-usage)
4. [Customizing Existing Tabs](#customizing-existing-tabs)
5. [Creating New Tabs](#creating-new-tabs)
6. [Copy-Paste Between Suites](#copy-paste-between-suites)
7. [Advanced Customization](#advanced-customization)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [Example: Complete Custom Tab](#example-complete-custom-tab)

## Introduction

This guide provides comprehensive instructions on how to use and customize the modular tab system in AutoDiag Pro. The tab separation allows for easy customization and reuse of tab components across different diagnostic suites.

## Tab Structure Overview

### File Location

All tab files are located in:
```
AutoDiag/ui/
AutoECU/ui/
AutoKey/ui/
```

### Available Tabs

| Suite | Tab File | Purpose | Key Features |
|-------|----------|---------|-------------|
| **AutoDiag** | `dashboard_tab.py` | Main dashboard with system overview | Stat cards, quick actions, live updates |
| **AutoDiag** | `diagnostics_tab.py` | Vehicle diagnostics interface | Full scan, DTC reading, clearing |
| **AutoDiag** | `live_data_tab.py` | Real-time data streaming | Parameter monitoring, start/stop controls |
| **AutoDiag** | `special_functions_tab.py` | Advanced vehicle functions | Function execution, parameter input |
| **AutoDiag** | `calibrations_tab.py` | Calibration procedures | Procedure execution, battery registration |
| **AutoDiag** | `advanced_tab.py` | Advanced diagnostic functions | Complex operations, detailed results |
| **AutoDiag** | `security_tab.py` | Security and access control | User information, session management |
| **AutoECU** | `dashboard_tab.py` | ECU programming dashboard | ECU health, programming status, modules |
| **AutoECU** | `ecu_scan_tab.py` | ECU scanning interface | Module identification, connection status |
| **AutoECU** | `programming_tab.py` | ECU programming functions | Memory operations, flash programming |
| **AutoECU** | `parameters_tab.py` | Parameter management | ECU parameter editing and saving |
| **AutoECU** | `diagnostics_tab.py` | ECU diagnostics | DTC reading, system health |
| **AutoECU** | `coding_tab.py` | ECU coding functions | Advanced coding operations |
| **AutoKey** | `dashboard_tab.py` | Key programming dashboard | System overview, quick actions |
| **AutoKey** | `key_programming_tab.py` | Key programming functions | Key learning, programming |
| **AutoKey** | `transponder_tab.py` | Transponder operations | Transponder programming, cloning |
| **AutoKey** | `security_tab.py` | Security functions | Access control, user management |
| **AutoKey** | `vehicle_info_tab.py` | Vehicle information | Vehicle data display and editing |

## Basic Tab Usage

### Accessing Tabs in Code

```python
# Import a specific tab class
from AutoDiag.ui.dashboard_tab import DashboardTab

# Create a tab instance (requires parent window reference)
dashboard_tab = DashboardTab(parent_window)

# Create the tab widget
tab_widget, tab_title = dashboard_tab.create_tab()

# Add to your tab widget
main_tab_widget.addTab(tab_widget, tab_title)
```

### Tab Class Structure

Each tab class follows this pattern:

```python
class YourTabName:
    def __init__(self, parent_window):
        """Initialize tab with parent window reference"""
        self.parent = parent_window
        # Initialize tab-specific components

    def create_tab(self):
        """Create and return the tab widget with title"""
        # Create UI components
        # Connect signals
        # Return (widget, title) tuple
        return tab_widget, "Tab Title"
```

## Customizing Existing Tabs

### Simple Modifications

1. **Locate the tab file** in `AutoDiag/ui/`, `AutoECU/ui/`, or `AutoKey/ui/`
2. **Open the file** in your preferred editor
3. **Make your changes** to the UI components or logic
4. **Save the file** - changes take effect immediately

### Example: Modifying Dashboard Tab

```python
# In AutoDiag/ui/dashboard_tab.py

def create_tab(self):
    # ... existing code ...

    # Modify the quick actions buttons
    btn1 = QPushButton("🚀 Quick Scan")  # Changed from original
    btn2 = QPushButton("🔍 Read DTCs")
    btn3 = QPushButton("📊 Live Data")
    btn4 = QPushButton("💻 ECU Info")

    # Add custom button
    btn5 = QPushButton("🔧 Custom Action")
    btn5.clicked.connect(self.custom_action)

    # ... rest of the method ...
```

### Adding Custom Methods

```python
class DashboardTab:
    def __init__(self, parent_window):
        self.parent = parent_window
        # Add custom attributes
        self.custom_data = None

    def custom_action(self):
        """Custom action for the dashboard"""
        self.parent.status_label.setText("🔧 Performing custom action...")
        # Your custom logic here
        self.parent.status_label.setText("✅ Custom action completed")

    # ... rest of the class ...
```

## Creating New Tabs

### Step-by-Step Guide

1. **Create a new file** in `AutoDiag/ui/`, `AutoECU/ui/`, or `AutoKey/ui/` (e.g., `custom_tab.py`)

2. **Define your tab class**:

```python
# AutoDiag/ui/custom_tab.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class CustomTab:
    def __init__(self, parent_window):
        self.parent = parent_window

    def create_tab(self):
        """Create your custom tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Add your custom UI components
        header = QLabel("🎯 Custom Tab")
        header.setProperty("class", "tab-title")
        layout.addWidget(header)

        content = QLabel("This is your custom tab content")
        layout.addWidget(content)

        return tab, "🎯 Custom"
```

3. **Import in main.py**:

```python
# In AutoDiag/main.py
from AutoDiag.ui.custom_tab import CustomTab
```

4. **Add to tab creation**:

```python
def create_tabs_using_separate_classes(self):
    # ... existing tab creation ...

    # Add your custom tab
    custom_tab = CustomTab(self)
    custom_widget, custom_title = custom_tab.create_tab()
    self.tab_widget.addTab(custom_widget, custom_title)

    # ... rest of the method ...
```

## Copy-Paste Between Suites

### Basic Copy-Paste Workflow

1. **Identify the tab** you want to copy from one suite to another
2. **Copy the entire file** from the source suite
3. **Paste into the target suite** in the appropriate `ui/` directory
4. **Update imports** if needed for the target suite
5. **Add to main.py** in the target suite

### Example: Copying Dashboard Tab to AutoECU

```bash
# Copy the file
cp AutoDiag/ui/dashboard_tab.py AutoECU/ui/dashboard_tab.py

# Update AutoECU/main.py to import and use the tab
```

### Cross-Suite Considerations

- **Method Names**: Ensure parent methods exist in the target suite
- **Imports**: Update any suite-specific imports
- **Dependencies**: Check for shared module dependencies
- **Theme Compatibility**: Verify theme classes are available

### Example: Copying Dashboard Tab from AutoDiag to AutoKey

```python
# Copy the file
cp AutoDiag/ui/dashboard_tab.py AutoKey/ui/dashboard_tab.py

# Update AutoKey/main.py
from AutoKey.ui.dashboard_tab import DashboardTab

# Add to tab creation
def create_tabs_using_separate_classes(self):
    dashboard_tab = DashboardTab(self)
    dashboard_widget, dashboard_title = dashboard_tab.create_tab()
    self.tab_widget.addTab(dashboard_widget, dashboard_title)
```

## Advanced Customization

### Dynamic Tab Loading

```python
def load_tabs_dynamically(self, tab_config):
    """Load tabs based on configuration"""
    for tab_name in tab_config:
        try:
            module = __import__(f'AutoDiag.ui.{tab_name}_tab', fromlist=[tab_name.capitalize() + 'Tab'])
            tab_class = getattr(module, tab_name.capitalize() + 'Tab')
            tab_instance = tab_class(self)
            widget, title = tab_instance.create_tab()
            self.tab_widget.addTab(widget, title)
        except ImportError as e:
            print(f"Could not load tab {tab_name}: {e}")
```

### Tab Configuration System

```python
# Create a tab configuration file
{
    "enabled_tabs": [
        "dashboard",
        "diagnostics",
        "live_data",
        "special_functions"
    ],
    "tab_order": [
        "dashboard",
        "diagnostics",
        "live_data",
        "special_functions",
        "calibrations",
        "advanced",
        "security"
    ],
    "custom_tabs": [
        {
            "name": "custom_analysis",
            "file": "custom_analysis_tab",
            "title": "🔬 Analysis"
        }
    ]
}
```

## Troubleshooting

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Tab not appearing | Check import statement in main.py |
| Missing methods | Ensure parent window has required methods |
| Import errors | Verify file exists in correct location |
| Theme issues | Check DACOS theme imports and application |
| Signal connection errors | Verify signal/slot compatibility |

### Debugging Tips

```python
# Add debug prints to tab creation
def create_tab(self):
    print(f"DEBUG: Creating {self.__class__.__name__} tab")
    try:
        # Your tab creation code
        print("DEBUG: Tab creation successful")
        return widget, title
    except Exception as e:
        print(f"DEBUG: Error creating tab: {e}")
        raise
```

## Best Practices

### Code Organization

- **Keep tabs focused**: Each tab should have a single responsibility
- **Use consistent naming**: Follow existing naming conventions
- **Document your tabs**: Add docstrings and comments
- **Handle errors gracefully**: Add proper error handling

### Performance Tips

- **Lazy loading**: Load heavy components only when needed
- **Memory management**: Clean up resources when tabs are closed
- **Efficient updates**: Use timers wisely for live data

### Collaboration Guidelines

- **Version control**: Use meaningful commit messages
- **Code reviews**: Review tab changes before merging
- **Documentation**: Update documentation when adding new tabs

## Example: Complete Custom Tab

```python
# AutoDiag/ui/vehicle_health_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
                          QPushButton, QProgressBar, QTextEdit)
from PyQt6.QtCore import Qt, QTimer

class VehicleHealthTab:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.health_timer = None
        self.health_progress = None

    def create_tab(self):
        """Create vehicle health monitoring tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("❤️ Vehicle Health Monitor")
        header.setProperty("class", "tab-title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Health status frame
        health_frame = QFrame()
        health_frame.setProperty("class", "glass-card")
        health_layout = QVBoxLayout(health_frame)

        # Health indicators
        self.health_progress = QProgressBar()
        self.health_progress.setRange(0, 100)
        self.health_progress.setValue(85)
        self.health_progress.setFormat("Overall Health: %p%")

        health_status = QLabel("Status: Good")
        health_status.setProperty("class", "section-title")

        health_layout.addWidget(self.health_progress)
        health_layout.addWidget(health_status)

        # Control buttons
        controls = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Refresh Health")
        refresh_btn.clicked.connect(self.refresh_health)

        diagnose_btn = QPushButton("🔍 Full Diagnosis")
        diagnose_btn.clicked.connect(self.run_full_diagnosis)

        controls.addWidget(refresh_btn)
        controls.addWidget(diagnose_btn)

        # Results area
        results_frame = QFrame()
        results_frame.setProperty("class", "glass-card")
        results_layout = QVBoxLayout(results_frame)

        results_title = QLabel("Health Details")
        results_title.setProperty("class", "section-title")

        self.health_results = QTextEdit()
        self.health_results.setReadOnly(True)
        self.health_results.setPlainText("Vehicle health information will appear here.")

        results_layout.addWidget(results_title)
        results_layout.addWidget(self.health_results)

        # Assemble everything
        layout.addWidget(health_frame)
        layout.addLayout(controls)
        layout.addWidget(results_frame)

        # Start health monitoring
        self.start_health_monitoring()

        return tab, "❤️ Health"

    def start_health_monitoring(self):
        """Start periodic health monitoring"""
        self.health_timer = QTimer()
        self.health_timer.timeout.connect(self.update_health_status)
        self.health_timer.start(5000)  # Update every 5 seconds

    def update_health_status(self):
        """Update health status with mock data"""
        import random
        new_health = random.randint(70, 95)
        self.health_progress.setValue(new_health)

        if new_health > 80:
            status = "Good"
            color = "success"
        elif new_health > 60:
            status = "Fair"
            color = "warning"
        else:
            status = "Poor"
            color = "danger"

        self.health_results.setPlainText(
            f"Vehicle Health Update\n\n"
            f"Overall Health: {new_health}%\n"
            f"Status: {status}\n"
            f"Recommendation: {'No action needed' if new_health > 80 else 'Check vehicle soon' if new_health > 60 else 'Immediate attention required'}"
        )

    def refresh_health(self):
        """Manually refresh health status"""
        self.update_health_status()
        self.parent.status_label.setText("❤️ Health refreshed")

    def run_full_diagnosis(self):
        """Run comprehensive vehicle diagnosis"""
        self.parent.status_label.setText("🔍 Running full diagnosis...")

        # Simulate diagnosis
        QTimer.singleShot(2000, lambda: [
            self.health_results.setPlainText(
                "Full Diagnosis Results\n\n"
                "✅ Engine: Good\n"
                "✅ Transmission: Good\n"
                "⚠️  Brakes: Fair (check soon)\n"
                "✅ Electrical: Good\n"
                "❌ Suspension: Poor (needs attention)\n"
            ),
            self.parent.status_label.setText("✅ Diagnosis complete")
        ])

```

## Conclusion

This guide provides everything you need to work with the modular tab system in AutoDiag Pro. Whether you're customizing existing tabs, creating new ones, or copying tabs between suites, the separated structure makes these operations straightforward and efficient.

For more advanced use cases or specific questions, refer to the main documentation or consult with the development team.