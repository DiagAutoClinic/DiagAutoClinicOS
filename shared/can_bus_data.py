#!/usr/bin/env python3
"""
CAN Bus Data Import System
Handles .REF file imports and real automotive data integration
"""

import logging
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class CANMessage:
    """CAN bus message structure"""
    timestamp: float
    can_id: int
    dlc: int
    data: bytes
    bus: str = "CAN1"

@dataclass 
class CANParameter:
    """CAN parameter definition"""
    name: str
    can_id: int
    start_byte: int
    start_bit: int
    length_bits: int
    conversion_factor: float = 1.0
    conversion_offset: float = 0.0
    unit: str = ""
    min_value: float = None
    max_value: float = None
    description: str = ""

class CANBusDataManager:
    """Manages CAN bus data import and real automotive parameters"""
    
    def __init__(self):
        self.parameters: Dict[str, CANParameter] = {}
        self.messages: List[CANMessage] = []
        self.current_brand: str = ""
        self.data_dir = Path("data/can_bus")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def import_ref_file(self, file_path: Path, brand: str) -> bool:
        """Import .REF file for specific brand"""
        try:
            logger.info(f"Importing CAN bus data from {file_path} for {brand}")
            
            if not file_path.exists():
                logger.error(f"REF file not found: {file_path}")
                return False
            
            # Detect file format and parse accordingly
            if file_path.suffix.lower() == '.ref':
                success = self._parse_ref_format(file_path, brand)
            elif file_path.suffix.lower() == '.csv':
                success = self._parse_csv_format(file_path, brand)
            elif file_path.suffix.lower() == '.json':
                success = self._parse_json_format(file_path, brand)
            else:
                logger.error(f"Unsupported file format: {file_path.suffix}")
                return False
            
            if success:
                self.current_brand = brand
                self._save_brand_data(brand)
                logger.info(f"Successfully imported {len(self.parameters)} parameters for {brand}")
                return True
            else:
                logger.error(f"Failed to import data from {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error importing REF file: {e}")
            return False
    
    def _parse_ref_format(self, file_path: Path, brand: str) -> bool:
        """Parse proprietary .REF format - supports Racelogic format"""
        try:
            # First try to detect if it's a Racelogic file
            with open(file_path, 'rb') as f:
                header = f.read(100)
            
            if b'Racelogic' in header:
                # Use Racelogic parser
                return self._parse_racelogic_format(file_path, brand)
            else:
                # Try text-based REF format
                return self._parse_text_ref_format(file_path, brand)
            
        except Exception as e:
            logger.error(f"Error detecting REF format: {e}")
            return False
    
    def _parse_racelogic_format(self, file_path: Path, brand: str) -> bool:
        """Parse Racelogic CAN Data File format"""
        try:
            from shared.racelogic_parser import parse_racelogic_ref_file
            
            logger.info(f"Parsing Racelogic format file: {file_path.name}")
            parser = parse_racelogic_ref_file(file_path)
            
            if not parser:
                logger.error(f"Failed to parse Racelogic file: {file_path}")
                return False
            
            # Convert Racelogic parameters to our CANParameter format
            parameter_count = 0
            for racelogic_param in parser.parameters:
                param = CANParameter(
                    name=racelogic_param.name,
                    can_id=racelogic_param.can_id,
                    start_byte=0,  # Racelogic doesn't use byte/bit positioning
                    start_bit=0,
                    length_bits=16,  # Default to 16-bit values
                    conversion_factor=racelogic_param.conversion_factor,
                    conversion_offset=racelogic_param.conversion_offset,
                    unit=racelogic_param.unit,
                    description=racelogic_param.description
                )
                
                self.parameters[f"{brand}_{param.name}"] = param
                parameter_count += 1
            
            logger.info(f"Parsed {parameter_count} parameters from Racelogic format")
            return parameter_count > 0
            
        except Exception as e:
            logger.error(f"Error parsing Racelogic format: {e}")
            return False
    
    def _parse_text_ref_format(self, file_path: Path, brand: str) -> bool:
        """Parse text-based .REF format"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            parameter_count = 0
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#') or line.startswith('//'):
                    continue
                
                # Parse REF format: PARAM_NAME,CAN_ID,START_BYTE,BIT_POS,LENGTH,SCALE,OFFSET,UNIT,DESCRIPTION
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 6:
                    param = CANParameter(
                        name=parts[0],
                        can_id=int(parts[1], 16) if parts[1].startswith('0x') else int(parts[1]),
                        start_byte=int(parts[2]),
                        start_bit=int(parts[3]),
                        length_bits=int(parts[4]),
                        conversion_factor=float(parts[5]) if len(parts) > 5 and parts[5] else 1.0,
                        conversion_offset=float(parts[6]) if len(parts) > 6 and parts[6] else 0.0,
                        unit=parts[7] if len(parts) > 7 else "",
                        description=parts[8] if len(parts) > 8 else ""
                    )
                    
                    self.parameters[f"{brand}_{param.name}"] = param
                    parameter_count += 1
            
            logger.info(f"Parsed {parameter_count} parameters from text REF format")
            return parameter_count > 0
            
        except Exception as e:
            logger.error(f"Error parsing text REF format: {e}")
            return False
    
    def _parse_csv_format(self, file_path: Path, brand: str) -> bool:
        """Parse CSV format CAN data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                parameter_count = 0
                for row in reader:
                    param = CANParameter(
                        name=row.get('name', ''),
                        can_id=int(row.get('can_id', '0'), 16),
                        start_byte=int(row.get('start_byte', '0')),
                        start_bit=int(row.get('start_bit', '0')),
                        length_bits=int(row.get('length_bits', '8')),
                        conversion_factor=float(row.get('conversion_factor', '1.0')),
                        conversion_offset=float(row.get('conversion_offset', '0.0')),
                        unit=row.get('unit', ''),
                        description=row.get('description', '')
                    )
                    
                    if param.name:
                        self.parameters[f"{brand}_{param.name}"] = param
                        parameter_count += 1
            
            logger.info(f"Parsed {parameter_count} parameters from CSV format")
            return parameter_count > 0
            
        except Exception as e:
            logger.error(f"Error parsing CSV format: {e}")
            return False
    
    def _parse_json_format(self, file_path: Path, brand: str) -> bool:
        """Parse JSON format CAN data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            parameter_count = 0
            for param_data in data.get('parameters', []):
                param = CANParameter(
                    name=param_data.get('name', ''),
                    can_id=int(param_data.get('can_id', '0'), 16),
                    start_byte=int(param_data.get('start_byte', '0')),
                    start_bit=int(param_data.get('start_bit', '0')),
                    length_bits=int(param_data.get('length_bits', '8')),
                    conversion_factor=float(param_data.get('conversion_factor', '1.0')),
                    conversion_offset=float(param_data.get('conversion_offset', '0.0')),
                    unit=param_data.get('unit', ''),
                    description=param_data.get('description', '')
                )
                
                if param.name:
                    self.parameters[f"{brand}_{param.name}"] = param
                    parameter_count += 1
            
            logger.info(f"Parsed {parameter_count} parameters from JSON format")
            return parameter_count > 0
            
        except Exception as e:
            logger.error(f"Error parsing JSON format: {e}")
            return False
    
    def _save_brand_data(self, brand: str):
        """Save imported data for specific brand"""
        brand_file = self.data_dir / f"{brand.lower()}_can_data.json"
        
        brand_data = {
            'brand': brand,
            'import_timestamp': datetime.now().isoformat(),
            'parameters': {k: asdict(v) for k, v in self.parameters.items()}
        }
        
        with open(brand_file, 'w', encoding='utf-8') as f:
            json.dump(brand_data, f, indent=2, ensure_ascii=False)
    
    def load_brand_data(self, brand: str) -> bool:
        """Load previously imported data for brand"""
        try:
            brand_file = self.data_dir / f"{brand.lower()}_can_data.json"
            
            if not brand_file.exists():
                logger.warning(f"No CAN data found for {brand}")
                return False
            
            with open(brand_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.parameters.clear()
            for key, param_data in data['parameters'].items():
                param = CANParameter(**param_data)
                self.parameters[key] = param
            
            self.current_brand = brand
            logger.info(f"Loaded {len(self.parameters)} CAN parameters for {brand}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading brand data for {brand}: {e}")
            return False
    
    def get_parameter_value(self, param_name: str, raw_data: bytes) -> Optional[float]:
        """Extract parameter value from raw CAN data"""
        try:
            if param_name not in self.parameters:
                return None
            
            param = self.parameters[param_name]
            
            # Extract bits from data
            value = 0
            for i in range(param.length_bits):
                bit_pos = param.start_bit + i
                byte_pos = param.start_byte + (bit_pos // 8)
                bit_in_byte = 7 - (bit_pos % 8)
                
                if byte_pos < len(raw_data):
                    bit_value = (raw_data[byte_pos] >> bit_in_byte) & 1
                    value |= bit_value << i
            
            # Apply conversion
            converted_value = (value * param.conversion_factor) + param.conversion_offset
            return converted_value
            
        except Exception as e:
            logger.error(f"Error extracting parameter value: {e}")
            return None
    
    def get_real_time_data(self, brand: str, can_messages: List[CANMessage]) -> Dict[str, Any]:
        """Get real-time parameter values from CAN messages"""
        if not self.load_brand_data(brand):
            return {}
        
        real_time_data = {}
        
        for message in can_messages:
            # Find parameters that use this CAN ID
            matching_params = [
                param for param in self.parameters.values() 
                if param.can_id == message.can_id
            ]
            
            for param in matching_params:
                value = self.get_parameter_value(param.name, message.data)
                if value is not None:
                    # Convert to display format
                    display_name = param.name.replace(f"{brand}_", "")
                    real_time_data[display_name] = {
                        'value': value,
                        'unit': param.unit,
                        'raw_can_id': hex(param.can_id),
                        'description': param.description
                    }
        
        return real_time_data
    
    def get_available_brands(self) -> List[str]:
        """Get list of brands with CAN data"""
        brand_list = []
        for file_path in self.data_dir.glob("*_can_data.json"):
            brand_name = file_path.stem.replace("_can_data", "").replace("_", " ").title()
            brand_list.append(brand_name)
        return sorted(brand_list)
    
    def export_can_parameters(self, brand: str, output_file: Optional[Path] = None) -> bool:
        """Export CAN parameters to file"""
        try:
            if not self.load_brand_data(brand):
                return False
            
            if output_file is None:
                output_file = self.data_dir / f"{brand.lower()}_parameters_export.csv"
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['name', 'can_id', 'start_byte', 'start_bit', 'length_bits', 
                             'conversion_factor', 'conversion_offset', 'unit', 'description']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                for param in self.parameters.values():
                    writer.writerow({
                        'name': param.name,
                        'can_id': hex(param.can_id),
                        'start_byte': param.start_byte,
                        'start_bit': param.start_bit,
                        'length_bits': param.length_bits,
                        'conversion_factor': param.conversion_factor,
                        'conversion_offset': param.conversion_offset,
                        'unit': param.unit,
                        'description': param.description
                    })
            
            logger.info(f"Exported {len(self.parameters)} parameters to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting CAN parameters: {e}")
            return False
    
    def get_parameter_summary(self) -> Dict[str, Any]:
        """Get summary of imported parameters"""
        if not self.parameters:
            return {'total_parameters': 0, 'brands': [], 'file_count': 0}
        
        brands = set()
        for param_key in self.parameters.keys():
            if '_' in param_key:
                brand = param_key.split('_')[0]
                brands.add(brand.title())
        
        return {
            'total_parameters': len(self.parameters),
            'brands': sorted(list(brands)),
            'file_count': len(list(self.data_dir.glob("*_can_data.json"))),
            'current_brand': self.current_brand
        }

# Global CAN bus data manager instance
can_bus_manager = CANBusDataManager()

def import_can_data_file(file_path: str, brand: str) -> bool:
    """Convenience function to import CAN data"""
    return can_bus_manager.import_ref_file(Path(file_path), brand)

def get_real_time_parameters(brand: str, can_messages: List[CANMessage]) -> Dict[str, Any]:
    """Get real-time parameters for brand"""
    return can_bus_manager.get_real_time_data(brand, can_messages)

def list_available_can_brands() -> List[str]:
    """List brands with available CAN data"""
    return can_bus_manager.get_available_brands()