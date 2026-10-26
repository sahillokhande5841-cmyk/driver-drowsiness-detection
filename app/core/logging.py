import logging
import sys
from typing import Optional
from app.core.config import settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """Configures application-wide structured logging."""
    level = log_level or settings.LOG_LEVEL
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format=settings.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True
    )


def get_logger(name: str) -> logging.Logger:
    """Returns a named logger configured with the application formatting."""
    return logging.getLogger(name)
