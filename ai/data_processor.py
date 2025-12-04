#!/usr/bin/env python3
"""
AI Data Processor Module
Handles data collection, preprocessing, and storage for AI training
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Processes and stores diagnostic data for AI training
    """

    def __init__(self, db_path: str = "diagnostic_data.db"):
        """
        Initialize data processor with SQLite database

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        """Initialize database schema for diagnostic data storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create diagnostic sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS diagnostic_sessions (
                        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        vehicle_id TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        session_duration REAL,
                        device_type TEXT,
                        protocol_type TEXT,
                        raw_data BLOB,
                        processed_data TEXT,
                        dtc_codes TEXT,
                        vehicle_info TEXT,
                        metadata TEXT
                    )
                ''')

                # Create live data table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS live_data (
                        data_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER,
                        timestamp DATETIME NOT NULL,
                        parameter_name TEXT NOT NULL,
                        parameter_value REAL,
                        unit TEXT,
                        status TEXT,
                        FOREIGN KEY (session_id) REFERENCES diagnostic_sessions(session_id)
                    )
                ''')

                # Create fault patterns table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS fault_patterns (
                        pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fault_code TEXT NOT NULL,
                        description TEXT,
                        severity TEXT,
                        common_causes TEXT,
                        repair_suggestions TEXT,
                        occurrence_count INTEGER DEFAULT 0,
                        last_seen DATETIME
                    )
                ''')

                conn.commit()
                logger.info("Database initialized successfully")

        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def store_diagnostic_session(self, session_data: Dict[str, Any]) -> int:
        """
        Store a complete diagnostic session

        Args:
            session_data: Dictionary containing session information

        Returns:
            session_id: ID of the stored session
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Insert session data
                cursor.execute('''
                    INSERT INTO diagnostic_sessions (
                        vehicle_id, timestamp, session_duration, device_type,
                        protocol_type, raw_data, processed_data, dtc_codes,
                        vehicle_info, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_data.get('vehicle_id', ''),
                    session_data.get('timestamp', datetime.now().isoformat()),
                    session_data.get('session_duration', 0.0),
                    session_data.get('device_type', ''),
                    session_data.get('protocol_type', ''),
                    json.dumps(session_data.get('raw_data', {})),
                    json.dumps(session_data.get('processed_data', {})),
                    json.dumps(session_data.get('dtc_codes', [])),
                    json.dumps(session_data.get('vehicle_info', {})),
                    json.dumps(session_data.get('metadata', {}))
                ))

                session_id = cursor.lastrowid
                conn.commit()

                logger.info(f"Stored diagnostic session {session_id}")
                return session_id

        except sqlite3.Error as e:
            logger.error(f"Error storing diagnostic session: {e}")
            raise

    def store_live_data(self, session_id: int, live_data: List[Dict[str, Any]]):
        """
        Store live data from a diagnostic session

        Args:
            session_id: ID of the diagnostic session
            live_data: List of live data points
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                for data_point in live_data:
                    cursor.execute('''
                        INSERT INTO live_data (
                            session_id, timestamp, parameter_name,
                            parameter_value, unit, status
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        session_id,
                        data_point.get('timestamp', datetime.now().isoformat()),
                        data_point.get('parameter_name', ''),
                        data_point.get('parameter_value', 0.0),
                        data_point.get('unit', ''),
                        data_point.get('status', '')
                    ))

                conn.commit()
                logger.info(f"Stored {len(live_data)} live data points for session {session_id}")

        except sqlite3.Error as e:
            logger.error(f"Error storing live data: {e}")
            raise

    def update_fault_patterns(self, fault_data: Dict[str, Any]):
        """
        Update fault pattern database with new diagnostic information

        Args:
            fault_data: Dictionary containing fault pattern information
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if fault code exists
                cursor.execute('''
                    SELECT pattern_id, occurrence_count
                    FROM fault_patterns
                    WHERE fault_code = ?
                ''', (fault_data['fault_code'],))

                result = cursor.fetchone()

                if result:
                    # Update existing pattern
                    pattern_id, current_count = result
                    cursor.execute('''
                        UPDATE fault_patterns
                        SET occurrence_count = ?,
                            last_seen = ?,
                            description = ?,
                            severity = ?,
                            common_causes = ?,
                            repair_suggestions = ?
                        WHERE pattern_id = ?
                    ''', (
                        current_count + 1,
                        datetime.now().isoformat(),
                        fault_data.get('description', ''),
                        fault_data.get('severity', ''),
                        fault_data.get('common_causes', ''),
                        fault_data.get('repair_suggestions', ''),
                        pattern_id
                    ))
                else:
                    # Insert new pattern
                    cursor.execute('''
                        INSERT INTO fault_patterns (
                            fault_code, description, severity,
                            common_causes, repair_suggestions,
                            occurrence_count, last_seen
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        fault_data['fault_code'],
                        fault_data.get('description', ''),
                        fault_data.get('severity', ''),
                        fault_data.get('common_causes', ''),
                        fault_data.get('repair_suggestions', ''),
                        1,
                        datetime.now().isoformat()
                    ))

                conn.commit()
                logger.info(f"Updated fault pattern: {fault_data['fault_code']}")

        except sqlite3.Error as e:
            logger.error(f"Error updating fault patterns: {e}")
            raise

    def get_training_data(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Retrieve training data for AI model development

        Args:
            limit: Maximum number of sessions to retrieve

        Returns:
            List of diagnostic sessions with processed data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT session_id, processed_data, dtc_codes, vehicle_info
                    FROM diagnostic_sessions
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))

                sessions = []
                for row in cursor.fetchall():
                    sessions.append({
                        'session_id': row[0],
                        'processed_data': json.loads(row[1]) if row[1] else {},
                        'dtc_codes': json.loads(row[2]) if row[2] else [],
                        'vehicle_info': json.loads(row[3]) if row[3] else {}
                    })

                return sessions

        except sqlite3.Error as e:
            logger.error(f"Error retrieving training data: {e}")
            return []

    def get_fault_patterns(self) -> List[Dict[str, Any]]:
        """
        Retrieve all fault patterns for analysis

        Returns:
            List of fault patterns with occurrence data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT fault_code, description, severity,
                           common_causes, repair_suggestions,
                           occurrence_count, last_seen
                    FROM fault_patterns
                    ORDER BY occurrence_count DESC
                ''')

                patterns = []
                for row in cursor.fetchall():
                    patterns.append({
                        'fault_code': row[0],
                        'description': row[1],
                        'severity': row[2],
                        'common_causes': row[3],
                        'repair_suggestions': row[4],
                        'occurrence_count': row[5],
                        'last_seen': row[6]
                    })

                return patterns

        except sqlite3.Error as e:
            logger.error(f"Error retrieving fault patterns: {e}")
            return []

    def preprocess_diagnostic_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess raw diagnostic data for AI consumption

        Args:
            raw_data: Raw diagnostic data from vehicle

        Returns:
            Processed data dictionary with normalized values
        """
        processed_data = {}

        # Normalize DTC codes
        if 'dtc_codes' in raw_data:
            processed_data['dtc_codes'] = [
                self._normalize_dtc_code(code)
                for code in raw_data['dtc_codes']
            ]

        # Normalize live parameters
        if 'live_data' in raw_data:
            processed_data['live_parameters'] = {}
            for param_name, param_value in raw_data['live_data'].items():
                processed_data['live_parameters'][param_name] = {
                    'value': self._normalize_parameter_value(param_name, param_value),
                    'unit': self._get_parameter_unit(param_name)
                }

        # Add vehicle context
        if 'vehicle_info' in raw_data:
            processed_data['vehicle_context'] = {
                'make': raw_data['vehicle_info'].get('make', ''),
                'model': raw_data['vehicle_info'].get('model', ''),
                'year': raw_data['vehicle_info'].get('year', ''),
                'engine_type': raw_data['vehicle_info'].get('engine_type', '')
            }

        return processed_data

    def _normalize_dtc_code(self, dtc_code: str) -> str:
        """Normalize DTC code format"""
        # Remove any non-alphanumeric characters
        normalized = ''.join(c for c in dtc_code.upper() if c.isalnum())
        # Ensure standard PXXXX format
        if normalized.startswith('P') and len(normalized) == 5:
            return normalized
        elif len(normalized) == 4 and normalized.isdigit():
            return f"P{normalized}"
        else:
            return f"P{normalized[:4]}" if len(normalized) >= 4 else "P0000"

    def _normalize_parameter_value(self, param_name: str, param_value: Any) -> float:
        """Normalize parameter values based on expected ranges"""
        # This is a simplified normalization - real implementation would use
        # vehicle-specific parameter ranges and normalization algorithms
        try:
            return float(param_value)
        except (ValueError, TypeError):
            return 0.0

    def _get_parameter_unit(self, param_name: str) -> str:
        """Get standard unit for parameter"""
        # Common parameter units mapping
        unit_mapping = {
            'rpm': 'RPM',
            'speed': 'km/h',
            'temperature': '°C',
            'pressure': 'kPa',
            'voltage': 'V',
            'current': 'A',
            'throttle': '%',
            'load': '%',
            'timing': '°',
            'airflow': 'g/s',
            'lambda': 'λ'
        }

        # Simple heuristic to determine unit based on parameter name
        param_lower = param_name.lower()
        for key, unit in unit_mapping.items():
            if key in param_lower:
                return unit

        return ''

# Global data processor instance
data_processor = DataProcessor()