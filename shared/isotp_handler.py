#!/usr/bin/env python3
"""
ISO-TP (ISO 15765-2) Protocol Handler
Provides Segmentation and Reassembly (SAR) for UDS over CAN.
"""

import time
import logging
from typing import List, Optional, Tuple, Union
from enum import Enum

logger = logging.getLogger(__name__)

class IsoTpFrameType(Enum):
    SINGLE_FRAME = 0
    FIRST_FRAME = 1
    CONSECUTIVE_FRAME = 2
    FLOW_CONTROL = 3

class IsoTpHandler:
    """
    Handles ISO 15765-2 protocol (Segmentation and Reassembly).
    Works with any transport that provides send_can_frame and read_can_frame methods.
    """
    
    def __init__(self, transport_interface, tx_id: int, rx_id: int, timeout_ms: int = 1000):
        """
        :param transport_interface: Object with send_message(id, data) and read_message(timeout)
        :param tx_id: CAN ID to transmit on (e.g., 0x7E0)
        :param rx_id: CAN ID to listen to (e.g., 0x7E8)
        :param timeout_ms: Default timeout for operations
        """
        self.transport = transport_interface
        self.tx_id = tx_id
        self.rx_id = rx_id
        self.timeout = timeout_ms / 1000.0
        
        # ISO-TP Constants
        self.block_size = 0  # 0 = Send all without waiting for FC (unless ECU specifies otherwise)
        self.st_min = 0      # Minimum separation time
        self.max_wft = 0     # Max wait frame transmissions

    def send_data(self, data: bytes) -> bool:
        """
        Send data using ISO-TP (handles segmentation if needed)
        """
        length = len(data)
        
        if length <= 7:
            return self._send_single_frame(data)
        else:
            return self._send_multi_frame(data)

    def receive_data(self, timeout_ms: Optional[int] = None) -> Optional[bytes]:
        """
        Receive data using ISO-TP (handles reassembly)
        """
        timeout = (timeout_ms / 1000.0) if timeout_ms else self.timeout
        start_time = time.time()
        
        # Wait for First Frame or Single Frame
        while time.time() - start_time < timeout:
            msg = self.transport.read_message(timeout_ms=int((timeout - (time.time() - start_time)) * 1000))
            
            if not msg or not msg.data:
                continue
                
            # Filter by ID if transport doesn't do it for us
            # Note: J2534Message data usually includes the 4-byte CAN ID at the start for ISO15765
            # We need to adapt based on the transport's data format.
            # Assuming transport returns (can_id, data_bytes) or just data_bytes if filtered.
            # For this implementation, let's assume the transport abstraction returns JUST the CAN payload
            # or we need to parse it. 
            # Let's assume the transport deals with the raw J2534 format and gives us the relevant bytes.
            # Actually, looking at J2534PassThru, read_message returns a J2534Message with .data
            # .data includes CAN ID (4 bytes) + Payload.
            
            can_id_bytes = msg.data[:4]
            payload = msg.data[4:]
            
            can_id = int.from_bytes(can_id_bytes, 'big')
            
            # Simple check for 11-bit ID match (ignoring flags for now)
            if (can_id & 0x7FF) != (self.rx_id & 0x7FF):
                continue
                
            pci_byte = payload[0]
            frame_type = (pci_byte & 0xF0) >> 4
            
            if frame_type == IsoTpFrameType.SINGLE_FRAME.value:
                length = pci_byte & 0x0F
                if length == 0: # CAN FD or escaped
                    length = payload[1]
                    return payload[2:2+length]
                return payload[1:1+length]
                
            elif frame_type == IsoTpFrameType.FIRST_FRAME.value:
                return self._handle_first_frame(payload)
                
        return None

    def _send_single_frame(self, data: bytes) -> bool:
        """Send a Single Frame (SF)"""
        # PCI: 0x0L (L = Length)
        pci = 0x00 | len(data)
        payload = bytes([pci]) + data
        # Pad with 0xAA or 0x00 to 8 bytes (standard practice, though not strictly required by all ECUs)
        padding = b'\xAA' * (8 - len(payload))
        full_payload = payload + padding
        
        return self._send_can_frame(full_payload)

    def _send_multi_frame(self, data: bytes) -> bool:
        """Send a Multi-Frame message (FF + CFs)"""
        length = len(data)
        
        # 1. Send First Frame (FF)
        # PCI: 0x1L LL (L = Length, 12 bits)
        pci_hi = 0x10 | ((length >> 8) & 0x0F)
        pci_lo = length & 0xFF
        
        # First 6 bytes of data
        payload = bytes([pci_hi, pci_lo]) + data[:6]
        if not self._send_can_frame(payload):
            return False
            
        # 2. Wait for Flow Control (FC)
        if not self._wait_for_flow_control():
            logger.error("ISO-TP: Timeout waiting for Flow Control")
            return False
            
        # 3. Send Consecutive Frames (CF)
        offset = 6
        sn = 1 # Sequence Number (starts at 1)
        
        while offset < length:
            chunk = data[offset:offset+7]
            pci = 0x20 | (sn & 0x0F)
            payload = bytes([pci]) + chunk
            
            # Pad last frame
            if len(payload) < 8:
                payload += b'\xAA' * (8 - len(payload))
                
            if not self._send_can_frame(payload):
                return False
                
            offset += 7
            sn = (sn + 1) & 0x0F
            
            # STmin delay
            if self.st_min > 0:
                time.sleep(self.st_min / 1000.0)
                
        return True

    def _wait_for_flow_control(self) -> bool:
        """Wait for Flow Control (FC) frame"""
        start_time = time.time()
        while time.time() - start_time < 1.0: # 1s timeout for FC
            msg = self.transport.read_message(timeout_ms=100)
            if not msg: continue
            
            can_id = int.from_bytes(msg.data[:4], 'big')
            if (can_id & 0x7FF) != (self.rx_id & 0x7FF): continue
            
            payload = msg.data[4:]
            pci = payload[0]
            frame_type = (pci & 0xF0) >> 4
            
            if frame_type == IsoTpFrameType.FLOW_CONTROL.value:
                flow_status = pci & 0x0F
                if flow_status == 0: # Continue to send
                    self.block_size = payload[1]
                    st_min_raw = payload[2]
                    
                    # Parse STmin
                    if st_min_raw <= 0x7F:
                        self.st_min = st_min_raw # ms
                    elif 0xF1 <= st_min_raw <= 0xF9:
                        self.st_min = (st_min_raw - 0xF0) * 0.1 # 100us units
                    else:
                        self.st_min = 0
                        
                    return True
                elif flow_status == 1: # Wait
                    time.sleep(0.1)
                    continue
                elif flow_status == 2: # Overflow
                    logger.error("ISO-TP: FC Overflow")
                    return False
                    
        return False

    def _handle_first_frame(self, payload: bytes) -> Optional[bytes]:
        """Handle First Frame and reception of Consecutive Frames"""
        # Parse Length
        length = ((payload[0] & 0x0F) << 8) | payload[1]
        data = bytearray(payload[2:])
        
        # Send Flow Control (CTS - Clear To Send)
        # PCI: 30 00 00 (FC, BS=0, STmin=0)
        fc_frame = b'\x30\x00\x00' + (b'\xAA' * 5)
        self._send_can_frame(fc_frame)
        
        # Receive Consecutive Frames
        next_sn = 1
        start_time = time.time()
        
        while len(data) < length:
            if time.time() - start_time > self.timeout:
                logger.error("ISO-TP: Timeout waiting for CF")
                return None
                
            msg = self.transport.read_message(timeout_ms=int(self.timeout * 1000))
            if not msg: continue
            
            can_id = int.from_bytes(msg.data[:4], 'big')
            if (can_id & 0x7FF) != (self.rx_id & 0x7FF): continue
            
            cf_payload = msg.data[4:]
            pci = cf_payload[0]
            frame_type = (pci & 0xF0) >> 4
            
            if frame_type == IsoTpFrameType.CONSECUTIVE_FRAME.value:
                sn = pci & 0x0F
                if sn != next_sn:
                    logger.warning(f"ISO-TP: SN Mismatch (Exp: {next_sn}, Got: {sn})")
                    # In strict mode we might abort, but let's try to continue or just log
                
                chunk_len = min(7, length - len(data))
                data.extend(cf_payload[1:1+chunk_len])
                next_sn = (next_sn + 1) & 0x0F
                
        return bytes(data)

    def _send_can_frame(self, payload: bytes) -> bool:
        """Helper to wrap transport send"""
        # Construct J2534 CAN frame (ID + Data)
        # Assuming 11-bit ID for now
        can_id_bytes = self.tx_id.to_bytes(4, 'big')
        full_data = can_id_bytes + payload
        
        # We need a dummy message object structure that the transport expects
        # The transport abstraction needs to be compatible.
        # For now, we assume the transport has a simple 'send_raw(data)' or we construct the J2534Message here
        # But J2534Message requires imports. Let's make this class dependent on the protocol.
        
        # Ideally, we should import J2534Message here or pass a factory.
        # To keep it simple, we'll assume the transport has a 'send_can(id, data)' method
        # OR we just pass the raw bytes if the transport expects that.
        
        # Let's try to use the 'send_message' signature from J2534PassThru
        # It expects a J2534Message object.
        
        from shared.j2534_passthru import J2534Message, J2534Protocol
        
        msg = J2534Message(J2534Protocol.ISO15765, data=full_data)
        # We need the channel_id. The transport interface should probably hold the channel_id.
        
        return self.transport.send_to_channel(msg)

