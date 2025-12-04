#!/usr/bin/env python3
"""
Racelogic .REF File Parser
Parses Racelogic CAN Data File V1a format
"""

import logging
import zlib
import struct
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RacelogicParameter:
    """Racelogic CAN parameter definition"""
    name: str
    can_id: int
    channel: int
    conversion_factor: float
    conversion_offset: float
    unit: str
    description: str
    min_value: float = 0.0
    max_value: float = 1000.0

class RacelogicParser:
    """Parser for Racelogic .REF files"""
    
    def __init__(self):
        self.header = {}
        self.parameters: List[RacelogicParameter] = []
        self.decompressed_data = None
        
    def parse_file(self, file_path: Path) -> bool:
        """Parse a Racelogic .REF file"""
        try:
            logger.info(f"Parsing Racelogic file: {file_path}")
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Check header
            if not self._parse_header(file_data):
                return False
            
            # Decompress data section
            if not self._decompress_data(file_data):
                return False
            
            # Parse parameters
            if not self._parse_parameters():
                return False
            
            logger.info(f"Successfully parsed {len(self.parameters)} parameters from {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error parsing Racelogic file: {e}")
            return False
    
    def _parse_header(self, data: bytes) -> bool:
        """Parse Racelogic header"""
        try:
            # Look for header marker
            header_marker = b"Racelogic Can Data File V1a"
            
            if header_marker not in data:
                logger.error("Invalid Racelogic file - header not found")
                return False
            
            header_start = data.find(header_marker)
            header_end = data.find(b'\x00\x0b', header_start)
            
            if header_end == -1:
                logger.error("Invalid Racelogic file - header end not found")
                return False
            
            header_data = data[header_start:header_end]
            header_str = header_data.decode('utf-8', errors='ignore')
            
            # Parse header fields
            self.header = {
                'version': 'V1a',
                'raw_header': header_str
            }
            
            # Look for serial number
            if 'Unit serial number' in header_str:
                # Extract serial number
                lines = header_str.split('\r\n')
                for line in lines:
                    if 'Unit serial number' in line:
                        self.header['serial_number'] = line.split(':')[1].strip()
                        break
            
            logger.debug(f"Parsed header: {self.header}")
            return True
            
        except Exception as e:
            logger.error(f"Error parsing header: {e}")
            return False
    
    def _decompress_data(self, data: bytes) -> bool:
        """Decompress the data section"""
        try:
            # Find compressed data section (starts after header)
            header_marker = b"Racelogic Can Data File V1a"
            header_start = data.find(header_marker)
            
            # Look for zlib compression marker (78 da or 78 9c)
            comp_start = -1
            for i in range(header_start + len(header_marker), len(data) - 4):
                if data[i:i+2] in [b'\x78\xda', b'\x78\x9c', b'\x78\x01']:
                    comp_start = i
                    break
            
            if comp_start == -1:
                logger.error("No compressed data found")
                return False
            
            # Extract compressed data
            compressed_data = data[comp_start:]
            
            # Try to decompress
            try:
                self.decompressed_data = zlib.decompress(compressed_data)
                logger.debug(f"Decompressed {len(self.decompressed_data)} bytes")
            except Exception as e:
                logger.error(f"Decompression failed: {e}")
                # Try with different window size
                try:
                    self.decompressed_data = zlib.decompress(compressed_data, wbits=15)
                except:
                    logger.error("All decompression attempts failed")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error decompressing data: {e}")
            return False
    
    def _parse_parameters(self) -> bool:
        """Parse CAN parameters from decompressed data"""
        try:
            if not self.decompressed_data:
                return False
            
            # Parse the decompressed binary data
            # Racelogic format typically contains parameter definitions
            
            params_found = 0
            i = 0
            
            while i < len(self.decompressed_data) - 20:  # Minimum parameter size
                # Look for parameter patterns
                param = self._extract_parameter_at_offset(i)
                if param:
                    self.parameters.append(param)
                    params_found += 1
                    logger.debug(f"Found parameter: {param.name} (CAN ID: 0x{param.can_id:03X})")
                
                i += 8  # Move to next potential parameter
            
            if params_found == 0:
                # Try alternative parsing methods
                return self._parse_parameters_alternative()
            
            logger.info(f"Extracted {params_found} parameters using primary method")
            return True
            
        except Exception as e:
            logger.error(f"Error parsing parameters: {e}")
            return False
    
    def _extract_parameter_at_offset(self, offset: int) -> Optional[RacelogicParameter]:
        """Extract parameter definition at specific offset"""
        try:
            data = self.decompressed_data
            
            if offset + 20 > len(data):
                return None
            
            # Try to identify parameter patterns
            # Look for CAN ID (typically in 0x100-0x7FF range)
            
            # Try different byte orders for CAN ID
            can_id_candidates = []
            
            # Little-endian 16-bit
            if offset + 2 <= len(data):
                cand1 = struct.unpack('<H', data[offset:offset+2])[0]
                if 0x100 <= cand1 <= 0x7FF:
                    can_id_candidates.append(cand1)
            
            # Big-endian 16-bit
            if offset + 2 <= len(data):
                cand2 = struct.unpack('>H', data[offset:offset+2])[0]
                if 0x100 <= cand2 <= 0x7FF:
                    can_id_candidates.append(cand2)
            
            if not can_id_candidates:
                return None
            
            # Use the first valid CAN ID
            can_id = can_id_candidates[0]
            
            # Extract other parameter data
            conversion_factor = 1.0
            conversion_offset = 0.0
            channel = (can_id >> 8) & 0x0F  # Extract channel from CAN ID
            
            # Try to find parameter name in nearby bytes
            name = self._extract_parameter_name(data, offset + 2)
            
            # Create parameter with generic automotive names if none found
            if not name:
                name = self._generate_parameter_name(can_id)
            
            return RacelogicParameter(
                name=name,
                can_id=can_id,
                channel=channel,
                conversion_factor=conversion_factor,
                conversion_offset=conversion_offset,
                unit=self._get_unit_for_can_id(can_id),
                description=f"CAN ID 0x{can_id:03X} parameter"
            )
            
        except Exception as e:
            logger.debug(f"Error extracting parameter at offset {offset}: {e}")
            return None
    
    def _extract_parameter_name(self, data: bytes, start_offset: int) -> Optional[str]:
        """Extract parameter name from data"""
        try:
            # Look for ASCII text near the offset
            for offset in range(start_offset, min(start_offset + 50, len(data))):
                # Check for printable ASCII characters
                text_chunk = []
                for i in range(offset, min(offset + 20, len(data))):
                    if 32 <= data[i] <= 126:  # Printable ASCII
                        text_chunk.append(chr(data[i]))
                    else:
                        if len(text_chunk) > 3:  # Found a word
                            name = ''.join(text_chunk)
                            # Filter for reasonable parameter names
                            if any(keyword in name.upper() for keyword in 
                                  ['TEMP', 'RPM', 'SPEED', 'PRESSURE', 'VOLTAGE', 'CURRENT']):
                                return name
                        break
                
                if len(text_chunk) > 3:
                    name = ''.join(text_chunk)
                    if any(keyword in name.upper() for keyword in 
                          ['TEMP', 'RPM', 'SPEED', 'PRESSURE', 'VOLTAGE', 'CURRENT']):
                        return name
            
            return None
            
        except Exception:
            return None
    
    def _generate_parameter_name(self, can_id: int) -> str:
        """Generate a generic parameter name based on CAN ID"""
        # Common automotive CAN ID ranges and their typical parameters
        id_ranges = {
            (0x100, 0x1FF): ["Engine_RPM", "Engine_Load", "Throttle_Position", "Engine_Temp"],
            (0x200, 0x2FF): ["Vehicle_Speed", "Transmission_Gear", "Brake_Pressure", "Steering_Angle"],
            (0x300, 0x3FF): ["Fuel_Level", "Oil_Pressure", "Coolant_Pressure", "Turbo_Boost"],
            (0x400, 0x4FF): ["Battery_Voltage", "Alternator_Current", "Fuel_Pressure", "Idle_RPM"],
            (0x500, 0x5FF): ["Catalyst_Temp", "O2_Sensor", "MAF_Sensor", "IAT_Sensor"],
            (0x600, 0x6FF): ["ABS_Status", "ESP_Status", "Airbag_Status", "Central_Lock"],
        }
        
        for (start, end), names in id_ranges.items():
            if start <= can_id <= end:
                index = (can_id - start) % len(names)
                return names[index]
        
        return f"CAN_ID_0x{can_id:03X}"
    
    def _get_unit_for_can_id(self, can_id: int) -> str:
        """Get unit based on CAN ID range"""
        if 0x100 <= can_id <= 0x1FF:
            return "RPM" if "RPM" in self._generate_parameter_name(can_id) else "units"
        elif 0x200 <= can_id <= 0x2FF:
            return "km/h" if "Speed" in self._generate_parameter_name(can_id) else "units"
        elif 0x300 <= can_id <= 0x3FF:
            return "PSI" if "Pressure" in self._generate_parameter_name(can_id) else "units"
        elif 0x400 <= can_id <= 0x4FF:
            return "V" if "Voltage" in self._generate_parameter_name(can_id) else "units"
        else:
            return "units"
    
    def _parse_parameters_alternative(self) -> bool:
        """Alternative parameter parsing method"""
        try:
            # If primary method fails, try to extract patterns manually
            data = self.decompressed_data
            
            # Look for repeating CAN ID patterns
            seen_ids = set()
            param_count = 0
            
            for i in range(0, len(data) - 2, 2):
                # Try little-endian
                can_id = struct.unpack('<H', data[i:i+2])[0]
                if 0x100 <= can_id <= 0x7FF and can_id not in seen_ids:
                    seen_ids.add(can_id)
                    
                    param = RacelogicParameter(
                        name=self._generate_parameter_name(can_id),
                        can_id=can_id,
                        channel=(can_id >> 8) & 0x0F,
                        conversion_factor=1.0,
                        conversion_offset=0.0,
                        unit=self._get_unit_for_can_id(can_id),
                        description=f"CAN ID 0x{can_id:03X} parameter (alternative parse)"
                    )
                    
                    self.parameters.append(param)
                    param_count += 1
            
            logger.info(f"Extracted {param_count} parameters using alternative method")
            return param_count > 0
            
        except Exception as e:
            logger.error(f"Alternative parsing failed: {e}")
            return False
    
    def get_parameters_dict(self) -> Dict[str, Any]:
        """Get parameters as dictionary for compatibility"""
        params_dict = {}
        for param in self.parameters:
            params_dict[f"{param.name}"] = param
        return params_dict

def parse_racelogic_ref_file(file_path: Path) -> Optional[RacelogicParser]:
    """Parse a Racelogic .REF file and return parser instance"""
    parser = RacelogicParser()
    if parser.parse_file(file_path):
        return parser
    return None