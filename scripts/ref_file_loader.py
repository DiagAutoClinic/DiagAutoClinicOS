#!/usr/bin/env python3
"""
Racelogic REF File Parser
Parses "Racelogic Can Data File V1a" format with zlib compression
"""

import zlib
import struct
import re
import json
import pickle
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, BinaryIO
from collections import defaultdict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class RacelogicSignal:
    """Signal definition from Racelogic REF file"""
    name: str
    can_id: int
    start_bit: int
    bit_length: int
    byte_order: str  # 'Intel' or 'Motorola'
    scale: float
    offset: float
    min_val: float
    max_val: float
    unit: str
    description: str = ""
    multiplex_id: Optional[int] = None
    raw_bytes: bytes = field(default_factory=bytes)
    
    def decode(self, data: bytes) -> float:
        """Decode signal from CAN data bytes"""
        if len(data) < 8:
            return 0.0
        
        raw_value = self._extract_bits(data)
        return (raw_value * self.scale) + self.offset
    
    def _extract_bits(self, data: bytes) -> int:
        """Extract bits from CAN data based on start/bit length"""
        value = 0
        data_int = int.from_bytes(data[:8], 'little')
        
        for i in range(self.bit_length):
            bit_pos = self.start_bit + i
            if data_int & (1 << bit_pos):
                value |= (1 << i)
        
        return value

@dataclass
class RacelogicMessage:
    """CAN message definition"""
    can_id: int
    name: str
    dlc: int = 8
    signals: List[RacelogicSignal] = field(default_factory=list)
    cycle_time: int = 0
    description: str = ""
    
    def decode(self, data: bytes) -> Dict[str, float]:
        """Decode all signals in this message"""
        result = {}
        for signal in self.signals:
            result[signal.name] = signal.decode(data)
        return result

@dataclass
class RacelogicDatabase:
    """Complete vehicle CAN database"""
    manufacturer: str
    model: str
    year_range: str
    serial_number: str
    messages: Dict[int, RacelogicMessage] = field(default_factory=dict)
    file_path: str = ""
    parse_date: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def get_message(self, can_id: int) -> Optional[RacelogicMessage]:
        return self.messages.get(can_id)
    
    def decode_frame(self, can_id: int, data: bytes) -> Optional[Dict[str, float]]:
        msg = self.get_message(can_id)
        return msg.decode(data) if msg else None
    
    def save_json(self, filepath: str):
        """Save database to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(asdict(self), f, indent=2, default=str)
    
    @classmethod
    def load_json(cls, filepath: str) -> 'RacelogicDatabase':
        """Load database from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls(**data)

# ============================================================================
# MAIN PARSER
# ============================================================================

