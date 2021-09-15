""" Logging utilities. """

import logging


def get_logger(name="asmr") -> logging.Logger:
    log_fmt = '%(asctime)s [%(levelname)s] %(message)s'
    logging.basicConfig(format=log_fmt)

    return logging.getLogger(name)
