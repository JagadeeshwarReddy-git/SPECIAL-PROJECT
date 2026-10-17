import logging

logging.basicConfig(
    filename="application.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("AI-Social-Media")

from utils.logger import logger

logger.info("YouTube Analysis Started")
logger.info("CSV Uploaded Successfully")
logger.error("API Error")