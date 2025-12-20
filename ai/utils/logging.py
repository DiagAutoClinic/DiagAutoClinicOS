# ai/utils/logging.py

import logging
import sys
from typing import Optional

def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> logging.Logger:
    """Setup standardized logging for the AI system."""
    logger = logging.getLogger("charlemaine")
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# Global logger instance
logger = setup_logging()