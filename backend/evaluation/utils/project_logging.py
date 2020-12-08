import logging
from pathlib import Path


def get_logger(name: str, log_file: Path = None, level: int = logging.DEBUG):
    logger = logging.getLogger(name)
    logger.handlers = []
    formatter = logging.Formatter("[%(levelname)-8s] [%(name)-8s] %(message)s\t(%(filename)s %(funcName)s %(lineno)d)")
    if log_file:
        file_handler = logging.FileHandler(log_file, mode="w")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    logger.setLevel(level)
    return logger
