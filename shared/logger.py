"""
DiagAutoClinicOS - Centralized Logging
"""
import logging
import sys
from pathlib import Path
from datetime import datetime

# Try to use loguru if available, fall back to standard logging
try:
    from loguru import logger
    USING_LOGURU = True
except ImportError:
    USING_LOGURU = False
    logger = logging.getLogger('DiagAutoClinicOS')

def setup_logging(log_level: str = "INFO", log_file: Path = None):
    """Setup application-wide logging"""
    
    if USING_LOGURU:
        # Remove default handler
        logger.remove()
        
        # Console handler with color
        logger.add(
            sys.stderr,
            level=log_level,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
        )
        
        # File handler if specified
        if log_file:
            logger.add(
                log_file,
                rotation="1 day",
                retention="30 days",
                level=log_level,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}"
            )
    else:
        # Standard logging setup
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level))
        console_handler.setFormatter(logging.Formatter(log_format))
        
        logger.setLevel(getattr(logging, log_level))
        logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, log_level))
            file_handler.setFormatter(logging.Formatter(log_format))
            logger.addHandler(file_handler)
    
    logger.info(f"Logging initialized (using {'loguru' if USING_LOGURU else 'standard logging'})")
    return logger

def get_logger(name: str):
    """Get a logger for a specific module"""
    if USING_LOGURU:
        return logger.bind(name=name)
    else:
        return logging.getLogger(name)