from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import json

class TechnicianLiability:
    """Forces acknowledgment of irreversible actions"""
    
    def __init__(self):
        self.acknowledgments: Dict[str, Dict] = {}
    
    def create_acknowledgment(self, 
                            technician_id: str,
                            private_key: Ed25519PrivateKey,
                            action: str,
                            consequences: List[str],
                            backup_hash: str) -> str:
        """Create a signed acknowledgment of destruction"""
        
        payload = {
            "technician_id": technician_id,
            "action": action,
            "consequences": consequences,
            "backup_hash": backup_hash,
            "timestamp": time.time(),
            "vin": self.vin,
            "ecu_id": self.ecu_id
        }
        
        # Canonical JSON (deterministic)
        payload_bytes = json.dumps(payload, sort_keys=True).encode()
        
        # Hash
        payload_hash = hashlib.sha256(payload_bytes).hexdigest()
        
        # Sign
        signature = private_key.sign(payload_bytes)
        
        # Store
        self.acknowledgments[payload_hash] = {
            "payload": payload,
            "signature": signature.hex(),
            "public_key": private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()
        }
        
        # Notarize acknowledgment
        self._notarize_acknowledgment(payload_hash, signature)
        
        return payload_hash
    
    def verify_acknowledgment(self, acknowledgment_hash: str) -> bool:
        """Verify the acknowledgment exists and is valid"""
        if acknowledgment_hash not in self.acknowledgments:
            return False
        
        ack = self.acknowledgments[acknowledgment_hash]
        
        # Verify signature
        public_key = serialization.load_pem_public_key(
            ack["public_key"].encode()
        )
        
        payload_bytes = json.dumps(ack["payload"], sort_keys=True).encode()
        
        try:
            public_key.verify(
                bytes.fromhex(ack["signature"]),
                payload_bytes
            )
            return True
        except:
            return False
    
    def get_acknowledgment_consequences(self, acknowledgment_hash: str) -> List[str]:
        """What the technician agreed to"""
        if acknowledgment_hash in self.acknowledgments:
            return self.acknowledgments[acknowledgment_hash]["payload"]["consequences"]
        return []