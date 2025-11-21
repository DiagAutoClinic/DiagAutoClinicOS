#!/usr/bin/env python3
"""
Enhanced Circular Gauge & Stat Card Components
Matches launcher.py futuristic teal aesthetic
"""

import re
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QBrush, QLinearGradient

class CircularGauge(QWidget):
    """Futuristic circular gauge with glow effects"""
    
    def __init__(self, value=0, max_value=100, label="", unit="%", parent=None):
        super().__init__(parent)
        self._value = 0
        self._animated_value = 0
        self.max_value = 100
        self.label_text = label
        self.unit = unit
        self.setMinimumSize(140, 140)
        self.setMaximumSize(220, 220)
        
        # Animation setup
        self.animation = QPropertyAnimation(self, b"animated_value")
        self.animation.setDuration(800)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Initialize the value
        self.set_value(value)
        
    @pyqtProperty(float)
    def animated_value(self):
        return self._animated_value
    
    @animated_value.setter
    def animated_value(self, value):
        self._animated_value = value
        self.update()
        
    def set_value(self, value):
        """Update gauge value with smooth animation"""
        try:
            v = float(value)
        except (TypeError, ValueError):
            v = 0
        
        # Clamp to 0-100
        self._value = max(0, min(100, v))
        
        # Animate to new value
        self.animation.stop()
        self.animation.setStartValue(self._animated_value)
        self.animation.setEndValue(self._value)
        self.animation.start()
        
    def paintEvent(self, event):
        """Custom paint with futuristic teal glow"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get dimensions
        width = self.width()
        height = self.height()
        size = min(width, height)
        
        # Center point
        center_x = width / 2
        center_y = height / 2
        radius = size / 2 - 25
        
        # Draw outer glow ring
        painter.setPen(QPen(QColor(42, 245, 209, 60), 18, Qt.PenStyle.SolidLine))
        glow_rect = QRectF(center_x - radius - 2, center_y - radius - 2, 
                           (radius + 2) * 2, (radius + 2) * 2)
        painter.drawArc(glow_rect, 0, 360 * 16)
        
        # Background circle (dark teal)
        painter.setPen(QPen(QColor(19, 79, 74, 180), 14, Qt.PenStyle.SolidLine))
        rect = QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2)
        painter.drawArc(rect, 0, 360 * 16)
        
        # Progress arc with gradient
        percentage = (self._animated_value / self.max_value) * 100
        angle = int((percentage / 100) * 360 * 16)
        
        # Gradient color based on value
        if percentage < 33:
            start_color = QColor(255, 77, 77)  # Red
            end_color = QColor(220, 38, 38)
        elif percentage < 66:
            start_color = QColor(245, 158, 11)  # Orange
            end_color = QColor(251, 191, 36)
        else:
            start_color = QColor(33, 245, 193)  # Teal (theme accent)
            end_color = QColor(42, 245, 209)
        
        # Create gradient pen
        painter.setPen(QPen(start_color, 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(rect, 90 * 16, -angle)
        
        # Inner glow effect
        if percentage > 0:
            painter.setPen(QPen(QColor(end_color.red(), end_color.green(), end_color.blue(), 100), 
                               18, Qt.PenStyle.SolidLine))
            painter.drawArc(rect, 90 * 16, -angle)
        
        # Center circle background
        center_radius = radius * 0.7
        center_rect = QRectF(center_x - center_radius, center_y - center_radius,
                            center_radius * 2, center_radius * 2)
        
        gradient = QLinearGradient(center_x, center_y - center_radius,
                                   center_x, center_y + center_radius)
        gradient.setColorAt(0, QColor(15, 61, 58))
        gradient.setColorAt(1, QColor(11, 46, 43))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(33, 245, 193, 100), 2))
        painter.drawEllipse(center_rect)
        
        # Draw value text (large)
        painter.setPen(QColor(33, 245, 193))  # Accent teal
        value_font = QFont("Segoe UI", 22, QFont.Weight.Bold)
        painter.setFont(value_font)
        value_text = f"{int(self._animated_value)}"
        
        value_rect = QRectF(center_x - center_radius, center_y - center_radius/2,
                           center_radius * 2, center_radius)
        painter.drawText(value_rect, Qt.AlignmentFlag.AlignCenter, value_text)
        
        # Draw unit text (smaller)
        painter.setPen(QColor(158, 217, 207))  # Muted teal
        unit_font = QFont("Segoe UI", 11)
        painter.setFont(unit_font)
        unit_rect = QRectF(center_x - center_radius, center_y + center_radius/4,
                          center_radius * 2, center_radius/2)
        painter.drawText(unit_rect, Qt.AlignmentFlag.AlignCenter, self.unit)
        
        # Draw label below gauge
        if self.label_text:
            painter.setPen(QColor(158, 217, 207))
            label_font = QFont("Segoe UI", 10)
            painter.setFont(label_font)
            label_rect = QRectF(center_x - radius - 10, center_y + radius + 5, 
                               (radius + 10) * 2, 25)
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, self.label_text)


class StatCard(QFrame):
    """Glassmorphic stat card matching launcher aesthetic"""
    
    def __init__(self, title, value, max_value=100, unit="%", parent=None):
        super().__init__(parent)
        self.setProperty("class", "stat-card")
        self.setMinimumSize(220, 240)
        self.setMaximumSize(320, 300)
        
        # Apply styling
        self.setStyleSheet("""
            QFrame[class="stat-card"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 rgba(19, 79, 74, 0.9),
                                            stop:1 rgba(11, 46, 43, 0.9));
                border: 2px solid rgba(42, 245, 209, 0.5);
                border-radius: 15px;
                padding: 15px;
            }
            QFrame[class="stat-card"]:hover {
                border: 2px solid #21F5C1;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 rgba(19, 79, 74, 1),
                                            stop:1 rgba(11, 46, 43, 1));
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #9ED9CF;
                font-size: 11pt;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        # Parse value
        clean_value = self._parse_value(value)
        
        # Circular gauge
        self.gauge = CircularGauge(clean_value, max_value, "", unit)
        
        # Value label (backup display)
        self.value_label = QLabel(f"{int(clean_value)}{unit}")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("""
            QLabel {
                font-size: 14pt;
                font-weight: bold;
                color: #21F5C1;
                background: transparent;
            }
        """)
        self.value_label.setVisible(False)  # Hidden by default, gauge shows value
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.gauge, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
    
    def _parse_value(self, value):
        """Parse value - handles strings like '97%' or numbers"""
        if isinstance(value, str):
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
        """Update the gauge value with animation"""
        clean_value = self._parse_value(value)
        self.gauge.set_value(clean_value)
        # Update text label too (if visible)
        if hasattr(self, 'value_label') and hasattr(self.gauge, 'unit'):
            try:
                val = int(clean_value)
                self.value_label.setText(f"{val}{self.gauge.unit}")
            except (TypeError, ValueError):
                self.value_label.setText(str(value))


