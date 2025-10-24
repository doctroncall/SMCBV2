"""
Logging Configuration
Structured logging with loguru for comprehensive debugging and monitoring
"""
import sys
from pathlib import Path
from enum import Enum
from typing import Optional
from loguru import logger
import json
from datetime import datetime

from config.settings import AppConfig, LOGS_DIR


class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class CustomLogger:
    """
    Custom logger with structured logging capabilities
    
    Features:
    - Multiple output sinks (console, files)
    - Rotating file logs
    - JSON formatting for structured logging
    - Category-based logging
    - Performance monitoring
    - Error tracking with context
    """
    
    def __init__(self, name: str = "MT5Bot"):
        """
        Initialize custom logger
        
        Args:
            name: Logger name
        """
        self.name = name
        self.logger = logger
        self._setup_complete = False
    
    def setup(
        self,
        level: str = "INFO",
        console_output: bool = True,
        file_output: bool = True,
        json_output: bool = True,
        rotation: str = "100 MB",
        retention: str = "30 days"
    ):
        """
        Setup logging configuration
        
        Args:
            level: Minimum log level
            console_output: Enable console logging
            file_output: Enable file logging
            json_output: Enable JSON structured logging
            rotation: Log rotation size/time
            retention: Log retention period
        """
        if self._setup_complete:
            return
        
        # Remove default handler
        self.logger.remove()
        
        # Console handler (with colors)
        if console_output:
            self.logger.add(
                sys.stdout,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
                level=level,
                colorize=True,
            )
        
        # File handler (human readable)
        if file_output:
            log_file = LOGS_DIR / "app.log"
            self.logger.add(
                log_file,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                level=level,
                rotation=rotation,
                retention=retention,
                compression="zip",
            )
        
        # JSON handler (structured logging)
        if json_output:
            json_log_file = LOGS_DIR / "app.json"
            self.logger.add(
                json_log_file,
                format="{message}",
                level=level,
                rotation=rotation,
                retention=retention,
                serialize=True,  # JSON serialization
            )
        
        # Category-specific handlers
        self._setup_category_handlers(level, rotation, retention)
        
        self._setup_complete = True
        self.logger.info(f"Logging initialized for {self.name}")
    
    def _setup_category_handlers(
        self,
        level: str,
        rotation: str,
        retention: str
    ):
        """Setup category-specific log files"""
        categories = [
            "mt5_connection",
            "data_fetcher",
            "analysis",
            "ml_training",
            "health",
            "errors"
        ]
        
        for category in categories:
            log_file = LOGS_DIR / f"{category}.log"
            self.logger.add(
                log_file,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
                level=level,
                rotation=rotation,
                retention=retention,
                filter=lambda record, cat=category: record["extra"].get("category") == cat,
            )
    
    def debug(self, message: str, category: str = "general", **kwargs):
        """Log debug message"""
        self.logger.bind(category=category).debug(message, **kwargs)
    
    def info(self, message: str, category: str = "general", **kwargs):
        """Log info message"""
        self.logger.bind(category=category).info(message, **kwargs)
    
    def warning(self, message: str, category: str = "general", **kwargs):
        """Log warning message"""
        self.logger.bind(category=category).warning(message, **kwargs)
    
    def error(self, message: str, category: str = "errors", **kwargs):
        """Log error message"""
        self.logger.bind(category=category).error(message, **kwargs)
    
    def critical(self, message: str, category: str = "errors", **kwargs):
        """Log critical message"""
        self.logger.bind(category=category).critical(message, **kwargs)
    
    def exception(self, message: str, category: str = "errors", **kwargs):
        """Log exception with traceback"""
        self.logger.bind(category=category).exception(message, **kwargs)
    
    def log_mt5_event(self, event: str, status: str, details: Optional[dict] = None):
        """Log MT5-specific event"""
        message = f"MT5 Event: {event} - Status: {status}"
        if details:
            message += f" - Details: {json.dumps(details)}"
        self.info(message, category="mt5_connection")
    
    def log_data_fetch(self, symbol: str, timeframe: str, bars: int, success: bool):
        """Log data fetch operation"""
        status = "SUCCESS" if success else "FAILED"
        message = f"Data Fetch: {symbol} {timeframe} - {bars} bars - {status}"
        self.info(message, category="data_fetcher")
    
    def log_analysis(self, symbol: str, timeframe: str, sentiment: str, confidence: float):
        """Log analysis result"""
        message = f"Analysis: {symbol} {timeframe} - {sentiment} ({confidence:.2%})"
        self.info(message, category="analysis")
    
    def log_ml_training(
        self,
        model_version: str,
        samples: int,
        accuracy: float,
        duration: float
    ):
        """Log ML training event"""
        message = (
            f"ML Training: {model_version} - "
            f"Samples: {samples}, Accuracy: {accuracy:.2%}, "
            f"Duration: {duration:.2f}s"
        )
        self.info(message, category="ml_training")
    
    def log_health_check(self, component: str, status: str, metrics: Optional[dict] = None):
        """Log health check result"""
        message = f"Health Check: {component} - {status}"
        if metrics:
            message += f" - Metrics: {json.dumps(metrics)}"
        self.info(message, category="health")
    
    def log_performance(self, operation: str, duration: float, success: bool = True):
        """Log performance metric"""
        status = "SUCCESS" if success else "FAILED"
        message = f"Performance: {operation} - {duration:.4f}s - {status}"
        self.debug(message, category="general")
    
    def catch(self, **kwargs):
        """Decorator to catch and log exceptions"""
        return self.logger.catch(**kwargs)
    
    def contextualize(self, **kwargs):
        """Context manager for adding context to logs"""
        return self.logger.contextualize(**kwargs)


