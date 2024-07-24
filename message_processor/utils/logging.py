import logging


def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("message_processor")
    return logger


logger = setup_logging()
