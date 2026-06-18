"""
This scripts is to create log for the projects code.
"""

import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
log_file = os.path.join(LOG_DIR, "logger.log")
logger_name = "weather_notifier"

# Setting up logging
def setup_logger():
    os.makedirs(LOG_DIR, exist_ok=True)
    logger = logging.getLogger(logger_name)

    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt= "%(asctime)s | %(levelname)-8s | %(module)-10s | %(message)s", datefmt= "%Y-%m-%d %H:%M:%S")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)

    return logger

# Log to use for the module
def get_logger():
    return logging.getLogger(logger_name)
