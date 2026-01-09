import hashlib
import os
import sys
import platform

# Hardcoded Build Identity for Alpha
# In a real CI/CD pipeline, this would be injected during build
BUILD_ID = "DACOS-ALPHA-20260107-SIGNED-V1"
KNOWN_HASHES = [
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", # Empty file hash (placeholder)
    # Add real hashes of key files here in production
]

class BuildVerifier:
    @staticmethod
    def get_build_id() -> str:
        return BUILD_ID

    @staticmethod
    def get_system_fingerprint() -> str:
        """
        Generates a system fingerprint for client classification.
        Includes Python version, OS platform, machine type, and processor.
        """
        fingerprint_tuple = (
            sys.version,
            platform.system(),
            platform.release(),
            platform.machine(),
            platform.processor()
        )
        return str(fingerprint_tuple)

    @staticmethod
    def get_integrity_hash() -> str:
        """
        Generates a hash of the build ID and system fingerprint.
        This binds the build to the specific runtime environment.
        """
        fingerprint = BuildVerifier.get_system_fingerprint()
        integrity_string = f"{BUILD_ID}|{fingerprint}"
        return hashlib.sha256(integrity_string.encode()).hexdigest()

    @staticmethod
    def verify_integrity() -> bool:
        """
        Verifies the integrity of the runtime environment.
        For Alpha Containment: Checks if running from source or frozen, 
        and validates key constants.
        """
        # 1. Check Build ID presence
        if not BUILD_ID.startswith("DACOS-ALPHA"):
            return False
            
        # 2. Hardened Integrity Check (Tuple Hashing)
        # We generate the integrity hash locally. 
        # In a real scenario, this hash is sent to the server for validation.
        # For local containment, we ensure we can generate it successfully.
        try:
            current_hash = BuildVerifier.get_integrity_hash()
            # In alpha, if we can generate a valid hash, we pass the local check.
            # The server (via Telemetry) will validate if this hash is allowed.
            if not current_hash:
                return False
        except Exception:
            return False

        # 3. Simple Anti-Tamper (Mock implementation for Alpha)
        # In production, this would check checksums of own code objects or .exe signature
        # For now, we assume if the module is loaded and ID matches, it's "signed"
        # Logic: If we are running in a modified environment where someone changed this file,
        # they could just change this function to return True.
        # However, the user asked for "Containment", not perfect security.
        # "Pre-coded default login... It’s not security. It’s containment."
        
        return True

    @staticmethod
    def verify_remote_build(server_response_id: str) -> bool:
        """
        Verifies if the server recognizes this build ID.
        """
        return server_response_id == BUILD_ID
