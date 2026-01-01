import logging
from datetime import datetime
import os

# Import settings to check environment
try:
    from ..config.settings import settings
except ImportError:
    from src.config.settings import settings

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging
def setup_logging():
    # Determine log level based on environment
    if settings.environment.lower() == "production":
        log_level = logging.WARNING  # Only warnings and errors in production
        console_log_level = logging.WARNING
    else:
        log_level = logging.INFO  # Info and above in development
        console_log_level = logging.INFO

    # Create custom formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create file handler - always log to file regardless of environment
    file_handler = logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # Create console handler - only add if not in production or if debug is True
    console_handler = None
    if settings.environment.lower() != "production" or settings.debug:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_log_level)
        console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    if console_handler:
        root_logger.addHandler(console_handler)

# Initialize logging
setup_logging()

# Get logger for the application
logger = logging.getLogger(__name__)
