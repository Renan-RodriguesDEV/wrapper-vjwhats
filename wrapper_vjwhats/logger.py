import datetime
import logging
import os


def setup_logger(name: str = "whatsapp_logger"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    if logger.handlers:
        return logger

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter())
    console_handler.setLevel(logging.DEBUG)

    if not os.path.exists("logs"):
        os.makedirs("logs")
    file_handler = logging.FileHandler(
        f"logs/{name}_{os.getpid()}_{datetime.datetime.now().strftime('%Y%m%d')}.log",encoding="utf-8"
    )
    file_handler.setFormatter(formatter())
    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


def formatter():
    return logging.Formatter(
        "%(asctime)s | %(filename)s:%(lineno)d | [%(levelname)s] >> %(message)s"
    )
