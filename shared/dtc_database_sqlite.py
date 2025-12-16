#!/usr/bin/env python3
"""
DiagAutoClinicOS - DTC Database (SQLite Version)
Professional diagnostic trouble code database with SQLite backend
"""

import sqlite3
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class DTCDatabaseSQLite:
    """SQLite-based DTC database"""

    def __init__(self, db_path: str = "diagautoclinic_dtc.db"):
        """
        Initialize DTC database with SQLite connection
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize the database and create tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create dtc_codes table if it doesn't exist
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS dtc_codes (
                        code TEXT PRIMARY KEY,
                        description TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        category TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Create index for better search performance
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_dtc_search 
                    ON dtc_codes(description)
                ''')

                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_dtc_code 
                    ON dtc_codes(code)
                ''')

                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_dtc_severity 
                    ON dtc_codes(severity)
                ''')

                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_dtc_category 
                    ON dtc_codes(category)
                ''')

                conn.commit()

                # Populate with base data if table is empty
                cursor.execute('SELECT COUNT(*) FROM dtc_codes')
                count = cursor.fetchone()[0]

                if count == 0:
                    self._populate_base_data()

                logger.info("DTC database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize DTC database: {e}")
            raise

    def _populate_base_data(self):
        """Populate with base DTC data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                base_dtcs = [
                    ('P0300', 'Random/Multiple Cylinder Misfire Detected', 'High', 'Powertrain'),
                    ('P0171', 'System Too Lean (Bank 1)', 'Medium', 'Powertrain'),
                    ('U0100', 'Lost Communication With ECU', 'High', 'Network'),
                    ('B1000', 'ECU Malfunction', 'Critical', 'Body'),
                    ('C1201', 'ABS System Malfunction', 'High', 'Chassis'),
                    ('P0217', 'Engine Overtemperature', 'Critical', 'Powertrain'),
                    ('P0420', 'Catalyst System Efficiency Below Threshold', 'Medium', 'Powertrain'),
                ]

                cursor.executemany('''
                    INSERT INTO dtc_codes (code, description, severity, category)
                    VALUES (?, ?, ?, ?)
                ''', base_dtcs)

                conn.commit()
                logger.info(f"Populated {len(base_dtcs)} base DTC codes into database")

        except Exception as e:
            logger.error(f"Failed to populate base DTC data: {e}")

    def get_dtc_info(self, code: str) -> Dict:
        """Return DTC information for a given code"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT description, severity, category FROM dtc_codes WHERE code = ?
                ''', (code.upper(),))

                result = cursor.fetchone()
                if result:
                    return {
                        'description': result[0],
                        'severity': result[1],
                        'category': result[2]
                    }
                return {
                    'description': 'Unknown DTC Code',
                    'severity': 'Unknown',
                    'category': 'Unknown'
                }

        except Exception as e:
            logger.error(f"Error querying DTC info: {e}")
            return {
                'description': 'Unknown DTC Code',
                'severity': 'Unknown',
                'category': 'Unknown'
            }

    def search_dtcs(self, search_term: str) -> List[Tuple]:
        """Search DTCs by code or description and return matches"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT code, description, severity, category
                    FROM dtc_codes
                    WHERE code LIKE ? OR description LIKE ?
                    ORDER BY code
                ''', (f'%{search_term}%', f'%{search_term}%'))

                return cursor.fetchall()

        except Exception as e:
            logger.error(f"Error searching DTCs: {e}")
            return []

    def add_dtc(self, code: str, description: str, severity: str, category: str) -> bool:
        """Add a new DTC to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO dtc_codes (code, description, severity, category)
                    VALUES (?, ?, ?, ?)
                ''', (code.upper(), description, severity, category))
                conn.commit()
                return True

        except Exception as e:
            logger.error(f"Error adding DTC: {e}")
            return False

    def update_dtc(self, code: str, description: Optional[str] = None, severity: Optional[str] = None, category: Optional[str] = None) -> bool:
        """Update an existing DTC"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Build update query dynamically
                updates = []
                params = []

                if description:
                    updates.append("description = ?")
                    params.append(description)
                if severity:
                    updates.append("severity = ?")
                    params.append(severity)
                if category:
                    updates.append("category = ?")
                    params.append(category)

                if not updates:
                    return False

                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(code.upper())

                query = f"UPDATE dtc_codes SET {', '.join(updates)} WHERE code = ?"
                cursor.execute(query, params)
                conn.commit()

                return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Error updating DTC: {e}")
            return False

    def delete_dtc(self, code: str) -> bool:
        """Delete a DTC from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM dtc_codes WHERE code = ?', (code.upper(),))
                conn.commit()
                return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Error deleting DTC: {e}")
            return False

    def get_all_dtcs(self) -> List[Tuple]:
        """Get all DTCs from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT code, description, severity, category
                    FROM dtc_codes
                    ORDER BY code
                ''')
                return cursor.fetchall()

        except Exception as e:
            logger.error(f"Error getting all DTCs: {e}")
            return []

    def get_dtc_count(self) -> int:
        """Get the total number of DTCs in the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM dtc_codes')
                return cursor.fetchone()[0]

        except Exception as e:
            logger.error(f"Error getting DTC count: {e}")
            return 0

    def get_dtcs_by_severity(self, severity: str) -> List[Tuple]:
        """Get DTCs by severity level"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT code, description, severity, category
                    FROM dtc_codes
                    WHERE severity = ?
                    ORDER BY code
                ''', (severity,))
                return cursor.fetchall()

        except Exception as e:
            logger.error(f"Error getting DTCs by severity: {e}")
            return []

    def get_dtcs_by_category(self, category: str) -> List[Tuple]:
        """Get DTCs by category"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT code, description, severity, category
                    FROM dtc_codes
                    WHERE category = ?
                    ORDER BY code
                ''', (category,))
                return cursor.fetchall()

        except Exception as e:
            logger.error(f"Error getting DTCs by category: {e}")
            return []

    def populate_enhanced_data(self):
        """Populate with comprehensive DTC data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check current count
                cursor.execute('SELECT COUNT(*) FROM dtc_codes')
                current_count = cursor.fetchone()[0]

                if current_count > 10:  # Already has enhanced data
                    return

                # Comprehensive DTC list
                enhanced_dtcs = [
                    # Powertrain DTCs
                    ('P0100', 'Mass or Volume Air Flow Circuit Malfunction', 'Medium', 'Powertrain'),
                    ('P0101', 'Mass or Volume Air Flow Circuit Range/Performance Problem', 'Medium', 'Powertrain'),
                    ('P0102', 'Mass or Volume Air Flow Circuit Low Input', 'Medium', 'Powertrain'),
                    ('P0103', 'Mass or Volume Air Flow Circuit High Input', 'Medium', 'Powertrain'),
                    ('P0104', 'Mass or Volume Air Flow Circuit Intermittent', 'Medium', 'Powertrain'),
                    ('P0105', 'Manifold Absolute Pressure/Barometric Pressure Circuit Malfunction', 'Medium', 'Powertrain'),
                    ('P0106', 'Manifold Absolute Pressure/Barometric Pressure Circuit Range/Performance Problem', 'Medium', 'Powertrain'),
                    ('P0107', 'Manifold Absolute Pressure/Barometric Pressure Circuit Low Input', 'Medium', 'Powertrain'),
                    ('P0108', 'Manifold Absolute Pressure/Barometric Pressure Circuit High Input', 'Medium', 'Powertrain'),
                    ('P0109', 'Manifold Absolute Pressure/Barometric Pressure Circuit Intermittent', 'Medium', 'Powertrain'),
                    ('P0110', 'Intake Air Temperature Circuit Malfunction', 'Low', 'Powertrain'),
                    ('P0111', 'Intake Air Temperature Circuit Range/Performance Problem', 'Low', 'Powertrain'),
                    ('P0112', 'Intake Air Temperature Circuit Low Input', 'Low', 'Powertrain'),
                    ('P0113', 'Intake Air Temperature Circuit High Input', 'Low', 'Powertrain'),
                    ('P0114', 'Intake Air Temperature Circuit Intermittent', 'Low', 'Powertrain'),
                    ('P0115', 'Engine Coolant Temperature Circuit Malfunction', 'Medium', 'Powertrain'),
                    ('P0116', 'Engine Coolant Temperature Circuit Range/Performance Problem', 'Medium', 'Powertrain'),
                    ('P0117', 'Engine Coolant Temperature Circuit Low Input', 'Medium', 'Powertrain'),
                    ('P0118', 'Engine Coolant Temperature Circuit High Input', 'Medium', 'Powertrain'),
                    ('P0119', 'Engine Coolant Temperature Circuit Intermittent', 'Medium', 'Powertrain'),
                    ('P0120', 'Throttle/Pedal Position Sensor/Switch A Circuit Malfunction', 'High', 'Powertrain'),
                    ('P0121', 'Throttle/Pedal Position Sensor/Switch A Circuit Range/Performance Problem', 'High', 'Powertrain'),
                    ('P0122', 'Throttle/Pedal Position Sensor/Switch A Circuit Low Input', 'High', 'Powertrain'),
                    ('P0123', 'Throttle/Pedal Position Sensor/Switch A Circuit High Input', 'High', 'Powertrain'),
                    ('P0124', 'Throttle/Pedal Position Sensor/Switch A Circuit Intermittent', 'High', 'Powertrain'),
                    ('P0125', 'Insufficient Coolant Temperature for Closed Loop Fuel Control', 'Medium', 'Powertrain'),
                    ('P0126', 'Insufficient Coolant Temperature for Stable Operation', 'Medium', 'Powertrain'),
                    ('P0130', 'O2 Sensor Circuit Malfunction (Bank 1 Sensor 1)', 'Medium', 'Powertrain'),
                    ('P0131', 'O2 Sensor Circuit Low Voltage (Bank 1 Sensor 1)', 'Medium', 'Powertrain'),
                    ('P0132', 'O2 Sensor Circuit High Voltage (Bank 1 Sensor 1)', 'Medium', 'Powertrain'),
                    ('P0133', 'O2 Sensor Circuit Slow Response (Bank 1 Sensor 1)', 'Medium', 'Powertrain'),
                    ('P0134', 'O2 Sensor Circuit No Activity Detected (Bank 1 Sensor 1)', 'Medium', 'Powertrain'),
                    ('P0135', 'O2 Sensor Heater Circuit Malfunction (Bank 1 Sensor 1)', 'Low', 'Powertrain'),
                    ('P0136', 'O2 Sensor Circuit Malfunction (Bank 1 Sensor 2)', 'Medium', 'Powertrain'),
                    ('P0137', 'O2 Sensor Circuit Low Voltage (Bank 1 Sensor 2)', 'Medium', 'Powertrain'),
                    ('P0138', 'O2 Sensor Circuit High Voltage (Bank 1 Sensor 2)', 'Medium', 'Powertrain'),
                    ('P0139', 'O2 Sensor Circuit Slow Response (Bank 1 Sensor 2)', 'Medium', 'Powertrain'),
                    ('P0140', 'O2 Sensor Circuit No Activity Detected (Bank 1 Sensor 2)', 'Medium', 'Powertrain'),
                    ('P0141', 'O2 Sensor Heater Circuit Malfunction (Bank 1 Sensor 2)', 'Low', 'Powertrain'),
                    ('P0142', 'O2 Sensor Circuit Malfunction (Bank 1 Sensor 3)', 'Medium', 'Powertrain'),
                    ('P0143', 'O2 Sensor Circuit Low Voltage (Bank 1 Sensor 3)', 'Medium', 'Powertrain'),
                    ('P0144', 'O2 Sensor Circuit High Voltage (Bank 1 Sensor 3)', 'Medium', 'Powertrain'),
                    ('P0145', 'O2 Sensor Circuit Slow Response (Bank 1 Sensor 3)', 'Medium', 'Powertrain'),
                    ('P0146', 'O2 Sensor Circuit No Activity Detected (Bank 1 Sensor 3)', 'Medium', 'Powertrain'),
                    ('P0147', 'O2 Sensor Heater Circuit Malfunction (Bank 1 Sensor 3)', 'Low', 'Powertrain'),
                    ('P0150', 'O2 Sensor Circuit Malfunction (Bank 2 Sensor 1)', 'Medium', 'Powertrain'),
                    ('P0151', 'O2 Sensor Circuit Low Voltage (Bank 2 Sensor 1)', 'Medium', 'Powertrain'),
                    ('P0152', 'O2 Sensor Circuit High Voltage (Bank 2 Sensor 1)', 'Medium', 'Powertrain'),
                    ('P0153', 'O2 Sensor Circuit Slow Response (Bank 2 Sensor 1)', 'Medium', 'Powertrain'),
                    ('P0154', 'O2 Sensor Circuit No Activity Detected (Bank 2 Sensor 1)', 'Medium', 'Powertrain'),
                    ('P0155', 'O2 Sensor Heater Circuit Malfunction (Bank 2 Sensor 1)', 'Low', 'Powertrain'),
                    ('P0156', 'O2 Sensor Circuit Malfunction (Bank 2 Sensor 2)', 'Medium', 'Powertrain'),
                    ('P0157', 'O2 Sensor Circuit Low Voltage (Bank 2 Sensor 2)', 'Medium', 'Powertrain'),
                    ('P0158', 'O2 Sensor Circuit High Voltage (Bank 2 Sensor 2)', 'Medium', 'Powertrain'),
                    ('P0159', 'O2 Sensor Circuit Slow Response (Bank 2 Sensor 2)', 'Medium', 'Powertrain'),
                    ('P0160', 'O2 Sensor Circuit No Activity Detected (Bank 2 Sensor 2)', 'Medium', 'Powertrain'),
                    ('P0161', 'O2 Sensor Heater Circuit Malfunction (Bank 2 Sensor 2)', 'Low', 'Powertrain'),
                    ('P0162', 'O2 Sensor Circuit Malfunction (Bank 2 Sensor 3)', 'Medium', 'Powertrain'),
                    ('P0163', 'O2 Sensor Circuit Low Voltage (Bank 2 Sensor 3)', 'Medium', 'Powertrain'),
                    ('P0164', 'O2 Sensor Circuit High Voltage (Bank 2 Sensor 3)', 'Medium', 'Powertrain'),
                    ('P0165', 'O2 Sensor Circuit Slow Response (Bank 2 Sensor 3)', 'Medium', 'Powertrain'),
                    ('P0166', 'O2 Sensor Circuit No Activity Detected (Bank 2 Sensor 3)', 'Medium', 'Powertrain'),
                    ('P0167', 'O2 Sensor Heater Circuit Malfunction (Bank 2 Sensor 3)', 'Low', 'Powertrain'),
                    ('P0170', 'Fuel Trim Malfunction (Bank 1)', 'Medium', 'Powertrain'),
                    ('P0171', 'System Too Lean (Bank 1)', 'Medium', 'Powertrain'),
                    ('P0172', 'System Too Rich (Bank 1)', 'Medium', 'Powertrain'),
                    ('P0173', 'Fuel Trim Malfunction (Bank 2)', 'Medium', 'Powertrain'),
                    ('P0174', 'System Too Lean (Bank 2)', 'Medium', 'Powertrain'),
                    ('P0175', 'System Too Rich (Bank 2)', 'Medium', 'Powertrain'),
                    ('P0176', 'Fuel Composition Sensor Circuit Malfunction', 'Medium', 'Powertrain'),
                    ('P0177', 'Fuel Composition Sensor Circuit Range/Performance', 'Medium', 'Powertrain'),
                    ('P0178', 'Fuel Composition Sensor Circuit Low Input', 'Medium', 'Powertrain'),
                    ('P0179', 'Fuel Composition Sensor Circuit High Input', 'Medium', 'Powertrain'),
                    ('P0180', 'Fuel Temperature Sensor A Circuit Malfunction', 'Low', 'Powertrain'),
                    ('P0181', 'Fuel Temperature Sensor A Circuit Range/Performance', 'Low', 'Powertrain'),
                    ('P0182', 'Fuel Temperature Sensor A Circuit Low Input', 'Low', 'Powertrain'),
                    ('P0183', 'Fuel Temperature Sensor A Circuit High Input', 'Low', 'Powertrain'),
                    ('P0184', 'Fuel Temperature Sensor A Circuit Intermittent', 'Low', 'Powertrain'),
                    ('P0185', 'Fuel Temperature Sensor B Circuit Malfunction', 'Low', 'Powertrain'),
                    ('P0186', 'Fuel Temperature Sensor B Circuit Range/Performance', 'Low', 'Powertrain'),
                    ('P0187', 'Fuel Temperature Sensor B Circuit Low Input', 'Low', 'Powertrain'),
                    ('P0188', 'Fuel Temperature Sensor B Circuit High Input', 'Low', 'Powertrain'),
                    ('P0189', 'Fuel Temperature Sensor B Circuit Intermittent', 'Low', 'Powertrain'),
                    ('P0190', 'Fuel Rail Pressure Sensor Circuit Malfunction', 'High', 'Powertrain'),
                    ('P0191', 'Fuel Rail Pressure Sensor Circuit Range/Performance', 'High', 'Powertrain'),
                    ('P0192', 'Fuel Rail Pressure Sensor Circuit Low Input', 'High', 'Powertrain'),
                    ('P0193', 'Fuel Rail Pressure Sensor Circuit High Input', 'High', 'Powertrain'),
                    ('P0194', 'Fuel Rail Pressure Sensor Circuit Intermittent', 'High', 'Powertrain'),
                    ('P0195', 'Engine Oil Temperature Sensor Malfunction', 'Low', 'Powertrain'),
                    ('P0196', 'Engine Oil Temperature Sensor Range/Performance', 'Low', 'Powertrain'),
                    ('P0197', 'Engine Oil Temperature Sensor Low Input', 'Low', 'Powertrain'),
                    ('P0198', 'Engine Oil Temperature Sensor High Input', 'Low', 'Powertrain'),
                    ('P0199', 'Engine Oil Temperature Sensor Intermittent', 'Low', 'Powertrain'),
                    ('P0200', 'Injector Circuit Malfunction', 'High', 'Powertrain'),
                    ('P0201', 'Injector Circuit Malfunction - Cylinder 1', 'High', 'Powertrain'),
                    ('P0202', 'Injector Circuit Malfunction - Cylinder 2', 'High', 'Powertrain'),
                    ('P0203', 'Injector Circuit Malfunction - Cylinder 3', 'High', 'Powertrain'),
                    ('P0204', 'Injector Circuit Malfunction - Cylinder 4', 'High', 'Powertrain'),
                    ('P0205', 'Injector Circuit Malfunction - Cylinder 5', 'High', 'Powertrain'),
                    ('P0206', 'Injector Circuit Malfunction - Cylinder 6', 'High', 'Powertrain'),
                    ('P0207', 'Injector Circuit Malfunction - Cylinder 7', 'High', 'Powertrain'),
                    ('P0208', 'Injector Circuit Malfunction - Cylinder 8', 'High', 'Powertrain'),
                    ('P0209', 'Injector Circuit Malfunction - Cylinder 9', 'High', 'Powertrain'),
                    ('P0210', 'Injector Circuit Malfunction - Cylinder 10', 'High', 'Powertrain'),
                    ('P0211', 'Injector Circuit Malfunction - Cylinder 11', 'High', 'Powertrain'),
                    ('P0212', 'Injector Circuit Malfunction - Cylinder 12', 'High', 'Powertrain'),
                    ('P0213', 'Cold Start Injector 1 Malfunction', 'High', 'Powertrain'),
                    ('P0214', 'Cold Start Injector 2 Malfunction', 'High', 'Powertrain'),
                    ('P0215', 'Engine Shutoff Solenoid Malfunction', 'High', 'Powertrain'),
                    ('P0216', 'Injection Timing Control Circuit Malfunction', 'High', 'Powertrain'),
                    ('P0217', 'Engine Overtemperature Condition', 'Critical', 'Powertrain'),
                    ('P0218', 'Transmission Overtemperature Condition', 'Critical', 'Powertrain'),
                    ('P0219', 'Engine Overspeed Condition', 'Critical', 'Powertrain'),
                    ('P0220', 'Throttle/Pedal Position Sensor/Switch B Circuit Malfunction', 'High', 'Powertrain'),
                    ('P0221', 'Throttle/Pedal Position Sensor/Switch B Circuit Range/Performance Problem', 'High', 'Powertrain'),
                    ('P0222', 'Throttle/Pedal Position Sensor/Switch B Circuit Low Input', 'High', 'Powertrain'),
                    ('P0223', 'Throttle/Pedal Position Sensor/Switch B Circuit High Input', 'High', 'Powertrain'),
                    ('P0224', 'Throttle/Pedal Position Sensor/Switch B Circuit Intermittent', 'High', 'Powertrain'),
                    ('P0225', 'Throttle/Pedal Position Sensor/Switch C Circuit Malfunction', 'High', 'Powertrain'),
                    ('P0226', 'Throttle/Pedal Position Sensor/Switch C Circuit Range/Performance Problem', 'High', 'Powertrain'),
                    ('P0227', 'Throttle/Pedal Position Sensor/Switch C Circuit Low Input', 'High', 'Powertrain'),
                    ('P0228', 'Throttle/Pedal Position Sensor/Switch C Circuit High Input', 'High', 'Powertrain'),
                    ('P0229', 'Throttle/Pedal Position Sensor/Switch C Circuit Intermittent', 'High', 'Powertrain'),
                    ('P0230', 'Fuel Pump Primary Circuit Malfunction', 'High', 'Powertrain'),
                    ('P0231', 'Fuel Pump Secondary Circuit Low', 'High', 'Powertrain'),
                    ('P0232', 'Fuel Pump Secondary Circuit High', 'High', 'Powertrain'),
                    ('P0233', 'Fuel Pump Secondary Circuit Intermittent', 'High', 'Powertrain'),
                    ('P0234', 'Engine Overboost Condition', 'Critical', 'Powertrain'),
                    ('P0235', 'Turbocharger/Supercharger Boost Sensor A Circuit Malfunction', 'Medium', 'Powertrain'),
                    ('P0236', 'Turbocharger/Supercharger Boost Sensor A Circuit Range/Performance', 'Medium', 'Powertrain'),
                    ('P0237', 'Turbocharger/Supercharger Boost Sensor A Circuit Low Input', 'Medium', 'Powertrain'),
                    ('P0238', 'Turbocharger/Supercharger Boost Sensor A Circuit High Input', 'Medium', 'Powertrain'),
                    ('P0239', 'Turbocharger/Supercharger Boost Sensor B Circuit Malfunction', 'Medium', 'Powertrain'),
                    ('P0240', 'Turbocharger/Supercharger Boost Sensor B Circuit Range/Performance', 'Medium', 'Powertrain'),
                    ('P0241', 'Turbocharger/Supercharger Boost Sensor B Circuit Low Input', 'Medium', 'Powertrain'),
                    ('P0242', 'Turbocharger/Supercharger Boost Sensor B Circuit High Input', 'Medium', 'Powertrain'),
                    ('P0243', 'Turbocharger/Supercharger Wastegate Solenoid A Malfunction', 'Medium', 'Powertrain'),
                    ('P0244', 'Turbocharger/Supercharger Wastegate Solenoid A Range/Performance', 'Medium', 'Powertrain'),
                    ('P0245', 'Turbocharger/Supercharger Wastegate Solenoid A Low Input', 'Medium', 'Powertrain'),
                    ('P0246', 'Turbocharger/Supercharger Wastegate Solenoid A High Input', 'Medium', 'Powertrain'),
                    ('P0247', 'Turbocharger/Supercharger Wastegate Solenoid B Malfunction', 'Medium', 'Powertrain'),
                    ('P0248', 'Turbocharger/Supercharger Wastegate Solenoid B Range/Performance', 'Medium', 'Powertrain'),
                    ('P0249', 'Turbocharger/Supercharger Wastegate Solenoid B Low Input', 'Medium', 'Powertrain'),
                    ('P0250', 'Turbocharger/Supercharger Wastegate Solenoid B High Input', 'Medium', 'Powertrain'),
                    ('P0300', 'Random/Multiple Cylinder Misfire Detected', 'High', 'Powertrain'),
                    ('P0301', 'Cylinder 1 Misfire Detected', 'High', 'Powertrain'),
                    ('P0302', 'Cylinder 2 Misfire Detected', 'High', 'Powertrain'),
                    ('P0303', 'Cylinder 3 Misfire Detected', 'High', 'Powertrain'),
                    ('P0304', 'Cylinder 4 Misfire Detected', 'High', 'Powertrain'),
                    ('P0305', 'Cylinder 5 Misfire Detected', 'High', 'Powertrain'),
                    ('P0306', 'Cylinder 6 Misfire Detected', 'High', 'Powertrain'),
                    ('P0307', 'Cylinder 7 Misfire Detected', 'High', 'Powertrain'),
                    ('P0308', 'Cylinder 8 Misfire Detected', 'High', 'Powertrain'),
                    ('P0309', 'Cylinder 9 Misfire Detected', 'High', 'Powertrain'),
                    ('P0310', 'Cylinder 10 Misfire Detected', 'High', 'Powertrain'),
                    ('P0311', 'Cylinder 11 Misfire Detected', 'High', 'Powertrain'),
                    ('P0312', 'Cylinder 12 Misfire Detected', 'High', 'Powertrain'),
                    ('P0420', 'Catalyst System Efficiency Below Threshold', 'Medium', 'Powertrain'),
                    ('P0700', 'Transmission Control System Malfunction', 'High', 'Powertrain'),

                    # Network DTCs
                    ('U0100', 'Lost Communication with ECM/PCM A', 'Critical', 'Network'),
                    ('U0101', 'Lost Communication with TCM', 'Critical', 'Network'),
                    ('U0121', 'Lost Communication with Anti-Lock Brake System (ABS) Control Module', 'High', 'Network'),
                    ('U0140', 'Lost Communication with Body Control Module', 'High', 'Network'),

                    # Body DTCs
                    ('B0001', 'Front Impact Sensor Circuit Malfunction', 'Critical', 'Body'),
                    ('B1000', 'ECU Malfunction', 'Critical', 'Body'),

                    # Chassis DTCs
                    ('C1201', 'ABS System Malfunction', 'High', 'Chassis'),
                    ('C1234', 'Wheel Speed Sensor Fault', 'High', 'Chassis'),
                ]

                # Use executemany for better performance
                cursor.executemany('''
                    INSERT OR IGNORE INTO dtc_codes (code, description, severity, category)
                    VALUES (?, ?, ?, ?)
                ''', enhanced_dtcs)

                conn.commit()
                logger.info(f"Populated {len(enhanced_dtcs)} enhanced DTC codes into database")

        except Exception as e:
            logger.error(f"Failed to populate enhanced DTC data: {e}")

    def close(self):
        """Close database connection"""
        pass  # SQLite connection is auto-closed with context manager

# Global DTC database instance
_dtc_database_instance = None

def get_dtc_database():
    """Get the global DTC database instance"""
    global _dtc_database_instance
    if _dtc_database_instance is None:
        _dtc_database_instance = DTCDatabaseSQLite()
    return _dtc_database_instance

# Test
if __name__ == "__main__":
    dtc_db = DTCDatabaseSQLite()
    print("DTC Database Test:")
    print("-" * 50)

    # Test basic functionality
    info = dtc_db.get_dtc_info('P0300')
    print(f"P0300: {info}")

    info = dtc_db.get_dtc_info('U0100')
    print(f"U0100: {info}")

    info = dtc_db.get_dtc_info('INVALID')
    print(f"INVALID: {info}")

    # Test search
    results = dtc_db.search_dtcs('misfire')
    print(f"Found {len(results)} misfire-related DTCs")

    # Test count
    count = dtc_db.get_dtc_count()
    print(f"Total DTCs: {count}")

    print("\n[OK] DTC Database SQLite version is working!")