#!/usr/bin/env python3
"""
Modern Techy Style Manager for AutoKey
Provides dark/light mode and modern styling for key programming
"""

from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtWidgets import QApplication, QStyleFactory

class StyleManager:
    def __init__(self):
        self.settings = QSettings("AutoKey", "Style")
        self.current_theme = self.settings.value("theme", "dark")
        self.font_family = self.settings.value("font_family", "Segoe UI")
        self.font_size = int(self.settings.value("font_size", "9"))
        
    def set_theme(self, theme_name):
        """Set the application theme with error handling"""
        if theme_name not in self.get_theme_names():
            print(f"Warning: Unknown theme {theme_name}. Using dark theme.")
            theme_name = "dark"
        
        self.current_theme = theme_name
        self.settings.setValue("theme", theme_name)
        
        if theme_name == "dark":
            self.apply_dark_theme()
        elif theme_name == "light":
            self.apply_light_theme()
        elif theme_name == "security":
            self.apply_security_theme()
        elif theme_name == "professional":
            self.apply_professional_theme()
        else:
            self.apply_dark_theme()
            
    def set_font(self, font_family=None, font_size=None):
        """Set application font"""
        if font_family:
            self.font_family = font_family
            self.settings.setValue("font_family", font_family)
        if font_size:
            self.font_size = font_size
            self.settings.setValue("font_size", str(font_size))
        
        self.set_theme(self.current_theme)
        
    def apply_dark_theme(self):
        """Apply modern dark theme for key programming"""
        app = QApplication.instance()
        app.setStyle(QStyleFactory.create("Fusion"))
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(20, 15, 25))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Base, QColor(30, 25, 35))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(40, 35, 45))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(45, 40, 50))
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Button, QColor(45, 40, 50))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(180, 100, 255))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(120, 80, 215))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        app.setPalette(palette)
        app.setStyleSheet(self.get_dark_stylesheet())
        
    def apply_light_theme(self):
        """Apply modern light theme"""
        app = QApplication.instance()
        app.setStyle(QStyleFactory.create("Fusion"))
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.Text, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(100, 0, 200))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(120, 80, 215))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        app.setPalette(palette)
        app.setStyleSheet(self.get_light_stylesheet())
        
    def apply_security_theme(self):
        """Apply security-focused theme for key programming"""
        app = QApplication.instance()
        app.setStyle(QStyleFactory.create("Fusion"))
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(15, 20, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 230, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 30, 40))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 40, 50))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(45, 50, 60))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(220, 230, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(220, 230, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(60, 70, 100))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 230, 255))
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.cyan)
        palette.setColor(QPalette.ColorRole.Link, QColor(120, 150, 255))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(80, 120, 255))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        app.setPalette(palette)
        app.setStyleSheet(self.get_security_stylesheet())
        
    def apply_professional_theme(self):
        """Apply professional theme"""
        app = QApplication.instance()
        app.setStyle(QStyleFactory.create("Fusion"))
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 48))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(241, 241, 241))
        palette.setColor(QPalette.ColorRole.Base, QColor(37, 37, 38))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 48))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(63, 63, 70))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(241, 241, 241))
        palette.setColor(QPalette.ColorRole.Text, QColor(241, 241, 241))
        palette.setColor(QPalette.ColorRole.Button, QColor(63, 63, 70))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(241, 241, 241))
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 151, 251))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 151, 251))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        app.setPalette(palette)
        app.setStyleSheet(self.get_professional_stylesheet())

    def _get_base_stylesheet(self):
        """Common styles shared across themes"""
        return f"""
            QWidget {{
                font-family: '{self.font_family}';
                font-size: {self.font_size}pt;
            }}
            
            QToolTip {{
                padding: 5px;
                border: 1px solid #666;
                opacity: 240;
            }}
        """

    def get_dark_stylesheet(self):
        """Return dark theme stylesheet for AutoKey"""
        base_styles = self._get_base_stylesheet()
        return base_styles + """
            /* AutoKey Dark Theme */
            QMainWindow, QDialog {
                background-color: #1a1520;
                color: #f0f0f0;
            }
            
            /* Key Programming Specific Styling */
            QFrame[class="key_frame"] {
                background-color: #252030;
                border: 2px solid #3a2a4a;
                border-radius: 8px;
                padding: 15px;
            }
            
            QFrame[class="key_frame"]:hover {
                border-color: #9060c0;
                background-color: #2a2535;
            }
            
            QLabel[class="key_status"] {
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            
            QLabel[class="key_status_programmed"] {
                background-color: #107c10;
                color: white;
            }
            
            QLabel[class="key_status_unprogrammed"] {
                background-color: #d13438;
                color: white;
            }
            
            QLabel[class="key_status_learning"] {
                background-color: #9060c0;
                color: white;
            }
            
            QLabel[class="key_status_syncing"] {
                background-color: #ff8c00;
                color: white;
            }
            
            /* Key Programming Buttons */
            QPushButton[class="key_button"] {
                background-color: #9060c0;
                color: white;
                border: 2px solid #7a50a0;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 10pt;
                min-width: 120px;
            }
            
            QPushButton[class="key_button"]:hover {
                background-color: #7a50a0;
            }
            
            QPushButton[class="key_button"]:pressed {
                background-color: #654080;
            }
            
            QPushButton[class="program_key_button"] {
                background-color: #9060c0;
                color: white;
                border: 2px solid #7a50a0;
            }
            
            QPushButton[class="clone_key_button"] {
                background-color: #20a0a0;
                color: white;
                border: 2px solid #1a8080;
            }
            
            QPushButton[class="reset_key_button"] {
                background-color: #d13438;
                color: white;
                border: 2px solid #b02a30;
            }
            
            /* Key Data Tables */
            QTableWidget[class="key_data_table"] {
                background-color: #252030;
                color: #f0f0f0;
                gridline-color: #3a2a4a;
                border: 1px solid #3a2a4a;
                border-radius: 6px;
                alternate-background-color: #2a2535;
            }
            
            QTableWidget[class="key_data_table"]::item {
                padding: 8px;
                border-bottom: 1px solid #3a2a4a;
            }
            
            QTableWidget[class="key_data_table"]::item:selected {
                background-color: #9060c0;
                color: white;
            }
            
            /* Security Code Input */
            QLineEdit[class="security_code"] {
                background-color: #252030;
                color: #ffcc00;
                border: 2px solid #3a2a4a;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-weight: bold;
                letter-spacing: 2px;
            }
            
            QLineEdit[class="security_code"]:focus {
                border-color: #ffcc00;
                background-color: #2a2535;
            }
            
            /* Transponder Section */
            QGroupBox[class="transponder_group"] {
                color: #f0f0f0;
                font-weight: bold;
                border: 2px solid #3a2a4a;
                border-radius: 6px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            
            QGroupBox[class="transponder_group"]::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #9060c0;
            }
            
            /* Immobilizer Status */
            QLabel[class="immobilizer_status"] {
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
                border: 2px solid;
            }
            
            QLabel[class="immobilizer_active"] {
                background-color: #d13438;
                color: white;
                border-color: #b02a30;
            }
            
            QLabel[class="immobilizer_inactive"] {
                background-color: #107c10;
                color: white;
                border-color: #0e6b0e;
            }
            
            /* Vehicle Information */
            QFrame[class="vehicle_info"] {
                background-color: #252030;
                border: 2px solid #3a2a4a;
                border-radius: 8px;
                padding: 12px;
            }
            
            QLabel[class="vehicle_make"] {
                font-size: 14pt;
                font-weight: bold;
                color: #9060c0;
            }
            
            QLabel[class="vehicle_model"] {
                font-size: 12pt;
                color: #cccccc;
            }
        """

    def get_light_stylesheet(self):
        """Return light theme stylesheet"""
        base_styles = self._get_base_stylesheet()
        return base_styles + """
            /* AutoKey Light Theme */
            QMainWindow, QDialog {
                background-color: #f5f5f5;
                color: #333333;
            }
            
            QFrame[class="key_frame"] {
                background-color: #ffffff;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
            }
        """

    def get_security_stylesheet(self):
    """Return enhanced security theme stylesheet"""
    base_styles = self._get_base_stylesheet()
    return base_styles + """
        /* Enhanced Security Theme */
        QMainWindow, QDialog {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #0a0f1a, stop: 1 #151a25);
            color: #dce5ff;
        }
        
        /* User Info */
        QLabel[class="user-info"] {
            color: #4a8aff;
            font-weight: bold;
            padding: 5px;
            background-color: rgba(74, 138, 255, 0.1);
            border-radius: 4px;
        }
        
        /* Tab Headers */
        QLabel[class="tab-header"] {
            font-size: 16pt;
            font-weight: bold;
            color: #4a8aff;
            padding: 10px;
            background-color: rgba(74, 138, 255, 0.1);
            border-radius: 6px;
            margin: 5px;
        }
        
        /* Function/Procedure Names */
        QLabel[class="function-name"], QLabel[class="procedure-name"] {
            font-size: 14pt;
            font-weight: bold;
            color: #ffaa00;
            padding: 5px;
        }
        
        /* Security Info */
        QLabel[class="security-info"] {
            color: #ff6b6b;
            font-weight: bold;
            padding: 3px;
            background-color: rgba(255, 107, 107, 0.1);
            border-radius: 3px;
        }
        
        /* Specialized Group Boxes */
        QGroupBox {
            color: #4a8aff;
            font-weight: bold;
            border: 2px solid #3a4a6a;
            border-radius: 8px;
            margin-top: 1ex;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
            color: #4a8aff;
        }
        
        /* Enhanced Lists */
        QListWidget {
            background-color: #1a1f2a;
            color: #dce5ff;
            border: 1px solid #2a3a5a;
            border-radius: 4px;
            padding: 5px;
        }
        
        QListWidget::item {
            padding: 8px;
            border-bottom: 1px solid #2a3a5a;
        }
        
        QListWidget::item:selected {
            background-color: #2a5aaa;
            color: white;
        }
        
        QListWidget::item:hover {
            background-color: #1a4a9a;
        }
        
        /* Enhanced Text Edits */
        QTextEdit {
            background-color: #1a1f2a;
            color: #dce5ff;
            border: 1px solid #2a3a5a;
            border-radius: 4px;
            padding: 8px;
        }
        
        /* Security Status */
        QTextEdit[class="security-log"] {
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 10pt;
            background-color: #0a0f1a;
            color: #a0b0ff;
        }
    """
    
    def get_security_stylesheet(self):
        """Return security theme stylesheet"""
        base_styles = self._get_base_stylesheet()
        return base_styles + """
            /* AutoKey Security Theme */
            QMainWindow, QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #0f1420, stop: 1 #1a2230);
                color: #dce5ff;
            }
            
            QFrame[class="key_frame"] {
                background-color: rgba(40, 45, 60, 0.9);
                border: 2px solid #4a5a7a;
                border-radius: 8px;
                padding: 15px;
            }
            
            QPushButton[class="key_button"] {
                background-color: #4a6cd4;
                color: white;
                border: 2px solid #3a5cb4;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            
            QLineEdit[class="security_code"] {
                background-color: #1a1f2a;
                color: #ffcc00;
                border: 2px solid #4a5a7a;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-weight: bold;
            }
        """
    
    def get_professional_stylesheet(self):
        """Return professional theme stylesheet"""
        base_styles = self._get_base_stylesheet()
        return base_styles + """
            /* AutoKey Professional Theme */
            QMainWindow, QDialog {
                background-color: #2d2d30;
                color: #f0f0f0;
            }
            
            QFrame[class="key_frame"] {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 12px;
            }
        """

    def get_theme_names(self):
        """Return available theme names"""
        return ["dark", "light", "security", "professional"]
    
    def get_theme_info(self):
        """Return theme metadata for UI display"""
        return {
            "dark": {
                "name": "Dark Mode", 
                "description": "Modern dark theme for key programming",
                "preview_color": "#1a1520"
            },
            "light": {
                "name": "Light Mode", 
                "description": "Clean light theme for bright environments", 
                "preview_color": "#f5f5f5"
            },
            "security": {
                "name": "Security Blue", 
                "description": "Security-focused blue theme",
                "preview_color": "#0f1420"
            },
            "professional": {
                "name": "Professional", 
                "description": "VS Code inspired professional theme",
                "preview_color": "#2d2d30"
            }
        }
