"""
Unified CAN Database Manager
Loads and manages multiple vehicle databases
"""

import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Set
import sqlite3
from datetime import datetime

class CANDatabaseManager:
    def __init__(self, db_dir: Path = Path("parsed_databases")):
        self.db_dir = db_dir
        self.databases: Dict[str, RacelogicDatabase] = {}
        self._load_all_databases()
    
    def _load_all_databases(self):
        """Load all JSON databases"""
        for json_file in self.db_dir.glob("*.json"):
            try:
                db = RacelogicDatabase.load_json(str(json_file))
                key = f"{db.manufacturer}_{db.model}"
                self.databases[key] = db
            except:
                continue
    
    def find_vehicle(self, manufacturer: str, model: str = "") -> List[RacelogicDatabase]:
        """Find vehicle databases"""
        results = []
        manufacturer_lower = manufacturer.lower()
        
        for db in self.databases.values():
            if manufacturer_lower in db.manufacturer.lower():
                if not model or model.lower() in db.model.lower():
                    results.append(db)
        
        return results
    
    def find_signal_across_all(self, signal_name: str) -> Dict[str, List[Tuple[int, RacelogicSignal]]]:
        """Find a signal across all vehicles"""
        results = {}
        
        for key, db in self.databases.items():
            matches = find_signal_by_name(db, signal_name)
            if matches:
                results[key] = matches
        
        return results