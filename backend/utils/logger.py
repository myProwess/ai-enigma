"""
Centralized logging configuration for the NewsAPI Flask backend.
Provides a factory function to create named loggers with consistent formatting.
"""

import logging
import os
from typing import Optional

from utils.config import Config


def get_logger(name: str, log_level: Optional[str] = None) -> logging.Logger:
    """
    Create and return a named logger with console and file handlers.

    Args:
        name: The name for the logger (typically __name__).
        log_level: Optional override for the log level.

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    level = getattr(logging, (log_level or Config.LOG_LEVEL).upper(), logging.INFO)
    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Console handler ──────────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ── File handler ─────────────────────────────────────────────────
    try:
        log_dir = os.path.dirname(Config.LOG_FILE)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.FileHandler(Config.LOG_FILE, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except (OSError, PermissionError) as exc:
        logger.warning("Could not create file handler for logging: %s", exc)

    return logger
