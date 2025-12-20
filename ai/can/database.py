# ai/can/database.py

import sqlite3
import os
from typing import Optional, Any, Dict
from ..core.config import AIConfig
from ..core.exceptions import CANDatabaseError
from ..utils.logging import logger

class CANDatabase:
    def __init__(self, config: AIConfig):
        self.config = config
        self.connection: Optional[sqlite3.Connection] = None
        self.available = False

    def connect(self) -> bool:
        """Connect to the CAN database."""
        try:
            if os.path.exists(self.config.can_db_path):
                self.connection = sqlite3.connect(self.config.can_db_path)
                self.available = True
                logger.info("CAN database connected successfully")
                return True
            else:
                logger.warning("CAN database file not found")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to CAN database: {e}")
            raise CANDatabaseError(f"Database connection failed: {e}") from e

    def disconnect(self):
        """Disconnect from the CAN database."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.available = False
            logger.info("CAN database disconnected")

    def is_available(self) -> bool:
        return self.available

    def query_signal_definition(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """Query signal definition from database."""
        if not self.available or not self.connection:
            return None

        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM signals WHERE id = ?", (signal_id,))
            row = cursor.fetchone()
            if row:
                # Assuming table structure - adjust as needed
                return {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    # Add other fields as needed
                }
            return None
        except Exception as e:
            logger.warning(f"Database query failed: {e}")
            return None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()