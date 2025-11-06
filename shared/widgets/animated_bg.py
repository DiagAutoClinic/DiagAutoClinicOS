#!/usr/bin/env python3
"""
Animated Neon Clinic Background - Light rays + pulse
Open-source ready
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QRadialGradient, QBrush, QColor, QPen
from PyQt6.QtCore import QTimer, QPointF, Qt
import math

class NeonClinicBG(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(40)

    def paintEvent(self, event):
        if self.width() < 100 or self.height() < 100:
            return
        
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        center = QPointF(self.width() / 2, self.height() / 2)

        # Pulsing core glow
        pulse = 0.8 + 0.2 * math.sin(self.angle * 0.08)
        core = QRadialGradient(center, 500 * pulse)
        core.setColorAt(0, QColor(0, 255, 170, 80))
        core.setColorAt(0.6, QColor(0, 212, 255, 40))
        core.setColorAt(1, QColor(0, 0, 0, 0))
        p.setBrush(core)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(center, 450 * pulse, 450 * pulse)

        # Rotating light rays
        for i in range(12):
            a = self.angle + i * 30
            x1 = center.x() + 200 * math.cos(math.radians(a))
            y1 = center.y() + 200 * math.sin(math.radians(a))
            x2 = center.x() + 1200 * math.cos(math.radians(a))
            y2 = center.y() + 1200 * math.sin(math.radians(a))
            
            ray = QRadialGradient(center, 800)
            ray.setColorAt(0, QColor(0, 212, 255, 60))
            ray.setColorAt(0.8, QColor(0, 255, 170, 20))
            ray.setColorAt(1, QColor(0, 0, 0, 0))
            
            pen = QPen(QBrush(ray), 4)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        self.angle += 1.2
