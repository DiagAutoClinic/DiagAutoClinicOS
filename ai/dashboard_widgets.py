#!/usr/bin/env python3
"""
AI Dashboard Widgets Module
Custom UI components for AI monitoring and visualization
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
import random
from typing import List, Dict, Any

class AIHealthMonitor(QWidget):
    """
    AI Health Monitor Widget
    Displays real-time AI health score and system status
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.health_score = 0.0
        self.ai_status = "Initializing"
        self.setup_ui()

    def setup_ui(self):
        """Setup the AI health monitor UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title
        title = QLabel("🤖 AI Health Monitor")
        title.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            color: #21F5C1;
            padding: 5px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Health Score Display
        self.health_label = QLabel("Health Score: 0%")
        self.health_label.setStyleSheet("""
            font-size: 24pt;
            font-weight: bold;
            color: white;
            padding: 10px;
        """)
        self.health_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.health_label)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #21F5C1;
                border-radius: 10px;
                text-align: center;
                background: #3a3a3a;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #21F5C1, stop:1 #134F4A);
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Status Label
        self.status_label = QLabel("Status: Initializing")
        self.status_label.setStyleSheet("""
            font-size: 12pt;
            color: #FFD700;
            padding: 5px;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # AI Activity Indicator
        self.activity_label = QLabel("AI Activity: Idle")
        self.activity_label.setStyleSheet("""
            font-size: 10pt;
            color: #87CEEB;
            padding: 5px;
        """)
        self.activity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.activity_label)

        # Set widget styling
        self.setStyleSheet("""
            AIHealthMonitor {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e1e, stop:1 #2b2b2b);
                border: 2px solid #21F5C1;
                border-radius: 15px;
            }
        """)

    def update_health_score(self, score: float):
        """
        Update the AI health score display

        Args:
            score: Health score between 0.0 and 1.0
        """
        self.health_score = score
        percentage = int(score * 100)
        self.health_label.setText(f"Health Score: {percentage}%")
        self.progress_bar.setValue(percentage)

        # Update color based on score
        if score >= 0.8:
            color = "#4CAF50"  # Green
            status = "Excellent"
        elif score >= 0.6:
            color = "#FFD700"  # Yellow
            status = "Good"
        elif score >= 0.4:
            color = "#FFA500"  # Orange
            status = "Fair"
        else:
            color = "#F44336"  # Red
            status = "Poor"

        self.status_label.setText(f"Status: {status}")
        self.status_label.setStyleSheet(f"""
            font-size: 12pt;
            color: {color};
            font-weight: bold;
            padding: 5px;
        """)

    def update_activity(self, activity: str):
        """
        Update AI activity status

        Args:
            activity: Current AI activity description
        """
        self.activity_label.setText(f"AI Activity: {activity}")

class AIPredictionWidget(QWidget):
    """
    AI Prediction Widget
    Displays current AI predictions and recommendations
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.predictions = []
        self.setup_ui()

    def setup_ui(self):
        """Setup the AI prediction widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title
        title = QLabel("🔮 AI Predictions")
        title.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            color: #21F5C1;
            padding: 5px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Predictions Container
        self.predictions_container = QFrame()
        self.predictions_container.setStyleSheet("""
            background: #1e1e1e;
            border: 1px solid #21F5C1;
            border-radius: 10px;
            padding: 10px;
        """)
        self.predictions_layout = QVBoxLayout(self.predictions_container)
        self.predictions_layout.setSpacing(8)

        # Default message
        self.default_label = QLabel("No predictions available")
        self.default_label.setStyleSheet("""
            color: #888;
            font-style: italic;
            padding: 20px;
        """)
        self.default_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.predictions_layout.addWidget(self.default_label)

        layout.addWidget(self.predictions_container)

        # Set widget styling
        self.setStyleSheet("""
            AIPredictionWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e1e, stop:1 #2b2b2b);
                border: 2px solid #21F5C1;
                border-radius: 15px;
            }
        """)

    def update_predictions(self, predictions: List[Dict[str, Any]]):
        """
        Update the predictions display

        Args:
            predictions: List of prediction dictionaries
        """
        self.predictions = predictions

        # Clear existing predictions
        for i in reversed(range(self.predictions_layout.count())):
            widget = self.predictions_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        if not predictions:
            self.predictions_layout.addWidget(self.default_label)
            return

        # Add each prediction
        for prediction in predictions:
            prediction_widget = self._create_prediction_item(prediction)
            self.predictions_layout.addWidget(prediction_widget)

    def _create_prediction_item(self, prediction: Dict[str, Any]) -> QFrame:
        """Create a prediction item widget"""
        item = QFrame()
        item.setStyleSheet("""
            background: #2b2b2b;
            border: 1px solid #21F5C1;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 5px;
        """)

        layout = QVBoxLayout(item)
        layout.setSpacing(5)

        # Prediction type and description
        type_label = QLabel(f"🔴 {prediction['type']}" if prediction['severity'] == 'critical'
                          else f"🟡 {prediction['type']}" if prediction['severity'] == 'warning'
                          else f"🟢 {prediction['type']}")
        type_label.setStyleSheet("""
            font-size: 11pt;
            font-weight: bold;
            color: #F44336 if critical else #FFA500 if warning else #4CAF50;
        """)

        desc_label = QLabel(prediction['description'])
        desc_label.setStyleSheet("color: white; font-size: 10pt;")

        # Confidence and action
        confidence_label = QLabel(f"Confidence: {prediction['confidence']:.2f}")
        confidence_label.setStyleSheet("color: #87CEEB; font-size: 9pt;")

        action_label = QLabel(f"Action: {prediction['suggested_action']}")
        action_label.setStyleSheet("color: #FFD700; font-size: 9pt; font-style: italic;")

        layout.addWidget(type_label)
        layout.addWidget(desc_label)
        layout.addWidget(confidence_label)
        layout.addWidget(action_label)

        return item

