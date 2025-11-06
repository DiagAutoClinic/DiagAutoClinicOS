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