class RacelogicREFParser:
    """Parser for Racelogic Can Data File V1a format"""
    
    HEADER_SIGNATURE = b"Racelogic Can Data File V1a"
    ZLIB_HEADER = b'\x78\xDA'  # Default zlib compression
    
    def __init__(self, ref_dir: Path = None):
        self.ref_dir = ref_dir or Path("can_bus_data/Vehicle_CAN_Files_REF")
        self._cache: Dict[str, RacelogicDatabase] = {}
        
    def parse_file(self, filename: str) -> Optional[RacelogicDatabase]:
        """Parse a single REF file"""
        if filename in self._cache:
            return self._cache[filename]
        
        filepath = self.ref_dir / filename
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'rb') as f:
                raw_data = f.read()
            
            logger.info(f"Parsing {filename} ({len(raw_data)} bytes)")
            
            # Extract metadata from filename
            metadata = self._extract_filename_metadata(filename)
            
            # Parse the file structure
            database = self._parse_racelogic_format(raw_data, metadata)
            
            if database:
                database.file_path = str(filepath)
                self._cache[filename] = database
                logger.info(f"Parsed {len(database.messages)} messages from {filename}")
            
            return database
            
        except Exception as e:
            logger.error(f"Error parsing {filename}: {e}")
            return None
    
    def _parse_racelogic_format(self, data: bytes, metadata: Dict) -> Optional[RacelogicDatabase]:
        """Parse Racelogic V1a format with zlib sections"""
        
        # Check header
        if not data.startswith(self.HEADER_SIGNATURE):
            logger.warning("Not a valid Racelogic REF file")
            return None
        
        # Extract header section (text)
        header_end = data.find(b'\x00\x0B\x78\xDA')
        if header_end == -1:
            header_end = data.find(b'\x00')
        
        header_text = data[:header_end].decode('ascii', errors='ignore')
        serial_number = self._extract_serial_number(header_text)
        
        # Find all zlib compressed sections
        zlib_positions = []
        pos = 0
        while pos < len(data):
            found = data.find(self.ZLIB_HEADER, pos)
            if found == -1:
                break
            zlib_positions.append(found)
            pos = found + 2
        
        # Decompress and parse each section
        messages = {}
        signal_count = 0
        
        for zlib_pos in zlib_positions:
            try:
                # Try to decompress from this position
                decompressed = self._decompress_section(data[zlib_pos:])
                if decompressed:
                    # Parse CAN data from decompressed section
                    section_msgs = self._parse_compressed_section(decompressed)
                    messages.update(section_msgs)
                    signal_count += sum(len(m.signals) for m in section_msgs.values())
            except Exception as e:
                logger.debug(f"Failed to parse zlib section at {zlib_pos}: {e}")
        
        # Create database
        database = RacelogicDatabase(
            manufacturer=metadata.get('manufacturer', 'Unknown'),
            model=metadata.get('model', 'Unknown'),
            year_range=metadata.get('year_range', ''),
            serial_number=serial_number,
            messages=messages
        )
        
        logger.info(f"Extracted {len(messages)} messages with {signal_count} signals")
        return database
    
    def _decompress_section(self, data: bytes) -> Optional[bytes]:
        """Decompress zlib section"""
        try:
            # zlib header is 2 bytes, try to decompress from there
            decompressed = zlib.decompress(data)
            return decompressed
        except zlib.error:
            # Try different compression formats
            for wbits in [zlib.MAX_WBITS, zlib.MAX_WBITS | 16, -zlib.MAX_WBITS]:
                try:
                    decompressor = zlib.decompressobj(wbits)
                    decompressed = decompressor.decompress(data)
                    return decompressed
                except:
                    continue
        return None
    
    def _parse_compressed_section(self, data: bytes) -> Dict[int, RacelogicMessage]:
        """Parse decompressed CAN definitions"""
        messages = {}
        
        # The compressed data contains structured CAN definitions
        # Parse based on observed patterns from your analysis
        
        pos = 0
        while pos < len(data) - 20:  # Minimum size for a message definition
            try:
                # Try to parse CAN ID (likely 4 bytes)
                can_id = struct.unpack_from('<I', data, pos)[0]
                pos += 4
                
                # Parse signal count (likely 1 byte)
                signal_count = data[pos]
                pos += 1
                
                # Parse message name (null-terminated string)
                name_end = data.find(b'\x00', pos)
                if name_end == -1:
                    break
                name = data[pos:name_end].decode('ascii', errors='ignore')
                pos = name_end + 1
                
                # Parse signals
                signals = []
                for _ in range(signal_count):
                    if pos >= len(data) - 16:
                        break
                    
                    # Parse signal structure (estimated 16 bytes per signal)
                    sig_name_end = data.find(b'\x00', pos)
                    if sig_name_end == -1:
                        break
                    sig_name = data[pos:sig_name_end].decode('ascii', errors='ignore')
                    pos = sig_name_end + 1
                    
                    # Parse signal parameters (start_bit, length, scale, offset)
                    if pos + 16 <= len(data):
                        params = struct.unpack_from('<HHff', data, pos)
                        start_bit, bit_length, scale, offset = params
                        pos += 16
                        
                        signal = RacelogicSignal(
                            name=sig_name,
                            can_id=can_id,
                            start_bit=start_bit,
                            bit_length=bit_length,
                            byte_order='Intel',  # Racelogic typically uses Intel
                            scale=scale,
                            offset=offset,
                            min_val=0,
                            max_val=0,
                            unit=''
                        )
                        signals.append(signal)
                
                if signals:
                    message = RacelogicMessage(
                        can_id=can_id,
                        name=name,
                        dlc=8,
                        signals=signals
                    )
                    messages[can_id] = message
                    
            except Exception as e:
                logger.debug(f"Failed to parse at position {pos}: {e}")
                pos += 1
        
        return messages
    
    def _extract_filename_metadata(self, filename: str) -> Dict:
        """Extract manufacturer, model, year from filename"""
        stem = Path(filename).stem
        
        # Pattern: Manufacturer-Model (Code) Year-Year
        pattern = r'^([^-]+)-([^(]+) \(([^)]+)\) (\d{4}-\d{4})'
        match = re.match(pattern, stem)
        
        if match:
            manufacturer, model, code, years = match.groups()
            return {
                'manufacturer': manufacturer.strip(),
                'model': model.strip(),
                'code': code.strip(),
                'year_range': years.strip()
            }
        
        # Alternative pattern: Manufacturer-Model Year-Year
        pattern2 = r'^([^-]+)-([^\d]+) (\d{4}-\d{4})'
        match2 = re.match(pattern2, stem)
        
        if match2:
            manufacturer, model, years = match2.groups()
            return {
                'manufacturer': manufacturer.strip(),
                'model': model.strip(),
                'year_range': years.strip()
            }
        
        # Fallback
        return {'manufacturer': stem, 'model': '', 'year_range': ''}
    
    def _extract_serial_number(self, header_text: str) -> str:
        """Extract unit serial number from header"""
        match = re.search(r'Unit serial number\s*:\s*(\S+)', header_text)
        return match.group(1) if match else '00000000'
    
    def batch_parse_all(self) -> Dict[str, RacelogicDatabase]:
        """Parse all REF files in directory"""
        databases = {}
        ref_files = list(self.ref_dir.glob("*.REF"))
        
        logger.info(f"Found {len(ref_files)} REF files")
        
        for ref_file in ref_files:
            try:
                db = self.parse_file(ref_file.name)
                if db:
                    databases[ref_file.name] = db
                    logger.info(f"✓ Parsed {ref_file.name}")
                else:
                    logger.warning(f"✗ Failed to parse {ref_file.name}")
            except Exception as e:
                logger.error(f"Error processing {ref_file.name}: {e}")
        
        logger.info(f"Successfully parsed {len(databases)}/{len(ref_files)} files")
        return databases
    
    def export_all_to_json(self, output_dir: Path):
        """Export all parsed databases to JSON"""
        output_dir.mkdir(exist_ok=True)
        databases = self.batch_parse_all()
        
        for filename, db in databases.items():
            json_file = output_dir / f"{Path(filename).stem}.json"
            db.save_json(str(json_file))
            logger.info(f"Exported {filename} to {json_file}")
        
        # Create index file
        index = {
            'total_files': len(databases),
            'parse_date': datetime.now().isoformat(),
            'files': list(databases.keys())
        }
        
        index_file = output_dir / "index.json"
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
        
        logger.info(f"Created index with {len(databases)} databases")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_vehicle_mapping(database: RacelogicDatabase) -> Dict[str, List[int]]:
    """Create a mapping of signal types to CAN IDs"""
    mapping = defaultdict(list)
    
    for can_id, message in database.messages.items():
        for signal in message.signals:
            sig_lower = signal.name.lower()
            
            # Categorize signals
            if any(x in sig_lower for x in ['rpm', 'engine']):
                mapping['engine'].append(can_id)
            elif any(x in sig_lower for x in ['speed', 'velocity']):
                mapping['speed'].append(can_id)
            elif any(x in sig_lower for x in ['temp', 'temperature']):
                mapping['temperature'].append(can_id)
            elif any(x in sig_lower for x in ['volt', 'voltage']):
                mapping['voltage'].append(can_id)
            elif any(x in sig_lower for x in ['press', 'pressure']):
                mapping['pressure'].append(can_id)
            else:
                mapping['other'].append(can_id)
    
    return dict(mapping)

