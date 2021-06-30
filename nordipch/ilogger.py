import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("giggle.log"),
        logging.StreamHandler()
    ]
)

logger=logging.getLogger() 