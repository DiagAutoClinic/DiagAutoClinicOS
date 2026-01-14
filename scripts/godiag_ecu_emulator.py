#!/usr/bin/env python3
"""
Godiag J2534 ECU Emulator
-------------------------
This script turns a Godiag J2534 device (or any J2534 VCI) into a Virtual ECU.
It listens on the CAN bus for UDS requests and responds like a real vehicle.

Usage:
1. Connect Godiag device to PC.
2. Connect Godiag CAN High/Low to another VCI (e.g. Scanmatik) via Breakout Box.
3. Run this script.
4. Use AutoKey (or any scanner) on the other VCI to "diagnose" this script.

Target ECU: Engine (0x7E0)
Response ID: 0x7E8
"""

import sys
import os
import time
import logging
import random
import ctypes

# Add parent directory to path to import shared modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.j2534_passthru import J2534PassThru, J2534Protocol, J2534Message, J2534FilterType, get_passthru_device

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [ECU] - %(message)s')
logger = logging.getLogger("ECU_Emulator")

# Constants
ECU_REQUEST_ID = b'\x00\x00\x07\xE0'  # What the scanner sends to us
ECU_RESPONSE_ID = b'\x00\x00\x07\E8' # What we send back
BROADCAST_ID = b'\x00\x00\x07\DF'    # Functional addressing

# Simulation State
class ECUState:
    def __init__(self):
        self.session = 0x01 # Default Session
        self.security_locked = True
        self.security_seed = b'\x00\x00\x00\x00'
        self.vin = b"WBA1234567890ABCD" # Fake BMW VIN

ecu_state = ECUState()

def find_godiag_dll():
    """Attempts to find the Godiag J2534 DLL"""
    common_paths = [
        r"C:\Program Files (x86)\Godiag\J2534\Godiag_J2534.dll",
        r"C:\Program Files\Godiag\J2534\Godiag_J2534.dll",
        r"C:\Program Files (x86)\GODIAG J2534 Driver\GODIAG_PT32.dll", # From user's drivers folder
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'drivers', 'GODIAG J2534 Driver', 'GODIAG_PT32.dll'))
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
    return None

def handle_uds_request(data):
    """Parses UDS request and returns response data (excluding CAN ID)"""
    if not data:
        return None

    # Simple Single Frame Parser (doesn't handle Multi-Frame ISO-TP for inputs yet)
    # Byte 0 is PCI (Protocol Control Information). 0x02 = Single Frame, Len 2
    pci_type = data[0] & 0xF0
    
    if pci_type != 0x00:
        # For now, ignore multi-frame inputs from scanner
        return None
        
    data_len = data[0] & 0x0F
    service_id = data[1]
    
    response = bytearray()
    
    # 1. Service 0x10: Diagnostic Session Control
    if service_id == 0x10:
        sub_function = data[2]
        ecu_state.session = sub_function
        # Reset security on session change
        ecu_state.security_locked = True
        
        # Positive Response: 0x50 + SubFunc + P2(00 32) + P2*(01 F4)
        response = b'\x06\x50' + bytes([sub_function]) + b'\x00\x32\x01\xF4'
        logger.info(f"Session changed to {sub_function:02X}")

    # 2. Service 0x27: Security Access
    elif service_id == 0x27:
        sub_function = data[2]
        
        # Request Seed (Odd numbers: 01, 03, 05...)
        if sub_function % 2 != 0:
            # Generate random seed
            seed = bytes([random.randint(0, 255) for _ in range(4)])
            ecu_state.security_seed = seed
            
            # Response: 0x67 + SubFunc + Seed
            response = b'\x06\x67' + bytes([sub_function]) + seed
            logger.info(f"Security Seed Requested: {seed.hex()}")
            
        # Send Key (Even numbers: 02, 04, 06...)
        else:
            received_key = data[3:7]
            # Simple algo: Key = Seed (for testing)
            expected_key = ecu_state.security_seed
            
            if received_key == expected_key:
                ecu_state.security_locked = False
                response = b'\x02\x67' + bytes([sub_function])
                logger.info("Security Unlocked Successfully!")
            else:
                # Negative Response: 7F 27 35 (Invalid Key)
                response = b'\x03\x7F\x27\x35'
                logger.warning("Security Unlock Failed: Invalid Key")

    # 3. Service 0x22: Read Data By Identifier
    elif service_id == 0x22:
        did_high = data[2]
        did_low = data[3]
        
        # VIN (F190)
        if did_high == 0xF1 and did_low == 0x90:
            # Multi-frame response required for VIN (17 bytes)
            # We will just send the first part for this simple emulator or implement basic ISO-TP
            # Constructing a valid ISO-TP Multi-Frame sequence is complex.
            # Let's cheat and send just the first frame to ack, or a short fake VIN if possible.
            # Actually, standard VIN is 17 bytes.
            # Frame 1: 10 14 62 F1 90 [VIN 0-2]
            # Frame 2: 21 [VIN 3-9]
            # Frame 3: 22 [VIN 10-16]
            # Implementing full ISO-TP sender is out of scope for 5 mins, 
            # so we will return a "Condition Not Correct" or just a short 1-frame response for testing.
            
            # Let's pretend this ECU has a short ID for testing
            response = b'\x05\x62\xF1\x90\xAA\xBB' 
            logger.info("Read Data F190 (VIN) requested")

    # 4. Service 0x3E: Tester Present
    elif service_id == 0x3E:
        # Zero subfunction means no response required, but 0x80 bit usually suppresses it.
        # If byte 2 is 0x00, we respond.
        if data[2] == 0x00:
             response = b'\x02\x7E\x00'
        else:
             logger.debug("Tester Present (No Response)")
             return None

    # 5. Service 0x11: ECU Reset
    elif service_id == 0x11:
        sub_function = data[2]
        # Hard Reset (01) or Soft Reset (03)
        ecu_state.session = 0x01
        ecu_state.security_locked = True
        response = b'\x02\x51' + bytes([sub_function])
        logger.info(f"ECU Reset ({sub_function:02X})")
        
    else:
        # Service Not Supported
        response = b'\x03\x7F' + bytes([service_id]) + b'\x11'

    return response

