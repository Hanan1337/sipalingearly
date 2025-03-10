import logging
import os
from datetime import datetime

def setup_logging():
    """Setup logging configuration with file and console output."""
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,  # Set level to DEBUG for detailed logging
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/bot.log"),  # Log to file
            logging.StreamHandler()  # Log to console
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("✅ Logging setup complete.")
    return logger
