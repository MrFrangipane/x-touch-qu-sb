import logging


def make_logger(module_name) -> logging.Logger:
    return logging.getLogger('.'.join(module_name.split('.')[1:]))
