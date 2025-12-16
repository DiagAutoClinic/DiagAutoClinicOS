#!/usr/bin/env python3
"""
BMW CAN Bus Module
Specialized functions for BMW vehicles based on parsed .REF data
"""

import sqlite3
from typing import Dict, List, Optional, Tuple
import struct
import can
from dataclasses import dataclass

@dataclass
class BMWSignal:
    """BMW-specific signal with enhanced metadata"""
    name: str
    can_id: int
    description: str
    category: str  # engine, chassis, body, diag, etc.
    access: str    # read, write, r/w
    ecu_source: str  # DME, DDE, EGS, etc.

class BMWCAN:
    """Main BMW CAN bus interface"""
    
    # BMW-specific CAN IDs (from database analysis)
    BMW_BROADCAST_IDS = {
        0x0AA: "DME1 (Engine Control)",
        0x0AB: "DME2 (Engine Control)",
        0x0B0: "EGS (Transmission)",
        0x0B4: "DSC (Stability Control)",
        0x0C8: "KOMBI (Instrument Cluster)",
        0x0D0: "FRM (Footwell Module)",
        0x0DA: "CAS (Car Access System)",
        0x12F: "BDC (Body Domain Controller)",
        0x1D0: "SZL (Steering Column)",
        0x1F0: "JBE (Junction Box)",
    }
    
    def __init__(self, db_path="can_database.db", vehicle_model=None):
        """Initialize BMW CAN interface"""
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # Load BMW-specific signals
        self.signals = self._load_bmw_signals(vehicle_model)
        self.bus = None  # CAN bus interface
        
    def _load_bmw_signals(self, model_filter=None) -> Dict[int, List[BMWSignal]]:
        """Load BMW signals from database"""
        query = """
            SELECT s.name, m.can_id, s.unit, s.start_bit, s.bit_length,
                   s.scale, s.offset, s.signed, s.byte_order
            FROM signals s
            JOIN messages m ON s.message_id = m.id
            JOIN vehicles v ON m.vehicle_id = v.id
            WHERE v.make = 'BMW'
        """
        
        if model_filter:
            query += f" AND v.model LIKE '%{model_filter}%'"
        
        self.cursor.execute(query)
        signals_by_id = {}
        
        for row in self.cursor.fetchall():
            name, can_id, unit, start_bit, bit_length, scale, offset, signed, byte_order = row
            
            # Categorize signal based on name patterns
            category = self._categorize_signal(name)
            ecu_source = self._identify_ecu_source(can_id)
            
            signal = BMWSignal(
                name=name,
                can_id=can_id,
                description=f"{name} from {ecu_source}",
                category=category,
                access="read",  # Default, can be updated
                ecu_source=ecu_source
            )
            
            if can_id not in signals_by_id:
                signals_by_id[can_id] = []
            signals_by_id[can_id].append(signal)
        
        return signals_by_id
    
    def _categorize_signal(self, signal_name: str) -> str:
        """Categorize signal based on naming patterns"""
        name_lower = signal_name.lower()
        
        if any(word in name_lower for word in ['rpm', 'throttle', 'fuel', 'temp', 'pressure', 'boost']):
            return 'engine'
        elif any(word in name_lower for word in ['speed', 'wheel', 'brake', 'steer', 'yaw']):
            return 'chassis'
        elif any(word in name_lower for word in ['door', 'window', 'mirror', 'seat', 'light']):
            return 'body'
        elif any(word in name_lower for word in ['dtc', 'fault', 'error', 'diagnos']):
            return 'diagnostic'
        elif any(word in name_lower for word in ['voltage', 'current', 'battery']):
            return 'electrical'
        else:
            return 'miscellaneous'
    
    def _identify_ecu_source(self, can_id: int) -> str:
        """Identify which ECU is likely sending this CAN ID"""
        for id_range, ecu in self.BMW_BROADCAST_IDS.items():
            if can_id == id_range or can_id in range(id_range, id_range + 0x10):
                return ecu
        return "Unknown ECU"
    
    def connect_can_bus(self, interface='socketcan', channel='can0'):
        """Connect to physical CAN bus"""
        try:
            self.bus = can.Bus(interface=interface, channel=channel, bustype='socketcan')
            print(f"✅ Connected to CAN bus: {interface}:{channel}")
            return True
        except Exception as e:
            print(f"❌ CAN bus connection failed: {e}")
            return False
    
    def read_live_data(self, timeout=1.0):
        """Read and decode live CAN data"""
        if not self.bus:
            print("⚠️  CAN bus not connected. Use connect_can_bus() first.")
            return []
        
        messages = []
        try:
            msg = self.bus.recv(timeout=timeout)
            while msg:
                if msg.arbitration_id in self.signals:
                    decoded = self.decode_message(msg)
                    messages.append(decoded)
                msg = self.bus.recv(timeout=0.1)  # Non-blocking subsequent reads
        except can.CanError:
            pass
        
        return messages
    
    def decode_message(self, can_msg) -> Dict:
        """Decode a single CAN message"""
        decoded = {
            'can_id': hex(can_msg.arbitration_id),
            'ecu': self._identify_ecu_source(can_msg.arbitration_id),
            'data': can_msg.data.hex(),
            'signals': []
        }
        
        if can_msg.arbitration_id in self.signals:
            for signal in self.signals[can_msg.arbitration_id]:
                # TODO: Implement actual decoding using signal.bit_length, scale, offset
                # This would use the same logic as ref_parser.CANSignal.decode()
                decoded['signals'].append({
                    'name': signal.name,
                    'category': signal.category,
                    'description': signal.description
                })
        
        return decoded
    
    def get_engine_params(self):
        """Get common engine parameters"""
        engine_signals = []
        for can_id, signals in self.signals.items():
            for sig in signals:
                if sig.category == 'engine':
                    engine_signals.append(sig)
        return engine_signals
    
    def get_diagnostic_codes(self):
        """Get diagnostic-related signals"""
        diag_signals = []
        for can_id, signals in self.signals.items():
            for sig in signals:
                if sig.category == 'diagnostic':
                    diag_signals.append(sig)
        return diag_signals
    
    def find_signal(self, pattern: str):
        """Find signals matching pattern"""
        matches = []
        for can_id, signals in self.signals.items():
            for sig in signals:
                if pattern.lower() in sig.name.lower():
                    matches.append(sig)
        return matches
    
    def close(self):
        """Cleanup resources"""
        if self.bus:
            self.bus.shutdown()
        self.conn.close()

# Quick test function
def test_bmw_module():
    """Test the BMW CAN module"""
    print("Testing BMW CAN Module...")
    
    bmw = BMWCAN()
    
    # Show statistics
    total_signals = sum(len(sigs) for sigs in bmw.signals.values())
    print(f"Loaded {total_signals} BMW signals")
    print(f"CAN IDs with signals: {len(bmw.signals)}")
    
    # Show engine signals
    engine_sigs = bmw.get_engine_params()
    print(f"\nEngine parameters found: {len(engine_sigs)}")
    for sig in engine_sigs[:5]:  # Show first 5
        print(f"  • {sig.name} (0x{sig.can_id:X}) - {sig.ecu_source}")
    
    # Show diagnostic signals
    diag_sigs = bmw.get_diagnostic_codes()
    print(f"\nDiagnostic signals found: {len(diag_sigs)}")
    for sig in diag_sigs[:5]:
        print(f"  • {sig.name} (0x{sig.can_id:X})")
    
    bmw.close()
    print("\n✅ BMW module test complete")

if __name__ == "__main__":
    test_bmw_module()