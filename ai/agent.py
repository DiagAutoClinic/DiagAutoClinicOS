# ai/agent.py

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from ai.environment.actions import ReadPID, ActuatorTest, ClearCodes

# Try to import the DACOS VIN Truth Engine
try:
    from core.dacos_vin_truth_engin import DACOSVinTruthEngine
except ImportError:
    # Handle case where core is not in path (e.g. running tests)
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    try:
        from core.dacos_vin_truth_engin import DACOSVinTruthEngine
    except ImportError:
        DACOSVinTruthEngine = None

logger = logging.getLogger(__name__)

class CharlemaineAgent:
    """
    Charlemaine: The Technical Intelligence Layer of DiagAutoClinic OS (DACOS).
    
    Purpose:
    - Analyze, explain, and enforce automotive diagnostic logic with precision.
    - Interpret VIN data using structured WMI, VDS, and VIS rules.
    - Explain vehicle metadata based solely on verified decoding logic.
    - Enforce strict technical discipline (backups, checksums, voltage safety).
    - Act as a knowledge interface over DACOS documentation and APIs.
    
    Principles:
    - No guessing, speculating, or inventing data.
    - Explicitly state limitations when information is incomplete.
    - Prioritize safety and procedural correctness.
    """
    
    def __init__(self, belief_state=None, storage_path: Path = None):
        self.belief = belief_state
        self.identity = "Charlemaine"
        self.role = "Technical Intelligence Layer"
        self.logger = logging.getLogger("Charlemaine")

        # Initialize VIN Truth Engine
        if DACOSVinTruthEngine:
            if storage_path is None:
                storage_path = Path("vin_storage")
            storage_path.mkdir(exist_ok=True)
            
            # Master key management
            master_key = os.environ.get('DACOS_VIN_MASTER_KEY')
            if not master_key:
                if isinstance(master_key, str):
                    master_key = master_key.encode()
                else:
                    master_key = os.urandom(32)
                
            self.vin_engine = DACOSVinTruthEngine(master_key, storage_path)
            self.logger.info("Charlemaine initialized with VIN Truth Engine")
        else:
            self.vin_engine = None
            self.logger.warning("DACOS VIN Truth Engine not available - Charlemaine running in limited mode")

    def analyze_vin(self, vin: str) -> Dict[str, Any]:
        """
        Analyze a VIN using the 7-Layer Truth Engine.
        Returns a comprehensive report with epistemological confidence.
        """
        if not self.vin_engine:
            return {"error": "VIN Engine not available"}
            
        self.logger.info(f"Analyzing VIN: {vin}")
        try:
            result = self.vin_engine.decode(vin)
            return result
        except Exception as e:
            self.logger.error(f"VIN Analysis failed: {e}")
            return {"error": str(e)}

    def explain_metadata(self, vin_data: Dict[str, Any]) -> str:
        """
        Generate a human-readable explanation of the VIN analysis.
        """
        if "error" in vin_data:
            return f"Cannot explain metadata due to error: {vin_data['error']}"
            
        manufacturer = vin_data.get("manufacturer", {}).get("value", "Unknown")
        model = vin_data.get("model", {}).get("value", "Unknown")
        year = vin_data.get("model_year", {}).get("value", "Unknown")
        confidence = vin_data.get("confidence", 0.0)
        
        explanation = (
            f"Vehicle Identification Analysis:\n"
            f"  Manufacturer: {manufacturer}\n"
            f"  Model: {model}\n"
            f"  Year: {year}\n"
            f"  Confidence Score: {confidence:.2f}\n\n"
        )
        
        if confidence < 0.8:
            explanation += "WARNING: Identification confidence is low. Verify manually before proceeding with critical operations.\n"
            
        return explanation

    def enforce_safety_protocol(self, operation: str, context: Dict[str, Any]) -> bool:
        """
        Enforce strict technical discipline (backups, checksums, voltage safety).
        """
        self.logger.info(f"Enforcing safety for operation: {operation}")
        
        # Voltage Check
        voltage = context.get("voltage", 0.0)
        if voltage < 11.5:
            self.logger.error(f"Safety Violation: Voltage too low ({voltage}V). Minimum 11.5V required.")
            return False
            
        # Critical Operations (Coding, Programming) require specific checks
        if operation in ["CODING", "PROGRAMMING", "FLASHING"]:
            if not context.get("ignition_on", False):
                self.logger.error("Safety Violation: Ignition must be ON.")
                return False
            
            if not context.get("backup_verified", False):
                self.logger.error("Safety Violation: No verified backup found.")
                return False
                
        return True

    def act(self, observation):
        """
        Determine the next diagnostic action based on the current belief state.
        """
        # Choose action that reduces entropy (uncertainty)
        if self.belief:
            entropy = self.belief.entropy()
        else:
            entropy = 0.5 # Default assumption if no belief state

        if entropy > 1.0:
            # High uncertainty: Gather more data
            return ReadPID()
        elif entropy > 0.3:
            # Moderate uncertainty: Test specific components
            return ActuatorTest()
        else:
            # Low uncertainty: Action safe to perform
            return ClearCodes()

    def summarize_function(self):
        return (
            "I am Charlemaine, the technical intelligence layer of DiagAutoClinic OS. "
            "I decode VIN data using the 7-Layer Truth Engine, explain vehicle metadata "
            "using verified logic, and enforce safety protocols like backups and voltage checks. "
            "I do not speculate on incomplete data."
        )
