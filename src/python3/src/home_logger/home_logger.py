"""
The logging in this project aims to be simple enough that all 
logging config, logic, and convenience functions 
can be located in this one script.
"""

import os
import logging
import datetime

from constants.path import LOG_FOLDER
from utilities.shell import safe_check_output

now = datetime.datetime.now()

"default logging config"


class LogConfig():
    LOG_FOLDER_COMPONENT = "maestro-python3"
    LEVEL = logging.WARNING
    WRITE_TO_FILE = True
    WRITE_TO_STDOUT = True
    FORMATTER = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')


"logging configs for unit tests"


class LogConfigTesting(LogConfig):
    LOG_FOLDER_COMPONENT = "maestro-python3-tests"
    WRITE_TO_FILE = False
    WRITE_TO_STDOUT = False


"logging configs when running mflow or tui"


class LogConfigTui(LogConfig):
    LOG_FOLDER_COMPONENT = "mflow"
    WRITE_TO_STDOUT = False


"logging configs when running mflow or tui"


class LogConfigHeimdall(LogConfig):
    LOG_FOLDER_COMPONENT = "heimdall"


"logging configs when running mflow or tui"


class LogConfigSearch(LogConfig):
    LOG_FOLDER_COMPONENT = "search"


def get_log_config_from_environment():
    status = os.environ.get("MAESTRO_PYTHON3_LOGGING_CONFIG", "").lower()
    if status in ("test", "testing", "tests"):
        return LogConfigTesting
    elif status in ("mflow", "tui"):
        return LogConfigTui
    elif status == "search":
        return LogConfigSearch
    elif status == "heimdall":
        return LogConfigHeimdall
    return LogConfig


def get_log_file_path():
    cname = get_log_config_from_environment().LOG_FOLDER_COMPONENT
    folder = LOG_FOLDER+cname
    os.makedirs(folder, exist_ok=True)
    return folder+"/"+now.strftime('%Y-%m-%d')+".log"


def set_log_level(level):
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


def get_logger():
    log_file_path = get_log_file_path()
    folder = os.path.dirname(log_file_path)
    safe_check_output("mkdir -p "+folder)
    logger = logging.getLogger('maestro-python3-logger')
    config = get_log_config_from_environment()

    """
    add null in case no other handlers so error/critical not printed to stdout
    https://docs.python-guide.org/writing/logging/
    """
    logger.addHandler(logging.NullHandler())

    if config.WRITE_TO_FILE:
        fh = logging.FileHandler(log_file_path)
        fh.setFormatter(config.FORMATTER)
        logger.addHandler(fh)
        logger.fh = fh

    if config.WRITE_TO_STDOUT:
        ch = logging.StreamHandler()
        ch.setFormatter(config.FORMATTER)
        logger.addHandler(ch)
        logger.ch = ch

    for handler in logger.handlers:
        handler.setLevel(config.LEVEL)

    return logger


logger = get_logger()
LOG_FILE = get_log_file_path()
