import logging
from datetime import datetime
import os

# Handle both direct execution and module import
try:
    from ..config.settings import settings
except ImportError:
    # When running tests or as module, use absolute imports
    from src.config.settings import settings

LOGS_DIR = "logs" if settings.environment == "development" else "/tmp/logs"

# Create temporary logs directory if it doesn't exist
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Configure logging
def setup_logging():
    # Create custom formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create file handler
    file_handler = logging.FileHandler(f'{LOGS_DIR}/app_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

# Initialize logging
setup_logging()

# Get logger for the application
logger = logging.getLogger(__name__)
