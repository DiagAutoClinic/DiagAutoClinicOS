#!/usr/bin/env python3
"""
GODIAG GD101 CAN Bus Sniffer - ELM327 Protocol
===============================================
CAN bus sniffing using GODIAG GD101 via OBD2 16-pin connector.
Uses ELM327 AT commands for proper device communication.

Usage:
    python scripts/godiag_gd101_elm327_sniffer.py --port COM2
    python scripts/godiag_gd101_elm327_sniffer.py --port COM2 --duration 60
"""

import sys
import os
import time
import argparse
import logging
from datetime import datetime
from typing import Optional, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


class GoDiagELM327Sniffer:
    """
    CAN Bus Sniffer for GODIAG GD101 using ELM327 AT commands
    """
    
    def __init__(self, port: str = "COM2", baudrate: int = 38400):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.is_connected = False
        self.captured_frames = []
        self.start_time = 0.0
        
        try:
            import serial
            self.serial = serial
        except ImportError:
            raise ImportError("pyserial required: pip install pyserial")
    
    def connect(self) -> bool:
        """Connect to GODIAG GD101 and initialize ELM327"""
        try:
            print(f"Connecting to GODIAG GD101 on {self.port}...")
            
            # Try different baud rates
            for baud in [38400, 115200, 9600, 57600]:
                try:
                    self.serial_conn = self.serial.Serial(
                        port=self.port,
                        baudrate=baud,
                        timeout=2,
                        bytesize=self.serial.EIGHTBITS,
                        parity=self.serial.PARITY_NONE,
                        stopbits=self.serial.STOPBITS_ONE
                    )
                    
                    # Reset device
                    self._send_at_command("ATZ", timeout=3)
                    time.sleep(1)
                    
                    # Check if ELM327 responds
                    response = self._send_at_command("ATI")
                    if response and ("ELM" in response or "OBD" in response or ">" in response):
                        print(f"Connected at {baud} baud")
                        print(f"Device: {response.strip()}")
                        self.baudrate = baud
                        break
                    else:
                        self.serial_conn.close()
                        continue
                        
                except Exception:
                    continue
            
            if not self.serial_conn or not self.serial_conn.is_open:
                print("Failed to connect - trying default settings")
                self.serial_conn = self.serial.Serial(
                    port=self.port,
                    baudrate=38400,
                    timeout=2
                )
            
            # Initialize ELM327 for CAN monitoring
            print("\nInitializing ELM327 for CAN bus monitoring...")
            
            # Basic setup
            self._send_at_command("ATE0")      # Echo off
            self._send_at_command("ATL0")      # Linefeeds off
            self._send_at_command("ATS0")      # Spaces off
            self._send_at_command("ATH1")      # Headers on (show CAN IDs)
            self._send_at_command("ATSP6")     # Protocol 6 = ISO 15765-4 CAN (11-bit, 500kbps)
            
            # Try to set CAN monitoring mode
            self._send_at_command("ATCAF0")    # CAN auto formatting off
            self._send_at_command("ATD0")      # DLC display off
            
            # Set CAN filter to receive all messages
            self._send_at_command("ATCF000")   # CAN filter
            self._send_at_command("ATCM000")   # CAN mask (receive all)
            
            self.is_connected = True
            print("ELM327 initialized successfully")
            
            self._print_obd2_pinout()
            
            return True
            
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from device"""
        if self.serial_conn:
            try:
                self._send_at_command("ATZ")  # Reset
                self.serial_conn.close()
            except:
                pass
        self.is_connected = False
        print("Disconnected from GODIAG GD101")
    
    def start_monitoring(self, duration: float = 30, output_file: str = None):
        """Start CAN bus monitoring"""
        if not self.is_connected:
            print("Not connected!")
            return
        
        print("\n" + "=" * 60)
        print("GODIAG GD101 CAN BUS MONITOR - OBD2 16-PIN")
        print("=" * 60)
        print(f"Port: {self.port}")
        print(f"Duration: {duration}s")
        print("=" * 60)
        print("Press Ctrl+C to stop\n")
        
        self.start_time = time.time()
        self.captured_frames = []
        
        # Open output file
        output_handle = None
        if output_file:
            output_handle = open(output_file, 'w')
            output_handle.write(f"# GODIAG GD101 CAN Capture - {datetime.now()}\n")
        
        try:
            # Method 1: Try CAN monitor mode (ATMA)
            print("Starting CAN monitor mode (ATMA)...")
            self.serial_conn.write(b'ATMA\r')
            self.serial_conn.flush()
            
            frame_count = 0
            unique_ids = set()
            
            while (time.time() - self.start_time) < duration:
                if self.serial_conn.in_waiting:
                    try:
                        line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                        
                        if line and line != '>' and not line.startswith('SEARCHING') and not line.startswith('NO DATA'):
                            timestamp = time.time() - self.start_time
                            
                            # Parse CAN frame (format: IIIDDDDDDDDDDDDDDD)
                            if len(line) >= 3:
                                try:
                                    # Try to extract CAN ID (first 3 chars for 11-bit)
                                    can_id = int(line[:3], 16)
                                    data = line[3:]
                                    
                                    frame_str = f"[{timestamp:.3f}] 0x{can_id:03X}: {data}"
                                    print(frame_str)
                                    
                                    self.captured_frames.append({
                                        'timestamp': timestamp,
                                        'id': can_id,
                                        'data': data
                                    })
                                    
                                    frame_count += 1
                                    unique_ids.add(can_id)
                                    
                                    if output_handle:
                                        output_handle.write(f"{frame_str}\n")
                                        output_handle.flush()
                                        
                                except ValueError:
                                    # Not a valid CAN frame, might be status message
                                    if line:
                                        print(f"[STATUS] {line}")
                                        
                    except Exception as e:
                        pass
                
                time.sleep(0.001)
            
            # Stop monitoring
            self.serial_conn.write(b'\r')  # Send CR to stop ATMA
            time.sleep(0.5)
            
        except KeyboardInterrupt:
            print("\nStopped by user")
            self.serial_conn.write(b'\r')
        
        finally:
            if output_handle:
                output_handle.close()
            
            # Print statistics
            print("\n" + "=" * 60)
            print("CAPTURE STATISTICS")
            print("=" * 60)
            print(f"Duration: {time.time() - self.start_time:.2f}s")
            print(f"Frames captured: {len(self.captured_frames)}")
            print(f"Unique CAN IDs: {len(unique_ids)}")
            if unique_ids:
                print("IDs found:")
                for cid in sorted(unique_ids):
                    print(f"  0x{cid:03X}")
            print("=" * 60)
    
    def send_obd2_request(self, pid: str = "0100"):
        """Send OBD2 request to wake up the bus"""
        print(f"\nSending OBD2 request: {pid}")
        response = self._send_at_command(pid, timeout=5)
        if response:
            print(f"Response: {response}")
        return response
    
    def _send_at_command(self, cmd: str, timeout: float = 2) -> str:
        """Send AT command and get response"""
        try:
            if not self.serial_conn:
                return ""
            
            # Clear buffer
            self.serial_conn.reset_input_buffer()
            
            # Send command
            self.serial_conn.write(f"{cmd}\r".encode())
            self.serial_conn.flush()
            
            # Read response
            response = ""
            start = time.time()
            
            while (time.time() - start) < timeout:
                if self.serial_conn.in_waiting:
                    data = self.serial_conn.read(self.serial_conn.in_waiting)
                    response += data.decode('utf-8', errors='ignore')
                    if '>' in response:
                        break
                time.sleep(0.05)
            
            return response.replace('\r', '\n').strip()
            
        except Exception as e:
            return ""
    
    def _print_obd2_pinout(self):
        """Print OBD2 pinout info"""
        print("\n" + "=" * 60)
        print("OBD2 16-PIN CAN BUS PINOUT")
        print("=" * 60)
        print("Pin 4:  Chassis Ground -> 0V")
        print("Pin 5:  Signal Ground  -> 0V")
        print("Pin 6:  CAN High       -> 2.5V")
        print("Pin 14: CAN Low        -> 2.5V")
        print("Pin 16: Battery +12V")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="GODIAG GD101 CAN Sniffer (ELM327)")
    parser.add_argument('--port', '-p', default='COM2', help='COM port')
    parser.add_argument('--duration', '-d', type=float, default=30, help='Duration in seconds')
    parser.add_argument('--output', '-o', default='', help='Output file')
    parser.add_argument('--wake', '-w', action='store_true', help='Send OBD2 request first')
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    sniffer = GoDiagELM327Sniffer(port=args.port)
    
    if not sniffer.connect():
        print("Failed to connect!")
        sys.exit(1)
    
    try:
        # Optionally wake up the bus with OBD2 request
        if args.wake:
            sniffer.send_obd2_request("0100")  # Supported PIDs
            time.sleep(1)
        
        output_file = args.output or f"can_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        sniffer.start_monitoring(duration=args.duration, output_file=output_file)
        
    finally:
        sniffer.disconnect()


if __name__ == "__main__":
    main()
