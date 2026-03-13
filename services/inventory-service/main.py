import logging
import sys
import time
from config import SERVICE_NAME
from inventory import init_db
from consumer import start_consuming

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(SERVICE_NAME)

if __name__ == "__main__":
    logger.info(f"{SERVICE_NAME} starting...")

    retries = 5
    for attempt in range(retries):
        try:
            init_db()
            break
        except Exception as e:
            logger.warning(f"DB init attempt {attempt + 1}/{retries} failed: {e}")
            if attempt < retries - 1:
                time.sleep(5)
            else:
                logger.error("Could not connect to database, exiting")
                sys.exit(1)

    start_consuming()
