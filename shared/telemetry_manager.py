import time
import logging
import threading
import json
import random
import hashlib
import os
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from .build_info import BuildVerifier
except ImportError:
    class BuildVerifier:
        @staticmethod
        def get_build_id() -> str: return "UNKNOWN"

logger = logging.getLogger(__name__)

TELEMETRY_DISPLAY_NAME = "Anonymous Diagnostic Improvement Telemetry"
TELEMETRY_ENDPOINT = "https://telemetry.dacos.co.za/v1/heartbeat"

RESTRICT_INTEGRITY_FAIL    = "RESTRICT_INTEGRITY_FAIL"
RESTRICT_TELEMETRY_OFFLINE = "RESTRICT_TELEMETRY_OFFLINE"

# 7-day offline grace window (seconds)
OFFLINE_CACHE_TTL = 7 * 24 * 3600

# Local cache file — sits next to this module
_CACHE_FILE = Path(__file__).parent / ".telemetry_cache"


def _cache_write(ts: float) -> None:
    """Write last-verified timestamp to local cache (HMAC-stamped)."""
    try:
        secret = BuildVerifier.get_build_id() + "DACOS-ALPHA-SALT"
        sig = hashlib.sha256(f"{ts:.0f}{secret}".encode()).hexdigest()
        _CACHE_FILE.write_text(json.dumps({"ts": ts, "sig": sig}))
    except Exception as e:
        logger.debug(f"Telemetry cache write failed: {e}")


def _cache_read() -> Optional[float]:
    """Read and verify cached timestamp. Returns ts on success, None on tamper/missing."""
    try:
        data = json.loads(_CACHE_FILE.read_text())
        ts   = float(data["ts"])
        secret = BuildVerifier.get_build_id() + "DACOS-ALPHA-SALT"
        expected = hashlib.sha256(f"{ts:.0f}{secret}".encode()).hexdigest()
        if data.get("sig") != expected:
            return None
        return ts
    except Exception:
        return None


