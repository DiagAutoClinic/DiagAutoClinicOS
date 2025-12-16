#!/usr/bin/env python3
"""
Vehicle CAN Module Template
Copy and adapt for each manufacturer
"""

import sqlite3
from typing import Dict, List
import abc

class BaseVehicleCAN(abc.ABC):
    """Abstract base class for all vehicle CAN modules"""
    
    def __init__(self, make: str, db_path="can_database.db"):
        self.make = make
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.signals = self._load_signals()
    
    @abc.abstractmethod
    def _load_signals(self) -> Dict:
        """Load manufacturer-specific signals"""
        pass
    
    @abc.abstractmethod
    def get_common_signals(self) -> List:
        """Get commonly used signals for this manufacturer"""
        pass
    
    @abc.abstractmethod
    def get_diagnostic_protocol(self):
        """Get diagnostic protocol specific to this manufacturer"""
        pass

# Template for creating new manufacturer modules
"""
MANUFACTURER_MODULE_TEMPLATE:

class ManufacturerCAN(BaseVehicleCAN):
    def __init__(self, db_path="can_database.db", model_filter=None):
        super().__init__("Manufacturer", db_path)
        self.model_filter = model_filter
        
    def _load_signals(self):
        # Custom signal loading logic
        pass
        
    def get_common_signals(self):
        # Return common signals for this brand
        pass
        
    def get_diagnostic_protocol(self):
        # Return diagnostic protocol info
        pass
"""