"""
Centralized logging configuration.

Provides structured logging for the restaurant recommendation system.
Logs filter counts, candidate sizes, Groq latency, token usage,
and validation failures — per architecture §12 and implementation-plan §4.1.

Usage:
    from app.logging_config import setup_logging
    setup_logging()  # call once at startup
"""

import logging
import os
import sys


# ── Log format ──────────────────────────────────────────────────────────────
# Structured format: timestamp | level | module | message
_LOG_FORMAT = (
    "%(asctime)s  %(levelname)-8s  [%(name)s]  %(message)s"
)
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


from typing import Optional

def setup_logging(level: Optional[str] = None) -> None:
    """Configure the root logger for the application.

    Args:
        level: Override log level (e.g. ``"DEBUG"``).  Defaults to the
            ``LOG_LEVEL`` environment variable, or ``"INFO"`` if unset.
    """
    log_level = level or os.getenv("LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Reset any existing handlers (avoids duplicate log lines on re-init)
    root = logging.getLogger()
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))

    root.setLevel(numeric_level)
    root.addHandler(handler)

    # Quieten noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("datasets").setLevel(logging.WARNING)
    logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("fsspec").setLevel(logging.WARNING)

    logging.getLogger(__name__).debug(
        "Logging initialised at %s level", log_level.upper()
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger scoped to the application namespace.

    Convenience wrapper that prefixes with ``app.`` for consistency.
    """
    if not name.startswith("app."):
        name = f"app.{name}"
    return logging.getLogger(name)
