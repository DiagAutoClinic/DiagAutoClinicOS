# charlemaine.py
# DiagAutoClinicOS Local AI Diagnostic Agent - "Charlemaine"
# Fully offline, private, runs on your laptop forever.

from ai.core.config import AIConfig
from ai.core.initializer import SystemInitializer
from ai.core.diagnostics_engine import DiagnosticsEngine
from ai.utils.logging import logger
from datetime import datetime

class Charlemaine:
    def __init__(self):
        self.name = "Charlemaine"
        self.version = "1.0"
        self.mode = "LOCAL OFFLINE AI"

        # Initialize system
        self.config = AIConfig()
        initializer = SystemInitializer(self.config)
        self.ml_loader, self.can_db, self.rule_engine = initializer.initialize()
        self.diagnostics_engine = DiagnosticsEngine(self.config, self.ml_loader, self.can_db, self.rule_engine)

        logger.info(f"\n{self.name} is now awake.")
        logger.info(f"Mode: {self.mode}")
        logger.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        logger.info("=" * 60)

    def diagnose(self, live_data):
        result = self.diagnostics_engine.diagnose(live_data)

        # Print result (keep the original printing)
        print(f"\n{self.name}'s Diagnosis:")
        print(f"   - {result['diagnosis']}")
        print(f"   - Confidence: {result['confidence']:.1%}")
        print(f"   - Severity: {result['severity']}")
        for rec in result["recommendations"]:
            print(f"   * {rec}")

        # Print next test recommendation
        if result.get('next_test'):
            print(f"   - Next Recommended Test: {result['next_test']} (Cost: {result['next_test_cost']})")

        print("=" * 60)
        return result

# --- Initialize Charlemaine ---
charlemaine = Charlemaine()

# --- Example: Test her immediately ---
if __name__ == "__main__":
    test_data = {
        "live_parameters": {
            "engine_rpm": {"value": 920},
            "coolant_temp": {"value": 112},
            "battery_voltage": {"value": 11.8},
            "throttle_position": {"value": 18}
        },
        "dtc_codes": ["P0118", "P0301"],
        "vehicle_context": {
            "make": "Toyota",
            "model": "Hilux",
            "year": 2018
        }
    }

    print("Running test diagnosis...\n")
    charlemaine.diagnose(test_data)