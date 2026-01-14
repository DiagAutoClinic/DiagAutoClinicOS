import sys
import json
import ctypes
import os
import logging

# Ensure we can find the shared modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from shared.j2534_passthru import J2534PassThru, J2534Protocol, J2534Message, J2534Status

# Configure logging to stderr so it doesn't pollute stdout (which is used for JSON communication)
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("J2534Bridge")

class J2534Bridge:
    def __init__(self):
        self.device = None
        self.running = True

    def run(self):
        logger.info("J2534 Bridge (32-bit) Started")
        while self.running:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                response = self.handle_request(request)
                
                # Send response as JSON line
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                
            except json.JSONDecodeError:
                self.send_error("Invalid JSON")
            except Exception as e:
                self.send_error(str(e))
                logger.error(f"Bridge Error: {e}", exc_info=True)

    def send_error(self, message):
        response = {"status": "error", "error": message}
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()

    def handle_request(self, req):
        cmd = req.get("cmd")
        
        if cmd == "load_driver":
            path = req.get("path")
            return self.load_driver(path)
            
        elif cmd == "open":
            return self.open_device()
            
        elif cmd == "close":
            return self.close_device()
            
        elif cmd == "connect":
            protocol = req.get("protocol") # "ISO15765", etc.
            baudrate = req.get("baudrate", 500000)
            flags = req.get("flags", 0)
            return self.connect(protocol, baudrate, flags)
            
        elif cmd == "disconnect":
            channel_id = req.get("channel_id")
            return self.disconnect(channel_id)
            
        elif cmd == "send_message":
            channel_id = req.get("channel_id")
            data_hex = req.get("data") # hex string
            protocol_id = req.get("protocol_id")
            flags = req.get("flags", 0)
            return self.send_message(channel_id, data_hex, protocol_id, flags)
            
        elif cmd == "read_message":
            channel_id = req.get("channel_id")
            timeout = req.get("timeout", 100)
            return self.read_message(channel_id, timeout)
            
        elif cmd == "exit":
            self.running = False
            return {"status": "ok", "message": "Exiting"}
            
        else:
            return {"status": "error", "error": f"Unknown command: {cmd}"}

    def load_driver(self, path):
        try:
            self.device = J2534PassThru(dll_path=path)
            if self.device.dll_handle:
                return {"status": "ok", "message": "Driver loaded"}
            else:
                return {"status": "error", "error": self.device.init_error or "Failed to load driver"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def open_device(self):
        if not self.device: return {"status": "error", "error": "No driver loaded"}
        if self.device.open():
            return {"status": "ok", "device_id": self.device.device_id.value}
        else:
            return {"status": "error", "error": self.device.get_last_error()}

    def close_device(self):
        if not self.device: return {"status": "error", "error": "No driver loaded"}
        if self.device.close():
            return {"status": "ok"}
        else:
            return {"status": "error", "error": self.device.get_last_error()}

    def connect(self, protocol_name, baudrate, flags):
        if not self.device: return {"status": "error", "error": "No driver loaded"}
        
        # Map string to Enum
        try:
            proto = getattr(J2534Protocol, protocol_name)
        except AttributeError:
            return {"status": "error", "error": f"Invalid protocol: {protocol_name}"}
            
        channel_id = self.device.connect(proto, flags, baudrate)
        if channel_id > 0:
            return {"status": "ok", "channel_id": channel_id}
        else:
            return {"status": "error", "error": self.device.get_last_error()}

    def disconnect(self, channel_id):
        if not self.device: return {"status": "error", "error": "No driver loaded"}
        if self.device.disconnect(channel_id):
            return {"status": "ok"}
        else:
            return {"status": "error", "error": self.device.get_last_error()}

    def send_message(self, channel_id, data_hex, protocol_id, flags):
        if not self.device: return {"status": "error", "error": "No driver loaded"}
        
        try:
            data = bytes.fromhex(data_hex)
            proto = J2534Protocol(protocol_id)
            msg = J2534Message(proto, flags, data)
            
            if self.device.send_message(channel_id, msg):
                return {"status": "ok"}
            else:
                return {"status": "error", "error": self.device.get_last_error()}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def read_message(self, channel_id, timeout):
        if not self.device: return {"status": "error", "error": "No driver loaded"}
        
        msg = self.device.read_message(channel_id, timeout)
        if msg:
            return {
                "status": "ok",
                "found": True,
                "data": msg.data.hex(),
                "protocol_id": msg.protocol.value,
                "rx_status": msg.rx_status,
                "timestamp": msg.timestamp
            }
        else:
            return {"status": "ok", "found": False}

if __name__ == "__main__":
    bridge = J2534Bridge()
    bridge.run()
