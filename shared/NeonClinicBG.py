# shared/NeonClinicBG.py
import os
from pathlib import Path
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtCore import Qt

class NeonClinicBG(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.pixmap = None
        self.load_background()

    def load_background(self):
        # Get project root: shared/ → DiagAutoClinicOS/
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent
        img_path = project_root / "resources" / "bg" / "neon_clinic_bg.jpg"

        if img_path.exists():
            self.pixmap = QPixmap(str(img_path))
            if self.pixmap.isNull():
                print(f"[NeonClinicBG] Image loaded but null: {img_path}")
            else:
                print(f"[NeonClinicBG] Background loaded: {img_path}")
        else:
            print(f"[NeonClinicBG] Image NOT FOUND: {img_path}")
            self.pixmap = None

    def paintEvent(self, event):
        if not self.pixmap:
            return
        painter = QPainter(self)
        scaled = self.pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)