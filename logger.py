
import logging
def get_logger(name: str = "app"):
    logger = logging.getLogger(name)
    return logger
logger = get_logger(__name__)
