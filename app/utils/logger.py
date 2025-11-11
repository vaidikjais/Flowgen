"""
Structured Logging Utility

Provides structured logging with request context and JSON formatting
for production-ready observability.
"""
import logging
import sys
from typing import Optional
from contextvars import ContextVar

# Context variable for request ID tracking across async calls
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class RequestContextFilter(logging.Filter):
    """
    Logging filter that adds request context to log records.
    
    Adds request_id to all log records if available in context.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add request_id to log record."""
        record.request_id = request_id_var.get() or "-"
        return True


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure application-wide structured logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level.upper())
    console_handler.setFormatter(formatter)
    console_handler.addFilter(RequestContextFilter())
    
    root_logger.addHandler(console_handler)
    
    # Silence noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (typically __name__ of the module)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Add request context filter if not already added
    if not any(isinstance(f, RequestContextFilter) for f in logger.filters):
        logger.addFilter(RequestContextFilter())
    
    return logger


def set_request_id(request_id: str) -> None:
    """
    Set request ID in context for current async context.
    
    Args:
        request_id: Unique request identifier
    """
    request_id_var.set(request_id)


def get_request_id() -> Optional[str]:
    """
    Get current request ID from context.
    
    Returns:
        Request ID if set, None otherwise
    """
    return request_id_var.get()


def clear_request_id() -> None:
    """Clear request ID from context."""
    request_id_var.set(None)

