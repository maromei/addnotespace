LOGGING_FORMATTERS = {
    "standard": {
        "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    },
}

LOGGING_HANDLERS = {
    "console_info": {
        "level": "INFO",
        "formatter": "standard",
        "class": "logging.StreamHandler",
        "stream": "ext://sys.stdout",
    },
    "file_info": {
        "level": "INFO",
        "formatter": "standard",
        "class": "logging.handlers.RotatingFileHandler",
        "filename": "logs/log.txt",
        "mode": "a+",
        "maxBytes": 5 * 10**6, # 5 MegaBytes
        "backupCount": 1,
    }
}


DEFAULT_LOGGER_CONFIG = {
    "handlers": ["console_info", "file_info"],
    "level": "WARNING",
    "propagate": True,
}


LOGGERS = {
    "": DEFAULT_LOGGER_CONFIG,
    "addnotespace": DEFAULT_LOGGER_CONFIG,
    "addnotespace.settings": DEFAULT_LOGGER_CONFIG,
    "addnotespace.style_loader": DEFAULT_LOGGER_CONFIG,
    "addnotespace.defaults": DEFAULT_LOGGER_CONFIG,
}


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": LOGGING_FORMATTERS,
    "handlers": LOGGING_HANDLERS,
    "loggers": LOGGERS,
}
