#!/usr/bin/env python3
"""
AutoDiag Pro - Advanced Tab
Separate tab implementation with consistent layout
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
                            QScrollArea, QListWidget, QListWidgetItem, QTextEdit)
from PyQt6.QtCore import Qt
from datetime import datetime

class AdvancedTab:
    """
    Enhanced Advanced Tab with consistent layout and comprehensive functionality.
    
    This tab provides access to advanced diagnostic functions with detailed
    information and execution capabilities.
    """
    
    def __init__(self, parent_window):
        """
        Initialize the Advanced Tab.
        
        Args:
            parent_window: The main application window instance
        """
        self.parent = parent_window
        self.advanced_status_label = None
        self.advanced_functions_list = None
        self.advanced_function_details = None
        self.advanced_results_text = None
        self.execute_advanced_btn = None
        self.refresh_advanced_btn = None

    def create_tab(self) -> tuple[QWidget, str]:
        """
        Create the advanced tab and return the widget.
        
        Returns:
            tuple: (tab_widget, tab_title)
        """
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("🚀 Advanced Functions")
        header.setProperty("class", "tab-title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)

        # Main content area - Create a scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(10, 10, 10, 10)

        # System status display
        self.advanced_status_label = QLabel("Advanced diagnostics system ready - Select a function to begin")
        self.advanced_status_label.setProperty("class", "section-title")
        self.advanced_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.advanced_status_label.setWordWrap(True)
        content_layout.addWidget(self.advanced_status_label)

        # Functions list frame
        functions_frame = QFrame()
        functions_frame.setProperty("class", "glass-card")
        functions_frame.setMinimumHeight(200)
        functions_layout = QVBoxLayout(functions_frame)
        
        functions_title = QLabel("Available Advanced Functions")
        functions_title.setProperty("class", "section-title")
        functions_layout.addWidget(functions_title)
        
        self.advanced_functions_list = QListWidget()
        self.advanced_functions_list.setProperty("class", "glass-card")
        self.advanced_functions_list.itemSelectionChanged.connect(self.show_advanced_function_details)
        self.advanced_functions_list.itemDoubleClicked.connect(self.execute_advanced_function)
        functions_layout.addWidget(self.advanced_functions_list)
        
        content_layout.addWidget(functions_frame)

        # Function details frame
        details_frame = QFrame()
        details_frame.setProperty("class", "glass-card")
        details_frame.setMinimumHeight(150)
        details_layout = QVBoxLayout(details_frame)
        
        details_title = QLabel("Function Details")
        details_title.setProperty("class", "section-title")
        details_layout.addWidget(details_title)
        
        self.advanced_function_details = QTextEdit()
        self.advanced_function_details.setReadOnly(True)
        self.advanced_function_details.setMaximumHeight(150)
        self.advanced_function_details.setPlainText("Select an advanced function to view details and parameters.")
        details_layout.addWidget(self.advanced_function_details)
        
        content_layout.addWidget(details_frame)

        # Control buttons frame
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        
        self.execute_advanced_btn = QPushButton("⚡ Execute Function")
        self.execute_advanced_btn.setProperty("class", "primary")
        self.execute_advanced_btn.clicked.connect(self.execute_advanced_function)
        self.execute_advanced_btn.setEnabled(False)

        self.refresh_advanced_btn = QPushButton("🔄 Refresh Functions")
        self.refresh_advanced_btn.setProperty("class", "success")
        self.refresh_advanced_btn.clicked.connect(self.refresh_advanced_functions_list)

        buttons_layout.addWidget(self.execute_advanced_btn)
        buttons_layout.addWidget(self.refresh_advanced_btn)
        buttons_layout.addStretch()
        
        content_layout.addWidget(buttons_frame)

        # Results frame
        results_frame = QFrame()
        results_frame.setProperty("class", "glass-card")
        results_frame.setMinimumHeight(150)
        results_layout = QVBoxLayout(results_frame)
        
        results_title = QLabel("Execution Results")
        results_title.setProperty("class", "section-title")
        results_layout.addWidget(results_title)
        
        self.advanced_results_text = QTextEdit()
        self.advanced_results_text.setReadOnly(True)
        self.advanced_results_text.setPlainText("Advanced function execution results will appear here.")
        results_layout.addWidget(self.advanced_results_text)
        
        content_layout.addWidget(results_frame)

        # Add stretch to push everything up
        content_layout.addStretch()

        # Set the scroll area content
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Initialize functions list
        self.refresh_advanced_functions_list()

        return tab, "🚀 Advanced"

    def refresh_advanced_functions_list(self) -> None:
        """Refresh the advanced functions list with enhanced error handling"""
        self.advanced_functions_list.clear()

        try:
            from shared.advance import get_advanced_functions
            from shared.logger import get_logger
            
            # Get logger for this module
            logger = get_logger(__name__)
            logger.info("Loading advanced functions...")
            
            functions = get_advanced_functions()
            
            if not functions:
                self.advanced_status_label.setText("⚠️ No advanced functions available")
                self.advanced_functions_list.addItem("No advanced functions available")
                return
                
            # Validate function objects
            valid_functions = []
            for func in functions:
                if hasattr(func, 'name') and hasattr(func, 'category'):
                    valid_functions.append(func)
                else:
                    logger.warning(f"Invalid advanced function object found: {func}")
            
            if not valid_functions:
                self.advanced_status_label.setText("⚠️ No valid advanced functions found")
                self.advanced_functions_list.addItem("No valid functions available")
                return
                
            for func in valid_functions:
                try:
                    # Add complexity indicator
                    complexity_emoji = "🟢" if func.complexity == "Low" else "🟡" if func.complexity == "Medium" else "🔴"
                    item_text = f"{complexity_emoji} {func.name} ({func.category} - {func.estimated_time})"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, func)
                    self.advanced_functions_list.addItem(item)
                except Exception as e:
                    logger.error(f"Error adding advanced function {getattr(func, 'name', 'Unknown')}: {e}")

            self.advanced_status_label.setText(f"✅ Found {len(valid_functions)} advanced functions available")
            logger.info(f"Successfully loaded {len(valid_functions)} advanced functions")

        except ImportError as e:
            self.advanced_status_label.setText("❌ Advanced functions module not available")
            self.advanced_functions_list.addItem("Module import error - check installation")
            logger.error(f"Import error loading advanced functions: {e}")
            
        except Exception as e:
            self.advanced_status_label.setText("❌ Error loading advanced functions")
            self.advanced_functions_list.addItem("Error loading functions")
            logger.error(f"Error loading advanced functions: {e}")

        # Update function details
        self.advanced_function_details.setPlainText("Select an advanced function to view details and parameters.")
        self.execute_advanced_btn.setEnabled(False)

    def show_advanced_function_details(self) -> None:
        """Show details of selected advanced function with enhanced validation"""
        current_item = self.advanced_functions_list.currentItem()
        if not current_item:
            self.advanced_function_details.setPlainText("Select an advanced function to view details and parameters.")
            self.execute_advanced_btn.setEnabled(False)
            return

        func = current_item.data(Qt.ItemDataRole.UserRole)
        if not func:
            self.advanced_function_details.setPlainText("❌ Invalid function selected.")
            self.execute_advanced_btn.setEnabled(False)
            return

        try:
            # Validate function attributes
            required_attrs = ['name', 'category', 'complexity', 'description']
            missing_attrs = [attr for attr in required_attrs if not hasattr(func, attr)]
            
            if missing_attrs:
                self.advanced_function_details.setPlainText(f"❌ Function missing required attributes: {', '.join(missing_attrs)}")
                self.execute_advanced_btn.setEnabled(False)
                return

            # Build details text with error handling
            details = f"Advanced Function Details:\n"
            details += "=" * 40 + "\n\n"
            
            details += f"Name: {func.name}\n"
            details += f"Category: {func.category}\n"
            
            # Complexity with color coding
            complexity = getattr(func, 'complexity', 'Unknown')
            complexity_emoji = "🟢" if complexity == "Low" else "🟡" if complexity == "Medium" else "🔴"
            details += f"Complexity: {complexity_emoji} {complexity}\n"
            
            # Estimated time
            if hasattr(func, 'estimated_time'):
                details += f"Estimated Time: {func.estimated_time}\n"
            
            # Security level if available
            if hasattr(func, 'security_level'):
                details += f"Security Level: {func.security_level}\n"
            
            details += "\n"

            # Description
            details += f"Description:\n{func.description}\n\n"

            # Prerequisites if available
            if hasattr(func, 'prerequisites') and func.prerequisites:
                details += "Prerequisites:\n"
                for pre in func.prerequisites:
                    if isinstance(pre, str):
                        details += f"• {pre}\n"
                    else:
                        details += f"• {str(pre)}\n"
                details += "\n"

            # Risks if available
            if hasattr(func, 'risks') and func.risks:
                details += "⚠️ Risks & Warnings:\n"
                for risk in func.risks:
                    if isinstance(risk, str):
                        details += f"⚠️ {risk}\n"
                    else:
                        details += f"⚠️ {str(risk)}\n"
                details += "\n"

            # Expected results if available
            if hasattr(func, 'mock_result'):
                details += "Expected Results:\n"
                for key, value in func.mock_result.items():
                    if key not in ["status", "timestamp"]:
                        formatted_key = key.replace('_', ' ').title()
                        details += f"• {formatted_key}: {value}\n"
            elif hasattr(func, 'expected_results'):
                details += "Expected Results:\n"
                if isinstance(func.expected_results, list):
                    for result in func.expected_results:
                        details += f"• {result}\n"
                elif isinstance(func.expected_results, dict):
                    for key, value in func.expected_results.items():
                        formatted_key = key.replace('_', ' ').title()
                        details += f"• {formatted_key}: {value}\n"

            # Special notes for high-complexity functions
            if complexity in ["High", "Expert"]:
                details += "\n⚠️ HIGH COMPLEXITY FUNCTION:\n"
                details += "This function requires expert knowledge.\n"
                details += "Ensure proper understanding before proceeding.\n"

            self.advanced_function_details.setPlainText(details)
            self.execute_advanced_btn.setEnabled(True)
            
        except Exception as e:
            from shared.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error displaying advanced function details: {e}")
            
            self.advanced_function_details.setPlainText(f"❌ Error displaying function details:\n\n{str(e)}")
            self.execute_advanced_btn.setEnabled(False)

    def execute_advanced_function(self) -> None:
        """Execute the selected advanced function"""