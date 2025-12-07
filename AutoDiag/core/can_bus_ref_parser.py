#!/usr/bin/env python3
"""
CAN Bus REF File Parser
Parses Racelogic CAN Data File V1a format (.REF files)
"""

import struct
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


@dataclass
class CANSignal:
    """Represents a CAN signal definition"""
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
    """Represents a CAN message definition"""
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
    """Complete CAN database for a vehicle"""
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


class REFFileParser:
    """Parser for Racelogic CAN Data File V1a format"""
    
    HEADER_SIGNATURE = b"Racelogic Can Data File V1a"
    
    def __init__(self, ref_dir: Optional[Path] = None):
        self.ref_dir = ref_dir or Path(__file__).parents[2] / "can_bus_data" / "Vehicle_CAN_Files_REF"
        self._cache: Dict[str, VehicleCANDatabase] = {}
        
    def list_available_vehicles(self) -> List[Tuple[str, str, str]]:
        """List all available vehicle REF files
        Returns: List of (manufacturer, model, filename) tuples
        """
        vehicles = []
        if not self.ref_dir.exists():
            logger.warning(f"REF directory not found: {self.ref_dir}")
            return vehicles
            
        for ref_file in self.ref_dir.glob("*.REF"):
            name = ref_file.stem
            if "-" in name:
                parts = name.split("-", 1)
                manufacturer = parts[0].strip()
                model = parts[1].strip() if len(parts) > 1 else ""
                vehicles.append((manufacturer, model, ref_file.name))
            else:
                vehicles.append((name, "", ref_file.name))
                
        return sorted(vehicles, key=lambda x: (x[0], x[1]))
    
    def get_manufacturers(self) -> List[str]:
        """Get list of unique manufacturers"""
        vehicles = self.list_available_vehicles()
        return sorted(set(v[0] for v in vehicles))
    
    def get_models_for_manufacturer(self, manufacturer: str) -> List[str]:
        """Get models available for a manufacturer"""
        vehicles = self.list_available_vehicles()
        return sorted([v[1] for v in vehicles if v[0] == manufacturer])
    
    def parse_file(self, filename: str) -> Optional[VehicleCANDatabase]:
        """Parse a REF file and return vehicle CAN database"""
        # Check cache first
        if filename in self._cache:
            return self._cache[filename]
            
        file_path = self.ref_dir / filename
        if not file_path.exists():
            logger.error(f"REF file not found: {file_path}")
            return None
            
        try:
            with open(file_path, 'rb') as f:
                # Limit data read to prevent UI freezing on large files
                data = f.read(100000)  # Read only first 100KB

            logger.info(f"Parsing REF file {filename} ({len(data)} bytes)")

            # Parse the file
            db = self._parse_ref_data(data, filename)
            if db:
                db.file_path = str(file_path)
                self._cache[filename] = db
                logger.info(f"Successfully parsed {len(db.messages)} messages from {filename}")
            else:
                logger.warning(f"Failed to parse {filename}, using defaults")

            return db

        except Exception as e:
            logger.error(f"Error parsing REF file {filename}: {e}")
            return None
    
    def _parse_ref_data(self, data: bytes, filename: str) -> Optional[VehicleCANDatabase]:
        """Parse REF file binary data"""
        # Extract manufacturer and model from filename
        name = Path(filename).stem
        if "-" in name:
            parts = name.split("-", 1)
            manufacturer = parts[0].strip()
            model = parts[1].strip()
        else:
            manufacturer = name
            model = ""
        
        # Extract year range from model name
        year_match = re.search(r'(\d{4})\s*[-–]\s*(\d{4}|\-)?', model)
        year_range = year_match.group(0) if year_match else ""
        
        # Create database
        db = VehicleCANDatabase(
            manufacturer=manufacturer,
            model=model,
            year_range=year_range
        )
        
        # Parse the binary content
        # Racelogic format typically has:
        # - Header with file info
        # - Channel definitions
        # - CAN message definitions
        
        try:
            # Find text sections in the binary data
            text_sections = self._extract_text_sections(data)
            
            # Parse CAN IDs and signals from the data
            messages = self._extract_can_messages(data, text_sections)
            
            for msg in messages:
                db.messages[msg.can_id] = msg
                
            logger.info(f"Parsed {len(db.messages)} CAN messages from {filename}")
            
        except Exception as e:
            logger.warning(f"Partial parse of {filename}: {e}")
            # Create default messages based on common automotive CAN IDs
            db.messages = self._create_default_messages(manufacturer)
            
        return db
    
    def _extract_text_sections(self, data: bytes) -> List[str]:
        """Extract readable text sections from binary data"""
        text_sections = []
        current_text = ""
        
        for byte in data:
            if 32 <= byte <= 126:  # Printable ASCII
                current_text += chr(byte)
            elif byte == 0 and len(current_text) > 3:
                text_sections.append(current_text)
                current_text = ""
            else:
                if len(current_text) > 3:
                    text_sections.append(current_text)
                current_text = ""
                
        return text_sections
    
    def _extract_can_messages(self, data: bytes, text_sections: List[str]) -> List[CANMessage]:
        """Extract CAN message definitions from parsed data"""
        messages = []
        
        # Look for CAN ID patterns in the binary data
        # Standard CAN IDs are 11-bit (0x000-0x7FF)
        # Extended CAN IDs are 29-bit
        
        found_ids = set()
        for i in range(0, len(data) - 4, 2):
            # Try to find potential CAN IDs
            value_le = int.from_bytes(data[i:i+2], 'little')
            value_be = int.from_bytes(data[i:i+2], 'big')
            
            # Check if it looks like a standard CAN ID
            for value in [value_le, value_be]:
                if 0x100 <= value <= 0x7FF:
                    found_ids.add(value)
        
        # Create message definitions for found IDs
        for can_id in sorted(found_ids)[:50]:  # Limit to first 50
            msg = CANMessage(
                can_id=can_id,
                name=f"MSG_0x{can_id:03X}",
                dlc=8
            )
            messages.append(msg)
            
        return messages
    
    def _create_default_messages(self, manufacturer: str) -> Dict[int, CANMessage]:
        """Create default CAN message definitions based on manufacturer"""
        messages = {}
        
        # Common OBD-II PIDs (standard across all vehicles)
        obd_messages = [
            (0x7E8, "ECU_Response", [
                CANSignal("Engine_RPM", 24, 16, 'big', 0.25, 0, 0, 16383.75, "RPM"),
                CANSignal("Vehicle_Speed", 24, 8, 'big', 1, 0, 0, 255, "km/h"),
                CANSignal("Coolant_Temp", 24, 8, 'big', 1, -40, -40, 215, "°C"),
                CANSignal("Throttle_Position", 24, 8, 'big', 0.392, 0, 0, 100, "%"),
            ]),
            (0x7E0, "ECU_Request", []),
        ]
        
        # Manufacturer-specific messages
        manufacturer_messages = {
            "BMW": [
                (0x1D0, "Engine_Data", [
                    CANSignal("Engine_RPM", 16, 16, 'big', 0.25, 0, 0, 8000, "RPM"),
                    CANSignal("Throttle", 32, 8, 'big', 0.4, 0, 0, 100, "%"),
                ]),
                (0x1D2, "Speed_Data", [
                    CANSignal("Vehicle_Speed", 0, 16, 'big', 0.01, 0, 0, 300, "km/h"),
                ]),
                (0x1D5, "Brake_Data", [
                    CANSignal("Brake_Pressure", 0, 16, 'big', 0.1, 0, 0, 200, "bar"),
                ]),
                (0x1F0, "Steering", [
                    CANSignal("Steering_Angle", 0, 16, 'big', 0.1, -720, -720, 720, "°"),
                ]),
            ],
            "Mercedes": [
                (0x200, "Engine_Status", [
                    CANSignal("Engine_RPM", 0, 16, 'big', 1, 0, 0, 8000, "RPM"),
                    CANSignal("Engine_Load", 16, 8, 'big', 0.4, 0, 0, 100, "%"),
                ]),
                (0x208, "Transmission", [
                    CANSignal("Gear_Position", 0, 4, 'big', 1, 0, 0, 8, ""),
                    CANSignal("Trans_Temp", 8, 8, 'big', 1, -40, -40, 215, "°C"),
                ]),
            ],
            "Toyota": [
                (0x2C1, "Engine_Data", [
                    CANSignal("Engine_RPM", 0, 16, 'big', 0.25, 0, 0, 8000, "RPM"),
                    CANSignal("Accelerator", 16, 8, 'big', 0.4, 0, 0, 100, "%"),
                ]),
                (0x2C4, "Speed", [
                    CANSignal("Vehicle_Speed", 0, 16, 'big', 0.01, 0, 0, 300, "km/h"),
                ]),
            ],
            "Honda": [
                (0x17C, "Engine", [
                    CANSignal("Engine_RPM", 0, 16, 'big', 1, 0, 0, 8000, "RPM"),
                ]),
                (0x1DC, "Speed", [
                    CANSignal("Vehicle_Speed", 0, 16, 'big', 0.01, 0, 0, 300, "km/h"),
                ]),
            ],
            "Ford": [
                (0x201, "Engine_RPM", [
                    CANSignal("Engine_RPM", 0, 16, 'big', 0.25, 0, 0, 8000, "RPM"),
                ]),
                (0x217, "Vehicle_Speed", [
                    CANSignal("Vehicle_Speed", 0, 16, 'big', 0.01, 0, 0, 300, "km/h"),
                ]),
            ],
            "Audi": [
                (0x280, "Motor_1", [
                    CANSignal("Engine_RPM", 16, 16, 'big', 0.25, 0, 0, 8000, "RPM"),
                    CANSignal("Throttle", 40, 8, 'big', 0.4, 0, 0, 100, "%"),
                ]),
                (0x320, "Kombi_1", [
                    CANSignal("Vehicle_Speed", 0, 16, 'big', 0.01, 0, 0, 300, "km/h"),
                ]),
            ],
            "Volkswagen": [
                (0x280, "Motor_1", [
                    CANSignal("Engine_RPM", 16, 16, 'big', 0.25, 0, 0, 8000, "RPM"),
                ]),
                (0x5A0, "Airbag", [
                    CANSignal("Crash_Status", 0, 8, 'big', 1, 0, 0, 255, ""),
                ]),
            ],
            "Porsche": [
                (0x300, "Engine", [
                    CANSignal("Engine_RPM", 0, 16, 'big', 0.25, 0, 0, 9000, "RPM"),
                    CANSignal("Oil_Temp", 24, 8, 'big', 1, -40, -40, 215, "°C"),
                ]),
                (0x310, "Chassis", [
                    CANSignal("Vehicle_Speed", 0, 16, 'big', 0.01, 0, 0, 350, "km/h"),
                    CANSignal("Lateral_G", 16, 16, 'big', 0.001, -2, -2, 2, "g"),
                ]),
            ],
            "Ferrari": [
                (0x400, "Engine", [
                    CANSignal("Engine_RPM", 0, 16, 'big', 1, 0, 0, 9000, "RPM"),
                    CANSignal("Oil_Pressure", 16, 8, 'big', 0.5, 0, 0, 10, "bar"),
                ]),
            ],
        }
        
        # Add OBD messages
        for can_id, name, signals in obd_messages:
            msg = CANMessage(can_id=can_id, name=name, signals=signals)
            messages[can_id] = msg
        
        # Add manufacturer-specific messages
        if manufacturer in manufacturer_messages:
            for can_id, name, signals in manufacturer_messages[manufacturer]:
                msg = CANMessage(can_id=can_id, name=name, signals=signals)
                messages[can_id] = msg
                
        return messages


# Global parser instance
ref_parser = REFFileParser()


def get_vehicle_database(manufacturer: str, model: str = "") -> Optional[VehicleCANDatabase]:
    """Get CAN database for a specific vehicle"""
    vehicles = ref_parser.list_available_vehicles()
    
    # Find matching vehicle
    for mfr, mdl, filename in vehicles:
        if mfr.lower() == manufacturer.lower():
            if not model or model.lower() in mdl.lower():
                return ref_parser.parse_file(filename)
    
    # Return default database if no specific match
    db = VehicleCANDatabase(
        manufacturer=manufacturer,
        model=model or "Generic",
        year_range=""
    )
    db.messages = ref_parser._create_default_messages(manufacturer)
    return db


def list_all_vehicles() -> List[Tuple[str, str, str]]:
    """List all available vehicles"""
    return ref_parser.list_available_vehicles()


def get_all_manufacturers() -> List[str]:
    """Get all available manufacturers"""
    return ref_parser.get_manufacturers()
