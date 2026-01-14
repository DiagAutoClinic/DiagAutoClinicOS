import subprocess
import json
import os
import sys
import logging
import threading
import time
from typing import Optional, Dict
from shared.j2534_passthru import J2534PassThru, J2534Protocol, J2534Message, J2534Status

logger = logging.getLogger(__name__)

class J2534BridgeClient(J2534PassThru):
    """
    Client that communicates with a 32-bit J2534 Bridge process.
    Implements the same interface as J2534PassThru.
    """
    def __init__(self, dll_path: str, python32_path: str):
        self.dll_path = dll_path
        self.python32_path = python32_path
        self.process = None
        self._is_open = False
        self.channels: Dict[int, J2534Protocol] = {}
        self.device_id = None
        self.last_error = ""
        self.lock = threading.Lock()
        
        # Determine path to bridge script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.bridge_script = os.path.join(current_dir, "j2534_bridge.py")

        self._start_process()

    def _start_process(self):
        try:
            logger.info(f"Starting J2534 Bridge process: {self.python32_path}")
            self.process = subprocess.Popen(
                [self.python32_path, self.bridge_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=sys.stderr # Forward logs to console
            )
            
            # Load the driver immediately
            resp = self._send_command({"cmd": "load_driver", "path": self.dll_path})
            if resp.get("status") != "ok":
                raise Exception(f"Failed to load driver in bridge: {resp.get('error')}")
                
        except Exception as e:
            logger.error(f"Failed to start bridge: {e}")
            self.process = None
            raise

    def __del__(self):
        """Ensure subprocess is killed if client is garbage collected"""
        if self.process:
            try:
                self.process.terminate()
                # Give it a moment to die gracefully
                try:
                    self.process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    self.process.kill()
            except Exception:
                pass

    def _send_command(self, cmd_dict: dict) -> dict:
        with self.lock:
            if not self.process:
                return {"status": "error", "error": "Bridge process not running"}
            
            try:
                json_str = json.dumps(cmd_dict) + "\n"
                self.process.stdin.write(json_str.encode('utf-8'))
                self.process.stdin.flush()
                
                response_line = self.process.stdout.readline().decode('utf-8').strip()
                if not response_line:
                    return {"status": "error", "error": "Bridge process closed connection"}
                    
                return json.loads(response_line)
            except Exception as e:
                logger.error(f"Bridge communication error: {e}")
                return {"status": "error", "error": str(e)}

    def open(self) -> bool:
        resp = self._send_command({"cmd": "open"})
        if resp.get("status") == "ok":
            self._is_open = True
            self.device_id = resp.get("device_id")
            return True
        else:
            self.last_error = resp.get("error", "Unknown error")
            return False

    def close(self) -> bool:
        resp = self._send_command({"cmd": "close"})
        self._is_open = False
        
        # Also terminate the process cleanly
        self._send_command({"cmd": "exit"})
        if self.process:
            self.process.terminate()
            self.process = None
            
        return resp.get("status") == "ok"

    def connect(self, protocol: J2534Protocol, flags: int = 0, baudrate: int = 500000) -> int:
        resp = self._send_command({
            "cmd": "connect",
            "protocol": protocol.name,
            "flags": flags,
            "baudrate": baudrate
        })
        
        if resp.get("status") == "ok":
            channel_id = resp.get("channel_id")
            self.channels[channel_id] = protocol
            return channel_id
        else:
            self.last_error = resp.get("error", "Unknown error")
            return -1

    def disconnect(self, channel_id: int) -> bool:
        resp = self._send_command({"cmd": "disconnect", "channel_id": channel_id})
        if resp.get("status") == "ok":
            if channel_id in self.channels:
                del self.channels[channel_id]
            return True
        else:
            self.last_error = resp.get("error", "Unknown error")
            return False

    def send_message(self, channel_id: int, message: J2534Message, timeout_ms: int = 1000) -> bool:
        resp = self._send_command({
            "cmd": "send_message",
            "channel_id": channel_id,
            "data": message.data.hex(),
            "protocol_id": message.protocol.value,
            "flags": message.tx_flags
        })
        return resp.get("status") == "ok"

    def read_message(self, channel_id: int, timeout_ms: int = 1000) -> Optional[J2534Message]:
        resp = self._send_command({
            "cmd": "read_message",
            "channel_id": channel_id,
            "timeout": timeout_ms
        })
        
        if resp.get("status") == "ok" and resp.get("found"):
            data = bytes.fromhex(resp.get("data"))
            msg = J2534Message(
                protocol=J2534Protocol(resp.get("protocol_id")),
                data=data
            )
            msg.rx_status = resp.get("rx_status")
            msg.timestamp = resp.get("timestamp")
            return msg
        return None

    def is_connected(self) -> bool:
        return self._is_open

    def get_last_error(self) -> str:
        return self.last_error
