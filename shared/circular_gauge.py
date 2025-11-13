#!/usr/bin/env python3
"""
Circular Gauge Widget for DACOS
Modern data visualization component
"""

import re
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont

class CircularGauge(QWidget):
    """Modern circular gauge for displaying percentage values"""
    
    def __init__(self, value=0, max_value=100, label="", unit="%", parent=None):
        super().__init__(parent)
        self.value = 0
        self.max_value = 100
        self.label_text = label
        self.unit = unit
        self.setMinimumSize(150, 150)
        self.setMaximumSize(200, 200)
        
        # Initialize the value
        self.set_value(value)
        
    def set_value(self, value):
        """Update gauge value - accepts int, float, or str"""
        try:
            v = float(value)
        except (TypeError, ValueError):
            v = 0
        
        # Clamp to 0-100
        self.value = max(0, min(100, v))
        self.update()
        
    def paintEvent(self, event):
        """Custom paint event for circular gauge"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get widget dimensions
        width = self.width()
        height = self.height()
        size = min(width, height)
        
        # Center point
        center_x = width / 2
        center_y = height / 2
        radius = size / 2 - 20
        
        # Background circle
        painter.setPen(QPen(QColor(20, 77, 77, 100), 12, Qt.PenStyle.SolidLine))
        rect = QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2)
        painter.drawArc(rect, 0, 360 * 16)
        
        # Progress arc
        percentage = (self.value / self.max_value) * 100
        angle = int((percentage / 100) * 360 * 16)
        
        # Gradient color based on value
        if percentage < 33:
            color = QColor(239, 68, 68)  # Red
        elif percentage < 66:
            color = QColor(251, 191, 36)  # Yellow
        else:
            color = QColor(16, 185, 129)  # Green/Teal
        
        painter.setPen(QPen(color, 12, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(rect, 90 * 16, -angle)
        
        # Draw value text
        painter.setPen(QColor(220, 255, 250))
        value_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        painter.setFont(value_font)
        value_text = f"{int(self.value)}{self.unit}"
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, value_text)
        
        # Draw label
        if self.label_text:
            painter.setPen(QColor(94, 234, 212))
            label_font = QFont("Segoe UI", 10)
            painter.setFont(label_font)
            label_rect = QRectF(center_x - radius, center_y + radius/2, radius * 2, 30)
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, self.label_text)


class StatCard(QFrame):
    """Glassmorphic stat card with circular gauge"""
    
    def __init__(self, title, value, max_value=100, unit="%", parent=None):
        super().__init__(parent)
        self.setProperty("class", "stat-card")
        self.setMinimumSize(200, 220)
        self.setMaximumSize(300, 280)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title_label = QLabel(title)
        title_label.setProperty("class", "stat-label")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        
        # Parse value - handle strings like "97%" or numbers
        clean_value = self._parse_value(value)
        
        # Circular gauge
        self.gauge = CircularGauge(clean_value, max_value, "", unit)
        self.gauge.setProperty("class", "circular-gauge")
        
        # Value label (for compatibility)
        self.value_label = QLabel(f"{int(clean_value)}{unit}")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet(
            "font-size: 14pt; font-weight: bold; color: #14b8a6;"
        )
        
        layout.addWidget(title_label)
        layout.addWidget(self.gauge, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
    
    def _parse_value(self, value):
        """Parse value - handles strings like '97%' or numbers"""
        if isinstance(value, str):
            # Remove % and any other non-numeric characters
            numeric = re.sub(r'[^0-9.]', '', value)
            try:
                return float(numeric) if numeric else 0
            except ValueError:
                return 0
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0
        
    def update_value(self, value):
        """Update the gauge value"""
        clean_value = self._parse_value(value)
        self.gauge.set_value(clean_value)
        # Update text label too
        if hasattr(self, 'value_label') and hasattr(self.gauge, 'unit'):
            try:
                val = int(clean_value)
                self.value_label.setText(f"{val}{self.gauge.unit}")
            except (TypeError, ValueError):
                self.value_label.setText(str(value))