class AIActivityIndicator(QWidget):
    """
    AI Activity Indicator Widget
    Shows real-time AI processing activity
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.activity_level = 0
        self.setup_ui()

    def setup_ui(self):
        """Setup the AI activity indicator UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title
        title = QLabel("🤖 AI Activity")
        title.setStyleSheet("""
            font-size: 14pt;
            font-weight: bold;
            color: #21F5C1;
            padding: 5px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Activity Bars
        self.activity_bars = []
        for i in range(5):
            bar = QFrame()
            bar.setFixedHeight(8)
            bar.setStyleSheet("""
                background: #3a3a3a;
                border-radius: 4px;
                margin: 2px 0;
            """)
            self.activity_bars.append(bar)
            layout.addWidget(bar)

        # Activity Label
        self.activity_label = QLabel("AI Processing: Idle")
        self.activity_label.setStyleSheet("""
            color: #87CEEB;
            font-size: 10pt;
            padding: 5px;
        """)
        self.activity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.activity_label)

        # Set widget styling
        self.setStyleSheet("""
            AIActivityIndicator {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e1e, stop:1 #2b2b2b);
                border: 2px solid #21F5C1;
                border-radius: 15px;
            }
        """)

        # Start animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._animate_activity)
        self.animation_timer.start(200)

    def set_activity_level(self, level: int):
        """
        Set the AI activity level (0-5)

        Args:
            level: Activity level between 0 and 5
        """
        self.activity_level = max(0, min(5, level))

    def _animate_activity(self):
        """Animate the activity bars"""
        for i, bar in enumerate(self.activity_bars):
            if i < self.activity_level:
                # Active bar with animation
                bar.setStyleSheet(f"""
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #21F5C1, stop:1 #134F4A);
                    border-radius: 4px;
                    margin: 2px 0;
                """)
            else:
                # Inactive bar
                bar.setStyleSheet("""
                    background: #3a3a3a;
                    border-radius: 4px;
                    margin: 2px 0;
                """)

    def update_activity_text(self, text: str):
        """
        Update the activity text

        Args:
            text: Activity description text
        """
        self.activity_label.setText(f"AI Processing: {text}")

class AIMaintenanceWidget(QWidget):
    """
    AI Maintenance Recommendations Widget
    Displays AI-generated maintenance recommendations
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.recommendations = []
        self.setup_ui()

    def setup_ui(self):
        """Setup the AI maintenance widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title
        title = QLabel("🔧 AI Recommendations")
        title.setStyleSheet("""
            font-size: 14pt;
            font-weight: bold;
            color: #21F5C1;
            padding: 5px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Recommendations Container
        self.recommendations_container = QFrame()
        self.recommendations_container.setStyleSheet("""
            background: #1e1e1e;
            border: 1px solid #21F5C1;
            border-radius: 10px;
            padding: 10px;
        """)
        self.recommendations_layout = QVBoxLayout(self.recommendations_container)
        self.recommendations_layout.setSpacing(8)

        # Default message
        self.default_label = QLabel("No recommendations available")
        self.default_label.setStyleSheet("""
            color: #888;
            font-style: italic;
            padding: 20px;
        """)
        self.default_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.recommendations_layout.addWidget(self.default_label)

        layout.addWidget(self.recommendations_container)

        # Set widget styling
        self.setStyleSheet("""
            AIMaintenanceWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e1e, stop:1 #2b2b2b);
                border: 2px solid #21F5C1;
                border-radius: 15px;
            }
        """)

    def update_recommendations(self, recommendations: List[str]):
        """
        Update the recommendations display

        Args:
            recommendations: List of recommendation strings
        """
        self.recommendations = recommendations

        # Clear existing recommendations
        for i in reversed(range(self.recommendations_layout.count())):
            widget = self.recommendations_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        if not recommendations:
            self.recommendations_layout.addWidget(self.default_label)
            return

        # Add each recommendation
        for i, recommendation in enumerate(recommendations):
            recommendation_widget = self._create_recommendation_item(recommendation, i)
            self.recommendations_layout.addWidget(recommendation_widget)

    def _create_recommendation_item(self, recommendation: str, index: int) -> QFrame:
        """Create a recommendation item widget"""
        item = QFrame()
        item.setStyleSheet("""
            background: #2b2b2b;
            border: 1px solid #21F5C1;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 5px;
        """)

        layout = QVBoxLayout(item)
        layout.setSpacing(5)

        # Priority indicator
        priority = "URGENT" if "URGENT:" in recommendation else "RECOMMENDED" if "RECOMMENDED:" in recommendation else "INFO"
        priority_color = "#F44336" if priority == "URGENT" else "#FFA500" if priority == "RECOMMENDED" else "#4CAF50"

        priority_label = QLabel(priority)
        priority_label.setStyleSheet(f"""
            font-size: 9pt;
            font-weight: bold;
            color: {priority_color};
            padding: 2px 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        """)

        # Recommendation text
        text = recommendation.replace("URGENT:", "").replace("RECOMMENDED:", "").strip()
        text_label = QLabel(text)
        text_label.setStyleSheet("color: white; font-size: 10pt;")
        text_label.setWordWrap(True)

        layout.addWidget(priority_label)
        layout.addWidget(text_label)

        return item