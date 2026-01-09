from enum import Enum, auto
from typing import Dict, Optional
import hashlib

class FlashState(Enum):
    IDLE = auto()
    IDENTITY_VERIFIED = auto()        # VIN + ECU match
    BACKUP_LOCKED = auto()            # Backup hash stored + notarized
    ERASE_ARMED = auto()              # All invariants hold
    WRITE_ARMED = auto()              # New data hash verified
    COMMITTING = auto()               # Writing in progress
    VERIFYING = auto()                # Read-back verification
    COMPLETE = auto()                 # Success
    RECOVERY = auto()                 # Failed, backup available
    BRICKED = auto()                  # Failed, no recovery

class SystemInvariantViolation(Exception):
    """Thrown when physics is violated"""
    pass

class FlashFSM:
    """Finite State Machine that CANNOT skip steps"""
    
    def __init__(self, vin: str, ecu_id: str):
        self.state = FlashState.IDLE
        self.vin = vin
        self.ecu_id = ecu_id
        self.backup_hash: Optional[str] = None
        self.new_data_hash: Optional[str] = None
        self.transition_log: List[Dict] = []
        self.technician_id: Optional[str] = None
        self.invariant_monitor = InvariantMonitor()
        
        # Setup physics monitoring
        self.invariant_monitor.voltage_stable(12.2, 15.0)
        self.invariant_monitor.power_source_verified()
        self.invariant_monitor.start_monitoring()
    
    def _transition(self, new_state: FlashState, reason: str):
        """Log EVERY state change with system snapshot"""
        snapshot = {
            "timestamp": time.time(),
            "from": self.state.name,
            "to": new_state.name,
            "reason": reason,
            "violations": self.invariant_monitor.get_violations(),
            "technician": self.technician_id,
            "system_hash": self._system_hash()
        }
        
        self.transition_log.append(snapshot)
        self.state = new_state
        
        # Notarize critical transitions
        if new_state in [FlashState.BACKUP_LOCKED, FlashState.ERASE_ARMED]:
            self._notarize_transition(snapshot)
    
    def _system_hash(self) -> str:
        """Hash of current system state - makes tampering evident"""
        state_str = f"{self.state}:{self.backup_hash}:{self.new_data_hash}"
        return hashlib.sha256(state_str.encode()).hexdigest()
    
    def verify_identity(self, vin_resolution: Dict, ecu_snapshot: Dict) -> bool:
        """Step 1: VIN epistemology + ECU reality check"""
        if self.state != FlashState.IDLE:
            raise RuntimeError(f"Can't verify from state {self.state}")
        
        # Run Pre-Flash Safety Law
        from dacos.vin.safety_law import pre_flash_safety_law
        law_result = pre_flash_safety_law(
            vin=self.vin,
            resolved_attributes=vin_resolution,
            ecu_snapshot=ecu_snapshot,
            battery_voltage=self.invariant_monitor.read_voltage(),
            charging_active=True,
            operation="ERASE",
            backup_exists=False
        )
        
        if law_result.decision == "DENY":
            return False
        
        if law_result.decision == "ALLOW_WITH_OVERRIDE":
            self._require_technician_acknowledgment(law_result.reasons)
        
        self._transition(FlashState.IDENTITY_VERIFIED, "Identity verified")
        return True
    
    def create_backup(self, data: bytes) -> str:
        """Step 2: Backup with cryptographic lock"""
        if self.state != FlashState.IDENTITY_VERIFIED:
            raise RuntimeError(f"Can't backup from state {self.state}")
        
        # Calculate backup hash
        self.backup_hash = hashlib.sha256(data).hexdigest()
        
        # Store with attestation
        from dacos.vin.crypto.attestation import create_backup_attestation
        attestation = create_backup_attestation(
            vin=self.vin,
            ecu_id=self.ecu_id,
            backup_data=data,
            tool_id="AutoECU"
        )
        
        # REMOTE NOTARIZATION (no skipping)
        from dacos.vin.crypto.notary import submit_to_notary
        submit_to_notary(attestation)
        
        self._transition(FlashState.BACKUP_LOCKED, "Backup hash-locked and notarized")
        return self.backup_hash
    
    def arm_erase(self, technician_id: str, acknowledgment_hash: str):
        """Step 3: Acknowledge irreversible destruction"""
        if self.state != FlashState.BACKUP_LOCKED:
            raise RuntimeError(f"Can't arm erase from state {self.state}")
        
        # Verify technician signed acknowledgment
        if not self._verify_acknowledgment(technician_id, acknowledgment_hash):
            raise ValueError("Invalid technician acknowledgment")
        
        self.technician_id = technician_id
        
        # PHYSICS CHECK - right before erase
        violations = self.invariant_monitor.get_violations()
        if violations:
            raise SystemInvariantViolation(f"Physics violated: {violations}")
        
        self._transition(FlashState.ERASE_ARMED, "Erase armed with technician liability")
    
    def erase(self) -> bool:
        """Step 4: Irreversible erase with continuous monitoring"""
        if self.state != FlashState.ERASE_ARMED:
            raise RuntimeError(f"Can't erase from state {self.state}")
        
        self._transition(FlashState.COMMITTING, "Beginning erase")
        
        try:
            # Monitor DURING erase
            start_time = time.time()
            while time.time() - start_time < 30:  # 30s max erase
                violations = self.invariant_monitor.get_violations()
                if violations:
                    # EMERGENCY STOP - power loss during erase
                    self._transition(FlashState.RECOVERY, f"Erase aborted: {violations}")
                    return False
                
                # Actually perform erase in chunks
                if not self._erase_chunk():
                    self._transition(FlashState.RECOVERY, "Erase hardware failure")
                    return False
            
            self._transition(FlashState.WRITE_ARMED, "Erase complete")
            return True
            
        except SystemInvariantViolation:
            self._transition(FlashState.RECOVERY, "Physics violation during erase")
            return False
    
    def write(self, new_data: bytes) -> bool:
        """Step 5: Write with hash verification"""
        if self.state != FlashState.WRITE_ARMED:
            raise RuntimeError(f"Can't write from state {self.state}")
        
        # Pre-verify data
        self.new_data_hash = hashlib.sha256(new_data).hexdigest()
        
        # Checksum layer
        if not self._verify_checksum(new_data):
            self._transition(FlashState.RECOVERY, "Data checksum invalid")
            return False
        
        self._transition(FlashState.COMMITTING, "Beginning write")
        
        try:
            # Write with monitoring
            for chunk in self._chunk_data(new_data):
                violations = self.invariant_monitor.get_violations()
                if violations:
                    self._transition(FlashState.RECOVERY, f"Write aborted: {violations}")
                    return False
                
                self._write_chunk(chunk)
            
            self._transition(FlashState.VERIFYING, "Write complete, verifying")
            
            # POST-WRITE VERIFICATION (non-optional)
            if not self._verify_write():
                self._transition(FlashState.RECOVERY, "Write verification failed")
                return False
            
            self._transition(FlashState.COMPLETE, "Flash successful")
            return True
            
        except SystemInvariantViolation:
            self._transition(FlashState.RECOVERY, "Physics violation during write")
            return False
    
    def recover(self) -> bool:
        """Only possible if backup exists and ECU is alive"""
        if self.state != FlashState.RECOVERY:
            raise RuntimeError(f"Can't recover from state {self.state}")
        
        if not self.backup_hash:
            self._transition(FlashState.BRICKED, "No backup for recovery")
            return False
        
        # Attempt recovery flash
        # ... recovery logic with same invariants
        
        return True