# Global logger instance
_logger_instance = None


def setup_logging(
    level: Optional[str] = None,
    console_output: bool = True,
    file_output: bool = True,
    json_output: bool = True
) -> CustomLogger:
    """
    Setup global logging configuration
    
    Args:
        level: Log level (uses config if not provided)
        console_output: Enable console logging
        file_output: Enable file logging
        json_output: Enable JSON logging
        
    Returns:
        CustomLogger: Configured logger instance
    """
    global _logger_instance
    
    if _logger_instance is None:
        _logger_instance = CustomLogger()
    
    log_level = level or AppConfig.LOG_LEVEL
    
    _logger_instance.setup(
        level=log_level,
        console_output=console_output,
        file_output=file_output,
        json_output=json_output,
    )
    
    return _logger_instance


def get_logger() -> CustomLogger:
    """
    Get global logger instance
    
    Returns:
        CustomLogger: Logger instance
    """
    global _logger_instance
    
    if _logger_instance is None:
        _logger_instance = setup_logging()
    
    return _logger_instance


# Convenience functions
def log_debug(message: str, **kwargs):
    """Log debug message (convenience function)"""
    get_logger().debug(message, **kwargs)


def log_info(message: str, **kwargs):
    """Log info message (convenience function)"""
    get_logger().info(message, **kwargs)


def log_warning(message: str, **kwargs):
    """Log warning message (convenience function)"""
    get_logger().warning(message, **kwargs)


def log_error(message: str, **kwargs):
    """Log error message (convenience function)"""
    get_logger().error(message, **kwargs)


def log_exception(message: str, **kwargs):
    """Log exception with traceback (convenience function)"""
    get_logger().exception(message, **kwargs)


if __name__ == "__main__":
    # Test logging
    print("📝 Testing Logger...")
    
    # Setup logger
    logger_instance = setup_logging(level="DEBUG")
    
    # Test different log levels
    logger_instance.info("Application started", category="general")
    logger_instance.debug("Debug information", category="general")
    logger_instance.warning("Warning message", category="general")
    logger_instance.error("Error occurred", category="errors")
    
    # Test category-specific logging
    logger_instance.log_mt5_event(
        "Connection Established",
        "SUCCESS",
        {"server": "ICMarkets", "account": "12345"}
    )
    
    logger_instance.log_data_fetch("EURUSD", "H1", 1000, True)
    
    logger_instance.log_analysis("EURUSD", "H1", "BULLISH", 0.82)
    
    logger_instance.log_ml_training("v1.0.0", 10000, 0.73, 125.5)
    
    logger_instance.log_health_check(
        "MT5 Connection",
        "HEALTHY",
        {"ping": 23, "uptime": "8h"}
    )
    
    logger_instance.log_performance("data_fetch", 0.234, True)
    
    # Test exception logging
    try:
        raise ValueError("Test exception")
    except Exception:
        logger_instance.exception("Caught test exception", category="errors")
    
    # Test decorator
    @logger_instance.catch()
    def risky_function():
        raise RuntimeError("This will be caught and logged")
    
    try:
        risky_function()
    except Exception:
        pass  # Already logged by decorator
    
    print("\n✓ Logger test completed")
    print(f"✓ Logs saved to: {LOGS_DIR}")
