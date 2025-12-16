"""
Real-time CAN Signal Decoder
"""

from typing import Dict, Any
import can
from dataclasses import dataclass
import threading
from queue import Queue
import time

class LiveCANDecoder:
    def __init__(self, database: RacelogicDatabase):
        self.database = database
        self.bus = None
        self.running = False
        self.message_queue = Queue()
        
    def connect(self, interface: str = 'socketcan', channel: str = 'can0'):
        """Connect to CAN interface"""
        try:
            self.bus = can.Bus(interface=interface, channel=channel)
            return True
        except:
            return False
    
    def start_decoding(self):
        """Start live decoding thread"""
        self.running = True
        thread = threading.Thread(target=self._decode_loop)
        thread.daemon = True
        thread.start()
    
    def _decode_loop(self):
        """Main decoding loop"""
        while self.running and self.bus:
            try:
                msg = self.bus.recv(timeout=0.1)
                if msg:
                    decoded = self.decode_frame(msg.arbitration_id, msg.data)
                    if decoded:
                        self.message_queue.put({
                            'timestamp': time.time(),
                            'can_id': msg.arbitration_id,
                            'data': decoded
                        })
            except:
                continue
    
    def decode_frame(self, can_id: int, data: bytes) -> Optional[Dict[str, float]]:
        """Decode a single CAN frame"""
        return self.database.decode_frame(can_id, data)
    
    def get_decoded_messages(self) -> List[Dict]:
        """Get all decoded messages from queue"""
        messages = []
        while not self.message_queue.empty():
            messages.append(self.message_queue.get())
        return messages