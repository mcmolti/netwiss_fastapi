"""
Centralized logging configuration for the proposal generation API.

This module provides structured logging setup with proper formatters
and handlers for development and production environments.
"""

import logging
import logging.config
import os
from typing import Dict, Any


def get_logging_config() -> Dict[str, Any]:
    """
    Get logging configuration based on environment.

    Returns:
        Logging configuration dictionary
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "detailed")

    # Base configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {"format": "%(levelname)s - %(message)s"},
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "function": "%(funcName)s", "line": %(lineno)d, "message": "%(message)s"}',
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": log_format,
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "detailed",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
        },
        "loggers": {
            "app": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "app.services": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "app.routers": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
        },
        "root": {"level": log_level, "handlers": ["console"]},
    }

    return config


def setup_logging():
    """
    Set up logging configuration for the application.
    Creates logs directory if it doesn't exist.
    """
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Apply logging configuration
    config = get_logging_config()
    logging.config.dictConfig(config)

    # Get logger and log startup message
    logger = logging.getLogger("app")
    logger.info("Logging system initialized")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"app.{name}")
