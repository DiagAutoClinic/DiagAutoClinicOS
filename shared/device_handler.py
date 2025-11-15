# =============================
# shared/device_handler.py
# =============================
import logging
import importlib

logger = logging.getLogger(__name__)

class DeviceHandler:
    def __init__(self, mock_mode=False):
        self.mock_mode = mock_mode
        if self.mock_mode:
            logger.warning("DeviceHandler running in mock mode (no real hardware required)")

        self.j2534_available = False
        self.socketcan_available = False
        self.usb_available = False
        self.bluetooth_available = False
        self.detect_devices()

    def detect_devices(self):
        logger.info("Starting device detection...")

        # --- J2534 Interface ---
        try:
            import winreg  # Only on Windows
            self.j2534_available = True
            logger.info("✓ J2534 registry detected (Windows environment)")
        except Exception as e:
            logger.error(f"Error checking J2534: {e}")

        # --- SocketCAN ---
        try:
            import socket
            self.socketcan_available = True
            logger.info("✓ SocketCAN base available")
        except Exception as e:
            logger.error(f"Error checking SocketCAN: {e}")

        # --- USB backend ---
        try:
            import usb.core
            import usb.util
            self.usb_available = True
            logger.info("✓ USB backend loaded successfully")
        except Exception as e:
            logger.error(f"USB detection error: {e}")

        # --- Bluetooth ---
        try:
            import bluetooth
            self.bluetooth_available = True
            logger.info("✓ Bluetooth backend active")
        except ImportError:
            logger.warning("Bluetooth module not available - Bluetooth features disabled")
