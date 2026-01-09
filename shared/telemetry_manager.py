import time
import logging
import threading
import json
import random
from typing import Dict, Any, Optional

try:
    from .build_info import BuildVerifier
except ImportError:
    class BuildVerifier:
        @staticmethod
        def get_build_id() -> str: return "UNKNOWN"

logger = logging.getLogger(__name__)

# Rebranded Display Name
TELEMETRY_DISPLAY_NAME = "Anonymous Diagnostic Improvement Telemetry"
TELEMETRY_ENDPOINT = "https://telemetry.dacos-alpha.com/v1/heartbeat" # Mock URL

# Restricted Mode Trigger Reasons
RESTRICT_INTEGRITY_FAIL = "RESTRICT_INTEGRITY_FAIL"
RESTRICT_TELEMETRY_OFFLINE = "RESTRICT_TELEMETRY_OFFLINE"

class TelemetryManager:
    """
    Manages anonymous diagnostic improvement telemetry.
    Enforces online mode requirements for Alpha containment.
    """
    # Telemetry States
    STATE_STOPPED = "STOPPED"
    STATE_STARTING = "STARTING"
    STATE_RUNNING = "RUNNING"

    # Internal ACK Results
    ACK_OK = "ACK_OK"
    ACK_REJECTED = "ACK_REJECTED"
    ACK_TIMEOUT = "ACK_TIMEOUT"

    def __init__(self):
        self.last_ack_time = 0
        self.heartbeat_interval = 60.0 # Seconds
        self.ack_timeout = self.heartbeat_interval * 3 # Allow 3 missed heartbeats (180s)
        self.session_id = f"sess_{int(time.time())}_{random.randint(1000,9999)}"
        
        # internal state management
        self._state = self.STATE_STOPPED
        
        self._lock = threading.Lock()
        self.pending_payloads = []
        
        # Initial grace period (5 minutes)
        # Prevents false restriction due to slow network startup
        self.grace_period_start = time.time()
        self.grace_period_duration = 300.0 
        self.last_ack_time = time.time() 
        
        # Track last online state for transition emission
        self._last_online_state = True # Assume online at start due to grace period

    def start(self):
        self._state = self.STATE_STARTING
        # perform any startup checks here if needed
        self._state = self.STATE_RUNNING
        logger.info(f"{TELEMETRY_DISPLAY_NAME} service started (State: {self._state}).")
        # In a real app, this might start a background thread.
        # For Qt app, we usually use QTimer in the main thread or a worker.
        # Here we provide methods to be called by the main loop.

    def stop(self):
        self._state = self.STATE_STOPPED
        logger.info(f"{TELEMETRY_DISPLAY_NAME} service stopped.")

    @property
    def is_running(self) -> bool:
        """Returns True only if the service is fully in RUNNING state."""
        return self._state == self.STATE_RUNNING

    def send_heartbeat(self, user_hash: str = "anonymous") -> bool:
        """
        Sends a heartbeat with Build ID to verification server.
        Returns True if ACK received (mocked).
        """
        if not self.is_running:
            return False

        payload = {
            "type": "heartbeat",
            "session_id": self.session_id,
            "build_id": BuildVerifier.get_build_id(),
            "timestamp": time.time(),
            "user_hash": user_hash # Anonymized user identifier
        }

        # Simulate Network Request
        success = self._mock_network_request(payload)
        
        if success:
            with self._lock:
                self.last_ack_time = time.time()
            return True
        else:
            logger.warning("Telemetry heartbeat failed - No ACK received")
            return False

    def send_capability_snapshot(self, snapshot_data: Dict[str, Any]) -> bool:
        """
        Sends the session capability snapshot.
        """
        if not self.is_running:
            return False

        payload = {
            "type": "capability_snapshot",
            "session_id": self.session_id,
            "build_id": BuildVerifier.get_build_id(),
            "timestamp": time.time(),
            "data": snapshot_data
        }
        
        return self._mock_network_request(payload)

    def _mock_network_request(self, payload: Dict[str, Any]) -> bool:
        """
        Simulates sending data to the server.
        In Alpha, we just log it and return True most of the time.
        Returns True/False externally, but logs structured results internally.
        """
        # Log the "transmission" for verification
        logger.debug(f"Transmitting {TELEMETRY_DISPLAY_NAME}: {json.dumps(payload)}")
        
        result = self.ACK_OK
        
        # Simulate occasional network failure or server rejection if Build ID is bad
        if payload['build_id'] == "UNKNOWN":
            result = self.ACK_REJECTED
            logger.warning(f"Telemetry Request Failed: {result} (Invalid Build ID)")
            return False
            
        # In a real scenario, we might have ACK_TIMEOUT or other errors
        # For now, we assume success if build ID is valid
        logger.debug(f"Telemetry Request Success: {result}")
        return True

    @property
    def is_in_grace_period(self) -> bool:
        """Checks if the application is still within the startup grace period."""
        return (time.time() - self.grace_period_start) < self.grace_period_duration

    @property
    def is_online(self) -> bool:
        """
        Checks if the client is considered 'online' and verified.
        Emits restriction reason on transition from True -> False.
        """
        # If disabled/stopped, we are not online
        if not self.is_running:
            # We don't track transitions here as stopping is intentional
            self._last_online_state = False
            return False
            
        current_status = True
        
        # Check grace period first
        if self.is_in_grace_period:
            current_status = True
        
        # Check if ACK timeout has passed
        elif time.time() - self.last_ack_time > self.ack_timeout:
            current_status = False
        
        # Check for transition from True -> False
        if self._last_online_state and not current_status:
            logger.warning(f"Online Status Transition: True -> False (Reason: {RESTRICT_TELEMETRY_OFFLINE})")
            # Queue the restriction event so it's captured
            self.queue_diagnostic_event("restriction_triggered", {
                "reason": RESTRICT_TELEMETRY_OFFLINE,
                "last_ack": self.last_ack_time,
                "timeout": self.ack_timeout
            })
            
        self._last_online_state = current_status
        return current_status

    def queue_diagnostic_event(self, event_type: str, data: Dict[str, Any]):
        """
        Queues an anonymous diagnostic event (e.g., successful VIN decode).
        """
        payload = {
            "type": "event",
            "event": event_type,
            "data": data, # Ensure no PII is passed here
            "timestamp": time.time()
        }
        self.pending_payloads.append(payload)
        
        # Cap pending payloads to prevent memory leak
        if len(self.pending_payloads) > 500:
            self.pending_payloads.pop(0) # Drop oldest
            
        # In real impl, flush periodically
