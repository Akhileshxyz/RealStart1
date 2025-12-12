import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logging():
    """Configure application logging"""

    # Root logger
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler for all logs
            logging.FileHandler("logs/app.log"),
            # File handler for errors only
            logging.FileHandler("logs/error.log", mode='a'),
        ]
    )

    # Error handler
    error_handler = logging.FileHandler("logs/error.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    # Security audit handler
    security_handler = logging.FileHandler("logs/security.log")
    security_handler.setLevel(logging.WARNING)
    security_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    # Create security logger
    security_logger = logging.getLogger("security")
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.INFO)

    return logging.getLogger(__name__)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)
