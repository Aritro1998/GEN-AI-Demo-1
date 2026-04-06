# repository/ai_utils/logger.py
"""
Logging utilities for AI operations.
"""

import logging
import os
from datetime import datetime


class AILogger:
    """Custom logger for AI service operations"""
    
    def __init__(self, name: str = "plant_disease_ai"):
        self.logger = logging.getLogger(name)
        
        # Set level from environment or default to INFO
        log_level = os.getenv("LOG_LEVEL", "INFO")
        self.logger.setLevel(getattr(logging, log_level))
        
        # Create console handler if not exists
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(console_handler)
            
            # Optional: File handler
            log_file = os.getenv("LOG_FILE")
            if log_file:
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
