import zlib, csv, json, sqlite3
from pathlib import Path
from typing import List, Dict
import re

class CANSignal:
    def __init__(self, name: str, can_id, unit: str, start_bit, bit_length,
                 scale, offset, min_val, max_val, signed, byte_order: str, dlc):
        self.name = name
        self.can_id: int = int(can_id, 16) if isinstance(can_id, str) else int(can_id)
        self.unit = unit
        self.start_bit: int = int(start_bit)
        self.bit_length: int = int(bit_length)
        self.scale: float = float(scale)
        self.offset: float = float(offset)
        self.min_val: float = float(min_val)
        self.max_val: float = float(max_val)
        self.signed: bool = signed if isinstance(signed, bool) else signed.lower() in ('signed', 'true')
        self.byte_order: str = byte_order  # "little_endian" or "big_endian"
        self.dlc: int = int(dlc)
    
    def decode(self, data: bytes) -> float:
        # Ensure data is long enough
        required_bytes = (self.start_bit + self.bit_length + 7) // 8
        if len(data) < required_bytes:
            raise ValueError(f"Data too short: need {required_bytes} bytes, got {len(data)}")
        
        raw_value = 0
        for bit in range(self.bit_length):
            if self.byte_order == 'little_endian':
                # Intel format: LSB first
                total_bit = self.start_bit + bit
                byte_index = total_bit // 8
                bit_in_byte = total_bit % 8
                if data[byte_index] & (1 << bit_in_byte):
                    raw_value |= (1 << bit)
            elif self.byte_order == 'big_endian':
                # Motorola format: MSB first
                total_bit = self.start_bit + bit
                byte_index = total_bit // 8
                bit_in_byte = 7 - (total_bit % 8)
                if data[byte_index] & (1 << bit_in_byte):
                    raw_value |= (1 << (self.bit_length - 1 - bit))
            else:
                raise ValueError(f"Unknown byte_order: {self.byte_order}")
        
        # Handle signed
        if self.signed:
            if raw_value & (1 << (self.bit_length - 1)):
                raw_value -= (1 << self.bit_length)
        
        # Apply scale and offset
        value = raw_value * self.scale + self.offset
        return value

class CANMessage:
    def __init__(self, can_id: int, dlc: int):
        self.can_id = can_id
        self.dlc = dlc
        self.signals = []
    
    def add_signal(self, signal: CANSignal):
        self.signals.append(signal)

class VehicleDatabase:
    def __init__(self, filename: str):
        # EXTRACT: Acura-TSX (CU2 CU4) 2009-2014.REF
        self.filename = Path(filename).name
        self.manufacturer = ""
        self.model = ""
        self.year_range = ""
        self.messages = {}
    
    def add_signal(self, signal: CANSignal):
        can_id = signal.can_id
        if can_id not in self.messages:
            self.messages[can_id] = CANMessage(can_id, signal.dlc)
        self.messages[can_id].add_signal(signal)