class TelemetryManager:
    """
    Manages anonymous diagnostic improvement telemetry.
    Enforces containment for Alpha:
      - DTC clearing / coding blocked if not verified within 7 days.
      - Heartbeat sent periodically; if server unreachable the local
        cache file extends the grace window for OFFLINE_CACHE_TTL seconds.
    """
    STATE_STOPPED  = "STOPPED"
    STATE_STARTING = "STARTING"
    STATE_RUNNING  = "RUNNING"

    ACK_OK       = "ACK_OK"
    ACK_REJECTED = "ACK_REJECTED"
    ACK_TIMEOUT  = "ACK_TIMEOUT"

    def __init__(self):
        self.session_id              = f"sess_{int(time.time())}_{random.randint(1000, 9999)}"
        self._state                  = self.STATE_STOPPED
        self._lock                   = threading.Lock()
        self.pending_payloads        = []
        self._last_online_state      = True
        self._consecutive_failures   = 0
        self._circuit_open           = False

        # Last time we received a positive ACK (from server OR local cache)
        self.last_ack_time = self._load_cache_time()

        # Heartbeat thread
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self):
        self._state = self.STATE_RUNNING
        logger.info(f"{TELEMETRY_DISPLAY_NAME} started.")
        self._stop_event.clear()
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop, daemon=True, name="TelemetryHeartbeat"
        )
        self._heartbeat_thread.start()

    def stop(self):
        self._stop_event.set()
        self._state = self.STATE_STOPPED
        logger.info(f"{TELEMETRY_DISPLAY_NAME} stopped.")

    @property
    def is_running(self) -> bool:
        return self._state == self.STATE_RUNNING

    # ------------------------------------------------------------------
    # Heartbeat
    # ------------------------------------------------------------------

    def _heartbeat_loop(self):
        """Background thread: send heartbeat every 60 s while running."""
        interval = 60.0
        while not self._stop_event.wait(interval):
            if not self.is_running or self._circuit_open:
                break
            self.send_heartbeat()

    def send_heartbeat(self, user_hash: str = "anonymous") -> bool:
        if not self.is_running:
            return False

        if self._circuit_open:
            self.queue_diagnostic_event("heartbeat_queued", {
                "user_hash": user_hash, "timestamp": time.time()
            })
            return False

        payload = {
            "type":       "heartbeat",
            "session_id": self.session_id,
            "build_id":   BuildVerifier.get_build_id(),
            "timestamp":  time.time(),
            "user_hash":  user_hash,
        }

        success = self._send_to_server(payload)

        if success:
            self._consecutive_failures = 0
            now = time.time()
            with self._lock:
                self.last_ack_time = now
            _cache_write(now)
            return True

        self._consecutive_failures += 1
        if self._consecutive_failures >= 3:
            self._circuit_open = True
            logger.warning("Telemetry server unreachable — offline mode, retries suspended")
        return False

    def _send_to_server(self, payload: Dict[str, Any]) -> bool:
        """
        Attempt a real HTTP POST to TELEMETRY_ENDPOINT.
        Falls back gracefully if the server is unreachable — this is expected
        during the Alpha period before the endpoint is deployed.
        """
        # Reject immediately for unknown builds
        if payload.get("build_id") == "UNKNOWN":
            logger.warning("Telemetry rejected: UNKNOWN build ID")
            return False

        try:
            import urllib.request
            import urllib.error
            data = json.dumps(payload).encode("utf-8")
            req  = urllib.request.Request(
                TELEMETRY_ENDPOINT,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception as e:
            # Server doesn't exist yet during Alpha — not an error worth logging loudly
            logger.debug(f"Telemetry server unreachable: {e}")
            return False

    # ------------------------------------------------------------------
    # Online status
    # ------------------------------------------------------------------

    def _load_cache_time(self) -> float:
        """Initialise last_ack_time from cache or current time."""
        cached = _cache_read()
        if cached is not None:
            logger.debug(f"Telemetry: loaded cache timestamp (age {(time.time()-cached)/3600:.1f}h)")
            return cached
        # First run — write now so we start with a full 7-day window
        now = time.time()
        _cache_write(now)
        return now

    @property
    def is_online(self) -> bool:
        """
        True if the build has been verified within the last OFFLINE_CACHE_TTL seconds.
        Combines the in-memory last_ack_time with the on-disk cache so the window
        survives restarts.
        """
        if not self.is_running:
            self._last_online_state = False
            return False

        # Prefer in-memory (most recent) but also check disk cache
        mem_ok  = (time.time() - self.last_ack_time) < OFFLINE_CACHE_TTL
        disk_ts = _cache_read()
        disk_ok = disk_ts is not None and (time.time() - disk_ts) < OFFLINE_CACHE_TTL

        current_status = mem_ok or disk_ok

        if self._last_online_state and not current_status:
            logger.warning(
                f"Restricted Mode: offline cache expired "
                f"(last ACK {(time.time()-self.last_ack_time)/3600:.1f}h ago, "
                f"7-day limit exceeded)"
            )
            self.queue_diagnostic_event("restriction_triggered", {
                "reason":   RESTRICT_TELEMETRY_OFFLINE,
                "last_ack": self.last_ack_time,
                "timeout":  OFFLINE_CACHE_TTL,
            })

        self._last_online_state = current_status
        return current_status

    @property
    def is_in_grace_period(self) -> bool:
        """Kept for backwards compatibility — always False; grace is handled by is_online."""
        return False

    # ------------------------------------------------------------------
    # Capability snapshot / events
    # ------------------------------------------------------------------

    def send_capability_snapshot(self, snapshot_data: Dict[str, Any]) -> bool:
        if not self.is_running:
            return False
        payload = {
            "type":       "capability_snapshot",
            "session_id": self.session_id,
            "build_id":   BuildVerifier.get_build_id(),
            "timestamp":  time.time(),
            "data":       snapshot_data,
        }
        return self._send_to_server(payload)

    def queue_diagnostic_event(self, event_type: str, data: Dict[str, Any]):
        payload = {
            "type":      "event",
            "event":     event_type,
            "data":      data,
            "timestamp": time.time(),
        }
        self.pending_payloads.append(payload)
        if len(self.pending_payloads) > 500:
            self.pending_payloads.pop(0)