class StatusIndicator(QFrame):
    """Animated status indicator with glow"""
    
    def __init__(self, status="ready", parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 20)
        self.status = status
        self.glow_intensity = 0
        
        # Animation
        self.glow_animation = QPropertyAnimation(self, b"glow")
        self.glow_animation.setDuration(1000)
        self.glow_animation.setStartValue(0)
        self.glow_animation.setEndValue(100)
        self.glow_animation.setLoopCount(-1)  # Infinite
        self.glow_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.glow_animation.start()
    
    @pyqtProperty(int)
    def glow(self):
        return self.glow_intensity
    
    @glow.setter
    def glow(self, value):
        self.glow_intensity = value
        self.update()
    
    def set_status(self, status):
        """Update status: 'ready', 'success', 'warning', 'error', 'active'"""
        self.status = status
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Color based on status
        colors = {
            'ready': QColor(33, 245, 193),      # Teal
            'success': QColor(16, 185, 129),    # Green
            'warning': QColor(245, 158, 11),    # Orange
            'error': QColor(255, 77, 77),       # Red
            'active': QColor(59, 130, 246)      # Blue
        }
        
        base_color = colors.get(self.status, colors['ready'])
        
        # Outer glow (pulsing)
        glow_alpha = int(30 + (self.glow_intensity / 100) * 70)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(base_color.red(), base_color.green(), 
                                      base_color.blue(), glow_alpha)))
        painter.drawEllipse(2, 2, 16, 16)
        
        # Inner circle
        painter.setBrush(QBrush(base_color))
        painter.drawEllipse(5, 5, 10, 10)