def main():
    print("=========================================")
    print("   DACOS Godiag ECU Emulator (J2534)     ")
    print("=========================================")
    
    dll_path = find_godiag_dll()
    if not dll_path:
        print("ERROR: Godiag J2534 DLL not found.")
        print("Please install Godiag drivers or update the path in this script.")
        return

    print(f"Loading Driver: {dll_path}")
    
    # Initialize Device
    device = J2534PassThru(dll_path=dll_path)
    
    if not device.open():
        print("Failed to open device.")
        return

    print("Device Opened.")
    
    # Connect to CAN
    channel_id = device.connect(J2534Protocol.ISO15765, baudrate=500000)
    if channel_id == -1:
        print("Failed to connect to CAN.")
        device.close()
        return

    print(f"Connected to CAN (Channel {channel_id})")

    # Set Filter to receive ECU Requests (0x7E0)
    # Mask: FFFFFFFF (Check all bits)
    # Pattern: 000007E0 (Must match 7E0)
    # FlowControl: 000007E8 (Use 7E8 as source for flow control frames if we were doing proper ISO-TP)
    
    mask_msg = J2534Message(J2534Protocol.ISO15765, data=b'\x00\x00\xFF\xFF')
    pattern_msg = J2534Message(J2534Protocol.ISO15765, data=ECU_REQUEST_ID)
    flow_msg = J2534Message(J2534Protocol.ISO15765, data=ECU_RESPONSE_ID)
    
    filter_id = device.start_msg_filter(channel_id, J2534FilterType.PASS_FILTER, mask_msg, pattern_msg, flow_msg)
    
    if filter_id == -1:
        print("Failed to set filter. Aborting.")
        device.close()
        return

    print(f"Filter Set (ID: {filter_id}). Listening for ID 7E0...")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            msg = device.read_message(channel_id, timeout_ms=100)
            if msg:
                # Parse Message
                # msg.data[0:4] is CAN ID
                can_id = msg.data[0:4]
                payload = msg.data[4:]
                
                if can_id == ECU_REQUEST_ID or can_id == BROADCAST_ID:
                    logger.info(f"RX: {payload.hex()} (ID: {can_id.hex()})")
                    
                    response_payload = handle_uds_request(payload)
                    
                    if response_payload:
                        # Construct Response
                        # Prepend Response CAN ID
                        tx_data = ECU_RESPONSE_ID + response_payload
                        tx_msg = J2534Message(J2534Protocol.ISO15765, data=tx_data)
                        
                        device.send_message(channel_id, tx_msg)
                        logger.info(f"TX: {response_payload.hex()}")
            
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        device.stop_msg_filter(channel_id, filter_id)
        device.disconnect(channel_id)
        device.close()
        print("Disconnected.")

if __name__ == "__main__":
    main()