def find_signal_by_name(database: RacelogicDatabase, pattern: str) -> List[Tuple[int, RacelogicSignal]]:
    """Find signals by name pattern"""
    results = []
    pattern_lower = pattern.lower()
    
    for can_id, message in database.messages.items():
        for signal in message.signals:
            if pattern_lower in signal.name.lower():
                results.append((can_id, signal))
    
    return results

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Example usage
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    parser = RacelogicREFParser()
    
    if len(sys.argv) > 1:
        # Parse specific file
        filename = sys.argv[1]
        db = parser.parse_file(filename)
        
        if db:
            print(f"\n=== {db.manufacturer} {db.model} {db.year_range} ===")
            print(f"Messages: {len(db.messages)}")
            print(f"Serial: {db.serial_number}")
            
            # Show first few messages
            for can_id, msg in list(db.messages.items())[:5]:
                print(f"\nCAN 0x{can_id:03X} - {msg.name} ({len(msg.signals)} signals)")
                for sig in msg.signals[:3]:
                    print(f"  {sig.name}: bits {sig.start_bit}-{sig.start_bit+sig.bit_length}")
    else:
        # Batch parse all files
        print("Batch parsing all REF files...")
        databases = parser.batch_parse_all()
        
        # Export to JSON
        output_dir = Path("parsed_databases")
        parser.export_all_to_json(output_dir)
        
        print(f"\n✅ Parsed {len(databases)} vehicles")
        print(f"JSON files saved to: {output_dir}")