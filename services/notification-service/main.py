import logging
import sys
from config import SERVICE_NAME
from consumer import start_consuming

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(SERVICE_NAME)

if __name__ == "__main__":
    logger.info(f"{SERVICE_NAME} starting...")
    start_consuming()
