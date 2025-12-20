# ai/core/config.py

from dataclasses import dataclass, field
import os

@dataclass
class AIConfig:
    base_model_path: str = field(default_factory=lambda: os.getenv("AI_MODEL_PATH", "ai/deployed_local_model"))
    can_db_path: str = field(default_factory=lambda: os.getenv("CAN_DB_PATH", "can_bus_databases.sqlite"))
    enable_ml: bool = field(default_factory=lambda: os.getenv("ENABLE_ML", "1") == "1")
    enable_ai_engine: bool = field(default_factory=lambda: os.getenv("ENABLE_AI_ENGINE", "1") == "1")
    model_path: str = field(init=False)
    preprocessor_path: str = field(init=False)

    def __post_init__(self):
        self.model_path = f"{self.base_model_path}/diagnostic_ai_model.keras"
        self.preprocessor_path = f"{self.base_model_path}/preprocessor.pkl"