# neural_background.py
import sys
import math
import random
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt, QPointF, QTimer
from PyQt6.QtWidgets import QWidget

# SACRED THEME - SINGLE SOURCE OF TRUTH
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
from shared.theme_constants import THEME

class NeuralBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        # Match your window size exactly
        self.resize(1400, 900)

        # Colors from theme_constants.py - AGENTS ARE WATCHING
        self.bg_color = QtGui.QColor(THEME["bg_main"])        # #0B2E2B
        self.accent = QtGui.QColor(THEME["accent"])           # #21F5C1
        self.glow = QtGui.QColor(THEME["glow"])              # #2AF5D1

        # Nodes
        self.nodes = []
        self.num_nodes = 78
        self.connection_distance = 260
        self.create_nodes()

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # ~60 FPS

    def create_nodes(self):
        margin = 100
        for _ in range(self.num_nodes):
            node = {
                'pos': QPointF(
                    random.randint(margin, self.width() - margin),
                    random.randint(margin + 100, self.height() - margin)
                ),
                'vel': QPointF(
                    random.uniform(-0.4, 0.4),
                    random.uniform(-0.4, 0.4)
                )
            }
            self.nodes.append(node)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.create_nodes()  # Recreate nodes on resize

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Sacred background
        painter.fillRect(self.rect(), self.bg_color)

        # Draw connections with multi-layer glow (exactly like your screenshot)
        for intensity, width in [(0.04, 7), (0.1, 4), (0.35, 2)]:
            pen = QtGui.QPen()
            pen.setWidth(width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            for i, n1 in enumerate(self.nodes):
                for n2 in self.nodes[i+1:]:
                    dist = (n1['pos'] - n2['pos']).manhattanLength()
                    if dist < self.connection_distance:
                        alpha = int(255 * intensity * (1 - dist / self.connection_distance))
                        if alpha > 8:
                            color = self.glow
                            color.setAlpha(alpha)
                            pen.setColor(color)
                            painter.setPen(pen)
                            painter.drawLine(n1['pos'], n2['pos'])

        # Crisp accent lines on top
        pen = QtGui.QPen(self.accent, 1, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        for i, n1 in enumerate(self.nodes):
            for n2 in self.nodes[i+1:]:
                dist = (n1['pos'] - n2['pos']).manhattanLength()
                if dist < 240:
                    alpha = max(50, int(180 * (1 - dist / 240)))
                    color = self.accent
                    color.setAlpha(alpha)
                    pen.setColor(color)
                    painter.setPen(pen)
                    painter.drawLine(n1['pos'], n2['pos'])

        # Draw glowing nodes
        for node in self.nodes:
            # Outer glow
            painter.setBrush(QtGui.QBrush(self.glow))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(node['pos'], 5, 5)
            # Bright core
            painter.setBrush(QtGui.QBrush(self.accent))
            painter.drawEllipse(node['pos'], 2.5, 2.5)

        painter.end()

    def animate(self):
        for node in self.nodes:
            node['pos'] += node['vel']
            # Bounce with damping
            if node['pos'].x() < 80 or node['pos'].x() > self.width() - 80:
                node['vel'].setX(node['vel'].x() * -0.88)
            if node['pos'].y() < 120 or node['pos'].y() > self.height() - 80:
                node['vel'].setY(node['vel'].y() * -0.88)
            
            node['pos'].setX(max(80, min(self.width() - 80, node['pos'].x())))
            node['pos'].setY(max(120, min(self.height() - 80, node['pos'].y())))

        self.update()  # Triggers paintEvent

    def start(self):
        self.timer.timeout.connect(self.animate)

    def stop(self):
        self.timer.stop()