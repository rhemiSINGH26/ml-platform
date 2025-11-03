"""
Logging configuration for the MLOps platform.
Provides structured logging with JSON output and file rotation.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any
from loguru import logger
from config.settings import settings


def serialize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize log record to JSON-friendly format."""
    return {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "logger": record["name"],
        "message": record["message"],
        "function": record["function"],
        "line": record["line"],
        "module": record["module"],
        "process": record["process"].id,
        "thread": record["thread"].id,
        "extra": record.get("extra", {}),
    }


def setup_logging() -> None:
    """Configure logging for the application."""
    
    # Remove default logger
    logger.remove()
    
    # Console logging
    if settings.log_format == "json":
        logger.add(
            sys.stderr,
            format="{message}",
            level=settings.log_level,
            serialize=True,
        )
    else:
        # Human-readable format for development
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=settings.log_level,
            colorize=True,
        )
    
    # File logging
    if settings.log_to_file:
        settings.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Main application log
        logger.add(
            settings.logs_dir / "app.log",
            rotation=settings.log_rotation,
            retention=settings.log_retention,
            level=settings.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            backtrace=True,
            diagnose=True,
        )
        
        # API-specific log
        logger.add(
            settings.logs_dir / "api.log",
            rotation=settings.log_rotation,
            retention=settings.log_retention,
            level=settings.log_level,
            filter=lambda record: "api" in record["extra"].get("service", ""),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        )
        
        # Training log
        logger.add(
            settings.logs_dir / "training.log",
            rotation=settings.log_rotation,
            retention=settings.log_retention,
            level=settings.log_level,
            filter=lambda record: "training" in record["extra"].get("service", ""),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        )
        
        # Agent log
        logger.add(
            settings.logs_dir / "agent.log",
            rotation=settings.log_rotation,
            retention=settings.log_retention,
            level=settings.log_level,
            filter=lambda record: "agent" in record["extra"].get("service", ""),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        )
        
        # Error log (errors only)
        logger.add(
            settings.logs_dir / "error.log",
            rotation=settings.log_rotation,
            retention=settings.log_retention,
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            backtrace=True,
            diagnose=True,
        )


# Intercept standard logging and redirect to loguru
class InterceptHandler(logging.Handler):
    """Intercept standard logging and redirect to loguru."""
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record."""
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        
        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_uvicorn_logging() -> None:
    """Configure uvicorn logging to use loguru."""
    logging.getLogger("uvicorn").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.error").handlers = [InterceptHandler()]


def setup_mlflow_logging() -> None:
    """Configure MLflow logging to use loguru."""
    logging.getLogger("mlflow").handlers = [InterceptHandler()]
    logging.getLogger("mlflow").setLevel(logging.INFO)


def get_logger(name: str, service: str = "app") -> Any:
    """
    Get a logger with the specified name and service.
    
    Args:
        name: Logger name (usually __name__)
        service: Service name for filtering logs
        
    Returns:
        Logger instance
    """
    return logger.bind(service=service, logger_name=name)


# Initialize logging on import
setup_logging()
setup_uvicorn_logging()
setup_mlflow_logging()


# Export logger for convenience
__all__ = ["logger", "get_logger", "setup_logging"]
