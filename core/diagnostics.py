#!/usr/bin/env python3
"""
Diagnostics Module for AutoDiag Pro
Handles VIN reading, DTC reading, and DTC clearing
"""

import struct
import logging
import sys
import os

# Add project root to Python path to enable imports from shared directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)

# Import shared modules
try:
    from shared.dtc_database import DTCDatabase
    from shared.vin_decoder import VINDecoder
    DTC_DATABASE_AVAILABLE = True
    VIN_DECODER_AVAILABLE = True
except ImportError:
    DTC_DATABASE_AVAILABLE = False
    VIN_DECODER_AVAILABLE = False
    logger.warning("DTC database or VIN decoder not available, using fallbacks")


class DiagnosticsManager:
    """Manages diagnostic operations like VIN reading and DTC handling"""

    def __init__(self, device_manager, ai_engine=None):
        self.device_manager = device_manager
        self.dtc_database = DTCDatabase() if DTC_DATABASE_AVAILABLE else None
        self.vin_decoder = VINDecoder() if VIN_DECODER_AVAILABLE else None
        self.ai_engine = ai_engine  # AI engine integration

    def read_vin(self, parent_window):
        """Read the VIN from the identified ECU."""
        if not self.device_manager.ecu_identified or not self.device_manager.j2534_handle:
            QMessageBox.warning(parent_window, "VIN Read Error", "ECU not identified or device not connected.")
            return

        try:
            # Send VIN Read Request (KWP2000 0x1A 0x90)
            vin_request = b'\x1A\x90'
            vin_response = self.device_manager._send_vw_kwp_command(vin_request)

            # Check for positive response header (0x5A 0x90)
            if len(vin_response) >= 3 and vin_response[:2] == b'\x5A\x90':
                # Extract VIN (usually starts from byte 3, length 17 for standard VIN)
                raw_vin_bytes = vin_response[2:2+17]  # Adjust range based on actual response format
                # Decode VIN, removing padding characters (often 0x00 or space)
                raw_vin_string = raw_vin_bytes.decode('ascii', errors='ignore').rstrip('\x00 \x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F')
                if len(raw_vin_string) >= 17:
                    vin = raw_vin_string
                    if self.vin_decoder:
                        decoded_vin_info = self.vin_decoder.decode(vin)

                        if decoded_vin_info.get('error'):
                            QMessageBox.critical(parent_window, "VIN Read Error", f"Failed to decode VIN: {decoded_vin_info['error']}")
                        else:
                            QMessageBox.information(parent_window, "VIN Read Success", f"VIN: {vin}\nDecoded: {decoded_vin_info}")
                    else:
                        QMessageBox.information(parent_window, "VIN Read Success", f"VIN: {vin}")
                else:
                    QMessageBox.critical(parent_window, "VIN Read Error", f"Received invalid VIN length: {len(raw_vin_string)}")
            else:
                QMessageBox.critical(parent_window, "VIN Read Error", f"ECU returned error: {vin_response.hex()}")

        except Exception as e:
            QMessageBox.critical(parent_window, "VIN Read Error", f"Failed to communicate: {str(e)}")
            logger.error(f"Exception during VIN read: {e}")

    def read_dtcs(self, parent_window):
        """Read DTCs from the identified ECU."""
        if not self.device_manager.ecu_identified or not self.device_manager.j2534_handle:
            QMessageBox.warning(parent_window, "DTC Read Error", "ECU not identified or device not connected.")
            return

        try:
            # Send DTC Read Request (KWP2000 0x17 0x00 - Read Status Of DTCs, All DTCs)
            dtc_request = b'\x17\x00'
            dtc_response = self.device_manager._send_vw_kwp_command(dtc_request)

            # Check for positive response header (0x57 0x00)
            if len(dtc_response) >= 2 and dtc_response[:2] == b'\x57\x00':
                # Parse DTCs from the response
                # The format is typically: [Header] [DTC Code (2 bytes)] [Status Byte] [DTC Code] [Status] ...
                # This is a simplified parser. Real parsing requires understanding the exact byte structure per OBD/KWP standard.
                raw_dtcs = dtc_response[2:]  # Remove header
                dtc_list = []
                i = 0
                while i < len(raw_dtcs) - 2:  # Need at least 3 bytes for DTC + Status
                    dtc_code_bytes = raw_dtcs[i:i+2]
                    status_byte = raw_dtcs[i+2]
                    i += 3  # Move to next DTC

                    # Convert 2-byte DTC code to string (e.g., 0x01 0x34 -> P0134)
                    dtc_code = struct.unpack('>H', dtc_code_bytes)[0]  # Big-endian unsigned short
                    dtc_str = f"P{dtc_code:04X}"  # Format as PXXXX

                    # Determine status from status_byte (simplified)
                    # Common bits: Bit 0 = Test Failed, Bit 7 = Confirmed DTC
                    status = "Active"
                    if status_byte & 0x01:  # Bit 0 set
                        status = "Pending"
                    if status_byte & 0x80:  # Bit 7 set
                        status = "Active/Confirmed"

                    dtc_list.append({'code': dtc_str, 'status': status})

                if dtc_list:
                    dtc_text = "Active DTCs:\n"
                    for dtc in dtc_list:
                        # Get description from database
                        if self.dtc_database:
                            dtc_info = self.dtc_database.get_dtc_info(dtc['code'])
                            description = dtc_info.get('description', 'Unknown DTC')
                            severity = dtc_info.get('severity', 'Unknown')
                        else:
                            description = 'Unknown DTC'
                            severity = 'Unknown'
                        dtc_text += f"{dtc['code']}: {description} (Status: {dtc['status']}, Severity: {severity})\n"
                    QMessageBox.information(parent_window, "DTC Read Success", dtc_text)
                else:
                    QMessageBox.information(parent_window, "DTC Read Success", "No active DTCs found.")

            else:
                QMessageBox.critical(parent_window, "DTC Read Error", f"ECU returned error: {dtc_response.hex()}")

        except Exception as e:
            QMessageBox.critical(parent_window, "DTC Read Error", f"Failed to communicate: {str(e)}")
            logger.error(f"Exception during DTC read: {e}")

    def clear_dtcs(self, parent_window):
        """Clear DTCs from the identified ECU."""
        if not self.device_manager.ecu_identified or not self.device_manager.j2534_handle:
            QMessageBox.warning(parent_window, "DTC Clear Error", "ECU not identified or device not connected.")
            return

        reply = QMessageBox.question(parent_window, "Confirm Clear DTCs",
                                   "Are you sure you want to clear all DTCs?\nThis action cannot be undone.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Send DTC Clear Request (KWP2000 0x18 0x00 - Clear Diagnostic Information)
                clear_request = b'\x18\x00'
                clear_response = self.device_manager._send_vw_kwp_command(clear_request)

                # Check for positive response header (0x58 0x00)
                if clear_response[:2] == b'\x58\x00':
                    QMessageBox.information(parent_window, "DTC Clear Success", "DTCs cleared successfully.")
                else:
                    QMessageBox.critical(parent_window, "DTC Clear Error", f"ECU returned error: {clear_response.hex()}")

            except Exception as e:
                QMessageBox.critical(parent_window, "DTC Clear Error", f"Failed to communicate: {str(e)}")
                logger.error(f"Exception during DTC clear: {e}")