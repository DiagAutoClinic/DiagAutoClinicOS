# shared/animated_bg.py
"""
NeonClinicBG – animated background used by the launcher.
Uses a static image + a moving neon‑glow overlay.
"""

from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, pyqtProperty
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtWidgets import QWidget

from pathlib import Path


class NeonGlowOverlay(QWidget):
    """A tiny widget that paints a moving neon‑glow circle."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.radius = 120
        self._opacity = 0.0
        self.pos = QPoint(0, 0)

        # fade‑in / fade‑out animation
        self.anim = QPropertyAnimation(self, b"opacity")
        self.anim.setDuration(1800)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(0.35)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim.setLoopCount(-1)          # infinite
        self.anim.start()

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value: float):
        self._opacity = value
        self.update()

    def paintEvent(self, event):
        if self.opacity <= 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(0, 255, 200, int(self.opacity * 255))
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self.pos, self.radius, self.radius)


class NeonClinicBG(QWidget):
    """
    Full‑screen background:
      • static image (dacos_logo.png)
      • moving neon‑glow circle
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

        # ------------------------------------------------------------------
        # 1. Load the static image
        # ------------------------------------------------------------------
        img_path = Path(__file__).parent.parent / "assets" / "dacos_logo.png"
        if not img_path.exists():
            # fallback – a dark teal gradient
            self.bg_pix = None
        else:
            self.bg_pix = QPixmap(str(img_path)).scaled(
                1920, 1080, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )

        # ------------------------------------------------------------------
        # 2. Neon‑glow overlay
        # ------------------------------------------------------------------
        self.glow = NeonGlowOverlay(self)
        self.glow.resize(self.size())

        # move the glow in a smooth figure‑8 pattern
        self.glow_timer = QTimer(self)
        self.glow_timer.timeout.connect(self._move_glow)
        self.glow_timer.start(30)          # ~33 fps

        self.glow_phase = 0

    # ----------------------------------------------------------------------
    def _move_glow(self):
        """Figure‑8 motion – looks like a neon pulse scanning the car."""
        w, h = self.width(), self.height()
        self.glow_phase = (self.glow_phase + 3) % 360

        # parametric figure‑8 (Lissajous)
        cx, cy = w // 2, h // 2
        a, b = w * 0.35, h * 0.35
        x = cx + a * (self.glow_phase / 180 * 3.14159 * 2) % (2 * 3.14159)
        y = cy + b * (self.glow_phase / 90  * 3.14159 * 2) % (2 * 3.14159)

        self.glow.pos = QPoint(int(x), int(y))
        self.glow.update()

    # ----------------------------------------------------------------------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.bg_pix:
            self.bg_pix = self.bg_pix.scaled(
                self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
        self.glow.resize(self.size())

    # ----------------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. dark teal fallback
        painter.fillRect(self.rect(), QColor(10, 25, 40))

        # 2. static image (centered)
        if self.bg_pix:
            rect = self.bg_pix.rect()
            rect.moveCenter(self.rect().center())
            painter.drawPixmap(rect.topLeft(), self.bg_pix)

        # 3. the glow is painted by its own widget


# Alias for compatibility
AnimatedBackground = NeonClinicBG