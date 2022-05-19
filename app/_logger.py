""" logger to file for production or stdout for development """

import logging
from rich.logging import RichHandler


def set_logger(env):
    if env:
        logging.basicConfig(
            filename='alert.log',
            filemode='w',
            level="INFO",
            format='%(asctime)s | %(message)s',
            datefmt='%d-%b-%y %H:%M:%S',
            # handlers=[RichHandler(rich_tracebacks=True)]
        )
    else:
        logging.basicConfig(
            # filename='alert.log',
            # filemode='w',
            level="INFO",
            format='%(asctime)s | %(message)s',
            datefmt='%d-%b-%y %H:%M:%S',
            handlers=[RichHandler(rich_tracebacks=True)]
        )
