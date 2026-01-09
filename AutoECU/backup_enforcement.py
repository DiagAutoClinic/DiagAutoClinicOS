class BackupEnforcement:
    """Physically impossible to bypass"""
    
    def __init__(self):
        self.backups: Dict[str, Dict] = {}  # ecu_id -> backup info
    
    def register_backup(self, ecu_id: str, data: bytes) -> str:
        """Register a backup - returns backup_id for later verification"""
        backup_hash = hashlib.sha256(data).hexdigest()
        
        # Store in TWO separate locations immediately
        self._store_primary(ecu_id, data, backup_hash)
        self._store_secondary(ecu_id, data, backup_hash)
        
        # Create attestation
        attestation = {
            "ecu_id": ecu_id,
            "backup_hash": backup_hash,
            "timestamp": time.time(),
            "data_length": len(data),
            "primary_location": self._primary_path(ecu_id),
            "secondary_location": self._secondary_path(ecu_id)
        }
        
        # Cryptographic lock
        attestation_hash = hashlib.sha256(
            json.dumps(attestation, sort_keys=True).encode()
        ).hexdigest()
        
        # REMOTE NOTARIZATION (no local-only backups)
        self._notarize_backup(attestation_hash, attestation)
        
        self.backups[ecu_id] = {
            "hash": backup_hash,
            "attestation": attestation,
            "attestation_hash": attestation_hash
        }
        
        return backup_hash
    
    def verify_backup_exists(self, ecu_id: str) -> bool:
        """Check if backup exists AND is accessible"""
        if ecu_id not in self.backups:
            return False
        
        backup = self.backups[ecu_id]
        
        # Verify both storage locations
        primary_ok = self._verify_file(backup["attestation"]["primary_location"], 
                                      backup["hash"])
        secondary_ok = self._verify_file(backup["attestation"]["secondary_location"], 
                                        backup["hash"])
        
        # Verify remote attestation
        remote_ok = self._verify_remote_attestation(backup["attestation_hash"])
        
        return primary_ok and secondary_ok and remote_ok
    
    def _verify_file(self, path: str, expected_hash: str) -> bool:
        """Verify file exists and matches hash"""
        try:
            with open(path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
                return file_hash == expected_hash
        except:
            return False
    
    def enforce_no_backup_no_erase(self, ecu_id: str, fsm: FlashFSM):
        """HARD STOP if backup doesn't exist"""
        if not self.verify_backup_exists(ecu_id):
            # NOT a warning - transition directly to BRICKED
            fsm._transition(FlashState.BRICKED, 
                          "No valid backup exists - erase impossible")
            raise SystemInvariantViolation(
                "Sacred Law Violated: No backup, no erase"
            )