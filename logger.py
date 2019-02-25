import logging

import settings

_LOGGING_CONFIGURED = False


def get_logger(name):
    """
    Configure logging and return the logger for [name].

    Logging configuration is done once only the first time this method is called.
    """
    global _LOGGING_CONFIGURED
    if not _LOGGING_CONFIGURED:
        level = logging.DEBUG if settings.ENV == "development" else logging.INFO
        logging.basicConfig(level=level)
        _LOGGING_CONFIGURED = True
    return logging.getLogger(name)
