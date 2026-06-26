"""
Logging utilities
"""
import logging
import sys
from datetime import datetime
from typing import Optional


class Logger:
    """Custom logger with different levels"""
    
    _instance = None
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):
        """Setup logger configuration"""
        self.logger = logging.getLogger('booking_system')
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """Get a logger instance"""
        if name:
            return logging.getLogger(f'booking_system.{name}')
        return self.logger


# Singleton instance
logger = Logger()

def log_info(message: str) -> None:
    """Log info message"""
    logger.logger.info(message)

def log_error(message: str) -> None:
    """Log error message"""
    logger.logger.error(message)

def log_debug(message: str) -> None:
    """Log debug message"""
    logger.logger.debug(message)

def log_warning(message: str) -> None:
    """Log warning message"""
    logger.logger.warning(message)