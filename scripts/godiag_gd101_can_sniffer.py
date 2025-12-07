#!/usr/bin/env python3
"""
GODIAG GD101 CAN Bus Sniffer - OBD2 16-Pin Only
================================================
Direct CAN bus sniffing using GODIAG GD101 via standard OBD2 16-pin connector.

OBD2 16-Pin CAN Bus Pinout:
- Pin 4:  Chassis Ground (0V)
- Pin 5:  Signal Ground (0V)
- Pin 6:  CAN High (CANH) - 2.5V ± 1V
- Pin 14: CAN Low (CANL) - 2.5V ± 1V
- Pin 16: +12V Battery Power

Usage:
    python scripts/godiag_gd101_can_sniffer.py --port COM3
    python scripts/godiag_gd101_can_sniffer.py --port COM3 --baudrate 500000
    python scripts/godiag_gd101_can_sniffer.py --port COM3 --filter 7E0-7EF
    python scripts/godiag_gd101_can_sniffer.py --mock  # Test mode without hardware
"""

import sys
import os
import time
import argparse
import logging
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


class CANBaudRate(Enum):
    """Standard CAN bus baud rates"""
    CAN_125K = 125000
    CAN_250K = 250000
    CAN_500K = 500000  # Most common for OBD2
    CAN_1M = 1000000


@dataclass
class CANFrame:
    """CAN bus frame structure"""
    timestamp: float
    arbitration_id: int
    is_extended: bool
    is_remote: bool
    dlc: int
    data: bytes
    
    def __str__(self) -> str:
        id_str = f"0x{self.arbitration_id:08X}" if self.is_extended else f"0x{self.arbitration_id:03X}"
        data_str = ' '.join(f'{b:02X}' for b in self.data)
        return f"[{self.timestamp:.6f}] {id_str} [{self.dlc}] {data_str}"
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'id': self.arbitration_id,
            'extended': self.is_extended,
            'remote': self.is_remote,
            'dlc': self.dlc,
            'data': self.data.hex()
        }


