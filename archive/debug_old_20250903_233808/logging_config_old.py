"""
Centralized Logging Configuration for Untold Story
Moderne Logging-Konfiguration als Alternative zu print-Statements
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from enum import Enum


class LogLevel(Enum):
    """Log-Level für das Spiel"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class GameLogger:
    """Zentraler Game-Logger für alle Engine-Komponenten"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            self._initialized = True
    
    def _setup_logging(self):
        """Konfiguriert das Logging-System"""
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Main logger
        self.logger = logging.getLogger("untold_story")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler (für wichtige Meldungen)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler (für alle Meldungen)
        file_handler = logging.FileHandler(
            logs_dir / "game.log", 
            mode='a', 
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        
        # Error file handler (nur für Fehler)
        error_handler = logging.FileHandler(
            logs_dir / "errors.log",
            mode='a',
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        self.logger.addHandler(error_handler)
    
    def debug(self, message: str, component: Optional[str] = None):
        """Debug-Level Nachricht"""
        self._log(logging.DEBUG, message, component)
    
    def info(self, message: str, component: Optional[str] = None):
        """Info-Level Nachricht"""
        self._log(logging.INFO, message, component)
    
    def warning(self, message: str, component: Optional[str] = None):
        """Warning-Level Nachricht"""
        self._log(logging.WARNING, message, component)
    
    def error(self, message: str, component: Optional[str] = None):
        """Error-Level Nachricht"""
        self._log(logging.ERROR, message, component)
    
    def critical(self, message: str, component: Optional[str] = None):
        """Critical-Level Nachricht"""
        self._log(logging.CRITICAL, message, component)
    
    def _log(self, level: int, message: str, component: Optional[str] = None):
        """Interne Log-Funktion"""
        if component:
            formatted_message = f"[{component}] {message}"
        else:
            formatted_message = message
        
        self.logger.log(level, formatted_message)
    
    def set_level(self, level: LogLevel):
        """Setze Log-Level"""
        self.logger.setLevel(level.value)
        
        # Update console handler level
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                handler.setLevel(level.value)


# Global logger instance
game_logger = GameLogger()


# Convenience functions for easy migration from print statements
def log_debug(message: str, component: str = "GAME"):
    """Convenience function for debug logging"""
    game_logger.debug(message, component)


def log_info(message: str, component: str = "GAME"):
    """Convenience function for info logging"""
    game_logger.info(message, component)


def log_warning(message: str, component: str = "GAME"):
    """Convenience function for warning logging"""
    game_logger.warning(message, component)


def log_error(message: str, component: str = "GAME"):
    """Convenience function for error logging"""
    game_logger.error(message, component)


def log_critical(message: str, component: str = "GAME"):
    """Convenience function for critical logging"""
    game_logger.critical(message, component)


# Component-specific loggers
def log_battle(message: str, level: str = "info"):
    """Battle-specific logging"""
    if level == "debug":
        game_logger.debug(message, "BATTLE")
    elif level == "warning":
        game_logger.warning(message, "BATTLE")
    elif level == "error":
        game_logger.error(message, "BATTLE")
    else:
        game_logger.info(message, "BATTLE")


def log_ui(message: str, level: str = "info"):
    """UI-specific logging"""
    if level == "debug":
        game_logger.debug(message, "UI")
    elif level == "warning":
        game_logger.warning(message, "UI")
    elif level == "error":
        game_logger.error(message, "UI")
    else:
        game_logger.info(message, "UI")


def log_scene(message: str, level: str = "info"):
    """Scene-specific logging"""
    if level == "debug":
        game_logger.debug(message, "SCENE")
    elif level == "warning":
        game_logger.warning(message, "SCENE")
    elif level == "error":
        game_logger.error(message, "SCENE")
    else:
        game_logger.info(message, "SCENE")


def log_system(message: str, level: str = "info"):
    """System-specific logging"""
    if level == "debug":
        game_logger.debug(message, "SYSTEM")
    elif level == "warning":
        game_logger.warning(message, "SYSTEM")
    elif level == "error":
        game_logger.error(message, "SYSTEM")
    else:
        game_logger.info(message, "SYSTEM")


# Migration helpers
def replace_print(message: str, component: str = "MIGRATION"):
    """
    Temporary function to replace print statements.
    Use this for gradual migration from print() to proper logging.
    """
    game_logger.info(f"[PRINT-MIGRATION] {message}", component)


# Performance logging for battle system
def log_performance(operation: str, duration: float, component: str = "PERFORMANCE"):
    """Log performance metrics"""
    if duration > 0.1:  # Log slow operations (>100ms)
        game_logger.warning(f"SLOW: {operation} took {duration:.3f}s", component)
    elif duration > 0.05:  # Log moderate operations (>50ms)
        game_logger.info(f"{operation} took {duration:.3f}s", component)
    else:
        game_logger.debug(f"{operation} took {duration:.3f}s", component)
