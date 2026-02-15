"""Logging configuration"""
import logging
import sys
from .settings import settings


def setup_logger(name: str) -> logging.Logger:
    """Configure and return a logger instance"""
    logger = logging.getLogger(name)
    logger.setLevel(settings.log_level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.log_level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler if not already added
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    return logger
