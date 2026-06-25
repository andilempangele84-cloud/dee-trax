#!/usr/bin/env python3
"""
Logging Configuration

Sets up structured logging for the AI Engine using loguru and Python logging.
"""

import sys
import logging
from datetime import datetime
from loguru import logger
from pythonjsonlogger import jsonlogger
from config.environment import settings


def setup_logging() -> logging.Logger:
    """
    Configure application logging
    
    Returns:
        Configured logger instance
    """
    
    # Remove default handler
    logger.remove()
    
    # Log format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    # Add console handler
    logger.add(
        sys.stderr,
        format=log_format,
        level=settings.LOG_LEVEL,
        colorize=True,
    )
    
    # Add file handler for production
    if settings.ENVIRONMENT == "production":
        logger.add(
            "logs/ai-engine-{time}.log",
            format=log_format,
            level="INFO",
            rotation="500 MB",
            retention="30 days",
            compression="zip",
        )
        
        logger.add(
            "logs/ai-engine-errors-{time}.log",
            format=log_format,
            level="ERROR",
            rotation="500 MB",
            retention="90 days",
            compression="zip",
        )
    
    # Configure standard logging to use loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    
    return logger


class InterceptHandler(logging.Handler):
    """
    Handler that intercepts standard logging messages and passes them to loguru
    """
    
    def emit(self, record: logging.LogRecord):
        # Get corresponding loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        
        # Find caller from the standard logging framework
        frame, _ = logging.findCaller()
        logger.opt(depth=6, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )
