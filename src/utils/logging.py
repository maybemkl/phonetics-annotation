"""Logging configuration and utilities."""

import logging
import sys
from pathlib import Path
from typing import Optional

import structlog
from rich.console import Console
from rich.logging import RichHandler

from config import get_settings


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[Path] = None
) -> None:
    """Set up logging configuration."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if log_format == "json" 
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    level = getattr(logging, log_level.upper())
    
    # Create console handler
    console_handler = RichHandler(
        console=Console(stderr=True),
        show_time=True,
        show_path=True,
        markup=True,
    )
    console_handler.setLevel(level)
    
    # Create formatter
    if log_format == "json":
        formatter = logging.Formatter(
            "%(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a logger instance."""
    return structlog.get_logger(name)


# Initialize logging with default settings
def _init_logging():
    """Initialize logging with settings from config."""
    settings = get_settings()
    setup_logging(
        log_level=settings.logging.log_level,
        log_format=settings.logging.log_format,
        log_file=Path("logs/phonetics_annotation.log")
    )


# Auto-initialize logging when module is imported
_init_logging()
