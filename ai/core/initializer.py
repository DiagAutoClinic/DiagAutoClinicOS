# ai/core/initializer.py

from typing import Tuple, Any
from .config import AIConfig
from .exceptions import AIInitializationError

class SystemInitializer:
    def __init__(self, config: AIConfig):
        self.config = config

    def initialize(self) -> Tuple[Any, Any, Any]:
        """Initialize all system components and return (ml, can, rules)"""
        try:
            ml = self._init_ml()
            can = self._init_can()
            rules = self._init_rules()
            return ml, can, rules
        except Exception as e:
            raise AIInitializationError(f"Failed to initialize AI system: {e}") from e

    def _init_ml(self) -> Any:
        """Initialize ML components"""
        from ..ml.loader import MLLoader
        loader = MLLoader(self.config)
        loader.load()
        return loader

    def _init_can(self) -> Any:
        """Initialize CAN database components"""
        from ..can.database import CANDatabase
        db = CANDatabase(self.config)
        db.connect()
        return db

    def _init_rules(self) -> Any:
        """Initialize rule-based components"""
        from ..rules.base import RuleEngine
        from ..rules.engine_rules import create_engine_rules

        engine = RuleEngine()
        rules = create_engine_rules()
        for rule in rules:
            engine.add_rule(rule)
        return engine