class RacelogicREFParser:
    def __init__(self):
        pass
    
    def parse_file(self, filepath: str) -> VehicleDatabase:
        with open(filepath, 'rb') as f:
            data = f.read()
        
        # Skip header: "Racelogic Can Data File V1a\r\nUnit serial number : 00000000\r\n"
        header = b"Racelogic Can Data File V1a\r\nUnit serial number : 00000000\r\n"
        header_pos = data.find(header)
        if header_pos == -1:
            raise ValueError("Invalid REF file: header not found")
        data = data[header_pos + len(header):]
        
        # Find zlib sections starting with \x78\xDA
        zlib_starts = []
        pos = 0
        while True:
            idx = data.find(b'\x78\xDA', pos)
            if idx == -1:
                break
            zlib_starts.append(idx)
            pos = idx + 2
        
        messages = {}
        for start in zlib_starts:
            # Find end of this zlib section (next \x78\xDA or end)
            end = data.find(b'\x78\xDA', start + 2)
            if end == -1:
                end = len(data)
            compressed = data[start:end]
            
            try:
                decompressed = zlib.decompress(compressed, wbits=15)
                csv_text = decompressed.decode('utf-8', errors='ignore')
                
                # Parse CSV
                lines = csv_text.splitlines()
                reader = csv.reader(lines)
                for row in reader:
                    if len(row) < 12:
                        continue
                    name, can_id, unit, start_bit, bit_length, scale, offset, min_val, max_val, signed, byte_order, dlc = row[:12]
                    # Map signed
                    signed_bool = signed.lower() in ('signed', 'true')
                    # Map byte_order
                    if byte_order.lower() == 'motorola':
                        byte_order = 'big_endian'
                    elif byte_order.lower() == 'intel':
                        byte_order = 'little_endian'
                    signal = CANSignal(name, can_id, unit, start_bit, bit_length, scale, offset, min_val, max_val, signed_bool, byte_order, dlc)
                    can_id_int = signal.can_id
                    if can_id_int not in messages:
                        messages[can_id_int] = CANMessage(can_id_int, signal.dlc)
                    messages[can_id_int].add_signal(signal)
            except Exception as e:
                print(f"Error decompressing section at {start}: {e}")
                continue
        
        # Parse filename for metadata
        filename = Path(filepath).name
        # Example: "Acura-TSX (CU2 CU4) 2009-2014.REF"
        match = re.match(r'([^-]+)-(.+?)\s+(\d{4}-\d{4})\.REF', filename)
        if match:
            manufacturer = match.group(1)
            model = match.group(2)
            year_range = match.group(3)
        else:
            # Fallback parsing
            parts = filename.replace('.REF', '').rsplit('-', 1)
            if len(parts) == 2:
                manufacturer = parts[0]
                model_year = parts[1]
                year_match = re.search(r'(\d{4}-\d{4})', model_year)
                if year_match:
                    year_range = year_match.group(1)
                    model = model_year.replace(year_range, '').strip()
                else:
                    model = model_year
                    year_range = ""
            else:
                manufacturer = filename.replace('.REF', '')
                model = ""
                year_range = ""
        
        db = VehicleDatabase(filepath)
        db.manufacturer = manufacturer
        db.model = model
        db.year_range = year_range
        db.messages = messages
        return db
    
    def save_to_sqlite(self, databases: Dict[str, VehicleDatabase], output_path: str):
        conn = sqlite3.connect(output_path)
        c = conn.cursor()
        
        # Create tables
        c.execute('''CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            make TEXT,
            model TEXT,
            years TEXT
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER,
            can_id INTEGER,
            dlc INTEGER,
            FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER,
            name TEXT,
            unit TEXT,
            start_bit INTEGER,
            bit_length INTEGER,
            scale REAL,
            offset REAL,
            min_val REAL,
            max_val REAL,
            signed INTEGER,
            byte_order TEXT,
            dlc INTEGER,
            FOREIGN KEY(message_id) REFERENCES messages(id)
        )''')
        
        for db_name, db in databases.items():
            c.execute('INSERT INTO vehicles (make, model, years) VALUES (?, ?, ?)', 
                      (db.manufacturer, db.model, db.year_range))
            vehicle_id = c.lastrowid
            
            for msg in db.messages.values():
                c.execute('INSERT INTO messages (vehicle_id, can_id, dlc) VALUES (?, ?, ?)', 
                          (vehicle_id, msg.can_id, msg.dlc))
                message_id = c.lastrowid
                
                for sig in msg.signals:
                    c.execute('''INSERT INTO signals (message_id, name, unit, start_bit, bit_length, scale, offset, min_val, max_val, signed, byte_order, dlc) 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                              (message_id, sig.name, sig.unit, sig.start_bit, sig.bit_length, sig.scale, sig.offset, 
                               sig.min_val, sig.max_val, 1 if sig.signed else 0, sig.byte_order, sig.dlc))
        
        conn.commit()
        conn.close()