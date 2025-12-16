#!/usr/bin/env python3
"""
SQLite CAN Database Manager for AutoDiag Pro
Handles the consolidated CAN database with 1197 vehicles, 8481 messages, 20811 signals
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class CANSignal:
    """Represents a CAN signal definition from SQLite database"""
    id: int
    name: str
    start_bit: int
    bit_length: int
    byte_order: str  # 'little' or 'big'
    scale: float = 1.0
    offset: float = 0.0
    min_value: float = 0.0
    max_value: float = 0.0
    unit: str = ""
    description: str = ""

    def decode(self, data: bytes) -> float:
        """Decode signal value from CAN data bytes"""
        try:
            # Extract bits from data
            value = 0
            for i in range(self.bit_length):
                bit_pos = self.start_bit + i
                byte_idx = bit_pos // 8
                bit_idx = bit_pos % 8
                if byte_idx < len(data):
                    if data[byte_idx] & (1 << bit_idx):
                        value |= (1 << i)

            # Apply scale and offset
            return (value * self.scale) + self.offset
        except Exception as e:
            logger.error(f"Error decoding signal {self.name}: {e}")
            return 0.0

@dataclass
class CANMessage:
    """Represents a CAN message definition from SQLite database"""
    id: int
    can_id: int
    name: str
    dlc: int = 8  # Data Length Code
    signals: List[CANSignal] = field(default_factory=list)
    description: str = ""
    transmitter: str = ""
    cycle_time_ms: int = 0

    def decode_all(self, data: bytes) -> Dict[str, float]:
        """Decode all signals from CAN data"""
        result = {}
        for signal in self.signals:
            result[signal.name] = signal.decode(data)
        return result

@dataclass
class VehicleCANDatabase:
    """Complete CAN database for a vehicle from SQLite"""
    vehicle_id: int
    manufacturer: str
    model: str
    year_range: str
    messages: Dict[int, CANMessage] = field(default_factory=dict)
    file_path: str = ""

    def get_message(self, can_id: int) -> Optional[CANMessage]:
        """Get message definition by CAN ID"""
        return self.messages.get(can_id)

    def decode_frame(self, can_id: int, data: bytes) -> Optional[Dict[str, float]]:
        """Decode a CAN frame"""
        msg = self.get_message(can_id)
        if msg:
            return msg.decode_all(data)
        return None

class SQLiteCANManager:
    """SQLite-based CAN database manager"""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or Path(__file__).parents[2] / "can_bus_databases.sqlite"
        self._connection: Optional[sqlite3.Connection] = None
        self._cache: Dict[str, VehicleCANDatabase] = {}

    def connect(self) -> bool:
        """Connect to SQLite database"""
        try:
            self._connection = sqlite3.connect(str(self.db_path))
            self._connection.row_factory = sqlite3.Row
            logger.info(f"Connected to CAN database: {self.db_path}")

            # Verify database structure
            self._verify_database()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to CAN database: {e}")
            return False

    def disconnect(self):
        """Disconnect from database"""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Disconnected from CAN database")

    def _verify_database(self):
        """Verify database has required tables"""
        if not self._connection:
            return

        required_tables = ['vehicles', 'messages', 'signals']
        cursor = self._connection.cursor()

        for table in required_tables:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not cursor.fetchone():
                logger.warning(f"Required table '{table}' not found in database")
                return

        # Get database statistics
        cursor.execute("SELECT COUNT(*) FROM vehicles")
        vehicle_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM messages")
        message_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM signals")
        signal_count = cursor.fetchone()[0]

        logger.info(f"CAN Database loaded: {vehicle_count} vehicles, {message_count} messages, {signal_count} signals")

    def get_all_manufacturers(self) -> List[str]:
        """Get list of all manufacturers"""
        if not self._connection:
            return []

        try:
            cursor = self._connection.cursor()
            cursor.execute("SELECT DISTINCT manufacturer FROM vehicles ORDER BY manufacturer")
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting manufacturers: {e}")
            return []

    def get_models_for_manufacturer(self, manufacturer: str) -> List[str]:
        """Get models for a specific manufacturer"""
        if not self._connection:
            return []

        try:
            cursor = self._connection.cursor()
            cursor.execute(
                "SELECT DISTINCT model FROM vehicles WHERE manufacturer = ? ORDER BY model",
                (manufacturer,)
            )
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting models for {manufacturer}: {e}")
            return []

    def get_vehicle_database(self, manufacturer: str, model: str = "") -> Optional[VehicleCANDatabase]:
        """Get CAN database for a specific vehicle"""
        if not self._connection:
            return None

        # Create cache key
        cache_key = f"{manufacturer}_{model}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            cursor = self._connection.cursor()

            # Find vehicle
            if model:
                cursor.execute(
                    "SELECT id, manufacturer, model, year_range FROM vehicles WHERE manufacturer = ? AND model = ?",
                    (manufacturer, model)
                )
            else:
                cursor.execute(
                    "SELECT id, manufacturer, model, year_range FROM vehicles WHERE manufacturer = ?",
                    (manufacturer,)
                )

            vehicle_row = cursor.fetchone()
            if not vehicle_row:
                logger.warning(f"Vehicle not found: {manufacturer} {model}")
                return None

            vehicle_id, mfr, mdl, year_range = vehicle_row

            # Create database object
            db = VehicleCANDatabase(
                vehicle_id=vehicle_id,
                manufacturer=mfr,
                model=mdl,
                year_range=year_range
            )

            # Load messages for this vehicle
            cursor.execute("""
                SELECT id, can_id, name, dlc, description, transmitter, cycle_time_ms
                FROM messages
                WHERE vehicle_id = ?
                ORDER BY can_id
            """, (vehicle_id,))

            message_rows = cursor.fetchall()

            for msg_row in message_rows:
                msg_id, can_id, name, dlc, description, transmitter, cycle_time_ms = msg_row

                # Load signals for this message
                cursor.execute("""
                    SELECT id, name, start_bit, bit_length, byte_order, scale, offset,
                           min_value, max_value, unit, description
                    FROM signals
                    WHERE message_id = ?
                    ORDER BY start_bit
                """, (msg_id,))

                signals = []
                for sig_row in cursor.fetchall():
                    sig_id, sig_name, start_bit, bit_length, byte_order, scale, offset, \
                    min_value, max_value, unit, sig_description = sig_row

                    signal = CANSignal(
                        id=sig_id,
                        name=sig_name,
                        start_bit=start_bit,
                        bit_length=bit_length,
                        byte_order=byte_order,
                        scale=scale,
                        offset=offset,
                        min_value=min_value,
                        max_value=max_value,
                        unit=unit,
                        description=sig_description
                    )
                    signals.append(signal)

                message = CANMessage(
                    id=msg_id,
                    can_id=can_id,
                    name=name,
                    dlc=dlc,
                    signals=signals,
                    description=description,
                    transmitter=transmitter,
                    cycle_time_ms=cycle_time_ms
                )

                db.messages[can_id] = message

            # Cache the database
            self._cache[cache_key] = db

            logger.info(f"Loaded CAN database for {manufacturer} {model}: {len(db.messages)} messages")
            return db

        except Exception as e:
            logger.error(f"Error loading vehicle database {manufacturer} {model}: {e}")
            return None

    def search_signals(self, query: str, manufacturer: str = None, model: str = None) -> List[Dict[str, Any]]:
        """Search for signals by name or description"""
        if not self._connection:
            return []

        try:
            cursor = self._connection.cursor()

            # Build query
            sql = """
                SELECT s.id, s.name, s.unit, s.description, s.min_value, s.max_value,
                       m.can_id, m.name as message_name,
                       v.manufacturer, v.model
                FROM signals s
                JOIN messages m ON s.message_id = m.id
                JOIN vehicles v ON m.vehicle_id = v.id
                WHERE (s.name LIKE ? OR s.description LIKE ?)
            """

            params = [f"%{query}%", f"%{query}%"]

            if manufacturer:
                sql += " AND v.manufacturer = ?"
                params.append(manufacturer)

            if model:
                sql += " AND v.model = ?"
                params.append(model)

            sql += " ORDER BY s.name LIMIT 100"

            cursor.execute(sql, params)
            results = []

            for row in cursor.fetchall():
                results.append({
                    'signal_id': row[0],
                    'signal_name': row[1],
                    'unit': row[2],
                    'description': row[3],
                    'min_value': row[4],
                    'max_value': row[5],
                    'can_id': row[6],
                    'message_name': row[7],
                    'manufacturer': row[8],
                    'model': row[9]
                })

            return results

        except Exception as e:
            logger.error(f"Error searching signals: {e}")
            return []

    def get_signal_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not self._connection:
            return {}

        try:
            cursor = self._connection.cursor()

            stats = {}

            # Vehicle count
            cursor.execute("SELECT COUNT(*) FROM vehicles")
            stats['vehicle_count'] = cursor.fetchone()[0]

            # Message count
            cursor.execute("SELECT COUNT(*) FROM messages")
            stats['message_count'] = cursor.fetchone()[0]

            # Signal count
            cursor.execute("SELECT COUNT(*) FROM signals")
            stats['signal_count'] = cursor.fetchone()[0]

            # Manufacturers
            cursor.execute("SELECT COUNT(DISTINCT manufacturer) FROM vehicles")
            stats['manufacturer_count'] = cursor.fetchone()[0]

            # Top manufacturers by message count
            cursor.execute("""
                SELECT v.manufacturer, COUNT(m.id) as msg_count
                FROM vehicles v
                JOIN messages m ON v.id = m.vehicle_id
                GROUP BY v.manufacturer
                ORDER BY msg_count DESC
                LIMIT 10
            """)
            stats['top_manufacturers'] = [(row[0], row[1]) for row in cursor.fetchall()]

            return stats

        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

    def export_vehicle_data(self, manufacturer: str, model: str, format: str = 'json') -> Optional[str]:
        """Export vehicle CAN data"""
        db = self.get_vehicle_database(manufacturer, model)
        if not db:
            return None

        # Export as JSON
        import json

        data = {
            'manufacturer': db.manufacturer,
            'model': db.model,
            'year_range': db.year_range,
            'messages': {}
        }

        for can_id, message in db.messages.items():
            data['messages'][f"0x{can_id:03X}"] = {
                'name': message.name,
                'dlc': message.dlc,
                'description': message.description,
                'transmitter': message.transmitter,
                'cycle_time_ms': message.cycle_time_ms,
                'signals': [
                    {
                        'name': signal.name,
                        'start_bit': signal.start_bit,
                        'bit_length': signal.bit_length,
                        'byte_order': signal.byte_order,
                        'scale': signal.scale,
                        'offset': signal.offset,
                        'min_value': signal.min_value,
                        'max_value': signal.max_value,
                        'unit': signal.unit,
                        'description': signal.description
                    }
                    for signal in message.signals
                ]
            }

        return json.dumps(data, indent=2)

# Global instance
can_db_manager = SQLiteCANManager()

def get_vehicle_database(manufacturer: str, model: str = "") -> Optional[VehicleCANDatabase]:
    """Get CAN database for a specific vehicle"""
    return can_db_manager.get_vehicle_database(manufacturer, model)

def list_all_vehicles() -> List[Tuple[str, str, str]]:
    """List all available vehicles"""
    if not can_db_manager._connection:
        can_db_manager.connect()

    vehicles = []
    manufacturers = can_db_manager.get_all_manufacturers()

    for mfr in manufacturers:
        models = can_db_manager.get_models_for_manufacturer(mfr)
        for model in models:
            vehicles.append((mfr, model, f"{mfr}-{model}"))

    return vehicles

def get_all_manufacturers() -> List[str]:
    """Get all available manufacturers"""
    if not can_db_manager._connection:
        can_db_manager.connect()

    return can_db_manager.get_all_manufacturers()

def search_can_signals(query: str, manufacturer: str = None, model: str = None) -> List[Dict[str, Any]]:
    """Search for CAN signals"""
    if not can_db_manager._connection:
        can_db_manager.connect()

    return can_db_manager.search_signals(query, manufacturer, model)

def get_can_database_stats() -> Dict[str, Any]:
    """Get CAN database statistics"""
    if not can_db_manager._connection:
        can_db_manager.connect()

    return can_db_manager.get_signal_statistics()