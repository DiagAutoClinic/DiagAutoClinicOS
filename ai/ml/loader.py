# ai/ml/loader.py

import os
from typing import Optional, Tuple, Any
from ..core.config import AIConfig
from ..core.exceptions import ModelLoadError
from ..utils.logging import logger

class MLLoader:
    def __init__(self, config: AIConfig):
        self.config = config
        self.model: Optional[Any] = None
        self.preprocessor: Optional[Any] = None
        self.available = False

    def load(self) -> bool:
        """Load ML model and preprocessor if available."""
        if not self.config.enable_ml:
            logger.info("ML disabled in configuration")
            return False

        try:
            import tensorflow as tf
            import joblib

            if os.path.exists(self.config.model_path):
                self.model = tf.keras.models.load_model(self.config.model_path)
                self.preprocessor = joblib.load(self.config.preprocessor_path)
                self.available = True
                logger.info("ML model and preprocessor loaded successfully")
                return True
            else:
                logger.warning("ML model files not found")
                return False
        except ImportError as e:
            logger.warning(f"ML dependencies not available: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            raise ModelLoadError(f"Model loading failed: {e}") from e

    def is_available(self) -> bool:
        return self.available

    def get_model(self) -> Optional[Any]:
        return self.model

    def get_preprocessor(self) -> Optional[Any]:
        return self.preprocessor