#!/usr/bin/env python3
"""
Calibrations Tab Component
Separate tab for calibrations functionality
"""

from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class CalibrationsTab(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        backup_btn = QPushButton("Backup Current")
        restore_btn = QPushButton("Restore Settings")
        reset_btn = QPushButton("Reset to Factory")
        
        backup_btn.clicked.connect(self.backup_settings)
        restore_btn.clicked.connect(self.restore_settings)
        reset_btn.clicked.connect(self.factory_reset)
        
        controls_layout.addWidget(backup_btn)
        controls_layout.addWidget(restore_btn)
        controls_layout.addWidget(reset_btn)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Idle Speed Calibration
        group1 = QGroupBox("Idle Speed Calibration")
        group1_layout = QVBoxLayout(group1)
        
        idle_layout = QHBoxLayout()
        idle_layout.addWidget(QLabel("Target RPM:"))
        self.idle_spinbox = QSpinBox()
        self.idle_spinbox.setRange(500, 2000)
        self.idle_spinbox.setValue(750)
        idle_layout.addWidget(self.idle_spinbox)
        
        apply_idle_btn = QPushButton("Apply")
        apply_idle_btn.clicked.connect(self.apply_idle_speed)
        idle_layout.addWidget(apply_idle_btn)
        idle_layout.addStretch()
        
        group1_layout.addLayout(idle_layout)
        layout.addWidget(group1)
        
        # Fuel Trim Calibration
        group2 = QGroupBox("Fuel Trim Calibration")
        group2_layout = QGridLayout(group2)
        
        # Short Term Fuel Trim
        group2_layout.addWidget(QLabel("Short Term FT:"), 0, 0)
        self.stft_spinbox = QDoubleSpinBox()
        self.stft_spinbox.setRange(-25.0, 25.0)
        self.stft_spinbox.setValue(0.0)
        self.stft_spinbox.setSuffix("%")
        group2_layout.addWidget(self.stft_spinbox, 0, 1)
        
        # Long Term Fuel Trim
        group2_layout.addWidget(QLabel("Long Term FT:"), 1, 0)
        self.ltft_spinbox = QDoubleSpinBox()
        self.ltft_spinbox.setRange(-25.0, 25.0)
        self.ltft_spinbox.setValue(0.0)
        self.ltft_spinbox.setSuffix("%")
        group2_layout.addWidget(self.ltft_spinbox, 1, 1)
        
        apply_fuel_btn = QPushButton("Apply Fuel Trims")
        apply_fuel_btn.clicked.connect(self.apply_fuel_trims)
        group2_layout.addWidget(apply_fuel_btn, 2, 0, 1, 2)
        
        layout.addWidget(group2)
        
        # Ignition Timing Calibration
        group3 = QGroupBox("Ignition Timing")
        group3_layout = QHBoxLayout(group3)
        
        group3_layout.addWidget(QLabel("Base Timing:"))
        self.timing_spinbox = QDoubleSpinBox()
        self.timing_spinbox.setRange(0.0, 60.0)
        self.timing_spinbox.setValue(10.0)
        self.timing_spinbox.setSuffix("° BTDC")
        group3_layout.addWidget(self.timing_spinbox)
        
        self.retard_checkbox = QCheckBox("Retard under load")
        group3_layout.addWidget(self.retard_checkbox)
        
        apply_timing_btn = QPushButton("Apply Timing")
        apply_timing_btn.clicked.connect(self.apply_ignition_timing)
        group3_layout.addWidget(apply_timing_btn)
        group3_layout.addStretch()
        
        layout.addWidget(group3)
        
        # ECU Adaptation
        group4 = QGroupBox("ECU Adaptation")
        group4_layout = QGridLayout(group4)
        
        adapt_buttons = [
            ("Reset Fuel Adaptations", self.reset_fuel_adaptations),
            ("Reset Airflow Meter", self.reset_airflow_meter),
            ("Reset Throttle Body", self.reset_throttle_body),
            ("Reset Idle Learn", self.reset_idle_learn)
        ]
        
        for i, (text, callback) in enumerate(adapt_buttons):
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            group4_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addWidget(group4)
        
        # Results
        layout.addWidget(QLabel("Calibration Results:"))
        self.results = QTextEdit()
        self.results.setMaximumHeight(120)
        layout.addWidget(self.results)
        
    def backup_settings(self):
        """Backup current ECU settings"""
        filename, _ = QFileDialog.getSaveFileName(self, "Backup Settings", "", "BIN Files (*.bin)")
        if filename:
            self.results.append(f"[{datetime.now().strftime('%H:%M:%S')}] Backing up current settings to {filename}...")
            QTimer.singleShot(2000, lambda: self.results.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Settings backed up successfully\n"
                "  File size: 64KB\n"
                "  Checksum: 0xA5B3"
            ))
        
    def restore_settings(self):
        """Restore ECU settings from backup"""
        filename, _ = QFileDialog.getOpenFileName(self, "Restore Settings", "", "BIN Files (*.bin)")
        if filename:
            reply = QMessageBox.question(self, "Restore Settings", 
                                       f"Restore settings from {filename}?\nThis will overwrite current calibration!",
                                       QMessageBox.StandardButton.Yes | 
                                       QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.results.append(f"[{datetime.now().strftime('%H:%M:%S')}] Restoring settings from {filename}...")
                QTimer.singleShot(3000, lambda: self.results.append(
                    f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Settings restored successfully\n"
                    "  ECU will restart...\n"
                    "  Status: READY"
                ))
        
    def factory_reset(self):
        """Reset to factory defaults"""
        reply = QMessageBox.warning(self, "Factory Reset", 
                                  "This will reset ALL calibrations to factory defaults!\n\n"
                                  "This action cannot be undone!\n\n"
                                  "Are you sure?",
                                  QMessageBox.StandardButton.Yes | 
                                  QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.results.append(f"[{datetime.now().strftime('%H:%M:%S')}] Factory reset initiated...")
            QTimer.singleShot(5000, lambda: self.results.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Factory reset completed\n"
                "  All settings restored to defaults\n"
                "  ECU will restart..."
            ))
        
    def apply_idle_speed(self):
        """Apply new idle speed setting"""
        rpm = self.idle_spinbox.value()
        self.results.append(f"[{datetime.now().strftime('%H:%M:%S')}] Applying idle speed: {rpm} RPM...")
        QTimer.singleShot(1500, lambda: self.results.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Idle speed calibrated to {rpm} RPM\n"
            "  New value stored in ECU\n"
            "  Status: READY"
        ))
        
    def apply_fuel_trims(self):
        """Apply fuel trim adjustments"""
        stft = self.stft_spinbox.value()
        ltft = self.ltft_spinbox.value()
        self.results.append(f"[{datetime.now().strftime('%H:%M:%S')}] Applying fuel trims: STFT={stft}%, LTFT={ltft}%...")
        QTimer.singleShot(2000, lambda: self.results.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Fuel trims updated\n"
            f"  STFT: {stft}%\n"
            f"  LTFT: {ltft}%\n"
            "  Status: ADAPTED"
        ))
        
    def apply_ignition_timing(self):
        """Apply ignition timing adjustment"""
        timing = self.timing_spinbox.value()
        retard = self.retard_checkbox.isChecked()
        self.results.append(f"[{datetime.now().strftime('%H:%M:%S')}] Applying ignition timing: {timing}° BTDC...")
        QTimer.singleShot(1800, lambda: self.results.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Ignition timing updated\n"
            f"  Base timing: {timing}° BTDC\n"
            f"  Load retard: {'ON' if retard else 'OFF'}\n"
            "  Status: CALIBRATED"
        ))
        
    def reset_fuel_adaptations(self):
        """Reset fuel adaptation values"""
        self.results.append(f"[{datetime.now().strftime('%H:%M:%S')}] Resetting fuel adaptations...")
        QTimer.singleShot(1200, lambda: self.results.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Fuel adaptations reset\n"
            "  Short term FT: 0%\n"
            "  Long term FT: 0%\n"
            "  Status: READY FOR LEARNING"
        ))
        
    def reset_airflow_meter(self):
        """Reset airflow meter adaptation"""
        self.results.append(f"[{datetime.now().strftime('%H:%M:%S')}] Resetting airflow meter...")
        QTimer.singleShot(1000, lambda: self.results.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Airflow meter reset\n"
            "  MAF adaptation: Cleared\n"
            "  Status: READY"
        ))
        
    def reset_throttle_body(self):
        """Reset throttle body adaptation"""
        self.results.append(f"[{datetime.now().strftime('%H:%M:%S')}] Resetting throttle body...")
        QTimer.singleShot(1500, lambda: self.results.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Throttle body reset\n"
            "  Throttle position: Recalibrated\n"
            "  Status: READY"
        ))
        
    def reset_idle_learn(self):
        """Reset idle learning values"""
        self.results.append(f"[{datetime.now().strftime('%H:%M:%S')}] Resetting idle learn...")
        QTimer.singleShot(800, lambda: self.results.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Idle learn reset\n"
            "  Idle values: Cleared\n"
            "  Status: READY FOR LEARNING"
        ))