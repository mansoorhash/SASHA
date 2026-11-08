import logging
import os
from datetime import datetime

def setup_logger(name, log_file=None, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        if log_file:
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger

def get_logger(name):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    file_name = f"sasha-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    log_file = os.path.join(log_dir, file_name)
    return setup_logger(name, log_file)
