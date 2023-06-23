import os
from pathlib import Path
from logger_config import LOGGING_HANDLERS


def create_log_dir():
    """
    Creates the directory log if it does not exists yet.
    """

    log_dir = Path(LOGGING_HANDLERS["file_info"]["filename"]).parent

    if not log_dir.exists():
        os.makedirs(log_dir)