class GoDiagGD101CANSniffer:
    """
    CAN Bus Sniffer for GODIAG GD101 via OBD2 16-Pin Connector
    
    Supports:
    - Raw CAN frame capture
    - CAN ID filtering
    - Multiple baud rates (125K, 250K, 500K, 1M)
    - 11-bit and 29-bit CAN IDs
    - Real-time logging to file
    """
    
    # GODIAG GD101 Commands
    CMD_INIT = b'\x00\x01'
    CMD_CLOSE = b'\x00\x02'
    CMD_SET_BAUDRATE = b'\x10'
    CMD_SET_FILTER = b'\x11'
    CMD_START_SNIFF = b'\x12\x01'
    CMD_STOP_SNIFF = b'\x12\x00'
    CMD_READ_FRAME = b'\x13'
    
    def __init__(self, port: str = "COM1", baudrate: int = 500000, mock_mode: bool = False):
        self.port = port
        self.can_baudrate = baudrate
        self.mock_mode = mock_mode
        self.serial_conn = None
        self.is_connected = False
        self.is_sniffing = False
        self.captured_frames: List[CANFrame] = []
        self.filter_ids: List[Tuple[int, int]] = []  # (start_id, end_id) ranges
        self.start_time = 0.0
        
        # Statistics
        self.stats = {
            'total_frames': 0,
            'filtered_frames': 0,
            'errors': 0,
            'unique_ids': set()
        }
        
        if not mock_mode:
            try:
                import serial
                self.serial = serial
            except ImportError:
                logger.error("pyserial not installed. Install with: pip install pyserial")
                raise ImportError("pyserial required for real hardware mode")
    
    def connect(self) -> bool:
        """Connect to GODIAG GD101 via OBD2 16-pin port"""
        if self.mock_mode:
            logger.info("[MOCK] Connected to GODIAG GD101 (simulation mode)")
            self.is_connected = True
            return True
        
        try:
            logger.info(f"Connecting to GODIAG GD101 on {self.port}...")
            
            # Open serial connection
            self.serial_conn = self.serial.Serial(
                port=self.port,
                baudrate=115200,  # Serial communication baudrate (not CAN)
                timeout=2,
                bytesize=self.serial.EIGHTBITS,
                parity=self.serial.PARITY_NONE,
                stopbits=self.serial.STOPBITS_ONE
            )
            
            # Initialize device
            self._send_command(self.CMD_INIT)
            time.sleep(0.5)
            
            # Set CAN baudrate
            self._set_can_baudrate(self.can_baudrate)
            
            self.is_connected = True
            logger.info(f"Connected to GODIAG GD101 - CAN baudrate: {self.can_baudrate} bps")
            
            # Print OBD2 pin information
            self._print_obd2_pinout()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from GODIAG GD101"""
        if self.is_sniffing:
            self.stop_sniffing()
        
        if self.mock_mode:
            self.is_connected = False
            logger.info("[MOCK] Disconnected from GODIAG GD101")
            return True
        
        try:
            if self.serial_conn:
                self._send_command(self.CMD_CLOSE)
                self.serial_conn.close()
            
            self.is_connected = False
            logger.info("Disconnected from GODIAG GD101")
            return True
            
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
            return False
    
    def set_filter(self, filter_spec: str) -> bool:
        """
        Set CAN ID filter
        
        Args:
            filter_spec: Filter specification (e.g., "7E0-7EF", "7DF", "0x100-0x1FF")
        
        Returns:
            True if filter set successfully
        """
        try:
            self.filter_ids.clear()
            
            if not filter_spec:
                logger.info("No filter set - capturing all CAN IDs")
                return True
            
            # Parse filter specification
            parts = filter_spec.replace('0x', '').replace('0X', '').split(',')
            
            for part in parts:
                part = part.strip()
                if '-' in part:
                    # Range filter (e.g., "7E0-7EF")
                    start, end = part.split('-')
                    start_id = int(start, 16)
                    end_id = int(end, 16)
                    self.filter_ids.append((start_id, end_id))
                else:
                    # Single ID filter
                    can_id = int(part, 16)
                    self.filter_ids.append((can_id, can_id))
            
            logger.info(f"Filter set: {self.filter_ids}")
            
            # Send filter to device (if real hardware)
            if not self.mock_mode and self.serial_conn:
                for start_id, end_id in self.filter_ids:
                    filter_cmd = self.CMD_SET_FILTER + bytes([
                        (start_id >> 8) & 0xFF, start_id & 0xFF,
                        (end_id >> 8) & 0xFF, end_id & 0xFF
                    ])
                    self._send_command(filter_cmd)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set filter: {e}")
            return False
    
    def start_sniffing(self, duration: float = 0, output_file: Optional[str] = None) -> bool:
        """
        Start CAN bus sniffing
        
        Args:
            duration: Sniffing duration in seconds (0 = indefinite)
            output_file: Optional file to save captured frames
        
        Returns:
            True if sniffing started successfully
        """
        if not self.is_connected:
            logger.error("Not connected to device")
            return False
        
        self.captured_frames.clear()
        self.stats = {
            'total_frames': 0,
            'filtered_frames': 0,
            'errors': 0,
            'unique_ids': set()
        }
        self.start_time = time.time()
        self.is_sniffing = True
        
        logger.info("=" * 60)
        logger.info("GODIAG GD101 CAN BUS SNIFFER - OBD2 16-PIN")
        logger.info("=" * 60)
        logger.info(f"Port: {self.port}")
        logger.info(f"CAN Baudrate: {self.can_baudrate} bps")
        logger.info(f"Filter: {self.filter_ids if self.filter_ids else 'None (all IDs)'}")
        logger.info(f"Duration: {'Indefinite' if duration == 0 else f'{duration}s'}")
        logger.info("=" * 60)
        logger.info("Press Ctrl+C to stop sniffing")
        logger.info("")
        
        # Send start sniffing command
        if not self.mock_mode and self.serial_conn:
            self._send_command(self.CMD_START_SNIFF)
        
        # Open output file if specified
        output_handle = None
        if output_file:
            output_handle = open(output_file, 'w')
            output_handle.write(f"# GODIAG GD101 CAN Bus Capture\n")
            output_handle.write(f"# Date: {datetime.now().isoformat()}\n")
            output_handle.write(f"# Port: {self.port}\n")
            output_handle.write(f"# Baudrate: {self.can_baudrate}\n")
            output_handle.write(f"# Filter: {self.filter_ids}\n")
            output_handle.write("#\n")
            output_handle.write("# Timestamp, ID, DLC, Data\n")
        
        try:
            while self.is_sniffing:
                # Check duration
                if duration > 0 and (time.time() - self.start_time) >= duration:
                    logger.info(f"Duration {duration}s reached, stopping...")
                    break
                
                # Read CAN frame
                frame = self._read_can_frame()
                
                if frame:
                    # Apply filter
                    if self._passes_filter(frame.arbitration_id):
                        self.captured_frames.append(frame)
                        self.stats['filtered_frames'] += 1
                        self.stats['unique_ids'].add(frame.arbitration_id)
                        
                        # Print frame
                        print(frame)
                        
                        # Write to file
                        if output_handle:
                            output_handle.write(f"{frame}\n")
                            output_handle.flush()
                    
                    self.stats['total_frames'] += 1
                
                time.sleep(0.001)  # Small delay to prevent CPU overload
                
        except KeyboardInterrupt:
            logger.info("\nSniffing stopped by user")
        
        finally:
            self.is_sniffing = False
            
            if output_handle:
                output_handle.close()
            
            # Send stop sniffing command
            if not self.mock_mode and self.serial_conn:
                self._send_command(self.CMD_STOP_SNIFF)
            
            self._print_statistics()
        
        return True
    
    def stop_sniffing(self):
        """Stop CAN bus sniffing"""
        self.is_sniffing = False
    
    def _read_can_frame(self) -> Optional[CANFrame]:
        """Read a single CAN frame from the device"""
        if self.mock_mode:
            return self._generate_mock_frame()
        
        try:
            if not self.serial_conn or not self.serial_conn.is_open:
                return None
            
            # Send read command
            self.serial_conn.write(self.CMD_READ_FRAME)
            self.serial_conn.flush()
            
            # Read response (expected format: status + id(4) + dlc(1) + data(0-8))
            response = self.serial_conn.read(14)  # Max frame size
            
            if len(response) < 6:
                return None
            
            status = response[0]
            if status != 0x00:  # No frame available
                return None
            
            # Parse CAN frame
            arb_id = (response[1] << 24) | (response[2] << 16) | (response[3] << 8) | response[4]
            is_extended = (arb_id & 0x80000000) != 0
            arb_id &= 0x1FFFFFFF  # Mask to 29-bit
            
            dlc = response[5] & 0x0F
            data = response[6:6 + dlc]
            
            timestamp = time.time() - self.start_time
            
            return CANFrame(
                timestamp=timestamp,
                arbitration_id=arb_id,
                is_extended=is_extended,
                is_remote=False,
                dlc=dlc,
                data=bytes(data)
            )
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.debug(f"Read error: {e}")
            return None
    
    def _generate_mock_frame(self) -> Optional[CANFrame]:
        """Generate mock CAN frame for testing"""
        import random
        
        # Simulate realistic OBD2 traffic
        if random.random() > 0.3:  # 70% chance of frame
            # Common OBD2 CAN IDs
            obd2_ids = [0x7E0, 0x7E8, 0x7DF, 0x7E1, 0x7E9, 0x7E2, 0x7EA]
            
            arb_id = random.choice(obd2_ids)
            dlc = random.randint(1, 8)
            data = bytes([random.randint(0, 255) for _ in range(dlc)])
            
            timestamp = time.time() - self.start_time
            
            time.sleep(random.uniform(0.01, 0.1))  # Simulate bus timing
            
            return CANFrame(
                timestamp=timestamp,
                arbitration_id=arb_id,
                is_extended=False,
                is_remote=False,
                dlc=dlc,
                data=data
            )
        
        return None
    
    def _passes_filter(self, can_id: int) -> bool:
        """Check if CAN ID passes the filter"""
        if not self.filter_ids:
            return True
        
        for start_id, end_id in self.filter_ids:
            if start_id <= can_id <= end_id:
                return True
        
        return False
    
    def _set_can_baudrate(self, baudrate: int) -> bool:
        """Set CAN bus baudrate"""
        baudrate_map = {
            125000: 0x01,
            250000: 0x02,
            500000: 0x03,
            1000000: 0x04
        }
        
        baud_code = baudrate_map.get(baudrate, 0x03)  # Default to 500K
        cmd = self.CMD_SET_BAUDRATE + bytes([baud_code])
        
        if self.serial_conn:
            return self._send_command(cmd) is not None
        
        return True
    
    def _send_command(self, cmd: bytes, timeout_ms: int = 1000) -> Optional[bytes]:
        """Send command to GODIAG GD101"""
        try:
            if not self.serial_conn or not self.serial_conn.is_open:
                return None
            
            self.serial_conn.write(cmd)
            self.serial_conn.flush()
            
            # Read response
            start_time = time.time()
            response = b''
            
            while (time.time() - start_time) * 1000 < timeout_ms:
                if self.serial_conn.in_waiting:
                    response += self.serial_conn.read(self.serial_conn.in_waiting)
                    break
                time.sleep(0.01)
            
            return response if response else None
            
        except Exception as e:
            logger.error(f"Command error: {e}")
            return None
    
    def _print_obd2_pinout(self):
        """Print OBD2 16-pin connector information"""
        print("\n" + "=" * 60)
        print("OBD2 16-PIN CONNECTOR - CAN BUS PINOUT")
        print("=" * 60)
        print("Pin 4:  Chassis Ground    -> 0V")
        print("Pin 5:  Signal Ground     -> 0V")
        print("Pin 6:  CAN High (CANH)   -> 2.5V +/- 1V")
        print("Pin 14: CAN Low (CANL)    -> 2.5V +/- 1V")
        print("Pin 16: +12V Battery      -> +12V +/- 2V")
        print("=" * 60)
        print("")
    
    def _print_statistics(self):
        """Print sniffing statistics"""
        duration = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("CAN BUS SNIFFING STATISTICS")
        print("=" * 60)
        print(f"Duration:        {duration:.2f} seconds")
        print(f"Total Frames:    {self.stats['total_frames']}")
        print(f"Filtered Frames: {self.stats['filtered_frames']}")
        print(f"Unique IDs:      {len(self.stats['unique_ids'])}")
        print(f"Errors:          {self.stats['errors']}")
        
        if duration > 0:
            fps = self.stats['total_frames'] / duration
            print(f"Frame Rate:      {fps:.2f} frames/sec")
        
        if self.stats['unique_ids']:
            print(f"\nUnique CAN IDs captured:")
            for can_id in sorted(self.stats['unique_ids']):
                print(f"  0x{can_id:03X}")
        
        print("=" * 60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="GODIAG GD101 CAN Bus Sniffer - OBD2 16-Pin Only",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --port COM3                    # Basic sniffing on COM3
  %(prog)s --port COM3 --baudrate 500000  # Specify CAN baudrate
  %(prog)s --port COM3 --filter 7E0-7EF   # Filter OBD2 diagnostic IDs
  %(prog)s --port COM3 --duration 60      # Sniff for 60 seconds
  %(prog)s --port COM3 --output capture.txt  # Save to file
  %(prog)s --mock                         # Test mode without hardware

OBD2 16-Pin CAN Bus Connections:
  Pin 4:  Chassis Ground (0V)
  Pin 5:  Signal Ground (0V)
  Pin 6:  CAN High (CANH)
  Pin 14: CAN Low (CANL)
  Pin 16: +12V Battery Power
        """
    )
    
    parser.add_argument('--port', '-p', default='COM1',
                        help='Serial port for GODIAG GD101 (default: COM1)')
    parser.add_argument('--baudrate', '-b', type=int, default=500000,
                        choices=[125000, 250000, 500000, 1000000],
                        help='CAN bus baudrate (default: 500000)')
    parser.add_argument('--filter', '-f', default='',
                        help='CAN ID filter (e.g., "7E0-7EF" or "7DF,7E0-7EF")')
    parser.add_argument('--duration', '-d', type=float, default=0,
                        help='Sniffing duration in seconds (0 = indefinite)')
    parser.add_argument('--output', '-o', default='',
                        help='Output file for captured frames')
    parser.add_argument('--mock', '-m', action='store_true',
                        help='Run in mock mode (no hardware required)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create sniffer
    sniffer = GoDiagGD101CANSniffer(
        port=args.port,
        baudrate=args.baudrate,
        mock_mode=args.mock
    )
    
    # Connect
    if not sniffer.connect():
        logger.error("Failed to connect to GODIAG GD101")
        sys.exit(1)
    
    try:
        # Set filter
        if args.filter:
            sniffer.set_filter(args.filter)
        
        # Generate output filename if not specified
        output_file = args.output
        if not output_file and not args.mock:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"can_capture_{timestamp}.txt"
        
        # Start sniffing
        sniffer.start_sniffing(
            duration=args.duration,
            output_file=output_file
        )
        
    finally:
        sniffer.disconnect()


if __name__ == "__main__":
    main()
